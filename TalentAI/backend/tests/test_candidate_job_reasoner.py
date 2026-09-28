from pprint import pprint

from app.ai.analyzer.candidate_job_reasoner import (
    CandidateJobReasoner,
)


def main():

    print("=" * 60)
    print("CANDIDATE-JOB REASONER TEST")
    print("=" * 60)

    match_result = {
        "skills": {
            "required": {
                "matched": [
                    {
                        "requirement": "Python",
                        "status": "matched",
                        "confidence": 1.0,
                    },
                    {
                        "requirement": "Machine Learning",
                        "status": "matched",
                        "confidence": 0.85,
                    },
                    {
                        "requirement": "Pandas",
                        "status": "matched",
                        "confidence": 0.95,
                    },
                    {
                        "requirement": "Scikit-learn",
                        "status": "matched",
                        "confidence": 0.95,
                    },
                    {
                        "requirement": "Data Analysis",
                        "status": "matched",
                        "confidence": 0.90,
                    },
                    {
                        "requirement": "Artificial Intelligence",
                        "status": "matched",
                        "confidence": 0.85,
                    },
                ],

                "possible": [
                    {
                        "requirement": "SQL",
                        "status": "possible",
                        "confidence": 0.21,
                    }
                ],

                "unknown": [],
            }
        },

        "experience": {
            "candidate_years": 1.67,
            "required_years": 3.0,
            "status": "partial",
        },

        "relevant_experience": {
            "relevant_years": 0.42,
            "required_years": 3.0,
        },

        "project_relevance": {
            "overall_project_relevance": 0.54,
            "project_count": 1,
            "status": "moderate",
        },

        "education": {
            "status": "unknown",
        },
    }

    reasoner = CandidateJobReasoner()

    evidence = {
        "Python": {
            "evidence_strength": 1.0,
            "evidence_quality": "strong",
        },

        "Machine Learning": {
            "evidence_strength": 1.0,
            "evidence_quality": "strong",
        },

        "Pandas": {
            "evidence_strength": 0.95,
            "evidence_quality": "strong",
        },

        "Scikit-learn": {
            "evidence_strength": 0.95,
            "evidence_quality": "strong",
        },

        "Data Analysis": {
            "evidence_strength": 0.90,
            "evidence_quality": "strong",
        },

        "Artificial Intelligence": {
            "evidence_strength": 0.95,
            "evidence_quality": "strong",
        },

        "SQL": {
            "evidence_strength": 0.0,
            "evidence_quality": "none",
        },
    }

    result = reasoner.reason(
        job_title="Data Scientist",
        match_result=match_result,
        evidence=evidence,
    )

    pprint(result)

    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Job title
    # ---------------------------------------------------------

    assert (
        result["job_title"]
        == "Data Scientist"
    )

    # ---------------------------------------------------------
    # Skill alignment
    # ---------------------------------------------------------

    assert (
        result["skill_alignment"]["matched"]
        == 6
    )

    assert (
        result["skill_alignment"]["possible"]
        == 1
    )

    assert (
        result["skill_alignment"]["unknown"]
        == 0
    )

    # ---------------------------------------------------------
    # Experience alignment
    # ---------------------------------------------------------

    assert (
        result["experience_alignment"]["candidate_years"]
        == 1.67
    )

    assert (
        result["experience_alignment"]["required_years"]
        == 3.0
    )

    assert (
        result["experience_alignment"]["status"]
        == "partial"
    )

    # ---------------------------------------------------------
    # Relevant experience
    # ---------------------------------------------------------

    assert (
        result["relevant_experience"]["relevant_years"]
        == 0.42
    )

    assert (
        result["relevant_experience"]["required_years"]
        == 3.0
    )

    # ---------------------------------------------------------
    # Project alignment
    # ---------------------------------------------------------

    assert (
        result["project_alignment"]["project_count"]
        == 1
    )

    assert (
        result["project_alignment"]["score"]
        == 0.54
    )

    # IMPORTANT:
    # The input project_relevance status is "moderate".
    # CandidateJobReasoner should preserve that status.

    assert (
        result["project_alignment"]["status"]
        == "moderate"
    )

    # ---------------------------------------------------------
    # Education alignment
    # ---------------------------------------------------------

    assert (
        result["education_alignment"]["status"]
        == "unknown"
    )

    # ---------------------------------------------------------
    # Overall score
    # ---------------------------------------------------------

    assert (
        0.0
        <= result["overall_score"]
        <= 1.0
    )

    print("\nProject alignment validation:")
    print(
        "Score:",
        result["project_alignment"]["score"]
    )
    print(
        "Project count:",
        result["project_alignment"]["project_count"]
    )
    print(
        "Status:",
        result["project_alignment"]["status"]
    )

    print("\n" + "=" * 60)
    print("✅ Candidate-job reasoning test passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()

    