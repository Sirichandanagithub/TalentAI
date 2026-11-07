
import re


# ============================================================
# GITHUB URL EXTRACTION
# ============================================================

def extract_github_url(text: str) -> str:
    if not text:
        return ""

    match = re.search(
        r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
        text,
        flags=re.IGNORECASE,
    )

    return match.group(0).rstrip(".,;:!?)\"]'") if match else ""


# ============================================================
# CLEAN PROJECT TEXT
# ============================================================

BULLET_PATTERN = re.compile(
    r"^[\s\uf06c\uF0B7\u2022\u25AA\u25AB\u25CF\u25CB"
    r"\u25A0\u25A1\u25C6\u25C7\u27A2\-]+\s*"
)

METADATA_PATTERN = re.compile(
    r"^(?:tools?|technologies|technology|tech stack|"
    r"tools used|skills|github)\s*:",
    re.IGNORECASE,
)

DESCRIPTION_STARTERS = (
    "developed ",
    "designed ",
    "created ",
    "built ",
    "implemented ",
    "utilized ",
    "used ",
    "provided ",
    "supports ",
    "this ",
    "the ",
    "an ",
    "a ",
    "achieved ",
    "gained ",
    "learned ",
    "worked ",
    "integrated ",
    "allows ",
    "engineered ",
    "quantified ",
    "resulting ",
    "which ",
    "that ",
    "enabling ",
    "using ",
)


def clean_project_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_lines = []

    for line in text.split("\n"):
        line = BULLET_PATTERN.sub("", line).strip()

        # Remove remaining standalone private-use bullet characters.
        line = re.sub(r"^[\uf06c\uF0B7]+\s*", "", line).strip()

        line = re.sub(r"[ \t]+", " ", line)

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


# ============================================================
# PROJECT SECTION
# ============================================================

def extract_project_section(text: str):
    if not text:
        return None

    text = clean_project_text(text)

    return text if text else None


# ============================================================
# PROJECT HEADING DETECTION
# ============================================================

MONTH_PATTERN = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
    r"Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)


def is_project_heading(line: str) -> bool:
    if not line:
        return False

    line = clean_project_text(line).strip()

    if not line:
        return False

    # Metadata cannot be a project heading.
    if METADATA_PATTERN.match(line):
        return False

    # A project heading should not look like a description sentence.
    if line.casefold().startswith(DESCRIPTION_STARTERS):
        return False

    # Reject standalone bullet symbols and punctuation.
    if not re.search(r"[A-Za-z0-9]", line):
        return False

    # Reject very long lines.
    if len(line.split()) > 20:
        return False

    # Strong signal: project heading with a dated bracket.
    if re.search(
        r"\[[^\]]*(?:19|20)\d{2}[^\]]*\]\s*$",
        line,
    ):
        return True

    # Strong signal: explicit month/year range.
    if re.search(
        rf"\b(?:{MONTH_PATTERN})\s*[-–—]\s*"
        rf"(?:{MONTH_PATTERN})?\s*,?\s*(?:19|20)\d{{2}}\b",
        line,
        re.IGNORECASE,
    ):
        return True

    # Short uppercase titles are supported only when they look
    # like standalone titles rather than arbitrary uppercase text.
    if (
        line == line.upper()
        and 1 <= len(line.split()) <= 10
        and not re.search(r"[.!?]$", line)
        and len(line) >= 4
    ):
        return True

    return False


# ============================================================
# PROJECT NAME
# ============================================================

