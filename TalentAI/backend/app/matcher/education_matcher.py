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

    for key in [
        "institution",
        "program",
        "degree",
        "field",
        "location"
    ]:

        value = education.get(
            key
        )

        if value:

            parts.append(
                str(value)
            )

    return normalize_text(
        " ".join(parts)
    )


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

    normalized = normalize_text(
        candidate_text
    )

    if not normalized:
        return None

    # --------------------------------------------------------
    # Explicit bachelor's indicators
    # --------------------------------------------------------

    bachelor_indicators = {
        "btech",
        "b tech",
        "be",
        "b e",
        "bsc",
        "b sc",
        "bachelor",
        "bachelors",
        "bachelor of technology",
        "bachelor of engineering",
        "bachelor of science"
    }

    words = set(
        normalized.split()
    )

    if words.intersection(
        bachelor_indicators
    ):
        return "bachelor"

    # --------------------------------------------------------
    # Undergraduate field indicators
    # --------------------------------------------------------

    for field in BACHELOR_FIELD_PATTERNS:

        field_normalized = normalize_text(
            field
        )

        if field_normalized in normalized:
            return "bachelor"

    return None


# ============================================================
# RELATED EDUCATION MATCH
# ============================================================

def related_education_match(
    requirement: str,
    candidate_text: str
) -> Optional[str]:

    requirement_normalized = normalize_text(
        requirement
    )

    candidate_normalized = normalize_text(
        candidate_text
    )

    if not requirement_normalized:
        return None

    if not candidate_normalized:
        return None

    # --------------------------------------------------------
    # Direct concept relationships
    # --------------------------------------------------------

    related_concepts = EDUCATION_CONCEPTS.get(
        requirement_normalized,
        set()
    )

    for concept in related_concepts:

        concept_normalized = normalize_text(
            concept
        )

        if exact_education_match(
            concept_normalized,
            candidate_normalized
        ):
            return concept

    # --------------------------------------------------------
    # Special handling for combined programs
    #
    # Example:
    #
    # CSE_AI&DS
    #
    # becomes:
    #
    # cse ai and ds
    #
    # Therefore it can provide evidence for:
    #
    # Computer Science
    # Artificial Intelligence
    # Data Science
    # --------------------------------------------------------

    candidate_words = set(
        candidate_normalized.split()
    )

    if "cse" in candidate_words:

        if requirement_normalized == "computer science":
            return "cse"

    if (
        "ai" in candidate_words
        or "artificial intelligence" in candidate_normalized
    ):

        if requirement_normalized == "artificial intelligence":
            return "ai"

    if (
        "ds" in candidate_words
        or "data science" in candidate_normalized
    ):

        if requirement_normalized == "data science":
            return "ds"

    # --------------------------------------------------------
    # Degree aliases
    # --------------------------------------------------------

    for alias, meanings in DEGREE_ALIASES.items():

        alias_normalized = normalize_text(
            alias
        )

        if alias_normalized in candidate_words:

            normalized_meanings = {
                normalize_text(
                    meaning
                )
                for meaning in meanings
            }

            if requirement_normalized in normalized_meanings:

                return alias

    # --------------------------------------------------------
    # Degree-level inference
    # --------------------------------------------------------

    if requirement_normalized in {
        "bachelor",
        "bachelors",
        "bachelor degree",
        "bachelors degree"
    }:

        inferred_degree = infer_degree_level(
            candidate_normalized
        )

        if inferred_degree == "bachelor":
            return inferred_degree

    return None


# ============================================================
# MATCH SINGLE EDUCATION REQUIREMENT
# ============================================================

def match_education_requirement(
    requirement: str,
    education_entries: List[Dict]
) -> Dict:

    if not requirement:

        return {
            "requirement": requirement,
            "status": "unknown",
            "confidence": 0.0,
            "evidence": []
        }

    if not education_entries:

        return {
            "requirement": requirement,
            "status": "unknown",
            "confidence": 0.0,
            "evidence": []
        }

    # ========================================================
    # STEP 1: EXACT MATCH
    # ========================================================

    for education in education_entries:

        candidate_text = normalize_education_entry(
            education
        )

        if not candidate_text:
            continue

        if exact_education_match(
            requirement,
            candidate_text
        ):

            return {
                "requirement": requirement,
                "status": "exact",
                "confidence": 1.0,
                "evidence": [
                    candidate_text
                ]
            }

    # ========================================================
    # STEP 2: RELATED MATCH
    # ========================================================

    for education in education_entries:

        candidate_text = normalize_education_entry(
            education
        )

        if not candidate_text:
            continue

        related = related_education_match(
            requirement,
            candidate_text
        )

        if related:

            return {
                "requirement": requirement,
                "status": "related",
                "confidence": 0.85,
                "evidence": [
                    candidate_text
                ]
            }

    # ========================================================
    # STEP 3: UNKNOWN
    # ========================================================

    return {
        "requirement": requirement,
        "status": "unknown",
        "confidence": 0.0,
        "evidence": []
    }


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

    if not required_education:

        return {
            "status": "not_required",
            "matched": [],
            "unknown": []
        }

    if not resume:

        return {
            "status": "unknown",
            "matched": [],
            "unknown": required_education
        }

    education_entries = resume.get(
        "education",
        []
    )

    if not education_entries:

        return {
            "status": "unknown",
            "matched": [],
            "unknown": required_education
        }

    results = match_education_requirements(
        required_education,
        education_entries
    )

    matched = []
    unknown = []

    for result in results:

        if result["status"] in [
            "exact",
            "related"
        ]:

            matched.append(
                result
            )

        else:

            unknown.append(
                result
            )

    if matched:
        status = "matched"
    else:
        status = "unknown"

    return {
        "status": status,
        "matched": matched,
        "unknown": unknown
    }