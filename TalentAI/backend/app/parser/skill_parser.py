import re


# ============================================================
# CLEAN SKILL TEXT
# ============================================================

def clean_skill_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize multiple newlines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# SKILL SECTION
# ============================================================

def extract_skill_section(text: str):

    if not text:
        return None

    text = clean_skill_text(text)

    return text if text else None


# ============================================================
# SKILL CATEGORY NORMALIZATION
# ============================================================

def normalize_category(category: str):

    if not category:
        return None

    category = category.strip().lower()

    category = re.sub(
        r"[^a-z0-9]+",
        "_",
        category
    )

    category = category.strip("_")

    category_map = {

        "programming_languages":
            "programming_languages",

        "programming_language":
            "programming_languages",

        "languages":
            "programming_languages",

        "databases":
            "databases",

        "database":
            "databases",

        "data_science":
            "data_science",

        "data_analysis":
            "data_science",

        "machine_learning":
            "machine_learning",

        "machine_learning_and_ai":
            "machine_learning",

        "deep_learning":
            "machine_learning",

        "tools":
            "tools",

        "tools_and_technologies":
            "tools",

        "technologies":
            "tools",

        "others":
            "others",

        "other":
            "others"
    }

    return category_map.get(
        category,
        category
    )


# ============================================================
# SPLIT SKILLS
# ============================================================
def split_skills(text: str):

    if not text:
        return []

    text = text.strip().lstrip(":")

    skills = []
    current = []
    parentheses_depth = 0

    for char in text:

        if char == "(":
            parentheses_depth += 1

        elif char == ")":
            parentheses_depth = max(
                0,
                parentheses_depth - 1
            )

        if char in ",|;" and parentheses_depth == 0:

            skill = "".join(current).strip()

            if skill:
                skills.append(skill)

            current = []

        else:
            current.append(char)

    # Add final skill
    skill = "".join(current).strip()

    if skill:
        skills.append(skill)

    cleaned_skills = []

    for skill in skills:

        skill = re.sub(
            r"^[\-\u2022]+",
            "",
            skill
        ).strip()

        if skill:
            cleaned_skills.append(skill)

    return cleaned_skills


# ============================================================
# EXTRACT CATEGORIES
# ============================================================

def extract_skill_categories(text: str):

    if not text:
        return {}

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    categories = {}

    current_category = None

    for line in lines:

        # Detect category headings
        if re.match(
            r"^(Programming Languages|Programming Language|"
            r"Databases|Database|"
            r"Data Science|"
            r"Data Analysis|"
            r"Machine Learning|"
            r"Deep Learning|"
            r"Tools|"
            r"Tools and Technologies|"
            r"Technologies|"
            r"Others|Other)\s*:?\s*$",
            line,
            re.IGNORECASE
        ):

            current_category = normalize_category(
                line.rstrip(":").strip()
            )

            categories.setdefault(
                current_category,
                []
            )

            continue

        if current_category:

            skills = split_skills(line)

            categories[current_category].extend(
                skills
            )

    return categories


# ============================================================
# NORMALIZE SKILLS
# ============================================================

def normalize_skills(categories: dict):

    if not categories:
        return {}

    normalized = {}

    for category, skills in categories.items():

        unique_skills = []

        for skill in skills:

            skill = skill.strip()

            if not skill:
                continue

            # Avoid duplicates
            if skill.lower() not in [
                existing.lower()
                for existing in unique_skills
            ]:
                unique_skills.append(skill)

        normalized[category] = unique_skills

    return normalized


# ============================================================
# MASTER SKILL PARSER
# ============================================================

def parse_skills(text: str):

    section = extract_skill_section(text)

    if not section:
        return {}

    categories = extract_skill_categories(
        section
    )

    return normalize_skills(
        categories
    )