"""
RELEVANT EXPERIENCE ANALYSIS TEST

TalentAI - AI Resume Coach

Tests:
    1. Relevant Experience Analyzer
    2. Candidate total experience
    3. Role duration
    4. Experience status
    5. Relevant experience
    6. Relevance score
    7. Result structure
"""

import json
from pathlib import Path

from app.utils.pdf import extract_text_from_pdf
from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume
from app.ai.analyzer.relevant_experience import (
    RelevantExperienceAnalyzer
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RESUME_PATH = (
    BASE_DIR
    / "uploads"
    / "resumes"
    / "af201f6f-c017-43fb-8eca-e3d08e9ba616.pdf"
)


# ============================================================
# JOB
# ============================================================

JOB_TITLE = "Data Scientist"

REQUIRED_YEARS = 3

REQUIRED_SKILLS = [
    "Python",
    "SQL",
    "Machine Learning",
    "Pandas",
    "Scikit-learn",
    "Data Analysis"
]


# ============================================================
# HELPER
# ============================================================

def print_json(
    title,
    data
):
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
# LOAD RESUME
# ============================================================

def load_resume():

    if not RESUME_PATH.exists():

        raise FileNotFoundError(
            f"Resume not found:\n{RESUME_PATH}"
        )

    # --------------------------------------------------------
    # PDF extraction
    # --------------------------------------------------------

    resume_text = extract_text_from_pdf(
        str(RESUME_PATH)
    )

    if not resume_text:

        raise ValueError(
            "No text could be extracted from resume."
        )

    # --------------------------------------------------------
    # Section detection
    # --------------------------------------------------------

    sections = extract_sections(
        resume_text
    )

    # --------------------------------------------------------
    # Resume parsing
    # --------------------------------------------------------

    resume = parse_resume(
        sections
    )

    return resume


# ============================================================
# MAIN TEST
# ============================================================

def test_relevant_experience():

    print("=" * 70)
    print("RELEVANT EXPERIENCE ANALYSIS TEST")
    print("=" * 70)

    # ========================================================
    # JOB
    # ========================================================

    print("\nJOB")
    print("-" * 70)

    print(
        f"Job Title        : {JOB_TITLE}"
    )

    print(
        f"Required Years   : {REQUIRED_YEARS}"
    )

    print("\nRequired Skills")

    for skill in REQUIRED_SKILLS:

        print(
            f"  - {skill}"
        )

    # ========================================================
    # LOAD RESUME
    # ========================================================

    print("\n")
    print("=" * 70)
    print("LOADING RESUME")
    print("=" * 70)

    resume = load_resume()

    print(
        "✅ Resume loaded successfully."
    )

    # ========================================================
    # ANALYZER
    # ========================================================

    print("\n")
    print("=" * 70)
    print("RUNNING ANALYZER")
    print("=" * 70)

    analyzer = RelevantExperienceAnalyzer()

    result = analyzer.analyze(
        resume=resume,
        job_title=JOB_TITLE,
        required_skills=REQUIRED_SKILLS,
        required_years=REQUIRED_YEARS
    )

    # ========================================================
    # FULL RESULT
    # ========================================================

    print_json(
        "FULL RESULT",
        result
    )

    # ========================================================
    # IMPORTANT RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("IMPORTANT RESULTS")
    print("=" * 70)

    print(
        f"\nJob Title              : "
        f"{result.get('job_title')}"
    )

    print(
        f"Required Experience   : "
        f"{result.get('required_years')} years"
    )

    print(
        f"Candidate Experience  : "
        f"{result.get('candidate_years')} years"
    )

    print(
        f"Relevant Experience   : "
        f"{result.get('relevant_years')} years"
    )

    print(
        f"Experience Status      : "
        f"{result.get('experience_status')}"
    )

    print(
        f"Relevance Status       : "
        f"{result.get('relevance_status')}"
    )

    print(
        f"Relevance Score        : "
        f"{result.get('relevance_score')}"
    )

    print(
        f"Experience Ratio       : "
        f"{result.get('experience_requirement_ratio')}"
    )

    print(
        f"Relevant Ratio         : "
        f"{result.get('relevant_experience_ratio')}"
    )

    # ========================================================
    # RELEVANT ROLES
    # ========================================================

    print("\n")
    print("=" * 70)
    print("RELEVANT ROLES")
    print("=" * 70)

    relevant_roles = result.get(
        "relevant_roles",
        []
    )

    if not relevant_roles:

        print(
            "\nNo relevant roles identified."
        )

    else:

        for index, role in enumerate(
            relevant_roles,
            start=1
        ):

            print(
                f"\nRole {index}"
            )

            print("-" * 50)

            print(
                f"Job Title              : "
                f"{role.get('job_title')}"
            )

            print(
                f"Company                : "
                f"{role.get('company')}"
            )

            print(
                f"Duration               : "
                f"{role.get('duration_years')} years"
            )

            print(
                f"Title Relevance        : "
                f"{role.get('title_relevance')}"
            )

            print(
                f"Skill Relevance        : "
                f"{role.get('skill_relevance')}"
            )

            print(
                f"Relevance Score        : "
                f"{role.get('relevance')}"
            )

            print(
                f"Relevance Status       : "
                f"{role.get('status')}"
            )

            print(
                f"Matched Skills         : "
                f"{role.get('matched_skills')}"
            )

            print(
                f"Possible Skills        : "
                f"{role.get('possible_skills')}"
            )

            print(
                f"Unknown Skills         : "
                f"{role.get('unknown_skills')}"
            )

            print(
                f"Evidence Strength      : "
                f"{role.get('evidence_strength')}"
            )

    # ========================================================
    # VALIDATION
    # ========================================================

    print("\n")
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Result structure
    # --------------------------------------------------------

    required_result_keys = [
        "job_title",
        "required_years",
        "candidate_years",
        "relevant_years",
        "experience_status",
        "experience_requirement_ratio",
        "relevant_experience_ratio",
        "relevant_roles",
        "relevance_status",
        "relevance_score"
    ]

    for key in required_result_keys:

        assert key in result, (
            f"Missing result key: {key}"
        )

    print(
        "✅ Result structure is valid."
    )

    # --------------------------------------------------------
    # Job title
    # --------------------------------------------------------

    assert (
        result["job_title"]
        ==
        JOB_TITLE
    )

    print(
        "✅ Job title detected correctly."
    )

    # --------------------------------------------------------
    # Required experience
    # --------------------------------------------------------

    assert (
        result["required_years"]
        ==
        REQUIRED_YEARS
    )

    print(
        "✅ Required experience detected correctly."
    )

    # --------------------------------------------------------
    # Candidate experience
    # --------------------------------------------------------

    assert (
        result["candidate_years"]
        > 0
    )

    print(
        f"✅ Candidate experience detected: "
        f"{result['candidate_years']} years"
    )

    # --------------------------------------------------------
    # Experience status
    # --------------------------------------------------------

    assert result[
        "experience_status"
    ] in [
        "matched",
        "partial",
        "missing"
    ]

    print(
        f"✅ Experience status: "
        f"{result['experience_status']}"
    )

    # --------------------------------------------------------
    # Relevant experience
    # --------------------------------------------------------

    assert (
        result["relevant_years"]
        >= 0
    )

    print(
        f"✅ Relevant experience detected: "
        f"{result['relevant_years']} years"
    )

    # --------------------------------------------------------
    # Relevance score
    # --------------------------------------------------------

    assert (
        0.0
        <=
        result["relevance_score"]
        <=
        1.0
    )

    print(
        f"✅ Relevance score: "
        f"{result['relevance_score']}"
    )

    # --------------------------------------------------------
    # Role validation
    # --------------------------------------------------------

    assert isinstance(
        result["relevant_roles"],
        list
    )

    print(
        f"✅ Role analysis completed: "
        f"{len(result['relevant_roles'])} role(s)"
    )

    # --------------------------------------------------------
    # Ratio validation
    # --------------------------------------------------------

    if result[
        "experience_requirement_ratio"
    ] is not None:

        assert (
            result[
                "experience_requirement_ratio"
            ]
            >= 0
        )

    if result[
        "relevant_experience_ratio"
    ] is not None:

        assert (
            result[
                "relevant_experience_ratio"
            ]
            >= 0
        )

    print(
        "✅ Experience ratios are valid."
    )

    # ========================================================
    # FINAL
    # ========================================================

    print("\n")
    print("=" * 70)
    print("RELEVANT EXPERIENCE TEST PASSED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    test_relevant_experience()