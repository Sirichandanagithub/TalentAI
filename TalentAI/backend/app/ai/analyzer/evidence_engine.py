import re
from typing import Any, Dict, List


# ============================================================
# EVIDENCE WEIGHTS
# ============================================================

EVIDENCE_WEIGHTS = {
    "experience": 1.00,
    "project": 0.95,
    "skills": 0.90,
    "certification": 0.80,
    "education": 0.60,
    "summary": 0.50,
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: Any) -> str:

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9+#.\- ]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SAFE LIST
# ============================================================

def safe_list(value: Any) -> List:

    if isinstance(value, list):
        return value

    if value is None:
        return []

    return [value]


# ============================================================
# EXACT TEXT MATCH
# ============================================================

def contains_requirement(
    requirement: str,
    text: str
) -> bool:

    requirement_normalized = normalize_text(
        requirement
    )

    text_normalized = normalize_text(
        text
    )

    if not requirement_normalized:
        return False

    if not text_normalized:
        return False

    # --------------------------------------------------------
    # Word-boundary matching
    # --------------------------------------------------------

    pattern = (
        r"(?<!\w)"
        + re.escape(requirement_normalized)
        + r"(?!\w)"
    )

    if re.search(
        pattern,
        text_normalized,
        re.IGNORECASE
    ):
        return True

    return False


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {
    "python": [
        "python",
        "py"
    ],

    "javascript": [
        "javascript",
        "java script",
        "js"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn",
        "scikit_learn"
    ],

    "pandas": [
        "pandas",
        "panda"
    ],

    "data analysis": [
        "data analysis",
        "data analytics"
    ],

    "sql": [
        "sql"
    ],

    "tensorflow": [
        "tensorflow"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ]
}


# ============================================================
# REQUIREMENT ALIAS MATCH
# ============================================================

def requirement_matches_text(
    requirement: str,
    text: str
) -> bool:

    # First try exact matching
    if contains_requirement(
        requirement,
        text
    ):
        return True

    normalized_requirement = normalize_text(
        requirement
    )

    aliases = SKILL_ALIASES.get(
        normalized_requirement,
        []
    )

    for alias in aliases:

        if contains_requirement(
            alias,
            text
        ):
            return True

    return False


# ============================================================
# EXTRACT TEXT FROM VALUE
# ============================================================

def value_to_text(value: Any) -> str:

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, list):

        parts = []

        for item in value:

            text = value_to_text(item)

            if text:
                parts.append(text)

        return " ".join(parts)

    if isinstance(value, dict):

        parts = []

        for key, item in value.items():

            # Include both key and value only when useful.
            # This allows structured resume sections to be
            # searched correctly.

            if key == "raw_text":

                parts.append(
                    value_to_text(item)
                )

            else:

                parts.append(
                    value_to_text(item)
                )

        return " ".join(parts)

    return str(value)


# ============================================================
# FLATTEN STRUCTURED SKILLS
# ============================================================

def flatten_skills(
    skills: Any
) -> List[str]:

    flattened = []

    if skills is None:
        return flattened

    # --------------------------------------------------------
    # Flat list
    # --------------------------------------------------------

    if isinstance(skills, list):

        for skill in skills:

            if isinstance(skill, dict):

                skill_name = (
                    skill.get("skill")
                    or skill.get("name")
                    or skill.get("technology")
                    or ""
                )

                if skill_name:
                    flattened.append(
                        str(skill_name)
                    )

            else:

                skill_text = str(skill).strip()

                if skill_text:
                    flattened.append(
                        skill_text
                    )

        return flattened

    # --------------------------------------------------------
    # Structured dictionary
    #
    # Example:
    #
    # {
    #     "programming_languages": ["Python"],
    #     "data_science": ["Data Analysis"],
    #     "machine_learning": ["Deep Learning"]
    # }
    # --------------------------------------------------------

    if isinstance(skills, dict):

        for category, values in skills.items():

            if isinstance(values, list):

                for value in values:

                    if value:
                        flattened.append(
                            str(value)
                        )

            elif values:

                flattened.append(
                    str(values)
                )

        return flattened

    # --------------------------------------------------------
    # Single value
    # --------------------------------------------------------

    flattened.append(
        str(skills)
    )

    return flattened


