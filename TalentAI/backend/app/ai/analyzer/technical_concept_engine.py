
from typing import Any, Dict, List


class TechnicalConceptEngine:
    """
    Identifies technical concepts demonstrated by a project
    and maps them to related concepts in a job description.

    Conceptual relationships are not direct skill evidence.
    """

    CONCEPTS = {
        "predictive_classification": {
            "label": "Predictive Classification",
            "aliases": [
                "classification",
                "predictive classification",
                "fraud detection",
                "spam detection",
                "credit risk prediction",
                "binary classification",
                "multiclass classification",
            ],
            "related": [
                "supervised machine learning",
                "predictive modeling",
                "classification algorithms",
            ],
        },

        "ensemble_learning": {
            "label": "Ensemble Learning",
            "aliases": [
                "random forest",
                "random forests",
                "gradient boosting",
                "xgboost",
                "adaboost",
                "ensemble learning",
                "ensemble methods",
            ],
            "related": [
                "machine learning algorithms",
                "predictive modeling",
                "classification algorithms",
            ],
        },

        "anomaly_detection": {
            "label": "Anomaly Detection",
            "aliases": [
                "anomaly detection",
                "outlier detection",
            ],
            "related": [
                "predictive modeling",
                "data analysis",
                "classification",
            ],
        },

        "model_evaluation": {
            "label": "Model Evaluation",
            "aliases": [
                "model evaluation",
                "model performance",
                "accuracy",
                "precision",
                "recall",
                "false positives",
                "false negatives",
                "f1 score",
                "roc auc",
            ],
            "related": [
                "machine learning model validation",
                "classification evaluation",
                "model assessment",
            ],
        },

        "data_preprocessing": {
            "label": "Data Preprocessing",
            "aliases": [
                "data preprocessing",
                "data cleaning",
                "data transformation",
                "missing value handling",
                "feature scaling",
                "data normalization",
            ],
            "related": [
                "data preparation",
                "feature engineering",
            ],
        },

        "feature_engineering": {
            "label": "Feature Engineering",
            "aliases": [
                "feature engineering",
                "feature selection",
                "feature extraction",
                "feature construction",
            ],
            "related": [
                "data preprocessing",
                "predictive modeling",
            ],
        },

        "regression": {
            "label": "Regression Modeling",
            "aliases": [
                "regression",
                "linear regression",
                "logistic regression",
                "regression modeling",
            ],
            "related": [
                "predictive modeling",
                "supervised machine learning",
            ],
        },

        "clustering": {
            "label": "Clustering",
            "aliases": [
                "clustering",
                "k means",
                "k-means",
                "hierarchical clustering",
                "dbscan",
            ],
            "related": [
                "unsupervised machine learning",
                "customer segmentation",
                "pattern discovery",
            ],
        },
    }

    @staticmethod
    def _clean_text(value: Any) -> str:

        if value is None:
            return ""

        if isinstance(value, dict):
            return " ".join(
                TechnicalConceptEngine._clean_text(item)
                for item in value.values()
            )

        if isinstance(value, (list, tuple, set)):
            return " ".join(
                TechnicalConceptEngine._clean_text(item)
                for item in value
            )

        return str(value).lower().strip()

    @staticmethod
    def _contains_phrase(text: str, phrase: str) -> bool:

        import re

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(phrase.lower())
            + r"(?![a-zA-Z0-9])"
        )

        return bool(re.search(pattern, text))

    def extract_concepts(self, text: str) -> List[Dict[str, Any]]:

        normalized_text = self._clean_text(text)

        extracted = []

        for concept_id, concept_data in self.CONCEPTS.items():

            matched_aliases = [
                alias
                for alias in concept_data["aliases"]
                if self._contains_phrase(
                    normalized_text,
                    alias
                )
            ]

            if matched_aliases:

                extracted.append({
                    "concept_id": concept_id,
                    "concept": concept_data["label"],
                    "matched_evidence": matched_aliases,
                    "related_concepts": concept_data["related"],
                })

        return extracted

    def analyze(
        self,
        project: Dict[str, Any],
        job_title: str = "",
        job_description: str = "",
        responsibilities: Any = None,
        requirements: Any = None,
    ) -> Dict[str, Any]:

        project_text = " ".join(
            part
            for part in [
                self._clean_text(
                    project.get("project_name")
                    or project.get("name")
                ),
                self._clean_text(project.get("description")),
                self._clean_text(project.get("raw_text")),
                self._clean_text(project.get("technologies")),
            ]
            if part
        )

        job_text = " ".join(
            part
            for part in [
                self._clean_text(job_title),
                self._clean_text(job_description),
                self._clean_text(responsibilities),
                self._clean_text(requirements),
            ]
            if part
        )

        if not project_text or not job_text:

            return {
                "status": "insufficient_data",
                "project_concepts": [],
                "job_concepts": [],
                "concept_matches": [],
            }

        project_concepts = self.extract_concepts(
            project_text
        )

        job_concepts = self.extract_concepts(
            job_text
        )

        job_concept_ids = {
            item["concept_id"]
            for item in job_concepts
        }

        concept_matches = []

        for project_concept in project_concepts:

            concept_id = project_concept["concept_id"]

            concept_data = self.CONCEPTS[concept_id]

            related_matches = [
                related
                for related in concept_data["related"]
                if any(
                    self._contains_phrase(
                        job_text,
                        related
                    )
                    for _ in [0]
                )
            ]

            direct_match = (
                concept_id in job_concept_ids
            )

            if direct_match or related_matches:

                concept_matches.append({
                    "project_concept": (
                        project_concept["concept"]
                    ),
                    "concept_id": concept_id,
                    "matched_evidence": (
                        project_concept["matched_evidence"]
                    ),
                    "match_type": (
                        "direct_concept"
                        if direct_match
                        else "related_concept"
                    ),
                    "job_related_concepts": (
                        related_matches
                    ),
                })

        return {
            "status": "analyzed",
            "project_concepts": project_concepts,
            "job_concepts": job_concepts,
            "concept_matches": concept_matches,
            "concept_match_count": len(concept_matches),
        }
