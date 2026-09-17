import re
from typing import Dict, List

from app.matcher.experience_matcher import (
    extract_experience_period,
    calculate_month_difference,
    months_to_years,
)


class SkillExperienceMatcher:
    """
    Analyzes how much practical experience a candidate has
    with a specific skill.

    Sources considered:
        1. Professional experience
        2. Projects
        3. Certifications
        4. Education
        5. Main skills section

    The main goal is to distinguish:

        Skill exists
        vs
        Skill has practical experience
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):

        # Small alias map so common variations are handled.
        self.skill_aliases = {
            "python": [
                "python",
                "python3",
                "py",
            ],
            "sql": [
                "sql",
                "mysql",
                "postgresql",
                "postgres",
            ],
            "machine learning": [
                "machine learning",
                "ml",
                "machine-learning",
            ],
            "deep learning": [
                "deep learning",
                "dl",
            ],
            "artificial intelligence": [
                "artificial intelligence",
                "ai",
            ],
            "data science": [
                "data science",
                "data scientist",
            ],
            "data analysis": [
                "data analysis",
                "data analytics",
                "data analyst",
            ],
            "pandas": [
                "pandas",
            ],
            "scikit-learn": [
                "scikit-learn",
                "scikit learn",
                "sklearn",
            ],
            "tensorflow": [
                "tensorflow",
            ],
            "pytorch": [
                "pytorch",
            ],
            "fastapi": [
                "fastapi",
            ],
            "flask": [
                "flask",
            ],
            "django": [
                "django",
            ],
            "aws": [
                "aws",
                "amazon web services",
            ],
        }

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for safe skill searching.
        """

        if not text:
            return ""

        text = str(text).lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ============================================================
    # CANONICAL SKILL
    # ============================================================

    def _canonical_skill(
        self,
        skill: str,
    ) -> str:
        """
        Convert skill aliases into a canonical skill name.
        """

        normalized = self._normalize_text(skill)

        for canonical, aliases in self.skill_aliases.items():

            if normalized == canonical:
                return canonical

            if normalized in aliases:
                return canonical

        return normalized

    # ============================================================
    # SKILL ALIASES
    # ============================================================

    def _get_skill_aliases(
        self,
        skill: str,
    ) -> List[str]:
        """
        Return all searchable aliases for a skill.
        """

        canonical = self._canonical_skill(skill)

        return self.skill_aliases.get(
            canonical,
            [canonical],
        )

    # ============================================================
    # TEXT CONTAINS SKILL
    # ============================================================

    def _text_contains_skill(
        self,
        text: str,
        skill: str,
    ) -> bool:
        """
        Check whether a skill appears in a piece of text.

        Word boundaries prevent false matches such as:

            SQL → SQLAlchemy

        when SQL itself is not actually mentioned.
        """

        normalized_text = self._normalize_text(text)

        if not normalized_text:
            return False

        aliases = self._get_skill_aliases(skill)

        for alias in aliases:

            normalized_alias = self._normalize_text(alias)

            if not normalized_alias:
                continue

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(normalized_alias)
                + r"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                normalized_text,
            ):
                return True

        return False

    # ============================================================
    # ROLE TEXT
    # ============================================================

    def _build_role_text(
        self,
        role: Dict,
    ) -> str:
        """
        Combine useful fields from an experience entry.
        """

        if not isinstance(role, dict):
            return ""

        parts = []

        for field in [
            "job_title",
            "company",
            "description",
            "responsibilities",
            "technologies",
            "skills",
            "tech",
            "technology",
        ]:

            value = role.get(field)

            if isinstance(value, list):

                parts.extend(
                    str(item)
                    for item in value
                    if item
                )

            elif isinstance(value, dict):

                for item in value.values():

                    if isinstance(item, list):

                        parts.extend(
                            str(x)
                            for x in item
                            if x
                        )

                    elif item:

                        parts.append(
                            str(item)
                        )

            elif value:

                parts.append(
                    str(value)
                )

        return " ".join(parts)

    # ============================================================
    # ROLE DURATION
    # ============================================================

    def _get_role_duration(
        self,
        role: Dict,
    ) -> Dict:
        """
        Reuse the central experience date parser.

        This prevents different parts of TalentAI from
        calculating experience differently.
        """

        period = extract_experience_period(role)

        if not period:

            return {
                "duration_months": 0,
                "duration_years": 0.0,
                "current": False,
            }

        duration_months = calculate_month_difference(
            period["start"],
            period["end"],
        )

        return {
            "duration_months": duration_months,
            "duration_years": months_to_years(
                duration_months
            ),
            "current": period.get(
                "current",
                False,
            ),
        }

    # ============================================================
    # EXPERIENCE SOURCE ANALYSIS
    # ============================================================

    def _analyze_experience_source(
        self,
        skill: str,
        experiences: List[Dict],
    ) -> Dict:
        """
        Find professional experience involving the skill.
        """

        matched_roles = []

        total_months = 0

        for role in experiences:

            if not isinstance(role, dict):
                continue

            role_text = self._build_role_text(
                role
            )

            if not self._text_contains_skill(
                role_text,
                skill,
            ):
                continue

            duration = self._get_role_duration(
                role
            )

            duration_months = duration[
                "duration_months"
            ]

            total_months += duration_months

            matched_roles.append(
                {
                    "job_title": role.get(
                        "job_title"
                    ),
                    "company": role.get(
                        "company"
                    ),
                    "duration_months": (
                        duration_months
                    ),
                    "duration_years": (
                        duration["duration_years"]
                    ),
                    "current": (
                        duration["current"]
                    ),
                }
            )

        return {
            "experience_years": months_to_years(
                total_months
            ),
            "experience_months": total_months,
            "roles": matched_roles,
        }

    # ============================================================
    # PROJECT SOURCE ANALYSIS
    # ============================================================

    def _analyze_project_source(
        self,
        skill: str,
        projects: List[Dict],
    ) -> List[Dict]:
        """
        Find projects demonstrating the skill.
        """

        matched_projects = []

        for project in projects:

            if not isinstance(project, dict):
                continue

            project_parts = []

            for field in [
                "project_name",
                "name",
                "description",
                "technologies",
                "skills",
            ]:

                value = project.get(field)

                if isinstance(value, list):

                    project_parts.extend(
                        str(item)
                        for item in value
                        if item
                    )

                elif value:

                    project_parts.append(
                        str(value)
                    )

            project_text = " ".join(
                project_parts
            )

            if self._text_contains_skill(
                project_text,
                skill,
            ):

                matched_projects.append(
                    {
                        "project_name": project.get(
                            "project_name",
                            project.get(
                                "name"
                            ),
                        ),
                        "evidence": project_text,
                    }
                )

        return matched_projects

    # ============================================================
    # CERTIFICATION SOURCE
    # ============================================================

    def _analyze_certification_source(
        self,
        skill: str,
        certifications,
    ) -> List[str]:
        """
        Find certifications mentioning the skill.
        """

        matched = []

        if not isinstance(
            certifications,
            list,
        ):
            return matched

        for certification in certifications:

            if isinstance(
                certification,
                dict,
            ):

                text = " ".join(
                    str(value)
                    for value in certification.values()
                    if value
                )

            else:

                text = str(
                    certification
                )

            if self._text_contains_skill(
                text,
                skill,
            ):

                matched.append(
                    text
                )

        return matched

    # ============================================================
    # EDUCATION SOURCE
    # ============================================================

    def _analyze_education_source(
        self,
        skill: str,
        education,
    ) -> List[str]:
        """
        Find education entries mentioning the skill.
        """

        matched = []

        if not isinstance(
            education,
            list,
        ):
            return matched

        for entry in education:

            if isinstance(
                entry,
                dict,
            ):

                text = " ".join(
                    str(value)
                    for value in entry.values()
                    if value
                )

            else:

                text = str(entry)

            if self._text_contains_skill(
                text,
                skill,
            ):

                matched.append(
                    text
                )

        return matched

    # ============================================================
    # MAIN SKILL ANALYSIS
    # ============================================================

    def analyze_skill(
        self,
        skill: str,
        resume: Dict,
    ) -> Dict:
        """
        Analyze one skill across the entire resume.
        """

        if not isinstance(
            resume,
            dict,
        ):
            return {
                "skill": skill,
                "status": "unknown",
                "experience_years": 0.0,
                "experience_months": 0,
                "sources": [],
                "roles": [],
                "projects": [],
                "certifications": [],
                "education": [],
                "strength": "unknown",
            }

        canonical_skill = self._canonical_skill(
            skill
        )

        experiences = resume.get(
            "experience",
            [],
        )

        projects = resume.get(
            "projects",
            [],
        )

        certifications = resume.get(
            "certifications",
            [],
        )

        education = resume.get(
            "education",
            [],
        )

        # --------------------------------------------------------
        # EXPERIENCE
        # --------------------------------------------------------

        experience_result = (
            self._analyze_experience_source(
                canonical_skill,
                experiences,
            )
        )

        # --------------------------------------------------------
        # PROJECTS
        # --------------------------------------------------------

        project_result = (
            self._analyze_project_source(
                canonical_skill,
                projects,
            )
        )

        # --------------------------------------------------------
        # CERTIFICATIONS
        # --------------------------------------------------------

        certification_result = (
            self._analyze_certification_source(
                canonical_skill,
                certifications,
            )
        )

        # --------------------------------------------------------
        # EDUCATION
        # --------------------------------------------------------

        education_result = (
            self._analyze_education_source(
                canonical_skill,
                education,
            )
        )

        # --------------------------------------------------------
        # MAIN SKILLS SECTION
        # --------------------------------------------------------

        skills_section = resume.get(
            "skills",
            [],
        )

        skills_text = str(
            skills_section
        )

        skill_in_skills_section = (
            self._text_contains_skill(
                skills_text,
                canonical_skill,
            )
        )

        # --------------------------------------------------------
        # SOURCES
        # --------------------------------------------------------

        sources = []

        if experience_result["roles"]:
            sources.append(
                "experience"
            )

        if project_result:
            sources.append(
                "project"
            )

        if certification_result:
            sources.append(
                "certification"
            )

        if education_result:
            sources.append(
                "education"
            )

        if skill_in_skills_section:
            sources.append(
                "skills"
            )

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        if experience_result["roles"]:

            status = "matched"

        elif project_result:

            status = "possible"

        elif (
            certification_result
            or education_result
            or skill_in_skills_section
        ):

            status = "possible"

        else:

            status = "unknown"

        # --------------------------------------------------------
        # STRENGTH
        # --------------------------------------------------------

        if experience_result["roles"]:

            strength = "strong"

        elif project_result:

            strength = "moderate"

        elif (
            certification_result
            or education_result
        ):

            strength = "moderate"

        elif skill_in_skills_section:

            strength = "weak"

        else:

            strength = "unknown"

        return {
            "skill": skill,
            "canonical_skill": canonical_skill,
            "status": status,
            "experience_years": (
                experience_result[
                    "experience_years"
                ]
            ),
            "experience_months": (
                experience_result[
                    "experience_months"
                ]
            ),
            "sources": sources,
            "roles": experience_result[
                "roles"
            ],
            "projects": project_result,
            "certifications": certification_result,
            "education": education_result,
            "skills_section": (
                skill_in_skills_section
            ),
            "strength": strength,
        }

    # ============================================================
    # MULTIPLE SKILLS
    # ============================================================

    def analyze(
        self,
        skills: List[str],
        resume: Dict,
    ) -> Dict:
        """
        Analyze multiple skills.
        """

        if not skills:

            return {
                "skills": [],
                "matched": [],
                "possible": [],
                "unknown": [],
            }

        results = []

        matched = []
        possible = []
        unknown = []

        for skill in skills:

            result = self.analyze_skill(
                skill,
                resume,
            )

            results.append(
                result
            )

            if result["status"] == "matched":

                matched.append(
                    result
                )

            elif result["status"] == "possible":

                possible.append(
                    result
                )

            else:

                unknown.append(
                    result
                )

        return {
            "skills": results,
            "matched": matched,
            "possible": possible,
            "unknown": unknown,
        }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def analyze_skill_experience(
    skills: List[str],
    resume: Dict,
) -> Dict:
    """
    Convenience function for external callers.
    """

    matcher = SkillExperienceMatcher()

    return matcher.analyze(
        skills,
        resume,
    )