import re


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
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill: str) -> str:

    return normalize_text(skill)


# ============================================================
# COLLECT RESUME SKILLS
# ============================================================

def collect_resume_skills(resume: dict) -> list:

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

    # Also collect technologies from projects
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

    # Remove duplicates while preserving order
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

    resume_map = {
        normalize_skill(skill): skill
        for skill in resume_skills
    }

    required_matches = []
    required_missing = []
    required_unknown = []

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    for skill in required_skills:

        normalized = normalize_skill(
            skill
        )

        if normalized in resume_map:

            required_matches.append(
                skill
            )

        else:

            # At this stage we cannot know whether
            # the candidate actually has the skill.
            # The resume simply doesn't mention it.
            required_unknown.append(
                skill
            )

    # --------------------------------------------------------
    # Preferred skills
    # --------------------------------------------------------

    preferred_matches = []
    preferred_unknown = []

    for skill in preferred_skills:

        normalized = normalize_skill(
            skill
        )

        if normalized in resume_map:

            preferred_matches.append(
                skill
            )

        else:

            preferred_unknown.append(
                skill
            )

    return {
        "required": {
            "matched": required_matches,
            "unknown": required_unknown,
            "missing": required_missing
        },

        "preferred": {
            "matched": preferred_matches,
            "unknown": preferred_unknown
        }
    }


# ============================================================
# EXPERIENCE MATCHING
# ============================================================

def extract_resume_experience_years(
    resume: dict
):

    if not resume:
        return None

    experiences = resume.get(
        "experience",
        []
    )

    if not isinstance(
        experiences,
        list
    ):
        return None

    # --------------------------------------------------------
    # We currently do NOT calculate years automatically.
    #
    # The resume parser currently gives us dates such as:
    #
    # {'start': 'April 2025', 'end': None}
    #
    # We don't yet have enough information to reliably
    # calculate total experience for every resume format.
    # --------------------------------------------------------

    if not experiences:

        return None

    return None


def match_experience(
    resume: dict,
    required_experience: dict | None
) -> dict:

    if not required_experience:

        return {
            "status": "not_required",
            "required_years": None,
            "candidate_years": None
        }

    required_years = required_experience.get(
        "minimum_years"
    )

    if required_years is None:

        return {
            "status": "unknown",
            "required_years": None,
            "candidate_years": None
        }

    candidate_years = extract_resume_experience_years(
        resume
    )

    # --------------------------------------------------------
    # We don't invent experience.
    # --------------------------------------------------------

    if candidate_years is None:

        return {
            "status": "unknown",
            "required_years": required_years,
            "candidate_years": None
        }

    if candidate_years >= required_years:

        status = "matched"

    else:

        status = "partial"

    return {
        "status": status,
        "required_years": required_years,
        "candidate_years": candidate_years
    }


# ============================================================
# EDUCATION MATCHING
# ============================================================

def match_education(
    resume: dict,
    required_education: list
) -> dict:

    if not required_education:

        return {
            "status": "not_required",
            "matched": [],
            "unknown": []
        }

    education_entries = resume.get(
        "education",
        []
    )

    if not education_entries:

        return {
            "status": "unknown",
            "matched": [],
            "unknown": required_education
        }

    resume_text_parts = []

    for education in education_entries:

        if not isinstance(
            education,
            dict
        ):
            continue

        for key in [
            "institution",
            "program",
            "location"
        ]:

            value = education.get(
                key
            )

            if value:

                resume_text_parts.append(
                    str(value)
                )

    resume_text = normalize_text(
        " ".join(
            resume_text_parts
        )
    )

    matched = []
    unknown = []

    for requirement in required_education:

        normalized = normalize_text(
            requirement
        )

        if normalized in resume_text:

            matched.append(
                requirement
            )

        else:

            unknown.append(
                requirement
            )

    if matched:

        status = "matched"

    else:

        status = "unknown"

    return {
        "status": status,
        "matched": matched,
        "unknown": unknown
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

    # --------------------------------------------------------
    # Resume skills
    # --------------------------------------------------------

    resume_skills = collect_resume_skills(
        resume
    )

    # --------------------------------------------------------
    # Job skills
    # --------------------------------------------------------

    required_skills = job_description.get(
        "required_skills",
        []
    )

    preferred_skills = job_description.get(
        "preferred_skills",
        []
    )

    # --------------------------------------------------------
    # Skill matching
    # --------------------------------------------------------

    skill_matches = match_skills(
        resume_skills,
        required_skills,
        preferred_skills
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience_match = match_experience(
        resume,
        job_description.get(
            "experience"
        )
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    education_match = match_education(
        resume,
        job_description.get(
            "education",
            []
        )
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    project_match = match_projects(
        resume,
        required_skills
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

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