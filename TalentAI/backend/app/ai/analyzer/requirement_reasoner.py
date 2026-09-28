from typing import Dict, List


# ============================================================
# REQUIREMENT REASONER
# ============================================================


class RequirementReasoner:
    """
    Requirement-level reasoning layer.

    This class does NOT perform matching itself.

    It combines the outputs of:

        HybridMatcher
              ↓
        ContextMatcher
              ↓
        EvidenceEngine
              ↓
        RequirementReasoner

    The purpose is to make the final requirement classification
    more explainable and evidence-aware.
    """

    # ========================================================
    # THRESHOLDS
    # ========================================================

    STRONG_CONFIDENCE = 0.85

    MATCHED_CONFIDENCE = 0.65

    POSSIBLE_CONFIDENCE = 0.40

    # ========================================================
    # WEIGHTS
    # ========================================================

    EVIDENCE_WEIGHT = 0.35

    CONTEXT_WEIGHT = 0.30

    MATCH_WEIGHT = 0.35

    # ========================================================
    # INDIRECT RELATIONSHIPS
    # ========================================================

    INDIRECT_RELATIONSHIPS = {
        "related",
        "strong_related",
    }

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize(value) -> str:
        """
        Normalize a value for safe comparison.
        """

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

    # ========================================================
    # DIRECT MATCH DETECTION
    # ========================================================

    def _is_direct_match(
        self,
        hybrid_result: Dict
    ) -> bool:
        """
        Determine whether HybridMatcher produced a
        direct requirement match.

        Direct examples:

            Python → Python
            Pandas → Pandas
            Scikit-learn → Scikit-learn

        Indirect relationships such as:

            MySQL → SQL
            TensorFlow → Machine Learning

        are NOT considered direct.
        """

        if not isinstance(
            hybrid_result,
            dict
        ):
            return False

        relationship = self._normalize(
            hybrid_result.get(
                "relationship"
            )
        )

        match_source = self._normalize(
            hybrid_result.get(
                "match_source"
            )
        )

        status = self._normalize(
            hybrid_result.get(
                "status"
            )
        )

        # ----------------------------------------------------
        # Explicit relationship information
        # ----------------------------------------------------

        if relationship in self.INDIRECT_RELATIONSHIPS:
            return False

        # ----------------------------------------------------
        # Canonical match
        # ----------------------------------------------------

        if match_source == "canonical":
            return True

        # ----------------------------------------------------
        # Exact relationship
        # ----------------------------------------------------

        if relationship == "exact":
            return True

        # ----------------------------------------------------
        # Rule-based exact match
        # ----------------------------------------------------

        if (
            relationship == ""
            and match_source in {
                "rule",
                "exact",
            }
        ):
            return True

        # ----------------------------------------------------
        # Strong semantic match without relationship
        # ----------------------------------------------------

        if (
            status == "matched"
            and relationship
            not in self.INDIRECT_RELATIONSHIPS
            and match_source
            not in {
                "hybrid",
                "relationship",
            }
        ):
            return True

        return False

    # ========================================================
    # RELATIONSHIP MATCH DETECTION
    # ========================================================

    def _is_relationship_match(
        self,
        hybrid_result: Dict
    ) -> bool:
        """
        Determine whether the HybridMatcher result
        represents an indirect relationship.
        """

        if not isinstance(
            hybrid_result,
            dict
        ):
            return False

        relationship = self._normalize(
            hybrid_result.get(
                "relationship"
            )
        )

        match_source = self._normalize(
            hybrid_result.get(
                "match_source"
            )
        )

        if relationship in self.INDIRECT_RELATIONSHIPS:
            return True

        if match_source in {
            "relationship",
            "hybrid",
        }:
            return relationship in self.INDIRECT_RELATIONSHIPS

        return False

    # ========================================================
    # CONTEXT SUPPORT
    # ========================================================

    def _is_context_supported(
        self,
        context_result: Dict
    ) -> bool:
        """
        Determine whether the resume provides contextual
        support for the requirement.
        """

        if not isinstance(
            context_result,
            dict
        ):
            return False

        context_status = self._normalize(
            context_result.get(
                "context_status"
            )
        )

        context_score = float(
            context_result.get(
                "context_score",
                0.0
            ) or 0.0
        )

        if context_status == "supported":
            return True

        if context_score >= 0.60:
            return True

        return False

    # ========================================================
    # EVIDENCE DETECTION
    # ========================================================

    def _has_evidence(
        self,
        evidence_result: Dict
    ) -> bool:
        """
        Determine whether any resume evidence exists.
        """

        if not isinstance(
            evidence_result,
            dict
        ):
            return False

        evidence = evidence_result.get(
            "evidence",
            []
        )

        if isinstance(
            evidence,
            list
        ) and evidence:
            return True

        evidence_count = evidence_result.get(
            "evidence_count",
            0
        )

        try:

            if int(
                evidence_count
            ) > 0:
                return True

        except (
            TypeError,
            ValueError
        ):

            pass

        evidence_strength = evidence_result.get(
            "evidence_strength",
            0.0
        )

        try:

            if float(
                evidence_strength
            ) > 0:
                return True

        except (
            TypeError,
            ValueError
        ):

            pass

        return False

    # ========================================================
    # DIRECT EVIDENCE
    # ========================================================

    def _has_direct_evidence(
        self,
        evidence_result: Dict
    ) -> bool:
        """
        Determine whether the evidence is directly
        demonstrated by the resume.

        Direct sources currently include:

            experience
            project
            skills
            certification
        """

        if not isinstance(
            evidence_result,
            dict
        ):
            return False

        if evidence_result.get(
            "direct_evidence",
            False
        ):
            return True

        evidence = evidence_result.get(
            "evidence",
            []
        )

        if not isinstance(
            evidence,
            list
        ):
            return False

        direct_sources = {
            "experience",
            "project",
            "skills",
            "certification",
        }

        for item in evidence:

            if not isinstance(
                item,
                dict
            ):
                continue

            source = self._normalize(
                item.get(
                    "source"
                )
            )

            if source in direct_sources:
                return True

        return False

    # ========================================================
    # MATCH SCORE
    # ========================================================

    def _calculate_match_score(
        self,
        hybrid_result: Dict,
        direct_match: bool,
        relationship_match: bool
    ) -> float:
        """
        Calculate the contribution of the HybridMatcher.

        Direct matches use the original HybridMatcher
        confidence.

        Relationship-only matches are capped at 0.60 so
        that an indirect relationship cannot behave like
        a confirmed direct match.
        """

        if not isinstance(
            hybrid_result,
            dict
        ):
            return 0.0

        confidence = hybrid_result.get(
            "confidence",
            hybrid_result.get(
                "semantic_similarity",
                0.0
            )
        )

        try:

            confidence = float(
                confidence
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0

        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )

        # ----------------------------------------------------
        # Direct match
        # ----------------------------------------------------

        if direct_match:
            return round(
                confidence,
                4
            )

        # ----------------------------------------------------
        # Relationship-only match
        # ----------------------------------------------------

        if relationship_match:
            return 0.60

        # ----------------------------------------------------
        # No meaningful match
        # ----------------------------------------------------

        return round(
            confidence,
            4
        )

    # ========================================================
    # EVIDENCE SCORE
    # ========================================================

    def _calculate_evidence_score(
        self,
        evidence_result: Dict
    ) -> float:
        """
        Convert EvidenceEngine output into a normalized
        evidence score.
        """

        if not isinstance(
            evidence_result,
            dict
        ):
            return 0.0

        evidence_strength = evidence_result.get(
            "evidence_strength",
            0.0
        )

        try:

            evidence_strength = float(
                evidence_strength
            )

        except (
            TypeError,
            ValueError
        ):

            evidence_strength = 0.0

        evidence_strength = max(
            0.0,
            min(
                evidence_strength,
                1.0
            )
        )

        return round(
            evidence_strength,
            4
        )

    # ========================================================
    # CONTEXT SCORE
    # ========================================================

    def _calculate_context_score(
        self,
        context_result: Dict
    ) -> float:
        """
        Convert ContextMatcher output into a normalized
        context score.
        """

        if not isinstance(
            context_result,
            dict
        ):
            return 0.0

        context_score = context_result.get(
            "context_score",
            0.0
        )

        try:

            context_score = float(
                context_score
            )

        except (
            TypeError,
            ValueError
        ):

            context_score = 0.0

        context_score = max(
            0.0,
            min(
                context_score,
                1.0
            )
        )

        return round(
            context_score,
            4
        )

    # ========================================================
    # OVERALL CONFIDENCE
    # ========================================================

    def _calculate_confidence(
        self,
        match_score: float,
        context_score: float,
        evidence_score: float
    ) -> float:
        """
        Calculate final requirement confidence.

        Formula:

            Match       × 0.35
            Context     × 0.30
            Evidence    × 0.35
        """

        confidence = (
            match_score * self.MATCH_WEIGHT
            + context_score * self.CONTEXT_WEIGHT
            + evidence_score * self.EVIDENCE_WEIGHT
        )

        confidence = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )

        return round(
            confidence,
            4
        )

    # ========================================================
    # STATUS DETERMINATION
    # ========================================================

    def _determine_status(
        self,
        direct_match: bool,
        relationship_match: bool,
        context_supported: bool,
        evidence_found: bool,
        direct_evidence: bool,
        confidence: float
    ) -> str:
        """
        Determine the final requirement status.

        Reasoning priority:

            1. Direct match + supporting evidence
            2. Direct match + context
            3. Direct match with high confidence
            4. Relationship + direct evidence + context
            5. Relationship + strong direct evidence
            6. Direct match without enough support
            7. Relationship match
            8. Context + evidence
            9. Evidence only
            10. Unknown

        Important:

        A relationship match alone does NOT become matched.

        However, if the resume itself directly demonstrates
        the requirement and the context layer confirms that
        evidence, the requirement can become matched.
        """

        # ----------------------------------------------------
        # 1. DIRECT MATCH + STRONG SUPPORT
        # ----------------------------------------------------

        if (
            direct_match
            and (
                context_supported
                or direct_evidence
            )
            and confidence >= self.MATCHED_CONFIDENCE
        ):
            return "matched"

        # ----------------------------------------------------
        # 2. DIRECT MATCH + HIGH CONFIDENCE
        # ----------------------------------------------------

        if (
            direct_match
            and confidence >= self.STRONG_CONFIDENCE
        ):
            return "matched"

        # ----------------------------------------------------
        # 3. INDIRECT MATCH + DIRECT EVIDENCE + CONTEXT
        # ----------------------------------------------------

        if (
            relationship_match
            and direct_evidence
            and context_supported
            and confidence >= self.MATCHED_CONFIDENCE
        ):
            return "matched"

        # ----------------------------------------------------
        # 4. INDIRECT MATCH + STRONG DIRECT EVIDENCE
        # ----------------------------------------------------

        if (
            relationship_match
            and direct_evidence
            and confidence >= self.STRONG_CONFIDENCE
        ):
            return "matched"

        # ----------------------------------------------------
        # 5. DIRECT MATCH WITHOUT ENOUGH SUPPORT
        # ----------------------------------------------------

        if direct_match:
            return "possible"

        # ----------------------------------------------------
        # 6. RELATIONSHIP MATCH
        # ----------------------------------------------------

        if relationship_match:
            return "possible"

        # ----------------------------------------------------
        # 7. CONTEXT + EVIDENCE
        # ----------------------------------------------------

        if (
            context_supported
            and evidence_found
            and confidence >= self.POSSIBLE_CONFIDENCE
        ):
            return "possible"

        # ----------------------------------------------------
        # 8. EVIDENCE ONLY
        # ----------------------------------------------------

        if evidence_found:
            return "possible"

        # ----------------------------------------------------
        # 9. UNKNOWN
        # ----------------------------------------------------

        return "unknown"

    # ========================================================
    # REASON GENERATION
    # ========================================================

    def _build_reason(
        self,
        requirement: str,
        status: str,
        direct_match: bool,
        relationship_match: bool,
        context_supported: bool,
        evidence_found: bool,
        direct_evidence: bool,
        evidence_quality: str
    ) -> str:
        """
        Build a human-readable explanation for the
        requirement classification.
        """

        if status == "matched":

            if (
                direct_match
                and context_supported
                and direct_evidence
            ):

                return (
                    f"{requirement} is directly matched and "
                    "supported by resume evidence and context."
                )

            if (
                direct_match
                and direct_evidence
            ):

                return (
                    f"{requirement} is directly matched and "
                    "supported by resume evidence."
                )

            if (
                direct_match
                and context_supported
            ):

                return (
                    f"{requirement} is directly matched and "
                    "supported by resume context."
                )

            if (
                relationship_match
                and direct_evidence
                and context_supported
            ):

                return (
                    f"{requirement} has an indirect skill "
                    "relationship, but the resume directly "
                    "demonstrates the requirement and the "
                    "context layer supports it."
                )

            if (
                relationship_match
                and direct_evidence
            ):

                return (
                    f"{requirement} has a related skill match "
                    "and is directly supported by resume evidence."
                )

            return (
                f"{requirement} is sufficiently supported "
                "by the candidate's resume."
            )

        if status == "possible":

            if (
                relationship_match
                and not direct_evidence
            ):

                return (
                    f"{requirement} has a related skill match, "
                    "but it is not directly demonstrated in "
                    "the candidate's resume."
                )

            if (
                evidence_found
                and not direct_match
            ):

                return (
                    f"{requirement} has resume evidence, "
                    "but the match is not sufficiently direct "
                    "to classify it as a confirmed match."
                )

            if context_supported:

                return (
                    f"{requirement} has contextual support, "
                    "but the available evidence is not strong "
                    "enough for a confirmed match."
                )

            return (
                f"{requirement} has some supporting signals, "
                "but additional evidence is needed."
            )

        return (
            f"No direct or sufficient supporting evidence "
            f"was found for {requirement}."
        )

    # ========================================================
    # MAIN REASON METHOD
    # ========================================================

    def reason(
        self,
        requirement: str,
        hybrid_result: Dict,
        context_result: Dict,
        evidence_result: Dict
    ) -> Dict:
        """
        Reason about one job requirement.

        Inputs:

            hybrid_result
                Result from HybridMatcher.

            context_result
                Result from ContextMatcher.

            evidence_result
                Result from EvidenceEngine.

        Returns:

            A structured requirement reasoning result.
        """

        # ----------------------------------------------------
        # MATCH ANALYSIS
        # ----------------------------------------------------

        direct_match = self._is_direct_match(
            hybrid_result
        )

        relationship_match = self._is_relationship_match(
            hybrid_result
        )

        # ----------------------------------------------------
        # CONTEXT ANALYSIS
        # ----------------------------------------------------

        context_supported = self._is_context_supported(
            context_result
        )

        context_score = self._calculate_context_score(
            context_result
        )

        # ----------------------------------------------------
        # EVIDENCE ANALYSIS
        # ----------------------------------------------------

        evidence_found = self._has_evidence(
            evidence_result
        )

        direct_evidence = self._has_direct_evidence(
            evidence_result
        )

        evidence_score = self._calculate_evidence_score(
            evidence_result
        )

        # ----------------------------------------------------
        # MATCH SCORE
        # ----------------------------------------------------

        match_score = self._calculate_match_score(
            hybrid_result=hybrid_result,
            direct_match=direct_match,
            relationship_match=relationship_match
        )

        # ----------------------------------------------------
        # FINAL CONFIDENCE
        # ----------------------------------------------------

        confidence = self._calculate_confidence(
            match_score=match_score,
            context_score=context_score,
            evidence_score=evidence_score
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = self._determine_status(
            direct_match=direct_match,
            relationship_match=relationship_match,
            context_supported=context_supported,
            evidence_found=evidence_found,
            direct_evidence=direct_evidence,
            confidence=confidence
        )

        # ----------------------------------------------------
        # EVIDENCE METADATA
        # ----------------------------------------------------

        evidence_quality = (
            evidence_result.get(
                "evidence_quality",
                "none"
            )
            if isinstance(
                evidence_result,
                dict
            )
            else "none"
        )

        best_source = (
            evidence_result.get(
                "best_source"
            )
            if isinstance(
                evidence_result,
                dict
            )
            else None
        )

        source_coverage = (
            evidence_result.get(
                "source_coverage",
                0.0
            )
            if isinstance(
                evidence_result,
                dict
            )
            else 0.0
        )

        try:

            source_coverage = float(
                source_coverage
            )

        except (
            TypeError,
            ValueError
        ):

            source_coverage = 0.0

        source_coverage = max(
            0.0,
            min(
                source_coverage,
                1.0
            )
        )

        # ----------------------------------------------------
        # EXPLANATION
        # ----------------------------------------------------

        reason = self._build_reason(
            requirement=requirement,
            status=status,
            direct_match=direct_match,
            relationship_match=relationship_match,
            context_supported=context_supported,
            evidence_found=evidence_found,
            direct_evidence=direct_evidence,
            evidence_quality=evidence_quality
        )

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "requirement": requirement,

            "status": status,

            "confidence": confidence,

            "direct_match": direct_match,

            "relationship_match": relationship_match,

            "context_supported": context_supported,

            "evidence_found": evidence_found,

            "direct_evidence": direct_evidence,

            "match_score": match_score,

            "context_score": context_score,

            "evidence_score": evidence_score,

            "evidence_quality": evidence_quality,

            "best_source": best_source,

            "source_coverage": round(
                source_coverage,
                4
            ),

            "reason": reason
        }

    # ========================================================
    # MULTIPLE REQUIREMENTS
    # ========================================================

    def reason_multiple(
        self,
        requirements: List[str],
        hybrid_results: Dict,
        context_results: Dict,
        evidence_results: Dict
    ) -> List[Dict]:
        """
        Reason about multiple requirements.

        Expected structure:

            hybrid_results[requirement]
            context_results[requirement]
            evidence_results[requirement]
        """

        results = []

        for requirement in requirements:

            hybrid_result = hybrid_results.get(
                requirement,
                {}
            )

            context_result = context_results.get(
                requirement,
                {}
            )

            evidence_result = evidence_results.get(
                requirement,
                {}
            )

            results.append(
                self.reason(
                    requirement=requirement,
                    hybrid_result=hybrid_result,
                    context_result=context_result,
                    evidence_result=evidence_result
                )
            )

        return results


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================


def reason_requirement(
    requirement: str,
    hybrid_result: Dict,
    context_result: Dict,
    evidence_result: Dict
) -> Dict:
    """
    Convenience function for reasoning about one requirement.
    """

    reasoner = RequirementReasoner()

    return reasoner.reason(
        requirement=requirement,
        hybrid_result=hybrid_result,
        context_result=context_result,
        evidence_result=evidence_result
    )