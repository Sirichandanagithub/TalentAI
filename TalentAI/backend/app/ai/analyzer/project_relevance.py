from typing import Dict, List

from app.ai.analyzer.hybrid_matcher import HybridMatcher


class ProjectRelevanceAnalyzer:
    """
    Analyze how relevant resume projects are to a target job.

    The analyzer evaluates:
    - technology / skill overlap
    - required skill coverage
    - preferred skill coverage
    - project description evidence
    - overall project relevance
    """

    REQUIRED_MATCH_WEIGHT = 1.0
    REQUIRED_POSSIBLE_WEIGHT = 0.5
    PREFERRED_MATCH_WEIGHT = 0.25

    HIGH_THRESHOLD = 0.75
    MODERATE_THRESHOLD = 0.45
    LOW_THRESHOLD = 0.20

    def __init__(self):
        self.matcher = HybridMatcher()

    # ============================================================
    # NORMALIZATION
    # ============================================================

    def _normalize_text(self, value) -> str:
        if value is None:
            return ""

        return str(value).strip().lower()

    # ============================================================
    # PROJECT TEXT
    # ============================================================

    def _project_text(self, project: Dict) -> str:
        """
        Build searchable text from the project.
        """

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

        if not isinstance(technologies, list):
            technologies = [technologies]

        technology_text = " ".join(
            str(item)
            for item in technologies
            if item
        )

        return " ".join(
            [
                str(project_name),
                str(description),
                str(raw_text),
                technology_text
            ]
        ).strip()

    # ============================================================
    # CANDIDATE SKILLS
    # ============================================================

    def _project_skills(
        self,
        project: Dict
    ) -> List[str]:
        """
        Extract skills/technologies explicitly associated
        with the project.
        """

        technologies = project.get(
            "technologies",
            []
        )

        if not technologies:
            return []

        if isinstance(technologies, str):
            technologies = [technologies]

        return [
            str(skill).strip()
            for skill in technologies
            if str(skill).strip()
        ]

    # ============================================================
    # TITLE RELEVANCE
    # ============================================================

    def _title_relevance(
        self,
        project_name: str,
        required_skills: List[str]
    ) -> float:
        """
        Lightweight title relevance signal.

        This is intentionally conservative. We do not assume
        that a project title alone proves a skill.
        """

        if not project_name:
            return 0.0

        title_words = set(
            self._normalize_text(project_name).split()
        )

        if not title_words:
            return 0.0

        matches = 0

        for skill in required_skills:

            skill_words = set(
                self._normalize_text(skill).split()
            )

            if skill_words and skill_words.intersection(
                title_words
            ):
                matches += 1

        if not required_skills:
            return 0.0

        return round(
            matches / len(required_skills),
            2
        )

    # ============================================================
    # ANALYZE SINGLE PROJECT
    # ============================================================

    def analyze_project(
        self,
        project: Dict,
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Dict:
        """
        Analyze one project against the job requirements.
        """

        project_name = project.get(
            "project_name"
        )

        description = project.get(
            "description"
        )

        technologies = self._project_skills(
            project
        )

        project_text = self._project_text(
            project
        )

        matched_required = []
        possible_required = []
        unknown_required = []

        evidence = []

        # --------------------------------------------------------
        # REQUIRED SKILLS
        # --------------------------------------------------------

        for skill in required_skills:

            result = self.matcher.match_requirement(
                skill,
                technologies
            )

            status = result.get(
                "status",
                "unknown"
            )

            if status == "matched":

                matched_required.append(skill)

                evidence.append(
                    f"Project explicitly uses {skill}"
                )

            elif status == "possible":

                possible_required.append(skill)

                evidence.append(
                    f"Project has related evidence for {skill}"
                )

            else:
                # ------------------------------------------------
                # Technology list may be empty or incomplete.
                # Check project description as supporting evidence.
                # ------------------------------------------------

                normalized_skill = self._normalize_text(
                    skill
                )

                normalized_text = self._normalize_text(
                    project_text
                )

                if (
                    normalized_skill
                    and normalized_skill in normalized_text
                ):
                    matched_required.append(skill)

                    evidence.append(
                        f"Project description mentions {skill}"
                    )

                else:
                    unknown_required.append(skill)

        # --------------------------------------------------------
        # PREFERRED SKILLS
        # --------------------------------------------------------

        matched_preferred = []
        possible_preferred = []
        unknown_preferred = []

        for skill in preferred_skills:

            result = self.matcher.match_requirement(
                skill,
                technologies
            )

            status = result.get(
                "status",
                "unknown"
            )

            if status == "matched":

                matched_preferred.append(skill)

                evidence.append(
                    f"Project explicitly uses preferred skill {skill}"
                )

            elif status == "possible":

                possible_preferred.append(skill)

            else:

                normalized_skill = self._normalize_text(
                    skill
                )

                normalized_text = self._normalize_text(
                    project_text
                )

                if (
                    normalized_skill
                    and normalized_skill in normalized_text
                ):
                    matched_preferred.append(skill)

                    evidence.append(
                        f"Project description mentions preferred skill {skill}"
                    )

                else:
                    unknown_preferred.append(skill)

        # --------------------------------------------------------
        # REQUIRED SKILL SCORE
        # --------------------------------------------------------

        required_count = len(
            required_skills
        )

        if required_count:

            required_score = (
                len(matched_required)
                * self.REQUIRED_MATCH_WEIGHT
                +
                len(possible_required)
                * self.REQUIRED_POSSIBLE_WEIGHT
            ) / required_count

        else:
            required_score = 0.0

        # --------------------------------------------------------
        # PREFERRED SKILL SCORE
        # --------------------------------------------------------

        preferred_count = len(
            preferred_skills
        )

        if preferred_count:

            preferred_score = (
                len(matched_preferred)
                * self.PREFERRED_MATCH_WEIGHT
            ) / (
                preferred_count
                * self.PREFERRED_MATCH_WEIGHT
            )

        else:
            preferred_score = 0.0

        # --------------------------------------------------------
        # TITLE SCORE
        # --------------------------------------------------------

        title_score = self._title_relevance(
            project_name or "",
            required_skills
        )

        # --------------------------------------------------------
        # FINAL SCORE
        # --------------------------------------------------------

        relevance_score = (
            required_score * 0.75
            +
            preferred_score * 0.10
            +
            title_score * 0.15
        )

        relevance_score = round(
            min(relevance_score, 1.0),
            2
        )

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        if relevance_score >= self.HIGH_THRESHOLD:

            status = "high"

        elif relevance_score >= self.MODERATE_THRESHOLD:

            status = "moderate"

        elif relevance_score >= self.LOW_THRESHOLD:

            status = "low"

        else:

            status = "none"

        return {
            "project_name": project_name,
            "description": description,
            "technologies": technologies,

            "relevance_score": relevance_score,
            "status": status,

            "required_skill_score": round(
                required_score,
                2
            ),

            "preferred_skill_score": round(
                preferred_score,
                2
            ),

            "title_relevance": title_score,

            "matched_required": matched_required,
            "possible_required": possible_required,
            "unknown_required": unknown_required,

            "matched_preferred": matched_preferred,
            "possible_preferred": possible_preferred,
            "unknown_preferred": unknown_preferred,

            "evidence": evidence
        }

    # ============================================================
    # ANALYZE ALL PROJECTS
    # ============================================================

    def analyze(
        self,
        projects: List[Dict],
        required_skills: List[str],
        preferred_skills: List[str] = None
    ) -> Dict:
        """
        Analyze all candidate projects.
        """

        preferred_skills = preferred_skills or []
        projects = projects or []

        if not projects:

            return {
                "overall_project_relevance": 0.0,
                "relevant_projects": [],
                "project_count": 0
            }

        analyzed_projects = []

        for project in projects:

            result = self.analyze_project(
                project=project,
                required_skills=required_skills,
                preferred_skills=preferred_skills
            )

            analyzed_projects.append(
                result
            )

        # --------------------------------------------------------
        # Overall relevance
        # --------------------------------------------------------

        scores = [
            project["relevance_score"]
            for project in analyzed_projects
        ]

        overall_relevance = round(
            sum(scores) / len(scores),
            2
        )

        return {
            "overall_project_relevance": overall_relevance,
            "project_count": len(
                analyzed_projects
            ),
            "relevant_projects": analyzed_projects
        }


# ================================================================
# CONVENIENCE FUNCTION
# ================================================================

def analyze_project_relevance(
    projects: List[Dict],
    required_skills: List[str],
    preferred_skills: List[str] = None
) -> Dict:

    analyzer = ProjectRelevanceAnalyzer()

    return analyzer.analyze(
        projects=projects,
        required_skills=required_skills,
        preferred_skills=preferred_skills
    )