# ============================================================
# SEARCH SKILLS
# ============================================================

def find_skill_evidence(
    requirement: str,
    skills: Any
) -> List[Dict]:

    evidence = []

    flattened_skills = flatten_skills(
        skills
    )

    for skill_name in flattened_skills:

        if requirement_matches_text(
            requirement,
            skill_name
        ):

            evidence.append(
                {
                    "source": "skills",
                    "text": skill_name,
                    "weight": EVIDENCE_WEIGHTS["skills"]
                }
            )

    return evidence


# ============================================================
# SEARCH PROJECTS
# ============================================================

def find_project_evidence(
    requirement: str,
    projects: Any
) -> List[Dict]:

    evidence = []

    for project in safe_list(projects):

        if isinstance(project, dict):

            project_name = project.get(
                "project_name",
                ""
            )

            description = project.get(
                "description",
                ""
            )

            raw_text = project.get(
                "raw_text",
                ""
            )

            technologies = project.get(
                "technologies",
                []
            )

            project_text = " ".join(
                [
                    value_to_text(project_name),
                    value_to_text(description),
                    value_to_text(raw_text),
                    value_to_text(technologies)
                ]
            )

        else:

            project_text = str(project)

            project_name = ""

        if requirement_matches_text(
            requirement,
            project_text
        ):

            evidence.append(
                {
                    "source": "project",
                    "project": project_name,
                    "text": project_text.strip(),
                    "weight": EVIDENCE_WEIGHTS["project"]
                }
            )

    return evidence


# ============================================================
# SEARCH EXPERIENCE
# ============================================================

def find_experience_evidence(
    requirement: str,
    experiences: Any
) -> List[Dict]:

    evidence = []

    for experience in safe_list(experiences):

        if isinstance(experience, dict):

            job_title = experience.get(
                "job_title",
                ""
            )

            company = experience.get(
                "company",
                ""
            )

            description = experience.get(
                "description",
                ""
            )

            raw_text = experience.get(
                "raw_text",
                ""
            )

            experience_text = " ".join(
                [
                    value_to_text(job_title),
                    value_to_text(company),
                    value_to_text(description),
                    value_to_text(raw_text)
                ]
            )

        else:

            experience_text = str(
                experience
            )

            job_title = ""
            company = ""

        if requirement_matches_text(
            requirement,
            experience_text
        ):

            evidence.append(
                {
                    "source": "experience",
                    "job_title": job_title,
                    "company": company,
                    "text": experience_text.strip(),
                    "weight": EVIDENCE_WEIGHTS["experience"]
                }
            )

    return evidence


# ============================================================
# SEARCH CERTIFICATIONS
# ============================================================

def find_certification_evidence(
    requirement: str,
    certifications: Any
) -> List[Dict]:

    evidence = []

    for certification in safe_list(
        certifications
    ):

        if isinstance(certification, dict):

            name = certification.get(
                "certification_name",
                ""
            )

            issuer = certification.get(
                "issuer",
                ""
            )

            description = certification.get(
                "description",
                ""
            )

            raw_text = certification.get(
                "raw_text",
                ""
            )

            certification_text = " ".join(
                [
                    value_to_text(name),
                    value_to_text(issuer),
                    value_to_text(description),
                    value_to_text(raw_text)
                ]
            )

        else:

            certification_text = str(
                certification
            )

            name = ""
            issuer = ""

        if requirement_matches_text(
            requirement,
            certification_text
        ):

            evidence.append(
                {
                    "source": "certification",
                    "certification": name,
                    "issuer": issuer,
                    "text": certification_text.strip(),
                    "weight": EVIDENCE_WEIGHTS[
                        "certification"
                    ]
                }
            )

    return evidence


# ============================================================
# SEARCH EDUCATION
# ============================================================

def find_education_evidence(
    requirement: str,
    education: Any
) -> List[Dict]:

    evidence = []

    for item in safe_list(education):

        text = value_to_text(
            item
        )

        if requirement_matches_text(
            requirement,
            text
        ):

            evidence.append(
                {
                    "source": "education",
                    "text": text.strip(),
                    "weight": EVIDENCE_WEIGHTS[
                        "education"
                    ]
                }
            )

    return evidence


# ============================================================
# SEARCH SUMMARY
# ============================================================

