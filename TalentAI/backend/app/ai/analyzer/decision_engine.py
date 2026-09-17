from typing import Any, Dict, List


# ============================================================
# CONFIGURATION
# ============================================================

# Semantic confidence levels
STRONG_MATCH_THRESHOLD = 0.65
POSSIBLE_MATCH_THRESHOLD = 0.50

# Evidence strength levels
VERY_STRONG_EVIDENCE = 0.80
STRONG_EVIDENCE = 0.60
MODERATE_EVIDENCE = 0.40
WEAK_EVIDENCE = 0.20


# ============================================================
# EVIDENCE STRENGTH CLASSIFICATION
# ============================================================

def classify_evidence_strength(
    evidence_strength: float
) -> str:

    if evidence_strength >= VERY_STRONG_EVIDENCE:
        return "very_strong"

    if evidence_strength >= STRONG_EVIDENCE:
        return "strong"

    if evidence_strength >= MODERATE_EVIDENCE:
        return "moderate"

    if evidence_strength >= WEAK_EVIDENCE:
        return "weak"

    return "none"


# ============================================================
# GET EVIDENCE SOURCES
# ============================================================

def get_evidence_sources(
    evidence_result: Dict
) -> List[str]:

    if not isinstance(
        evidence_result,
        dict
    ):
        return []

    evidence = evidence_result.get(
        "evidence",
        []
    )

    if not isinstance(
        evidence,
        list
    ):
        return []

    sources = []

    for item in evidence:

        if not isinstance(
            item,
            dict
        ):
            continue

        source = item.get(
            "source"
        )

        if source and source not in sources:

            sources.append(source)

    return sources


# ============================================================
# GENERATE REASON
# ============================================================

def generate_reason(
    requirement: str,
    match_result: Dict,
    evidence_result: Dict
) -> str:

    status = match_result.get(
        "status",
        "unknown"
    )

    confidence = match_result.get(
        "confidence",
        0.0
    )

    evidence_sources = get_evidence_sources(
        evidence_result
    )

    verified = len(
        evidence_sources
    ) > 0

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    if (
        status == "matched"
        and match_result.get("relationship") == "exact"
    ):

        if verified:

            return (
                f"{requirement} is explicitly matched and "
                f"supported by resume evidence from "
                f"{', '.join(evidence_sources)}."
            )

        return (
            f"{requirement} is an exact skill match, "
            f"but supporting resume evidence was not found."
        )

    # --------------------------------------------------------
    # Strong matched
    # --------------------------------------------------------

    if status == "matched":

        if verified:

            return (
                f"{requirement} is strongly related to the "
                f"candidate's skills and is supported by "
                f"evidence from {', '.join(evidence_sources)}."
            )

        return (
            f"{requirement} has a strong semantic match, "
            f"but supporting resume evidence was not found."
        )

    # --------------------------------------------------------
    # Possible
    # --------------------------------------------------------

    if status == "possible":

        if verified:

            return (
                f"{requirement} has a possible semantic "
                f"relationship and supporting evidence was "
                f"found in {', '.join(evidence_sources)}."
            )

        return (
            f"{requirement} has some semantic similarity, "
            f"but the match is not strong enough to verify."
        )

    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    if verified:

        return (
            f"{requirement} appears in the resume, but the "
            f"available matching evidence is not strong "
            f"enough to classify it as a confirmed match."
        )

    return (
        f"{requirement} was not sufficiently supported by "
        f"the available resume evidence."
    )


# ============================================================
# CALCULATE FINAL CONFIDENCE
# ============================================================

def calculate_final_confidence(
    match_result: Dict,
    evidence_result: Dict
) -> float:

    match_confidence = float(
        match_result.get(
            "confidence",
            0.0
        )
    )

    evidence_strength = float(
        evidence_result.get(
            "evidence_strength",
            0.0
        )
    )

    status = match_result.get(
        "status",
        "unknown"
    )

    # --------------------------------------------------------
    # No match
    # --------------------------------------------------------

    if status == "unknown":

        # Evidence alone should not create a match.
        return round(
            match_confidence,
            4
        )

    # --------------------------------------------------------
    # Exact rule match
    # --------------------------------------------------------

    if (
        match_result.get("relationship")
        == "exact"
    ):

        if evidence_strength > 0:

            # Exact + evidence
            final_confidence = (
                0.70 * match_confidence
                + 0.30 * evidence_strength
            )

            return round(
                min(final_confidence, 1.0),
                4
            )

        return round(
            match_confidence,
            4
        )

    # --------------------------------------------------------
    # Related / semantic match
    # --------------------------------------------------------

    if status == "matched":

        if evidence_strength > 0:

            final_confidence = (
                0.65 * match_confidence
                + 0.35 * evidence_strength
            )

            return round(
                min(final_confidence, 1.0),
                4
            )

        return round(
            match_confidence,
            4
        )

    # --------------------------------------------------------
    # Possible match
    # --------------------------------------------------------

    if status == "possible":

        if evidence_strength > 0:

            final_confidence = (
                0.60 * match_confidence
                + 0.40 * evidence_strength
            )

            return round(
                min(final_confidence, 1.0),
                4
            )

        return round(
            match_confidence,
            4
        )

    return round(
        match_confidence,
        4
    )


