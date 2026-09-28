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
            "NLP"
        ]
    },
    {
        "project_name": "Sales Dashboard",
        "description": "Created data visualization dashboards.",
        "technologies": [
            "Python",
            "Pandas"
        ]
    }
]

required = [
    "Python",
    "Machine Learning",
    "Pandas",
    "SQL",
    "Data Analysis"
]

preferred = [
    "AWS",
    "TensorFlow"
]


def test_project_relevance():

    analyzer = ProjectRelevanceAnalyzer()

    result = analyzer.analyze(
        projects=resume_projects,
        required_skills=required,
        preferred_skills=preferred
    )

    print("\nPROJECT RELEVANCE RESULT")
    print("=" * 60)

    print(result)

    assert "overall_project_relevance" in result
    assert "relevant_projects" in result
    assert len(result["relevant_projects"]) == 2

    print("\nTEST PASSED")


if __name__ == "__main__":
    test_project_relevance()