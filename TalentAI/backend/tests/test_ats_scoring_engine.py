from app.ai.analyzer.ats_scoring_engine import (
    calculate_ats_score,
    calculate_skill_score,
    calculate_experience_score,
    calculate_education_score,
    calculate_project_score,
    calculate_preferred_score,
    extract_missing_requirements,
    extract_matched_requirements,
    generate_score_summary
)


print("=" * 60)
print("ATS SCORING ENGINE TEST")
print("=" * 60)


# ============================================================
# SAMPLE MATCH RESULT
# ============================================================

match_result = {

    "skills": {

        "required": {

            "matched": [
                {
                    "requirement": "Python",
                    "confidence": 1.0
                },
                {
                    "requirement": "SQL",
                    "confidence": 0.75
                },
                {
                    "requirement": "Machine Learning",
                    "confidence": 0.75
                },
                {
                    "requirement": "Data Analysis",
                    "confidence": 1.0
                }
            ],

            "possible": [],

            "unknown": [
                {
                    "requirement": "Pandas",
                    "confidence": 0.0
                },
                {
                    "requirement": "Scikit-learn",
                    "confidence": 0.0
                }
            ]
        },

        "preferred": {

            "matched": [],

            "possible": [
                {
                    "requirement": "TensorFlow",
                    "confidence": 0.5366
                }
            ],

            "unknown": [
                {
                    "requirement": "AWS",
                    "confidence": 0.35
                }
            ]
        }
    },

    "experience": {

        "status": "partial",

        "required_years": 3,

        "candidate_years": 2.0
    },

    "education": {

        "status": "matched",

        "matched": [
            {
                "requirement": "computer science",
                "confidence": 0.85
            },
            {
                "requirement": "data science",
                "confidence": 0.85
            }
        ],

        "unknown": []
    },

    "projects": {

        "matched_skills": [
            "Python",
            "SQL",
            "Data Analysis"
        ],

        "unknown_skills": [
            "Machine Learning",
            "Pandas"
        ]
    }
}


# ============================================================
# TEST 1
# ============================================================

print("\n" + "=" * 60)
print("TEST 1: SKILL SCORE")
print("=" * 60)

score = calculate_skill_score(
    match_result["skills"]["required"]
)

print(
    "Skill score:",
    score
)


# ============================================================
# TEST 2
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: EXPERIENCE SCORE")
print("=" * 60)

score = calculate_experience_score(
    match_result["experience"]
)

print(
    "Experience score:",
    score
)


# ============================================================
# TEST 3
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: EDUCATION SCORE")
print("=" * 60)

score = calculate_education_score(
    match_result["education"]
)

print(
    "Education score:",
    score
)


# ============================================================
# TEST 4
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: PROJECT SCORE")
print("=" * 60)

score = calculate_project_score(
    match_result["projects"]
)

print(
    "Project score:",
    score
)


# ============================================================
# TEST 5
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: PREFERRED SKILL SCORE")
print("=" * 60)

score = calculate_preferred_score(
    match_result["skills"]["preferred"]
)

print(
    "Preferred score:",
    score
)


# ============================================================
# TEST 6
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: FINAL ATS SCORE")
print("=" * 60)

result = calculate_ats_score(
    match_result
)

print(
    result
)


# ============================================================
# TEST 7
# ============================================================

print("\n" + "=" * 60)
print("TEST 7: MATCHED REQUIREMENTS")
print("=" * 60)

matched = extract_matched_requirements(
    match_result
)

print(
    matched
)


# ============================================================
# TEST 8
# ============================================================

print("\n" + "=" * 60)
print("TEST 8: MISSING REQUIREMENTS")
print("=" * 60)

missing = extract_missing_requirements(
    match_result
)

print(
    missing
)


# ============================================================
# TEST 9
# ============================================================

print("\n" + "=" * 60)
print("TEST 9: SCORE SUMMARY")
print("=" * 60)

summary = generate_score_summary(
    match_result
)

print(
    summary
)


# ============================================================
# TEST 10
# ============================================================

print("\n" + "=" * 60)
print("TEST 10: EMPTY MATCH RESULT")
print("=" * 60)

empty_result = calculate_ats_score(
    {}
)

print(
    empty_result
)


# ============================================================
# TEST 11
# ============================================================

print("\n" + "=" * 60)
print("TEST 11: NO EXPERIENCE REQUIREMENT")
print("=" * 60)

result = calculate_experience_score(
    {
        "status": "not_required",
        "required_years": None,
        "candidate_years": None
    }
)

print(
    "Experience score:",
    result
)


# ============================================================
# TEST 12
# ============================================================

print("\n" + "=" * 60)
print("TEST 12: COMPLETE ATS ANALYSIS")
print("=" * 60)

summary = generate_score_summary(
    match_result
)

print(
    "ATS SCORE:",
    summary["ats_score"]
)

print(
    "CLASSIFICATION:",
    summary["classification"]
)

print(
    "BREAKDOWN:",
    summary["breakdown"]
)

print(
    "MATCHED:",
    summary["matched_requirements"]
)

print(
    "MISSING:",
    summary["missing_requirements"]
)


print("\n")
print("=" * 60)
print("ATS SCORING ENGINE TEST FINISHED")
print("=" * 60)