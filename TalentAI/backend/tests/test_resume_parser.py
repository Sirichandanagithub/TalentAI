from pathlib import Path

from app.parser.resume_parser import parse_resume_pdf


# ============================================================
# FIND RESUME PDF
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = (
    BASE_DIR
    / "uploads"
    / "resumes"
    / "Srikanth Reddy Resume 2026 01.pdf"
)


# ============================================================
# CHECK FILE
# ============================================================

print("=" * 60)
print("RESUME PDF PARSER TEST")
print("=" * 60)

print("\nPDF:")
print(PDF_PATH)

if not PDF_PATH.exists():

    print("\nERROR: Resume PDF not found.")

    raise SystemExit(1)


print("\nFile exists: YES")
print("File size:", PDF_PATH.stat().st_size, "bytes")


# ============================================================
# PARSE RESUME
# ============================================================

print("\nPARSING RESUME...")

result = parse_resume_pdf(
    str(PDF_PATH)
)


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 60)
print("PARSER RESULT")
print("=" * 60)

print(result)


# ============================================================
# STATUS
# ============================================================

if result.get("success"):

    print("\n" + "=" * 60)
    print("RESUME PARSING SUCCESSFUL")
    print("=" * 60)

else:

    print("\n" + "=" * 60)
    print("RESUME PARSING FAILED")
    print("=" * 60)

    print("Message:")
    print(result.get("message"))