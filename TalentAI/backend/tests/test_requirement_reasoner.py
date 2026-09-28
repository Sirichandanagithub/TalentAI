from pprint import pprint

from app.ai.analyzer.requirement_reasoner import (
    RequirementReasoner,
)


def test_reasoner():

    reasoner = RequirementReasoner()

    # ========================================================
    # TEST 1
    # Direct + context + strong evidence
    # ========================================================

    print("\n" + "=" * 60)
    print("TEST 1: PYTHON")
    print("=" * 60)

    result = reasoner.reason(
        requirement="Python",

        hybrid_result={
            "status": "matched",
            "confidence": 1.0,
            "relationship": "exact",
            "match_source": "canonical",
            "rule_match": True,
        },

        context_result={
            "context_status": "supported",
            "context_score": 0.95,
        },

        evidence_result={
            "evidence_count": 3,
            "best_source": "experience",
            "best_weight": 1.0,
            "evidence_strength": 1.0,
            "evidence_quality": "strong",
            "direct_evidence": True,
            "source_coverage": 0.50,
        },
    )

    pprint(result)

    assert result["status"] == "matched"
    assert result["direct_match"] is True
    assert result["direct_evidence"] is True
    assert result["context_supported"] is True

    print("✅ Python reasoning passed")

    # ========================================================
    # TEST 2
    # MySQL → SQL relationship
    # No direct evidence
    # ========================================================

    print("\n" + "=" * 60)
    print("TEST 2: SQL FROM MYSQL")
    print("=" * 60)

    result = reasoner.reason(
        requirement="SQL",

        hybrid_result={
            "status": "matched",
            "confidence": 0.75,
            "relationship": "related",
            "match_source": "hybrid",
            "rule_match": True,
        },

        context_result={
            "context_status": "unknown",
            "context_score": 0.0,
        },

        evidence_result={
            "evidence_count": 0,
            "best_source": None,
            "best_weight": 0.0,
            "evidence_strength": 0.0,
            "evidence_quality": "none",
            "direct_evidence": False,
            "source_coverage": 0.0,
        },
    )

    pprint(result)

    assert result["status"] == "possible"
    assert result["relationship_match"] is True
    assert result["direct_match"] is False
    assert result["evidence_found"] is False
    assert result["context_supported"] is False

    print("✅ SQL relationship reasoning passed")

    # ========================================================
    # TEST 3
    # Unknown requirement
    # ========================================================

    print("\n" + "=" * 60)
    print("TEST 3: AWS")
    print("=" * 60)

    result = reasoner.reason(
        requirement="AWS",

        hybrid_result={
            "status": "unknown",
            "confidence": 0.40,
            "relationship": "none",
            "match_source": "ai",
            "rule_match": False,
        },

        context_result={
            "context_status": "unknown",
            "context_score": 0.0,
        },

        evidence_result={
            "evidence_count": 0,
            "best_source": None,
            "best_weight": 0.0,
            "evidence_strength": 0.0,
            "evidence_quality": "none",
            "direct_evidence": False,
            "source_coverage": 0.0,
        },
    )

    pprint(result)

    assert result["status"] == "unknown"
    assert result["evidence_found"] is False
    assert result["direct_match"] is False

    print("✅ AWS unknown reasoning passed")

    # ========================================================
    # TEST 4
    # Evidence exists but matcher is uncertain
    # ========================================================

    print("\n" + "=" * 60)
    print("TEST 4: EVIDENCE OVERRIDES UNCERTAINTY")
    print("=" * 60)

    result = reasoner.reason(
        requirement="Machine Learning",

        hybrid_result={
            "status": "possible",
            "confidence": 0.55,
            "relationship": "related",
            "match_source": "hybrid",
            "rule_match": True,
        },

        context_result={
            "context_status": "supported",
            "context_score": 0.95,
        },

        evidence_result={
            "evidence_count": 1,
            "best_source": "project",
            "best_weight": 0.95,
            "evidence_strength": 0.95,
            "evidence_quality": "strong",
            "direct_evidence": True,
            "source_coverage": 0.1667,
        },
    )

    pprint(result)

    assert result["status"] == "possible"
    assert result["evidence_found"] is True
    assert result["direct_evidence"] is True
    assert result["context_supported"] is True

    print("✅ Evidence-aware reasoning passed")

    # ========================================================
    # TEST 5
    # Direct evidence but no context
    # ========================================================

    print("\n" + "=" * 60)
    print("TEST 5: DIRECT EVIDENCE")
    print("=" * 60)

    result = reasoner.reason(
        requirement="Pandas",

        hybrid_result={
            "status": "matched",
            "confidence": 1.0,
            "relationship": "exact",
            "match_source": "canonical",
            "rule_match": True,
        },

        context_result={
            "context_status": "unknown",
            "context_score": 0.0,
        },

        evidence_result={
            "evidence_count": 1,
            "best_source": "project",
            "best_weight": 0.95,
            "evidence_strength": 0.95,
            "evidence_quality": "strong",
            "direct_evidence": True,
            "source_coverage": 0.1667,
        },
    )

    pprint(result)

    assert result["status"] == "matched"
    assert result["direct_match"] is True
    assert result["direct_evidence"] is True

    print("✅ Direct evidence reasoning passed")

    print("\n" + "=" * 60)
    print("REQUIREMENT REASONER TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_reasoner()