from typing import Dict, List


class SkillRelationshipEngine:
    """
    Understands relationships between technical skills.

    Example:
        TensorFlow -> Deep Learning -> Machine Learning -> AI
        PostgreSQL -> SQL
        Pandas -> Data Analysis -> Data Science
    """

    # ---------------------------------------------------------
    # STRONG RELATIONSHIPS
    # ---------------------------------------------------------

    STRONG_RELATIONSHIPS = {

        "tensorflow": {
            "deep learning",
            "machine learning",
            "artificial intelligence",
        },

        "pytorch": {
            "deep learning",
            "machine learning",
            "artificial intelligence",
        },

        "postgresql": {
            "sql",
        },

        "mysql": {
            "sql",
        },

        "pandas": {
            "data analysis",
            "data science",
        },

        "numpy": {
            "data science",
            "machine learning",
            "data analysis",
        },

        "scikit-learn": {
            "machine learning",
            "data science",
        },
    }

    # ---------------------------------------------------------
    # RELATED RELATIONSHIPS
    # ---------------------------------------------------------

    RELATED_RELATIONSHIPS = {

        "deep learning": {
            "machine learning",
            "artificial intelligence",
        },

        "machine learning": {
            "artificial intelligence",
            "data science",
            "data analysis",
        },

        "data analysis": {
            "data science",
            "machine learning",
        },

        "data science": {
            "machine learning",
            "data analysis",
            "artificial intelligence",
        },

        "artificial intelligence": {
            "machine learning",
            "deep learning",
            "data science",
        },

        # "python": {
        #     "data science",
        #     "machine learning",
        #     "artificial intelligence",
        # },
    }

    # ---------------------------------------------------------
    # SKILL ALIASES
    # ---------------------------------------------------------

    SKILL_ALIASES = {

        "py": "python",

        "ml": "machine learning",

        "ai": "artificial intelligence",

        "artificial intelligence": "artificial intelligence",

        "dl": "deep learning",

        "data analytics": "data analysis",

        "data analyst": "data analysis",

        "postgres": "postgresql",

        "postgres sql": "postgresql",

        "sklearn": "scikit-learn",

        "scikit learn": "scikit-learn",
    }

    # ---------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------

    def normalize_skill(self, skill: str) -> str:
        """
        Convert a skill into a canonical representation.
        """

        if not skill:
            return ""

        normalized = skill.strip().lower()

        normalized = " ".join(normalized.split())

        return self.SKILL_ALIASES.get(
            normalized,
            normalized
        )

    # ---------------------------------------------------------
    # DIRECT RELATIONSHIP
    # ---------------------------------------------------------

    def find_relationship(
        self,
        required_skill: str,
        candidate_skill: str
    ) -> Dict:
        """
        Determine the relationship between two skills.
        """

        required = self.normalize_skill(required_skill)
        candidate = self.normalize_skill(candidate_skill)

        # Empty input
        if not required or not candidate:
            return {
                "required_skill": required_skill,
                "candidate_skill": candidate_skill,
                "relationship": "none",
                "confidence": 0.0,
            }

        # Exact match
        if required == candidate:
            return {
                "required_skill": required_skill,
                "candidate_skill": candidate_skill,
                "relationship": "exact",
                "confidence": 1.0,
            }

        # Strong relationship
        strong_skills = self.STRONG_RELATIONSHIPS.get(
            required,
            set()
        )

        if candidate in strong_skills:
            return {
                "required_skill": required_skill,
                "candidate_skill": candidate_skill,
                "relationship": "strong",
                "confidence": 0.85,
            }

        # Reverse strong relationship
        reverse_strong = self.STRONG_RELATIONSHIPS.get(
            candidate,
            set()
        )

        if required in reverse_strong:
            return {
                "required_skill": required_skill,
                "candidate_skill": candidate_skill,
                "relationship": "strong",
                "confidence": 0.85,
            }

        # Related relationship
        related_skills = self.RELATED_RELATIONSHIPS.get(
            required,
            set()
        )

        if candidate in related_skills:
            return {
                "required_skill": required_skill,
                "candidate_skill": candidate_skill,
                "relationship": "related",
                "confidence": 0.65,
            }

        # Reverse related relationship
        reverse_related = self.RELATED_RELATIONSHIPS.get(
            candidate,
            set()
        )

        if required in reverse_related:
            return {
                "required_skill": required_skill,
                "candidate_skill": candidate_skill,
                "relationship": "related",
                "confidence": 0.65,
            }

        # No relationship
        return {
            "required_skill": required_skill,
            "candidate_skill": candidate_skill,
            "relationship": "none",
            "confidence": 0.0,
        }

    # ---------------------------------------------------------
    # FIND ALL RELATED SKILLS
    # ---------------------------------------------------------

    def find_related_skills(
        self,
        skill: str
    ) -> List[Dict]:
        """
        Return all skills related to the given skill.
        """

        normalized_skill = self.normalize_skill(skill)

        if not normalized_skill:
            return []

        relationships = []

        # Strong relationships
        for related_skill in self.STRONG_RELATIONSHIPS.get(
            normalized_skill,
            set()
        ):
            relationships.append({
                "skill": related_skill,
                "relationship": "strong",
                "confidence": 0.85,
            })

        # Related relationships
        for related_skill in self.RELATED_RELATIONSHIPS.get(
            normalized_skill,
            set()
        ):
            relationships.append({
                "skill": related_skill,
                "relationship": "related",
                "confidence": 0.65,
            })

        # Also check reverse relationships
        for source_skill, targets in self.STRONG_RELATIONSHIPS.items():

            if normalized_skill in targets:

                if not any(
                    item["skill"] == source_skill
                    for item in relationships
                ):
                    relationships.append({
                        "skill": source_skill,
                        "relationship": "strong",
                        "confidence": 0.85,
                    })

        for source_skill, targets in self.RELATED_RELATIONSHIPS.items():

            if normalized_skill in targets:

                if not any(
                    item["skill"] == source_skill
                    for item in relationships
                ):
                    relationships.append({
                        "skill": source_skill,
                        "relationship": "related",
                        "confidence": 0.65,
                    })

        return relationships

    # ---------------------------------------------------------
    # MATCH REQUIREMENT
    # ---------------------------------------------------------

    def match_requirement(
        self,
        required_skill: str,
        candidate_skills: List[str]
    ) -> Dict:
        """
        Compare one required skill against all candidate skills.

        Returns the strongest relationship found.
        """

        if not required_skill or not candidate_skills:
            return {
                "required_skill": required_skill,
                "status": "unknown",
                "best_match": None,
                "confidence": 0.0,
                "relationships": [],
            }

        relationships = []

        for candidate_skill in candidate_skills:

            result = self.find_relationship(
                required_skill,
                candidate_skill
            )

            if result["relationship"] != "none":
                relationships.append(result)

        # No relationship
        if not relationships:
            return {
                "required_skill": required_skill,
                "status": "unknown",
                "best_match": None,
                "confidence": 0.0,
                "relationships": [],
            }

        # Strongest relationship
        relationships.sort(
            key=lambda item: item["confidence"],
            reverse=True
        )

        best_match = relationships[0]

        if best_match["relationship"] == "exact":
            status = "matched"

        elif best_match["relationship"] == "strong":
            status = "strongly_related"

        else:
            status = "related"

        return {
            "required_skill": required_skill,
            "status": status,
            "best_match": best_match,
            "confidence": best_match["confidence"],
            "relationships": relationships,
        }

    # ---------------------------------------------------------
    # COMPATIBILITY WRAPPER
    # ---------------------------------------------------------

    def match(
        self,
        required_skill: str,
        candidate_skills: List[str]
    ) -> Dict:
        """
        Compatibility wrapper.
        """

        return self.match_requirement(
            required_skill,
            candidate_skills
            
        )