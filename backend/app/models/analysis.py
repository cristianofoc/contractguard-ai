"""ContractAnalysis ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Status lifecycle for an analysis job
STATUS_ENUM = Enum("pending", "processing", "completed", "failed", name="analysis_status")

# Overall risk classification
RISK_LEVEL_ENUM = Enum("low", "medium", "high", name="risk_level")


class ContractAnalysis(Base):
    __tablename__ = "contract_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # Processing state
    status: Mapped[str] = mapped_column(STATUS_ENUM, default="pending", nullable=False)

    # Results (populated after AI analysis completes)
    overall_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_risk_level: Mapped[str | None] = mapped_column(RISK_LEVEL_ENUM, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSONB array of clause analysis objects
    # Each element follows the ClauseAnalysis schema
    clauses: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship back to the owning user
    user: Mapped["User"] = relationship("User", back_populates="analyses")  # noqa: F821