# ============================================================
# MAKE DECISION
# ============================================================

def make_decision(
    requirement: str,
    match_result: Dict,
    evidence_result: Dict
) -> Dict:

    if not requirement:

        return {
            "requirement": "",
            "status": "unknown",
            "confidence": 0.0,
            "verified": False,
            "evidence_strength": "none",
            "evidence_sources": [],
            "reason": "No requirement was provided."
        }

    if not isinstance(
        match_result,
        dict
    ):

        match_result = {}

    if not isinstance(
        evidence_result,
        dict
    ):

        evidence_result = {}

    status = match_result.get(
        "status",
        "unknown"
    )

    confidence = calculate_final_confidence(
        match_result,
        evidence_result
    )

    raw_evidence_strength = float(
        evidence_result.get(
            "evidence_strength",
            0.0
        )
    )

    evidence_strength = classify_evidence_strength(
        raw_evidence_strength
    )

    evidence_sources = get_evidence_sources(
        evidence_result
    )

    # --------------------------------------------------------
    # Verification logic
    # --------------------------------------------------------

    verified = False

    if status == "matched":

        if evidence_sources:

            verified = True

        elif match_result.get(
            "relationship"
        ) == "exact":

            # Exact skill matches can be trusted even if
            # evidence extraction did not find another source.
            verified = True

    # Possible matches are never fully verified.
    if status == "possible":

        verified = False

    # Unknown matches are never verified.
    if status == "unknown":

        verified = False

    reason = generate_reason(
        requirement,
        match_result,
        evidence_result
    )

    return {
        "requirement": requirement,
        "status": status,
        "confidence": confidence,
        "verified": verified,
        "evidence_strength": evidence_strength,
        "evidence_sources": evidence_sources,
        "reason": reason
    }


# ============================================================
# BATCH DECISIONS
# ============================================================

def make_decisions(
    match_results: List[Dict],
    evidence_results: List[Dict]
) -> List[Dict]:

    if not match_results:

        return []

    decisions = []

    for index, match_result in enumerate(
        match_results
    ):

        requirement = match_result.get(
            "requirement",
            ""
        )

        if index < len(
            evidence_results
        ):

            evidence_result = (
                evidence_results[index]
            )

        else:

            evidence_result = {}

        decision = make_decision(
            requirement,
            match_result,
            evidence_result
        )

        decisions.append(
            decision
        )

    return decisions


# ============================================================
# COMPLETE REQUIREMENT ANALYSIS
# ============================================================

def analyze_requirement(
    requirement: str,
    match_result: Dict,
    evidence_result: Dict
) -> Dict:

    decision = make_decision(
        requirement,
        match_result,
        evidence_result
    )

    return {
        "requirement": requirement,
        "match": match_result,
        "evidence": evidence_result,
        "decision": decision
    }


# ============================================================
# ANALYZE MULTIPLE REQUIREMENTS
# ============================================================

def analyze_requirements(
    match_results: List[Dict],
    evidence_results: List[Dict]
) -> List[Dict]:

    if not match_results:

        return []

    results = []

    for index, match_result in enumerate(
        match_results
    ):

        requirement = match_result.get(
            "requirement",
            ""
        )

        if index < len(
            evidence_results
        ):

            evidence_result = (
                evidence_results[index]
            )

        else:

            evidence_result = {}

        results.append(
            analyze_requirement(
                requirement,
                match_result,
                evidence_result
            )
        )

    return results

# ============================================================
# DECISION ENGINE CLASS
# ============================================================

