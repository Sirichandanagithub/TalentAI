"""
TalentAI interview question generator.

This module generates job-relevant interview questions
from deterministic candidate-job matching results.

The LLM does not determine candidate skills or experience.
"""

from typing import Any, Dict

from app.ai.llm.provider import LLMProvider

from app.ai.llm.prompts import (
    SYSTEM_PROMPT,
    INTERVIEW_QUESTION_PROMPT,
)


class InterviewQuestionGenerator:
    """
    Generate interview questions from deterministic
    TalentAI matching results.
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
        Safely return a dictionary.
        """

        if isinstance(value, dict):
            return value

        return {}

    @staticmethod
    def _extract_skill_names(
        items: Any,
    ) -> list[str]:
        """
        Extract skill names from deterministic matching
        categories.

        This method does not classify or infer skills.
        """

        names = []

        if not isinstance(
            items,
            list,
        ):
            return names

        for item in items:

            if isinstance(
                item,
                dict,
            ):

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
                    str(
                        item
                    ).strip()
                )

        return names

    @classmethod
    def _build_payload(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the controlled payload sent to the LLM.

        Only deterministic candidate-job information is
        included.
        """

        if not isinstance(
            match_result,
            dict,
        ):
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

        gaps = reasoning.get(
            "gaps",
            [],
        )

        if not isinstance(
            gaps,
            list,
        ):
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

        return {
            "job_title": match_result.get(
                "job_title"
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
                "matched_skills": (
                    cls._extract_skill_names(
                        required_skills.get(
                            "matched",
                            [],
                        )
                    )
                ),
                "possible_skills": (
                    cls._extract_skill_names(
                        required_skills.get(
                            "possible",
                            [],
                        )
                    )
                ),
                "unknown_skills": (
                    cls._extract_skill_names(
                        required_skills.get(
                            "unknown",
                            [],
                        )
                    )
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
            "gaps": gaps,
        }

    def build_prompt(
        self,
        match_result: Dict[str, Any],
        candidate_name: str = "Candidate",
        job_title: str = "Target Role",
    ) -> str:
        """
        Build the controlled interview question prompt.
        """

        payload = self._build_payload(
            match_result
        )

        return INTERVIEW_QUESTION_PROMPT.format(
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
        Generate interview questions.
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