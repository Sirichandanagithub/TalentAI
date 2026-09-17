from pprint import pprint

from app.ai.analyzer.talent_match_engine import (
    TalentMatchEngine
)


# ============================================================
# TEST HEADER
# ============================================================

print("=" * 60)
print("TALENTAI END-TO-END MATCH ENGINE TEST")
print("=" * 60)


# ============================================================
# SAMPLE RESUME
# ============================================================

resume = {

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
        "CSS"
    ],

    "experience": [],

    "education": [],

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
        }
    ],

    "certifications": [],

    "summary":
        "Data professional with experience in Python "
        "and machine learning."
}


# ============================================================
# SAMPLE JOB
# ============================================================

job = {

    "job_title":
        "Data Scientist",

    "required_skills": [
        "Python",
        "SQL",
        "Machine Learning",
        "Pandas",
        "Scikit-learn",
        "Data Analysis",
        "Artificial Intelligence"
    ],

    "preferred_skills": [
        "TensorFlow",
        "AWS"
    ],

    "experience": {
        "minimum_years": 3
    },

    "education": [
        "computer science",
        "data science",
        "artificial intelligence"
    ]
}


# ============================================================
# INITIALIZE
# ============================================================

engine = TalentMatchEngine()


# ============================================================
# TEST 1
# ============================================================

print("\n" + "=" * 60)
print("TEST 1: PYTHON")
print("=" * 60)

result = engine.analyze_requirement(
    "Python",
    resume["skills"]
)

pprint(result)


# ============================================================
# TEST 2
# ============================================================

print("\n" + "=" * 60)
print("TEST 2: SQL")
print("=" * 60)

result = engine.analyze_requirement(
    "SQL",
    resume["skills"]
)

pprint(result)


# ============================================================
# TEST 3
# ============================================================

print("\n" + "=" * 60)
print("TEST 3: MACHINE LEARNING")
print("=" * 60)

result = engine.analyze_requirement(
    "Machine Learning",
    resume["skills"]
)

pprint(result)


# ============================================================
# TEST 4
# ============================================================

print("\n" + "=" * 60)
print("TEST 4: PANDAS")
print("=" * 60)

result = engine.analyze_requirement(
    "Pandas",
    resume["skills"]
)

pprint(result)


# ============================================================
# TEST 5
# ============================================================

print("\n" + "=" * 60)
print("TEST 5: AWS")
print("=" * 60)

result = engine.analyze_requirement(
    "AWS",
    resume["skills"]
)

pprint(result)


# ============================================================
# TEST 6
# ============================================================

print("\n" + "=" * 60)
print("TEST 6: REQUIRED SKILLS")
print("=" * 60)

result = engine.analyze_required_skills(
    job["required_skills"],
    resume["skills"],
    resume
)

pprint(result)


# ============================================================
# TEST 7
# ============================================================

print("\n" + "=" * 60)
print("TEST 7: PREFERRED SKILLS")
print("=" * 60)

result = engine.analyze_preferred_skills(
    job["preferred_skills"],
    resume["skills"],
    resume
)

pprint(result)


# ============================================================
# TEST 8
# ============================================================

print("\n" + "=" * 60)
print("TEST 8: BUILD MATCH RESULT")
print("=" * 60)

result = engine.build_match_result(
    resume,
    job
)

pprint(result)


# ============================================================
# TEST 9
# ============================================================

print("\n" + "=" * 60)
print("TEST 9: FINAL TALENTAI ANALYSIS")
print("=" * 60)

result = engine.analyze(
    resume,
    job
)

pprint(result)


# ============================================================
# TEST 10
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("TEST 10: FINAL SUMMARY")
print("=" * 60)


print(
    "Job:",
    result.get("job_title")
)

print(
    "ATS Score:",
    result.get("ats_score")
)

print(
    "Classification:",
    result.get("classification")
)

print(
    "Score Breakdown:",
    result.get("score_breakdown")
)


# ============================================================
# MATCH RESULT
# ============================================================

match_result = result.get(
    "match",
    {}
)

skills_result = match_result.get(
    "skills",
    {}
)

required_result = skills_result.get(
    "required",
    {}
)


