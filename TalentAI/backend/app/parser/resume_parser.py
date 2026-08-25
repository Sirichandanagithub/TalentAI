# ============================================================
# END-TO-END RESUME PARSER
# ============================================================

from app.utils.pdf import extract_text_from_pdf
from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume


# ============================================================
# PARSE RESUME PDF
# ============================================================

def parse_resume_pdf(pdf_path: str):

    """
    Complete resume parsing pipeline.

    PDF
      ↓
    Text Extraction
      ↓
    Section Detection
      ↓
    Master Parser
      ↓
    Structured Resume JSON
    """

    # ========================================================
    # STEP 1: EXTRACT TEXT FROM PDF
    # ========================================================

    text = extract_text_from_pdf(
        pdf_path
    )

    if not text:

        return {
            "success": False,
            "message": "Could not extract text from PDF.",
            "resume": None
        }


    # ========================================================
    # STEP 2: EXTRACT RESUME SECTIONS
    # ========================================================

    sections = extract_sections(
        text
    )

    if not sections:

        return {
            "success": False,
            "message": "Could not detect resume sections.",
            "resume": None
        }


    # ========================================================
    # STEP 3: MASTER PARSER
    # ========================================================

    resume = parse_resume(
        sections
    )


    # ========================================================
    # STEP 4: FINAL RESULT
    # ========================================================

    return {
        "success": True,
        "message": "Resume parsed successfully.",
        "resume": resume
    }