def extract_project_name(text: str):
    if not text:
        return None

    lines = [
        line.strip()
        for line in clean_project_text(text).splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    name = lines[0]

    name = re.sub(
        r",?\s*\[[^\]]*(?:19|20)\d{2}[^\]]*\]\s*$",
        "",
        name,
    )

    name = name.strip(" ,.-:")

    if not re.search(r"[A-Za-z0-9]", name):
        return None

    return name or None


# ============================================================
# PROJECT DESCRIPTION
# ============================================================

def extract_project_description(text: str):
    if not text:
        return None

    lines = [
        line.strip()
        for line in clean_project_text(text).splitlines()
        if line.strip()
    ]

    if len(lines) <= 1:
        return None

    description_lines = []

    for line in lines[1:]:

        clean_line = line.strip()

        if not clean_line:
            continue

        if METADATA_PATTERN.match(clean_line):
            continue

        if clean_line.casefold() in {
            "github",
            "github repository",
            "personal project",
            "ieee conference publication",
        }:
            continue

        if not re.search(r"[A-Za-z0-9]", clean_line):
            continue

        description_lines.append(clean_line)

    if not description_lines:
        return None

    return re.sub(
        r"\s+",
        " ",
        " ".join(description_lines),
    ).strip()


# ============================================================
# TECHNOLOGY EXTRACTION
# ============================================================

KNOWN_TECHNOLOGIES = [
    "Python",
    "JavaScript",
    "Java Script",
    "TypeScript",
    "Java",
    "C++",
    "C#",
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express",
    "FastAPI",
    "Flask",
    "Django",
    "Streamlit",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQL",
    "NoSQL",
    "Oracle",
    "SQLite",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Scikit-learn",
    "CountVectorizer",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "OpenCV",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "CNN",
    "RNN",
    "LangChain",
    "FAISS",
    "LangGraph",
    "LLM",
    "Docker",
    "Git",
    "GitHub",
    "AWS",
    "Azure",
    "Power BI",
    "Tableau",
    "Advanced Excel",
    "Jupyter Notebook",
    "Hadoop",
    "Spark",
    "Random Forest",
    "Java",
]


def extract_project_technologies(text: str):
    if not text:
        return []

    technologies = []

    def add_technology(value):
        value = value.strip(" .")

        if value and value.casefold() not in {
            item.casefold() for item in technologies
        }:
            technologies.append(value)

    # Extract explicitly declared technologies first.
    for line in clean_project_text(text).splitlines():

        match = re.match(
            r"^\s*(?:Tools?|Technologies|Technology|Tech Stack|Tools Used)\s*:\s*(.+)$",
            line,
            re.IGNORECASE,
        )

        if match:
            values = re.split(r"[,;|]", match.group(1))

            for value in values:
                add_technology(value)

    # Detect known technologies in project content.
    sorted_technologies = sorted(
        set(KNOWN_TECHNOLOGIES),
        key=len,
        reverse=True,
    )

    for technology in sorted_technologies:

        normalized = re.escape(technology).replace(
            r"\ ",
            r"\s+",
        )

        pattern = rf"(?<!\w){normalized}(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            add_technology(technology)

    return technologies


# ============================================================
# PROJECT ENTRY EXTRACTION
# ============================================================

def extract_project_entries(text: str):
    if not text:
        return []

    text = clean_project_text(text)

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

        if is_project_heading(line):

            if current_entry:
                entries.append("\n".join(current_entry))

            current_entry = [line]

        else:
            if current_entry:
                current_entry.append(line)
            else:
                # Preserve content before the first recognized heading.
                current_entry.append(line)

    if current_entry:
        entries.append("\n".join(current_entry))

    # Remove entries that have no meaningful project name.
    valid_entries = []

    for entry in entries:
        project_name = extract_project_name(entry)

        if project_name:
            valid_entries.append(entry)

    return valid_entries


# ============================================================
# MASTER PROJECT PARSER
# ============================================================

def parse_projects(text: str):

    section = extract_project_section(text)

    if not section:
        return []

    raw_entries = extract_project_entries(section)

    parsed_projects = []

    for entry in raw_entries:

        project_name = extract_project_name(entry)

        if not project_name:
            continue

        parsed_projects.append({
            "raw_text": entry,
            "project_name": project_name,
            "description": extract_project_description(entry),
            "technologies": extract_project_technologies(entry),
            "github_url": extract_github_url(entry),
        })

    return parsed_projects
