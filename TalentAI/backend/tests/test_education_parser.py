from app.utils.pdf import extract_text_from_pdf

from app.parser.section_detector import extract_sections

from app.parser.education_parser import parse_education


pdf_path = (
    r"C:\practice_vscode\TalentAI\backend"
    r"\uploads\resumes"
    r"\Srikanth Reddy Resume 2026 01.pdf"
)


resume_text = extract_text_from_pdf(pdf_path)

sections = extract_sections(resume_text)

education_text = sections.get("education")

result = parse_education(education_text)


print("=" * 60)
print("EDUCATION")
print("=" * 60)

for index, entry in enumerate(result, start=1):

    print(f"\n[{index}]")
    print(entry)