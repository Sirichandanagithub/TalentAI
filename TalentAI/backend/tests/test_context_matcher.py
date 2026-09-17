from app.ai.analyzer.context_matcher import ContextMatcher


# ============================================================
# SAMPLE RESUME
# ============================================================

resume = {
    "skills": {
        "programming": [
            "Python",
            "JavaScript"
        ],
        "data_science": [
            "Machine Learning",
            "Pandas",
            "Scikit-learn"
        ]
    },

    "experience": [
        {
            "job_title": "Data Analytics Intern",
            "company": "ABC Company",
            "description": (
                "Performed data analysis using Python and Pandas. "
                "Built reports and analyzed datasets."
            ),
            "raw_text": (
                "Data Analytics Intern - Python, Pandas, "
                "Data Analysis"
            )
        }
    ],

    "projects": [
        {
            "project_name": "Machine Learning Project",
            "description": (
                "Built a machine learning model using "
                "Python and Scikit-learn."
            ),
            "technologies": [
                "Python",
                "Pandas",
                "Scikit-learn"
            ]
        }
    ],

    "certifications": [
        {
            "name": "Machine Learning Certification"
        }
    ],

    "education": [
        {
            "institution": "Vignan Institute of Technology and Science",
            "degree": "CSE_AI&DS",
            "year": "2022-2026"
        }
    ]
}


# ============================================================
# INITIALIZE
# ============================================================

matcher = ContextMatcher()


# ============================================================
# TEST REQUIREMENTS
# ============================================================

requirements = [
    "Python",
    "Machine Learning",
    "Pandas",
    "Scikit-learn",
    "Data Analysis",
    "SQL",
    "TensorFlow"
]


# ============================================================
# RUN TESTS
# ============================================================

print("\n" + "=" * 70)
print("CONTEXT MATCHER TEST")
print("=" * 70)


for requirement in requirements:

    result = matcher.match(
        requirement,
        resume
    )

    print("\nRequirement:", requirement)

    print("Hybrid Status:")
    print("   ", result["hybrid_status"])

    print("Context Status:")
    print("   ", result["context_status"])

    print("Context Score:")
    print("   ", result["context_score"])

    print("Sources:")
    print("   ", result["sources"])

    print("Evidence:")

    for evidence in result["evidence"]:
        print("   ", evidence)

    print("Reason:")
    print("   ", result["reason"])


print("\n" + "=" * 70)
print("CONTEXT MATCHER TEST FINISHED")
print("=" * 70)