from app.utils.pdf import extract_text_from_pdf

from app.parser.section_detector import extract_sections

from app.parser.personal_parser import parse_personal


pdf_path = (
    r"C:\practice_vscode\TalentAI\backend"
    r"\uploads\resumes"
    r"\Srikanth Reddy Resume 2026 01.pdf"
)

resume_text = extract_text_from_pdf(pdf_path)

sections = extract_sections(resume_text)

result = parse_personal(
    sections["personal"]
)

print("=" * 60)
print("PERSONAL DETAILS")
print("=" * 60)

for key, value in result.items():
    print(f"{key:12}: {value}")