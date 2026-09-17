import json
from pathlib import Path

from app.utils.pdf import extract_text_from_pdf
from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume

from app.ai.analyzer.skill_experience_matcher import (
    SkillExperienceMatcher,
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


REQUIRED_SKILLS = [
    "Python",
    "SQL",
    "Machine Learning",
    "Pandas",
    "Scikit-learn",
    "Data Analysis",
]


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
            default=str,
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

def test_skill_experience_matcher():

    print("=" * 70)
    print("SKILL-SPECIFIC EXPERIENCE TEST")
    print("=" * 70)

    # ========================================================
    # REQUIRED SKILLS
    # ========================================================

    print("\nREQUIRED SKILLS")
    print("-" * 70)

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
    print("RUNNING SKILL EXPERIENCE ANALYZER")
    print("=" * 70)

    matcher = SkillExperienceMatcher()

    result = matcher.analyze(
        REQUIRED_SKILLS,
        resume,
    )

    # ========================================================
    # FULL RESULT
    # ========================================================

    print_json(
        "FULL RESULT",
        result,
    )

    # ========================================================
    # IMPORTANT RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("IMPORTANT RESULTS")
    print("=" * 70)

    print(
        f"\nTotal skills analyzed : "
        f"{len(result['skills'])}"
    )

    print(
        f"Matched skills        : "
        f"{len(result['matched'])}"
    )

    print(
        f"Possible skills       : "
        f"{len(result['possible'])}"
    )

    print(
        f"Unknown skills        : "
        f"{len(result['unknown'])}"
    )

    # ========================================================
    # PER-SKILL RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("SKILL ANALYSIS")
    print("=" * 70)

    for index, skill_result in enumerate(
        result["skills"],
        start=1,
    ):

        print(
            f"\nSkill {index}: "
            f"{skill_result['skill']}"
        )

        print("-" * 50)

        print(
            f"Status             : "
            f"{skill_result['status']}"
        )

        print(
            f"Experience         : "
            f"{skill_result['experience_years']} years"
        )

        print(
            f"Experience months  : "
            f"{skill_result['experience_months']}"
        )

        print(
            f"Sources            : "
            f"{skill_result['sources']}"
        )

        print(
            f"Strength            : "
            f"{skill_result['strength']}"
        )

        # ----------------------------------------------------
        # Roles
        # ----------------------------------------------------

        roles = skill_result.get(
            "roles",
            [],
        )

        if roles:

            print("\nRoles:")

            for role in roles:

                print(
                    f"  - "
                    f"{role.get('job_title')} "
                    f"@ "
                    f"{role.get('company')}"
                )

                print(
                    f"    Duration: "
                    f"{role.get('duration_years')} years"
                )

        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------

        projects = skill_result.get(
            "projects",
            [],
        )

        if projects:

            print("\nProjects:")

            for project in projects:

                print(
                    f"  - "
                    f"{project.get('project_name')}"
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
        "skills",
        "matched",
        "possible",
        "unknown",
    ]

    for key in required_result_keys:

        assert key in result, (
            f"Missing result key: {key}"
        )

    print(
        "✅ Result structure is valid."
    )

    # --------------------------------------------------------
    # Number of skills
    # --------------------------------------------------------

    assert len(
        result["skills"]
    ) == len(
        REQUIRED_SKILLS
    )

    print(
        "✅ All required skills analyzed."
    )

    # --------------------------------------------------------
    # Individual skill structure
    # --------------------------------------------------------

    required_skill_keys = [
        "skill",
        "canonical_skill",
        "status",
        "experience_years",
        "experience_months",
        "sources",
        "roles",
        "projects",
        "strength",
    ]

    for skill_result in result["skills"]:

        for key in required_skill_keys:

            assert key in skill_result, (
                f"Missing skill result key: {key}"
            )

        assert skill_result[
            "experience_years"
        ] >= 0

        assert skill_result[
            "experience_months"
        ] >= 0

        assert skill_result[
            "status"
        ] in [
            "matched",
            "possible",
            "unknown",
        ]

    print(
        "✅ Individual skill results are valid."
    )

    # --------------------------------------------------------
    # Python validation
    # --------------------------------------------------------

    python_result = next(
        (
            item
            for item in result["skills"]
            if item["skill"].lower()
            == "python"
        ),
        None,
    )

    assert python_result is not None

    print(
        "✅ Python skill analyzed."
    )

    # --------------------------------------------------------
    # At least one practical experience
    # --------------------------------------------------------

    has_practical_experience = any(
        item["experience_years"] > 0
        for item in result["skills"]
    )

    assert has_practical_experience

    print(
        "✅ Practical skill experience detected."
    )

    # ========================================================
    # FINAL
    # ========================================================

    print("\n")
    print("=" * 70)
    print("SKILL EXPERIENCE TEST PASSED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    test_skill_experience_matcher()