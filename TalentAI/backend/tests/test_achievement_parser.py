from app.parser.achievement_parser import parse_achievements


achievement_text = """
NSS CO-ORDINATOR (National service scheme)
➢ Coordinated National Service Scheme (NSS) activities, promoting community service and social responsibility.
➢ Led team of volunteers in organizing events, camps, and projects, fostering teamwork and leadership skills.

CSI CO-ORDINATOR (Computer Society)
➢ Coordinated Computer Society activities.
➢ Organized technical events and encouraged student participation.
"""


result = parse_achievements(achievement_text)


print()
print("# ACHIEVEMENTS")
print()

print("RESULT:", result)

print()

print(
    "Number of achievements:",
    len(result)
)

for index, achievement in enumerate(result, start=1):

    print()
    print(f"[{index}]")

    print(
        "Achievement Name :",
        achievement["achievement_name"]
    )

    print(
        "Description      :",
        achievement["description"]
    )

print()
print("TEST FILE FINISHED")