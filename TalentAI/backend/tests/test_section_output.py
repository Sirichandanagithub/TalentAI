from app.parser.section_detector import extract_sections


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
"""


print("=" * 60)
print("TESTING extract_sections()")
print("=" * 60)

sections = extract_sections(resume_text)

print("\nTYPE:")
print(type(sections))

print("\nRAW RESULT:")
print(sections)

print("\n" + "=" * 60)
print("SECTIONS")
print("=" * 60)

if isinstance(sections, dict):

    for section_name, section_text in sections.items():

        print(f"\n[{section_name.upper()}]")
        print("-" * 40)
        print(section_text)

else:

    print("Returned value is not a dictionary.")
    print("We need to inspect its structure before connecting the master parser.")