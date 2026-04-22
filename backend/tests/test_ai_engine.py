"""
Unit tests for AI engine utilities that don't require API calls.
Tests the clause splitter and score aggregation logic.
"""

import pytest

from app.services.ai_engine import ContractAnalyzer, _split_into_clauses
from app.schemas.analysis import ClauseAnalysis


class TestClauseSplitter:
    def test_splits_on_headings(self):
        text = "LIMITATION OF LIABILITY\nSome text here.\n\nINDEMNIFICATION\nMore text."
        clauses = _split_into_clauses(text)
        assert len(clauses) >= 1

    def test_fallback_on_no_headings(self):
        text = "This is a paragraph.\n\nThis is another paragraph."
        clauses = _split_into_clauses(text)
        assert len(clauses) >= 1

    def test_returns_title_body_tuples(self):
        text = "Some simple contract text without headings."
        clauses = _split_into_clauses(text)
        for title, body in clauses:
            assert isinstance(title, str)
            assert isinstance(body, str)

    def test_max_clauses_limit(self):
        # Create 30 paragraphs
        text = "\n\n".join(f"Paragraph {i} content here." for i in range(30))
        clauses = _split_into_clauses(text, max_clauses=10)
        assert len(clauses) <= 10


class TestScoreAggregation:
    def _make_clause(self, risk_level: str, risk_score: float) -> ClauseAnalysis:
        return ClauseAnalysis(
            id="test-id",
            title="Test Clause",
            original_text="text",
            plain_english="plain",
            risk_level=risk_level,
            risk_score=risk_score,
            red_flags=[],
            recommendation="none",
        )

    def test_all_low_risk(self):
        clauses = [self._make_clause("low", 0.1) for _ in range(3)]
        score = ContractAnalyzer._compute_overall_score(clauses)
        assert score == pytest.approx(0.1)

    def test_high_risk_weighted_more(self):
        low_clause = self._make_clause("low", 0.1)
        high_clause = self._make_clause("high", 0.9)
        score = ContractAnalyzer._compute_overall_score([low_clause, high_clause])
        # High-risk is weighted 2x, so result should be closer to 0.9 than 0.1
        assert score > 0.5

    def test_empty_clauses_returns_zero(self):
        score = ContractAnalyzer._compute_overall_score([])
        assert score == 0.0

    def test_score_to_level_low(self):
        assert ContractAnalyzer._score_to_level(0.1) == "low"
        assert ContractAnalyzer._score_to_level(0.3) == "low"

    def test_score_to_level_medium(self):
        assert ContractAnalyzer._score_to_level(0.31) == "medium"
        assert ContractAnalyzer._score_to_level(0.6) == "medium"

    def test_score_to_level_high(self):
        assert ContractAnalyzer._score_to_level(0.61) == "high"
        assert ContractAnalyzer._score_to_level(1.0) == "high"
