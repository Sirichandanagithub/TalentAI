from typing import Any


class RelevantExperienceAnalyzer:
    """
    Analyze how relevant a candidate's professional experience
    is to a target job.

    Responsibilities:
        1. Calculate job-title relevance
        2. Calculate skill relevance
        3. Get role duration from central experience matcher
        4. Calculate role-level relevance
        5. Calculate weighted relevant experience
        6. Calculate overall candidate experience

    Important:
        Date calculations are NOT duplicated here.

        The central experience matcher is responsible for:
            - start date
            - end date
            - duration months
            - duration years
    """

    # ============================================================
    # RELEVANCE WEIGHTS
    # ============================================================

    TITLE_WEIGHT = 0.40
    SKILL_WEIGHT = 0.60

    # ============================================================
    # STATUS THRESHOLDS
    # ============================================================

    HIGH_THRESHOLD = 0.75
    MODERATE_THRESHOLD = 0.50

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):
        pass

    # ============================================================
    # NORMALIZE TEXT
    # ============================================================

    def _normalize_text(
        self,
        value: Any
    ) -> str:
        """
        Normalize text for comparison.
        """

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
        )

    # ============================================================
    # EXTRACT ROLE TITLE
    # ============================================================

    def _get_role_title(
        self,
        role: dict
    ) -> str:
        """
        Extract role title safely.
        """

        return self._normalize_text(
            role.get(
                "job_title",
                ""
            )
        )

    # ============================================================
    # EXTRACT ROLE COMPANY
    # ============================================================

    def _get_role_company(
        self,
        role: dict
    ) -> str:
        """
        Extract company safely.
        """

        return self._normalize_text(
            role.get(
                "company",
                ""
            )
        )

    # ============================================================
    # TITLE RELEVANCE
    # ============================================================

    def _calculate_title_relevance(
        self,
        role: dict,
        target_title: str
    ) -> float:
        """
        Calculate basic title relevance.

        Returns:
            1.0 = exact match
            0.75 = strong partial match
            0.50 = weak/related match
            0.0 = no match
        """

        role_title = self._get_role_title(
            role
        )

        target_title = self._normalize_text(
            target_title
        )

        if not role_title or not target_title:
            return 0.0

        if role_title == target_title:
            return 1.0

        # --------------------------------------------------------
        # Remove common role noise
        # --------------------------------------------------------

        role_title_clean = role_title

        if "@" in role_title_clean:
            role_title_clean = (
                role_title_clean.split("@")[0]
                .strip()
            )

        if "[" in role_title_clean:
            role_title_clean = (
                role_title_clean.split("[")[0]
                .strip()
            )

        role_tokens = set(
            role_title_clean.split()
        )

        target_tokens = set(
            target_title.split()
        )

        if not role_tokens or not target_tokens:
            return 0.0

        overlap = role_tokens.intersection(
            target_tokens
        )

        overlap_ratio = (
            len(overlap)
            /
            len(target_tokens)
        )

        if overlap_ratio >= 0.75:
            return 0.75

        if overlap_ratio >= 0.50:
            return 0.50

        # --------------------------------------------------------
        # Related AI / Data roles
        # --------------------------------------------------------

        related_role_terms = {
            "data scientist": {
                "data",
                "scientist",
                "machine",
                "learning",
                "ai",
                "artificial",
                "intelligence",
                "ml"
            },
            "machine learning engineer": {
                "machine",
                "learning",
                "ml",
                "ai",
                "artificial",
                "intelligence",
                "data"
            },
            "ai engineer": {
                "ai",
                "artificial",
                "intelligence",
                "machine",
                "learning",
                "ml",
                "data"
            }
        }

        target_related_terms = (
            related_role_terms.get(
                target_title,
                set()
            )
        )

        if target_related_terms:
            role_words = set(
                role_title_clean.split()
            )

            related_overlap = (
                role_words.intersection(
                    target_related_terms
                )
            )

            if len(related_overlap) >= 2:
                return 0.50

        return 0.0

    # ============================================================
    # SKILL RELEVANCE
    # ============================================================

    def _calculate_skill_relevance(
        self,
        role: dict,
        required_skills: list
    ) -> tuple[float, list, list, list]:
        """
        Calculate relevance based on skills.

        Returns:
            (
                score,
                matched_skills,
                possible_skills,
                unknown_skills
            )
        """

        if not required_skills:
            return (
                0.0,
                [],
                [],
                []
            )

        # --------------------------------------------------------
        # Collect all text from role
        # --------------------------------------------------------

        role_text_parts = []

        for key in [
            "job_title",
            "company",
            "description",
            "raw_text",
            "location"
        ]:

            value = role.get(
                key
            )

            if value:
                role_text_parts.append(
                    str(value)
                )

        # --------------------------------------------------------
        # Skills may already be present
        # --------------------------------------------------------

        role_skills = role.get(
            "skills",
            []
        )

        if isinstance(
            role_skills,
            dict
        ):

            for values in role_skills.values():

                if isinstance(
                    values,
                    list
                ):

                    role_text_parts.extend(
                        [
                            str(value)
                            for value in values
                        ]
                    )

                elif values:

                    role_text_parts.append(
                        str(values)
                    )

        elif isinstance(
            role_skills,
            list
        ):

            role_text_parts.extend(
                [
                    str(skill)
                    for skill in role_skills
                ]
            )

        role_text = " ".join(
            role_text_parts
        ).lower()

        matched_skills = []
        possible_skills = []
        unknown_skills = []

        # ========================================================
        # ALIASES
        # ========================================================

        aliases = {
            "python": [
                "python",
                "py"
            ],

            "sql": [
                "sql",
                "mysql",
                "postgresql",
                "postgres"
            ],

            "machine learning": [
                "machine learning",
                "ml"
            ],

            "artificial intelligence": [
                "artificial intelligence",
                "ai"
            ],

            "data analysis": [
                "data analysis",
                "data analytics",
                "data analyst"
            ],

            "data science": [
                "data science",
                "data scientist"
            ],

            "scikit-learn": [
                "scikit-learn",
                "scikit learn",
                "sklearn"
            ],

            "pandas": [
                "pandas",
                "panda"
            ],

            "tensorflow": [
                "tensorflow"
            ]
        }

        # ========================================================
        # RELATED CONCEPTS
        # ========================================================

        related = {
            "machine learning": [
                "deep learning",
                "artificial intelligence"
            ],

            "artificial intelligence": [
                "machine learning",
                "deep learning"
            ],

            "data science": [
                "data analysis",
                "machine learning"
            ],

            "data analysis": [
                "data science",
                "pandas"
            ],

            "sql": [
                "mysql",
                "postgresql"
            ]
        }

        # ========================================================
        # MATCH EACH REQUIRED SKILL
        # ========================================================

        for skill in required_skills:

            skill_text = self._normalize_text(
                skill
            )

            if not skill_text:
                continue

            # ----------------------------------------------------
            # Direct match
            # ----------------------------------------------------

            if skill_text in role_text:

                matched_skills.append(
                    skill
                )

                continue

            # ----------------------------------------------------
            # Alias match
            # ----------------------------------------------------

            matched_alias = False

            for alias in aliases.get(
                skill_text,
                [skill_text]
            ):

                if alias in role_text:

                    matched_skills.append(
                        skill
                    )

                    matched_alias = True

                    break

            if matched_alias:
                continue

            # ----------------------------------------------------
            # Related concept
            # ----------------------------------------------------

            is_related = False

            for related_skill in related.get(
                skill_text,
                []
            ):

                if related_skill in role_text:

                    possible_skills.append(
                        skill
                    )

                    is_related = True

                    break

            if is_related:
                continue

            # ----------------------------------------------------
            # Unknown
            # ----------------------------------------------------

            unknown_skills.append(
                skill
            )

        # ========================================================
        # CALCULATE SKILL SCORE
        # ========================================================

        total = (
            len(matched_skills)
            +
            len(possible_skills)
            +
            len(unknown_skills)
        )

        if total == 0:

            score = 0.0

        else:

            score = (
                len(matched_skills)
                +
                (
                    len(possible_skills)
                    * 0.50
                )
            ) / total

        return (
            round(
                score,
                4
            ),
            matched_skills,
            possible_skills,
            unknown_skills
        )

    # ============================================================
    # ROLE DURATION FROM CENTRAL MATCHER
    # ============================================================

    def _get_role_duration_from_matcher(
        self,
        resume: dict,
        role: dict,
        required_years: float = 0
    ) -> float | None:
        """
        Get the duration of a specific role from the central
        experience matcher.

        Date calculations are intentionally NOT performed here.
        """

        try:

            from app.matcher.experience_matcher import (
                match_experience
            )

            result = match_experience(
                resume,
                {
                    "minimum_years": required_years
                }
            )

            details = result.get(
                "experience_details",
                []
            )

            if not details:
                return None

            role_title = self._normalize_text(
                role.get(
                    "job_title",
                    ""
                )
            )

            role_company = self._normalize_text(
                role.get(
                    "company",
                    ""
                )
            )

            # ====================================================
            # TITLE + COMPANY
            # ====================================================

            for detail in details:

                detail_title = self._normalize_text(
                    detail.get(
                        "job_title",
                        ""
                    )
                )

                detail_company = self._normalize_text(
                    detail.get(
                        "company",
                        ""
                    )
                )

                title_match = (
                    role_title
                    and detail_title
                    and (
                        role_title == detail_title
                        or role_title in detail_title
                        or detail_title in role_title
                    )
                )

                company_match = (
                    role_company
                    and detail_company
                    and (
                        role_company == detail_company
                        or role_company in detail_company
                        or detail_company in role_company
                    )
                )

                if title_match and (
                    not role_company
                    or company_match
                ):

                    duration = detail.get(
                        "duration_years"
                    )

                    if duration is not None:
                        return float(
                            duration
                        )

            # ====================================================
            # TITLE ONLY
            # ====================================================

            for detail in details:

                detail_title = self._normalize_text(
                    detail.get(
                        "job_title",
                        ""
                    )
                )

                if (
                    role_title
                    and detail_title
                    and (
                        role_title == detail_title
                        or role_title in detail_title
                        or detail_title in role_title
                    )
                ):

                    duration = detail.get(
                        "duration_years"
                    )

                    if duration is not None:
                        return float(
                            duration
                        )

            # ====================================================
            # RAW TEXT FALLBACK
            # ====================================================

            role_raw_text = self._normalize_text(
                role.get(
                    "raw_text",
                    ""
                )
            )

            if role_raw_text:

                for detail in details:

                    detail_title = self._normalize_text(
                        detail.get(
                            "job_title",
                            ""
                        )
                    )

                    if (
                        detail_title
                        and detail_title in role_raw_text
                    ):

                        duration = detail.get(
                            "duration_years"
                        )

                        if duration is not None:
                            return float(
                                duration
                            )

        except Exception:
            return None

        return None

    # ============================================================
    # DETERMINE RELEVANCE STATUS
    # ============================================================

    def _get_relevance_status(
        self,
        relevance_score: float
    ) -> str:
        """
        Convert relevance score into status.
        """

        if relevance_score >= self.HIGH_THRESHOLD:
            return "high"

        if relevance_score >= self.MODERATE_THRESHOLD:
            return "moderate"

        return "low"

    # ============================================================
    # ANALYZE SINGLE ROLE
    # ============================================================

    def analyze_role(
        self,
        resume: dict,
        role: dict,
        target_title: str = "",
        required_skills: list | None = None,
        required_years: float = 0
    ) -> dict:
        """
        Analyze one professional experience role.
        """

        if not role:

            return {
                "job_title": None,
                "company": None,
                "location": None,
                "duration_years": None,
                "title_relevance": 0.0,
                "skill_relevance": 0.0,
                "relevance": 0.0,
                "status": "low",
                "matched_skills": [],
                "possible_skills": [],
                "unknown_skills": [],
                "evidence_strength": "low"
            }

        required_skills = (
            required_skills
            if required_skills
            else []
        )

        # ========================================================
        # TITLE RELEVANCE
        # ========================================================

        title_relevance = (
            self._calculate_title_relevance(
                role,
                target_title
            )
        )

        # ========================================================
        # SKILL RELEVANCE
        # ========================================================

        (
            skill_relevance,
            matched_skills,
            possible_skills,
            unknown_skills
        ) = self._calculate_skill_relevance(
            role,
            required_skills
        )

        # ========================================================
        # OVERALL RELEVANCE
        # ========================================================

        relevance = (
            (
                title_relevance
                *
                self.TITLE_WEIGHT
            )
            +
            (
                skill_relevance
                *
                self.SKILL_WEIGHT
            )
        )

        relevance = round(
            relevance,
            4
        )

        # ========================================================
        # STATUS
        # ========================================================

        status = self._get_relevance_status(
            relevance
        )

        # ========================================================
        # ROLE DURATION
        # ========================================================

        duration_years = (
            self._get_role_duration_from_matcher(
                resume,
                role,
                required_years
            )
        )

        # ========================================================
        # EVIDENCE STRENGTH
        # ========================================================

        if (
            title_relevance >= 0.75
            and skill_relevance >= 0.75
        ):

            evidence_strength = "high"

        elif (
            title_relevance >= 0.50
            or skill_relevance >= 0.50
        ):

            evidence_strength = "moderate"

        else:

            evidence_strength = "low"

        # ========================================================
        # RESULT
        # ========================================================

        return {
            "job_title": role.get(
                "job_title"
            ),

            "company": role.get(
                "company"
            ),

            "location": role.get(
                "location"
            ),

            "duration_years": duration_years,

            "title_relevance": round(
                title_relevance,
                4
            ),

            "skill_relevance": round(
                skill_relevance,
                4
            ),

            "relevance": relevance,

            "status": status,

            "matched_skills": matched_skills,

            "possible_skills": possible_skills,

            "unknown_skills": unknown_skills,

            "evidence_strength": evidence_strength
        }

    # ============================================================
    # CALCULATE RELEVANT YEARS
    # ============================================================

    def _calculate_relevant_years(
        self,
        roles: list
    ) -> float:
        """
        Calculate weighted relevant experience.

        Weighting:
            high      -> 100%
            moderate  -> 75%
            low       -> 25%

        Roles with unknown duration are ignored.
        """

        relevant_years = 0.0

        for role in roles:

            duration = role.get(
                "duration_years"
            )

            if duration is None:
                continue

            try:

                duration = float(
                    duration
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            status = role.get(
                "status",
                "low"
            )

            if status == "high":

                relevant_years += duration

            elif status == "moderate":

                relevant_years += (
                    duration
                    *
                    0.75
                )

            elif status == "low":

                relevant_years += (
                    duration
                    *
                    0.25
                )

        return round(
            relevant_years,
            2
        )

    # ============================================================
    # ANALYZE ALL EXPERIENCES
    # ============================================================

    def analyze(
        self,
        resume: dict,
        job_title: str = "",
        required_skills: list | None = None,
        required_years: float = 0,
        target_title: str | None = None
    ) -> dict:
        """
        Analyze all candidate experience entries.

        `job_title` is the preferred public argument.

        `target_title` is retained for backward compatibility.
        """

        # --------------------------------------------------------
        # Backward compatibility
        # --------------------------------------------------------

        if not job_title and target_title:
            job_title = target_title

        required_skills = (
            required_skills
            if required_skills
            else []
        )

        # ========================================================
        # EMPTY RESUME
        # ========================================================

        if not resume:

            return {
                "job_title": job_title,
                "required_years": required_years,
                "candidate_years": 0.0,
                "relevant_years": 0.0,
                "experience_status": "missing",
                "experience_requirement_ratio": None,
                "relevant_experience_ratio": None,
                "relevant_roles": [],
                "roles": [],
                "relevance_status": "low",
                "relevance_score": 0.0
            }

        # ========================================================
        # EXPERIENCES
        # ========================================================

        experiences = resume.get(
            "experience",
            []
        )

        if not experiences:

            return {
                "job_title": job_title,
                "required_years": required_years,
                "candidate_years": 0.0,
                "relevant_years": 0.0,
                "experience_status": "missing",
                "experience_requirement_ratio": None,
                "relevant_experience_ratio": None,
                "relevant_roles": [],
                "roles": [],
                "relevance_status": "low",
                "relevance_score": 0.0
            }

        # ========================================================
        # CANDIDATE TOTAL EXPERIENCE
        # ========================================================

        try:

            from app.matcher.experience_matcher import (
                calculate_total_experience
            )

            candidate_years = (
                calculate_total_experience(
                    experiences
                )
            )

        except Exception:

            candidate_years = 0.0

        # ========================================================
        # EXPERIENCE STATUS
        # ========================================================

        if required_years and required_years > 0:

            if candidate_years >= required_years:

                experience_status = "matched"

            elif candidate_years > 0:

                experience_status = "partial"

            else:

                experience_status = "missing"

        else:

            experience_status = "matched"

        # ========================================================
        # EXPERIENCE RATIO
        # ========================================================

        if required_years and required_years > 0:

            experience_requirement_ratio = round(
                candidate_years
                /
                required_years,
                4
            )

        else:

            experience_requirement_ratio = None

        # ========================================================
        # ANALYZE EACH ROLE
        # ========================================================

        analyzed_roles = []

        for experience in experiences:

            if not isinstance(
                experience,
                dict
            ):
                continue

            role_result = self.analyze_role(
                resume=resume,
                role=experience,
                target_title=job_title,
                required_skills=required_skills,
                required_years=required_years
            )

            analyzed_roles.append(
                role_result
            )

        # ========================================================
        # RELEVANT EXPERIENCE
        # ========================================================

        relevant_years = (
            self._calculate_relevant_years(
                analyzed_roles
            )
        )

        # ========================================================
        # RELEVANT EXPERIENCE RATIO
        # ========================================================

        if required_years and required_years > 0:

            relevant_experience_ratio = round(
                relevant_years
                /
                required_years,
                4
            )

        else:

            relevant_experience_ratio = None

        # ========================================================
        # OVERALL RELEVANCE SCORE
        # ========================================================

        if analyzed_roles:

            relevance_score = round(
                sum(
                    role.get(
                        "relevance",
                        0.0
                    )
                    for role in analyzed_roles
                )
                /
                len(analyzed_roles),
                4
            )

        else:

            relevance_score = 0.0

        # ========================================================
        # OVERALL RELEVANCE STATUS
        # ========================================================

        relevance_status = (
            self._get_relevance_status(
                relevance_score
            )
        )

        # ========================================================
        # FINAL RESULT
        # ========================================================

        return {
            "job_title": job_title,

            "required_years": required_years,

            "candidate_years": candidate_years,

            "relevant_years": relevant_years,

            "experience_status": experience_status,

            "experience_requirement_ratio":
                experience_requirement_ratio,

            "relevant_experience_ratio":
                relevant_experience_ratio,

            "relevant_roles": analyzed_roles,

            # Keep this alias because other parts
            # of the project may already use it.
            "roles": analyzed_roles,

            "relevance_status": relevance_status,

            "relevance_score": relevance_score
        }