import re


# ============================================================
# CLEAN PROJECT TEXT
# ============================================================

def clean_project_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove PDF bullet characters while preserving text
    text = re.sub(
        r"^[➢•▪◦●○■□]+\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Normalize spaces inside lines
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
        r"^[➢•▪◦●○■□\-]+\s*",
        "",
        line
    ).strip()

    if not line:
        return False

    upper_line = line.upper()

    # --------------------------------------------------------
    # Ignore obvious description sentences
    # --------------------------------------------------------

    description_starters = (
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
        "integrating ",
        "allows ",
        "allows users ",
    )

    if line.lower().startswith(
        description_starters
    ):
        return False

    # --------------------------------------------------------
    # Technology / metadata lines are NOT headings
    # --------------------------------------------------------

    if re.match(
        r"^(technologies|technology|tech stack|tools used|tools)\s*:",
        line,
        re.IGNORECASE
    ):
        return False

    # --------------------------------------------------------
    # Known structural patterns
    #
    # These are patterns, NOT specific project names.
    # --------------------------------------------------------

    project_patterns = [

        # Something APP
        r".+\s+APP$",

        # Something PROJECT
        r".+\s+PROJECT$",

        # Something SYSTEM
        r".+\s+SYSTEM$",

        # Something APPLICATION
        r".+\s+APPLICATION$",

        # Something PLATFORM
        r".+\s+PLATFORM$",

        # Something PORTAL
        r".+\s+PORTAL$",

        # Something SUMMARIZER
        r".+\s+SUMMARIZER$",

        # AI project titles
        r"^ARTIFICIAL INTELLIGENCE\s*[-–—:]\s*.+$",

    ]

    for pattern in project_patterns:

        if re.fullmatch(
            pattern,
            line,
            re.IGNORECASE
        ):
            return True

    # --------------------------------------------------------
    # ALL CAPS heading
    #
    # Example:
    #
    # JOB TRACKER APP
    # VIDEO TRANSCRIPT SUMMARIZER
    # ARTIFICIAL INTELLIGENCE-...
    #
    # But avoid long paragraphs.
    # --------------------------------------------------------

    if (
        line == upper_line
        and len(line.split()) <= 15
        and not re.search(
            r"[.!?,]$",
            line
        )
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

    name = lines[0]

    name = re.sub(
        r"^[➢•▪◦●○■□\-]+\s*",
        "",
        name
    ).strip()

    return name if name else None


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

        clean_line = re.sub(
            r"^[➢•▪◦●○■□\-]+\s*",
            "",
            line
        ).strip()

        if not clean_line:
            continue

        # ----------------------------------------------------
        # Skip technology declarations
        # ----------------------------------------------------

        if re.match(
            r"^(technologies|technology|tech stack|tools used|tools)\s*:",
            clean_line,
            re.IGNORECASE
        ):
            continue

        description_lines.append(
            clean_line
        )

    if not description_lines:
        return None

    return " ".join(
        description_lines
    )


# ============================================================
# TECHNOLOGY EXTRACTION
# ============================================================

def extract_project_technologies(text: str):

    if not text:
        return []

    technologies = [

        # Programming
        "Python",
        "Java",
        "JavaScript",
        "Java Script",
        "TypeScript",
        "C",
        "C++",
        "C#",

        # Web
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

        # Databases
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "SQL",
        "NoSQL",
        "Oracle",
        "SQLite",

        # Data
        "Pandas",
        "NumPy",
        "Matplotlib",
        "Seaborn",
        "Scikit-learn",
        "CountVectorizer",

        # ML / AI
        "TensorFlow",
        "PyTorch",
        "Keras",
        "OpenCV",
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",

        # GenAI
        "LangChain",
        "FAISS",

        # DevOps
        "Docker",
        "Git",
        "GitHub",

        # Cloud
        "AWS",
        "Azure",

        # Analytics
        "Power BI",
        "Tableau",
        "Advanced Excel",
        "Jupyter Notebook",

        # Big Data
        "Hadoop",
        "Spark"
    ]

    found = []

    # Sort longer names first.
    #
    # Example:
    # "Java Script" should be checked before
    # "Java".
    #
    technologies = sorted(
        technologies,
        key=len,
        reverse=True
    )

    for technology in technologies:

        normalized_technology = technology.replace(
            " ",
            r"\s+"
        )

        pattern = (
            rf"(?<!\w)"
            rf"{normalized_technology}"
            rf"(?!\w)"
        )

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found.append(
                technology
            )

    return found


# ============================================================
# PROJECT ENTRY EXTRACTION
# ============================================================

def extract_project_entries(text: str):

    if not text:
        return []

    text = clean_project_text(
        text
    )

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
            r"^[➢•▪◦●○■□\-]+\s*",
            "",
            line
        ).strip()

        if not clean_line:
            continue

        # ----------------------------------------------------
        # Detect heading
        # ----------------------------------------------------

        heading = is_project_heading(
            clean_line
        )

        # ----------------------------------------------------
        # Start a new project
        # ----------------------------------------------------

        if heading:

            if current_entry:

                entries.append(
                    "\n".join(
                        current_entry
                    )
                )

            current_entry = [
                clean_line
            ]

        else:

            current_entry.append(
                clean_line
            )

    # --------------------------------------------------------
    # Add final project
    # --------------------------------------------------------

    if current_entry:

        entries.append(
            "\n".join(
                current_entry
            )
        )

    return entries


# ============================================================
# MASTER PROJECT PARSER
# ============================================================

def parse_projects(text: str):

    section = extract_project_section(
        text
    )

    if not section:
        return []

    raw_entries = extract_project_entries(
        section
    )

    parsed_projects = []

    for entry in raw_entries:

        parsed_projects.append(
            {
                "raw_text":
                    entry,

                "project_name":
                    extract_project_name(
                        entry
                    ),

                "description":
                    extract_project_description(
                        entry
                    ),

                "technologies":
                    extract_project_technologies(
                        entry
                    )
            }
        )

    return parsed_projects