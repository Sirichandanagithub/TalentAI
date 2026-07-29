import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.resume.models import Resume

from app.auth.models import User
# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Upload folder
UPLOAD_DIR = BASE_DIR / "uploads" / "resumes"


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

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Full path to save the file
    file_path = UPLOAD_DIR / unique_filename

    # Read uploaded file
    contents = await file.read()

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    # Save metadata to database
    resume = Resume(
        #user_id=1,  # Temporary
        #  (we'll replace this with current_user.id next)
        user_id=current_user.id,
        file_name=file.filename,
        file_path=str(file_path),
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