from app.matcher.experience_matcher import (
    calculate_total_experience,
    calculate_experience_details,
    match_experience,
)


# ============================================================
# TEST DATA
# ============================================================

resume = {
    "experience": [
        {
            "job_title": "Associate AI Engineer",
            "company": "Novum Labs",
            "location": "Hyderabad",
            "dates": {
                "start": "03/2025",
                "end": "Present",
                "current": True,
            },
            "description": (
                "Developed AI-powered applications using "
                "Python, FastAPI, LLM integration and NLP."
            ),
        }
    ]
}


required_experience = {
    "minimum_years": 3
}


# ============================================================
# TEST HEADER
# ============================================================

print("=" * 70)
print("EXPERIENCE MATCHER TEST")
print("=" * 70)


# ============================================================
# TEST 1 — TOTAL EXPERIENCE
# ============================================================

experiences = resume["experience"]

candidate_years = calculate_total_experience(
    experiences
)

print("\n" + "-" * 70)
print("TEST 1: TOTAL EXPERIENCE")
print("-" * 70)

print(
    "Candidate experience:",
    candidate_years,
    "years"
)


assert candidate_years is not None, (
    "Candidate experience should not be None"
)

assert candidate_years > 0, (
    "Candidate experience should be greater than 0"
)


# ============================================================
# TEST 2 — INDIVIDUAL EXPERIENCE DETAILS
# ============================================================

experience_details = calculate_experience_details(
    experiences
)

print("\n" + "-" * 70)
print("TEST 2: INDIVIDUAL EXPERIENCE DETAILS")
print("-" * 70)

print(
    "Number of experience entries:",
    len(experience_details)
)


assert len(experience_details) == 1, (
    "Expected exactly one experience detail"
)


detail = experience_details[0]

print("\nJob title:")
print(detail["job_title"])

print("\nCompany:")
print(detail["company"])

print("\nStart:")
print(detail["start"])

print("\nEnd:")
print(detail["end"])

print("\nCurrent:")
print(detail["current"])

print("\nDuration months:")
print(detail["duration_months"])

print("\nDuration years:")
print(detail["duration_years"])


# ------------------------------------------------------------
# Validate individual duration
# ------------------------------------------------------------

assert detail["duration_months"] > 0, (
    "Duration months should be greater than 0"
)

assert detail["duration_years"] > 0, (
    "Duration years should be greater than 0"
)

assert detail["current"] is True, (
    "Current role should have current=True"
)


# ============================================================
# TEST 3 — MATCH EXPERIENCE
# ============================================================

result = match_experience(
    resume,
    required_experience
)

print("\n" + "-" * 70)
print("TEST 3: MATCH EXPERIENCE")
print("-" * 70)

print("\nStatus:")
print(result["status"])

print("\nRequired years:")
print(result["required_years"])

print("\nCandidate years:")
print(result["candidate_years"])

print("\nExperience details:")
print(result["experience_details"])


# ------------------------------------------------------------
# Validate match result
# ------------------------------------------------------------

assert result["status"] == "partial", (
    "Candidate should be partial for a 3-year requirement"
)

assert result["required_years"] == 3, (
    "Required years should be 3"
)

assert result["candidate_years"] is not None, (
    "Candidate years should not be None"
)

assert result["experience_details"], (
    "Experience details should not be empty"
)


# ============================================================
# TEST 4 — VERIFY DURATION IS AVAILABLE THROUGH MATCHER
# ============================================================

matched_detail = result["experience_details"][0]

print("\n" + "-" * 70)
print("TEST 4: VERIFY ROLE DURATION")
print("-" * 70)

print(
    "Role:",
    matched_detail["job_title"]
)

print(
    "Duration:",
    matched_detail["duration_years"],
    "years"
)

print(
    "Duration:",
    matched_detail["duration_months"],
    "months"
)


assert matched_detail.get("duration_years") is not None, (
    "duration_years must NOT be None"
)

assert matched_detail.get("duration_years") > 0, (
    "duration_years must be greater than 0"
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("EXPERIENCE MATCHER TEST PASSED")
print("=" * 70)