import re

# ==========================================
# CLEANING
# ==========================================

def clean_personal_text(text: str) -> str:
    """
    Clean the personal section before extraction.
    """

    # Standardize line endings
    text = text.replace("\r", "\n")

    # Remove multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove empty lines
    text = re.sub(r"\n+", "\n", text)

    # Standardize separators
    text = text.replace("|", " | ")

    return text.strip()


# ==========================================
# NAME
# ==========================================

def extract_name(text: str):

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        return line

    return None


def validate_name(name):

    if not name:
        return None

    # Ignore names that are too short
    if len(name) < 3:
        return None

    # Ignore lines containing numbers
    if re.search(r"\d", name):
        return None

    return name

def normalize_name(name):

    if not name:
        return None

    name = " ".join(name.split())

    return name.title()


# ==========================================
# EMAIL
# ==========================================

def extract_email(text: str):
     pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

     match = re.search(pattern, text)

     if match:
        return match.group()

     return None

def validate_email(email):
    if not email:
        return None

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(pattern, email):
        return email

    return None


def normalize_email(email):

    if not email:
        return None

    return email.strip().lower()

# ==========================================
# PHONE
# ==========================================

def extract_phone(text: str):
    """
    Extract phone number.
    """

    pattern = (
        r"(?:\+91[\-\s]?)?"
        r"(?:\d{10}|\d{5}[\-\s]?\d{5})"
    )

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def validate_phone(phone):
    """
    Validate phone number.
    """

    if not phone:
        return None

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        return phone

    if len(digits) == 12 and digits.startswith("91"):
        return phone

    return None


def normalize_phone(phone):
    """
    Normalize phone number.
    """

    if not phone:
        return None

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        return "+91" + digits

    if len(digits) == 12:
        return "+" + digits

    return phone

# ==========================================
# LINKEDIN
# ==========================================

def extract_linkedin(text: str):

    if not text:
        return None

    pattern = (
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"linkedin\.com/"
        r"(?:in|company)/"
        r"[A-Za-z0-9_-]+/?"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group().strip()

    return None


def validate_linkedin(linkedin):

    if not linkedin:
        return None

    if not re.search(
        r"linkedin\.com/(in|company)/",
        linkedin,
        re.IGNORECASE
    ):
        return None

    return linkedin


# ==========================================
# GITHUB
# ==========================================

def extract_github(text: str):

    if not text:
        return None

    pattern = (
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"github\.com/"
        r"[A-Za-z0-9-]+/?"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group().strip()

    return None

def validate_github(github):

    if not github:
        return None

    if not re.search(
        r"github\.com/[A-Za-z0-9-]+",
        github,
        re.IGNORECASE
    ):
        return None

    return github


# ==========================================
# PORTFOLIO
# ==========================================

def extract_portfolio(text: str):

    if not text:
        return None

    pattern = (
        r"https?://"
        r"(?!www\.)"
        r"(?!linkedin\.com)"
        r"(?!github\.com)"
        r"(?![\w.-]*linkedin\.com)"
        r"(?![\w.-]*github\.com)"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        r"(?:/[^\s|]*)?"
    )

    matches = re.findall(pattern, text, re.IGNORECASE)

    if matches:
        return matches[0].rstrip(".,;)")

    return None


# ==========================================
# LOCATION
# ==========================================

# ==========================================
# LOCATION
# ==========================================

def extract_location(text: str):
    """
    Extract location from the personal section.
    Expected format:
    Name
    City, State, PIN | Phone | Email
    """

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    # Usually the location is on the second line.
    for line in lines[1:]:

        # Extract the first field before the pipe.
        location = line.split("|")[0].strip()

        if not location:
            continue

        # Ignore fields containing email or phone information.
        if re.search(r"@|\d{10}", location):
            continue

        # Location should contain a comma.
        if "," in location:
            return location

    return None

def normalize_location(location):
    """
    Normalize extracted location.
    """

    if not location:
        return None

    location = " ".join(location.split())

    location = location.replace(" ,", ",")

    return location.strip()


# ==========================================
# MASTER PARSER
# ==========================================

def parse_personal(text: str):

    text = clean_personal_text(text)

    name = normalize_name(
        validate_name(
            extract_name(text)
        )
    )

    email = normalize_email(
        validate_email(
            extract_email(text)
        )
    )

    phone = normalize_phone(
        validate_phone(
            extract_phone(text)
        )
    )

    linkedin = validate_linkedin(
        extract_linkedin(text)
    )

    github = validate_github(
        extract_github(text)
    )

    portfolio = extract_portfolio(text)

    location = normalize_location(
        extract_location(text)
    )

    return {

        "name": name,

        "email": email,

        "phone": phone,

        "linkedin": linkedin,

        "github": github,

        "portfolio": portfolio,

        "location": location
    }