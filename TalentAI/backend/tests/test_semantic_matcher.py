from app.matcher.semantic_matcher import (
    match_concept,
    match_requirements
)


# ============================================================
# TEST 1: EXACT MATCH
# ============================================================

print("=" * 60)
print("TEST 1: EXACT MATCH")
print("=" * 60)

result = match_concept(
    "Python",
    ["Python", "JavaScript", "MySQL"]
)

print(result)


# ============================================================
# TEST 2: RELATED MATCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: SQL -> MySQL")
print("=" * 60)

result = match_concept(
    "SQL",
    ["Python", "MySQL", "MongoDB"]
)

print(result)


# ============================================================
# TEST 3: MACHINE LEARNING
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: MACHINE LEARNING")
print("=" * 60)

result = match_concept(
    "Machine Learning",
    [
        "Python",
        "Classification",
        "Regression",
        "Deep Learning"
    ]
)

print(result)


# ============================================================
# TEST 4: UNKNOWN
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: UNKNOWN")
print("=" * 60)

result = match_concept(
    "AWS",
    [
        "Python",
        "MySQL",
        "Docker",
        "Git"
    ]
)

print(result)


# ============================================================
# TEST 5: MULTIPLE REQUIREMENTS
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: MULTIPLE REQUIREMENTS")
print("=" * 60)

requirements = [
    "Python",
    "SQL",
    "Machine Learning",
    "Pandas",
    "AWS"
]

candidate_skills = [
    "Python",
    "MySQL",
    "Classification",
    "Regression",
    "Deep Learning",
    "Docker"
]

results = match_requirements(
    requirements,
    candidate_skills
)

for result in results:

    print(
        f"\nRequirement : {result['requirement']}"
    )

    print(
        f"Status      : {result['status']}"
    )

    print(
        f"Confidence  : {result['confidence']}"
    )

    print(
        f"Evidence    : {result['evidence']}"
    )


print("\n")
print("=" * 60)
print("SEMANTIC MATCHER TEST FINISHED")
print("=" * 60)