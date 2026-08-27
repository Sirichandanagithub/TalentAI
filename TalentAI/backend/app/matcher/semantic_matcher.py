import re
from typing import List, Dict, Optional


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    # Normalize common separators
    text = text.replace("&", " and ")
    text = text.replace("-", " ")

    # Remove punctuation
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# EXACT MATCH
# ============================================================

def exact_match(
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

    # IMPORTANT:
    # Do NOT use simple substring matching.
    #
    # Example:
    # "sql" must NOT match "mysql"
    # "java" must NOT match "javascript"

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
# RELATED CONCEPTS
# ============================================================

# This is intentionally small.
#
# It is NOT our final knowledge base.
#
# It only provides a few broad relationships while we build
# the semantic layer.
#
# Later this can be replaced/enhanced with embeddings and
# external knowledge sources.

RELATED_CONCEPTS = {

    "sql": {
        "mysql",
        "postgresql",
        "postgres",
        "sqlite",
        "oracle",
        "sql server",
        "microsoft sql server",
        "tsql",
        "t sql"
    },

    "machine learning": {
        "classification",
        "regression",
        "supervised learning",
        "unsupervised learning",
        "scikit learn",
        "scikit-learn",
        "deep learning",
        "machine learning"
    },

    "artificial intelligence": {
        "machine learning",
        "deep learning",
        "natural language processing",
        "nlp",
        "computer vision",
        "artificial intelligence",
        "ai"
    },

    "data science": {
        "data analysis",
        "statistical analysis",
        "machine learning",
        "data visualization",
        "data preprocessing",
        "deep learning"
    },

    "data analysis": {
        "pandas",
        "numpy",
        "data visualization",
        "statistical analysis",
        "data preprocessing",
        "data analysis"
    },

    "computer science": {
        "computer science",
        "cse",
        "computer engineering",
        "software engineering"
    }
}


# ============================================================
# RELATED MATCH
# ============================================================

def related_match(
    requirement: str,
    candidate_skills: List[str]
) -> Optional[str]:

    requirement_normalized = normalize_text(
        requirement
    )

    if not requirement_normalized:
        return None

    related_skills = RELATED_CONCEPTS.get(
        requirement_normalized,
        set()
    )

    if not related_skills:
        return None

    for candidate_skill in candidate_skills:

        candidate_normalized = normalize_text(
            candidate_skill
        )

        if candidate_normalized in related_skills:

            return candidate_skill

    return None


# ============================================================
# SEMANTIC MATCH
# ============================================================

def match_concept(
    requirement: str,
    candidate_skills: List[str]
) -> Dict:

    if not requirement:

        return {
            "requirement": requirement,
            "status": "unknown",
            "confidence": 0.0,
            "evidence": []
        }

    if not candidate_skills:

        return {
            "requirement": requirement,
            "status": "unknown",
            "confidence": 0.0,
            "evidence": []
        }

    # --------------------------------------------------------
    # STEP 1: EXACT
    # --------------------------------------------------------

    for candidate_skill in candidate_skills:

        if exact_match(
            requirement,
            candidate_skill
        ):

            return {
                "requirement": requirement,
                "status": "exact",
                "confidence": 1.0,
                "evidence": [
                    candidate_skill
                ]
            }

    # --------------------------------------------------------
    # STEP 2: RELATED
    # --------------------------------------------------------

    related_skill = related_match(
        requirement,
        candidate_skills
    )

    if related_skill:

        return {
            "requirement": requirement,
            "status": "related",
            "confidence": 0.75,
            "evidence": [
                related_skill
            ]
        }

    # --------------------------------------------------------
    # STEP 3: UNKNOWN
    # --------------------------------------------------------

    return {
        "requirement": requirement,
        "status": "unknown",
        "confidence": 0.0,
        "evidence": []
    }


# ============================================================
# MATCH MULTIPLE REQUIREMENTS
# ============================================================

def match_requirements(
    requirements: List[str],
    candidate_skills: List[str]
) -> List[Dict]:

    if not requirements:

        return []

    results = []

    for requirement in requirements:

        result = match_concept(
            requirement,
            candidate_skills
        )

        results.append(
            result
        )

    return results