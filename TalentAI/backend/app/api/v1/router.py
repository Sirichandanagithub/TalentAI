from fastapi import APIRouter

from app.api.v1.auth import router as auth_router


api_router = APIRouter()


# Authentication routes
api_router.include_router(auth_router)


@api_router.get(
    "/health",
    tags=["System"],
)
def health_check():
    """
    Basic API health check.
    """
    return {
        "success": True,
        "status": "healthy",
        "service": "TalentAI API",
        "version": "v1",
    }