import re


# ============================================================
# CLEAN PROJECT TEXT
# ============================================================

def clean_project_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r", "\n")

    # Normalize spaces but preserve line breaks
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


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

def is_project_heading(line: str) -> bool:

    if not line:
        return False

    line = re.sub(
        r"^[➢•\-]+\s*",
        "",
        line
    ).strip()

    upper_line = line.upper()

    # --------------------------------------------------------
    # Known project-name patterns from resume
    # --------------------------------------------------------

    known_project_patterns = [

        r"^JOB TRACKER APP$",

        r"^ARTIFICIAL INTELLIGENCE\s*-\s*AN OVERVIEW",

        r"^VIDEO TRANSCRIPT SUMMARIZER$",
    ]

    for pattern in known_project_patterns:

        if re.search(
            pattern,
            line,
            re.IGNORECASE
        ):
            return True

    # --------------------------------------------------------
    # Generic project heading patterns
    # --------------------------------------------------------

    if (
        upper_line.endswith(" APP")
        or upper_line.endswith(" PROJECT")
        or upper_line.endswith(" SYSTEM")
        or upper_line.endswith(" APPLICATION")
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
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    return lines[0]


# ============================================================
# PROJECT DESCRIPTION
# ============================================================

def extract_project_description(text: str):

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

        # Skip technology declaration
        if re.match(
            r"^(technologies|technology|tech stack|tools used)\s*:",
            line,
            re.IGNORECASE
        ):
            continue

        description_lines.append(line)

    if not description_lines:
        return None

    return " ".join(description_lines)


# ============================================================
# TECHNOLOGY EXTRACTION
# ============================================================

def extract_project_technologies(text: str):

    if not text:
        return []

    technologies = [

        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "C",
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

        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "SQL",
        "NoSQL",

        "Pandas",
        "NumPy",
        "Matplotlib",
        "Seaborn",
        "Scikit-learn",

        "TensorFlow",
        "PyTorch",
        "Keras",
        "OpenCV",

        "LangChain",
        "FAISS",

        "Docker",
        "Git",
        "GitHub",

        "AWS",
        "Azure",

        "Power BI",
        "Tableau",

        "Hadoop",
        "Spark"
    ]

    found = []

    for technology in technologies:

        pattern = rf"(?<!\w){re.escape(technology)}(?!\w)"

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found.append(technology)

    return found


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

    # Common project-title indicators
    project_title_keywords = [
        "app",
        "application",
        "system",
        "project",
        "summarizer",
        "tracker",
        "platform",
        "website",
        "portal",
        "analyzer",
        "analysis",
        "prediction",
        "overview"
    ]

    for line in lines:

        clean_line = re.sub(
            r"^[➢•\-]+\s*",
            "",
            line
        ).strip()

        upper_line = clean_line.upper()

        # ----------------------------------------------------
        # Detect likely project heading
        # ----------------------------------------------------

        is_heading = False

        # ALL CAPS headings
        if clean_line == clean_line.upper() and len(clean_line.split()) <= 15:
            is_heading = True

        # Known project title patterns
        if any(
            keyword in clean_line.lower()
            for keyword in project_title_keywords
        ):
            if len(clean_line.split()) <= 15:
                is_heading = True

        # ----------------------------------------------------
        # Prevent description sentences from becoming headings
        # ----------------------------------------------------

        description_starters = [
            "developed",
            "designed",
            "created",
            "built",
            "implemented",
            "utilized",
            "used",
            "provided",
            "supports",
            "the",
            "this",
            "job tracker app is"
        ]

        if any(
            clean_line.lower().startswith(word)
            for word in description_starters
        ):
            is_heading = False

        # ----------------------------------------------------
        # Start new project
        # ----------------------------------------------------

        if is_heading and current_entry:

            entries.append(
                "\n".join(current_entry)
            )

            current_entry = []

        current_entry.append(clean_line)

    # Add final project
    if current_entry:

        entries.append(
            "\n".join(current_entry)
        )

    return entries

    # --------------------------------------------------------
    # Add final project
    # --------------------------------------------------------

    if current_entry:

        entries.append(
            "\n".join(current_entry)
        )

    return entries


# ============================================================
# MASTER PROJECT PARSER
# ============================================================

def parse_projects(text: str):

    section = extract_project_section(text)

    if not section:
        return []

    raw_entries = extract_project_entries(
        section
    )

    parsed_projects = []

    for entry in raw_entries:

        parsed_projects.append(
            {
                "raw_text": entry,

                "project_name": extract_project_name(
                    entry
                ),

                "description": extract_project_description(
                    entry
                ),

                "technologies": extract_project_technologies(
                    entry
                )
            }
        )

    return parsed_projects