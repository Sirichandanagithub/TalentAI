from typing import Dict, List, Optional


# ============================================================
# ATS SCORE WEIGHTS
# ============================================================

SKILL_WEIGHT = 40
EXPERIENCE_WEIGHT = 25
EDUCATION_WEIGHT = 15
PROJECT_WEIGHT = 15
PREFERRED_WEIGHT = 5


# ============================================================
# SCORE HELPERS
# ============================================================

def clamp_score(score: float) -> float:
    """
    Keep score between 0 and 100.
    """
    return round(
        max(0.0, min(100.0, score)),
        2
    )


# ============================================================
# SKILL SCORE
# ============================================================

def calculate_skill_score(
    skill_result: Dict
) -> Optional[float]:

    if not skill_result:
        return None

    matched = skill_result.get(
        "matched",
        []
    )

    possible = skill_result.get(
        "possible",
        []
    )

    unknown = skill_result.get(
        "unknown",
        []
    )

    total = (
        len(matched)
        + len(possible)
        + len(unknown)
    )

    if total == 0:
        return None

    matched_score = sum(
        float(item.get("confidence", 0.0))
        for item in matched
    )

    possible_score = sum(
        float(item.get("confidence", 0.0)) * 0.5
        for item in possible
    )

    score = (
        matched_score
        + possible_score
    ) / total

    return clamp_score(
        score * 100
    )


# ============================================================
# EXPERIENCE SCORE
# ============================================================

def calculate_experience_score(
    experience_result: Dict
) -> Optional[float]:

    if not experience_result:
        return 0.0

    status = experience_result.get(
        "status"
    )

    required = experience_result.get(
        "required_years"
    )

    candidate = experience_result.get(
        "candidate_years"
    )

    # --------------------------------------------------------
    # No experience requirement
    # --------------------------------------------------------

    if status == "not_required":
        return 100.0

    # --------------------------------------------------------
    # Experience cannot be determined
    #
    # IMPORTANT:
    # "unknown" does NOT mean 0 years.
    # It means the resume does not contain enough
    # reliable information to calculate experience.
    #
    # Returning None allows the ATS engine to exclude
    # this component from the weighted calculation.
    # --------------------------------------------------------

    if status == "unknown":
        return None

    # --------------------------------------------------------
    # Invalid / incomplete experience data
    # --------------------------------------------------------

    if required is None or candidate is None:
        return None

    # --------------------------------------------------------
    # No actual experience requirement
    # --------------------------------------------------------

    if required <= 0:
        return 100.0

    # --------------------------------------------------------
    # Candidate meets requirement
    # --------------------------------------------------------

    if candidate >= required:
        return 100.0

    # --------------------------------------------------------
    # Candidate has partial experience
    # --------------------------------------------------------

    score = (
        candidate / required
    ) * 100

    return clamp_score(
        score
    )


# ============================================================
# EDUCATION SCORE
# ============================================================

def calculate_education_score(
    education_result: Dict
) -> Optional[float]:

    if not education_result:
        return None

    status = education_result.get("status")

    matched = education_result.get("matched", [])
    not_matched = education_result.get("not_matched", [])
    unknown = education_result.get("unknown", [])

    # No education requirement.
    if status == "not_required":
        return 100.0

    # Count only requirements with sufficient evidence.
    evaluated_total = len(matched) + len(not_matched)

    # All requirements are unknown.
    if evaluated_total == 0:
        return None

    # Exact = 100%, Related = 85%.
    matched_score = sum(
        float(item.get("confidence", 0.0))
        for item in matched
    )

    # Confirmed not_matched requirements contribute zero.
    score = matched_score / evaluated_total

    return clamp_score(score * 100)


# ============================================================
# PROJECT SCORE
# ============================================================


