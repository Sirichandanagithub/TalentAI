from pathlib import Path

from app.utils.pdf import extract_text_from_pdf


# ============================================================
# TEST REAL RESUME PDF EXTRACTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RESUME_PATH = (
    BASE_DIR
    / "uploads"
    / "resumes"
    / "Srikanth Reddy Resume 2026 01.pdf"
)


print("=" * 60)
print("REAL RESUME PDF EXTRACTION TEST")
print("=" * 60)

print("\nPDF:")
print(RESUME_PATH)


# ============================================================
# CHECK FILE
# ============================================================

if not RESUME_PATH.exists():

    print("\nERROR: Resume PDF not found.")

    print("Expected path:")
    print(RESUME_PATH)

    raise FileNotFoundError(
        RESUME_PATH
    )


print("\nFile found: YES")


# ============================================================
# EXTRACT TEXT
# ============================================================

text = extract_text_from_pdf(
    str(RESUME_PATH)
)


# ============================================================
# VALIDATE RESULT
# ============================================================

print("\nExtracted text length:")
print(len(text))


if not text:

    print("\nERROR: No text extracted from PDF.")

    raise ValueError(
        "PDF extraction returned empty text."
    )


print("\n" + "=" * 60)
print("EXTRACTED RESUME TEXT")
print("=" * 60)

print(text)


print("\n" + "=" * 60)
print("PDF EXTRACTION TEST PASSED")
print("=" * 60)