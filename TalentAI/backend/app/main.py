from fastapi import FastAPI

from app.core.config import settings
from app.auth.routes import router as auth_router
from app.resume.routes import router as resume_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hello, this is TalentAI app",
)

app.include_router(auth_router)
app.include_router(resume_router)

@app.get("/")
async def root():
    return {"message": "TalentAI Backend Running 🚀"}