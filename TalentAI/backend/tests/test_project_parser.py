from app.parser.project_parser import parse_projects


print("TEST FILE STARTED")


project_text = """
JOB TRACKER APP

Job Tracker App is a web application that helps users manage and track
their job applications. Users can add job details, update the status
(like Applied, Interview, Offer, Rejected), and view all entries in a
dashboard. The app supports editing, deleting, and filtering applications.

Technologies: Python, JavaScript, HTML, CSS, MySQL
"""


print("PARSING STARTED")


result = parse_projects(project_text)


print("=" * 60)
print("PROJECTS")
print("=" * 60)


print("RESULT:", result)


for index, project in enumerate(result, start=1):

    print(f"\n[{index}]")

    print("Project Name :", project["project_name"])
    print("Description  :", project["description"])
    print("Technologies :", project["technologies"])


print("TEST FILE FINISHED")