
import re
from typing import Any, Dict, List

from app.ai.analyzer.hybrid_matcher import HybridMatcher
from app.ai.analyzer.project_semantic_analyzer import ProjectSemanticAnalyzer
from app.ai.analyzer.technical_concept_engine import TechnicalConceptEngine

class ProjectRelevanceAnalyzer:

    def __init__(self, matcher: HybridMatcher = None):

    # Reuse existing HybridMatcher when provided.
    # Create a new one only for standalone usage.
        self.matcher = matcher if matcher is not None else HybridMatcher()

        self.semantic_analyzer = ProjectSemanticAnalyzer(
            embedding_service=self.matcher.ai_matcher.embedding_service
        )

        self.technical_concept_engine = TechnicalConceptEngine()
    
    @staticmethod
    def _normalize_text(text: Any) -> str:
        return " ".join(str(text or "").lower().split())

    @staticmethod
    def _project_skills(
        project: Dict[str, Any]
    ) -> List[str]:

        technologies = project.get("technologies", [])

        if isinstance(technologies, str):
            technologies = [technologies]

        if not isinstance(technologies, (list, tuple, set)):
            return []

        return [
            str(item).strip()
            for item in technologies
            if item and str(item).strip()
        ]

    @staticmethod
    def _project_text(
        project: Dict[str, Any]
    ) -> str:

        technologies = (
            ProjectRelevanceAnalyzer._project_skills(
                project
            )
        )

        values = [
            project.get("project_name", ""),
            project.get("name", ""),
            project.get("title", ""),
            project.get("description", ""),
            project.get("raw_text", ""),
            " ".join(technologies),
        ]

        return " ".join(
            str(value)
            for value in values
            if value
        )

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
    @staticmethod
    def _is_non_usage_mention(
        skill: str,
        project: Dict[str, Any],
    ) -> bool:

        description = " ".join(
            str(project.get(field, "") or "")
            for field in ("description", "raw_text")
        ).lower()

        normalized_skill = str(skill or "").strip().lower()

        if not description or not normalized_skill:
            return False

        skill_pattern = (
            r"(?<!\w)"
            + re.escape(normalized_skill)
            + r"(?!\w)"
        )

        non_usage_patterns = [
            # Future learning intentions.
            skill_pattern
            + r".{0,80}\b(?:future learning goal|"
              r"goal to learn|plan to learn|"
              r"planning to learn|want to learn|"
              r"hope to learn|intend to learn)\b",

            # Explicit statements of non-usage.
            r"\b(?:not used|never used|did not use|"
            r"didn't use|no experience with|"
            r"no hands-on experience with)\s+"
            + skill_pattern,
        ]

        return any(
            re.search(pattern, description, re.IGNORECASE)
            for pattern in non_usage_patterns
        )


    @staticmethod
    def _context_relevance(
        project_text: str,
        job_context: str,
    ) -> float:
        """
        Estimate contextual relevance using meaningful
        word overlap between project and job context.

        This is a heuristic, not semantic model inference.
        """

        if not project_text or not job_context:
            return 0.0

        stop_words = {
            "the", "and", "for", "with", "using",
            "used", "from", "that", "this", "into",
            "have", "has", "had", "was", "were",
            "are", "is", "to", "of", "in", "on",
            "by", "a", "an", "as", "at", "or",
            "be", "been", "being", "it", "its",
            "their", "they", "them", "which",
            "who", "what", "when", "where",
            "how", "will", "can", "could",
            "should", "must", "may", "also",
            "such", "more", "most", "other",
            "work", "working", "experience",
            "knowledge", "ability", "skills",
            "skill", "required", "preferred",
            "responsibilities", "requirements",
            "candidate", "job", "role",
        }

        def meaningful_words(text: str) -> set:
            words = re.findall(
                r"\b[a-zA-Z][a-zA-Z0-9+#.]*\b",
                text.lower()
            )

            return {
                word
                for word in words
                if len(word) > 2
                and word not in stop_words
            }

        project_words = meaningful_words(project_text)
        job_words = meaningful_words(job_context)

        if not project_words or not job_words:
            return 0.0

        overlap = project_words.intersection(job_words)

        return min(
            len(overlap) / len(job_words),
            1.0
        )

    @staticmethod
    def _build_job_context(
        job_title: str = "",
        job_description: str = "",
        responsibilities: Any = None,
        requirements: Any = None,
    ) -> str:

        def convert_to_text(value: Any) -> str:

            if isinstance(value, dict):
                return " ".join(
                    convert_to_text(item)
                    for item in value.values()
                )

            if isinstance(value, (list, tuple, set)):
                return " ".join(
                    convert_to_text(item)
                    for item in value
                )

            return str(value or "")

        return " ".join([
            convert_to_text(job_title),
            convert_to_text(job_description),
            convert_to_text(responsibilities),
            convert_to_text(requirements),
        ])

    @staticmethod
    def _safe_confidence(value: Any) -> float:

        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(confidence, 1.0))

    @staticmethod
    def _skill_credit(
        skill_result: Dict[str, Any]
    ) -> float:

        status = skill_result.get("status")

        if status == "matched":
            return 1.0

        if status == "possible":
            return 0.5

        return 0.0

    def analyze_project(
        self,
        project: Dict[str, Any],
        required_skills: List[str],
        job_context: str = "",
        job_title: str = "",
        job_description: str = "",
        responsibilities: Any = None,
        requirements: Any = None,
    ) -> Dict[str, Any]:

        project_name = (
            project.get("project_name")
            or project.get("name")
            or project.get("title")
            or "Unnamed Project"
        )

        technologies = self._project_skills(project)

        matched_required = []
        possible_required = []
        unknown_required = []

        skill_results = []
        evidence = []

        required_count = len(required_skills)

        for skill in required_skills:

            result = self.matcher.match_requirement(
                skill,
                technologies,
            )

            status = result.get("status", "unknown")

            confidence = self._safe_confidence(
                result.get("confidence", 0.0)
            )

            description_mention = (
                self._description_mentions_skill(
                    skill,
                    project
                )
            
                and not self._is_non_usage_mention(
                    skill,
                    project
                )
            )

            relationship = result.get(
                "relationship",
                "none"
            )

            # Broad semantic relationships alone must not
            # establish a project skill match.
            if (
                status == "possible"
                and relationship in(
                    "strong_related",
                    "related",
                    "possible_required",
                )
    
                and not description_mention
            ):
                status = "unknown"
                confidence = 0.0

            if status == "matched":

                matched_required.append(skill)

            elif status == "possible":

                possible_required.append(skill)

            elif description_mention:

                status = "possible"
                confidence = max(confidence, 0.5)

                possible_required.append(skill)

                result["description_mention"] = True

            else:

                unknown_required.append(skill)

            skill_result = {
                "requirement": skill,
                "status": status,
                "confidence": confidence,
                "evidence": result.get("evidence", []),
                "rule_match": result.get(
                    "rule_match", False
                ),
                "semantic_similarity": result.get(
                    "semantic_similarity", 0.0
                ),
                "relationship": relationship,
                "match_source": result.get(
                    "match_source", "none"
                ),
            }

            skill_results.append(skill_result)

            if status != "unknown":

                evidence.append({
                    "requirement": skill,
                    "status": status,
                    "confidence": confidence,
                    "source": (
                        "project_description"
                        if result.get("description_mention")
                        else result.get(
                            "match_source", "unknown"
                        )
                    ),
                    "details": result.get("evidence", []),
                })

        if required_count:

            coverage_score = sum(
                self._skill_credit(item)
                for item in skill_results
            ) / required_count

            supported_results = [
                item
                for item in skill_results
                if item["status"] in (
                    "matched",
                    "possible"
                )
            ]

            if supported_results:

                evidence_confidence = sum(
                    item["confidence"]
                    for item in supported_results
                ) / len(supported_results)

            else:

                evidence_confidence = 0.0

        else:

            coverage_score = 0.0
            evidence_confidence = 0.0

        project_text = self._normalize_text(
            self._project_text(project)
        )

        contextual_relevance = self._context_relevance(
            project_text,
            job_context,
        )

        try:
            semantic_result = self.semantic_analyzer.analyze(
                project=project,
                job_title=job_title,
                job_description=job_description,
                responsibilities=responsibilities,
                requirements=requirements,
            )
        except Exception as exc:
            semantic_result = {
                "status": "fallback",
                "semantic_similarity": 0.0,
                "responsibility_similarity": 0.0,
                "requirement_similarity": 0.0,
                "responsibility_matches": [],
                "requirement_matches": [],
                "evidence_text": project_text,
            }
        try:
            technical_analysis = self.technical_concept_engine.analyze(
                project=project,
                job_title=job_title,
                job_description=job_description,
                responsibilities=responsibilities,
                requirements=requirements,
            )
        except Exception as exc:
            technical_analysis = {
                "status": "fallback",
                "project_concepts": [],
                "job_concepts": [],
                "concept_matches": [],
                "concept_match_count": 0,
                "error": str(exc),
            }
        relevance_score = contextual_relevance

        

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
            "required_skill_score": round(
                coverage_score, 4
            ),
            "evidence_confidence": round(
                evidence_confidence, 4
            ),
            "contextual_relevance": round(
                contextual_relevance, 4
            ),
            "matched_required": matched_required,
            "possible_required": possible_required,
            "unknown_required": unknown_required,
            "skill_results": skill_results,
            "evidence": evidence,

            "semantic_analysis": semantic_result,
            "technical_analysis": technical_analysis,
        }

    def analyze(
        self,
        projects: List[Dict[str, Any]],
        required_skills: List[str],
        preferred_skills: List[str] = None,
        job_title: str = "",
        job_description: str = "",
        responsibilities: Any = None,
        requirements: Any = None,
    ) -> Dict[str, Any]:

        job_context = self._build_job_context(
            job_title=job_title,
            job_description=job_description,
            responsibilities=responsibilities,
            requirements=requirements,
        )

        project_results = []

        for project in projects:

            if not isinstance(project, dict):
                continue

            result = self.analyze_project(
                project=project,
                required_skills=required_skills,
                job_context=job_context,
                job_title=job_title,
                job_description=job_description,
                responsibilities=responsibilities,
                requirements=requirements,
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
