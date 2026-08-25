import uuid
from pathlib import Path
from app.utils.pdf import extract_text_from_pdf
from fastapi import (
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.resume.models import Resume
from app.auth.models import User

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Upload folder
UPLOAD_DIR = BASE_DIR / "uploads" / "resumes"

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf"}

# Maximum file size (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


async def save_resume(
    db: Session,
    file: UploadFile,
    current_user: User,
):
    """
    Save uploaded resume to disk and store metadata in the database.
    """

    # Create upload directory if it doesn't exist
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Get original file extension
    file_extension = Path(file.filename).suffix

    # Validate file extension
    if file_extension.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    # Read uploaded file
    contents = await file.read()

    # Validate empty file
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 5 MB.",
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Full path to save the file
    file_path = UPLOAD_DIR / unique_filename

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    resume_text = extract_text_from_pdf(file_path)

    # Save metadata to database
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=str(file_path),
        resume_text=resume_text
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Return response
    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "original_filename": resume.file_name,
        "stored_filename": unique_filename,
        "file_path": resume.file_path,
        "uploaded_at": resume.uploaded_at,
    }