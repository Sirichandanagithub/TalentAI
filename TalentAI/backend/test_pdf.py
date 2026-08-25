from app.utils.pdf import extract_text_from_pdf

pdf_path = r"C:\practice_vscode\TalentAI\backend\uploads\resumes\Srikanth Reddy Resume 2026 01.pdf"

text = extract_text_from_pdf(pdf_path)

print("=" * 50)
print("Extracted Text:")
print("=" * 50)
print(text)

#C:\practice_vscode\TalentAI\backend\uploads\resumes\Srikanth Reddy Resume 2026 01.pdf