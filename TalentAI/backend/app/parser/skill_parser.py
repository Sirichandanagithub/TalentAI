import json
import re
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SKILLS_FILE = DATA_DIR / "skills.json"


# ============================================================
# CLEAN SKILL TEXT
# ============================================================

def clean_skill_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# CATEGORY NORMALIZATION
# ============================================================

CATEGORY_ALIASES = {
    "languages": "programming_languages",
    "programming_languages": "programming_languages",
    "web_development": "web_development",

    "database": "databases",
    "databases": "databases",

    "libraries_frameworks": "frameworks",
    "library_frameworks": "frameworks",
    "frameworks": "frameworks",

    "data_science": "data_science",
    "machine_learning": "machine_learning",

    "cloud": "cloud",
    "cloud_computing": "cloud",
    "cloud_and_devops": "cloud_and_devops",
    "devops": "devops",

    "tools": "tools_and_software",
    "software": "tools_and_software",
    "tools_and_software": "tools_and_software",

    "business": "business_and_management",
    "management": "business_and_management",
    "business_and_management": "business_and_management",

    "finance": "finance_and_accounting",
    "accounting": "finance_and_accounting",
    "finance_and_accounting": "finance_and_accounting",

    "marketing": "marketing_and_sales",
    "sales": "marketing_and_sales",
    "marketing_and_sales": "marketing_and_sales",

    "communication": "communication",
    "leadership": "leadership",
    "interpersonal": "interpersonal",

    "soft_skills": "interpersonal",

    "hard_skills": "other_skills",
    "professional_skills": "other_skills",
    "core_skills": "other_skills",
    "functional_skills": "other_skills",

    "domain_knowledge": "domain_knowledge",
    "domain_expertise": "domain_knowledge",

    "basics": "other_skills",
    "basic": "other_skills",
    "others": "other_skills",
    "other": "other_skills",
    "other_skills": "other_skills"
}


def normalize_category(category: str):

    if not category:
        return None

    category = category.strip().lower()

    category = re.sub(
        r"[^a-z0-9]+",
        "_",
        category
    ).strip("_")

    return CATEGORY_ALIASES.get(category)


# ============================================================
# LOAD KNOWN SKILLS
# ============================================================

def load_skill_dictionary():

    if not SKILLS_FILE.exists():
        return {}

    try:
        with open(
            SKILLS_FILE,
            "r",
            encoding="utf-8-sig"
        ) as file:

            data = json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}

    dictionary = {}

    for category, skills in data.items():

        normalized_category = normalize_category(category)

        if not normalized_category:
            continue

        dictionary.setdefault(
            normalized_category,
            []
        )

        for skill in skills:

            normalized_skill = normalize_skill_name(skill)

            if normalized_skill:
                dictionary[normalized_category].append(
                    normalized_skill
                )

    return dictionary


# ============================================================
# SKILL NAME NORMALIZATION
# ============================================================

SKILL_ALIASES = {
    "java script": "JavaScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "python": "Python",
    "java": "Java",
    "c++": "C++",
    "c#": "C#",
    "sql": "SQL",
    "mysql": "MySQL",
    "my sql": "MySQL",
    "sci-kit learn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "matplotlib": "Matplotlib",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "html": "HTML",
    "css": "CSS",
    "azure": "Azure",
    "aws": "AWS",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "ms excel": "Microsoft Excel",
    "microsoft excel": "Microsoft Excel",
    "microsoft word": "Microsoft Word",
    "microsoft powerpoint": "Microsoft PowerPoint"
}


GENERIC_SKILLS_BY_CATEGORY = {
    "machine_learning": {
        "analysis",
        "basics",
        "knowledge",
        "concepts",
        "fundamentals"
    },
    "data_science": {
        "analysis",
        "basics",
        "knowledge",
        "concepts",
        "fundamentals"
    }
}


def normalize_skill_name(skill: str):

    if not skill:
        return ""

    skill = skill.strip()

    skill = re.sub(
        r"^[\-\u2022➢*]+\s*",
        "",
        skill
    ).strip()

    skill = re.sub(
        r"[.,;:]+$",
        "",
        skill
    ).strip()

    skill = re.sub(r"\s+", " ", skill)

    return SKILL_ALIASES.get(
        skill.casefold(),
        skill
    )


def is_valid_skill_for_category(skill: str, category: str) -> bool:
    if not skill or not category:
        return False

    generic_skills = GENERIC_SKILLS_BY_CATEGORY.get(
        category,
        set()
    )

    return skill.casefold() not in generic_skills



# ============================================================
# BUILD KNOWN SKILL LOOKUP
# ============================================================

def get_known_skill_lookup():

    lookup = {}

    for category, skills in load_skill_dictionary().items():

        for skill in skills:

            lookup.setdefault(
                skill.casefold(),
                category
            )

    return lookup


# ============================================================
# SPLIT SKILLS
# ============================================================

def split_skills(text: str):

    if not text:
        return []

    text = text.strip().lstrip(":")

    text = re.sub(
        r"[•●▪➢]",
        ",",
        text
    )

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

    final_skill = "".join(current).strip()

    if final_skill:
        skills.append(final_skill)

    return [
        normalize_skill_name(skill)
        for skill in skills
        if normalize_skill_name(skill)
    ]


# ============================================================
# CATEGORY HEADING DETECTION
# ============================================================

def extract_category_heading(line: str):

    if not line:
        return None

    cleaned = line.strip().rstrip(":")

    return normalize_category(cleaned)


# ============================================================
# EXTRACT SKILL CATEGORIES
# ============================================================

def extract_skill_categories(text: str):

    if not text:
        return {}

    lines = [
        line.strip()
        for line in clean_skill_text(text).splitlines()
        if line.strip()
    ]

    categories = {}
    current_category = None

    for line in lines:

        match = re.match(
            r"^([^:]{2,60})\s*:\s*(.*)$",
            line
        )

        if match:

            category = normalize_category(
                match.group(1)
            )

            if category:

                current_category = category

                categories.setdefault(
                    category,
                    []
                )

                skill_text = match.group(2).strip()

                if skill_text:

                    categories[category].extend(
                        split_skills(skill_text)
                    )

            else:

                current_category = None

            continue

        heading = extract_category_heading(line)

        if heading:

            current_category = heading

            categories.setdefault(
                heading,
                []
            )

            continue

        if line.startswith(":") and current_category:

            categories[current_category].extend(
                split_skills(line[1:])
            )

            continue

        if current_category:

            categories[current_category].extend(
                split_skills(line)
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
        seen = set()

        for skill in skills:

            skill = normalize_skill_name(skill)

            if not skill:
                continue

            if not is_valid_skill_for_category(skill, category):
                continue

            key = skill.casefold()

            if key not in seen:
                unique_skills.append(skill)
                seen.add(key)

        if unique_skills:
            normalized[category] = unique_skills

    return normalized



# ============================================================
# EXTRACT SKILL SECTION
# ============================================================

def extract_skill_section(text: str):

    if not text:
        return None

    text = clean_skill_text(text)

    return text if text else None


# ============================================================
# MASTER SKILL PARSER
# ============================================================

def parse_skills(text: str):

    section = extract_skill_section(text)

    if not section:
        return {}

    categories = extract_skill_categories(section)

    return normalize_skills(categories)
