"""Pydantic v2 schemas for ContractAnalysis-related data."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ClauseAnalysis(BaseModel):
    """Single clause analysis result stored inside the JSONB column."""

    id: str = Field(description="UUID string for this clause")
    title: str
    original_text: str
    plain_english: str
    risk_level: Literal["low", "medium", "high"]
    risk_score: float = Field(ge=0.0, le=1.0)
    red_flags: list[str] = Field(default_factory=list)
    recommendation: str


class AnalysisCreate(BaseModel):
    """Internal schema used when creating a new analysis record."""

    filename: str
    file_url: str | None = None
    user_id: uuid.UUID


class AnalysisResponse(BaseModel):
    """Full analysis response returned to the client."""

    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    file_url: str | None
    status: Literal["pending", "processing", "completed", "failed"]
    overall_risk_score: float | None
    overall_risk_level: Literal["low", "medium", "high"] | None
    summary: str | None
    clauses: list[ClauseAnalysis] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalysisSummary(BaseModel):
    """Lightweight list-view response (used on the dashboard)."""

    id: uuid.UUID
    filename: str
    status: Literal["pending", "processing", "completed", "failed"]
    overall_risk_score: float | None
    overall_risk_level: Literal["low", "medium", "high"] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    """Paginated list of analyses."""

    items: list[AnalysisSummary]
    total: int
    page: int
    per_page: int