def calculate_project_score(
    project_result: Dict
) -> Optional[float]:
    """
    Calculate project score using:
    - Required skill coverage: 50%
    - Project relevance: 35%
    - Evidence confidence: 15%

    Stronger relevant projects receive greater contribution.
    Completely unrelated projects are excluded.
    """

    if not isinstance(project_result, dict):
        return None

    project_details = project_result.get(
        "project_details", []
    )

    if not isinstance(project_details, list) or not project_details:
        return None

    valid_projects = [
        project
        for project in project_details
        if isinstance(project, dict)
    ]

    if not valid_projects:
        return None

    # --------------------------------------------------------
    # NORMALIZE AND VALIDATE PROJECT METRICS
    # --------------------------------------------------------

    evaluated_projects = []

    for project in valid_projects:

        try:
            coverage = float(
                project.get("required_skill_score", 0.0) or 0.0
            )

            relevance = float(
                project.get("relevance_score", 0.0) or 0.0
            )

            confidence = float(
                project.get("evidence_confidence", 0.0) or 0.0
            )

        except (TypeError, ValueError):
            continue

        # Project metrics are expected in the range 0 to 1.
        coverage = max(0.0, min(coverage, 1.0))
        relevance = max(0.0, min(relevance, 1.0))
        confidence = max(0.0, min(confidence, 1.0))

        # Exclude projects with absolutely no job-related evidence.
        if (
            coverage == 0.0
            and relevance == 0.0
            and confidence == 0.0
        ):
            continue

        evaluated_projects.append({
            "coverage": coverage,
            "relevance": relevance,
            "confidence": confidence,
        })

    if not evaluated_projects:
        return None

    # --------------------------------------------------------
    # RANK PROJECTS BY RELEVANCE
    # --------------------------------------------------------

        # --------------------------------------------------------
    # RANK PROJECTS BY INDIVIDUAL PROJECT SCORE
    # --------------------------------------------------------

    for project in evaluated_projects:
        project["individual_score"] = (
            project["coverage"] * 50
            + project["relevance"] * 35
            + project["confidence"] * 15
        )

    evaluated_projects.sort(
        key=lambda project: project["individual_score"],
        reverse=True,
    )

    # --------------------------------------------------------
    # CONTROLLED PROJECT CONTRIBUTION
    #
    # First project: 60%
    # Second project: 25%
    # Third project: 10%
    # Remaining projects: 5% collectively
    # --------------------------------------------------------

    contribution_weights = []

    for index in range(len(evaluated_projects)):

        if index == 0:
            contribution_weights.append(0.60)

        elif index == 1:
            contribution_weights.append(0.25)

        elif index == 2:
            contribution_weights.append(0.10)

        else:
            contribution_weights.append(
                0.05 / (len(evaluated_projects) - 3)
            )

    total_weight = sum(contribution_weights)

    contribution_weights = [
        weight / total_weight
        for weight in contribution_weights
    ]

    # --------------------------------------------------------
    # CALCULATE WEIGHTED PROJECT COMPONENTS
    # --------------------------------------------------------

    weighted_coverage = 0.0
    weighted_relevance = 0.0
    weighted_confidence = 0.0

    for project, weight in zip(
        evaluated_projects,
        contribution_weights,
    ):

        weighted_coverage += (
            project["coverage"] * weight
        )

        weighted_relevance += (
            project["relevance"] * weight
        )

        weighted_confidence += (
            project["confidence"] * weight
        )

    # --------------------------------------------------------
    # FINAL PROJECT SCORE
    # --------------------------------------------------------

    project_score = (
        weighted_coverage * 50
        + weighted_relevance * 35
        + weighted_confidence * 15
    )

    return clamp_score(project_score)




def calculate_preferred_score(
    preferred_result: Dict
) -> Optional[float]:

    if not preferred_result:
        return None

    matched = preferred_result.get("matched", [])
    possible = preferred_result.get("possible", [])
    unknown = preferred_result.get("unknown", [])

    total = len(matched) + len(possible) + len(unknown)

    # No preferred skills were evaluated.
    if total == 0:
        return None

    matched_score = sum(
        float(item.get("confidence", 0.0))
        for item in matched
    )

    possible_score = sum(
        float(item.get("confidence", 0.0)) * 0.5
        for item in possible
    )

    return clamp_score(
        (matched_score + possible_score) / total * 100
    )



# ============================================================
# FINAL ATS SCORE
# ============================================================

