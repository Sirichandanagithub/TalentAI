
import re
from typing import Any, Dict, List

from app.ai.analyzer.hybrid_matcher import HybridMatcher


class ProjectRelevanceAnalyzer:
    def __init__(self):
        self.matcher = HybridMatcher()

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(str(text or "").lower().split())

    @staticmethod
    def _project_text(project: Dict[str, Any]) -> str:
        technologies = project.get("technologies", [])

        if isinstance(technologies, str):
            technologies = [technologies]

        return " ".join(
            str(value)
            for value in [
                project.get("project_name", ""),
                project.get("name", ""),
                project.get("description", ""),
                project.get("raw_text", ""),
                " ".join(str(item) for item in technologies),
            ]
            if value
        )

    @staticmethod
    def _project_skills(project: Dict[str, Any]) -> List[str]:
        technologies = project.get("technologies", [])

        if isinstance(technologies, str):
            technologies = [technologies]

        if not isinstance(technologies, (list, tuple, set)):
            return []

        return [
            str(technology).strip()
            for technology in technologies
            if technology and str(technology).strip()
        ]

    @staticmethod
    def _description_mentions_skill(
        skill: str,
        project: Dict[str, Any],
    ) -> bool:
        description = " ".join(
            str(project.get(field, "") or "")
            for field in ("description", "raw_text")
        )

        normalized_skill = str(skill or "").strip()

        if not normalized_skill or not description:
            return False

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_skill)
            + r"(?!\w)"
        )

        return bool(
            re.search(
                pattern,
                description,
                flags=re.IGNORECASE,
            )
        )

    def _title_relevance(
        self,
        project_name: str,
        required_skills: List[str],
    ) -> float:
        if not project_name or not required_skills:
            return 0.0

        normalized_title = self._normalize_text(project_name)
        matches = 0

        for skill in required_skills:
            normalized_skill = self._normalize_text(skill)

            if (
                normalized_skill
                and normalized_skill in normalized_title
            ):
                matches += 1

        return min(matches / len(required_skills), 1.0)

    def analyze_project(
        self,
        project: Dict[str, Any],
        required_skills: List[str],
        preferred_skills: List[str],
    ) -> Dict[str, Any]:
        project_name = (
            project.get("project_name")
            or project.get("name")
            or "Unnamed Project"
        )

        # Explicit technologies are the strongest evidence.
        technologies = self._project_skills(project)

        matched_required = []
        possible_required = []
        unknown_required = []

        matched_preferred = []
        possible_preferred = []
        unknown_preferred = []

        evidence = []

        # Assess required skills.
        for skill in required_skills:
            result = self.matcher.match_requirement(
                skill,
                technologies,
            )

            status = result.get("status", "unknown")

            if status == "matched":
                matched_required.append(skill)
                evidence.append(
                    f"Project technology evidence matches {skill}"
                )

            elif status == "possible":
                possible_required.append(skill)
                evidence.append(
                    f"Project has related technology evidence for {skill}"
                )

            elif self._description_mentions_skill(skill, project):
                possible_required.append(skill)
                evidence.append(
                    f"Project description mentions {skill}; "
                    "explicit technology evidence is not confirmed"
                )

            else:
                unknown_required.append(skill)

        # Assess preferred skills.
        for skill in preferred_skills:
            result = self.matcher.match_requirement(
                skill,
                technologies,
            )

            status = result.get("status", "unknown")

            if status == "matched":
                matched_preferred.append(skill)
                evidence.append(
                    f"Project technology evidence matches "
                    f"preferred skill {skill}"
                )

            elif status == "possible":
                possible_preferred.append(skill)
                evidence.append(
                    f"Project has related technology evidence "
                    f"for preferred skill {skill}"
                )

            elif self._description_mentions_skill(skill, project):
                possible_preferred.append(skill)
                evidence.append(
                    f"Project description mentions preferred skill "
                    f"{skill}; explicit technology evidence is not confirmed"
                )

            else:
                unknown_preferred.append(skill)

        # Preserve the existing scoring weights.
        required_count = len(required_skills)
        preferred_count = len(preferred_skills)

        if required_count:
            required_score = (
                len(matched_required)
                + (len(possible_required) * 0.5)
            ) / required_count
        else:
            required_score = 1.0

        if preferred_count:
            preferred_score = (
                len(matched_preferred)
                + (len(possible_preferred) * 0.5)
            ) / preferred_count
        else:
            preferred_score = 1.0

        title_score = self._title_relevance(
            project_name,
            required_skills,
        )

        relevance_score = (
            required_score * 0.75
            + preferred_score * 0.10
            + title_score * 0.15
        )

        relevance_score = round(
            max(0.0, min(relevance_score, 1.0)),
            4,
        )

        if relevance_score >= 0.75:
            relevance_level = "high"
        elif relevance_score >= 0.45:
            relevance_level = "moderate"
        elif relevance_score >= 0.20:
            relevance_level = "low"
        else:
            relevance_level = "very_low"

        return {
            "project_name": project_name,
            "relevance_score": relevance_score,
            "relevance_level": relevance_level,
            "status": relevance_level,
            "required_skill_score": round(required_score, 4),
            "preferred_skill_score": round(preferred_score, 4),
            "title_relevance": round(title_score, 4),
            "matched_required": matched_required,
            "possible_required": possible_required,
            "unknown_required": unknown_required,
            "matched_preferred": matched_preferred,
            "possible_preferred": possible_preferred,
            "unknown_preferred": unknown_preferred,
            "evidence": evidence,
        }

    def analyze(
        self,
        projects: List[Dict[str, Any]],
        required_skills: List[str],
        preferred_skills: List[str],
    ) -> Dict[str, Any]:
        project_results = []

        for project in projects:
            result = self.analyze_project(
                project=project,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
            )
            project_results.append(result)

        project_results.sort(
            key=lambda item: item["relevance_score"],
            reverse=True,
        )

        if project_results:
            overall_project_relevance = round(
                sum(
                    item["relevance_score"]
                    for item in project_results
                ) / len(project_results),
                4,
            )
        else:
            overall_project_relevance = 0.0

        return {
            "overall_project_relevance": overall_project_relevance,
            "relevant_projects": project_results,
            "project_count": len(project_results),
            "total_projects_analyzed": len(project_results),
        }
