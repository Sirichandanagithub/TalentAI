
import fitz


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF.

    Returns:
        str: Extracted text.

    Raises:
        ValueError: If the PDF is invalid or cannot be opened.
    """

    try:
        with fitz.open(pdf_path) as document:
            text_parts = []

            for page in document:
                text_parts.append(page.get_text())

        return "\n".join(text_parts).strip()

    except Exception as exc:
        raise ValueError("Unable to read or process the PDF file.") from exc
