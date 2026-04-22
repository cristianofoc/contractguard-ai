"""
Contract upload and management endpoints.

Flow:
1. User uploads a PDF or DOCX file.
2. An analysis record is created with status=pending.
3. AI analysis runs as a FastAPI BackgroundTask (non-blocking).
4. The client polls GET /{analysis_id} until status=completed.
"""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from fastapi import File as FastAPIFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.config import settings
from app.database import get_db
from app.models.analysis import ContractAnalysis
from app.models.user import User
from app.schemas.analysis import AnalysisListResponse, AnalysisResponse, AnalysisSummary
from app.services.ai_engine import ContractAnalyzer
from app.services.pdf_parser import extract_text

router = APIRouter(prefix="/contracts", tags=["contracts"])

# Allowed MIME types for uploaded contracts
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Maximum upload size: 10 MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


async def _run_analysis(analysis_id: uuid.UUID, contract_text: str) -> None:
    """
    Background task: run the AI engine and persist results.
    Uses a fresh DB session because BackgroundTasks run outside the request lifecycle.
    """
    from app.database import AsyncSessionLocal  # local import to avoid circular deps

    async with AsyncSessionLocal() as db:
        # Fetch the analysis record
        result = await db.execute(
            select(ContractAnalysis).where(ContractAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            return

        # Mark as processing so the client sees progress
        analysis.status = "processing"
        await db.commit()

        try:
            analyzer = ContractAnalyzer()
            analysis_result = await analyzer.analyze(contract_text)

            analysis.status = "completed"
            analysis.overall_risk_score = analysis_result.overall_risk_score
            analysis.overall_risk_level = analysis_result.overall_risk_level
            analysis.summary = analysis_result.summary
            analysis.clauses = [c.model_dump() for c in analysis_result.clauses]
        except Exception as exc:
            # Log and mark as failed — don't surface the error to the user directly
            print(f"[AI Engine Error] analysis_id={analysis_id}: {exc}")
            analysis.status = "failed"

        await db.commit()


@router.post("/upload", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = FastAPIFile(..., description="PDF or DOCX contract file"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnalysisResponse:
    """
    Upload a contract file and kick off an asynchronous AI analysis.

    Returns the newly created analysis record with status='pending'.
    The client should poll GET /{analysis_id} to retrieve results.
    """
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX files are supported",
        )

    # Read file into memory and enforce size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 10 MB size limit",
        )

    # Enforce free tier usage limit
    if (
        current_user.free_analyses_used >= settings.FREE_ANALYSES_LIMIT
        and not current_user.stripe_customer_id
    ):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Free tier limit reached ({settings.FREE_ANALYSES_LIMIT} analyses). "
                "Please purchase credits to continue."
            ),
        )

    # Extract text from the uploaded file
    try:
        contract_text = extract_text(content, file.content_type or "")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # Create the analysis record
    analysis = ContractAnalysis(
        user_id=current_user.id,
        filename=file.filename or "unknown",
        status="pending",
    )
    db.add(analysis)

    # Increment free usage counter
    current_user.free_analyses_used += 1

    await db.flush()

    # Schedule the AI analysis as a background task (returns immediately)
    background_tasks.add_task(_run_analysis, analysis.id, contract_text)

    await db.commit()
    await db.refresh(analysis)

    return AnalysisResponse.model_validate(analysis)


@router.get("/", response_model=AnalysisListResponse)
async def list_analyses(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnalysisListResponse:
    """
    List all contract analyses for the current user, newest first.
    Supports pagination via `page` and `per_page` query params.
    """
    offset = (page - 1) * per_page

    # Count total rows for pagination metadata
    count_result = await db.execute(
        select(func.count()).where(ContractAnalysis.user_id == current_user.id)
    )
    total = count_result.scalar_one()

    # Fetch the requested page
    rows_result = await db.execute(
        select(ContractAnalysis)
        .where(ContractAnalysis.user_id == current_user.id)
        .order_by(ContractAnalysis.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    analyses = rows_result.scalars().all()

    return AnalysisListResponse(
        items=[AnalysisSummary.model_validate(a) for a in analyses],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnalysisResponse:
    """Retrieve the full results of a specific analysis by its ID."""
    result = await db.execute(
        select(ContractAnalysis).where(
            ContractAnalysis.id == analysis_id,
            ContractAnalysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    return AnalysisResponse.model_validate(analysis)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete a specific analysis. Only the owning user can delete their analyses."""
    result = await db.execute(
        select(ContractAnalysis).where(
            ContractAnalysis.id == analysis_id,
            ContractAnalysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    await db.delete(analysis)
    await db.commit()
