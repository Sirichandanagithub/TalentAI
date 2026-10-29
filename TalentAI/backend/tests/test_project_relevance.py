
from app.ai.analyzer.project_relevance import ProjectRelevanceAnalyzer

resume_projects = [
    {
        "project_name": "Enterprise AI Assistant",
        "description": (
            "Built an AI-powered assistant using Python, FastAPI, "
            "LLM workflows and NLP."
        ),
        "technologies": [
            "Python",
            "FastAPI",
            "LangChain",
            "MySQL",
            "NLP",
        ],
    },
    {
        "project_name": "Sales Dashboard",
        "description": "Created data visualization dashboards.",
        "technologies": ["Python", "Pandas"],
    },
]

required = [
    "Python",
    "Machine Learning",
    "Pandas",
    "SQL",
    "Data Analysis",
]

preferred = ["AWS", "TensorFlow"]


def test_project_relevance():
    analyzer = ProjectRelevanceAnalyzer()

    result = analyzer.analyze(
        projects=resume_projects,
        required_skills=required,
        preferred_skills=preferred,
    )

    assert "overall_project_relevance" in result
    assert "relevant_projects" in result
    assert len(result["relevant_projects"]) == 2


def test_description_mention_does_not_prove_skill_usage():
    analyzer = ProjectRelevanceAnalyzer()

    project = {
        "project_name": "Customer Dashboard",
        "description": (
            "Built a dashboard. SQL is mentioned "
            "as a future learning goal."
        ),
        "technologies": ["Python", "Pandas"],
    }

    result = analyzer.analyze_project(
        project=project,
        required_skills=["SQL"],
        preferred_skills=[],
    )

    assert "SQL" not in result["matched_required"]
    assert "SQL" in result["unknown_required"]