def find_summary_evidence(
    requirement: str,
    summary: Any
) -> List[Dict]:

    if not summary:
        return []

    summary_text = value_to_text(
        summary
    )

    if requirement_matches_text(
        requirement,
        summary_text
    ):

        return [
            {
                "source": "summary",
                "text": summary_text.strip(),
                "weight": EVIDENCE_WEIGHTS[
                    "summary"
                ]
            }
        ]

    return []


# ============================================================
# COLLECT ALL EVIDENCE
# ============================================================

def collect_evidence(
    requirement: str,
    resume: Dict
) -> Dict:

    if not requirement:

        return {
            "requirement": requirement,
            "evidence": [],
            "evidence_count": 0,
            "best_source": None,
            "evidence_strength": 0.0,
            "status": "not_found"
        }

    if not isinstance(
        resume,
        dict
    ):

        return {
            "requirement": requirement,
            "evidence": [],
            "evidence_count": 0,
            "best_source": None,
            "evidence_strength": 0.0,
            "status": "not_found"
        }

    evidence = []

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    evidence.extend(
        find_skill_evidence(
            requirement,
            resume.get(
                "skills",
                []
            )
        )
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    evidence.extend(
        find_project_evidence(
            requirement,
            resume.get(
                "projects",
                []
            )
        )
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    evidence.extend(
        find_experience_evidence(
            requirement,
            resume.get(
                "experience",
                []
            )
        )
    )

    # --------------------------------------------------------
    # Certifications
    # --------------------------------------------------------

    evidence.extend(
        find_certification_evidence(
            requirement,
            resume.get(
                "certifications",
                []
            )
        )
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    evidence.extend(
        find_education_evidence(
            requirement,
            resume.get(
                "education",
                []
            )
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    evidence.extend(
        find_summary_evidence(
            requirement,
            resume.get(
                "summary",
                ""
            )
        )
    )

    # --------------------------------------------------------
    # Sort strongest evidence first
    # --------------------------------------------------------

    evidence.sort(
        key=lambda item: item.get(
            "weight",
            0.0
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    if not evidence:

        return {
            "requirement": requirement,
            "evidence": [],
            "evidence_count": 0,
            "best_source": None,
            "evidence_strength": 0.0,
            "status": "not_found"
        }

    # --------------------------------------------------------
    # Best evidence
    # --------------------------------------------------------

    best_weight = evidence[0].get(
        "weight",
        0.0
    )

    best_source = evidence[0].get(
        "source"
    )

    # --------------------------------------------------------
    # Evidence strength
    #
    # Multiple independent sources increase confidence,
    # but the value is capped at 1.0.
    # --------------------------------------------------------

    source_weights = []

    seen_sources = set()

    for item in evidence:

        source = item.get(
            "source"
        )

        if source not in seen_sources:

            source_weights.append(
                item.get(
                    "weight",
                    0.0
                )
            )

            seen_sources.add(
                source
            )

    evidence_strength = min(
        sum(source_weights) / 2.0,
        1.0
    )

    return {
        "requirement": requirement,
        "evidence": evidence,
        "evidence_count": len(evidence),
        "best_source": best_source,
        "best_weight": best_weight,
        "evidence_strength": round(
            evidence_strength,
            4
        ),
        "status": "found"
    }


# ============================================================
# BATCH EVIDENCE
# ============================================================

def collect_evidence_for_requirements(
    requirements: List[str],
    resume: Dict
) -> List[Dict]:

    if not requirements:
        return []

    results = []

    for requirement in requirements:

        results.append(
            collect_evidence(
                requirement,
                resume
            )
        )

    return results


# ============================================================
# EVIDENCE ENGINE CLASS
# ============================================================

class EvidenceEngine:
    """
    Object-oriented wrapper around the evidence functions.

    The underlying evidence collection logic remains in:

        collect_evidence()
        collect_evidence_for_requirements()

    This class provides a clean interface for TalentMatchEngine.
    """

    def find_evidence(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        return collect_evidence(
            requirement,
            resume
        )

    def find(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        return collect_evidence(
            requirement,
            resume
        )

    def find_multiple(
        self,
        requirements: List[str],
        resume: Dict
    ) -> List[Dict]:

        return collect_evidence_for_requirements(
            requirements,
            resume
        )