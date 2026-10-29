from app.ai.llm.resume_improvement import (
    ResumeImprovementGenerator,
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
            "The resume should present existing "
            "experience and project evidence more clearly."
        )


def build_match_result():
    return {
        "ats_score": 70.42,
        "classification": "strong",
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


def test_resume_improvement_generator():
    generator = ResumeImprovementGenerator(
        llm=FakeLLM()
    )

    result = generator.generate(
        match_result=build_match_result(),
        candidate_name="Candidate",
        job_title="Data Scientist",
    )

    assert isinstance(
        result,
        str,
    )

    assert result != ""


def test_payload_contains_deterministic_skill_names():
    payload = (
        ResumeImprovementGenerator._build_payload(
            build_match_result()
        )
    )

    assert payload[
        "skill_alignment"
    ]["matched_skills"] == [
        "Python",
        "Machine Learning",
        "Pandas",
    ]

    assert payload[
        "skill_alignment"
    ]["possible_skills"] == [
        "SQL"
    ]

    assert payload[
        "skill_alignment"
    ]["unknown_skills"] == []


def test_payload_contains_scores_from_match_engine():
    payload = (
        ResumeImprovementGenerator._build_payload(
            build_match_result()
        )
    )

    assert payload[
        "ats_score"
    ] == 70.42

    assert payload[
        "skill_alignment"
    ]["score"] == 0.8869

    assert payload[
        "experience_alignment"
    ]["candidate_years"] == 1.75

    assert payload[
        "experience_alignment"
    ]["required_years"] == 3.0

    assert payload[
        "project_alignment"
    ]["score"] == 0.54


def test_build_prompt_contains_candidate_and_job():
    generator = ResumeImprovementGenerator(
        llm=FakeLLM()
    )

    prompt = generator.build_prompt(
        match_result=build_match_result(),
        candidate_name="Candidate",
        job_title="Data Scientist",
    )

    assert "Candidate" in prompt
    assert "Data Scientist" in prompt
    assert "Python" in prompt
    assert "Machine Learning" in prompt


def test_generator_uses_llm():
    fake_llm = FakeLLM()

    generator = ResumeImprovementGenerator(
        llm=fake_llm
    )

    generator.generate(
        match_result=build_match_result(),
        candidate_name="Candidate",
        job_title="Data Scientist",
    )

    assert len(
        fake_llm.calls
    ) == 1


def test_invalid_match_result_does_not_crash():
    payload = (
        ResumeImprovementGenerator._build_payload(
            None
        )
    )

    assert isinstance(
        payload,
        dict,
    )

    assert payload[
        "skill_alignment"
    ]["matched_skills"] == []

    assert payload[
        "skill_alignment"
    ]["possible_skills"] == []

    assert payload[
        "skill_alignment"
    ]["unknown_skills"] == []

    