from app.parser.experience_parser import (
    extract_experience_entries,
    parse_experience
)

print("=" * 60)
print("MULTIPLE EXPERIENCE TEST")
print("=" * 60)

experience_text = """
Data Analytics Intern
Renu Sharma Healthcare and Education Foundation – Remote
[ April 2025 ]

As a Data Analytics Intern at Renu Sharma Healthcare and Education Foundation,
I was selected through a competitive interview process. In this fully remote role,
I worked closely with the team on data analytics activities.

Research Intern – BDL (DRDL)
➢ Organization: Bharat Dynamics Limited – Defence Research and Development Laboratory (DRDL)
[ May 2026 ]

Gained exposure to defense tech systems and contributed to small-scale development tasks.
Learned secure system design principles and problem-solving in critical environment.
"""

print("\nRAW ENTRIES")
print("=" * 60)

entries = extract_experience_entries(
    experience_text
)

print("Number of entries:", len(entries))

for index, entry in enumerate(entries, start=1):

    print(f"\n[{index}]")
    print(entry)

print("\nPARSED EXPERIENCES")
print("=" * 60)

result = parse_experience(
    experience_text
)

print("Number of parsed experiences:", len(result))

for index, experience in enumerate(result, start=1):

    print(f"\n[{index}]")

    print(
        "Job Title :",
        experience["job_title"]
    )

    print(
        "Company   :",
        experience["company"]
    )

    print(
        "Location  :",
        experience["location"]
    )

    print(
        "Dates     :",
        experience["dates"]
    )

    print(
        "Description:",
        experience["description"]
    )

print("\n")
print("=" * 60)
print("MULTIPLE EXPERIENCE TEST FINISHED")
print("=" * 60)