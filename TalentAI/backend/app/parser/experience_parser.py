import re


# ============================================================
# CLEAN EXPERIENCE TEXT
# ============================================================

def clean_experience_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")

    # Normalize bullet characters
    text = text.replace("➢", "\n➢")
    text = text.replace("•", "\n•")

    # Fix common PDF extraction spacing problems
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# EXPERIENCE SECTION
# ============================================================

def extract_experience_section(text: str):

    if not text:
        return None

    text = clean_experience_text(text)

    return text if text else None


# ============================================================
# JOB TITLE DETECTION
# ============================================================

def is_job_title(line: str) -> bool:

    if not line:
        return False

    # Remove bullets
    clean_line = re.sub(
        r"^[➢•\-]+\s*",
        "",
        line
    ).strip()

    if not clean_line:
        return False

    lower_line = clean_line.lower()

    title_keywords = [
        "developer",
        "engineer",
        "intern",
        "analyst",
        "manager",
        "designer",
        "consultant",
        "administrator",
        "architect",
        "scientist",
        "specialist",
        "associate",
        "executive",
        "lead",
        "trainee",
        "researcher",
        "director",
        "coordinator",
        "officer",
        "accountant",
        "tester",
        "qa",
        "technician"
    ]

    # Must contain a job-title keyword
    if not any(
        keyword in lower_line
        for keyword in title_keywords
    ):
        return False

    # Avoid treating long sentences as job titles
    if len(clean_line.split()) > 8:
        return False

    # Avoid description-like sentences
    sentence_patterns = [
        r"^as\s+",
        r"^i\s+",
        r"^gained\s+",
        r"^worked\s+",
        r"^developed\s+",
        r"^utilized\s+",
        r"^responsible\s+for",
        r"^contributed\s+",
        r"^learned\s+"
    ]

    for pattern in sentence_patterns:

        if re.match(
            pattern,
            lower_line
        ):
            return False

    return True


# ============================================================
# JOB TITLE
# ============================================================

def extract_job_title(text: str):

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    for line in lines:

        clean_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            line
        ).strip()

        if is_job_title(clean_line):

            return clean_line

    return lines[0]


# ============================================================
# COMPANY
# ============================================================
# ============================================================
# COMPANY
# ============================================================

def extract_company(text: str):

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    # --------------------------------------------------------
    # Case 1:
    # Organization: Bharat Dynamics Limited ...
    # --------------------------------------------------------

    for line in lines:

        clean_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            line
        ).strip()

        organization_match = re.match(
            r"^(?:Organization|Company)\s*:\s*(.+)$",
            clean_line,
            re.IGNORECASE
        )

        if organization_match:

            company = organization_match.group(1).strip()

            # Remove date information from company
            company = re.sub(
                r"\s*\[\s*"
                r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
                r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
                r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
                r"\s+(?:19|20)\d{2}"
                r"\s*\]",
                "",
                company,
                flags=re.IGNORECASE
            )

            return company.strip()

    # --------------------------------------------------------
    # Case 2:
    # Data Analytics Intern
    # Renu Sharma Healthcare and Education Foundation – Remote
    # [April 2025]
    # --------------------------------------------------------

    if len(lines) >= 2:

        company_line = lines[1]

        company_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            company_line
        ).strip()

        # Remove "Organization:" if present
        company_line = re.sub(
            r"^(Organization|Company)\s*:\s*",
            "",
            company_line,
            flags=re.IGNORECASE
        )

        # Remove location
        company_line = re.sub(
            r"\s*[-–—]\s*"
            r"(Remote|Hyderabad|Bangalore|Bengaluru|"
            r"Chennai|Mumbai|Delhi|Pune|Kolkata|"
            r"India|Telangana|Andhra Pradesh|"
            r"Maharashtra|Karnataka)\s*$",
            "",
            company_line,
            flags=re.IGNORECASE
        )

        # Remove date in brackets
        company_line = re.sub(
            r"\s*\[\s*.*?\s*\]\s*$",
            "",
            company_line
        )

        return company_line.strip()

    return None
# ============================================================
# LOCATION
# ============================================================

def extract_experience_location(text: str):

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
        "Remote",
        "India",
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


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_experience_dates(text: str):

    if not text:
        return None

    # --------------------------------------------------------
    # Month + year range
    # --------------------------------------------------------

    date_range_pattern = re.search(
        r"\b("
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+)?"
        r"(19|20)\d{2}"
        r"\s*[-–—]\s*"
        r"("
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+)?"
        r"(19|20)\d{2}\b",
        text,
        re.IGNORECASE
    )

    if date_range_pattern:

        date_text = date_range_pattern.group(0)

        parts = re.split(
            r"\s*[-–—]\s*",
            date_text
        )

        return {
            "start": parts[0].strip(),
            "end": parts[1].strip()
            if len(parts) > 1
            else None
        }

    # --------------------------------------------------------
    # Month + year
    # --------------------------------------------------------

    single_date_pattern = re.search(
        r"\b("
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+"
        r"(19|20)\d{2}"
        r")\b",
        text,
        re.IGNORECASE
    )

    if single_date_pattern:

        return {
            "start": single_date_pattern.group(1),
            "end": None
        }

    # --------------------------------------------------------
    # Year
    # --------------------------------------------------------

    year_pattern = re.search(
        r"\b(19|20)\d{2}\b",
        text
    )

    if year_pattern:

        return {
            "start": year_pattern.group(0),
            "end": None
        }

    return None


# ============================================================
# DESCRIPTION
# ============================================================
def extract_experience_description(text: str):

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    description_lines = []

    for index, line in enumerate(lines):

        # Skip job title
        if index == 0:
            continue

        # Skip company / organization line
        if index == 1:
            continue

        # Skip date-only lines
        if re.fullmatch(
            r"\[\s*("
            r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
            r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
            r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
            r"\s+)?"
            r"(?:19|20)\d{2}"
            r"\s*\]",
            line,
            re.IGNORECASE
        ):
            continue

        # Skip lines containing only a date
        if re.fullmatch(
            r"("
            r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
            r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
            r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
            r"\s+)?"
            r"(?:19|20)\d{2}",
            line,
            re.IGNORECASE
        ):
            continue

        description_lines.append(line)

    if not description_lines:
        return None

    return " ".join(description_lines)
# ============================================================
# EXPERIENCE ENTRY EXTRACTION
# ============================================================

def extract_experience_entries(text: str):

    if not text:
        return []

    text = clean_experience_text(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return []

    entries = []

    current_entry = []

    for line in lines:

        clean_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            line
        ).strip()

        # ----------------------------------------------------
        # Detect a new job title
        # ----------------------------------------------------

        if (
            is_job_title(clean_line)
            and current_entry
        ):

            entries.append(
                "\n".join(current_entry)
            )

            current_entry = []

        current_entry.append(
            line
        )

    # Add final entry
    if current_entry:

        entries.append(
            "\n".join(current_entry)
        )

    return entries


# ============================================================
# MASTER EXPERIENCE PARSER
# ============================================================

def parse_experience(text: str):

    section = extract_experience_section(
        text
    )

    if not section:
        return []

    raw_entries = extract_experience_entries(
        section
    )

    parsed_entries = []

    for entry in raw_entries:

        parsed_entries.append(
            {
                "raw_text": entry,

                "job_title": extract_job_title(
                    entry
                ),

                "company": extract_company(
                    entry
                ),

                "location":
                    extract_experience_location(
                        entry
                    ),

                "dates":
                    extract_experience_dates(
                        entry
                    ),

                "description":
                    extract_experience_description(
                        entry
                    )
            }
        )

    return parsed_entries



