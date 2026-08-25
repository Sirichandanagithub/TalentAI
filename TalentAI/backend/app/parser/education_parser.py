import re


def clean_education_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def extract_education_section(text: str):

    if not text:
        return None

    text = clean_education_text(text)

    return text if text else None


def extract_education_entries(text: str):

    if not text:
        return []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    entries = []

    current_entry = []

    year_pattern = re.compile(
        r"\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}\b"
    )

    for line in lines:

        # -------------------------------------------------
        # CASE 1:
        # Institution name
        # followed by year/degree on next line
        # -------------------------------------------------

        if year_pattern.search(line):

            if current_entry:

                current_entry.append(line)

                entries.append(
                    " ".join(current_entry)
                )

                current_entry = []

            else:

                entries.append(line)

        else:

            current_entry.append(line)

    # -------------------------------------------------
    # Remaining lines
    # -------------------------------------------------

    if current_entry:

        remaining = " ".join(current_entry)

        if remaining.strip():

            entries.append(remaining)

    return entries


def extract_years(text: str):

    if not text:
        return None

    match = re.search(
        r"\b((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2})\b",
        text
    )

    if not match:
        return None

    return {
        "start_year": match.group(1),
        "end_year": match.group(2)
    }


def extract_grade(text: str):
    if not text:
        return None

    match = re.search(
        r"(?:CGPA|GPA)\s*[-:]?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if match:

        return {
            "type": "CGPA",
            "value": match.group(1)
        }

    return None

def extract_location(text: str):

    if not text:
        return None

    locations = [
        "Hyderabad",
        "Bangalore",
        "Bengaluru",
        "Chennai",
        "Mumbai",
        "Delhi",
        "Pune",
        "Kolkata",
        "Telangana",
        "Andhra Pradesh",
        "Maharashtra",
        "Karnataka"
    ]

    for location in locations:

        if re.search(
            rf"\b{re.escape(location)}\b",
            text,
            re.IGNORECASE
        ):
            return location

    return None


def extract_institution(text: str):

    if not text:
        return None

    cleaned = text

    # Remove year range
    cleaned = re.sub(
        r"\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}\b",
        "",
        cleaned
    )

    # Remove CGPA/GPA
    cleaned = re.sub(
        r"(?:CGPA|GPA)\s*[-:]?\s*\d+(?:\.\d+)?",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove program/degree
    cleaned = re.sub(
        r"\b(CSE[_\s-]*AI&DS|CSE|SSC\s*BOARD|Intermediate)\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove location
    locations = [
        "Hyderabad",
        "Bangalore",
        "Bengaluru",
        "Chennai",
        "Mumbai",
        "Delhi",
        "Pune",
        "Kolkata",
        "Telangana",
        "Andhra Pradesh",
        "Maharashtra",
        "Karnataka"
    ]

    for location in locations:

        cleaned = re.sub(
            rf",?\s*\b{re.escape(location)}\b",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

    # Clean remaining punctuation/spaces
    cleaned = re.sub(r"\s+", " ", cleaned)

    cleaned = cleaned.strip(" ,.-:")

    return cleaned if cleaned else None

def extract_program(text: str):

    if not text:
        return None

    program_patterns = [
        r"CSE[_\s-]*AI&DS",
        r"Intermediate",
        r"SSC\s*BOARD",
        r"\bCSE\b"
    ]

    for pattern in program_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0).strip()

    return None


def parse_education(text: str):

    section = extract_education_section(text)

    if not section:
        return []

    raw_entries = extract_education_entries(section)

    parsed_entries = []

    for entry in raw_entries:

        years = extract_years(entry)

        grade = extract_grade(entry)

        institution = extract_institution(entry)

        location = extract_location(entry)

        program = extract_program(entry)

        parsed_entries.append(
            {
                "raw_text": entry,
                "institution": institution,
                "location": location,
                "program": program,
                "years": years,
                "grade": grade
            }
        )

    return parsed_entries