"""
PDF report generator using ReportLab.

Produces a downloadable PDF summarising the contract risk analysis.
Color coding: green (low), amber/yellow (medium), red (high).
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.analysis import ClauseAnalysis

# Risk level → background colour mapping
RISK_COLORS = {
    "low": colors.HexColor("#d4edda"),    # light green
    "medium": colors.HexColor("#fff3cd"),  # light amber
    "high": colors.HexColor("#f8d7da"),    # light red
}

RISK_TEXT_COLORS = {
    "low": colors.HexColor("#155724"),
    "medium": colors.HexColor("#856404"),
    "high": colors.HexColor("#721c24"),
}


def generate_report(
    filename: str,
    overall_risk_score: float,
    overall_risk_level: str,
    summary: str,
    clauses: list[ClauseAnalysis],
) -> bytes:
    """
    Build a PDF report and return it as bytes.

    Args:
        filename: Original contract filename (shown in the report header).
        overall_risk_score: Numeric score 0.0–1.0.
        overall_risk_level: "low" | "medium" | "high".
        summary: Executive summary text.
        clauses: List of clause-level analysis objects.

    Returns:
        Raw PDF bytes ready to send as a file download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
    )
    heading2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor("#16213e"),
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555"),
    )

    story = []

    # ── Title ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("ContractGuard AI — Risk Analysis Report", title_style))
    story.append(Paragraph(f"<b>Contract:</b> {filename}", body_style))
    story.append(
        Paragraph(
            f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            small_style,
        )
    )
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 0.3 * cm))

    # ── Overall Risk Score ────────────────────────────────────────────────────
    story.append(Paragraph("Overall Risk Assessment", heading2_style))

    risk_color = RISK_COLORS.get(overall_risk_level, colors.white)
    risk_text_color = RISK_TEXT_COLORS.get(overall_risk_level, colors.black)

    risk_table = Table(
        [
            [
                Paragraph(
                    f"<b>Risk Level:</b> {overall_risk_level.upper()}", body_style
                ),
                Paragraph(
                    f"<b>Risk Score:</b> {overall_risk_score:.0%}", body_style
                ),
            ]
        ],
        colWidths=["50%", "50%"],
    )
    risk_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), risk_color),
                ("TEXTCOLOR", (0, 0), (-1, -1), risk_text_color),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("ROUNDEDCORNERS", [4]),
            ]
        )
    )
    story.append(risk_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── Executive Summary ─────────────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", heading2_style))
    story.append(Paragraph(summary or "No summary available.", body_style))
    story.append(Spacer(1, 0.4 * cm))

    # ── Clause Breakdown ──────────────────────────────────────────────────────
    story.append(Paragraph("Clause-by-Clause Breakdown", heading2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))

    for i, clause in enumerate(clauses, start=1):
        clause_color = RISK_COLORS.get(clause.risk_level, colors.white)
        clause_text_color = RISK_TEXT_COLORS.get(clause.risk_level, colors.black)

        # Clause header row
        header = Table(
            [[
                Paragraph(f"<b>{i}. {clause.title}</b>", body_style),
                Paragraph(
                    f"<font color='#{clause_text_color.hexval()[2:]}'>■</font> "
                    f"{clause.risk_level.upper()} ({clause.risk_score:.0%})",
                    body_style,
                ),
            ]],
            colWidths=["70%", "30%"],
        )
        header.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), clause_color),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(header)

        # Plain-English explanation
        story.append(
            Paragraph(f"<b>Plain English:</b> {clause.plain_english}", body_style)
        )

        # Red flags
        if clause.red_flags:
            flags_text = " • ".join(clause.red_flags)
            story.append(
                Paragraph(f"<b>⚠ Red Flags:</b> {flags_text}", body_style)
            )

        # Recommendation
        if clause.recommendation:
            story.append(
                Paragraph(f"<b>Recommendation:</b> {clause.recommendation}", body_style)
            )

        story.append(Spacer(1, 0.3 * cm))
        story.append(
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee"))
        )

    # Build the PDF
    doc.build(story)
    return buffer.getvalue()
