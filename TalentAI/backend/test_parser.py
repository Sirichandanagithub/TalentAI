from app.utils.pdf import extract_text_from_pdf
#from app.parser.parser import parse_resume
from app.parser.education_parser import extract_education_section
from app.parser.section_detector import (
    find_section_headers,
    extract_education_section,

    

# Path to your uploaded resume
pdf_path = r"C:\practice_vscode\TalentAI\backend\uploads\resumes\Srikanth Reddy Resume 2026 01.pdf"

# Extract text
resume_text = extract_text_from_pdf(pdf_path)
print("=" * 50)
print("Detected Headers")
print("=" * 50)


headers = find_section_headers(resume_text)

print("=" * 50)
print("Detected Headers")
print("=" * 50)

for header in headers:
    print(header)

print()

print("=" * 50)
print("Extracted Sections")
print("=" * 50)

sections = extract_sections(resume_text)

for name, content in sections.items():

    print()

    print(f"[{name.upper()}]")

    print("-" * 30)

    print(content[:250])

print()

# Extract education section
education  = extract_education_section(resume_text)
print("=" * 50)
print("Education Section")
print("=" * 50)
print(education)

# Parse resume
#parsed_data = parse_resume(resume_text)

print("=" * 50)
#print("Parsed Resume")
print("=" * 50)
print(resume_text)

print(parsed_data)