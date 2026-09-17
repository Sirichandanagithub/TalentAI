# ============================================================
# ATS SCORER
# ============================================================
#
# Converts resume-job matching results into an ATS score.
#
# Scoring weights:
#   Required Skills : 50%
#   Preferred Skills: 15%
#   Experience      : 20%
#   Education       : 10%
#   Projects        : 5%
#
# Match confidence:
#   Exact   = 1.00
#   Related = 0.75
#   Unknown = 0.40
#
# IMPORTANT:
# Unknown does NOT mean missing.
# It means the resume does not provide enough evidence.
# ============================================================


# ============================================================
# SCORE CONFIGURATION
# ============================================================

REQUIRED_SKILLS_WEIGHT = 50
PREFERRED_SKILLS_WEIGHT = 15
EXPERIENCE_WEIGHT = 20
EDUCATION_WEIGHT = 10
PROJECT_WEIGHT = 5


EXACT_CONFIDENCE = 1.00
RELATED_CONFIDENCE = 0.75
UNKNOWN_CONFIDENCE = 0.40


# ============================================================
# MATCH CONFIDENCE
# ============================================================

def get_match_confidence(status: str) -> float:

    if status == "exact":
        return EXACT_CONFIDENCE

    if status == "related":
        return RELATED_CONFIDENCE

    if status == "unknown":
        return UNKNOWN_CONFIDENCE

    return 0.0


# ============================================================
# GENERIC SKILL SCORE
# ============================================================

def calculate_skill_score(
    matches: list,
    total_requirements: int
) -> float:

    if total_requirements == 0:
        return 1.0

    total_confidence = 0.0

    for match in matches:

        status = match.get(
            "status",
            "unknown"
        )

        total_confidence += get_match_confidence(
            status
        )

    return total_confidence / total_requirements


# ============================================================
# REQUIRED SKILLS SCORE
# ============================================================

def calculate_required_skills_score(
    skill_results: dict
) -> dict:

    required = skill_results.get(
        "required",
        {}
    )

    matched = required.get(
        "matched",
        []
    )

    unknown = required.get(
        "unknown",
        []
    )

    missing = required.get(
        "missing",
        []
    )

    total = (
        len(matched)
        + len(unknown)
        + len(missing)
    )

    if total == 0:

        return {
            "percentage": 100.0,
            "weighted_score": REQUIRED_SKILLS_WEIGHT,
            "matched": [],
            "unknown": [],
            "missing": []
        }

    # Existing resume_matcher currently stores
    # matched/unknown/missing as skill names.
    #
    # Exact matches receive 1.0.
    # Unknown matches receive 0.40.
    # Missing receives 0.0.

    score = (
        len(matched) * EXACT_CONFIDENCE
        + len(unknown) * UNKNOWN_CONFIDENCE
        + len(missing) * 0.0
    )

    percentage = (
        score / total
    ) * 100

    weighted_score = (
        percentage / 100
    ) * REQUIRED_SKILLS_WEIGHT

    return {
        "percentage": round(
            percentage,
            2
        ),
        "weighted_score": round(
            weighted_score,
            2
        ),
        "matched": matched,
        "unknown": unknown,
        "missing": missing
    }


# ============================================================
# PREFERRED SKILLS SCORE
# ============================================================

def calculate_preferred_skills_score(
    skill_results: dict
) -> dict:

    preferred = skill_results.get(
        "preferred",
        {}
    )

    matched = preferred.get(
        "matched",
        []
    )

    unknown = preferred.get(
        "unknown",
        []
    )

    total = (
        len(matched)
        + len(unknown)
    )

    if total == 0:

        return {
            "percentage": 100.0,
            "weighted_score": PREFERRED_SKILLS_WEIGHT,
            "matched": [],
            "unknown": []
        }

    score = (
        len(matched) * EXACT_CONFIDENCE
        + len(unknown) * UNKNOWN_CONFIDENCE
    )

    percentage = (
        score / total
    ) * 100

    weighted_score = (
        percentage / 100
    ) * PREFERRED_SKILLS_WEIGHT

    return {
        "percentage": round(
            percentage,
            2
        ),
        "weighted_score": round(
            weighted_score,
            2
        ),
        "matched": matched,
        "unknown": unknown
    }


# ============================================================
# EXPERIENCE SCORE
# ============================================================

