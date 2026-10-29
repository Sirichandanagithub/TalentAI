from app.ai.llm.output_validator import (
    ExplanationOutputValidator,
)


def build_match_result(
    unknown_skills=None,
):
    """
    Build a small deterministic TalentAI matching result
    for validator tests.
    """

    if unknown_skills is None:
        unknown_skills = []

    return {
        "match": {
            "skills": {
                "required": {
                    "matched": [
                        {
                            "requirement": "Python",
                            "status": "matched",
                        }
                    ],
                    "possible": [
                        {
                            "requirement": "Machine Learning",
                            "status": "possible",
                        }
                    ],
                    "unknown": [
                        {
                            "requirement": skill,
                            "status": "unknown",
                        }
                        for skill in unknown_skills
                    ],
                }
            }
        }
    }


def test_unknown_skill_with_insufficient_evidence_is_valid():
    """
    An unknown skill can be mentioned when the explanation
    correctly states that the resume does not provide
    sufficient evidence.
    """

    match_result = build_match_result(
        unknown_skills=["SQL"]
    )

    explanation = (
        "The resume does not provide sufficient "
        "evidence for SQL."
    )

    result = ExplanationOutputValidator.validate(
        explanation=explanation,
        match_result=match_result,
    )

    assert result["valid"] is True
    assert result["unsupported_skills"] == []
    assert result["unknown_skill_claims"] == []


def test_unknown_skill_claiming_candidate_lacks_skill_is_invalid():
    """
    An unknown skill must not be converted into a definitive
    claim that the candidate lacks the skill.
    """

    match_result = build_match_result(
        unknown_skills=["SQL"]
    )

    explanation = (
        "The candidate lacks SQL."
    )

    result = ExplanationOutputValidator.validate(
        explanation=explanation,
        match_result=match_result,
    )

    assert result["valid"] is False
    assert "SQL" in result["unsupported_skills"]
    assert "SQL" in result["unknown_skill_claims"]


def test_unknown_skill_claiming_no_proficiency_is_invalid():
    """
    An unknown skill must not be converted into a definitive
    proficiency claim.
    """

    match_result = build_match_result(
        unknown_skills=["SQL"]
    )

    explanation = (
        "The candidate is not proficient in SQL."
    )

    result = ExplanationOutputValidator.validate(
        explanation=explanation,
        match_result=match_result,
    )

    assert result["valid"] is False
    assert "SQL" in result["unsupported_skills"]
    assert "SQL" in result["unknown_skill_claims"]


def test_no_unknown_skills_is_valid():
    """
    If there are no unknown skills, the validator should
    not report unsupported unknown-skill claims.
    """

    match_result = build_match_result()

    explanation = (
        "The candidate has strong alignment with "
        "the required skills."
    )

    result = ExplanationOutputValidator.validate(
        explanation=explanation,
        match_result=match_result,
    )

    assert result["valid"] is True
    assert result["unsupported_skills"] == []
    assert result["unknown_skill_claims"] == []


def test_invalid_explanation_input_is_invalid():
    """
    The validator should reject non-string explanations.
    """

    match_result = build_match_result(
        unknown_skills=["SQL"]
    )

    result = ExplanationOutputValidator.validate(
        explanation=None,
        match_result=match_result,
    )

    assert result["valid"] is False
    assert result["unsupported_skills"] == []
    assert result["unknown_skill_claims"] == []

    assert (
        "Explanation must be a string."
        in result["details"]
    )
    