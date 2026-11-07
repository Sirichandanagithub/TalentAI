
import re


# ============================================================
# CLEAN EDUCATION TEXT
# ============================================================

def clean_education_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# EDUCATION HEADERS
# ============================================================

HEADER_LINES = {
    "institute", "institution", "university", "college",
    "school", "year", "years", "duration", "cgpa", "gpa",
    "grade", "grades", "percentage", "score", "qualification",
    "education"
}


# ============================================================
# QUALIFICATION DETECTION
# ============================================================

QUALIFICATION_PATTERNS = [
    r"\bb\.?\s*tech\b",
    r"\bbachelor(?:'s)?\s+of\s+(?:technology|engineering|science|arts|commerce|computer\s+applications)\b",
    r"\bb\.?\s*e\.?\b",
    r"\bb\.?\s*sc\.?\b",
    r"\bb\.?\s*com\.?\b",
    r"\bb\.?\s*a\.?\b",
    r"\bb\.?\s*c\.?\s*a\.?\b",
    r"\bm\.?\s*tech\b",
    r"\bmaster(?:'s)?\s+of\s+(?:technology|engineering|science|arts|commerce|business\s+administration)\b",
    r"\bm\.?\s*e\.?\b",
    r"\bm\.?\s*sc\.?\b",
    r"\bm\.?\s*com\.?\b",
    r"\bm\.?\s*b\.?\s*a\.?\b",
    r"\bm\.?\s*c\.?\s*a\.?\b",
    r"\bph\.?\s*d\.?\b",
    r"\bdoctor(?:ate)?\b",
    r"\bassociate(?:'s)?\s+degree\b",
    r"\bbachelor(?:'s)?\s+degree\b",
    r"\bmaster(?:'s)?\s+degree\b",
    r"\bhigh\s+school\b",
    r"\bsecondary\s+school\b",
    r"\bhigher\s+secondary\b",
    r"\bintermediate\b",
    r"\bpre[- ]university\b",
    r"\b\+2\b",
    r"\bcbse\b",
    r"\bicse\b",
    r"\bssc\b",
    r"\bhsc\b",
    r"\ba[- ]levels?\b",
    r"\bo[- ]levels?\b",
    r"\bged\b",
    r"\bdiploma\b",
    r"\bcertificate\s+program\b",
    r"\bpostgraduate\s+diploma\b",
    r"\bpost[- ]graduate\b",
    r"\bundergraduate\b",
    r"\bvocational\s+qualification\b"
]


def is_qualification_line(line: str) -> bool:
    if not line:
        return False

    return any(
        re.search(pattern, line, re.IGNORECASE)
        for pattern in QUALIFICATION_PATTERNS
    )


# ============================================================
# DATE EXTRACTION
# ============================================================


DATE_PATTERN = re.compile(
    r"\b("
    r"(?:19|20)\d{2}"
    r")\s*"
    r"(?:[-–—]|to)\s*"
    r"("
    r"(?:(?:19|20)\d{2})|"
    r"(?:\d{2})|"
    r"present|current"
    r")\b",
    re.IGNORECASE
)

MONTH_DATE_PATTERN = re.compile(
    r"\b[A-Za-z]{3,9}\s+((?:19|20)\d{2})"
    r"\s*[-–—]\s*"
    r"[A-Za-z]{3,9}\s+((?:19|20)\d{2})\b",
    re.IGNORECASE
)




def extract_years(text: str):
    if not text:
        return None

    month_match = MONTH_DATE_PATTERN.search(text)

    if month_match:
        return {
            "start_year": month_match.group(1),
            "end_year": month_match.group(2)
        }

    match = DATE_PATTERN.search(text)

    if not match:
        return None

    start_year = match.group(1)
    end_year = match.group(2)

    if end_year.isdigit() and len(end_year) == 2:
        end_year = start_year[:2] + end_year

    if end_year.lower() in {"present", "current"}:
        end_year = "Present"

    return {
        "start_year": start_year,
        "end_year": end_year
    }



