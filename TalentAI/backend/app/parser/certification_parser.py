import re


# ============================================================
# CLEAN CERTIFICATION TEXT
# ============================================================

def clean_certification_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")

    # Normalize bullet characters
    text = text.replace("➢", "-")
    text = text.replace("•", "-")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
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
# DATE EXTRACTION
# ============================================================

def extract_certification_date(text: str):

    if not text:
        return None

    # Month + year
    month_match = re.search(
        r"\b("
        r"January|February|March|April|May|June|"
        r"July|August|September|October|November|December"
        r")\s+(19|20)\d{2}\b",
        text,
        re.IGNORECASE
    )

    if month_match:
        return month_match.group()

    # Standalone year
    year_match = re.search(
        r"\b(19|20)\d{2}\b",
        text
    )

    if year_match:
        return year_match.group()

    return None


# ============================================================
# ISSUER EXTRACTION
# ============================================================

def extract_certification_issuer(text: str):

    if not text:
        return None

    # Explicit issuer patterns
    issuer_patterns = [

        r"\bissued\s+by\s+(.+?)(?:\s+\d{4}|$)",

        r"\bby\s+(.+?)(?:\s+\d{4}|$)",

        r"\bfrom\s+(.+?)(?:\s+\d{4}|$)"
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


    # Known certification issuers
    known_issuers = [
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
        "TCS"
    ]

    for issuer in known_issuers:

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

    # Remove bullet characters
    name = re.sub(
        r"^[\-\u2022➢]+",
        "",
        name
    ).strip()

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

        # Remove leading bullets
        line = re.sub(
            r"^[\-\u2022➢]+\s*",
            "",
            line
        ).strip()

        if not line:
            continue

        description_lines.append(line)

    if not description_lines:
        return None

    return " ".join(description_lines)


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

        upper_line = line.upper()

        # ----------------------------------------------------
        # Detect a new certification
        # ----------------------------------------------------

        is_new_certification = False

        # A line containing certification/certificate
        if (
            "CERTIFICATION" in upper_line
            or "CERTIFICATE" in upper_line
        ):
            is_new_certification = True

        # If current entry already contains a year and
        # the current line looks like a new title,
        # start a new entry.
        elif current_entry:

            current_has_date = any(
                re.search(
                    r"\b(19|20)\d{2}\b",
                    previous_line
                )
                for previous_line in current_entry
            )

            looks_like_title = (
                len(line.split()) >= 2
                and not line.startswith("-")
            )

            if current_has_date and looks_like_title:
                is_new_certification = True

        # ----------------------------------------------------
        # Start new certification
        # ----------------------------------------------------

        if is_new_certification and current_entry:

            entries.append(
                "\n".join(current_entry)
            )

            current_entry = []

        current_entry.append(line)

    # Add final entry
    if current_entry:

        entries.append(
            "\n".join(current_entry)
        )

    return entries


# ============================================================
# MASTER CERTIFICATION PARSER
# ============================================================

def parse_certifications(text: str):

    section = extract_certification_section(text)

    if not section:
        return []

    raw_entries = extract_certification_entries(
        section
    )

    parsed_certifications = []

    for entry in raw_entries:

        parsed_certifications.append(
            {
                "raw_text": entry,

                "certification_name":
                    extract_certification_name(
                        entry
                    ),

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