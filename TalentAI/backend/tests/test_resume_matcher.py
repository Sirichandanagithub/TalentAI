from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume
from app.parser.job_description_parser import parse_job_description
from app.matcher.resume_matcher import match_resume_to_job


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
[ April 2025 ]

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
# PARSE RESUME
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
# PARSE JOB DESCRIPTION
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: PARSE JOB DESCRIPTION")
print("=" * 60)

job_description = parse_job_description(
    job_description_text
)

print(job_description)


# ============================================================
# MATCH RESUME WITH JOB
# ============================================================

print("\n" + "=" * 60)
print("STEP 3: MATCH RESUME WITH JOB")
print("=" * 60)

result = match_resume_to_job(
    resume,
    job_description
)


# ============================================================
# JOB TITLE
# ============================================================

print("\n## JOB TITLE")

print(
    result["job_title"]
)


# ============================================================
# RESUME SKILLS
# ============================================================

print("\n## RESUME SKILLS")

for skill in result["resume_skills"]:

    print(
        f"- {skill}"
    )


# ============================================================
# REQUIRED SKILLS
# ============================================================

print("\n## REQUIRED SKILLS")

print(
    "Matched:"
)

for skill in result["skills"]["required"]["matched"]:

    print(
        f"  ✅ {skill}"
    )

print(
    "Unknown:"
)

for skill in result["skills"]["required"]["unknown"]:

    print(
        f"  ❓ {skill}"
    )

print(
    "Missing:"
)

for skill in result["skills"]["required"]["missing"]:

    print(
        f"  ❌ {skill}"
    )


# ============================================================
# PREFERRED SKILLS
# ============================================================

print("\n## PREFERRED SKILLS")

print(
    "Matched:"
)

for skill in result["skills"]["preferred"]["matched"]:

    print(
        f"  ✅ {skill}"
    )

print(
    "Unknown:"
)

for skill in result["skills"]["preferred"]["unknown"]:

    print(
        f"  ❓ {skill}"
    )


# ============================================================
# EXPERIENCE
# ============================================================

print("\n## EXPERIENCE")

print(
    result["experience"]
)


# ============================================================
# EDUCATION
# ============================================================

print("\n## EDUCATION")

print(
    result["education"]
)


# ============================================================
# PROJECTS
# ============================================================

print("\n## PROJECT MATCH")

print(
    result["projects"]
)


# ============================================================
# COMPLETE RESULT
# ============================================================

print("\n## COMPLETE MATCH RESULT")

print(result)


print("\n")
print("=" * 60)
print("RESUME MATCHER TEST FINISHED")
print("=" * 60)