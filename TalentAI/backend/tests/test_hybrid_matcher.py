from app.ai.analyzer.hybrid_matcher import HybridMatcher


# ============================================================
# INITIALIZE
# ============================================================

print("=" * 60)
print("HYBRID MATCHER TEST")
print("=" * 60)

matcher = HybridMatcher()

print("Hybrid matcher initialized successfully.")


# ============================================================
# TEST 1: EXACT MATCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 1: EXACT MATCH")
print("=" * 60)

result = matcher.match_requirement(
    "Python",
    [
        "Python",
        "JavaScript",
        "MySQL"
    ]
)

print(result)


# ============================================================
# TEST 2: SQL -> MYSQL
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: SQL -> MYSQL")
print("=" * 60)

result = matcher.match_requirement(
    "SQL",
    [
        "Python",
        "MySQL",
        "MongoDB"
    ]
)

print(result)


# ============================================================
# TEST 3: MACHINE LEARNING -> CLASSIFICATION
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: MACHINE LEARNING -> CLASSIFICATION")
print("=" * 60)

result = matcher.match_requirement(
    "Machine Learning",
    [
        "JavaScript",
        "Classification",
        "HTML"
    ]
)

print(result)


# ============================================================
# TEST 4: DATA SCIENCE -> DATA ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: DATA SCIENCE -> DATA ANALYSIS")
print("=" * 60)

result = matcher.match_requirement(
    "Data Science",
    [
        "Data Analysis",
        "HTML",
        "CSS"
    ]
)

print(result)


# ============================================================
# TEST 5: AI SEMANTIC MATCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: PREDICTIVE MODELING")
print("=" * 60)

result = matcher.match_requirement(
    "Machine Learning",
    [
        "Predictive modeling",
        "HTML",
        "CSS"
    ]
)

print(result)


# ============================================================
# TEST 6: POSSIBLE RELATIONSHIP
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: TENSORFLOW -> DEEP LEARNING")
print("=" * 60)

result = matcher.match_requirement(
    "TensorFlow",
    [
        "Deep Learning",
        "Python",
        "Docker"
    ]
)

print(result)


# ============================================================
# TEST 7: UNRELATED SKILL
# ============================================================

print("\n" + "=" * 60)
print("TEST 7: UNRELATED SKILL")
print("=" * 60)

result = matcher.match_requirement(
    "Python",
    [
        "Graphic Design",
        "Photography",
        "Video Editing"
    ]
)

print(result)


# ============================================================
# TEST 8: MULTIPLE REQUIREMENTS
# ============================================================

print("\n" + "=" * 60)
print("TEST 8: MULTIPLE REQUIREMENTS")
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
    print("Rule Match:", result["rule_match"])
    print(
        "Semantic Similarity:",
        result["semantic_similarity"]
    )
    print("Relationship:", result["relationship"])
    print("Match Source:", result["match_source"])


# ============================================================
# TEST 9: COMPLETE JOB MATCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 9: COMPLETE JOB MATCH")
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
# TEST 10: EMPTY INPUT
# ============================================================

print("\n" + "=" * 60)
print("TEST 10: EMPTY INPUT")
print("=" * 60)

result = matcher.match_requirement(
    "",
    []
)

print(result)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("HYBRID MATCHER TEST FINISHED")
print("=" * 60)