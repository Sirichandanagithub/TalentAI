from app.ai.analyzer.semantic_matcher_ai import (
    AISemanticMatcher
)


# ============================================================
# INITIALIZE
# ============================================================

print("=" * 60)
print("AI SEMANTIC MATCHER TEST")
print("=" * 60)

matcher = AISemanticMatcher()

print("AI semantic matcher initialized successfully.")


# ============================================================
# TEST 1: SQL -> MYSQL
# ============================================================

print("\n" + "=" * 60)
print("TEST 1: SQL -> MYSQL")
print("=" * 60)

result = matcher.match_requirement(
    "SQL",
    [
        "Python",
        "MySQL",
        "MongoDB",
        "HTML"
    ]
)

print(result)


# ============================================================
# TEST 2: MACHINE LEARNING -> CLASSIFICATION
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: MACHINE LEARNING -> CLASSIFICATION")
print("=" * 60)

result = matcher.match_requirement(
    "Machine Learning",
    [
        "JavaScript",
        "Classification",
        "HTML",
        "CSS"
    ]
)

print(result)


# ============================================================
# TEST 3: DATA SCIENCE -> DATA ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: DATA SCIENCE -> DATA ANALYSIS")
print("=" * 60)

result = matcher.match_requirement(
    "Data Science",
    [
        "Frontend Development",
        "Data Analysis",
        "HTML",
        "CSS"
    ]
)

print(result)


# ============================================================
# TEST 4: PYTHON -> JAVASCRIPT
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: PYTHON -> JAVASCRIPT")
print("=" * 60)

result = matcher.match_requirement(
    "Python",
    [
        "JavaScript",
        "HTML",
        "CSS"
    ]
)

print(result)


# ============================================================
# TEST 5: AWS -> MONGODB
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: AWS -> MONGODB")
print("=" * 60)

result = matcher.match_requirement(
    "AWS",
    [
        "MongoDB",
        "HTML",
        "CSS"
    ]
)

print(result)


# ============================================================
# TEST 6: MULTIPLE REQUIREMENTS
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: MULTIPLE REQUIREMENTS")
print("=" * 60)

requirements = [
    "Python",
    "SQL",
    "Machine Learning",
    "Data Science",
    "AWS"
]

candidate_skills = [
    "Python",
    "MySQL",
    "Classification",
    "Data Analysis",
    "MongoDB"
]

results = matcher.match_requirements(
    requirements,
    candidate_skills
)

for result in results:

    print("\nRequirement:", result["requirement"])
    print("Status:", result["status"])
    print("Confidence:", result["confidence"])
    print("Evidence:", result["evidence"])
    print("Match type:", result["match_type"])


# ============================================================
# TEST 7: COMPLETE JOB MATCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 7: COMPLETE JOB MATCH")
print("=" * 60)

required_skills = [
    "Python",
    "SQL",
    "Machine Learning",
    "Pandas",
    "Scikit-learn"
]

preferred_skills = [
    "AWS",
    "TensorFlow"
]

candidate_skills = [
    "Python",
    "MySQL",
    "Classification",
    "Data Analysis",
    "Deep Learning",
    "Docker"
]

result = matcher.match_job(
    required_skills,
    preferred_skills,
    candidate_skills
)

print(result)


# ============================================================
# TEST 8: EMPTY REQUIREMENT
# ============================================================

print("\n" + "=" * 60)
print("TEST 8: EMPTY REQUIREMENT")
print("=" * 60)

result = matcher.match_requirement(
    "",
    [
        "Python",
        "SQL"
    ]
)

print(result)


# ============================================================
# TEST 9: EMPTY CANDIDATE SKILLS
# ============================================================

print("\n" + "=" * 60)
print("TEST 9: EMPTY CANDIDATE SKILLS")
print("=" * 60)

result = matcher.match_requirement(
    "Python",
    []
)

print(result)


# ============================================================
# TEST 10: UNRELATED SKILLS
# ============================================================

print("\n" + "=" * 60)
print("TEST 10: UNRELATED SKILLS")
print("=" * 60)

result = matcher.match_requirement(
    "Machine Learning",
    [
        "Graphic Design",
        "Video Editing",
        "Photography"
    ]
)

print(result)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("AI SEMANTIC MATCHER TEST FINISHED")
print("=" * 60)