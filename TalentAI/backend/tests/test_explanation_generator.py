from app.ai.llm.explanation_generator import (
    ExplanationGenerator,
)

from app.ai.llm.prompts import SYSTEM_PROMPT


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self):
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)

        return FakeResponse(
            "The candidate has strong skill alignment "
            "but has an experience gap."
        )


def test_explanation_generator():
    """
    Test that ExplanationGenerator can build a prompt,
    call the injected LLM, and return its response.

    This test uses the same high-level structure produced
    by the Phase 4 CandidateJobReasoner.
    """

    fake_llm = FakeLLM()

    generator = ExplanationGenerator(
        llm=fake_llm
    )

    match_result = {
        "ats_score": 69.75,
        "classification": "strong",

        "candidate_job_reasoning":{
            "skill_alignment": {
            "matched": 6,
            "possible": 1,
            "unknown": 0,
            "score": 0.8869,
            "total": 7,
        },

        "experience_alignment": {
            "candidate_years": 1.67,
            "required_years": 3.0,
            "score": 0.5567,
            "status": "partial",
        },

        "relevant_experience": {
            "relevant_years": 1.34,
            "required_years": 3.0,
            "score": 0.4467,
        },

        "project_alignment": {
            "project_count": 1,
            "score": 0.54,
            "status": "moderate",
        },

        "education_alignment": {
            "score": 1.0,
            "status": "matched",
        },

        "evidence_alignment": {
            "requirements_with_evidence": 7,
            "score": 0.8286,
        },

        "gaps": [
            (
                "The candidate's documented overall experience "
                "is below the required experience."
            ),
            (
                "Relevant experience is below the target "
                "requirement."
            ),
        ],
    },
}

    result = generator.generate(
        match_result=match_result,
        candidate_name="Test Candidate",
        job_title="Data Scientist",
    )

    # --------------------------------------------------
    # Basic response validation
    # --------------------------------------------------

    assert isinstance(result, str)
    assert len(result) > 0

    # --------------------------------------------------
    # Verify LLM was called exactly once
    # --------------------------------------------------

    assert len(fake_llm.calls) == 1

    # --------------------------------------------------
    # Verify message structure
    # --------------------------------------------------

    messages = fake_llm.calls[0]

    assert len(messages) == 2

    assert messages[0][0] == "system"
    assert messages[1][0] == "human"

    # --------------------------------------------------
    # Verify important information reached the prompt
    # --------------------------------------------------

    prompt = messages[1][1]

    assert "Data Scientist" in prompt
    assert "Test Candidate" in prompt

    assert "69.75" in prompt
    assert "1.67" in prompt
    assert "1.34" in prompt
    assert "3.0" in prompt
    assert "0.8869" in prompt
    assert "0.54" in prompt
    assert "1.0" in prompt
    assert "0.8286" in prompt

    # --------------------------------------------------
    # Verify actual Phase 4 skill alignment structure
    # --------------------------------------------------

    assert "'matched': 6" in prompt
    assert "'possible': 1" in prompt
    assert "'unknown': 0" in prompt

    # --------------------------------------------------
    # Verify Phase 4 reasoning gaps
    # --------------------------------------------------

    assert "overall experience" in prompt
    assert "Relevant experience is below" in prompt

    # --------------------------------------------------
    # Internal fields must NOT be sent to the LLM
    # --------------------------------------------------

    assert "DO_NOT_SEND" not in prompt


def test_llm_payload_contains_only_controlled_fields():
    """
    Verify that ExplanationGenerator exposes only approved
    high-level fields to the LLM.

    Internal TalentMatchEngine structures must not be passed
    directly to the model.
    """

    match_result = {
        "ats_score": 80,
        "classification": "strong",

        "skill_alignment": {
            "matched": 6,
            "possible": 1,
            "unknown": 0,
            "score": 0.85,
            "total": 7,
        },

        "experience_alignment": {
            "candidate_years": 2.0,
            "required_years": 3.0,
            "score": 0.6667,
            "status": "partial",
        },

        "relevant_experience": {
            "relevant_years": 1.5,
            "required_years": 3.0,
            "score": 0.5,
        },

        "project_alignment": {
            "project_count": 1,
            "score": 0.7,
            "status": "moderate",
        },

        "education_alignment": {
            "score": 1.0,
            "status": "matched",
        },

        "evidence_alignment": {
            "requirements_with_evidence": 6,
            "score": 0.85,
        },

        "gaps": [
            "Experience is below the required level."
        ],

        # Internal field that should never be exposed.
        "secret_internal_field": "PRIVATE",

        # Internal matching details that should also
        # remain outside the LLM payload.
        "evidence": {
            "Python": {
                "best_source": "project",
                "weight": 0.95,
            }
        },

        "context": {
            "Python": {
                "context_score": 0.95,
            }
        },

        "reasoning": {
            "Python": {
                "confidence": 0.96,
            }
        },
    }

    payload = (
        ExplanationGenerator._build_llm_payload(
            match_result
        )
    )

    # --------------------------------------------------
    # Approved high-level fields
    # --------------------------------------------------

    assert "ats_score" in payload
    assert "classification" in payload
    assert "skill_alignment" in payload
    assert "experience_alignment" in payload
    assert "relevant_experience" in payload
    assert "project_alignment" in payload
    assert "education_alignment" in payload
    assert "evidence_alignment" in payload
    assert "gaps" in payload

    # --------------------------------------------------
    # Internal fields must NOT be exposed
    # --------------------------------------------------

    assert "secret_internal_field" not in payload
    assert "evidence" not in payload
    assert "context" not in payload
    assert "reasoning" not in payload


