
from typing import Any, Dict, List

from sentence_transformers.util import cos_sim


class ProjectSemanticAnalyzer:

    def __init__(self, embedding_service):
        # Reuse the existing embedding service.
        self.embedding_service = embedding_service

    @staticmethod
    def _clean_text(value: Any) -> str:

        if value is None:
            return ""

        if isinstance(value, dict):
            return " ".join(
                ProjectSemanticAnalyzer._clean_text(item)
                for item in value.values()
            )

        if isinstance(value, (list, tuple, set)):
            return " ".join(
                ProjectSemanticAnalyzer._clean_text(item)
                for item in value
            )

        return str(value).strip()

    @staticmethod
    def _normalize_similarity(value: float) -> float:

        return round(
            max(0.0, min(float(value), 1.0)),
            4
        )

    @staticmethod
    def _extract_items(value: Any) -> List[str]:

        if value is None:
            return []

        if isinstance(value, str):
            items = [value]

        elif isinstance(value, dict):
            items = list(value.values())

        elif isinstance(value, (list, tuple, set)):
            items = list(value)

        else:
            items = [value]

        cleaned = [
            ProjectSemanticAnalyzer._clean_text(item)
            for item in items
        ]

        return list(dict.fromkeys(
            item for item in cleaned if item
        ))

    @staticmethod
    def _best_match_score(matches: List[Dict]) -> float:

        if not matches:
            return 0.0

        # Top-three average avoids penalizing a project
        # for unrelated responsibilities.
        top_matches = sorted(
            matches,
            key=lambda item: item["similarity"],
            reverse=True
        )[:3]

        return round(
            sum(item["similarity"] for item in top_matches)
            / len(top_matches),
            4
        )

    def _compare_items(
        self,
        project_embedding,
        item_embeddings,
        items: List[str],
    ) -> List[Dict]:

        if not items:
            return []

        similarities = cos_sim(
            project_embedding.unsqueeze(0),
            item_embeddings
        )[0]

        results = []

        for index, item in enumerate(items):

            results.append({
                "text": item,
                "similarity": self._normalize_similarity(
                    similarities[index].item()
                ),
            })

        return sorted(
            results,
            key=lambda item: item["similarity"],
            reverse=True
        )

    def analyze(
        self,
        project: Dict[str, Any],
        job_title: str = "",
        job_description: str = "",
        responsibilities: Any = None,
        requirements: Any = None,
    ) -> Dict[str, Any]:

        project_title = self._clean_text(
            project.get("project_name")
            or project.get("name")
            or project.get("title")
        )

        project_description = self._clean_text(
            project.get("description")
        )

        technologies = self._extract_items(
            project.get("technologies", [])
        )

        # Avoid adding raw_text when structured fields
        # already contain the same information.
        project_parts = [
            project_title,
            project_description,
            "Technologies: " + ", ".join(technologies)
            if technologies else "",
        ]

        project_text = " ".join(
            part for part in project_parts if part
        )

        # Use raw_text only if structured project information
        # is unavailable.
        if not project_text:
            project_text = self._clean_text(
                project.get("raw_text")
            )

        responsibility_list = self._extract_items(
            responsibilities
        )

        requirement_list = self._extract_items(
            requirements
        )

        job_parts = [
            self._clean_text(job_title),
            self._clean_text(job_description),
            " ".join(responsibility_list),
            " ".join(requirement_list),
        ]

        job_text = " ".join(
            part for part in job_parts if part
        )

        empty_result = {
            "status": "insufficient_data",
            "semantic_similarity": 0.0,
            "responsibility_similarity": 0.0,
            "requirement_similarity": 0.0,
            "responsibility_matches": [],
            "requirement_matches": [],
            "evidence_text": project_text,
        }

        if not project_text or not job_text:
            return empty_result

        comparison_texts = (
            [job_text]
            + responsibility_list
            + requirement_list
        )

        try:

            embeddings = (
                self.embedding_service.generate_embeddings(
                    [project_text] + comparison_texts
                )
            )

            if embeddings is None or len(embeddings) != (
                len(comparison_texts) + 1
            ):
                raise ValueError(
                    "Embedding generation returned invalid results."
                )

            project_embedding = embeddings[0]

            # Project versus complete job context.
            job_similarity = cos_sim(
                project_embedding.unsqueeze(0),
                embeddings[1].unsqueeze(0)
            ).item()

            # Project versus individual responsibilities.
            responsibility_embeddings = (
                embeddings[2:2 + len(responsibility_list)]
            )

            responsibility_matches = (
                self._compare_items(
                    project_embedding,
                    responsibility_embeddings,
                    responsibility_list,
                )
            )

            # Project versus individual requirements.
            requirement_start = 2 + len(responsibility_list)

            requirement_embeddings = embeddings[
                requirement_start:
            ]

            requirement_matches = self._compare_items(
                project_embedding,
                requirement_embeddings,
                requirement_list,
            )

            return {
                "status": "analyzed",
                "semantic_similarity": (
                    self._normalize_similarity(job_similarity)
                ),
                "responsibility_similarity": (
                    self._best_match_score(
                        responsibility_matches
                    )
                ),
                "requirement_similarity": (
                    self._best_match_score(
                        requirement_matches
                    )
                ),
                "responsibility_matches": (
                    responsibility_matches
                ),
                "requirement_matches": requirement_matches,
                "evidence_text": project_text,
            }

        except Exception as exc:

            return {
                "status": "fallback",
                "semantic_similarity": 0.0,
                "responsibility_similarity": 0.0,
                "requirement_similarity": 0.0,
                "responsibility_matches": [],
                "requirement_matches": [],
                "evidence_text": project_text,
                "error": str(exc),
            }
