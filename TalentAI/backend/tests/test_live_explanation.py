"""
Live integration test for TalentAI Phase 4 → Phase 5.

This test:

1. Builds the same candidate and job data used by
   the TalentMatchEngine regression test.
2. Runs the real TalentMatchEngine.
3. Passes the real match result to ExplanationGenerator.
4. Sends the controlled explanation payload to Qwen3
   through Ollama.
5. Prints the generated explanation.

IMPORTANT:
This test requires Ollama and qwen3:1.7b to be available.
"""

from app.ai.analyzer.talent_match_engine import TalentMatchEngine
from app.ai.llm.explanation_generator import ExplanationGenerator


def test_live_explanation_generation():
    """
    Run the actual TalentAI Phase 4 matching engine and
    generate a Phase 5 LLM explanation.
    """

    # ==================================================
    # Candidate Resume
    # ==================================================

    resume = {
        "name": "Test Candidate",

        "summary": (
            "Data professional with experience in Python "
            "and machine learning."
        ),

        "skills": [
            "Python",
            "JavaScript",
            "MySQL",
            "MongoDB",
            "NoSQL",
            "Data Analysis",
            "Statistical Analysis",
            "Classification",
            "Regression",
            "Deep Learning",
            "Git",
            "Docker",
            "HTML",
            "CSS",
        ],

        "experience": [
            {
                "job_title": "Associate AI Engineer",
                "company": "Novum Labs",
                "location": "Hyderabad",
                "dates": {
                    "start": "January 2025",
                    "end": "Present",
                    "current": True,
                },
            }
        ],

        "education": [
            {
                "institution": (
                    "Vignan Institute of Technology and Science"
                ),
                "degree": "B.Tech",
                "field": "CSE_AI&DS",
                "year": "2026",
            }
        ],

        "projects": [
            {
                "project_name": "AI Crime Prediction System",
                "description": (
                    "Developed an AI-powered crime prediction "
                    "system using machine learning and Python."
                ),
                "technologies": [
                    "Python",
                    "Pandas",
                    "Scikit-learn",
                    "Django",
                ],
            }
        ],
    }

    # ==================================================
    # Target Job
    # ==================================================

    job = {
        "job_title": "Data Scientist",

        "required_skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
            "Scikit-learn",
            "Data Analysis",
            "Artificial Intelligence",
        ],

        "preferred_skills": [
            "TensorFlow",
            "AWS",
        ],

        "experience": {
            "minimum_years": 3,
        },

        "education": [
            "computer science",
            "data science",
            "artificial intelligence",
        ],
    }

    # ==================================================
    # Phase 4 — Real Matching Engine
    # ==================================================

    engine = TalentMatchEngine()

    match_result = engine.analyze(
        resume=resume,
        job=job,
    )

    # ==================================================
    # Basic validation of Phase 4 result
    # ==================================================

    assert isinstance(match_result, dict)

    assert "ats_score" in match_result
    assert "classification" in match_result

    reasoning = match_result.get(
        "candidate_job_reasoning",
        {}
    )

    assert isinstance(reasoning, dict)

    assert "skill_alignment" in reasoning
    assert "experience_alignment" in reasoning
    assert "relevant_experience" in reasoning
    assert "project_alignment" in reasoning
    assert "education_alignment" in reasoning
    assert "evidence_alignment" in reasoning
    



    # ==================================================
    # Phase 5 — Explanation Generator
    # ==================================================

    generator = ExplanationGenerator()

    explanation = generator.generate(
        match_result=match_result,
        candidate_name=resume["name"],
        job_title=job["job_title"],
    )

    # ==================================================
    # Validate LLM response
    # ==================================================

    assert isinstance(explanation, str)

    assert len(explanation.strip()) > 0

    # ==================================================
    # Display results
    # ==================================================

    print("\n")
    print("=" * 70)
    print("PHASE 4 MATCH RESULT")
    print("=" * 70)

    print(
        "ATS Score:",
        match_result.get("ats_score"),
    )

    print(
        "Classification:",
        match_result.get("classification"),
    )

    print(
        "Candidate-Job Reasoning:",
        match_result.get("candidate_job_reasoning"),
    )

    print("\n")
    print("=" * 70)
    print("PHASE 5 LLM EXPLANATION")
    print("=" * 70)

    print(explanation)

    print("\n")
    print("=" * 70)
    print("LIVE EXPLANATION TEST PASSED")
    print("=" * 70)