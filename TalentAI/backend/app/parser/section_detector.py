import json
from pathlib import Path


DATA_DIR = (
    Path(__file__).resolve().parent.parent / "data"
)

SECTION_HEADERS_FILE = DATA_DIR / "section_headers.json"


def load_section_headers():
    """
    Load supported section headers.
    """

    with open(
        SECTION_HEADERS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)

def find_section_headers(text: str):
    """
    Detect all section headers and return their positions.

    Duplicate section headers are ignored so that the same
    section does not overwrite itself during extraction.
    """

    headers = load_section_headers()

    lines = text.splitlines()

    found = []
    seen_sections = set()

    for index, line in enumerate(lines):

        clean = line.strip().lower()

        if not clean:
            continue

        for section, aliases in headers.items():

            aliases = [a.lower() for a in aliases]

            if clean in aliases:

                # Ignore duplicate section headers
                if section in seen_sections:
                    continue

                found.append(
                    {
                        "section": section,
                        "line": index,
                    }
                )

                seen_sections.add(section)

                break

    return sorted(
        found,
        key=lambda x: x["line"],
    )

def extract_sections(text: str):
    """
    Split the resume into sections.
    """

    headers = find_section_headers(text)

    lines = text.splitlines()

    sections = {}

    # Personal information (before first header)
    if headers:

        sections["personal"] = "\n".join(
            lines[: headers[0]["line"]]
        ).strip()

    else:

        sections["personal"] = text.strip()

        return sections

    # Extract every section
    for i in range(len(headers)):

        current = headers[i]

        start = current["line"] + 1

        if i + 1 < len(headers):

            end = headers[i + 1]["line"]

        else:

            end = len(lines)

        content = "\n".join(
            lines[start:end]
        ).strip()

        sections[current["section"]] = content

    return sections
    