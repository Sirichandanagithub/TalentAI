
"""
FastAPI routes for TalentAI analysis.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.analysis.schema import CandidateAnalysisRequest
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.session import get_db
from app.resume.models import Resume
from app.services.talent_ai_service import TalentAIService
from app.services.resume_analysis_service import ResumeAnalysisService


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


# Create services once for the application process.
talent_ai_service = TalentAIService()
resume_analysis_service = ResumeAnalysisService()


@router.post("/match")
async def analyze_candidate(
    request: CandidateAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze an authenticated user's uploaded resume
    against a job description.
    """

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == request.resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    if not isinstance(resume.parsed_data, dict) or not resume.parsed_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Structured resume data is unavailable. Please upload your resume again.",
        )

    return talent_ai_service.analyze_candidate(
        resume=resume.parsed_data,
        job=request.job,
    )


@router.post("/resume/{resume_id}")
async def analyze_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Perform resume-only analysis.

    Returns:
    - Resume Quality Score
    - ATS Compatibility Score
    """

    # 1. Retrieve only the authenticated user's resume.
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    # 2. Verify resume ownership and existence.
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    # 3. Verify extracted resume text exists.
    if not isinstance(resume.resume_text, str) or not resume.resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Extracted resume text is unavailable. Please upload your resume again.",
        )

    # 4. Run resume-only analysis.
    try:
        return resume_analysis_service.analyze_resume(
            resume_text=resume.resume_text
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
