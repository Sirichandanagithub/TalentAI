from app.parser.section_detector import extract_sections
from app.parser.master_parser import parse_resume


# ============================================================
# SAMPLE RESUME
# ============================================================

resume_text = """
BOKKA SRIKANTH REDDY
Phone: +917382020763 | Email | LinkedIn | Github
Hyderabad,Telangana,India,500070

To obtain a creative and challenging position in an organization that gives me an opportunity for self improvement while contributing to the symbolic growth of the organization with my technical, innovative and

EDUCATION

Vignan Institute of Technology and Science,Hyderabad
2022-2026 CSE_AI&DS

Narayana Junior College,Hyderabad
CGPA8.0
2020-2022 ,Intermediate

Santhi Nikethan Educational Institutions,Hyderabad
CGPA8.69
SSC BOARD
CGPA-10.

EXPERIENCE

Data Analytics Intern
Renu Sharma Healthcare and Education Foundation – Remote
[ April 2025 ]

As a Data Analytics Intern at Renu Sharma Healthcare and Education Foundation,
I was selected through a competitive interview process. In this fully remote role,
I worked closely with the team on data analytics activities.

PROJECTS

JOB TRACKER APP

Job Tracker App is a web application that helps users manage and track
their job applications. Users can add job details, update the status
(like Applied, Interview, Offer, Rejected), and view all entries in a
dashboard. The app supports editing, deleting, and filtering applications.

Technologies: Python, JavaScript, HTML, CSS, MySQL

SKILLS

Programming Languages:
Python, JavaScript

Databases:
MySQL, MongoDB, NoSQL

Data Science:
Data Visualization (Tableau, Power BI), Data Preprocessing,
Data Analysis, Statistical Analysis

Machine Learning:
Classification, Regression, Time-Series Analysis,
Deep Learning, Data Processing

Others:
Git, Docker

CERTIFICATIONS

FRONTEND WITH HTML AND CSS
TASK - Designed and developed a visually appealing static website
using HTML, CSS, and best practices
2024

PROBLEM SOLVING THROUGH PROGRAMMING IN C
NPTEL Online exam Qualified
2023

Data Engineering with Hadoop and Spark
GeeksforGeeks

ACHIEVEMENTS

NSS CO-ORDINATOR (National Service Scheme)
Coordinated National Service Scheme (NSS) activities, promoting community service and social responsibility.
Led team of volunteers in organizing events, camps, and projects, fostering teamwork and leadership skills.

CSI CO-ORDINATOR (Computer Society)
Coordinated Computer Society activities.
Organized technical events and encouraged student participation.

LANGUAGES

English
Hindi
Telugu
"""


# ============================================================
# STEP 1: SECTION DETECTION
# ============================================================

print("=" * 60)
print("STEP 1: SECTION DETECTION")
print("=" * 60)


sections = extract_sections(
    resume_text
)


# ============================================================
# RAW EXTRACTED SECTIONS
# ============================================================

print("\n" + "=" * 60)
print("RAW EXTRACTED SECTIONS")
print("=" * 60)


for section_name, section_text in sections.items():

    print("\n" + "-" * 60)
    print(f"SECTION: {section_name}")
    print("-" * 60)

    print(section_text)


# ============================================================
# DETECTED SECTION NAMES
# ============================================================

print("\nDetected sections:")

for section_name in sections:

    print(
        f" - {section_name}"
    )


# ============================================================
# STEP 2: MASTER PARSER
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: MASTER PARSER")
print("=" * 60)


result = parse_resume(
    sections
)


# ============================================================
# PERSONAL
# ============================================================

print("\n## PERSONAL")

print(
    result["personal"]
)


# ============================================================
# SUMMARY
# ============================================================

print("\n## SUMMARY")

print(
    result["summary"]
)


# ============================================================
# EDUCATION
# ============================================================

print("\n## EDUCATION")


for index, education in enumerate(
    result["education"],
    start=1
):

    print(f"\n[{index}]")

    print(
        education
    )


# ============================================================
# EXPERIENCE
# ============================================================

print("\n## EXPERIENCE")


for index, experience in enumerate(
    result["experience"],
    start=1
):

    print(f"\n[{index}]")

    print(
        experience
    )


# ============================================================
# PROJECTS
# ============================================================

print("\n## PROJECTS")


for index, project in enumerate(
    result["projects"],
    start=1
):

    print(f"\n[{index}]")

    print(
        project
    )


# ============================================================
# SKILLS
# ============================================================

print("\n## SKILLS")

print(
    result["skills"]
)


# ============================================================
# CERTIFICATIONS
# ============================================================

print("\n## CERTIFICATIONS")


for index, certification in enumerate(
    result["certifications"],
    start=1
):

    print(f"\n[{index}]")

    print(
        certification
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

print("\n## ACHIEVEMENTS")


for index, achievement in enumerate(
    result["achievements"],
    start=1
):

    print(f"\n[{index}]")

    print(
        achievement
    )


# ============================================================
# LANGUAGES
# ============================================================

print("\n## LANGUAGES")


for index, language in enumerate(
    result["languages"],
    start=1
):

    print(f"\n[{index}]")

    print(
        language
    )


# ============================================================
# TEST FINISHED
# ============================================================

print("\n")

print("=" * 60)

print(
    "MASTER PARSER TEST FINISHED"
)

print("=" * 60)