import re


# ============================================================
# CLEAN EXPERIENCE TEXT
# ============================================================

def clean_experience_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = text.replace("➢", "\n➢")
    text = text.replace("•", "\n•")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# EXPERIENCE SECTION
# ============================================================

def extract_experience_section(text: str):
    if not text:
        return None

    text = clean_experience_text(text)
    lines = text.splitlines()

    start_index = None

    for index, line in enumerate(lines):
        if re.match(
            r"^\s*(?:professional\s+)?experience\s*:?\s*$",
            line,
            re.IGNORECASE
        ):
            start_index = index + 1
            break

    if start_index is None:
        return text.strip() or None

    section_headers = {
        "education", "projects", "technical skills",
        "skills", "certifications", "achievements",
        "languages", "publications"
    }

    end_index = len(lines)

    for index in range(start_index, len(lines)):
        if lines[index].strip().lower().rstrip(":") in section_headers:
            end_index = index
            break

    result = "\n".join(lines[start_index:end_index]).strip()
    return result or None


# ============================================================
# DATE EXTRACTION
# ============================================================

MONTH_PATTERN = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
    r"Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)


def extract_experience_dates(text: str):
    if not text:
        return None

    text = re.sub(r"[\[\]()]", " ", str(text)).strip()

    # Month-to-month range within the same year:
    # April-June 2023
    match = re.search(
        rf"\b({MONTH_PATTERN})\s*[-–—]\s*"
        rf"({MONTH_PATTERN})\s*,?\s*((?:19|20)\d{{2}})\b",
        text,
        re.IGNORECASE
    )

    if match:
        year = match.group(3)
        return {
            "start": f"{match.group(1)} {year}",
            "end": f"{match.group(2)} {year}",
            "current": False
        }

    # Month/year range:
    # March 2023 - August 2024
    match = re.search(
        rf"\b({MONTH_PATTERN})\s*,?\s*((?:19|20)\d{{2}})"
        rf"\s*[-–—]\s*"
        rf"({MONTH_PATTERN})\s*,?\s*((?:19|20)\d{{2}})\b",
        text,
        re.IGNORECASE
    )

    if match:
        return {
            "start": f"{match.group(1)} {match.group(2)}",
            "end": f"{match.group(3)} {match.group(4)}",
            "current": False
        }

    # Year range:
    # 2022 - 2024
    match = re.search(
        r"\b((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2})\b",
        text
    )

    if match:
        return {
            "start": match.group(1),
            "end": match.group(2),
            "current": False
        }

    # Current employment:
    match = re.search(
        rf"\b({MONTH_PATTERN}\s*,?\s*(?:19|20)\d{{2}}|"
        rf"(?:19|20)\d{{2}})"
        r"\s*[-–—]\s*"
        r"(Present|Current|Now|Ongoing|Till Date)",
        text,
        re.IGNORECASE
    )

    if match:
        return {
            "start": match.group(1),
            "end": match.group(2),
            "current": True
        }

    # Single month and year
    match = re.search(
        rf"\b({MONTH_PATTERN})\s*,?\s*((?:19|20)\d{{2}})\b",
        text,
        re.IGNORECASE
    )

    if match:
        return {
            "start": f"{match.group(1)} {match.group(2)}",
            "end": None,
            "current": False
        }

    # Single year
    match = re.search(r"\b((?:19|20)\d{2})\b", text)

    if match:
        return {
            "start": match.group(1),
            "end": None,
            "current": False
        }

    return None


# ============================================================
# COMPANY AND LOCATION
# ============================================================

LOCATION_PATTERN = (
    r"Remote|Hyderabad|Bangalore|Bengaluru|Chennai|Mumbai|"
    r"Delhi|Pune|Kolkata|India|Telangana|Andhra Pradesh|"
    r"Maharashtra|Karnataka|Dubai|UAE"
)


