
from app.ai.analyzer.candidate_job_reasoner import CandidateJobReasoner


def test_non_applicable_education_is_excluded():
    reasoner = CandidateJobReasoner()

    result = reasoner._calculate_overall_score(
        skill_alignment={"score": 0.355, "total": 3},
        experience_alignment={"score": 0.6667, "status": "partial"},
        relevant_experience={"score": 0.4, "required_years": 3},
        project_alignment={"score": 0.35, "status": "low"},
        education_alignment={"score": 1.0, "status": "not_required"},
        evidence_alignment={"score": 0.3333, "total_requirements": 3},
    )

    print("Education test score:", result)
    assert result == 0.4297
    print("PASS: Non-applicable education was excluded.")


def test_non_applicable_experience_is_excluded():
    reasoner = CandidateJobReasoner()

    result = reasoner._calculate_overall_score(
        skill_alignment={"score": 0.8, "total": 3},
        experience_alignment={"score": 1.0, "status": "not_required"},
        relevant_experience={"score": 0.5, "required_years": 3},
        project_alignment={"score": 0.6, "status": "low"},
        education_alignment={"score": 0.7, "status": "matched"},
        evidence_alignment={"score": 0.5, "total_requirements": 2},
    )

    print("Experience test score:", result)
    assert result == 0.675
    print("PASS: Non-applicable experience was excluded.")


def test_all_criteria_not_applicable():
    reasoner = CandidateJobReasoner()

    result = reasoner._calculate_overall_score(
        skill_alignment={"score": 0.0, "total": 0},
        experience_alignment={"score": 0.0, "status": "not_required"},
        relevant_experience={"score": 1.0, "required_years": 0},
        project_alignment={"score": 0.0, "status": "not_required"},
        education_alignment={"score": 1.0, "status": "not_required"},
        evidence_alignment={"score": 0.0, "total_requirements": 0},
    )

    print("All-not-applicable test score:", result)
    assert result == 0.0
    print("PASS: All non-applicable criteria return 0.0 safely.")



def test_not_required_experience_not_reported_as_strength():
    reasoner = CandidateJobReasoner()

    strengths = reasoner._build_strengths(
        skill_alignment={"matched": 2},
        experience_alignment={
            "score": 0.0,
            "status": "not_required",
            "required_years": None,
        },
        relevant_experience={
            "score": 1.0,
            "status": "not_required",
            "required_years": None,
        },
        project_alignment={"score": 0.5},
        evidence_alignment={"score": 0.5},
    )

    assert not any("relevant experience" in s.lower() for s in strengths)
    assert not any("overall experience" in s.lower() for s in strengths)

    print("PASS: Non-required experience is not reported as a strength.")

    
if __name__ == "__main__":
    print("Starting scoring tests...")

    test_non_applicable_education_is_excluded()
    test_non_applicable_experience_is_excluded()
    test_all_criteria_not_applicable()
    test_not_required_experience_not_reported_as_strength()

    print("\nAll scoring tests passed!")
