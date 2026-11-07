
import re


# ============================================================
# CLEAN CERTIFICATION TEXT
# ============================================================

def clean_certification_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove PDF bullet symbols.
    text = re.sub(
        r"^[\uf06c➢•▪◦●○■□◆◇\-]+\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Normalize spaces.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# CERTIFICATION SECTION
# ============================================================

def extract_certification_section(text: str):
    if not text:
        return None

    text = clean_certification_text(text)
    return text if text else None


# ============================================================
# CERTIFICATION HEADING DETECTION
# ============================================================

def is_certification_title(line: str) -> bool:
    if not line:
        return False

    line = line.strip()

    if not line or re.fullmatch(r"(?:19|20)\d{2}", line):
        return False

    # Check only the heading before the colon.
    heading = line.split(":", 1)[0].strip()

    normalized = re.sub(r"\s+", " ", heading).casefold()
    compact = re.sub(r"[^a-z0-9]", "", normalized)

    known_titles = {
        "machine learning with python",
        "power bi and data analytics",
        "frontend with html and css",
        "problem solving through programming in c",
        "data engineering with hadoop and spark",
        "agentforce specialist",
    }

    if normalized in known_titles:
        return True

    # Handle PDF formatting such as POWERBI AND DATAANALYTICS.
    if compact == "powerbianddataanalytics":
        return True

    # A colon-separated heading is a likely certification title.
    if ":" in line and len(heading.split()) <= 12:
        return True

    if re.search(
        r"\b(certification|certificate|specialist|professional)\b",
        heading,
        re.IGNORECASE
    ):
        return True

    return False


# ============================================================
# CERTIFICATION DATE EXTRACTION
# ============================================================

def extract_certification_date(text: str):
    if not text:
        return None

    match = re.search(
        r"\b(January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
        r"\s+(?:19|20)\d{2}\b",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(0)

    match = re.search(r"\b(?:19|20)\d{2}\b", text)

    return match.group(0) if match else None


# ============================================================
# CERTIFICATION ISSUER EXTRACTION
# ============================================================

KNOWN_ISSUERS = [
    "Data Minds and Durga Soft",
    "Edunet Training",
    "GeeksforGeeks",
    "Coursera",
    "Udemy",
    "NPTEL",
    "VERZEO",
    "CISCO",
    "Cisco",
    "IBM",
    "Microsoft",
    "Google",
    "AWS",
    "Oracle",
    "Infosys",
    "TCS",
    "Salesforce",
]


def extract_certification_issuer(text: str):
    if not text:
        return None

    found = []

    for issuer in KNOWN_ISSUERS:
        if re.search(
            rf"\b{re.escape(issuer)}\b",
            text,
            re.IGNORECASE
        ):
            if issuer.casefold() not in {
                item.casefold() for item in found
            }:
                found.append(issuer)

    if not found:
        return None

    # Preserve multiple issuers.
    return " and ".join(found)


# ============================================================
# CERTIFICATION NAME
# ============================================================

def extract_certification_name(text: str):
    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    name = re.split(
        r"\s+(?=VERZEO\b|CISCO\b|Cisco\b)",
        lines[0].split(":", 1)[0],
        maxsplit=1,
        flags=re.IGNORECASE
    )[0].strip()

    


    name = re.sub(r"\s+", " ", name)

    # Normalize known title variations.
    compact = re.sub(r"[^a-z0-9]", "", name.casefold())

    if compact == "powerbianddataanalytics":
        return "Power BI and Data Analytics"

    return name or None


# ============================================================
# CERTIFICATION DESCRIPTION
# ============================================================

def extract_certification_description(text: str):
    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    description_parts = []

    first_line = lines[0]

    # Extract text following the first colon.
    if ":" in first_line:
        same_line_description = first_line.split(":", 1)[1].strip()

        # Remove issuer name and separator.
        same_line_description = re.sub(
            r"^(?:VERZEO|CISCO|Cisco|Edunet Training)\s*[-–—:]?\s*",
            "",
            same_line_description,
            flags=re.IGNORECASE
        )

        if same_line_description:
            description_parts.append(same_line_description)

    for line in lines[1:]:

        if re.fullmatch(r"(?:19|20)\d{2}", line):
            continue

        description_parts.append(line)

    if not description_parts:
        return None

    return re.sub(
        r"\s+",
        " ",
        " ".join(description_parts)
    ).strip()


# ============================================================
# CERTIFICATION ENTRY EXTRACTION
# ============================================================

def extract_certification_entries(text: str):
    if not text:
        return []

    text = clean_certification_text(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    entries = []
    current_entry = []

    for line in lines:

        if is_certification_title(line):

            if current_entry:
                entries.append("\n".join(current_entry))

            current_entry = [line]

        elif current_entry:
            current_entry.append(line)

    if current_entry:
        entries.append("\n".join(current_entry))

    return entries

# ============================================================
# MASTER CERTIFICATION PARSER
# ============================================================

def parse_certifications(text: str):

    section = extract_certification_section(text)

    if not section:
        return []

    raw_entries = extract_certification_entries(section)

    parsed_certifications = []

    for entry in raw_entries:

        name = extract_certification_name(entry)

        if not name:
            continue

        parsed_certifications.append({
            "raw_text": entry,
            "certification_name": name,
            "issuer": extract_certification_issuer(entry),
            "date": extract_certification_date(entry),
            "description": extract_certification_description(entry)
        })

    return parsed_certifications