def calculate_ats_score(
    match_result: Dict
) -> Dict:

    if not match_result:
        return {
            "score": 0.0,
            "breakdown": {},
            "classification": "poor"
        }

    skills_result = match_result.get(
        "skills",
        {}
    )

    required_skills = skills_result.get(
        "required",
        {}
    )

    preferred_skills = skills_result.get(
        "preferred",
        {}
    )

    experience_result = match_result.get(
        "experience",
        {}
    )

    education_result = match_result.get(
        "education",
        {}
    )

    project_result = match_result.get(
        "projects",
        {}
    )

    # --------------------------------------------------------
    # Individual scores
    # --------------------------------------------------------

    skill_score = calculate_skill_score(
        required_skills
    )

    experience_score = calculate_experience_score(
        experience_result
    )

    education_score = calculate_education_score(
        education_result
    )

    project_score = calculate_project_score(
        project_result
    )

    preferred_score = calculate_preferred_score(
        preferred_skills
    )

    # --------------------------------------------------------
    # Weighted final score
    #
    # Unknown components are excluded from the calculation.
    # Their weight is redistributed proportionally among
    # the components that have a reliable score.
    # --------------------------------------------------------

    score_components = {
        "skills": (
            skill_score,
            SKILL_WEIGHT
        ),

        "experience": (
            experience_score,
            EXPERIENCE_WEIGHT
        ),

        "education": (
            education_score,
            EDUCATION_WEIGHT
        ),

        "projects": (
            project_score,
            PROJECT_WEIGHT
        ),

        "preferred_skills": (
            preferred_score,
            PREFERRED_WEIGHT
        )
    }

    # Keep only components with a valid score
    valid_components = {
        name: (score, weight)
        for name, (score, weight)
        in score_components.items()
        if score is not None
    }

    # Total weight of components that can be evaluated
    total_weight = sum(
        weight
        for score, weight
        in valid_components.values()
    )

    if total_weight == 0:

        final_score = 0.0

    else:

        final_score = sum(
            score * weight
            for score, weight
            in valid_components.values()
        ) / total_weight

    final_score = clamp_score(
        final_score
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    if final_score >= 80:

        classification = "excellent"

    elif final_score >= 65:

        classification = "strong"

    elif final_score >= 50:

        classification = "moderate"

    elif final_score >= 35:

        classification = "weak"

    else:

        classification = "poor"

    # --------------------------------------------------------
    # Breakdown
    #
    # None is preserved for unknown components so the output
    # clearly communicates that the value was not determinable.
    # --------------------------------------------------------

    return {
        "score": final_score,

        "breakdown": {
            "skills": (
                round(skill_score, 2)
                if skill_score is not None
                else None
            ),

            "experience": (
                round(experience_score, 2)
                if experience_score is not None
                else None
            ),

            "education": (
                round(education_score, 2)
                if education_score is not None
                else None
            ),

            "projects": (
                round(project_score, 2)
                if project_score is not None
                else None
            ),

            "preferred_skills": (
                round(preferred_score, 2)
                if preferred_score is not None
                else None
            )
        },

        "weights": {
            "skills": SKILL_WEIGHT,
            "experience": EXPERIENCE_WEIGHT,
            "education": EDUCATION_WEIGHT,
            "projects": PROJECT_WEIGHT,
            "preferred_skills": PREFERRED_WEIGHT
        },

        "classification": classification
    }


# ============================================================
# MISSING REQUIREMENTS
# ============================================================

def extract_missing_requirements(
    match_result: Dict
) -> List[str]:

    missing = []

    if not match_result:
        return missing

    skills = match_result.get(
        "skills",
        {}
    )

    required = skills.get(
        "required",
        {}
    )

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    for item in required.get(
        "unknown",
        []
    ):

        requirement = item.get(
            "requirement"
        )

        if requirement:

            missing.append(
                requirement
            )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience = match_result.get(
        "experience",
        {}
    )

    if experience.get(
        "status"
    ) in [
        "partial",
        "missing"
    ]:

        required_years = experience.get(
            "required_years"
        )

        if required_years is not None:

            missing.append(
                f"{required_years}+ years experience"
            )

    # --------------------------------------------------------
    # Preferred skills are NOT considered
    # mandatory missing requirements.
    # --------------------------------------------------------

    return missing


# ============================================================
# MATCHED REQUIREMENTS
# ============================================================

def extract_matched_requirements(
    match_result: Dict
) -> List[str]:

    matched = []

    if not match_result:
        return matched

    skills = match_result.get(
        "skills",
        {}
    )

    required = skills.get(
        "required",
        {}
    )

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    for item in required.get(
        "matched",
        []
    ):

        requirement = item.get(
            "requirement"
        )

        if requirement:

            matched.append(
                requirement
            )

    return matched


# ============================================================
# SCORE SUMMARY
# ============================================================

def generate_score_summary(
    match_result: Dict
) -> Dict:

    score_result = calculate_ats_score(
        match_result
    )

    return {
        "ats_score": score_result[
            "score"
        ],

        "classification": score_result[
            "classification"
        ],

        "breakdown": score_result[
            "breakdown"
        ],

        "matched_requirements":
            extract_matched_requirements(
                match_result
            ),

        "missing_requirements":
            extract_missing_requirements(
                match_result
            )
    }