import re
from typing import List, Dict, Optional


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize education-related text so that variations such as:

        B.Tech
        B-Tech
        B_Tech
        Bachelor's

    can be compared consistently.
    """

    if not text:
        return ""

    text = str(text).lower().strip()

    # Normalize separators
    text = text.replace("&", " and ")
    text = text.replace("_", " ")
    text = text.replace("-", " ")

    # Normalize common degree punctuation
    text = text.replace("'", "")

    # Remove punctuation
    text = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# EDUCATION CONCEPTS
# ============================================================

EDUCATION_CONCEPTS = {

    "computer science": {
        "cse",
        "computer science",
        "computer science engineering",
        "computer engineering",
        "software engineering",
        "information science",
        "information technology"
    },

    "artificial intelligence": {
        "ai",
        "artificial intelligence",
        "artificial intelligence engineering",
        "machine learning",
        "ai ml",
        "aiml"
    },

    "data science": {
        "ds",
        "data science",
        "data science engineering",
        "data analytics",
        "data analysis"
    },

    "computer engineering": {
        "computer engineering",
        "computer science",
        "cse",
        "software engineering"
    },

    "information technology": {
        "it",
        "information technology",
        "information science"
    },

    "software engineering": {
        "software engineering",
        "computer science",
        "cse"
    }
}


# ============================================================
# DEGREE ALIASES
# ============================================================

DEGREE_ALIASES = {

    "btech": {
        "bachelor",
        "bachelor of technology",
        "b tech",
        "btech"
    },

    "be": {
        "bachelor",
        "bachelor of engineering",
        "b e",
        "be"
    },

    "bsc": {
        "bachelor",
        "bachelor of science",
        "b sc",
        "bsc"
    },

    "mtech": {
        "master",
        "master of technology",
        "m tech",
        "mtech"
    },

    "me": {
        "master",
        "master of engineering",
        "m e",
        "me"
    },

    "msc": {
        "master",
        "master of science",
        "m sc",
        "msc"
    }
}


# ============================================================
# BACHELOR FIELD PATTERNS
# ============================================================

BACHELOR_FIELD_PATTERNS = {
    "cse",
    "computer science",
    "computer science engineering",
    "computer engineering",
    "information technology",
    "information science",
    "software engineering",
    "artificial intelligence",
    "machine learning",
    "data science",
    "data science engineering",
    "data analytics",
}


# ============================================================
# NORMALIZE EDUCATION ENTRY
# ============================================================

def normalize_education_entry(
    education: Dict
) -> str:

    if not isinstance(
        education,
        dict
    ):
        return ""

    parts = []

    for key in ("program", "degree", "field"):
        value = education.get(key)
        if value:
            parts.append(str(value))

    # Fallback only when structured qualification fields are absent.
    if not parts and education.get("raw_text"):
        parts.append(str(education["raw_text"]))

    return normalize_text(" ".join(parts))

# ============================================================
# DEGREE AND FIELD RECOGNITION
# ============================================================

DEGREE_PATTERNS = {
    "btech": [
        r"\bb\s*\.?\s*tech\b",
        r"\bbachelor of technology\b",
    ],
    "be": [
        r"\bb\s*\.?\s*e\b",
        r"\bbachelor of engineering\b",
    ],
    "bsc": [
        r"\bb\s*\.?\s*sc\b",
        r"\bbachelor of science\b",
    ],
    "bca": [
        r"\bb\s*\.?\s*c\s*\.?\s*a\b",
        r"\bbachelor of computer applications\b",
    ],
    "bcom": [
        r"\bb\s*\.?\s*com\b",
        r"\bbachelor of commerce\b",
    ],
    "ba": [
        r"\bb\s*\.?\s*a\b",
        r"\bbachelor of arts\b",
    ],
    "mtech": [
        r"\bm\s*\.?\s*tech\b",
        r"\bmaster of technology\b",
    ],
    "mba": [
        r"\bm\s*\.?\s*b\s*\.?\s*a\b",
        r"\bmaster of business administration\b",
    ],
}

FIELD_PATTERNS = {
    "computer_science": [
        r"\bcse\b",
        r"\bcomputer science\b",
        r"\bcomputer engineering\b",
        r"\bsoftware engineering\b",
    ],
    "artificial_intelligence": [
        r"\bai\s*and\s*ml\b",
        r"\bai\s*ml\b",
        r"\bartificial intelligence\b",
        r"\bmachine learning\b",
        r"\baiml\b",
    ],
    "data_science": [
        r"\bdata science\b",
        r"\bdata analytics\b",
        r"\bdata analysis\b",
    ],
    "information_technology": [
        r"\binformation technology\b",
        r"\binformation science\b",
        r"\bit\b",
    ],
    "commerce": [
        r"\bcommerce\b",
        r"\bbcom\b",
    ],
    "business": [
        r"\bbusiness administration\b",
        r"\bmanagement\b",
    ],
    "arts": [
        r"\barts\b",
        r"\bhumanities\b",
    ],
}

RELATED_FIELDS = {
    "computer_science": {
        "computer_science",
        "artificial_intelligence",
        "data_science",
        "information_technology",
    },
}


def detect_degree(text: str) -> Optional[str]:
    text = normalize_text(text)

    for degree, patterns in DEGREE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return degree

    return None


def detect_field(text: str) -> Optional[str]:
    text = normalize_text(text)

    for field, patterns in FIELD_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return field

    return None


def extract_requirement_field(
    requirement: str
) -> Optional[str]:

    return detect_field(requirement)


def is_bachelor_degree(degree: Optional[str]) -> bool:
    return degree in {
        "btech",
        "be",
        "bsc",
        "bca",
        "bcom",
        "ba",
    }


# ============================================================
# EXACT EDUCATION MATCH
# ============================================================

def exact_education_match(
    requirement: str,
    candidate_text: str
) -> bool:

    requirement_normalized = normalize_text(
        requirement
    )

    candidate_normalized = normalize_text(
        candidate_text
    )

    if not requirement_normalized:
        return False

    if not candidate_normalized:
        return False

    candidate_words = set(
        candidate_normalized.split()
    )

    requirement_words = set(
        requirement_normalized.split()
    )

    return requirement_words.issubset(
        candidate_words
    )


# ============================================================
# INFER DEGREE LEVEL
# ============================================================

def infer_degree_level(
    candidate_text: str
) -> Optional[str]:
    """
    Infer whether an education entry represents a
    bachelor's-level qualification.

    This is a fallback for cases where the parser did not
    explicitly extract B.Tech / B.E. / B.Sc.

    Example:

        CSE_AI&DS
        CSE
        Computer Science Engineering

    can be treated as bachelor-level programs when the
    resume does not explicitly expose the degree name.
    """

    degree = detect_degree(
        candidate_text
    )

    if is_bachelor_degree(degree):
        return "bachelor"

    return None

    # --------------------------------------------------------
    # Explicit bachelor's indicators
    # --------------------------------------------------------



# ============================================================
# RELATED EDUCATION MATCH
# ============================================================

def related_education_match(
    requirement: str,
    candidate_text: str
) -> Optional[str]:

    requirement_degree = detect_degree(requirement)
    candidate_degree = detect_degree(candidate_text)

    requirement_field = extract_requirement_field(requirement)
    candidate_field = detect_field(candidate_text)

    # Related technical qualifications for Computer Science.
    if requirement_field == "computer_science":

        if candidate_degree == "be":
            if candidate_field in RELATED_FIELDS["computer_science"]:
                return "related"

        if candidate_degree == "bca":
            return "related"

    # Related fields for an explicitly technical bachelor's degree.
    if (
        requirement_degree in ("btech", "be")
        and candidate_degree == "bca"
    ):
        return "related"

    # Generic bachelor's-level requirement.
    normalized_requirement = normalize_text(requirement)

    generic_bachelor = normalized_requirement in {
        "bachelor",
        "bachelors",
        "bachelor degree",
        "bachelors degree",
        "undergraduate degree",
    }

    if generic_bachelor and is_bachelor_degree(candidate_degree):
        return "related"

    return None


# ============================================================
# MATCH SINGLE EDUCATION REQUIREMENT
# ============================================================

def match_education_requirement(
    requirement: str,
    education_entries: List[Dict]
) -> Dict:

    base_result = {
        "requirement": requirement,
        "status": "unknown",
        "confidence": 0.0,
        "evidence": []
    }

    if not requirement or not education_entries:
        return base_result

    requirement_degree = detect_degree(requirement)
    requirement_field = extract_requirement_field(requirement)

    normalized_requirement = normalize_text(requirement)

    generic_bachelor = normalized_requirement in {
        "bachelor",
        "bachelors",
        "bachelor degree",
        "bachelors degree",
        "undergraduate degree",
    }

    confirmed_unrelated = []

    for education in education_entries:

        candidate_text = normalize_education_entry(education)

        if not candidate_text:
            continue

        candidate_degree = detect_degree(candidate_text)
        candidate_field = detect_field(candidate_text)

        evidence = [candidate_text]

        # Generic bachelor's requirement.
        if generic_bachelor:
            if is_bachelor_degree(candidate_degree):
                return {
                    "requirement": requirement,
                    "status": "exact",
                    "confidence": 1.0,
                    "evidence": evidence
                }

            continue

        # A qualification with no identifiable degree is insufficient.
        if not candidate_degree:
            continue

        # A field-specific requirement.
        if requirement_field:

            if candidate_field in RELATED_FIELDS.get(
                requirement_field, {requirement_field}
            ):

                if (
                    requirement_degree is None
                    or candidate_degree == requirement_degree
                ):
                    return {
                        "requirement": requirement,
                        "status": "exact",
                        "confidence": 1.0,
                        "evidence": evidence
                    }

            related = related_education_match(
                requirement,
                candidate_text
            )

            if related:
                return {
                    "requirement": requirement,
                    "status": "related",
                    "confidence": 0.85,
                    "evidence": evidence
                }

            # A recognized degree in a clearly unrelated field.
            if candidate_field:
                confirmed_unrelated.append(candidate_text)

            elif candidate_degree in ("bcom", "ba", "mba"):
                confirmed_unrelated.append(candidate_text)

            continue

        # Degree-specific requirement without a field.
        if requirement_degree:

            if candidate_degree == requirement_degree:
                return {
                    "requirement": requirement,
                    "status": "exact",
                    "confidence": 1.0,
                    "evidence": evidence
                }

            related = related_education_match(
                requirement,
                candidate_text
            )

            if related:
                return {
                    "requirement": requirement,
                    "status": "related",
                    "confidence": 0.85,
                    "evidence": evidence
                }

            confirmed_unrelated.append(candidate_text)

    if confirmed_unrelated:
        return {
            "requirement": requirement,
            "status": "not_matched",
            "confidence": 0.0,
            "evidence": confirmed_unrelated
        }

    return base_result


# ============================================================
# MATCH MULTIPLE EDUCATION REQUIREMENTS
# ============================================================

def match_education_requirements(
    requirements: List[str],
    education_entries: List[Dict]
) -> List[Dict]:

    if not requirements:
        return []

    results = []

    for requirement in requirements:

        result = match_education_requirement(
            requirement,
            education_entries
        )

        results.append(
            result
        )

    return results


# ============================================================
# MASTER EDUCATION MATCH
# ============================================================

def match_education(
    resume: dict,
    required_education: List[str]
) -> Dict:

    if isinstance(required_education, str):
        required_education = [required_education]

    if not required_education:
        return {
            "status": "not_required",
            "matched": [],
            "not_matched": [],
            "unknown": []
        }

    if not resume:
        return {
            "status": "unknown",
            "matched": [],
            "not_matched": [],
            "unknown": required_education
        }

    education_entries = resume.get("education", [])

    if not education_entries:
        return {
            "status": "unknown",
            "matched": [],
            "not_matched": [],
            "unknown": required_education
        }

    results = match_education_requirements(
        required_education,
        education_entries
    )

    matched = []
    not_matched = []
    unknown = []

    for result in results:

        status = result.get("status")

        if status in ("exact", "related"):
            matched.append(result)

        elif status == "not_matched":
            not_matched.append(result)

        else:
            unknown.append(result)

    if matched:
        overall_status = "matched"
    elif not_matched and not unknown:
        overall_status = "not_matched"
    else:
        overall_status = "unknown"

    return {
        "status": overall_status,
        "matched": matched,
        "not_matched": not_matched,
        "unknown": unknown
    }