
from app.database.session import SessionLocal
from app.resume.models import Resume
from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume


RESUME_ID = 9


def reprocess_resume():

    db = SessionLocal()

    try:
        resume = (
            db.query(Resume)
            .filter(Resume.id == RESUME_ID)
            .first()
        )

        if resume is None:
            raise ValueError(
                f"Resume ID {RESUME_ID} not found"
            )

        if not resume.resume_text:
            raise ValueError(
                "Resume extracted text is empty."
            )

        # Extract sections from existing resume text.
        sections = extract_sections(resume.resume_text)

        # Run the updated master parser.
        new_parsed_data = parse_resume(sections)

        if not isinstance(new_parsed_data, dict):
            raise ValueError(
                "Parser did not return a valid dictionary."
            )

        # Update only parsed_data.
        resume.parsed_data = new_parsed_data

        db.commit()
        db.refresh(resume)

        print("\nRESUME REPROCESSED SUCCESSFULLY")
        print("--------------------------------")
        print("Resume ID:", resume.id)
        print("User ID:", resume.user_id)

        print("\nSKILLS:")
        print(resume.parsed_data.get("skills", {}))

        print("\nLANGUAGES:")
        print(resume.parsed_data.get("languages", []))

        print("\nEXPERIENCE:")
        print(resume.parsed_data.get("experience", []))

        print("\nPROJECTS:")
        print(resume.parsed_data.get("projects", []))

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    reprocess_resume()
