import re


# ============================================================
# CLEAN ACHIEVEMENT TEXT
# ============================================================

def clean_achievement_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# ACHIEVEMENT SECTION
# ============================================================

def extract_achievement_section(text: str):

    if not text:
        return None

    text = clean_achievement_text(text)

    return text if text else None


# ============================================================
# ACHIEVEMENT NAME
# ============================================================

def extract_achievement_name(text: str):

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    # First line is treated as the achievement heading
    name = lines[0]

    # Remove bullet characters if present
    name = re.sub(
        r"^[➢•\-]+\s*",
        "",
        name
    ).strip()

    return name if name else None


# ============================================================
# ACHIEVEMENT DESCRIPTION
# ============================================================

def extract_achievement_description(text: str):

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

        # Remove bullet characters
        clean_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            line
        ).strip()

        if clean_line:
            description_lines.append(clean_line)

    if not description_lines:
        return None

    return " ".join(description_lines)


# ============================================================
# ACHIEVEMENT ENTRY EXTRACTION
# ============================================================

def extract_achievement_entries(text: str):

    if not text:
        return []

    text = clean_achievement_text(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return []

    entries = []

    current_entry = []

    # Patterns used to identify achievement headings
    heading_patterns = [
        r"\bcoordinator\b",
        r"\bco-ordinator\b",
        r"\bpresident\b",
        r"\bsecretary\b",
        r"\bmember\b",
        r"\baward\b",
        r"\bwinner\b",
        r"\bachievement\b",
        r"\brepresentative\b",
        r"\bcaptain\b",
        r"\borganizer\b",
        r"\borganiser\b",
    ]

    for line in lines:

        # ----------------------------------------------------
        # Check whether the original line is a bullet
        # ----------------------------------------------------

        is_bullet = bool(
            re.match(
                r"^[➢•\-]+\s*",
                line
            )
        )

        # ----------------------------------------------------
        # Remove bullet characters
        # ----------------------------------------------------

        clean_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            line
        ).strip()

        if not clean_line:
            continue

        lower_line = clean_line.lower()

        # ----------------------------------------------------
        # Detect achievement heading
        # ----------------------------------------------------

        is_heading = False

        # IMPORTANT:
        # Bullet lines are descriptions, not headings.
        if not is_bullet:

            if any(
                re.search(
                    pattern,
                    lower_line
                )
                for pattern in heading_patterns
            ):
                is_heading = True

        # ----------------------------------------------------
        # New achievement found
        # ----------------------------------------------------

        if is_heading and current_entry:

            entries.append(
                "\n".join(current_entry)
            )

            current_entry = []

        # ----------------------------------------------------
        # Add current line
        # ----------------------------------------------------

        current_entry.append(clean_line)

    # --------------------------------------------------------
    # Add final achievement
    # --------------------------------------------------------

    if current_entry:

        entries.append(
            "\n".join(current_entry)
        )

    return entries


# ============================================================
# MASTER ACHIEVEMENT PARSER
# ============================================================

def parse_achievements(text: str):

    section = extract_achievement_section(text)

    if not section:
        return []

    raw_entries = extract_achievement_entries(
        section
    )

    parsed_achievements = []

    for entry in raw_entries:

        parsed_achievements.append(
            {
                "raw_text": entry,

                "achievement_name":
                    extract_achievement_name(
                        entry
                    ),

                "description":
                    extract_achievement_description(
                        entry
                    )
            }
        )

    return parsed_achievements