def test_prompt_prevents_unsupported_skill_claims():
    """
    Verify that the prompt prevents the LLM from inventing
    skill gaps or unsupported claims.

    The actual Phase 4 result does not contain a top-level
    skill_gaps field, so this test uses the real skill
    alignment structure.
    """

    match_result = {
        "ats_score": 69.75,
        "classification": "strong",

        "candidate_job_reasoning": {
            "skill_alignment": {
            "matched": 6,
            "possible": 1,
            "unknown": 0,
            "score": 0.8869,
            "total": 7,
        },

        "experience_alignment": {
            "candidate_years": 1.67,
            "required_years": 3.0,
            "score": 0.5567,
            "status": "partial",
        },

        "relevant_experience": {
            "relevant_years": 1.34,
            "required_years": 3.0,
            "score": 0.4467,
            "required_years": 3.0,
        },

        "gaps": [
            (
                "The candidate's documented overall experience "
                "is below the required experience."
            ),
            (
                "Relevant experience is below the target "
                "requirement."
            ),
        ],
    },
}

    generator = ExplanationGenerator(
        llm=FakeLLM()
    )

    prompt = generator.build_prompt(
        match_result=match_result,
        candidate_name="Test Candidate",
        job_title="Data Scientist",
    )

    prompt_lower = prompt.lower()

    # --------------------------------------------------
    # Prompt must prevent invention
    # --------------------------------------------------

    assert "do not invent information" in prompt_lower

    assert (
        "do not create additional skill gaps"
        in prompt_lower
    )

    # --------------------------------------------------
    # The real Phase 4 structure should be present
    # --------------------------------------------------

    assert "0.8869" in prompt
    assert "'matched': 6" in prompt
    assert "'possible': 1" in prompt
    assert "'unknown': 0" in prompt

    # --------------------------------------------------
    # We must NOT inject artificial skill gaps
    # --------------------------------------------------

    assert "TensorFlow" not in prompt
    assert "AWS" not in prompt


def test_system_prompt_prevents_skill_overclaiming():
    """
    Verify that the system prompt contains safeguards
    against unsupported claims.
    """

    prompt = SYSTEM_PROMPT.lower()

    # A skill gap must not automatically be described
    # as a confirmed lack of experience.
    assert (
        "never say that the candidate definitely lacks the skill"
        in prompt
    )

    # A matched skill must not automatically become
    # expertise or proficiency.
    assert (
        "never describe a matched skill as"
        in prompt
    )

def test_skill_gap_rules_prevent_unsupported_claims():
    from app.ai.llm.prompts import (
        SYSTEM_PROMPT,
        EXPLANATION_PROMPT,
    )

    combined_prompt = (
        SYSTEM_PROMPT
        + "\n"
        + EXPLANATION_PROMPT
    ).lower()

    assert "unknown_skills" in combined_prompt
    assert "never invent additional skill names" in combined_prompt
    assert (
        "does not prove that the candidate lacks that skill"
        in combined_prompt
    )
    assert (
        "do not say that the candidate definitely lacks an unknown skill"
        in combined_prompt
    )

def test_skill_names_are_extracted_from_deterministic_match_result():
    """
    Verify that actual skill names from TalentMatchEngine's
    deterministic classification are transferred into the
    controlled LLM payload.

    The LLM must receive the classifications already produced
    by the matching engine. It must not invent or infer them.
    """

    match_result = {
        "ats_score": 75.0,
        "classification": "strong",

        # This represents the deterministic structure produced
        # by TalentMatchEngine.
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
                            "requirement": "SQL",
                            "status": "unknown",
                        }
                    ],
                }
            }
        },

        "candidate_job_reasoning": {
            "skill_alignment": {
                "matched": 1,
                "possible": 1,
                "unknown": 1,
                "score": 0.67,
                "total": 3,
            },

            "experience_alignment": {
                "candidate_years": 1.5,
                "required_years": 3.0,
                "score": 0.5,
                "status": "partial",
            },

            "relevant_experience": {
                "relevant_years": 1.0,
                "required_years": 3.0,
                "score": 0.33,
            },

            "project_alignment": {
                "project_count": 1,
                "score": 0.5,
                "status": "moderate",
            },

            "education_alignment": {
                "score": 1.0,
                "status": "matched",
            },

            "evidence_alignment": {
                "requirements_with_evidence": 2,
                "score": 0.67,
            },

            "gaps": [
                "Experience is below the required level."
            ],
        },
    }

    payload = (
        ExplanationGenerator._build_llm_payload(
            match_result
        )
    )

    skill_alignment = payload["skill_alignment"]

    # --------------------------------------------------
    # Verify actual skill names are present
    # --------------------------------------------------

    assert "Python" in skill_alignment["matched_skills"]

    assert (
        "Machine Learning"
        in skill_alignment["possible_skills"]
    )

    assert "SQL" in skill_alignment["unknown_skills"]

    # --------------------------------------------------
    # Verify classifications were not mixed
    # --------------------------------------------------

    assert "SQL" not in skill_alignment["matched_skills"]
    assert "SQL" not in skill_alignment["possible_skills"]

    assert "Python" not in skill_alignment["possible_skills"]
    assert "Python" not in skill_alignment["unknown_skills"]

    assert (
        "Machine Learning"
        not in skill_alignment["matched_skills"]
    )

    assert (
        "Machine Learning"
        not in skill_alignment["unknown_skills"]
    )