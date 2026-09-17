import re


# ============================================================
# CLEAN CERTIFICATION TEXT
# ============================================================

def clean_certification_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize bullets
    text = text.replace("➢", "-")
    text = text.replace("•", "-")

    # Fix PDF extraction:
    # Qualifie2023 -> Qualifie 2023
    text = re.sub(
        r"([A-Za-z])((?:19|20)\d{2})\b",
        r"\1 \2",
        text
    )

    # Normalize spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n+",
        "\n",
        text
    )

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
# DATE EXTRACTION
# ============================================================

def extract_certification_date(text: str):

    if not text:
        return None

    # --------------------------------------------------------
    # Month + Year
    # --------------------------------------------------------

    month_match = re.search(
        r"\b("
        r"January|February|March|April|May|June|"
        r"July|August|September|October|November|December"
        r")\s+(19|20)\d{2}\b",
        text,
        re.IGNORECASE
    )

    if month_match:

        return month_match.group(0)

    # --------------------------------------------------------
    # Standalone year
    # --------------------------------------------------------

    year_match = re.search(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    if year_match:

        return year_match.group(0)

    return None


# ============================================================
# ISSUER EXTRACTION
# ============================================================

KNOWN_ISSUERS = [

    "NPTEL",
    "Coursera",
    "Udemy",
    "GeeksforGeeks",
    "IBM",
    "Microsoft",
    "Google",
    "AWS",
    "Cisco",
    "Oracle",
    "Infosys",
    "TCS",
    "Salesforce"
]


def extract_certification_issuer(text: str):

    if not text:
        return None

    # --------------------------------------------------------
    # Explicit issuer patterns
    # --------------------------------------------------------

    issuer_patterns = [

        r"\bissued\s+by\s+(.+?)(?:\s+\d{4}|$)",

        r"\bprovided\s+by\s+(.+?)(?:\s+\d{4}|$)",

        r"\bcertified\s+by\s+(.+?)(?:\s+\d{4}|$)",

        r"\bby\s+(.+?)(?:\s+\d{4}|$)"
    ]

    for pattern in issuer_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            issuer = match.group(1).strip()

            if issuer:

                return issuer

    # --------------------------------------------------------
    # Known issuers
    # --------------------------------------------------------

    for issuer in KNOWN_ISSUERS:

        if re.search(
            rf"\b{re.escape(issuer)}\b",
            text,
            re.IGNORECASE
        ):

            return issuer

    return None


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

    name = lines[0]

    name = re.sub(
        r"^[-•➢]+\s*",
        "",
        name
    ).strip()

    # Do not allow a year to become certification name
    if re.fullmatch(
        r"(19|20)\d{2}",
        name
    ):

        return None

    return name if name else None


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

    if len(lines) <= 1:
        return None

    description_lines = []

    for line in lines[1:]:

        # Ignore standalone year
        if re.fullmatch(
            r"(19|20)\d{2}",
            line
        ):
            continue

        # Remove bullet
        line = re.sub(
            r"^[-•➢]+\s*",
            "",
            line
        ).strip()

        if not line:
            continue

        # Do not treat issuer-only lines as descriptions
        if any(
            line.lower() == issuer.lower()
            for issuer in KNOWN_ISSUERS
        ):
            continue

        # Credential verification information
        if re.search(
            r"credential\s+id",
            line,
            re.IGNORECASE
        ):
            continue

        if re.search(
            r"certification\s+verification",
            line,
            re.IGNORECASE
        ):
            continue

        description_lines.append(
            line
        )

    if not description_lines:
        return None

    return " ".join(
        description_lines
    )


# ============================================================
# CERTIFICATION TITLE DETECTION
# ============================================================

def is_certification_title(line: str) -> bool:

    if not line:
        return False

    line = re.sub(
        r"^[-•➢]+\s*",
        "",
        line
    ).strip()

    if not line:
        return False

    # A year can NEVER be a title
    if re.fullmatch(
        r"(19|20)\d{2}",
        line
    ):
        return False

    lower_line = line.lower()

    # --------------------------------------------------------
    # Known certification names
    # --------------------------------------------------------

    known_titles = [

        "frontend with html and css",

        "problem solving through programming in c",

        "data engineering with hadoop and spark",

        "agentforce specialist"
    ]

    for title in known_titles:

        if lower_line == title:

            return True

    # --------------------------------------------------------
    # Strong certification keywords
    # --------------------------------------------------------

    certification_keywords = [

        "certification",
        "certificate",
        "specialist",
        "professional"
    ]

    if any(
        keyword in lower_line
        for keyword in certification_keywords
    ):

        return True

    # --------------------------------------------------------
    # ALL CAPS title
    # --------------------------------------------------------

    if (
        line == line.upper()
        and len(line.split()) <= 10
        and not re.search(
            r"[.!?,]$",
            line
        )
    ):

        return True

    return False


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

    if not lines:
        return []

    entries = []

    current_entry = []

    for line in lines:

        clean_line = re.sub(
            r"^[-•➢]+\s*",
            "",
            line
        ).strip()

        if not clean_line:
            continue

        # ----------------------------------------------------
        # Detect new certification
        # ----------------------------------------------------

        new_certification = is_certification_title(
            clean_line
        )

        # ----------------------------------------------------
        # Start a new entry ONLY when we already have one
        # ----------------------------------------------------

        if (
            new_certification
            and current_entry
        ):

            entries.append(
                "\n".join(
                    current_entry
                )
            )

            current_entry = []

        current_entry.append(
            clean_line
        )

    # --------------------------------------------------------
    # Add final entry
    # --------------------------------------------------------

    if current_entry:

        entries.append(
            "\n".join(
                current_entry
            )
        )

    return entries


# ============================================================
# MASTER CERTIFICATION PARSER
# ============================================================

def parse_certifications(text: str):

    section = extract_certification_section(
        text
    )

    if not section:
        return []

    raw_entries = extract_certification_entries(
        section
    )

    parsed_certifications = []

    for entry in raw_entries:

        name = extract_certification_name(
            entry
        )

        # Skip invalid entries
        if not name:
            continue

        parsed_certifications.append(
            {
                "raw_text": entry,

                "certification_name":
                    name,

                "issuer":
                    extract_certification_issuer(
                        entry
                    ),

                "date":
                    extract_certification_date(
                        entry
                    ),

                "description":
                    extract_certification_description(
                        entry
                    )
            }
        )

    return parsed_certifications