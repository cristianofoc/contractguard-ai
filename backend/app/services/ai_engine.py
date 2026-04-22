"""
Core AI engine: analyzes contract text using GPT-4o.

Architecture:
1. Split contract into logical clauses.
2. Analyse each clause via GPT-4o with structured output (JSON mode).
3. Aggregate scores into an overall risk rating.
4. Generate a brief executive summary.
"""

import json
import re
import uuid
from dataclasses import dataclass, field

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.analysis import ClauseAnalysis

# ─── Result container ──────────────────────────────────────────────────────────


@dataclass
class AnalysisResult:
    """Returned by ContractAnalyzer.analyze()."""

    overall_risk_score: float
    overall_risk_level: str  # "low" | "medium" | "high"
    summary: str
    clauses: list[ClauseAnalysis] = field(default_factory=list)


# ─── System prompt ─────────────────────────────────────────────────────────────

CLAUSE_SYSTEM_PROMPT = """You are an expert contract lawyer with 20+ years of experience
reviewing commercial contracts. Your task is to analyse a single contract clause and
assess the risk it poses to the party RECEIVING or SIGNING the contract (not the
drafter).

Respond with a JSON object using exactly these keys:
{
  "plain_english": "<1-3 sentence plain-English explanation>",
  "risk_level": "low" | "medium" | "high",
  "risk_score": <float 0.0 to 1.0>,
  "red_flags": ["<short red flag string>", ...],
  "recommendation": "<actionable recommendation>"
}

Guidelines:
- risk_score 0.0–0.3 → low, 0.31–0.6 → medium, 0.61–1.0 → high
- red_flags should be concrete and concise (≤15 words each)
- If the clause is benign, red_flags can be an empty list
- Do NOT include any text outside the JSON object"""

SUMMARY_SYSTEM_PROMPT = """You are an expert contract lawyer. Given a list of clause-level
risk assessments, write a concise 3-5 sentence executive summary of the contract's overall
risk profile from the perspective of the party signing it. Highlight the most critical
risks and any deal-breakers. Be direct and professional."""


# ─── Clause splitter ───────────────────────────────────────────────────────────


def _split_into_clauses(text: str, max_clauses: int = 20) -> list[tuple[str, str]]:
    """
    Split a contract text into (title, body) pairs.

    Strategy:
    1. Detect numbered/lettered headings (e.g. "1.", "Section 2", "ARTICLE III").
    2. Fall back to splitting on double newlines if no headings found.
    3. Cap at max_clauses to keep API costs predictable.

    Returns a list of (title, body) tuples.
    """
    # Pattern: optional number/letter prefix + ALL-CAPS or Title Case heading
    heading_pattern = re.compile(
        r"^(?:(?:ARTICLE|SECTION|CLAUSE|SCHEDULE)\s+[\w.]+\s*[:\-—]?\s*)?(?:\d+\.?\d*\.?\s+)?([A-Z][A-Z\s\-]+[A-Z]|[A-Z][a-z].{3,50})\s*$",
        re.MULTILINE,
    )

    matches = list(heading_pattern.finditer(text))

    if len(matches) < 2:
        # Fall back: split on double newlines and treat first line as title
        chunks = [c.strip() for c in re.split(r"\n{2,}", text) if c.strip()]
        clauses: list[tuple[str, str]] = []
        for chunk in chunks[:max_clauses]:
            lines = chunk.splitlines()
            title = lines[0][:80] if lines else "Clause"
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else chunk
            clauses.append((title, body or chunk))
        return clauses or [("Full Contract", text)]

    # Use heading positions to extract sections
    clauses = []
    for i, match in enumerate(matches[:max_clauses]):
        title = match.group(0).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            clauses.append((title, body))

    return clauses or [("Full Contract", text)]


# ─── Analyzer ─────────────────────────────────────────────────────────────────


class ContractAnalyzer:
    """
    Orchestrates AI-powered analysis of a full contract document.

    Usage:
        analyzer = ContractAnalyzer()
        result = await analyzer.analyze(contract_text)
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze(self, contract_text: str) -> AnalysisResult:
        """
        Analyse a full contract text.

        Steps:
        1. Split into clauses.
        2. Analyse each clause via GPT-4o.
        3. Compute weighted overall score.
        4. Generate executive summary.
        """
        clauses_raw = _split_into_clauses(contract_text)

        # Analyse clauses concurrently — but limit parallelism to avoid rate limits
        import asyncio

        semaphore = asyncio.Semaphore(5)

        async def analyse_one(title: str, body: str) -> ClauseAnalysis | None:
            async with semaphore:
                return await self._analyse_clause(title, body)

        tasks = [analyse_one(title, body) for title, body in clauses_raw]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures and log them
        clause_analyses: list[ClauseAnalysis] = []
        for res in results:
            if isinstance(res, Exception):
                print(f"[ContractAnalyzer] Clause analysis error: {res}")
            elif res is not None:
                clause_analyses.append(res)

        if not clause_analyses:
            raise RuntimeError("All clause analyses failed. Check OpenAI API key and quota.")

        # Compute weighted overall risk score
        overall_score = self._compute_overall_score(clause_analyses)
        overall_level = self._score_to_level(overall_score)

        # Generate executive summary
        summary = await self._generate_summary(clause_analyses, overall_score)

        return AnalysisResult(
            overall_risk_score=round(overall_score, 3),
            overall_risk_level=overall_level,
            summary=summary,
            clauses=clause_analyses,
        )

    async def _analyse_clause(self, title: str, body: str) -> ClauseAnalysis:
        """Call GPT-4o to analyse a single clause and return a ClauseAnalysis."""
        prompt = f"Clause title: {title}\n\nClause text:\n{body[:3000]}"  # truncate long clauses

        response = await self._client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": CLAUSE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,  # low temperature for consistent, structured output
            max_tokens=800,
        )

        raw_json = response.choices[0].message.content or "{}"
        data = json.loads(raw_json)

        return ClauseAnalysis(
            id=str(uuid.uuid4()),
            title=title,
            original_text=body,
            plain_english=data.get("plain_english", ""),
            risk_level=data.get("risk_level", "low"),
            risk_score=float(data.get("risk_score", 0.0)),
            red_flags=data.get("red_flags", []),
            recommendation=data.get("recommendation", ""),
        )

    async def _generate_summary(
        self, clauses: list[ClauseAnalysis], overall_score: float
    ) -> str:
        """Generate an executive summary given all clause analyses."""
        clause_summaries = "\n".join(
            f"- {c.title} ({c.risk_level}, score={c.risk_score:.2f}): {c.plain_english}"
            for c in clauses
        )
        user_message = (
            f"Overall risk score: {overall_score:.2f}\n\n"
            f"Clause breakdown:\n{clause_summaries[:4000]}"
        )

        response = await self._client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=400,
        )
        return (response.choices[0].message.content or "").strip()

    @staticmethod
    def _compute_overall_score(clauses: list[ClauseAnalysis]) -> float:
        """
        Compute a weighted average risk score.
        High-risk clauses are weighted 2x, medium 1.5x, low 1x.
        """
        if not clauses:
            return 0.0

        weight_map = {"low": 1.0, "medium": 1.5, "high": 2.0}
        total_weight = 0.0
        weighted_sum = 0.0

        for clause in clauses:
            weight = weight_map.get(clause.risk_level, 1.0)
            weighted_sum += clause.risk_score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def _score_to_level(score: float) -> str:
        """Map a numeric risk score to a categorical risk level."""
        if score <= 0.3:
            return "low"
        elif score <= 0.6:
            return "medium"
        return "high"