class DecisionEngine:
    """
    Object-oriented wrapper around the existing
    decision-engine functions.

    The underlying decision logic remains in:

        make_decision()
        make_decisions()
        analyze_requirement()
        analyze_requirements()

    This class provides a clean interface for
    TalentMatchEngine.
    """

    # ========================================================
    # ANALYZE ONE REQUIREMENT
    # ========================================================

    def analyze(
        self,
        requirement: str,
        match_result: Dict,
        evidence_result: Dict
    ) -> Dict:

        return analyze_requirement(
            requirement,
            match_result,
            evidence_result
        )

    # ========================================================
    # EVALUATE COMPLETE MATCH
    # ========================================================

    def evaluate(
        self,
        match_result: Dict
    ) -> Dict:
        """
        Evaluate a complete TalentAI match result.

        This method produces an overall decision based on
        the available skill matching, evidence and confidence.
        """

        if not isinstance(
            match_result,
            dict
        ):

            return {
                "decision": "review",
                "confidence": 0.0,
                "reason": (
                    "Invalid match result."
                )
            }

        skills = match_result.get(
            "skills",
            {}
        )

        required = skills.get(
            "required",
            {}
        )

        preferred = skills.get(
            "preferred",
            {}
        )

        matched = required.get(
            "matched",
            []
        )

        possible = required.get(
            "possible",
            []
        )

        unknown = required.get(
            "unknown",
            []
        )

        preferred_matched = preferred.get(
            "matched",
            []
        )

        # ----------------------------------------------------
        # No requirements
        # ----------------------------------------------------

        total_required = (
            len(matched)
            + len(possible)
            + len(unknown)
        )

        if total_required == 0:

            return {
                "decision": "review",
                "confidence": 0.0,
                "reason": (
                    "No required skills were available "
                    "for evaluation."
                )
            }

        # ----------------------------------------------------
        # Required skill ratio
        # ----------------------------------------------------

        matched_count = len(
            matched
        )

        possible_count = len(
            possible
        )

        required_score = (
            matched_count
            + 0.5 * possible_count
        ) / total_required

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        experience = match_result.get(
            "experience",
            {}
        )

        experience_status = experience.get(
            "status",
            "unknown"
        )

        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        education = match_result.get(
            "education",
            {}
        )

        education_status = education.get(
            "status",
            "unknown"
        )

        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------

        projects = match_result.get(
            "projects",
            {}
        )

        project_matches = projects.get(
            "matched_skills",
            []
        )

        # ----------------------------------------------------
        # Base confidence
        # ----------------------------------------------------

        confidence = (
            required_score
        )

        # Experience adjustment
        if experience_status == "matched":

            confidence += 0.15

        elif experience_status == "partial":

            confidence += 0.05

        # Education adjustment
        if education_status == "matched":

            confidence += 0.10

        # Project adjustment
        if project_matches:

            confidence += min(
                0.10,
                len(project_matches) * 0.02
            )

        # Preferred skills
        if preferred_matched:

            confidence += min(
                0.05,
                len(preferred_matched) * 0.01
            )

        confidence = round(
            min(
                confidence,
                1.0
            ),
            4
        )

        # ----------------------------------------------------
        # FINAL DECISION
        # ----------------------------------------------------

        if (
            required_score >= 0.80
            and experience_status in (
                "matched",
                "not_required"
            )
        ):

            decision = "strong_match"

            reason = (
                "The candidate satisfies most required "
                "skills and meets the experience requirement."
            )

        elif required_score >= 0.60:

            decision = "good_match"

            reason = (
                "The candidate satisfies a substantial "
                "portion of the required qualifications."
            )

        elif required_score >= 0.40:

            decision = "review"

            reason = (
                "The candidate has partial alignment "
                "with the job requirements and should "
                "be reviewed."
            )

        else:

            decision = "weak_match"

            reason = (
                "The candidate does not satisfy enough "
                "of the required qualifications."
            )

        # ----------------------------------------------------
        # Experience warning
        # ----------------------------------------------------

        if experience_status == "unknown":

            reason += (
                " Experience could not be reliably "
                "determined from the resume."
            )

        elif experience_status == "partial":

            reason += (
                " The candidate appears to have less "
                "experience than required."
            )

        return {
            "decision": decision,
            "confidence": confidence,
            "reason": reason,
            "required_skill_score": round(
                required_score,
                4
            ),
            "matched_required": matched_count,
            "possible_required": possible_count,
            "unknown_required": len(
                unknown
            ),
            "preferred_matched": len(
                preferred_matched
            ),
            "experience_status": experience_status,
            "education_status": education_status
        }

    # ========================================================
    # DECIDE
    # ========================================================

    def decide(
        self,
        match_result: Dict
    ) -> Dict:

        return self.evaluate(
            match_result
        )

    # ========================================================
    # DECIDE ONE REQUIREMENT
    # ========================================================

    def make_decision(
        self,
        requirement: str,
        match_result: Dict,
        evidence_result: Dict
    ) -> Dict:

        return make_decision(
            requirement,
            match_result,
            evidence_result
        )