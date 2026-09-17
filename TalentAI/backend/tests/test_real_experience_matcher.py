import os

from app.utils.pdf import extract_text_from_pdf
from app.parser.section_detector import extract_sections
from app.parser.experience_parser import parse_experience
from app.matcher.experience_matcher import (
    calculate_total_experience,
    match_experience
)


# ============================================================
# REAL RESUME PATH
# ============================================================

PDF_PATH = (
    r"C:\practice_vscode\TalentAI\backend"
    r"\uploads\resumes\Srikanth Reddy Resume 2026 01.pdf"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("REAL RESUME EXPERIENCE MATCHER TEST")
print("=" * 60)

print("\nPDF:")
print(PDF_PATH)


# ============================================================
# STEP 1: CHECK PDF
# ============================================================

print("\n" + "=" * 60)
print("STEP 1: CHECK PDF")
print("=" * 60)

if not os.path.exists(PDF_PATH):

    print("File found: NO")
    print("\nTest stopped.")

    raise SystemExit

print("File found: YES")


# ============================================================
# STEP 2: EXTRACT PDF TEXT
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: EXTRACT PDF TEXT")
print("=" * 60)

resume_text = extract_text_from_pdf(
    PDF_PATH
)

if not resume_text:

    print("No text extracted.")
    print("\nTest stopped.")

    raise SystemExit

print(
    "Extracted text length:",
    len(resume_text)
)


# ============================================================
# STEP 3: SECTION DETECTION
# ============================================================

print("\n" + "=" * 60)
print("STEP 3: SECTION DETECTION")
print("=" * 60)

sections = extract_sections(
    resume_text
)

print("\nDetected sections:")

for section_name in sections:

    print(
        " -",
        section_name
    )


# ============================================================
# STEP 4: EXTRACT EXPERIENCE SECTION
# ============================================================

print("\n" + "=" * 60)
print("STEP 4: EXPERIENCE SECTION")
print("=" * 60)

experience_text = sections.get(
    "experience",
    ""
)

if not experience_text:

    print("Experience section not found.")
    print("\nTest stopped.")

    raise SystemExit

print(experience_text)


# ============================================================
# STEP 5: PARSE EXPERIENCE
# ============================================================

print("\n" + "=" * 60)
print("STEP 5: PARSE EXPERIENCE")
print("=" * 60)

experiences = parse_experience(
    experience_text
)

print(
    "\nNumber of experience entries:",
    len(experiences)
)


for index, experience in enumerate(
    experiences,
    start=1
):

    print("\n" + "-" * 60)
    print(
        f"EXPERIENCE [{index}]"
    )
    print("-" * 60)

    print(experience)


# ============================================================
# STEP 6: CALCULATE TOTAL EXPERIENCE
# ============================================================

print("\n" + "=" * 60)
print("STEP 6: CALCULATE TOTAL EXPERIENCE")
print("=" * 60)

candidate_years = calculate_total_experience(
    experiences
)

print(
    "\nCandidate experience:",
    candidate_years
)


# ============================================================
# STEP 7: MATCH AGAINST JOB REQUIREMENT
# ============================================================

print("\n" + "=" * 60)
print("STEP 7: MATCH EXPERIENCE")
print("=" * 60)

required_experience = {
    "minimum_years": 3
}

resume = {
    "experience": experiences
}

experience_result = match_experience(
    resume,
    required_experience
)

print("\nRequired experience:")
print(
    required_experience
)

print("\nExperience match result:")
print(
    experience_result
)


# ============================================================
# STEP 8: INTERPRET RESULT
# ============================================================

print("\n" + "=" * 60)
print("STEP 8: RESULT INTERPRETATION")
print("=" * 60)

status = experience_result.get(
    "status"
)

candidate_years = experience_result.get(
    "candidate_years"
)

required_years = experience_result.get(
    "required_years"
)

print(
    "\nStatus:",
    status
)

print(
    "Required years:",
    required_years
)

print(
    "Candidate years:",
    candidate_years
)


if status == "matched":

    print(
        "\n✅ Candidate meets the experience requirement."
    )

elif status == "partial":

    print(
        "\n⚠️ Candidate has some experience, "
        "but less than required."
    )

elif status == "unknown":

    print(
        "\n❓ Experience cannot be reliably determined "
        "from the available resume dates."
    )

elif status == "missing":

    print(
        "\n❌ Candidate has no qualifying experience."
    )

elif status == "not_required":

    print(
        "\nℹ️ Experience is not required for this job."
    )


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 60)
print("REAL RESUME EXPERIENCE MATCHER TEST FINISHED")
print("=" * 60)