def calculate_experience_score(
    experience_match: dict
) -> dict:

    status = experience_match.get(
        "status"
    )

    required_years = experience_match.get(
        "required_years"
    )

    candidate_years = experience_match.get(
        "candidate_years"
    )

    # No experience requirement
    if status == "not_required":

        return {
            "percentage": 100.0,
            "weighted_score": EXPERIENCE_WEIGHT,
            "status": "not_required"
        }

    # We cannot verify experience
    if status == "unknown":

        return {
            "percentage": UNKNOWN_CONFIDENCE * 100,
            "weighted_score": (
                UNKNOWN_CONFIDENCE
                * EXPERIENCE_WEIGHT
            ),
            "status": "unknown",
            "required_years": required_years,
            "candidate_years": candidate_years
        }

    # Requirement satisfied
    if status == "matched":

        return {
            "percentage": 100.0,
            "weighted_score": EXPERIENCE_WEIGHT,
            "status": "matched",
            "required_years": required_years,
            "candidate_years": candidate_years
        }

    # Requirement partially satisfied
    if status == "partial":

        if (
            not required_years
            or candidate_years is None
        ):

            percentage = UNKNOWN_CONFIDENCE * 100

        else:

            percentage = min(
                (
                    candidate_years
                    / required_years
                ) * 100,
                100
            )

        weighted_score = (
            percentage / 100
        ) * EXPERIENCE_WEIGHT

        return {
            "percentage": round(
                percentage,
                2
            ),
            "weighted_score": round(
                weighted_score,
                2
            ),
            "status": "partial",
            "required_years": required_years,
            "candidate_years": candidate_years
        }

    return {
        "percentage": 0.0,
        "weighted_score": 0.0,
        "status": status
    }


# ============================================================
# EDUCATION SCORE
# ============================================================

def calculate_education_score(
    education_match: dict
) -> dict:

    status = education_match.get(
        "status"
    )

    if status == "not_required":

        return {
            "percentage": 100.0,
            "weighted_score": EDUCATION_WEIGHT,
            "status": "not_required"
        }

    if status == "matched":

        return {
            "percentage": 100.0,
            "weighted_score": EDUCATION_WEIGHT,
            "status": "matched",
            "matched": education_match.get(
                "matched",
                []
            )
        }

    # Unknown education should reduce
    # confidence rather than become zero.

    if status == "unknown":

        return {
            "percentage": UNKNOWN_CONFIDENCE * 100,
            "weighted_score": (
                UNKNOWN_CONFIDENCE
                * EDUCATION_WEIGHT
            ),
            "status": "unknown",
            "matched": education_match.get(
                "matched",
                []
            ),
            "unknown": education_match.get(
                "unknown",
                []
            )
        }

    return {
        "percentage": 0.0,
        "weighted_score": 0.0,
        "status": status
    }


# ============================================================
# PROJECT SCORE
# ============================================================

def calculate_project_score(
    project_match: dict,
    required_skills: list
) -> dict:

    matched = project_match.get(
        "matched_skills",
        []
    )

    unknown = project_match.get(
        "unknown_skills",
        []
    )

    total = (
        len(matched)
        + len(unknown)
    )

    if total == 0:

        return {
            "percentage": 100.0,
            "weighted_score": PROJECT_WEIGHT,
            "matched": [],
            "unknown": []
        }

    score = (
        len(matched) * EXACT_CONFIDENCE
        + len(unknown) * UNKNOWN_CONFIDENCE
    )

    percentage = (
        score / total
    ) * 100

    weighted_score = (
        percentage / 100
    ) * PROJECT_WEIGHT

    return {
        "percentage": round(
            percentage,
            2
        ),
        "weighted_score": round(
            weighted_score,
            2
        ),
        "matched": matched,
        "unknown": unknown
    }


# ============================================================
# MASTER ATS SCORE
# ============================================================

def calculate_ats_score(
    match_result: dict
) -> dict:

    if not match_result:

        return {
            "ats_score": 0.0,
            "breakdown": {},
            "summary": {}
        }

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    required_score = calculate_required_skills_score(
        match_result.get(
            "skills",
            {}
        )
    )

    # --------------------------------------------------------
    # Preferred skills
    # --------------------------------------------------------

    preferred_score = calculate_preferred_skills_score(
        match_result.get(
            "skills",
            {}
        )
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience_score = calculate_experience_score(
        match_result.get(
            "experience",
            {}
        )
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    education_score = calculate_education_score(
        match_result.get(
            "education",
            {}
        )
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    project_score = calculate_project_score(
        match_result.get(
            "projects",
            {}
        ),
        match_result.get(
            "skills",
            {}
        ).get(
            "required",
            {}
        ).get(
            "matched",
            []
        )
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    total_score = (
        required_score["weighted_score"]
        + preferred_score["weighted_score"]
        + experience_score["weighted_score"]
        + education_score["weighted_score"]
        + project_score["weighted_score"]
    )

    total_score = min(
        max(total_score, 0.0),
        100.0
    )

    # --------------------------------------------------------
    # Return detailed result
    # --------------------------------------------------------

    return {

        "ats_score": round(
            total_score,
            2
        ),

        "breakdown": {

            "required_skills": required_score,

            "preferred_skills": preferred_score,

            "experience": experience_score,

            "education": education_score,

            "projects": project_score
        },

        "summary": {

            "job_title":
                match_result.get(
                    "job_title"
                ),

            "total_score":
                round(
                    total_score,
                    2
                )
        }
    }