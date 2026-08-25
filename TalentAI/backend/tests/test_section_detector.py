from app.utils.pdf import extract_text_from_pdf
from app.parser.section_detector import (
    find_section_headers,
    extract_sections,
)

pdf_path = (
    r"C:\practice_vscode\TalentAI\backend\uploads\resumes"
    r"\Srikanth Reddy Resume 2026 01.pdf"
)

resume_text = extract_text_from_pdf(pdf_path)

print("=" * 60)
print("HEADERS")
print("=" * 60)

headers = find_section_headers(resume_text)

for item in headers:
    print(item)

print()

print("=" * 60)
print("SECTIONS")
print("=" * 60)

sections = extract_sections(resume_text)

for name, value in sections.items():

    print()

    print(f"[{name.upper()}]")

    print("-" * 40)

    print(value[:300])