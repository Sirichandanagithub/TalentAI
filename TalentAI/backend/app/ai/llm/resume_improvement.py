"""
TalentAI resume improvement generator.

This module converts deterministic candidate-job matching
results into practical resume improvement suggestions.

The LLM does not calculate scores, classify skills, or
invent candidate experience.
"""

from typing import Any, Dict

from app.ai.llm.provider import LLMProvider
from app.ai.llm.prompts import (
    SYSTEM_PROMPT,
    RESUME_IMPROVEMENT_PROMPT,
)


class ResumeImprovementGenerator:
    """
    Generate resume improvement suggestions from
    deterministic TalentAI matching results.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        llm: Any | None = None,
    ):
        self.provider = provider or LLMProvider()
        self._llm = llm

    @property
    def llm(self) -> Any:
        """
        Lazily create the configured LLM.
        """

        if self._llm is None:
            self._llm = self.provider.get_llm()

        return self._llm

    @staticmethod
    def _safe_dict(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Return a dictionary when the supplied value
        is a dictionary.
        """

        if isinstance(value, dict):
            return value

        return {}

    @classmethod
    def _build_payload(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the controlled payload sent to the LLM.

        The payload contains only deterministic matching
        information required for resume improvement.
        """

        if not isinstance(match_result, dict):
            match_result = {}

        reasoning = cls._safe_dict(
            match_result.get(
                "candidate_job_reasoning",
                {},
            )
        )

        skill_alignment = cls._safe_dict(
            reasoning.get(
                "skill_alignment",
                {},
            )
        )

        experience_alignment = cls._safe_dict(
            reasoning.get(
                "experience_alignment",
                {},
            )
        )

        relevant_experience = cls._safe_dict(
            reasoning.get(
                "relevant_experience",
                {},
            )
        )

        project_alignment = cls._safe_dict(
            reasoning.get(
                "project_alignment",
                {},
            )
        )

        education_alignment = cls._safe_dict(
            reasoning.get(
                "education_alignment",
                {},
            )
        )

        evidence_alignment = cls._safe_dict(
            reasoning.get(
                "evidence_alignment",
                {},
            )
        )

        gaps = reasoning.get(
            "gaps",
            [],
        )

        if not isinstance(gaps, list):
            gaps = []

        match = cls._safe_dict(
            match_result.get(
                "match",
                {},
            )
        )

        skills = cls._safe_dict(
            match.get(
                "skills",
                {},
            )
        )

        required_skills = cls._safe_dict(
            skills.get(
                "required",
                {},
            )
        )

        def extract_skill_names(
            items: Any,
        ) -> list[str]:
            """
            Extract skill names without performing
            any new classification.
            """

            names = []

            if not isinstance(items, list):
                return names

            for item in items:

                if isinstance(item, dict):

                    requirement = item.get(
                        "requirement"
                    )

                    if requirement:
                        names.append(
                            str(
                                requirement
                            ).strip()
                        )

                elif item:

                    names.append(
                        str(item).strip()
                    )

            return names

        matched_skills = extract_skill_names(
            required_skills.get(
                "matched",
                [],
            )
        )

        possible_skills = extract_skill_names(
            required_skills.get(
                "possible",
                [],
            )
        )

        unknown_skills = extract_skill_names(
            required_skills.get(
                "unknown",
                [],
            )
        )

        return {
            "ats_score": match_result.get(
                "ats_score"
            ),
            "classification": match_result.get(
                "classification"
            ),
            "skill_alignment": {
                "matched": skill_alignment.get(
                    "matched",
                    0,
                ),
                "possible": skill_alignment.get(
                    "possible",
                    0,
                ),
                "unknown": skill_alignment.get(
                    "unknown",
                    0,
                ),
                "matched_skills": matched_skills,
                "possible_skills": possible_skills,
                "unknown_skills": unknown_skills,
                "score": skill_alignment.get(
                    "score"
                ),
            },
            "experience_alignment": {
                "candidate_years": (
                    experience_alignment.get(
                        "candidate_years"
                    )
                ),
                "required_years": (
                    experience_alignment.get(
                        "required_years"
                    )
                ),
                "score": experience_alignment.get(
                    "score"
                ),
                "status": experience_alignment.get(
                    "status"
                ),
            },
            "relevant_experience": {
                "relevant_years": (
                    relevant_experience.get(
                        "relevant_years"
                    )
                ),
                "required_years": (
                    relevant_experience.get(
                        "required_years"
                    )
                ),
                "score": relevant_experience.get(
                    "score"
                ),
            },
            "project_alignment": {
                "project_count": (
                    project_alignment.get(
                        "project_count",
                        0,
                    )
                ),
                "score": project_alignment.get(
                    "score"
                ),
                "status": project_alignment.get(
                    "status"
                ),
            },
            "education_alignment": {
                "score": education_alignment.get(
                    "score"
                ),
                "status": education_alignment.get(
                    "status"
                ),
            },
            "evidence_alignment": {
                "requirements_with_evidence": (
                    evidence_alignment.get(
                        "requirements_with_evidence"
                    )
                ),
                "score": evidence_alignment.get(
                    "score"
                ),
            },
            "gaps": gaps,
        }

    def build_prompt(
        self,
        match_result: Dict[str, Any],
        candidate_name: str = "Candidate",
        job_title: str = "Target Role",
    ) -> str:
        """
        Build the controlled resume improvement prompt.
        """

        payload = self._build_payload(
            match_result
        )

        return RESUME_IMPROVEMENT_PROMPT.format(
            candidate_name=candidate_name,
            job_title=job_title,
            match_result=repr(payload),
        )

    def generate(
        self,
        match_result: Dict[str, Any],
        candidate_name: str = "Candidate",
        job_title: str = "Target Role",
    ) -> str:
        """
        Generate resume improvement suggestions.
        """

        user_prompt = self.build_prompt(
            match_result=match_result,
            candidate_name=candidate_name,
            job_title=job_title,
        )

        messages = [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            (
                "human",
                user_prompt,
            ),
        ]

        response = self.llm.invoke(
            messages
        )

        if hasattr(
            response,
            "content",
        ):
            return str(
                response.content
            ).strip()

        return str(
            response
        ).strip()