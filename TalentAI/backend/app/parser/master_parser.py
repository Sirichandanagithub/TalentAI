from app.parser.personal_parser import parse_personal
from app.parser.summary_parser import parse_summary
from app.parser.education_parser import parse_education
from app.parser.experience_parser import parse_experience
from app.parser.project_parser import parse_projects
from app.parser.skill_parser import parse_skills
from app.parser.certification_parser import parse_certifications
from app.parser.achievement_parser import parse_achievements


# ============================================================
# SUMMARY EXTRACTION FROM PERSONAL SECTION
# ============================================================

def extract_summary_from_personal(
    personal_text: str
) -> str | None:

    if not personal_text:
        return None

    lines = [
        line.strip()
        for line in personal_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    summary_start = False
    summary_lines = []

    for line in lines:

        lower_line = line.lower()

        # Detect the beginning of an objective/summary
        if (
            lower_line.startswith("to obtain ")
            or lower_line.startswith("objective:")
            or lower_line.startswith("career objective:")
            or lower_line.startswith("professional summary:")
            or lower_line.startswith("summary:")
        ):
            summary_start = True

        if summary_start:
            summary_lines.append(line)

    if not summary_lines:
        return None

    return " ".join(summary_lines).strip()


# ============================================================
# MASTER RESUME PARSER
# ============================================================

def parse_resume(sections: dict):

    if not sections:
        return {
            "personal": {},
            "summary": None,
            "education": [],
            "experience": [],
            "projects": [],
            "skills": {},
            "certifications": [],
            "achievements": []
        }

    # --------------------------------------------------------
    # PERSONAL
    # --------------------------------------------------------

    personal_text = sections.get(
        "personal",
        ""
    )

    personal = parse_personal(
        personal_text
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary_text = sections.get(
        "summary"
    )

    if summary_text:

        summary = parse_summary(
            summary_text
        )

    else:

        summary = extract_summary_from_personal(
            personal_text
        )

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education_text = sections.get(
        "education",
        ""
    )

    education = parse_education(
        education_text
    )

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    experience_text = sections.get(
        "experience",
        ""
    )

    experience = parse_experience(
        experience_text
    )

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects_text = sections.get(
        "projects",
        ""
    )

    projects = parse_projects(
        projects_text
    )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    skills_text = sections.get(
        "skills",
        ""
    )

    skills = parse_skills(
        skills_text
    )

    # --------------------------------------------------------
    # CERTIFICATIONS
    # --------------------------------------------------------

    certifications_text = sections.get(
        "certifications",
        ""
    )

    certifications = parse_certifications(
        certifications_text
    )

    # --------------------------------------------------------
    # ACHIEVEMENTS
    # --------------------------------------------------------

    achievements_text = sections.get(
        "achievements",
        ""
    )

    achievements = parse_achievements(
        achievements_text
    )

    # --------------------------------------------------------
    # FINAL STRUCTURED RESUME
    # --------------------------------------------------------

    return {
        "personal": personal,
        "summary": summary,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": skills,
        "certifications": certifications,
        "achievements": achievements
    }