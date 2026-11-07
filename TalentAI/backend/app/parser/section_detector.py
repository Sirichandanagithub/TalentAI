
import json
import re
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SECTION_HEADERS_FILE = DATA_DIR / "section_headers.json"


def load_section_headers():
    with open(SECTION_HEADERS_FILE, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def normalize_header(text: str) -> str:
    """
    Normalize section headings for reliable matching.
    """
    if not text:
        return ""

    text = text.strip().lower()

    # Remove PDF bullets and decorative symbols.
    text = re.sub(r"^[\W_]+", "", text, flags=re.UNICODE)

    # Remove trailing punctuation and bullets.
    text = re.sub(r"[\W_]+$", "", text, flags=re.UNICODE)

    # Normalize internal whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def find_section_headers(text: str):
    if not text:
        return []

    headers = load_section_headers()

    # Normalize aliases once.
    normalized_headers = {
        section: {
            normalize_header(alias)
            for alias in aliases
        }
        for section, aliases in headers.items()
    }

    found = []

    for index, line in enumerate(text.splitlines()):

        clean = normalize_header(line)

        if not clean:
            continue

        for section, aliases in normalized_headers.items():

            if clean in aliases:
                found.append({
                    "section": section,
                    "line": index,
                })
                break

    return sorted(found, key=lambda item: item["line"])


def extract_sections(text: str):
    if not text:
        return {"personal": ""}

    headers = find_section_headers(text)
    lines = text.splitlines()

    sections = {}

    if not headers:
        return {
            "personal": text.strip()
        }

    sections["personal"] = "\n".join(
        lines[:headers[0]["line"]]
    ).strip()

    # Preserve content from repeated sections.
    for index, current in enumerate(headers):

        start = current["line"] + 1

        if index + 1 < len(headers):
            end = headers[index + 1]["line"]
        else:
            end = len(lines)

        content = "\n".join(lines[start:end]).strip()

        section_name = current["section"]

        if section_name in sections and content:
            sections[section_name] += "\n" + content

        else:
            sections.setdefault(section_name, content)

    return sections
