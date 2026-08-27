import re


# ============================================================
# CLEAN JOB DESCRIPTION TEXT
# ============================================================

def clean_job_description_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize spaces while preserving line breaks
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# JOB DESCRIPTION SECTION
# ============================================================

def extract_job_description_section(text: str):

    if not text:
        return None

    text = clean_job_description_text(text)

    return text if text else None


# ============================================================
# JOB TITLE EXTRACTION
# ============================================================

def extract_job_title(text: str):

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    # --------------------------------------------------------
    # Look for common job-title labels
    # --------------------------------------------------------

    for line in lines:

        match = re.match(
            r"^(job title|position|role)\s*:\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:

            return match.group(2).strip()

    # --------------------------------------------------------
    # Common job-title keywords
    # --------------------------------------------------------

    job_title_keywords = [
        "software engineer",
        "software developer",
        "data scientist",
        "data analyst",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "artificial intelligence engineer",
        "backend developer",
        "frontend developer",
        "full stack developer",
        "web developer",
        "devops engineer",
        "cloud engineer",
        "business analyst",
        "product manager",
        "project manager"
    ]

    for line in lines[:10]:

        lower_line = line.lower()

        for title in job_title_keywords:

            if title in lower_line:

                return line.strip()

    return None


# ============================================================
# SKILL DATABASE
#
# This is intentionally kept separate so we can expand it
# later without changing the parser logic.
# ============================================================

KNOWN_SKILLS = [

    # Programming languages
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "C#",
    "Go",
    "Rust",
    "PHP",
    "Ruby",
    "Kotlin",
    "Swift",

    # Web
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express",

    # Backend
    "FastAPI",
    "Flask",
    "Django",
    "Spring",
    "Spring Boot",

    # Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Oracle",
    "Redis",
    "Cassandra",
    "NoSQL",

    # Data Science
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Scikit-learn",
    "Scikit Learn",

    # Machine Learning / AI
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "OpenCV",

    # Generative AI
    "Generative AI",
    "LLM",
    "Large Language Models",
    "LangChain",
    "LlamaIndex",
    "RAG",
    "FAISS",

    # Cloud
    "AWS",
    "Azure",
    "Google Cloud",
    "GCP",

    # DevOps
    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "Jenkins",

    # Big Data
    "Hadoop",
    "Spark",
    "Kafka",

    # BI
    "Power BI",
    "Tableau",

    # Other
    "Excel",
    "Statistics",
    "Data Analysis",
    "Data Visualization"
]


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_job_skills(text: str):

    if not text:
        return []

    found_skills = []

    for skill in KNOWN_SKILLS:

        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found_skills.append(skill)

    return found_skills


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_required_experience(text: str):

    if not text:
        return None

    patterns = [

        # 3+ years
        r"(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",

        # minimum 3 years
        r"(?:minimum|min\.?|at least)\s*(\d+)\s*(?:years?|yrs?)",

        # 3 years experience required
        r"(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?experience\s*(?:required|preferred)?"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return {
                "minimum_years": int(
                    match.group(1)
                )
            }

    return None


# ============================================================
# EDUCATION REQUIREMENT EXTRACTION
# ============================================================

def extract_education_requirements(text: str):

    if not text:
        return []

    education_keywords = [

        "bachelor",
        "bachelor's",
        "b.tech",
        "btech",
        "b.e",
        "be ",
        "master",
        "master's",
        "m.tech",
        "mtech",
        "m.e",
        "me ",
        "mba",
        "phd",
        "computer science",
        "information technology",
        "data science",
        "artificial intelligence"
    ]

    found = []

    lower_text = text.lower()

    for keyword in education_keywords:

        if keyword in lower_text:

            found.append(
                keyword.strip()
            )

    return list(
        dict.fromkeys(found)
    )


# ============================================================
# REQUIRED / PREFERRED SKILLS
# ============================================================

def classify_skill_requirements(text: str):

    if not text:
        return {
            "required_skills": [],
            "preferred_skills": []
        }

    required_skills = []
    preferred_skills = []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines:

        lower_line = line.lower()

        line_skills = extract_job_skills(
            line
        )

        if not line_skills:
            continue

        # ----------------------------------------------------
        # Preferred / nice-to-have language
        # ----------------------------------------------------

        is_preferred = any(
            phrase in lower_line
            for phrase in [
                "preferred",
                "nice to have",
                "nice-to-have",
                "plus",
                "bonus",
                "desirable",
                "optional"
            ]
        )

        if is_preferred:

            preferred_skills.extend(
                line_skills
            )

        else:

            required_skills.extend(
                line_skills
            )

    return {
        "required_skills": list(
            dict.fromkeys(
                required_skills
            )
        ),

        "preferred_skills": list(
            dict.fromkeys(
                preferred_skills
            )
        )
    }


# ============================================================
# MASTER JOB DESCRIPTION PARSER
# ============================================================

def parse_job_description(text: str):

    section = extract_job_description_section(
        text
    )

    if not section:

        return {
            "raw_text": None,
            "job_title": None,
            "required_skills": [],
            "preferred_skills": [],
            "experience": None,
            "education": []
        }

    skill_requirements = classify_skill_requirements(
        section
    )

    return {

        "raw_text": section,

        "job_title": extract_job_title(
            section
        ),

        "required_skills":
            skill_requirements[
                "required_skills"
            ],

        "preferred_skills":
            skill_requirements[
                "preferred_skills"
            ],

        "experience":
            extract_required_experience(
                section
            ),

        "education":
            extract_education_requirements(
                section
            )
    }