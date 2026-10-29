from fastapi import FastAPI

from app.core.config import settings

from app.auth.routes import router as auth_router
from app.resume.routes import router as resume_router
from app.analysis.routes import router as analysis_router

from app.api.v1.router import api_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hello, this is TalentAI app",
)


# ============================================================
# Existing API routes
# ============================================================

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(analysis_router)


# ============================================================
# Versioned API routes
# ============================================================

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "TalentAI Backend Running 🚀"
    }