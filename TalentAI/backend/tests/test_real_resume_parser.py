from pathlib import Path
from pprint import pprint

from app.utils.pdf import extract_text_from_pdf

from app.parser.section_detector import (
    extract_sections
)

from app.parser.master_parser import (
    parse_resume
)

from app.parser.job_description_parser import (
    parse_job_description
)

from app.matcher.resume_matcher import (
    match_resume
)

from app.matcher.experience_matcher import (
    match_experience
)

from app.matcher.education_matcher import (
    match_education
)

from app.ai.analyzer.talent_match_engine import (
    TalentMatchEngine
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

RESUME_PATH = (
    BASE_DIR
    / "uploads"
    / "resumes"
    / "Srikanth Reddy Resume 2026 01.pdf"
)


JOB_DESCRIPTION = """
Data Scientist

We are looking for a Data Scientist with 3+ years
of experience in Python, SQL and Machine Learning.

The candidate should have experience with Pandas,
Scikit-learn and Data Analysis.

Experience with AWS and TensorFlow is preferred.

Bachelor's degree in Computer Science, Data Science,
Artificial Intelligence or a related field is required.
"""


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("TALENTAI REAL END-TO-END MATCH TEST")
print("=" * 60)


# ============================================================
# STEP 1: CHECK RESUME
# ============================================================

print("\n" + "=" * 60)
print("STEP 1: CHECK REAL RESUME")
print("=" * 60)

print(
    f"\nPDF:\n{RESUME_PATH}"
)

if not RESUME_PATH.exists():

    raise FileNotFoundError(
        f"Resume not found: {RESUME_PATH}"
    )

print(
    "File found: YES"
)


# ============================================================
# STEP 2: EXTRACT PDF
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: EXTRACT PDF TEXT")
print("=" * 60)

resume_text = extract_text_from_pdf(
    str(RESUME_PATH)
)

if not resume_text:

    raise ValueError(
        "PDF extraction returned empty text."
    )

print(
    f"\nExtracted text length: "
    f"{len(resume_text)}"
)

print(
    "PDF extraction: PASSED"
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

print(
    "\nDetected sections:"
)

for section in sections:

    print(
        f" - {section}"
    )


# ============================================================
# STEP 4: MASTER RESUME PARSER
# ============================================================

print("\n" + "=" * 60)
print("STEP 4: MASTER RESUME PARSER")
print("=" * 60)

resume = parse_resume(
    sections
)

print(
    "\nResume parsed successfully."
)


# ============================================================
# STEP 5: PRINT RESUME STRUCTURE
# ============================================================

print("\n" + "=" * 60)
print("STEP 5: RESUME SUMMARY")
print("=" * 60)

print(
    "\nPERSONAL:"
)

pprint(
    resume.get(
        "personal",
        {}
    )
)

print(
    "\nEDUCATION:"
)

pprint(
    resume.get(
        "education",
        []
    )
)

print(
    "\nEXPERIENCE:"
)

pprint(
    resume.get(
        "experience",
        []
    )
)

print(
    "\nPROJECTS:"
)

pprint(
    resume.get(
        "projects",
        []
    )
)

print(
    "\nSKILLS:"
)

pprint(
    resume.get(
        "skills",
        {}
    )
)

print(
    "\nCERTIFICATIONS:"
)

pprint(
    resume.get(
        "certifications",
        []
    )
)


# ============================================================
# STEP 6: FLATTEN SKILLS
# ============================================================

print("\n" + "=" * 60)
print("STEP 6: CANDIDATE SKILLS")
print("=" * 60)

candidate_skills = []

skills = resume.get(
    "skills",
    {}
)

if isinstance(
    skills,
    dict
):

    for category_skills in skills.values():

        if isinstance(
            category_skills,
            list
        ):

            candidate_skills.extend(
                str(skill).strip()
                for skill in category_skills
                if skill
            )

        elif isinstance(
            category_skills,
            str
        ):

            candidate_skills.append(
                category_skills.strip()
            )

elif isinstance(
    skills,
    list
):

    candidate_skills = [
        str(skill).strip()
        for skill in skills
        if skill
    ]


# Remove duplicates

unique_skills = []

seen = set()

for skill in candidate_skills:

    normalized = skill.lower()

    if normalized not in seen:

        seen.add(
            normalized
        )

        unique_skills.append(
            skill
        )

candidate_skills = unique_skills


for skill in candidate_skills:

    print(
        f" - {skill}"
    )


# ============================================================
# STEP 7: JOB DESCRIPTION PARSER
# ============================================================

print("\n" + "=" * 60)
print("STEP 7: JOB DESCRIPTION PARSER")
print("=" * 60)

job = parse_job_description(
    JOB_DESCRIPTION
)

print()

pprint(
    job
)


# ============================================================
# STEP 8: EXISTING RESUME MATCHER
# ============================================================

print("\n" + "=" * 60)
print("STEP 8: EXISTING RESUME MATCHER")
print("=" * 60)

try:

    existing_match = match_resume(
        resume,
        job
    )

    pprint(
        existing_match
    )

except TypeError:

    print(
        "Existing matcher interface differs; "
        "skipping direct comparison."
    )

except Exception as exc:

    print(
        f"Existing matcher warning: {exc}"
    )


# ============================================================
# STEP 9: EXPERIENCE MATCH
# ============================================================

print("\n" + "=" * 60)
print("STEP 9: EXPERIENCE MATCH")
print("=" * 60)

try:

    experience_result = match_experience(
        resume.get(
            "experience",
            []
        ),
        job.get(
            "experience",
            {}
        )
    )

except TypeError:

    try:

        experience_result = match_experience(
            resume.get(
                "experience",
                []
            )
        )

    except Exception as exc:

        experience_result = {
            "status": "unknown",
            "error": str(exc)
        }

except Exception as exc:

    experience_result = {
        "status": "unknown",
        "error": str(exc)
    }

pprint(
    experience_result
)


# ============================================================
# STEP 10: EDUCATION MATCH
# ============================================================

print("\n" + "=" * 60)
print("STEP 10: EDUCATION MATCH")
print("=" * 60)

try:

    education_result = match_education(
        job.get(
            "education",
            []
        ),
        resume.get(
            "education",
            []
        )
    )

except TypeError:

    try:

        education_result = match_education(
            resume.get(
                "education",
                []
            ),
            job.get(
                "education",
                []
            )
        )

    except Exception as exc:

        education_result = {
            "status": "unknown",
            "error": str(exc)
        }

except Exception as exc:

    education_result = {
        "status": "unknown",
        "error": str(exc)
    }

pprint(
    education_result
)


# ============================================================
# STEP 11: PREPARE TALENTAI INPUT
# ============================================================

print("\n" + "=" * 60)
print("STEP 11: PREPARE TALENTAI INPUT")
print("=" * 60)

print(
    "\nTalentAI input prepared."
)

print(
    f"Candidate skills: "
    f"{len(candidate_skills)}"
)

print(
    f"Required skills: "
    f"{len(job.get('required_skills', []))}"
)

print(
    f"Preferred skills: "
    f"{len(job.get('preferred_skills', []))}"
)

print(
    f"Experience requirement: "
    f"{job.get('experience', {})}"
)

print(
    f"Education requirements: "
    f"{job.get('education', [])}"
)


# ============================================================
# STEP 12: INITIALIZE TALENTAI ENGINE
# ============================================================

print("\n" + "=" * 60)
print("STEP 12: INITIALIZE TALENTAI MATCH ENGINE")
print("=" * 60)

engine = TalentMatchEngine()


# ============================================================
# STEP 13: RUN TALENTAI
# ============================================================

print("\n" + "=" * 60)
print("STEP 13: RUN TALENTAI ANALYSIS")
print("=" * 60)

final_result = engine.analyze(
    resume,
    job
)


# ============================================================
# STEP 14: MATCH RESULT
# ============================================================

print("\n" + "=" * 60)
print("STEP 14: TALENTAI MATCH RESULT")
print("=" * 60)

match_result = final_result.get(
    "match",
    {}
)

print(
    "\nJOB TITLE:"
)

print(
    match_result.get(
        "job_title"
    )
)


# ============================================================
# SKILLS
# ============================================================

print(
    "\nREQUIRED SKILLS:"
)

required = (
    match_result
    .get(
        "skills",
        {}
    )
    .get(
        "required",
        {}
    )
)

print(
    "\nMatched:"
)

for item in required.get(
    "matched",
    []
):

    print(
        f"  [MATCHED] "
        f"{item}"
    )

print(
    "\nPossible:"
)

for item in required.get(
    "possible",
    []
):

    print(
        f"  [POSSIBLE] "
        f"{item}"
    )

print(
    "\nUnknown:"
)

for item in required.get(
    "unknown",
    []
):

    print(
        f"  [UNKNOWN] "
        f"{item}"
    )


# ============================================================
# PREFERRED
# ============================================================

print(
    "\nPREFERRED SKILLS:"
)

preferred = (
    match_result
    .get(
        "skills",
        {}
    )
    .get(
        "preferred",
        {}
    )
)

print(
    "\nMatched:"
)

for item in preferred.get(
    "matched",
    []
):

    print(
        f"  [MATCHED] "
        f"{item}"
    )

print(
    "\nPossible:"
)

for item in preferred.get(
    "possible",
    []
):

    print(
        f"  [POSSIBLE] "
        f"{item}"
    )

print(
    "\nUnknown:"
)

for item in preferred.get(
    "unknown",
    []
):

    print(
        f"  [UNKNOWN] "
        f"{item}"
    )


# ============================================================
# EXPERIENCE
# ============================================================

print(
    "\nEXPERIENCE:"
)

pprint(
    match_result.get(
        "experience",
        {}
    )
)


# ============================================================
# EDUCATION
# ============================================================

print(
    "\nEDUCATION:"
)

pprint(
    match_result.get(
        "education",
        {}
    )
)


# ============================================================
# PROJECTS
# ============================================================

print(
    "\nPROJECTS:"
)

pprint(
    match_result.get(
        "projects",
        {}
    )
)


# ============================================================
# DECISION
# ============================================================

print("\n" + "=" * 60)
print("STEP 15: TALENTAI DECISION")
print("=" * 60)

decision = final_result.get(
    "decision",
    {}
)

pprint(
    decision
)


# ============================================================
# COMPLETE RESULT
# ============================================================

print("\n" + "=" * 60)
print("STEP 16: COMPLETE TALENTAI RESULT")
print("=" * 60)

pprint(
    final_result
)


# ============================================================
# FINISHED
# ============================================================

print("\n" + "=" * 60)
print("REAL TALENTAI END-TO-END TEST FINISHED")
print("=" * 60)