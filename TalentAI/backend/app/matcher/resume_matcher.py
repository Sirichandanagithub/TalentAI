import re

from app.matcher.semantic_matcher import (
    match_concept,
    match_requirements
)

from app.matcher.experience_matcher import (
    match_experience
)

from app.matcher.education_matcher import (
    match_education
)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    # Normalize common variations
    text = text.replace("-", " ")
    text = text.replace("_", " ")

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return normalize_text_basic(text)


def normalize_text_basic(text: str) -> str:

    if not text:
        return ""

    return text.strip()


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill: str) -> str:

    return normalize_text(
        skill
    )


# ============================================================
# COLLECT RESUME SKILLS
# ============================================================

def collect_resume_skills(
    resume: dict
) -> list:

    if not resume:
        return []

    skills_section = resume.get(
        "skills",
        {}
    )

    if not isinstance(
        skills_section,
        dict
    ):
        return []

    all_skills = []

    for category, skills in skills_section.items():

        if not isinstance(
            skills,
            list
        ):
            continue

        all_skills.extend(
            skills
        )

    # --------------------------------------------------------
    # Also collect technologies from projects
    # --------------------------------------------------------

    projects = resume.get(
        "projects",
        []
    )

    if isinstance(
        projects,
        list
    ):

        for project in projects:

            if not isinstance(
                project,
                dict
            ):
                continue

            technologies = project.get(
                "technologies",
                []
            )

            if isinstance(
                technologies,
                list
            ):

                all_skills.extend(
                    technologies
                )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    unique_skills = []

    seen = set()

    for skill in all_skills:

        if not isinstance(
            skill,
            str
        ):
            continue

        normalized = normalize_skill(
            skill
        )

        if not normalized:
            continue

        if normalized not in seen:

            seen.add(
                normalized
            )

            unique_skills.append(
                skill
            )

    return unique_skills


# ============================================================
# MATCH SKILLS
# ============================================================

def match_skills(
    resume_skills: list,
    required_skills: list,
    preferred_skills: list
) -> dict:

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    required_results = match_requirements(
        required_skills,
        resume_skills
    )

    # --------------------------------------------------------
    # Preferred skills
    # --------------------------------------------------------

    preferred_results = match_requirements(
        preferred_skills,
        resume_skills
    )

    # --------------------------------------------------------
    # Separate required results
    # --------------------------------------------------------

    required_matched = []
    required_unknown = []

    for result in required_results:

        if result["status"] in [
            "exact",
            "related"
        ]:

            required_matched.append(
                result
            )

        else:

            required_unknown.append(
                result
            )

    # --------------------------------------------------------
    # Separate preferred results
    # --------------------------------------------------------

    preferred_matched = []
    preferred_unknown = []

    for result in preferred_results:

        if result["status"] in [
            "exact",
            "related"
        ]:

            preferred_matched.append(
                result
            )

        else:

            preferred_unknown.append(
                result
            )

    return {

        "required": {

            "matched":
                required_matched,

            "unknown":
                required_unknown,

            "missing": []
        },

        "preferred": {

            "matched":
                preferred_matched,

            "unknown":
                preferred_unknown
        }
    }


# ============================================================
# PROJECT MATCHING
# ============================================================

def match_projects(
    resume: dict,
    required_skills: list
) -> dict:

    projects = resume.get(
        "projects",
        []
    )

    if not projects:

        return {
            "matched_skills": [],
            "unknown_skills": required_skills
        }

    project_text = []

    for project in projects:

        if not isinstance(
            project,
            dict
        ):
            continue

        project_name = project.get(
            "project_name"
        )

        description = project.get(
            "description"
        )

        technologies = project.get(
            "technologies",
            []
        )

        if project_name:

            project_text.append(
                str(project_name)
            )

        if description:

            project_text.append(
                str(description)
            )

        if isinstance(
            technologies,
            list
        ):

            project_text.extend(
                str(item)
                for item in technologies
            )

    project_text = normalize_text(
        " ".join(project_text)
    )

    matched = []
    unknown = []

    for skill in required_skills:

        normalized = normalize_skill(
            skill
        )

        if normalized in project_text:

            matched.append(
                skill
            )

        else:

            unknown.append(
                skill
            )

    return {
        "matched_skills": matched,
        "unknown_skills": unknown
    }


# ============================================================
# MASTER MATCHER
# ============================================================

def match_resume_to_job(
    resume: dict,
    job_description: dict
) -> dict:

    if not resume:
        resume = {}

    if not job_description:
        job_description = {}

    # ========================================================
    # RESUME SKILLS
    # ========================================================

    resume_skills = collect_resume_skills(
        resume
    )

    # ========================================================
    # JOB SKILLS
    # ========================================================

    required_skills = job_description.get(
        "required_skills",
        []
    )

    preferred_skills = job_description.get(
        "preferred_skills",
        []
    )

    # ========================================================
    # SKILL MATCHING
    # ========================================================

    skill_matches = match_skills(
        resume_skills,
        required_skills,
        preferred_skills
    )

    # ========================================================
    # EXPERIENCE MATCHING
    # ========================================================

    experience_match = match_experience(
        resume,
        job_description.get(
            "experience"
        )
    )

    # ========================================================
    # EDUCATION MATCHING
    # ========================================================

    education_match = match_education(
        resume,
        job_description.get(
            "education",
            []
        )
    )

    # ========================================================
    # PROJECT MATCHING
    # ========================================================

    project_match = match_projects(
        resume,
        required_skills
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "job_title":
            job_description.get(
                "job_title"
            ),

        "resume_skills":
            resume_skills,

        "skills":
            skill_matches,

        "experience":
            experience_match,

        "education":
            education_match,

        "projects":
            project_match
    }