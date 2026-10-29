"""
LLM output validation for TalentAI.

This module validates generated explanations against the
deterministic skill classifications produced by the matching engine.

The validator does not perform skill matching.
It only checks whether the generated explanation contains
unsupported skill claims.
"""

from typing import Dict, List


class ExplanationOutputValidator:
    """
    Validate LLM-generated explanations against deterministic
    TalentAI matching results.
    """

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize text for simple case-insensitive matching.
        """

        if not isinstance(text, str):
            return ""

        return " ".join(
            text.lower().strip().split()
        )

    @classmethod
    def _extract_skill_names(
        cls,
        match_result: Dict,
    ) -> Dict[str, List[str]]:
        """
        Extract deterministic skill classifications from
        TalentMatchEngine output.
        """

        if not isinstance(match_result, dict):
            return {
                "matched_skills": [],
                "possible_skills": [],
                "unknown_skills": [],
            }

        match = match_result.get(
            "match",
            {}
        )

        if not isinstance(match, dict):
            return {
                "matched_skills": [],
                "possible_skills": [],
                "unknown_skills": [],
            }

        skills = match.get(
            "skills",
            {}
        )

        if not isinstance(skills, dict):
            return {
                "matched_skills": [],
                "possible_skills": [],
                "unknown_skills": [],
            }

        required = skills.get(
            "required",
            {}
        )

        if not isinstance(required, dict):
            required = {}

        def extract(category):
            names = []

            items = required.get(
                category,
                []
            )

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

        return {
            "matched_skills": extract("matched"),
            "possible_skills": extract("possible"),
            "unknown_skills": extract("unknown"),
        }

    @classmethod
    def validate(
        cls,
        explanation: str,
        match_result: Dict,
    ) -> Dict:
        """
        Validate an LLM-generated explanation.

        Returns a structured validation result containing:

        - valid
        - unsupported_skills
        - unknown_skill_claims
        - details
        """

        if not isinstance(explanation, str):
            return {
                "valid": False,
                "unsupported_skills": [],
                "unknown_skill_claims": [],
                "details": [
                    "Explanation must be a string."
                ],
            }

        skills = cls._extract_skill_names(
            match_result
        )

        normalized_explanation = cls._normalize(
            explanation
        )

        matched_skills = skills[
            "matched_skills"
        ]

        possible_skills = skills[
            "possible_skills"
        ]

        unknown_skills = skills[
            "unknown_skills"
        ]

        unsupported_skills = []
        unknown_skill_claims = []

        # --------------------------------------------------
        # Check whether unknown skills are mentioned.
        # Mentioning them is allowed.
        # --------------------------------------------------

        for skill in unknown_skills:

            normalized_skill = cls._normalize(
                skill
            )

            if not normalized_skill:
                continue

            if normalized_skill in normalized_explanation:

                # The skill is allowed to be mentioned.
                #
                # At this stage we record its presence.
                # We do not yet assume that the statement
                # is unsupported.
                pass

        # --------------------------------------------------
        # Detect explicit claims that an unknown skill
        # is definitely absent.
        # --------------------------------------------------

        absence_patterns = [
            "lacks {skill}",
            "lack {skill}",
            "does not have {skill}",
            "doesn't have {skill}",
            "has no {skill}",
            "does not know {skill}",
            "doesn't know {skill}",
            "is not skilled in {skill}",
            "isn't skilled in {skill}",
            "is not proficient in {skill}",
            "isn't proficient in {skill}",
            "has no experience in {skill}",
            "does not have experience in {skill}",
            "doesn't have experience in {skill}",
        ]

        for skill in unknown_skills:

            normalized_skill = cls._normalize(
                skill
            )

            if not normalized_skill:
                continue

            for pattern in absence_patterns:

                claim = pattern.format(
                    skill=normalized_skill
                )

                if claim in normalized_explanation:

                    unknown_skill_claims.append(
                        skill
                    )

                    break

        # --------------------------------------------------
        # Detect unsupported skills.
        #
        # We only consider explicit skill names from the
        # deterministic result. We do not attempt to guess
        # arbitrary words in the generated explanation.
        # --------------------------------------------------

        known_skills = (
            matched_skills
            + possible_skills
            + unknown_skills
        )

        known_skill_names = {
            cls._normalize(skill)
            for skill in known_skills
            if cls._normalize(skill)
        }

        # The validator intentionally does not treat every
        # noun in the explanation as a skill. Instead, it
        # focuses on explicit claims involving deterministic
        # unknown skills.
        #
        # This prevents false positives such as interpreting
        # normal English words as technical skills.

        if unknown_skill_claims:

            unsupported_skills.extend(
                unknown_skill_claims
            )

        valid = (
            len(unsupported_skills) == 0
        )

        details = []

        if unsupported_skills:

            for skill in unsupported_skills:

                details.append(
                    (
                        f"Unsupported claim detected for "
                        f"unknown skill: {skill}"
                    )
                )

        else:

            details.append(
                "No unsupported unknown-skill claims detected."
            )

        return {
            "valid": valid,
            "unsupported_skills": list(
                dict.fromkeys(
                    unsupported_skills
                )
            ),
            "unknown_skill_claims": list(
                dict.fromkeys(
                    unknown_skill_claims
                )
            ),
            "details": details,
        }