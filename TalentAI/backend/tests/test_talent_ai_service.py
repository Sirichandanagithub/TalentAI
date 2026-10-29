from app.services.talent_ai_service import TalentAIService


class FakeMatchEngine:
    def __init__(self):
        self.calls = []

    def analyze(self, resume, job):
        self.calls.append(
            {
                "resume": resume,
                "job": job,
            }
        )

        return {
            "job_title": job.get("job_title"),
            "ats_score": 75.0,
            "classification": "strong",
        }


class FakeExplanationGenerator:
    def __init__(self):
        self.calls = []

    def generate(
        self,
        match_result,
        candidate_name=None,
        job_title=None,
    ):
        self.calls.append(
            {
                "match_result": match_result,
                "candidate_name": candidate_name,
                "job_title": job_title,
            }
        )

        return "Generated explanation"


class FakeResumeImprovementGenerator:
    def __init__(self):
        self.calls = []

    def generate(
        self,
        match_result,
        candidate_name=None,
        job_title=None,
    ):
        self.calls.append(
            {
                "match_result": match_result,
                "candidate_name": candidate_name,
                "job_title": job_title,
            }
        )

        return "Generated resume improvements"


class FakeATSOptimizer:
    def __init__(self):
        self.calls = []

    def generate(
        self,
        match_result,
        candidate_name=None,
        job_title=None,
    ):
        self.calls.append(
            {
                "match_result": match_result,
                "candidate_name": candidate_name,
                "job_title": job_title,
            }
        )

        return "Generated ATS optimization"


class FakeInterviewGenerator:
    def __init__(self):
        self.calls = []

    def generate(
        self,
        match_result,
        candidate_name=None,
        job_title=None,
    ):
        self.calls.append(
            {
                "match_result": match_result,
                "candidate_name": candidate_name,
                "job_title": job_title,
            }
        )

        return "Generated interview questions"


def create_service():
    """
    Create a TalentAIService with fake dependencies.
    """

    return TalentAIService(
        match_engine=FakeMatchEngine(),
        explanation_generator=FakeExplanationGenerator(),
        resume_improvement_generator=FakeResumeImprovementGenerator(),
        ats_optimizer=FakeATSOptimizer(),
        interview_generator=FakeInterviewGenerator(),
    )


def test_analyze_candidate_delegates_to_match_engine():
    service = create_service()

    resume = {
        "name": "Test Candidate",
        "skills": ["Python"],
    }

    job = {
        "job_title": "Data Scientist",
        "required_skills": ["Python"],
    }

    result = service.analyze_candidate(
        resume=resume,
        job=job,
    )

    assert result["ats_score"] == 75.0
    assert result["classification"] == "strong"

    assert len(service.match_engine.calls) == 1
    assert service.match_engine.calls[0]["resume"] == resume
    assert service.match_engine.calls[0]["job"] == job


def test_generate_explanation_delegates_correctly():
    service = create_service()

    match_result = {
        "ats_score": 75.0,
        "classification": "strong",
    }

    result = service.generate_explanation(
        match_result=match_result,
        candidate_name="Test Candidate",
        job_title="Data Scientist",
    )

    assert result == "Generated explanation"

    assert len(service.explanation_generator.calls) == 1

    call = service.explanation_generator.calls[0]

    assert call["match_result"] == match_result
    assert call["candidate_name"] == "Test Candidate"
    assert call["job_title"] == "Data Scientist"


def test_generate_resume_improvements_delegates_correctly():
    service = create_service()

    match_result = {
        "ats_score": 75.0,
    }

    result = service.generate_resume_improvements(
        match_result=match_result,
        candidate_name="Test Candidate",
        job_title="Data Scientist",
    )

    assert result == "Generated resume improvements"

    assert len(
        service.resume_improvement_generator.calls
    ) == 1


def test_generate_ats_optimization_delegates_correctly():
    service = create_service()

    match_result = {
        "ats_score": 75.0,
    }

    result = service.generate_ats_optimization(
        match_result=match_result,
        candidate_name="Test Candidate",
        job_title="Data Scientist",
    )

    assert result == "Generated ATS optimization"

    assert len(service.ats_optimizer.calls) == 1


def test_generate_interview_questions_delegates_correctly():
    service = create_service()

    match_result = {
        "job_title": "Data Scientist",
        "ats_score": 75.0,
    }

    result = service.generate_interview_questions(
        match_result=match_result,
        candidate_name="Test Candidate",
        job_title="Data Scientist",
    )

    assert result == "Generated interview questions"

    assert len(service.interview_generator.calls) == 1