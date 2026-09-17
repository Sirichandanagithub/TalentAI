from app.parser.job_description_parser import (
    parse_job_description
)


# ============================================================
# SAMPLE JOB DESCRIPTION
# ============================================================

job_description = """
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
# PARSE JOB DESCRIPTION
# ============================================================

print("=" * 60)
print("JOB DESCRIPTION PARSER TEST")
print("=" * 60)

result = parse_job_description(
    job_description
)


# ============================================================
# RAW TEXT
# ============================================================

print("\n## RAW TEXT")

print(
    result["raw_text"]
)


# ============================================================
# JOB TITLE
# ============================================================

print("\n## JOB TITLE")

print(
    result["job_title"]
)


# ============================================================
# REQUIRED SKILLS
# ============================================================

print("\n## REQUIRED SKILLS")

for index, skill in enumerate(
    result["required_skills"],
    start=1
):

    print(
        f"[{index}] {skill}"
    )


# ============================================================
# PREFERRED SKILLS
# ============================================================

print("\n## PREFERRED SKILLS")

for index, skill in enumerate(
    result["preferred_skills"],
    start=1
):

    print(
        f"[{index}] {skill}"
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

for index, education in enumerate(
    result["education"],
    start=1
):

    print(
        f"[{index}] {education}"
    )


# ============================================================
# COMPLETE RESULT
# ============================================================

print("\n## COMPLETE RESULT")

print(result)


print("\n")
print("=" * 60)
print("JOB DESCRIPTION PARSER TEST FINISHED")
print("=" * 60)