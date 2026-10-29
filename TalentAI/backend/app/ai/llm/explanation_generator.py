"""
TalentAI explanation generator.

This module converts structured matching results into
human-readable explanations using the configured LLM.

The LLM does not perform matching calculations.
"""

from typing import Any, Dict

from app.ai.llm.provider import LLMProvider

from app.ai.llm.prompts import (
    SYSTEM_PROMPT,
    EXPLANATION_PROMPT,
)

from app.ai.llm.output_validator import (
    ExplanationOutputValidator,
)


class ExplanationGenerator:
    """
    Generate candidate-job explanations from structured
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
    def _get_value(
        data: Dict[str, Any],
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Safely retrieve a value from a dictionary.
        """

        return data.get(key, default)

    @classmethod
    def _build_skill_alignment(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract the high-level skill alignment summary
        produced by CandidateJobReasoner.
        """

        skill_alignment = cls._get_value(
            match_result,
            "skill_alignment",
            {},
        )

        if not isinstance(skill_alignment, dict):
            skill_alignment = {}

        return {
            "matched": cls._get_value(
                skill_alignment,
                "matched",
                0,
            ),
            "possible": cls._get_value(
                skill_alignment,
                "possible",
                0,
            ),
            "unknown": cls._get_value(
                skill_alignment,
                "unknown",
                0,
            ),
            "score": cls._get_value(
                skill_alignment,
                "score",
            ),
            "total": cls._get_value(
                skill_alignment,
                "total",
            ),
        }

    @classmethod
    def _build_experience_alignment(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract experience alignment from the actual
        TalentMatchEngine result.
        """

        experience_alignment = cls._get_value(
            match_result,
            "experience_alignment",
            {},
        )

        if not isinstance(experience_alignment, dict):
            experience_alignment = {}

        return {
            "candidate_years": cls._get_value(
                experience_alignment,
                "candidate_years",
            ),
            "required_years": cls._get_value(
                experience_alignment,
                "required_years",
            ),
            "score": cls._get_value(
                experience_alignment,
                "score",
            ),
            "status": cls._get_value(
                experience_alignment,
                "status",
            ),
        }

    @classmethod
    def _build_relevant_experience(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract relevant experience information.
        """

        relevant_experience = cls._get_value(
            match_result,
            "relevant_experience",
            {},
        )

        if not isinstance(relevant_experience, dict):
            relevant_experience = {}

        return {
            "relevant_years": cls._get_value(
                relevant_experience,
                "relevant_years",
            ),
            "required_years": cls._get_value(
                relevant_experience,
                "required_years",
            ),
            "score": cls._get_value(
                relevant_experience,
                "score",
            ),
        }

    @classmethod
    def _build_project_alignment(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract project alignment information.
        """

        project_alignment = cls._get_value(
            match_result,
            "project_alignment",
            {},
        )

        if not isinstance(project_alignment, dict):
            project_alignment = {}

        return {
            "project_count": cls._get_value(
                project_alignment,
                "project_count",
                0,
            ),
            "score": cls._get_value(
                project_alignment,
                "score",
            ),
            "status": cls._get_value(
                project_alignment,
                "status",
            ),
        }

    @classmethod
    def _build_education_alignment(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract education alignment.
        """

        education_alignment = cls._get_value(
            match_result,
            "education_alignment",
            {},
        )

        if not isinstance(education_alignment, dict):
            education_alignment = {}

        return {
            "score": cls._get_value(
                education_alignment,
                "score",
            ),
            "status": cls._get_value(
                education_alignment,
                "status",
            ),
        }

    @classmethod
    def _build_evidence_alignment(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract evidence alignment.
        """

        evidence_alignment = cls._get_value(
            match_result,
            "evidence_alignment",
            {},
        )

        if not isinstance(evidence_alignment, dict):
            evidence_alignment = {}

        return {
            "requirements_with_evidence": cls._get_value(
                evidence_alignment,
                "requirements_with_evidence",
            ),
            "score": cls._get_value(
                evidence_alignment,
                "score",
            ),
        }

    @staticmethod
    def _extract_skill_names_from_category(
        items: Any,
    ) -> list[str]:
        """
        Extract requirement names from one deterministic
        skill classification category.

        Supported input forms:

        1. A list of strings:

            ["Python", "SQL"]

        2. A list of dictionaries:

            [
                {"requirement": "Python"},
                {"requirement": "SQL"}
            ]

        The function does not classify or infer skills.
        It only extracts names already produced by
        the matching engine.
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
                        str(requirement).strip()
                    )

            elif item:

                names.append(
                    str(item).strip()
                )

        return names

    @classmethod
    def _extract_required_skill_names(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, list[str]]:
        """
        Extract required skill names from the deterministic
        matching result.

        The LLM does not perform skill matching.

        It only receives the classifications already produced
        by TalentMatchEngine.
        """

        if not isinstance(match_result, dict):
            return {
                "matched_skills": [],
                "possible_skills": [],
                "unknown_skills": [],
            }

        # ----------------------------------------------------
        # Primary source:
        #
        # TalentMatchEngine.analyze()
        #     ↓
        # match
        #     ↓
        # skills
        #     ↓
        # required
        #     ↓
        # matched / possible / unknown
        # ----------------------------------------------------

        match = match_result.get(
            "match",
            {},
        )

        if not isinstance(match, dict):
            match = {}

        skills = match.get(
            "skills",
            {},
        )

        if not isinstance(skills, dict):
            skills = {}

        required = skills.get(
            "required",
            {},
        )

        if not isinstance(required, dict):
            required = {}

        matched_skills = (
            cls._extract_skill_names_from_category(
                required.get(
                    "matched",
                    [],
                )
            )
        )

        possible_skills = (
            cls._extract_skill_names_from_category(
                required.get(
                    "possible",
                    [],
                )
            )
        )

        unknown_skills = (
            cls._extract_skill_names_from_category(
                required.get(
                    "unknown",
                    [],
                )
            )
        )

        return {
            "matched_skills": matched_skills,
            "possible_skills": possible_skills,
            "unknown_skills": unknown_skills,
        }

    @classmethod
    def _build_llm_payload(
        cls,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the strictly controlled payload sent to the LLM.

        TalentMatchEngine.analyze() returns the detailed
        candidate/job analysis under candidate_job_reasoning.

        The LLM must receive only the structured fields
        required for explanation.

        The LLM does not calculate or reinterpret any scores.

        Skill names are extracted directly from the deterministic
        TalentMatchEngine result.
        """

        if not isinstance(match_result, dict):
            match_result = {}

        reasoning = match_result.get(
            "candidate_job_reasoning",
            {},
        )

        if not isinstance(reasoning, dict):
            reasoning = {}

        skill_alignment = reasoning.get(
            "skill_alignment",
            {},
        )

        experience_alignment = reasoning.get(
            "experience_alignment",
            {},
        )

        relevant_experience = reasoning.get(
            "relevant_experience",
            {},
        )

        project_alignment = reasoning.get(
            "project_alignment",
            {},
        )

        education_alignment = reasoning.get(
            "education_alignment",
            {},
        )

        evidence_alignment = reasoning.get(
            "evidence_alignment",
            {},
        )

        gaps = reasoning.get(
            "gaps",
            [],
        )

        if not isinstance(
            skill_alignment,
            dict,
        ):
            skill_alignment = {}

        if not isinstance(
            experience_alignment,
            dict,
        ):
            experience_alignment = {}

        if not isinstance(
            relevant_experience,
            dict,
        ):
            relevant_experience = {}

        if not isinstance(
            project_alignment,
            dict,
        ):
            project_alignment = {}

        if not isinstance(
            education_alignment,
            dict,
        ):
            education_alignment = {}

        if not isinstance(
            evidence_alignment,
            dict,
        ):
            evidence_alignment = {}

        if not isinstance(
            gaps,
            list,
        ):
            gaps = []

        # ----------------------------------------------------
        # Extract deterministic skill classifications.
        # ----------------------------------------------------

        skill_names = (
            cls._extract_required_skill_names(
                match_result
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
                "matched_skills": skill_names.get(
                    "matched_skills",
                    [],
                ),
                "possible_skills": skill_names.get(
                    "possible_skills",
                    [],
                ),
                "unknown_skills": skill_names.get(
                    "unknown_skills",
                    [],
                ),
                "score": skill_alignment.get(
                    "score"
                ),
                "total": skill_alignment.get(
                    "total",
                    0,
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
        Build the user prompt sent to the LLM.
        """

        payload = self._build_llm_payload(
            match_result
        )

        return EXPLANATION_PROMPT.format(
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
        Generate an explanation from structured matching data.
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

    def validate_output(
        self,
        explanation: str,
        match_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate an LLM-generated explanation against the
        deterministic TalentMatchEngine result.

        This method does not modify the explanation.
        It only reports whether unsupported skill claims
        were detected.
        """

        return ExplanationOutputValidator.validate(
            explanation=explanation,
            match_result=match_result,
        )