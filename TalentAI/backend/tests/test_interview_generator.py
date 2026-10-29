from app.ai.llm.interview_generator import (
    InterviewQuestionGenerator,
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
            "1. Explain how you would handle "
            "class imbalance in a machine learning problem."
        )


def build_match_result():
    return {
        "job_title": "Data Scientist",
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


def test_interview_generator_returns_text():
    generator = InterviewQuestionGenerator(
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


def test_payload_contains_matched_skills():
    payload = (
        InterviewQuestionGenerator._build_payload(
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


def test_payload_contains_possible_skills():
    payload = (
        InterviewQuestionGenerator._build_payload(
            build_match_result()
        )
    )

    assert payload[
        "skill_alignment"
    ]["possible_skills"] == [
        "SQL"
    ]


def test_payload_contains_experience():
    payload = (
        InterviewQuestionGenerator._build_payload(
            build_match_result()
        )
    )

    assert payload[
        "experience_alignment"
    ]["candidate_years"] == 1.75

    assert payload[
        "experience_alignment"
    ]["required_years"] == 3.0


def test_payload_contains_project_information():
    payload = (
        InterviewQuestionGenerator._build_payload(
            build_match_result()
        )
    )

    assert payload[
        "project_alignment"
    ]["project_count"] == 1

    assert payload[
        "project_alignment"
    ]["score"] == 0.54


def test_prompt_contains_candidate_and_job():
    generator = InterviewQuestionGenerator(
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
    assert "SQL" in prompt


def test_generator_calls_llm_once():
    fake_llm = FakeLLM()

    generator = InterviewQuestionGenerator(
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


def test_invalid_match_result_is_safe():
    payload = (
        InterviewQuestionGenerator._build_payload(
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