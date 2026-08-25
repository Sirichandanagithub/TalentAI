from app.parser.certification_parser import parse_certifications


print("TEST FILE STARTED")


certification_text = """
FRONTEND WITH HTML AND CSS
➢ TASK - Designed and developed a visually appealing static website using HTML, CSS, and best practices
2024

PROBLEM SOLVING THROUGH PROGRAMMING IN C
➢ NPTEL Online exam Qualified
2023

Data Engineering with Hadoop and Spark
GeeksforGeeks
"""


print("PARSING STARTED")


result = parse_certifications(certification_text)


print("=" * 60)
print("CERTIFICATIONS")
print("=" * 60)

print("RESULT:", result)


for index, certification in enumerate(result, start=1):

    print(f"\n[{index}]")

    print(
        "Certification Name :",
        certification["certification_name"]
    )

    print(
        "Issuer             :",
        certification["issuer"]
    )

    print(
        "Date               :",
        certification["date"]
    )

    print(
        "Description        :",
        certification["description"]
    )


print("TEST FILE FINISHED")