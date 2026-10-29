from app.ai.llm.ats_optimizer import (
    ATSOptimizer,
)


class FakeResponse:
    def __init__(
        self,
        content: str,
    ):
        self.content = content


class FakeLLM:
    def __init__(self):
        self.calls = []

    def invoke(
        self,
        messages,
    ):
        self.calls.append(
            messages
        )

        return FakeResponse(
            "The resume can improve ATS alignment "
            "by presenting existing evidence more clearly."
        )


def build_match_result():
    return {
        "ats_score": 70.42,
        "classification": "strong",
        "score_breakdown": {
            "skills": 0.8869,
            "experience": 0.5833,
            "projects": 0.54,
            "education": 1.0,
        },
        "ats": {
            "score": 70.42,
            "classification": "strong",
        },
        "candidate_job_reasoning": {
            "skill_alignment": {
                "matched": 6,
                "possible": 1,
                "unknown": 0,
                "score": 0.8869,
            },
            "experience_alignment": {
                "candidate_years": 1.75,
                "required_years": 3.0,
                "score": 0.5833,
                "status": "partial",
            },
            "relevant_experience": {
                "relevant_years": 1.4,
                "required_years": 3.0,
                "score": 0.4667,
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
                    "The candidate's documented overall "
                    "experience is below the required "
                    "experience."
                ),
                "Relevant experience is below the target requirement.",
            ],
        },
        "match": {
            "skills": {
                "required": {
                    "matched": [
                        {
                            "requirement": "Python",
                            "status": "matched",
                        },
                        {
                            "requirement": "Machine Learning",
                            "status": "matched",
                        },
                        {
                            "requirement": "Pandas",
                            "status": "matched",
                        },
                    ],
                    "possible": [
                        {
                            "requirement": "SQL",
                            "status": "possible",
                        },
                    ],
                    "unknown": [],
                }
            }
        },
    }


def test_ats_optimizer_generates_output():
    optimizer = ATSOptimizer(
        llm=FakeLLM()
    )

    result = optimizer.generate(
        match_result=build_match_result(),
        candidate_name="Candidate",
        job_title="Data Scientist",
    )

    assert isinstance(
        result,
        str,
    )

    assert result != ""


def test_payload_preserves_ats_score():
    payload = ATSOptimizer._build_payload(
        build_match_result()
    )

    assert payload[
        "ats_score"
    ] == 70.42

    assert payload[
        "ats_details"
    ]["score"] == 70.42


def test_payload_preserves_skill_classifications():
    payload = ATSOptimizer._build_payload(
        build_match_result()
    )

    skills = payload[
        "skill_alignment"
    ]

    assert skills[
        "matched_skills"
    ] == [
        "Python",
        "Machine Learning",
        "Pandas",
    ]

    assert skills[
        "possible_skills"
    ] == [
        "SQL"
    ]

    assert skills[
        "unknown_skills"
    ] == []


def test_payload_preserves_experience_data():
    payload = ATSOptimizer._build_payload(
        build_match_result()
    )

    experience = payload[
        "experience_alignment"
    ]

    assert experience[
        "candidate_years"
    ] == 1.75

    assert experience[
        "required_years"
    ] == 3.0

    assert experience[
        "score"
    ] == 0.5833


def test_payload_preserves_project_and_evidence_data():
    payload = ATSOptimizer._build_payload(
        build_match_result()
    )

    assert payload[
        "project_alignment"
    ]["score"] == 0.54

    assert payload[
        "evidence_alignment"
    ]["score"] == 0.8286


def test_build_prompt_contains_target_information():
    optimizer = ATSOptimizer(
        llm=FakeLLM()
    )

    prompt = optimizer.build_prompt(
        match_result=build_match_result(),
        candidate_name="Candidate",
        job_title="Data Scientist",
    )

    assert "Candidate" in prompt
    assert "Data Scientist" in prompt
    assert "70.42" in prompt
    assert "Python" in prompt


def test_optimizer_calls_llm_once():
    fake_llm = FakeLLM()

    optimizer = ATSOptimizer(
        llm=fake_llm
    )

    optimizer.generate(
        match_result=build_match_result(),
        candidate_name="Candidate",
        job_title="Data Scientist",
    )

    assert len(
        fake_llm.calls
    ) == 1


def test_invalid_match_result_is_safe():
    payload = ATSOptimizer._build_payload(
        None
    )

    assert isinstance(
        payload,
        dict,
    )

    assert payload[
        "ats_score"
    ] is None

    assert payload[
        "skill_alignment"
    ]["matched_skills"] == []

    assert payload[
        "skill_alignment"
    ]["possible_skills"] == []

    assert payload[
        "skill_alignment"
    ]["unknown_skills"] == []