from app.ai.analyzer.evidence_engine import (
    collect_evidence,
    collect_evidence_for_requirements
)


# ============================================================
# TEST RESUME
# ============================================================

resume = {

    "summary":
        "Data professional with experience in Python and "
        "machine learning.",

    "skills": [
        "Python",
        "MySQL",
        "Data Analysis",
        "Docker"
    ],

    "experience": [

        {
            "job_title": "Data Analytics Intern",
            "company":
                "Renu Sharma Healthcare and Education Foundation",
            "description":
                "Worked on data-driven analysis using Python "
                "and statistical analysis."
        },

        {
            "job_title": "Research Intern",
            "company":
                "Bharat Dynamics Limited",
            "description":
                "Worked on secure system design and "
                "problem-solving."
        }
    ],

    "projects": [

        {
            "project_name":
                "AI Crime Prediction System",

            "description":
                "Developed an AI-powered crime prediction "
                "system using machine learning and Python.",

            "technologies": [
                "Python",
                "Pandas",
                "Scikit-learn",
                "Django"
            ]
        },

        {
            "project_name":
                "Job Tracker App",

            "description":
                "Web application for tracking job applications.",

            "technologies": [
                "HTML",
                "CSS",
                "JavaScript"
            ]
        }
    ],

    "certifications": [

        {
            "certification_name":
                "Data Engineering with Hadoop and Spark",

            "issuer":
                "GeeksforGeeks",

            "description":
                "Training in Hadoop and Spark."
        }
    ],

    "education": [

        {
            "degree":
                "B.Tech CSE AI and Data Science",

            "institution":
                "Vignan Institute of Technology and Science",

            "description":
                "Computer Science, Artificial Intelligence "
                "and Data Science"
        }
    ]
}


# ============================================================
# INITIALIZATION
# ============================================================

print("=" * 60)
print("EVIDENCE ENGINE TEST")
print("=" * 60)

print("Evidence engine initialized successfully.")


# ============================================================
# TEST 1: SKILL EVIDENCE
# ============================================================

print("\n" + "=" * 60)
print("TEST 1: PYTHON")
print("=" * 60)

result = collect_evidence(
    "Python",
    resume
)

print(result)


# ============================================================
# TEST 2: PROJECT EVIDENCE
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: PANDAS")
print("=" * 60)

result = collect_evidence(
    "Pandas",
    resume
)

print(result)


# ============================================================
# TEST 3: EXPERIENCE EVIDENCE
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: STATISTICAL ANALYSIS")
print("=" * 60)

result = collect_evidence(
    "Statistical Analysis",
    resume
)

print(result)


# ============================================================
# TEST 4: EDUCATION EVIDENCE
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: ARTIFICIAL INTELLIGENCE")
print("=" * 60)

result = collect_evidence(
    "Artificial Intelligence",
    resume
)

print(result)


# ============================================================
# TEST 5: CERTIFICATION EVIDENCE
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: HADOOP")
print("=" * 60)

result = collect_evidence(
    "Hadoop",
    resume
)

print(result)


# ============================================================
# TEST 6: PROJECT TECHNOLOGY
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: SCIKIT-LEARN")
print("=" * 60)

result = collect_evidence(
    "Scikit-learn",
    resume
)

print(result)


# ============================================================
# TEST 7: UNKNOWN SKILL
# ============================================================

print("\n" + "=" * 60)
print("TEST 7: AWS")
print("=" * 60)

result = collect_evidence(
    "AWS",
    resume
)

print(result)


# ============================================================
# TEST 8: MULTIPLE SOURCES
# ============================================================

print("\n" + "=" * 60)
print("TEST 8: MACHINE LEARNING")
print("=" * 60)

result = collect_evidence(
    "Machine Learning",
    resume
)

print(result)


# ============================================================
# TEST 9: MULTIPLE REQUIREMENTS
# ============================================================

print("\n" + "=" * 60)
print("TEST 9: MULTIPLE REQUIREMENTS")
print("=" * 60)

requirements = [
    "Python",
    "SQL",
    "Machine Learning",
    "Pandas",
    "Scikit-learn",
    "AWS"
]

results = collect_evidence_for_requirements(
    requirements,
    resume
)

for result in results:

    print("\nRequirement:")
    print(result["requirement"])

    print(
        "Status:",
        result["status"]
    )

    print(
        "Evidence count:",
        result["evidence_count"]
    )

    print(
        "Best source:",
        result["best_source"]
    )

    print(
        "Evidence strength:",
        result["evidence_strength"]
    )

    print(
        "Evidence:",
        result["evidence"]
    )


# ============================================================
# TEST 10: EMPTY REQUIREMENT
# ============================================================

print("\n" + "=" * 60)
print("TEST 10: EMPTY REQUIREMENT")
print("=" * 60)

result = collect_evidence(
    "",
    resume
)

print(result)


# ============================================================
# TEST 11: EMPTY RESUME
# ============================================================

print("\n" + "=" * 60)
print("TEST 11: EMPTY RESUME")
print("=" * 60)

result = collect_evidence(
    "Python",
    {}
)

print(result)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("EVIDENCE ENGINE TEST FINISHED")
print("=" * 60)