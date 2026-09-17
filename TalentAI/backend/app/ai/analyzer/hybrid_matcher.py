from typing import List, Dict

from app.matcher.semantic_matcher import match_concept
from app.ai.analyzer.semantic_matcher_ai import AISemanticMatcher
from app.ai.analyzer.skill_relationship_engine import SkillRelationshipEngine


# ============================================================
# CONFIGURATION
# ============================================================

SEMANTIC_STRONG_THRESHOLD = 0.65
SEMANTIC_POSSIBLE_THRESHOLD = 0.50


# ============================================================
# CANONICAL SKILL NORMALIZATION
# ============================================================

SKILL_ALIASES = {

    # --------------------------------------------------------
    # Programming languages
    # --------------------------------------------------------

    "python": "python",
    "py": "python",

    "javascript": "javascript",
    "java script": "javascript",
    "js": "javascript",

    "typescript": "typescript",
    "ts": "typescript",

    # --------------------------------------------------------
    # Data / ML libraries
    # --------------------------------------------------------

    "pandas": "pandas",
    "panda": "pandas",

    "numpy": "numpy",
    "numpy library": "numpy",

    "scikit-learn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit_learn": "scikit-learn",

    # --------------------------------------------------------
    # Machine Learning
    # --------------------------------------------------------

    "machine learning": "machine learning",
    "ml": "machine learning",

    "deep learning": "deep learning",
    "dl": "deep learning",

    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "sql": "sql",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "postgres": "postgresql",

    # --------------------------------------------------------
    # Web
    # --------------------------------------------------------

    "html": "html",
    "css": "css",

    "fastapi": "fastapi",
    "fast api": "fastapi",

    "django": "django",
    "flask": "flask",

    # --------------------------------------------------------
    # Cloud
    # --------------------------------------------------------

    "aws": "aws",
    "amazon web services": "aws",

    "azure": "azure",
    "microsoft azure": "azure",

    "gcp": "gcp",
    "google cloud": "gcp",
    "google cloud platform": "gcp",

    # --------------------------------------------------------
    # Data Science
    # --------------------------------------------------------

    "data science": "data science",

    "data analysis": "data analysis",

    "data analytics": "data analysis",

    "data preprocessing": "data preprocessing",

    "data visualization": "data visualization",

    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    "jupyter": "jupyter notebook",
    "jupyter notebook": "jupyter notebook",

    "tableau": "tableau",

    "power bi": "power bi",
    "powerbi": "power bi",

    # --------------------------------------------------------
    # Version control
    # --------------------------------------------------------

    "git": "git",
    "github": "github",
}


