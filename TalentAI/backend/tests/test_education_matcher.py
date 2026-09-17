from app.matcher.education_matcher import (
    match_education_requirement,
    match_education_requirements,
    match_education
)


# ============================================================
# TEST DATA
# ============================================================

education_entries = [

    {
        "institution":
            "Vignan Institute of Technology and Science",

        "program":
            "CSE_AI&DS",

        "location":
            "Hyderabad"
    }
]


# ============================================================
# TEST 1: EXACT MATCH
# ============================================================

print("=" * 60)
print("TEST 1: EXACT MATCH")
print("=" * 60)

result = match_education_requirement(
    "CSE_AI&DS",
    education_entries
)

print(result)


# ============================================================
# TEST 2: COMPUTER SCIENCE -> CSE
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: COMPUTER SCIENCE -> CSE")
print("=" * 60)

result = match_education_requirement(
    "Computer Science",
    education_entries
)

print(result)


# ============================================================
# TEST 3: ARTIFICIAL INTELLIGENCE -> AI
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: ARTIFICIAL INTELLIGENCE -> AI")
print("=" * 60)

result = match_education_requirement(
    "Artificial Intelligence",
    education_entries
)

print(result)


# ============================================================
# TEST 4: DATA SCIENCE -> DS
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: DATA SCIENCE -> DS")
print("=" * 60)

result = match_education_requirement(
    "Data Science",
    education_entries
)

print(result)


# ============================================================
# TEST 5: UNRELATED DEGREE
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: UNRELATED DEGREE")
print("=" * 60)

result = match_education_requirement(
    "Mechanical Engineering",
    education_entries
)

print(result)


# ============================================================
# TEST 6: MULTIPLE REQUIREMENTS
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: MULTIPLE REQUIREMENTS")
print("=" * 60)

requirements = [
    "Computer Science",
    "Data Science",
    "Artificial Intelligence",
    "Mechanical Engineering"
]

results = match_education_requirements(
    requirements,
    education_entries
)

for result in results:

    print("\nRequirement:")
    print(
        result["requirement"]
    )

    print(
        "Status:",
        result["status"]
    )

    print(
        "Confidence:",
        result["confidence"]
    )

    print(
        "Evidence:",
        result["evidence"]
    )


# ============================================================
# TEST 7: MASTER EDUCATION MATCH
# ============================================================

print("\n" + "=" * 60)
print("TEST 7: MASTER EDUCATION MATCH")
print("=" * 60)

resume = {
    "education": education_entries
}

required_education = [
    "Computer Science",
    "Data Science",
    "Artificial Intelligence",
    "Mechanical Engineering"
]

result = match_education(
    resume,
    required_education
)

print(result)


# ============================================================
# TEST 8: EMPTY REQUIREMENTS
# ============================================================

print("\n" + "=" * 60)
print("TEST 8: EMPTY REQUIREMENTS")
print("=" * 60)

result = match_education(
    resume,
    []
)

print(result)


# ============================================================
# TEST 9: EMPTY RESUME EDUCATION
# ============================================================

print("\n" + "=" * 60)
print("TEST 9: EMPTY RESUME EDUCATION")
print("=" * 60)

result = match_education(
    {
        "education": []
    },
    [
        "Computer Science"
    ]
)

print(result)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("EDUCATION MATCHER TEST FINISHED")
print("=" * 60)