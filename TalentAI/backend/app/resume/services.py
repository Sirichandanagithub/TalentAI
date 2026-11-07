
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

    # 1. Validate filename and extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    # 2. Read only up to 5 MB + 1 byte
    contents = await file.read(MAX_FILE_SIZE + 1)

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

    # 3. Validate actual PDF signature
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file.",
        )

    # 4. Create upload directory
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 5. Generate unique filename
    unique_filename = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / unique_filename

    try:
        # 6. Save PDF
        with open(file_path, "wb") as f:
            f.write(contents)

        # 7. Extract PDF text
        try:
            resume_text = extract_text_from_pdf(file_path)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unreadable PDF file.",
                ) from exc

        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract readable text from the PDF.",
            )

                # 8. Detect resume sections
        sections = extract_sections(resume_text)

        # 9. Parse structured resume data
        parsed_data = parse_resume(sections)

        # 10. Save resume details to database
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
        try:
            db.rollback()
        except Exception:
            pass

        try:
            if file_path.exists():
                file_path.unlink()
        except OSError:
            pass

        raise

    # 11. Return response
    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "original_filename": resume.file_name,
        "stored_filename": unique_filename,
        "uploaded_at": resume.uploaded_at,
    }