# ============================================================
# NORMALIZE ONE SKILL
# ============================================================

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill into a canonical representation.

    Examples:
        Python       -> python
        PYTHON       -> python
        sklearn      -> scikit-learn
        Scikit Learn -> scikit-learn
        Pandas       -> pandas
    """

    if not skill:
        return ""

    normalized = str(skill).strip().lower()

    # Remove common punctuation variations
    normalized = normalized.replace("_", " ")
    normalized = normalized.replace("–", "-")
    normalized = normalized.replace("—", "-")

    # Normalize repeated whitespace
    normalized = " ".join(normalized.split())

    # Remove trailing punctuation
    normalized = normalized.rstrip(".,;:")

    # Alias lookup
    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]

    return normalized


# ============================================================
# NORMALIZE CANDIDATE SKILLS
# ============================================================

def normalize_candidate_skills(
    candidate_skills: List[str]
) -> List[str]:
    """
    Normalize and deduplicate candidate skills.
    """

    normalized_skills = []

    for skill in candidate_skills:

        if not skill:
            continue

        canonical = normalize_skill(skill)

        if canonical and canonical not in normalized_skills:
            normalized_skills.append(canonical)

    return normalized_skills


# ============================================================
# HYBRID MATCHER
# ============================================================

class HybridMatcher:

    def __init__(self):

        # AI semantic matcher
        self.ai_matcher = AISemanticMatcher()

        # Skill relationship intelligence
        self.relationship_engine = SkillRelationshipEngine()

    # ========================================================
    # DIRECT CANONICAL MATCH
    # ========================================================

    def _direct_skill_match(
        self,
        requirement: str,
        candidate_skills: List[str]
    ) -> Dict:
        """
        Perform an exact canonical skill match.
        """

        normalized_requirement = normalize_skill(requirement)

        normalized_candidates = normalize_candidate_skills(
            candidate_skills
        )

        if (
            normalized_requirement
            and normalized_requirement in normalized_candidates
        ):

            # Find the original candidate skill for evidence
            evidence = []

            for skill in candidate_skills:

                if normalize_skill(skill) == normalized_requirement:

                    evidence.append(skill)

            return {
                "matched": True,
                "requirement": requirement,
                "confidence": 1.0,
                "evidence": evidence,
            }

        return {
            "matched": False,
            "requirement": requirement,
            "confidence": 0.0,
            "evidence": [],
        }

    # ========================================================
    # MATCH ONE REQUIREMENT
    # ========================================================

    def match_requirement(
        self,
        requirement: str,
        candidate_skills: List[str]
    ) -> Dict:

        # ----------------------------------------------------
        # Empty input
        # ----------------------------------------------------

        if not requirement or not candidate_skills:

            return {
                "requirement": requirement,
                "status": "unknown",
                "confidence": 0.0,
                "evidence": [],
                "rule_match": False,
                "semantic_similarity": 0.0,
                "relationship": "none",
                "match_source": "none"
            }

        # ====================================================
        # STEP 0: CANONICAL EXACT MATCH
        # ====================================================

        direct_result = self._direct_skill_match(
            requirement,
            candidate_skills
        )

        if direct_result["matched"]:

            return {
                "requirement": requirement,
                "status": "matched",
                "confidence": 1.0,
                "evidence": direct_result["evidence"],
                "rule_match": True,
                "semantic_similarity": 1.0,
                "relationship": "exact",
                "match_source": "canonical"
            }

        # ====================================================
        # NORMALIZED CANDIDATE SKILLS
        # ====================================================

        normalized_candidates = normalize_candidate_skills(
            candidate_skills
        )

        # ====================================================
        # STEP 1: RULE-BASED MATCH
        # ====================================================

        rule_result = match_concept(
            requirement,
            normalized_candidates
        )

        rule_status = rule_result.get(
            "status",
            "unknown"
        )

        rule_confidence = rule_result.get(
            "confidence",
            0.0
        )

        rule_evidence = rule_result.get(
            "evidence",
            []
        )

        # ====================================================
        # EXACT RULE MATCH
        # ====================================================

        if rule_status == "exact":

            return {
                "requirement": requirement,
                "status": "matched",
                "confidence": 1.0,
                "evidence": rule_evidence,
                "rule_match": True,
                "semantic_similarity": 1.0,
                "relationship": "exact",
                "match_source": "rule"
            }

        # ====================================================
        # RELATED RULE MATCH
        # ====================================================

        if rule_status == "related":

            # Ask AI to strengthen the rule-based relationship
            ai_result = self.ai_matcher.match_requirement(
                requirement,
                normalized_candidates
            )

            semantic_similarity = ai_result.get(
                "confidence",
                0.0
            )

            confidence = max(
                rule_confidence,
                semantic_similarity
            )

            return {
                "requirement": requirement,
                "status": "matched",
                "confidence": round(
                    confidence,
                    4
                ),
                "evidence": rule_evidence,
                "rule_match": True,
                "semantic_similarity": round(
                    semantic_similarity,
                    4
                ),
                "relationship": "related",
                "match_source": "hybrid"
            }

        # ====================================================
        # STEP 2: SKILL RELATIONSHIP MATCH
        # ====================================================

        relationship_result = (
            self.relationship_engine.match_requirement(
                requirement,
                normalized_candidates
            )
        )

        relationship_status = relationship_result.get(
            "status",
            "unknown"
        )

        relationship_confidence = relationship_result.get(
            "confidence",
            0.0
        )

        best_relationship = relationship_result.get(
            "best_match"
        )

        relationship_evidence = []

        if best_relationship:

            candidate_skill = best_relationship.get(
                "candidate_skill"
            )

            if candidate_skill:

                relationship_evidence.append(
                    candidate_skill
                )

        # ----------------------------------------------------
        # STRONG RELATIONSHIP
        # ----------------------------------------------------

        if relationship_status == "strongly_related":

            return {
                "requirement": requirement,
                "status": "possible",
                "confidence": round(
                    relationship_confidence,
                    4
                ),
                "evidence": relationship_evidence,
                "rule_match": False,
                "semantic_similarity": 0.0,
                "relationship": "strong_related",
                "match_source": "relationship"
            }

        # ----------------------------------------------------
        # GENERAL RELATED SKILL
        # ----------------------------------------------------

        if relationship_status == "related":

            return {
                "requirement": requirement,
                "status": "possible",
                "confidence": round(
                    relationship_confidence,
                    4
                ),
                "evidence": relationship_evidence,
                "rule_match": False,
                "semantic_similarity": 0.0,
                "relationship": "related",
                "match_source": "relationship"
            }

        # ====================================================
        # STEP 3: AI SEMANTIC MATCH
        # ====================================================

        ai_result = self.ai_matcher.match_requirement(
            requirement,
            normalized_candidates
        )

        semantic_similarity = ai_result.get(
            "confidence",
            0.0
        )

        semantic_evidence = ai_result.get(
            "evidence",
            []
        )

        # ====================================================
        # STRONG AI MATCH
        # ====================================================

        if semantic_similarity >= SEMANTIC_STRONG_THRESHOLD:

            return {
                "requirement": requirement,
                "status": "matched",
                "confidence": round(
                    semantic_similarity,
                    4
                ),
                "evidence": semantic_evidence,
                "rule_match": False,
                "semantic_similarity": round(
                    semantic_similarity,
                    4
                ),
                "relationship": "semantic",
                "match_source": "ai"
            }

        # ====================================================
        # POSSIBLE AI RELATIONSHIP
        # ====================================================

        if semantic_similarity >= SEMANTIC_POSSIBLE_THRESHOLD:

            return {
                "requirement": requirement,
                "status": "possible",
                "confidence": round(
                    semantic_similarity,
                    4
                ),
                "evidence": semantic_evidence,
                "rule_match": False,
                "semantic_similarity": round(
                    semantic_similarity,
                    4
                ),
                "relationship": "possible_related",
                "match_source": "ai"
            }

        # ====================================================
        # UNKNOWN
        # ====================================================

        return {
            "requirement": requirement,
            "status": "unknown",
            "confidence": round(
                semantic_similarity,
                4
            ),
            "evidence": [],
            "rule_match": False,
            "semantic_similarity": round(
                semantic_similarity,
                4
            ),
            "relationship": "none",
            "match_source": "ai"
        }

    # ========================================================
    # COMPATIBILITY METHOD
    # ========================================================

    def match(
        self,
        requirement: str,
        candidate_skills: List[str]
    ) -> Dict:
        """
        Compatibility wrapper used by TalentMatchEngine.
        """

        return self.match_requirement(
            requirement,
            candidate_skills
        )

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

            results.append(result)

        return results

    # ========================================================
    # MATCH COMPLETE JOB
    # ========================================================

    def match_job(
        self,
        required_skills: List[str],
        preferred_skills: List[str],
        candidate_skills: List[str]
    ) -> Dict:

        required_results = self.match_requirements(
            required_skills,
            candidate_skills
        )

        preferred_results = self.match_requirements(
            preferred_skills,
            candidate_skills
        )

        # ----------------------------------------------------
        # REQUIRED SKILLS
        # ----------------------------------------------------

        required_matched = []
        required_possible = []
        required_unknown = []

        for result in required_results:

            if result["status"] == "matched":

                required_matched.append(result)

            elif result["status"] == "possible":

                required_possible.append(result)

            else:

                required_unknown.append(result)

        # ----------------------------------------------------
        # PREFERRED SKILLS
        # ----------------------------------------------------

        preferred_matched = []
        preferred_possible = []
        preferred_unknown = []

        for result in preferred_results:

            if result["status"] == "matched":

                preferred_matched.append(result)

            elif result["status"] == "possible":

                preferred_possible.append(result)

            else:

                preferred_unknown.append(result)

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "required": {
                "matched": required_matched,
                "possible": required_possible,
                "unknown": required_unknown
            },

            "preferred": {
                "matched": preferred_matched,
                "possible": preferred_possible,
                "unknown": preferred_unknown
            }
        }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def hybrid_match_requirement(
    requirement: str,
    candidate_skills: List[str]
) -> Dict:

    matcher = HybridMatcher()

    return matcher.match_requirement(
        requirement,
        candidate_skills
    )