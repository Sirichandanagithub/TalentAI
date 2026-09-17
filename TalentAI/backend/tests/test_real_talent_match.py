"""
REAL END-TO-END TEST
TalentAI - AI Resume Coach

Pipeline:

Resume PDF
    ↓
PDF Text Extraction
    ↓
Section Detection
    ↓
Resume Parsing
    ↓
Job Description Parsing
    ↓
TalentMatchEngine
    ↓
Hybrid Skill Matching
    ↓
Experience Matching
    ↓
Education Matching
    ↓
Project Matching
    ↓
Context Matching
    ↓
Evidence Engine
    ↓
ATS Scoring
    ↓
Decision Engine
"""

import json
from pathlib import Path

from app.utils.pdf import extract_text_from_pdf
from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume
from app.parser.job_description_parser import parse_job_description

from app.matcher.resume_matcher import match_resume_to_job
from app.matcher.experience_matcher import match_experience

from app.ai.analyzer.talent_match_engine import TalentMatchEngine


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Resume uploaded through TalentAI
RESUME_PATH = (
    BASE_DIR
    / "uploads"
    / "resumes"
    / "af201f6f-c017-43fb-8eca-e3d08e9ba616.pdf"
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

JOB_TEXT = """
Data Scientist

We are looking for a Data Scientist to join our team.

Requirements:

- 3+ years of experience
- Python
- SQL
- Machine Learning
- Pandas
- Scikit-learn
- Data Analysis

Preferred skills:

- AWS
- TensorFlow

Education:

Bachelor's degree in Computer Science, Data Science,
Artificial Intelligence or a related field.
"""


# ============================================================
# HELPER
# ============================================================

def print_json(title, data):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            default=str
        )
    )


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("=" * 70)
    print("TALENTAI - REAL END-TO-END TEST")
    print("=" * 70)


    # ========================================================
    # 1. CHECK RESUME
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 1: CHECK RESUME")
    print("=" * 70)

    if not RESUME_PATH.exists():

        print("❌ Resume not found:")
        print(RESUME_PATH)

        print()
        print("Expected resume location:")
        print(BASE_DIR / "uploads" / "resumes")

        return

    print("✅ Resume found:")
    print(RESUME_PATH)


    # ========================================================
    # 2. PDF TEXT EXTRACTION
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 2: PDF TEXT EXTRACTION")
    print("=" * 70)

    resume_text = extract_text_from_pdf(
        str(RESUME_PATH)
    )

    if not resume_text:

        print("❌ No text extracted from resume.")

        return

    print("✅ PDF text extracted successfully.")

    print("\nFirst 1000 characters:")
    print("-" * 70)

    print(resume_text[:1000])


    # ========================================================
    # 3. SECTION DETECTION
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 3: SECTION DETECTION")
    print("=" * 70)

    sections = extract_sections(
        resume_text
    )

    print("Detected sections:")

    for section_name, section_content in sections.items():

        if isinstance(section_content, str):

            preview = (
                section_content[:150]
                .replace("\n", " ")
            )

        else:

            preview = str(section_content)[:150]

        print(
            f"\n{section_name}:"
            f"\n  {preview}"
        )

    print("\n✅ Section detection completed.")


    # ========================================================
    # 4. MASTER RESUME PARSER
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 4: MASTER RESUME PARSER")
    print("=" * 70)

    try:

        resume = parse_resume(
            sections
        )

        print_json(
            "PARSED RESUME",
            resume
        )

        print("\n✅ Resume parsing completed.")

    except Exception as e:

        print(
            f"❌ Resume parser error: {e}"
        )

        return


    # ========================================================
    # 5. JOB DESCRIPTION PARSER
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 5: JOB DESCRIPTION PARSER")
    print("=" * 70)

    try:

        job = parse_job_description(
            JOB_TEXT
        )

        print_json(
            "PARSED JOB DESCRIPTION",
            job
        )

        print("\n✅ Job description parsing completed.")

    except Exception as e:

        print(
            f"❌ Job description parser error: {e}"
        )

        return


    # ========================================================
    # 6. BASIC RESUME MATCHER
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 6: BASIC RESUME MATCHER")
    print("=" * 70)

    try:

        basic_match = match_resume_to_job(
            resume,
            job
        )

        print_json(
            "BASIC MATCH RESULT",
            basic_match
        )

        print("\n✅ Basic resume matching completed.")

    except Exception as e:

        print(
            f"⚠️ Basic resume matcher error: {e}"
        )


    # ========================================================
    # 7. EXPERIENCE MATCHING
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 7: EXPERIENCE MATCHING")
    print("=" * 70)

    try:

        experience_result = match_experience(
            resume,
            job
        )

        print_json(
            "EXPERIENCE MATCH",
            experience_result
        )

        print("\n✅ Experience matching completed.")

    except Exception as e:

        print(
            f"⚠️ Experience matcher error: {e}"
        )


    # ========================================================
    # 8. TALENT MATCH ENGINE
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 8: TALENT MATCH ENGINE")
    print("=" * 70)

    print("\nInitializing TalentMatchEngine...")

    try:

        engine = TalentMatchEngine()

        print("✅ TalentMatchEngine initialized.")

    except Exception as e:

        print(
            f"❌ TalentMatchEngine initialization error: {e}"
        )

        return


    # ========================================================
    # 9. FULL AI ANALYSIS
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 9: FULL AI TALENT ANALYSIS")
    print("=" * 70)

    try:

        result = engine.analyze(
            resume=resume,
            job=job
        )

        print_json(
            "FINAL TALENT MATCH RESULT",
            result
        )

        print("\n✅ Full TalentMatchEngine analysis completed.")

    except Exception as e:

        print(
            f"❌ TalentMatchEngine analysis error: {e}"
        )

        return


    # ========================================================
    # 10. EXTRACT IMPORTANT RESULTS
    # ========================================================

    print("\n" + "=" * 70)
    print("STEP 10: IMPORTANT RESULTS")
    print("=" * 70)


    # --------------------------------------------------------
    # ATS
    # --------------------------------------------------------

    ats_score = result.get(
        "ats_score"
    )

    classification = result.get(
        "classification"
    )

    print(
        f"\nATS Score        : {ats_score}"
    )

    print(
        f"Classification   : {classification}"
    )


    # --------------------------------------------------------
    # SCORE BREAKDOWN
    # --------------------------------------------------------

    score_breakdown = result.get(
        "score_breakdown",
        {}
    )

    print("\nScore Breakdown:")

    for key, value in score_breakdown.items():

        print(
            f"  {key}: {value}"
        )


    # --------------------------------------------------------
    # MATCH RESULTS
    # --------------------------------------------------------

    match = result.get(
        "match",
        {}
    )

    required = match.get(
        "required",
        {}
    )

    preferred = match.get(
        "preferred",
        {}
    )


    # ========================================================
    # REQUIRED SKILLS
    # ========================================================

    print("\n" + "-" * 70)
    print("REQUIRED SKILLS")
    print("-" * 70)

    matched_required = required.get(
        "matched",
        []
    )

    possible_required = required.get(
        "possible",
        []
    )

    unknown_required = required.get(
        "unknown",
        []
    )


    print("\n✅ MATCHED:")

    for item in matched_required:

        print(
            f"  • {item.get('requirement')}"
            f" | confidence={item.get('confidence')}"
            f" | source={item.get('match_source')}"
        )


    print("\n🟡 POSSIBLE:")

    for item in possible_required:

        print(
            f"  • {item.get('requirement')}"
            f" | confidence={item.get('confidence')}"
            f" | relationship={item.get('relationship')}"
            f" | source={item.get('match_source')}"
        )


    print("\n❌ UNKNOWN:")

    for item in unknown_required:

        print(
            f"  • {item.get('requirement')}"
            f" | confidence={item.get('confidence')}"
            f" | source={item.get('match_source')}"
        )


    # ========================================================
    # PREFERRED SKILLS
    # ========================================================

    print("\n" + "-" * 70)
    print("PREFERRED SKILLS")
    print("-" * 70)

    matched_preferred = preferred.get(
        "matched",
        []
    )

    possible_preferred = preferred.get(
        "possible",
        []
    )

    unknown_preferred = preferred.get(
        "unknown",
        []
    )


    print("\n✅ MATCHED:")

    for item in matched_preferred:

        print(
            f"  • {item.get('requirement')}"
            f" | confidence={item.get('confidence')}"
            f" | source={item.get('match_source')}"
        )


    print("\n🟡 POSSIBLE:")

    for item in possible_preferred:

        print(
            f"  • {item.get('requirement')}"
            f" | confidence={item.get('confidence')}"
            f" | relationship={item.get('relationship')}"
            f" | source={item.get('match_source')}"
        )


    print("\n❌ UNKNOWN:")

    for item in unknown_preferred:

        print(
            f"  • {item.get('requirement')}"
            f" | confidence={item.get('confidence')}"
            f" | source={item.get('match_source')}"
        )


    # ========================================================
    # 11. EXPERIENCE RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("EXPERIENCE RESULT")
    print("=" * 70)

    experience = match.get(
        "experience",
        {}
    )

    print_json(
        "EXPERIENCE",
        experience
    )


    # ========================================================
    # 12. EDUCATION RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("EDUCATION RESULT")
    print("=" * 70)

    education = match.get(
        "education",
        {}
    )

    print_json(
        "EDUCATION",
        education
    )


    # ========================================================
    # 13. PROJECT RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("PROJECT RESULT")
    print("=" * 70)

    projects = match.get(
        "projects",
        {}
    )

    print_json(
        "PROJECT MATCH",
        projects
    )


    # ========================================================
    # 14. CONTEXT / EVIDENCE
    # ========================================================

    print("\n" + "=" * 70)
    print("CONTEXT + EVIDENCE")
    print("=" * 70)

    context = result.get(
        "context",
        {}
    )

    evidence = result.get(
        "evidence",
        {}
    )

    print_json(
        "CONTEXT",
        context
    )

    print_json(
        "EVIDENCE",
        evidence
    )


    # ========================================================
    # 15. DECISION
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL DECISION")
    print("=" * 70)

    decision = result.get(
        "decision",
        {}
    )

    print_json(
        "DECISION",
        decision
    )


    # ========================================================
    # 16. FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(
        f"\nJob Title       : "
        f"{result.get('job_title')}"
    )

    print(
        f"ATS Score       : "
        f"{result.get('ats_score')}"
    )

    print(
        f"Classification  : "
        f"{result.get('classification')}"
    )

    print(
        f"Decision        : "
        f"{decision.get('decision', 'N/A')}"
    )

    print(
        f"Confidence      : "
        f"{decision.get('confidence', 'N/A')}"
    )


    print("\n" + "=" * 70)
    print("REAL TALENT MATCH TEST FINISHED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()