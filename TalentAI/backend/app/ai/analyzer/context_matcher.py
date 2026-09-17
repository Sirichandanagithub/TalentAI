from typing import Dict, List, Any
import re


class ContextMatcher:
    """
    Context-Aware Resume Matcher.

    Purpose:
        Determine how strongly a resume demonstrates a
        particular job requirement across different resume
        sections.

    Context sources:
        - Skills
        - Experience
        - Projects
        - Certifications
        - Education

    Important:
        This class does NOT replace HybridMatcher.

        HybridMatcher answers:
            "Does the candidate skill match the requirement?"

        ContextMatcher answers:
            "Where and how is this requirement demonstrated
             in the resume?"
    """

    # ============================================================
    # SOURCE WEIGHTS
    # ============================================================

    SOURCE_WEIGHTS = {
        "experience": 1.00,
        "project": 0.95,
        "skills": 0.90,
        "certification": 0.85,
        "education": 0.60,
    }

    # ============================================================
    # SKILL ALIASES
    # ============================================================

    SKILL_ALIASES = {
        "python": [
            "python",
            "py",
        ],

        "javascript": [
            "javascript",
            "java script",
            "js",
        ],

        "typescript": [
            "typescript",
            "type script",
            "ts",
        ],

        "machine learning": [
            "machine learning",
            "ml",
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

        "numpy": [
            "numpy",
        ],

        "scikit-learn": [
            "scikit-learn",
            "scikit learn",
            "sklearn",
        ],

        "sql": [
            "sql",
        ],

        "mysql": [
            "mysql",
        ],

        "postgresql": [
            "postgresql",
            "postgres",
        ],

        "tensorflow": [
            "tensorflow",
            "tensor flow",
        ],

        "pytorch": [
            "pytorch",
            "torch",
        ],

        "fastapi": [
            "fastapi",
            "fast api",
        ],

        "django": [
            "django",
        ],

        "flask": [
            "flask",
        ],

        "aws": [
            "aws",
            "amazon web services",
        ],

        "azure": [
            "azure",
        ],

        "gcp": [
            "gcp",
            "google cloud",
        ],
    }

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):
        pass

    # ============================================================
    # NORMALIZE REQUIREMENT
    # ============================================================

    def normalize_requirement(
        self,
        requirement: str
    ) -> str:
        """
        Convert a requirement into a canonical form.
        """

        if not requirement:
            return ""

        normalized = str(requirement).lower().strip()

        normalized = re.sub(
            r"[^a-z0-9+#.\- ]+",
            " ",
            normalized
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized
        ).strip()

        for canonical, aliases in self.SKILL_ALIASES.items():

            for alias in aliases:

                if normalized == alias:
                    return canonical

        return normalized

    # ============================================================
    # TEXT MATCHING
    # ============================================================

    def requirement_matches_text(
        self,
        requirement: str,
        text: str
    ) -> bool:
        """
        Determine whether a requirement is explicitly
        mentioned in a piece of text.

        Uses aliases where available.
        """

        if not requirement or not text:
            return False

        text = str(text).lower()

        canonical = self.normalize_requirement(
            requirement
        )

        aliases = self.SKILL_ALIASES.get(
            canonical,
            [canonical]
        )

        for alias in aliases:

            pattern = r"\b" + re.escape(alias.lower()) + r"\b"

            if re.search(pattern, text):
                return True

        return False

    # ============================================================
    # FIND MATCHING TEXT
    # ============================================================

    def find_matching_text(
        self,
        requirement: str,
        text: str
    ) -> List[str]:
        """
        Return sentences/lines containing the requirement.
        """

        if not requirement or not text:
            return []

        canonical = self.normalize_requirement(
            requirement
        )

        aliases = self.SKILL_ALIASES.get(
            canonical,
            [canonical]
        )

        matches = []

        # Split resume content into lines
        lines = str(text).splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            lower_line = line.lower()

            for alias in aliases:

                pattern = (
                    r"\b"
                    + re.escape(alias.lower())
                    + r"\b"
                )

                if re.search(pattern, lower_line):

                    if line not in matches:
                        matches.append(line)

                    break

        return matches

    # ============================================================
    # RESUME SKILLS
    # ============================================================

    def _check_skills(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        skills = resume.get(
            "skills",
            []
        )

        found = []

        if isinstance(skills, list):

            for skill in skills:

                if self.requirement_matches_text(
                    requirement,
                    str(skill)
                ):
                    found.append(str(skill))

        elif isinstance(skills, dict):

            for category_skills in skills.values():

                if isinstance(
                    category_skills,
                    list
                ):

                    for skill in category_skills:

                        if self.requirement_matches_text(
                            requirement,
                            str(skill)
                        ):
                            found.append(str(skill))

                elif isinstance(
                    category_skills,
                    str
                ):

                    if self.requirement_matches_text(
                        requirement,
                        category_skills
                    ):
                        found.append(category_skills)

        return {
            "found": bool(found),
            "evidence": found,
        }

    # ============================================================
    # EXPERIENCE
    # ============================================================

    def _check_experience(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        experience = resume.get(
            "experience",
            []
        )

        evidence = []

        if not isinstance(
            experience,
            list
        ):
            return {
                "found": False,
                "evidence": []
            }

        for entry in experience:

            if not isinstance(
                entry,
                dict
            ):
                continue

            text_parts = [
                entry.get(
                    "job_title",
                    ""
                ),
                entry.get(
                    "company",
                    ""
                ),
                entry.get(
                    "description",
                    ""
                ),
                entry.get(
                    "raw_text",
                    ""
                ),
            ]

            text = " ".join(
                str(part)
                for part in text_parts
                if part
            )

            matches = self.find_matching_text(
                requirement,
                text
            )

            for match in matches:

                evidence.append({
                    "job_title": entry.get(
                        "job_title"
                    ),
                    "company": entry.get(
                        "company"
                    ),
                    "text": match,
                })

        return {
            "found": bool(evidence),
            "evidence": evidence,
        }

    # ============================================================
    # PROJECTS
    # ============================================================

    def _check_projects(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        projects = resume.get(
            "projects",
            []
        )

        evidence = []

        if not isinstance(
            projects,
            list
        ):
            return {
                "found": False,
                "evidence": []
            }

        for project in projects:

            if not isinstance(
                project,
                dict
            ):
                continue

            project_name = project.get(
                "project_name",
                ""
            )

            description = project.get(
                "description",
                ""
            )

            technologies = project.get(
                "technologies",
                []
            )

            # ----------------------------------------------------
            # Check technologies
            # ----------------------------------------------------

            if isinstance(
                technologies,
                list
            ):

                for technology in technologies:

                    if self.requirement_matches_text(
                        requirement,
                        str(technology)
                    ):

                        evidence.append({
                            "project_name": project_name,
                            "type": "technology",
                            "text": str(technology),
                        })

            elif isinstance(
                technologies,
                str
            ):

                if self.requirement_matches_text(
                    requirement,
                    technologies
                ):

                    evidence.append({
                        "project_name": project_name,
                        "type": "technology",
                        "text": technologies,
                    })

            # ----------------------------------------------------
            # Check project description
            # ----------------------------------------------------

            text = " ".join([
                str(project_name),
                str(description),
            ])

            matches = self.find_matching_text(
                requirement,
                text
            )

            for match in matches:

                evidence.append({
                    "project_name": project_name,
                    "type": "description",
                    "text": match,
                })

        return {
            "found": bool(evidence),
            "evidence": evidence,
        }

    # ============================================================
    # CERTIFICATIONS
    # ============================================================

    def _check_certifications(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        certifications = resume.get(
            "certifications",
            []
        )

        evidence = []

        if not isinstance(
            certifications,
            list
        ):
            return {
                "found": False,
                "evidence": []
            }

        for certification in certifications:

            if isinstance(
                certification,
                dict
            ):

                text = " ".join(
                    str(value)
                    for value in certification.values()
                    if value
                )

            else:

                text = str(certification)

            matches = self.find_matching_text(
                requirement,
                text
            )

            for match in matches:
                evidence.append(match)

        return {
            "found": bool(evidence),
            "evidence": evidence,
        }

    # ============================================================
    # EDUCATION
    # ============================================================

    def _check_education(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        education = resume.get(
            "education",
            []
        )

        evidence = []

        if not isinstance(
            education,
            list
        ):
            return {
                "found": False,
                "evidence": []
            }

        for entry in education:

            if not isinstance(
                entry,
                dict
            ):
                continue

            text = " ".join(
                str(value)
                for value in entry.values()
                if value
            )

            matches = self.find_matching_text(
                requirement,
                text
            )

            for match in matches:
                evidence.append({
                    "text": match,
                    "education": entry,
                })

        return {
            "found": bool(evidence),
            "evidence": evidence,
        }

    # ============================================================
    # CONTEXT SCORE
    # ============================================================

    def calculate_context_score(
        self,
        sources: List[str]
    ) -> float:
        """
        Calculate context strength based on the strongest
        resume source.

        Experience > Project > Skills > Certification > Education
        """

        if not sources:
            return 0.0

        weights = [
            self.SOURCE_WEIGHTS.get(
                source,
                0.0
            )
            for source in sources
        ]

        return max(weights)

    # ============================================================
    # STATUS
    # ============================================================

    def determine_context_status(
        self,
        sources: List[str],
        hybrid_status: str = "unknown"
    ) -> str:
        """
        Determine how strongly the requirement is supported
        by resume context.
        """

        if not sources:
            return "unknown"

        score = self.calculate_context_score(
            sources
        )

        if score >= 0.95:
            return "supported"

        if score >= 0.85:
            return "supported"

        if score >= 0.60:
            return "indirect"

        return "indirect"

    # ============================================================
    # MAIN MATCH
    # ============================================================

    def match(
        self,
        requirement: str,
        resume: Dict,
        hybrid_result: Dict = None
    ) -> Dict:
        """
        Perform context-aware matching.

        Parameters:
            requirement:
                Job requirement such as "Python"

            resume:
                Parsed resume dictionary.

            hybrid_result:
                Optional result from HybridMatcher.
        """

        if not requirement:

            return {
                "requirement": requirement,
                "hybrid_status": "unknown",
                "context_status": "unknown",
                "context_score": 0.0,
                "sources": [],
                "evidence": [],
                "reason": (
                    "No requirement was provided."
                ),
            }

        if not isinstance(
            resume,
            dict
        ):

            return {
                "requirement": requirement,
                "hybrid_status": "unknown",
                "context_status": "unknown",
                "context_score": 0.0,
                "sources": [],
                "evidence": [],
                "reason": (
                    "Resume data is invalid."
                ),
            }

        hybrid_status = "unknown"

        if isinstance(
            hybrid_result,
            dict
        ):

            hybrid_status = hybrid_result.get(
                "status",
                "unknown"
            )

        sources = []
        evidence = []

        # ========================================================
        # 1. SKILLS
        # ========================================================

        skill_result = self._check_skills(
            requirement,
            resume
        )

        if skill_result["found"]:

            sources.append(
                "skills"
            )

            for item in skill_result["evidence"]:

                evidence.append({
                    "source": "skills",
                    "weight": self.SOURCE_WEIGHTS[
                        "skills"
                    ],
                    "text": item,
                })

        # ========================================================
        # 2. EXPERIENCE
        # ========================================================

        experience_result = self._check_experience(
            requirement,
            resume
        )

        if experience_result["found"]:

            sources.append(
                "experience"
            )

            for item in experience_result["evidence"]:

                evidence.append({
                    "source": "experience",
                    "weight": self.SOURCE_WEIGHTS[
                        "experience"
                    ],
                    "text": item,
                })

        # ========================================================
        # 3. PROJECTS
        # ========================================================

        project_result = self._check_projects(
            requirement,
            resume
        )

        if project_result["found"]:

            sources.append(
                "project"
            )

            for item in project_result["evidence"]:

                evidence.append({
                    "source": "project",
                    "weight": self.SOURCE_WEIGHTS[
                        "project"
                    ],
                    "text": item,
                })

        # ========================================================
        # 4. CERTIFICATIONS
        # ========================================================

        certification_result = self._check_certifications(
            requirement,
            resume
        )

        if certification_result["found"]:

            sources.append(
                "certification"
            )

            for item in certification_result["evidence"]:

                evidence.append({
                    "source": "certification",
                    "weight": self.SOURCE_WEIGHTS[
                        "certification"
                    ],
                    "text": item,
                })

        # ========================================================
        # 5. EDUCATION
        # ========================================================

        education_result = self._check_education(
            requirement,
            resume
        )

        if education_result["found"]:

            sources.append(
                "education"
            )

            for item in education_result["evidence"]:

                evidence.append({
                    "source": "education",
                    "weight": self.SOURCE_WEIGHTS[
                        "education"
                    ],
                    "text": item,
                })

        # ========================================================
        # REMOVE DUPLICATE SOURCES
        # ========================================================

        sources = list(
            dict.fromkeys(sources)
        )

        # ========================================================
        # CALCULATE SCORE
        # ========================================================

        context_score = self.calculate_context_score(
            sources
        )

        context_status = self.determine_context_status(
            sources,
            hybrid_status
        )

        # ========================================================
        # REASON
        # ========================================================

        if context_status == "supported":

            reason = (
                f"{requirement} is explicitly demonstrated "
                f"in the candidate's "
                f"{', '.join(sources)}."
            )

        elif context_status == "indirect":

            reason = (
                f"{requirement} is indirectly supported "
                f"through "
                f"{', '.join(sources)}."
            )

        else:

            reason = (
                f"No direct or contextual evidence of "
                f"{requirement} was found."
            )

        return {
            "requirement": requirement,
            "hybrid_status": hybrid_status,
            "context_status": context_status,
            "context_score": context_score,
            "sources": sources,
            "evidence": evidence,
            "reason": reason,
        }

    # ============================================================
    # COMPATIBILITY METHOD
    # ============================================================

    def match_requirement(
        self,
        requirement: str,
        resume: Dict,
        hybrid_result: Dict = None
    ) -> Dict:
        """
        Compatibility wrapper.
        """

        return self.match(
            requirement,
            resume,
            hybrid_result
        )