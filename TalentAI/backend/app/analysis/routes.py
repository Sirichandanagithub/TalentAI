"""
FastAPI routes for TalentAI candidate-job analysis.
"""

from fastapi import APIRouter

from app.analysis.schema import CandidateAnalysisRequest
from app.services.talent_ai_service import TalentAIService


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


# Create the service once for the application process.
talent_ai_service = TalentAIService()


@router.post("/match")
async def analyze_candidate(
    request: CandidateAnalysisRequest,
):
    """
    Analyze a candidate against a job description.

    This endpoint delegates the actual matching logic
    to TalentAIService.
    """

    return talent_ai_service.analyze_candidate(
        resume=request.resume,
        job=request.job,
    )