
import uuid
from pathlib import Path

from fastapi import (
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.auth.models import User
from app.parser.master_parser import parse_resume
from app.parser.section_detector import extract_sections
from app.resume.models import Resume
from app.utils.pdf import extract_text_from_pdf


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
    Save an uploaded PDF, extract its text, parse its sections,
    and store both the original text and structured data.
    """

    # Validate the filename and extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    file_extension = Path(file.filename).suffix

    if file_extension.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    # Read and validate the uploaded content
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 5 MB.",
        )

    # Create the upload directory
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Save the PDF
    with open(file_path, "wb") as f:
        f.write(contents)

    # Step 1: Extract text from the PDF
    resume_text = extract_text_from_pdf(file_path)

    # Step 2: Detect and extract resume sections
    sections = extract_sections(resume_text)

    # Step 3: Parse the sections into structured resume data
    parsed_data = parse_resume(sections)

    # Step 4: Store both raw text and structured data
    try:
        resume = Resume(
            user_id=current_user.id,
            file_name=file.filename,
            file_path=str(file_path),
            resume_text=resume_text,
            parsed_data=parsed_data,
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

    except Exception:
        db.rollback()
        raise

    # Return the existing response structure
    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "original_filename": resume.file_name,
        "stored_filename": unique_filename,
        "file_path": resume.file_path,
        "uploaded_at": resume.uploaded_at,
    }