def is_year_line(line: str) -> bool:
    if not line:
        return False

    return bool(
        DATE_PATTERN.fullmatch(line.strip())
    )


# ============================================================
# GRADE EXTRACTION
# ============================================================

def extract_grade(text: str):
    if not text:
        return None

    patterns = [
        (
            r"\bCGPA\s*[:=-]?\s*(\d+(?:\.\d+)?)",
            "CGPA"
        ),
        (
            r"\bGPA\s*[:=-]?\s*(\d+(?:\.\d+)?)",
            "GPA"
        ),
        (
            r"\b(?:percentage|percent|score)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*%?",
            "Percentage"
        ),
        (
            r"\bgrade\s*[:=-]?\s*([A-F][+-]?|A1|A2|B1|B2|C1|C2|D|E)",
            "Grade"
        )
    ]

    for pattern, grade_type in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return {
                "type": grade_type,
                "value": match.group(1)
            }

    # Preserve an unlabelled numeric result without
    # incorrectly assuming it is CGPA or GPA.
    match = re.fullmatch(
        r"\s*(\d{1,3}(?:\.\d{1,2})?)\s*%?\s*",
        text
    )

    if match:
        value = match.group(1)

        return {
            "type": "UNSPECIFIED",
            "value": value
        }

    return None


# ============================================================
# LOCATION EXTRACTION
# ============================================================

def extract_location(text: str):
    if not text:
        return None

    # Location is extracted from a comma-separated
    # institution line when available.
    parts = [
        part.strip()
        for part in text.split(",")
        if part.strip()
    ]

    if len(parts) >= 2:
        return ", ".join(parts[1:])

    return None


# ============================================================
# INSTITUTION EXTRACTION
# ============================================================

def extract_institution(text: str):
    if not text:
        return None

    parts = [
        part.strip()
        for part in text.split(",")
        if part.strip()
    ]

    if not parts:
        return None

    return parts[0].strip(" ,.-:") or None


# ============================================================
# PROGRAM EXTRACTION
# ============================================================

def extract_program(text: str):
    if not text:
        return None

    return text.strip(" ,.-:") or None


# ============================================================
# EDUCATION ENTRY EXTRACTION
# ============================================================


def extract_education_entries(text: str):

    if not text:
        return []

    lines = [
        line.strip()
        for line in clean_education_text(text).splitlines()
        if line.strip()
    ]

    entries = []
    current_entry = None
    pending_institution = None

    for line in lines:

        if line.casefold().rstrip(":") in HEADER_LINES:
            continue

        if is_qualification_line(line):

            if current_entry:
                entries.append(current_entry)

            current_entry = {
                "program": line,
                "institution": pending_institution,
                "years": None,
                "grade": None,
                "raw_lines": (
                    [pending_institution, line]
                    if pending_institution
                    else [line]
                )
            }

            pending_institution = None
            continue

        # Institution appearing before qualification.
        if current_entry is None:
            if not extract_years(line) and not extract_grade(line):
                pending_institution = line
            continue

        current_entry["raw_lines"].append(line)

        years = extract_years(line)

        if years:
            current_entry["years"] = years
            continue

        grade = extract_grade(line)

        if grade:
            current_entry["grade"] = grade
            continue

        if current_entry["institution"] is None:
            current_entry["institution"] = line

    if current_entry:
        entries.append(current_entry)

    return entries



# ============================================================
# MASTER EDUCATION PARSER
# ============================================================

def parse_education(text: str):

    if not text:
        return []

    raw_entries = extract_education_entries(text)

    parsed_entries = []

    for entry in raw_entries:

        institution_text = entry.get("institution")

        parsed_entries.append({
            "raw_text": " ".join(entry["raw_lines"]),
            "institution": extract_institution(institution_text),
            "location": extract_location(institution_text),
            "program": extract_program(entry.get("program")),
            "years": entry.get("years"),
            "grade": entry.get("grade")
        })

    return parsed_entries
