from app.ai.analyzer.decision_engine import (
    classify_evidence_strength,
    make_decision,
    make_decisions,
    analyze_requirement
)


# ============================================================
# TEST HELPER
# ============================================================

def print_result(
    title,
    result
):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(result)


# ============================================================
# INITIALIZATION
# ============================================================

print("=" * 60)
print("DECISION ENGINE TEST")
print("=" * 60)

print("Decision engine initialized successfully.")


# ============================================================
# TEST 1: EVIDENCE CLASSIFICATION
# ============================================================

print_result(
    "TEST 1: VERY STRONG EVIDENCE",
    classify_evidence_strength(0.90)
)

print_result(
    "TEST 2: STRONG EVIDENCE",
    classify_evidence_strength(0.70)
)

print_result(
    "TEST 3: MODERATE EVIDENCE",
    classify_evidence_strength(0.50)
)

print_result(
    "TEST 4: WEAK EVIDENCE",
    classify_evidence_strength(0.25)
)

print_result(
    "TEST 5: NO EVIDENCE",
    classify_evidence_strength(0.0)
)


# ============================================================
# TEST DATA
# ============================================================

exact_match = {

    "requirement": "Python",

    "status": "matched",

    "confidence": 1.0,

    "evidence": [
        "Python"
    ],

    "rule_match": True,

    "semantic_similarity": 1.0,

    "relationship": "exact",

    "match_source": "rule"
}


python_evidence = {

    "requirement": "Python",

    "evidence": [

        {
            "source": "skills",
            "text": "Python",
            "weight": 0.90
        },

        {
            "source": "experience",
            "text":
                "Worked on data analysis using Python.",
            "weight": 1.00
        },

        {
            "source": "project",
            "project":
                "AI Crime Prediction System",
            "text":
                "Developed using Python.",
            "weight": 0.95
        }

    ],

    "evidence_count": 3,

    "best_source": "experience",

    "evidence_strength": 1.0,

    "status": "found"
}


# ============================================================
# TEST 6: EXACT + STRONG EVIDENCE
# ============================================================

result = make_decision(
    "Python",
    exact_match,
    python_evidence
)

print_result(
    "TEST 6: PYTHON EXACT + EVIDENCE",
    result
)


# ============================================================
# TEST 7: RELATED + PROJECT EVIDENCE
# ============================================================

related_match = {

    "requirement":
        "Machine Learning",

    "status":
        "matched",

    "confidence":
        0.75,

    "evidence":
        ["Classification"],

    "rule_match":
        True,

    "semantic_similarity":
        0.717,

    "relationship":
        "related",

    "match_source":
        "hybrid"
}


ml_evidence = {

    "requirement":
        "Machine Learning",

    "evidence": [

        {
            "source":
                "project",

            "project":
                "AI Crime Prediction System",

            "text":
                "Machine learning classification model.",

            "weight":
                0.95
        }

    ],

    "evidence_count":
        1,

    "best_source":
        "project",

    "evidence_strength":
        0.475,

    "status":
        "found"
}


result = make_decision(
    "Machine Learning",
    related_match,
    ml_evidence
)

print_result(
    "TEST 7: MACHINE LEARNING RELATED + EVIDENCE",
    result
)


# ============================================================
# TEST 8: POSSIBLE WITHOUT EVIDENCE
# ============================================================

possible_match = {

    "requirement":
        "TensorFlow",

    "status":
        "possible",

    "confidence":
        0.5366,

    "evidence":
        ["Deep Learning"],

    "rule_match":
        False,

    "semantic_similarity":
        0.5366,

    "relationship":
        "possible_related",

    "match_source":
        "ai"
}


no_evidence = {

    "requirement":
        "TensorFlow",

    "evidence":
        [],

    "evidence_count":
        0,

    "best_source":
        None,

    "evidence_strength":
        0.0,

    "status":
        "not_found"
}


result = make_decision(
    "TensorFlow",
    possible_match,
    no_evidence
)

print_result(
    "TEST 8: TENSORFLOW POSSIBLE",
    result
)


# ============================================================
# TEST 9: UNKNOWN
# ============================================================

unknown_match = {

    "requirement":
        "AWS",

    "status":
        "unknown",

    "confidence":
        0.35,

    "evidence":
        [],

    "rule_match":
        False,

    "semantic_similarity":
        0.35,

    "relationship":
        "none",

    "match_source":
        "ai"
}


aws_evidence = {

    "requirement":
        "AWS",

    "evidence":
        [],

    "evidence_count":
        0,

    "best_source":
        None,

    "evidence_strength":
        0.0,

    "status":
        "not_found"
}


result = make_decision(
    "AWS",
    unknown_match,
    aws_evidence
)

print_result(
    "TEST 9: AWS UNKNOWN",
    result
)


# ============================================================
# TEST 10: EXACT WITHOUT ADDITIONAL EVIDENCE
# ============================================================

result = make_decision(
    "Python",
    exact_match,
    {
        "evidence": [],
        "evidence_count": 0,
        "best_source": None,
        "evidence_strength": 0.0
    }
)

print_result(
    "TEST 10: EXACT WITHOUT EVIDENCE",
    result
)


# ============================================================
# TEST 11: BATCH DECISIONS
# ============================================================

match_results = [

    exact_match,

    related_match,

    possible_match,

    unknown_match
]


evidence_results = [

    python_evidence,

    ml_evidence,

    no_evidence,

    aws_evidence
]


results = make_decisions(
    match_results,
    evidence_results
)

print_result(
    "TEST 11: BATCH DECISIONS",
    results
)


# ============================================================
# TEST 12: COMPLETE ANALYSIS
# ============================================================

result = analyze_requirement(
    "Python",
    exact_match,
    python_evidence
)

print_result(
    "TEST 12: COMPLETE REQUIREMENT ANALYSIS",
    result
)


# ============================================================
# TEST 13: EMPTY REQUIREMENT
# ============================================================

result = make_decision(
    "",
    {},
    {}
)

print_result(
    "TEST 13: EMPTY REQUIREMENT",
    result
)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("DECISION ENGINE TEST FINISHED")
print("=" * 60)