print(
    "Matched:",
    required_result.get(
        "matched",
        []
    )
)

print(
    "Possible:",
    required_result.get(
        "possible",
        []
    )
)

print(
    "Missing:",
    required_result.get(
        "unknown",
        []
    )
)


# ============================================================
# SKILL-SPECIFIC EXPERIENCE
# ============================================================

print("\n" + "-" * 60)
print("SKILL-SPECIFIC EXPERIENCE")
print("-" * 60)

skill_experience = match_result.get(
    "skill_experience",
    {}
)

print(
    "Matched Skills:",
    skill_experience.get(
        "matched",
        []
    )
)

print(
    "Possible Skills:",
    skill_experience.get(
        "possible",
        []
    )
)

print(
    "Unknown Skills:",
    skill_experience.get(
        "unknown",
        []
    )
)


# ============================================================
# EXPERIENCE
# ============================================================

print("\n" + "-" * 60)
print("EXPERIENCE")
print("-" * 60)

experience_result = match_result.get(
    "experience",
    {}
)

print(
    "Status:",
    experience_result.get(
        "status"
    )
)

print(
    "Required Years:",
    experience_result.get(
        "required_years"
    )
)

print(
    "Candidate Years:",
    experience_result.get(
        "candidate_years"
    )
)


# ============================================================
# EDUCATION
# ============================================================

print("\n" + "-" * 60)
print("EDUCATION")
print("-" * 60)

print(
    match_result.get(
        "education",
        {}
    )
)


# ============================================================
# PROJECTS
# ============================================================

print("\n" + "-" * 60)
print("PROJECTS")
print("-" * 60)

print(
    match_result.get(
        "projects",
        {}
    )
)


# ============================================================
# CONTEXT
# ============================================================

print("\n" + "-" * 60)
print("CONTEXT")
print("-" * 60)

print(
    result.get(
        "context",
        {}
    )
)


# ============================================================
# EVIDENCE
# ============================================================

print("\n" + "-" * 60)
print("EVIDENCE")
print("-" * 60)

print(
    result.get(
        "evidence",
        {}
    )
)


# ============================================================
# DECISION
# ============================================================

print("\n" + "-" * 60)
print("DECISION")
print("-" * 60)

print(
    result.get(
        "decision",
        {}
    )
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)


assert isinstance(
    result,
    dict
)

assert result.get(
    "job_title"
) == "Data Scientist"

assert "ats_score" in result

assert "classification" in result

assert "score_breakdown" in result

assert "match" in result

assert "context" in result

assert "evidence" in result

assert "decision" in result


# ------------------------------------------------------------
# Validate match result
# ------------------------------------------------------------

assert isinstance(
    match_result,
    dict
)

assert "skills" in match_result

assert "experience" in match_result

assert "education" in match_result

assert "projects" in match_result


# ------------------------------------------------------------
# Validate skill-specific experience
# ------------------------------------------------------------

assert "skill_experience" in match_result

assert isinstance(
    skill_experience,
    dict
)

assert "skills" in skill_experience

assert "matched" in skill_experience

assert "possible" in skill_experience

assert "unknown" in skill_experience


# ------------------------------------------------------------
# Validate required skills
# ------------------------------------------------------------

assert "required" in skills_result

assert "matched" in required_result

assert "possible" in required_result

assert "unknown" in required_result


# ------------------------------------------------------------
# Validate ATS score
# ------------------------------------------------------------

ats_score = result.get(
    "ats_score"
)

assert isinstance(
    ats_score,
    (int, float)
)

assert 0 <= ats_score <= 100


print("✅ Final result structure is valid.")

print(
    "✅ Job title detected:",
    result["job_title"]
)

print(
    "✅ ATS score:",
    result["ats_score"]
)

print(
    "✅ Classification:",
    result["classification"]
)

print(
    "✅ Skill-specific experience layer connected."
)

print(
    "✅ Context layer connected."
)

print(
    "✅ Evidence layer connected."
)

print(
    "✅ Decision layer connected."
)


# ============================================================
# FINISHED
# ============================================================

print("\n")

print("=" * 60)

print(
    "TALENTAI MATCH ENGINE TEST PASSED"
)

print("=" * 60)