
import re


# ============================================================
# CLEAN LANGUAGE TEXT
# ============================================================

def clean_language_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
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
# KNOWN SPOKEN LANGUAGES
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
    "Korean",
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

    text = re.sub(
        r"^[➢•\-*]+\s*",
        "",
        text
    ).strip()

    # Remove proficiency information.
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
        if text.casefold() == language.casefold():
            return language

    # Strict classification:
    # Unknown terms must not be treated as spoken languages.
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

    entries = []
    seen = set()

    for line in lines:

        parts = [
            part.strip()
            for part in line.split(",")
            if part.strip()
        ]

        for part in parts:

            language = extract_language_name(part)

            if not language:
                continue

            normalized = language.casefold()

            if normalized in seen:
                continue

            proficiency = extract_language_proficiency(part)

            entry = {
                "language": language
            }

            if proficiency:
                entry["proficiency"] = proficiency

            entries.append(entry)
            seen.add(normalized)

    return entries


# ============================================================
# MASTER LANGUAGE PARSER
# ============================================================

def parse_languages(text: str):

    section = extract_language_section(text)

    if not section:
        return []

    return extract_language_entries(section)
