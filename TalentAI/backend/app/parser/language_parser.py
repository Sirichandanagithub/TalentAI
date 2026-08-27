import re


# ============================================================
# CLEAN LANGUAGE TEXT
# ============================================================

def clean_language_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# LANGUAGE SECTION
# ============================================================

def extract_language_section(text: str):

    if not text:
        return None

    text = clean_language_text(text)

    return text if text else None


# ============================================================
# KNOWN LANGUAGES
# ============================================================

KNOWN_LANGUAGES = [
    "English",
    "Hindi",
    "Telugu",
    "Tamil",
    "Kannada",
    "Malayalam",
    "Bengali",
    "Marathi",
    "Gujarati",
    "Punjabi",
    "Urdu",
    "Odia",
    "Assamese",
    "French",
    "German",
    "Spanish",
    "Italian",
    "Portuguese",
    "Russian",
    "Arabic",
    "Chinese",
    "Japanese",
    "Korean"
]


# ============================================================
# PROFICIENCY EXTRACTION
# ============================================================

def extract_language_proficiency(text: str):

    if not text:
        return None

    proficiency_patterns = [
        r"\s*[-–—:]\s*(.+)$",
        r"\s*\(([^()]+)\)\s*$",
    ]

    for pattern in proficiency_patterns:

        match = re.search(
            pattern,
            text.strip(),
            re.IGNORECASE
        )

        if match:

            proficiency = match.group(1).strip()

            if proficiency:
                return proficiency

    return None


# ============================================================
# LANGUAGE NAME EXTRACTION
# ============================================================

def extract_language_name(text: str):

    if not text:
        return None

    text = text.strip()

    # Remove bullets
    text = re.sub(
        r"^[➢•\-*]+\s*",
        "",
        text
    ).strip()

    # Remove optional proficiency
    text = re.sub(
        r"\s*[-–—:]\s*.+$",
        "",
        text
    ).strip()

    text = re.sub(
        r"\s*\([^()]+\)\s*$",
        "",
        text
    ).strip()

    for language in KNOWN_LANGUAGES:

        if re.fullmatch(
            re.escape(language),
            text,
            re.IGNORECASE
        ):
            return language

    # If it is not in the known-language list,
    # return the cleaned text rather than losing it.
    if text:
        return text

    return None


# ============================================================
# LANGUAGE ENTRY EXTRACTION
# ============================================================

def extract_language_entries(text: str):

    if not text:
        return []

    text = clean_language_text(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return []

    entries = []

    for line in lines:

        # ----------------------------------------------------
        # Handle comma-separated languages
        # Example:
        # English, Hindi, Telugu
        # ----------------------------------------------------

        if "," in line:

            parts = [
                part.strip()
                for part in line.split(",")
                if part.strip()
            ]

        else:

            parts = [line]

        for part in parts:

            language = extract_language_name(part)

            if not language:
                continue

            proficiency = extract_language_proficiency(part)

            entry = {
                "language": language
            }

            # Proficiency is optional.
            # Only store it when explicitly mentioned.
            if proficiency:
                entry["proficiency"] = proficiency

            entries.append(entry)

    return entries


# ============================================================
# MASTER LANGUAGE PARSER
# ============================================================

def parse_languages(text: str):

    section = extract_language_section(text)

    if not section:
        return []

    return extract_language_entries(section)