def extract_experience_location(text: str):
    if not text:
        return None

    match = re.search(
        rf"\b({LOCATION_PATTERN})\b",
        text,
        re.IGNORECASE
    )

    return match.group(1) if match else None


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

    first_line = re.sub(r"^[➢•\-]+\s*", "", lines[0]).strip()

    # Format: Job Title @ Company
    if "@" in first_line:
        return first_line.split("@", 1)[1].strip() or None

    # Format: Company, Location [Dates]
    company = re.sub(r"\[[^\]]*\]", "", first_line)
    company = re.sub(
        rf",?\s*\b(?:{LOCATION_PATTERN})\b.*$",
        "",
        company,
        flags=re.IGNORECASE
    )

    company = company.strip(" ,.-:")
    return company or None


# ============================================================
# JOB TITLE
# ============================================================

JOB_TITLE_KEYWORDS = [
    "developer", "engineer", "intern", "analyst",
    "manager", "designer", "consultant",
    "administrator", "architect", "scientist",
    "specialist", "associate", "executive",
    "trainee", "researcher", "tester", "technician"
]


def is_job_title(line: str) -> bool:
    if not line:
        return False

    line = re.sub(r"^[➢•\-]+\s*", "", line).strip()

    if len(line.split()) > 8:
        return False

    return any(
        keyword in line.casefold()
        for keyword in JOB_TITLE_KEYWORDS
    )


def extract_job_title(text: str):
    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines:
        clean_line = re.sub(r"^[➢•\-]+\s*", "", line).strip()

        if is_job_title(clean_line):
            return clean_line.split("@", 1)[0].strip()

    # Do not assume the company name is the job title.
    return None


# ============================================================
# TECHNOLOGIES AND SKILLS
# ============================================================

def extract_experience_technologies(text: str):
    if not text:
        return []

    technologies = []

    for line in text.splitlines():
        match = re.match(
            r"^\s*(?:Tools?|Tech|Technologies|Technical Skills)\s*:\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:
            values = re.split(r"[,;|]", match.group(1))

            for value in values:
                value = value.strip(" .")

                if value and value.casefold() not in {
                    item.casefold() for item in technologies
                }:
                    technologies.append(value)

    return technologies


# ============================================================
# DESCRIPTION
# ============================================================

# ============================================================
# DESCRIPTION
# ============================================================

def extract_experience_description(text: str):
    if not text:
        return None

    description_lines = []

    lines = text.splitlines()

    for index, line in enumerate(lines):
        clean_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            line
        ).strip()

        if not clean_line:
            continue

        # Skip the first line (company, location and dates).
        if index == 0:
            continue

        # Skip date-only lines.
        if (
            extract_experience_dates(clean_line)
            and len(clean_line.split()) <= 5
        ):
            continue

        # Skip tools and skills metadata.
        if re.match(
            r"^(?:Tools?|Tech|Technologies|Technical Skills|Skills)\s*:",
            clean_line,
            re.IGNORECASE
        ):
            continue

        description_lines.append(clean_line)

    if not description_lines:
        return None

    # Join lines with spaces and normalize whitespace.
    description = " ".join(description_lines)

    description = re.sub(r"\s+", " ", description).strip()

    return description


# ============================================================
# ENTRY EXTRACTION
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
        clean_line = re.sub(r"^[➢•\-]+\s*", "", line).strip()

        # Start a new entry only when a clear job title appears.
        if is_job_title(clean_line) and current_entry:
            entries.append("\n".join(current_entry))
            current_entry = []

        current_entry.append(line)

    if current_entry:
        entries.append("\n".join(current_entry))

    return entries


# ============================================================
# MASTER EXPERIENCE PARSER
# ============================================================

def parse_experience(text: str):
    section = extract_experience_section(text)

    if not section:
        return []

    entries = extract_experience_entries(section)

    return [
        {
            "raw_text": entry,
            "job_title": extract_job_title(entry),
            "company": extract_company(entry),
            "location": extract_experience_location(entry),
            "dates": extract_experience_dates(entry),
            "technologies": extract_experience_technologies(entry),
            "description": extract_experience_description(entry),
        }
        for entry in entries
    ]
