from app.utils.pdf import extract_text_from_pdf

from app.parser.section_detector import extract_sections

from app.parser.summary_parser import parse_summary


pdf_path = (
    r"C:\practice_vscode\TalentAI\backend"
    r"\uploads\resumes"
    r"\Srikanth Reddy Resume 2026 01.pdf"
)


resume_text = extract_text_from_pdf(pdf_path)

sections = extract_sections(resume_text)


summary_text = sections.get("summary")


result = parse_summary(summary_text)


print("=" * 60)
print("SUMMARY")
print("=" * 60)

print(result)