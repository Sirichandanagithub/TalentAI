from app.parser.skill_parser import parse_skills


print("TEST FILE STARTED")


skill_text = """
Programming Languages
:
Python, JavaScript

Databases
:
MySQL, MongoDB, NoSQL

Data Science
:
Data Visualization (Tableau, Power BI), Data Preprocessing,
Data Analysis, Statistical Analysis

Machine Learning
:
Classification, Regression, Time-Series Analysis,
Deep Learning, Data Processing

Others
:
Git, Docker
"""


print("PARSING STARTED")


result = parse_skills(skill_text)


print("=" * 60)
print("SKILLS")
print("=" * 60)


print("RESULT:", result)


for category, skills in result.items():

    print(f"\n{category.upper()}")
    print("-" * 40)

    for skill in skills:
        print("-", skill)


print("TEST FILE FINISHED")