from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume
from app.parser.job_description_parser import parse_job_description
from app.matcher.resume_matcher import match_resume_to_job
from app.scoring.ats_scorer import calculate_ats_score


# ============================================================
# SAMPLE RESUME
# ============================================================

resume_text = """
BOKKA SRIKANTH REDDY

EDUCATION

Vignan Institute of Technology and Science, Hyderabad
2022-2026 CSE_AI&DS

EXPERIENCE

Data Analytics Intern
Renu Sharma Healthcare and Education Foundation – Remote
April 2025

PROJECTS

JOB TRACKER APP

Job Tracker App is a web application that helps users manage
and track their job applications.

Technologies: Python, JavaScript, HTML, CSS, MySQL

SKILLS

Programming Languages:
Python, JavaScript

Databases:
MySQL, MongoDB, NoSQL

Data Science:
Data Analysis, Statistical Analysis

Machine Learning:
Classification, Regression, Deep Learning

Others:
Git, Docker

LANGUAGES

English
Hindi
Telugu
"""


# ============================================================
# SAMPLE JOB DESCRIPTION
# ============================================================

job_description_text = """
Data Scientist

We are looking for a Data Scientist with 3+ years of experience
in Python, SQL and Machine Learning.

The candidate should have experience with Pandas,
Scikit-learn and Data Analysis.

Experience with AWS and TensorFlow is preferred.

Bachelor's degree in Computer Science, Data Science,
Artificial Intelligence or a related field is required.
"""


# ============================================================
# STEP 1: PARSE RESUME
# ============================================================

print("=" * 60)
print("STEP 1: PARSE RESUME")
print("=" * 60)

sections = extract_sections(
    resume_text
)

resume = parse_resume(
    sections
)


# ============================================================
# STEP 2: PARSE JOB DESCRIPTION
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: PARSE JOB DESCRIPTION")
print("=" * 60)

job_description = parse_job_description(
    job_description_text
)

print(job_description)


# ============================================================
# STEP 3: MATCH
# ============================================================

print("\n" + "=" * 60)
print("STEP 3: MATCH RESUME WITH JOB")
print("=" * 60)

match_result = match_resume_to_job(
    resume,
    job_description
)

print(match_result)


# ============================================================
# STEP 4: ATS SCORE
# ============================================================

print("\n" + "=" * 60)
print("STEP 4: CALCULATE ATS SCORE")
print("=" * 60)

ats_result = calculate_ats_score(
    match_result
)


# ============================================================
# FINAL SCORE
# ============================================================

print("\n" + "=" * 60)
print("FINAL ATS SCORE")
print("=" * 60)

print(
    f"\nATS SCORE: "
    f"{ats_result['ats_score']}/100"
)


# ============================================================
# SCORE BREAKDOWN
# ============================================================

print("\n" + "=" * 60)
print("SCORE BREAKDOWN")
print("=" * 60)

breakdown = ats_result[
    "breakdown"
]


print("\nRequired Skills")
print(
    f"Percentage : "
    f"{breakdown['required_skills']['percentage']}%"
)

print(
    f"Weighted   : "
    f"{breakdown['required_skills']['weighted_score']}"
)


print("\nPreferred Skills")
print(
    f"Percentage : "
    f"{breakdown['preferred_skills']['percentage']}%"
)

print(
    f"Weighted   : "
    f"{breakdown['preferred_skills']['weighted_score']}"
)


print("\nExperience")
print(
    f"Status     : "
    f"{breakdown['experience']['status']}"
)

print(
    f"Percentage : "
    f"{breakdown['experience']['percentage']}%"
)

print(
    f"Weighted   : "
    f"{breakdown['experience']['weighted_score']}"
)


print("\nEducation")
print(
    f"Status     : "
    f"{breakdown['education']['status']}"
)

print(
    f"Percentage : "
    f"{breakdown['education']['percentage']}%"
)

print(
    f"Weighted   : "
    f"{breakdown['education']['weighted_score']}"
)


print("\nProjects")
print(
    f"Percentage : "
    f"{breakdown['projects']['percentage']}%"
)

print(
    f"Weighted   : "
    f"{breakdown['projects']['weighted_score']}"
)


print("\n" + "=" * 60)
print("ATS SCORER TEST FINISHED")
print("=" * 60)