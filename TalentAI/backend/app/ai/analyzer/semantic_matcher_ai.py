from typing import List, Dict

from app.ai.embeddings.embedding_service import (
    EmbeddingService
)


# ============================================================
# CONFIGURATION
# ============================================================

# Similarity above this value is considered a strong match.
STRONG_MATCH_THRESHOLD = 0.65

# Similarity above this value is considered a possible match.
POSSIBLE_MATCH_THRESHOLD = 0.50


# ============================================================
# AI SEMANTIC MATCHER
# ============================================================

class AISemanticMatcher:

    def __init__(self):

        self.embedding_service = EmbeddingService()

    # ========================================================
    # MATCH SINGLE REQUIREMENT
    # ========================================================

    def match_requirement(
        self,
        requirement: str,
        candidate_skills: List[str]
    ) -> Dict:

        # ----------------------------------------------------
        # Empty requirement
        # ----------------------------------------------------

        if not requirement:

            return {
                "requirement": requirement,
                "status": "unknown",
                "confidence": 0.0,
                "evidence": [],
                "match_type": "none"
            }

        # ----------------------------------------------------
        # Empty candidate skills
        # ----------------------------------------------------

        if not candidate_skills:

            return {
                "requirement": requirement,
                "status": "unknown",
                "confidence": 0.0,
                "evidence": [],
                "match_type": "none"
            }

        # ----------------------------------------------------
        # Find most semantically similar skill
        # ----------------------------------------------------

        result = self.embedding_service.find_most_similar(
            requirement,
            candidate_skills
        )

        matched_skill = result.get(
            "match"
        )

        similarity = result.get(
            "similarity",
            0.0
        )

        # ----------------------------------------------------
        # Strong semantic match
        # ----------------------------------------------------

        if similarity >= STRONG_MATCH_THRESHOLD:

            return {
                "requirement": requirement,
                "status": "matched",
                "confidence": similarity,
                "evidence": [
                    matched_skill
                ] if matched_skill else [],
                "match_type": "semantic"
            }

        # ----------------------------------------------------
        # Possible semantic match
        # ----------------------------------------------------

        if similarity >= POSSIBLE_MATCH_THRESHOLD:

            return {
                "requirement": requirement,
                "status": "possible",
                "confidence": similarity,
                "evidence": [
                    matched_skill
                ] if matched_skill else [],
                "match_type": "semantic"
            }

        # ----------------------------------------------------
        # No meaningful semantic match
        # ----------------------------------------------------

        return {
            "requirement": requirement,
            "status": "unknown",
            "confidence": similarity,
            "evidence": [],
            "match_type": "semantic"
        }

    # ========================================================
    # MATCH MULTIPLE REQUIREMENTS
    # ========================================================

    def match_requirements(
        self,
        requirements: List[str],
        candidate_skills: List[str]
    ) -> List[Dict]:

        if not requirements:

            return []

        results = []

        for requirement in requirements:

            result = self.match_requirement(
                requirement,
                candidate_skills
            )

            results.append(
                result
            )

        return results

    # ========================================================
    # MATCH RESUME AGAINST JOB
    # ========================================================

    def match_job(
        self,
        required_skills: List[str],
        preferred_skills: List[str],
        candidate_skills: List[str]
    ) -> Dict:

        # ----------------------------------------------------
        # Required skills
        # ----------------------------------------------------

        required_results = self.match_requirements(
            required_skills,
            candidate_skills
        )

        # ----------------------------------------------------
        # Preferred skills
        # ----------------------------------------------------

        preferred_results = self.match_requirements(
            preferred_skills,
            candidate_skills
        )

        # ----------------------------------------------------
        # Separate required results
        # ----------------------------------------------------

        required_matched = []
        required_possible = []
        required_unknown = []

        for result in required_results:

            if result["status"] == "matched":

                required_matched.append(
                    result
                )

            elif result["status"] == "possible":

                required_possible.append(
                    result
                )

            else:

                required_unknown.append(
                    result
                )

        # ----------------------------------------------------
        # Separate preferred results
        # ----------------------------------------------------

        preferred_matched = []
        preferred_possible = []
        preferred_unknown = []

        for result in preferred_results:

            if result["status"] == "matched":

                preferred_matched.append(
                    result
                )

            elif result["status"] == "possible":

                preferred_possible.append(
                    result
                )

            else:

                preferred_unknown.append(
                    result
                )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        return {

            "required": {

                "matched":
                    required_matched,

                "possible":
                    required_possible,

                "unknown":
                    required_unknown
            },

            "preferred": {

                "matched":
                    preferred_matched,

                "possible":
                    preferred_possible,

                "unknown":
                    preferred_unknown
            }
        }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def match_requirement_ai(
    requirement: str,
    candidate_skills: List[str]
) -> Dict:

    matcher = AISemanticMatcher()

    return matcher.match_requirement(
        requirement,
        candidate_skills
    )


# ============================================================
# MULTIPLE REQUIREMENTS
# ============================================================

def match_requirements_ai(
    requirements: List[str],
    candidate_skills: List[str]
) -> List[Dict]:

    matcher = AISemanticMatcher()

    return matcher.match_requirements(
        requirements,
        candidate_skills
    )