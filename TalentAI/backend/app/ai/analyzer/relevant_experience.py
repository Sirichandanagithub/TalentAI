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
                role_title_clean
                .split("@")[0]
                .strip()
            )

        if "[" in role_title_clean:
            role_title_clean = (
                role_title_clean
                .split("[")[0]
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
                "ml",
            },
            "machine learning engineer": {
                "machine",
                "learning",
                "ml",
                "ai",
                "artificial",
                "intelligence",
                "data",
            },
            "ai engineer": {
                "ai",
                "artificial",
                "intelligence",
                "machine",
                "learning",
                "ml",
                "data",
            },
        }

        # --------------------------------------------------------
        # Normalize common seniority / level prefixes
        # --------------------------------------------------------

        role_title_family = role_title_clean

        for prefix in (
            "associate",
            "junior",
            "senior",
            "lead",
            "staff",
            "principal",
            "intern",
        ):
            if role_title_family.startswith(
                prefix + " "
            ):
                role_title_family = (
                    role_title_family[
                        len(prefix):
                    ]
                    .strip()
                )

        # --------------------------------------------------------
        # Explicit AI / Data role relationships
        # --------------------------------------------------------

        related_role_pairs = {
            ("data scientist", "ai engineer"),
            (
                "data scientist",
                "machine learning engineer"
            ),
            ("ai engineer", "data scientist"),
            (
                "ai engineer",
                "machine learning engineer"
            ),
            (
                "machine learning engineer",
                "data scientist"
            ),
            (
                "machine learning engineer",
                "ai engineer"
            ),
        }

        if (
            target_title,
            role_title_family
        ) in related_role_pairs:
            return 0.50

        target_related_terms = (
            related_role_terms.get(
                target_title,
                set()
            )
        )

        if target_related_terms:

            role_words = set(
                role_title_family.split()
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
        required_skills: list,
        resume: dict | None = None
    ) -> tuple[float, list, list, list]:
        """
        Calculate how strongly the candidate's experience role
        is related to the required skills.

        Evidence can come from:

            1. The specific experience role
            2. Candidate-level skills
            3. Candidate-level projects

        Important:

            Candidate-level skills and project evidence establish
            relevance only.

            They do NOT add employment duration.

        Returns:

            (
                score,
                matched_skills,
                possible_skills,
                unknown_skills
            )
        """

        resume = resume or {}

        if not required_skills:

            return (
                0.0,
                [],
                [],
                []
            )

        # ========================================================
        # 1. BUILD TEXT FROM EXPERIENCE ROLE
        # ========================================================

        role_text_parts = []

        for key in [
            "job_title",
            "company",
            "description",
            "raw_text",
            "location",
        ]:

            value = role.get(
                key,
                ""
            )

            if value:
                role_text_parts.append(
                    str(value)
                )

        # ========================================================
        # 2. ADD SKILLS ATTACHED TO ROLE
        # ========================================================

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
                            if value
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
                    str(value)
                    for value in role_skills
                    if value
                ]
            )

        elif role_skills:

            role_text_parts.append(
                str(role_skills)
            )

        # ========================================================
        # 3. BUILD CANDIDATE-LEVEL SKILL TEXT
        # ========================================================

        candidate_skills = resume.get(
            "skills",
            []
        )

        if isinstance(
            candidate_skills,
            list
        ):

            candidate_skill_text = " ".join(
                [
                    str(skill)
                    for skill in candidate_skills
                    if skill
                ]
            )

        elif candidate_skills:

            candidate_skill_text = str(
                candidate_skills
            )

        else:

            candidate_skill_text = ""

        # ========================================================
        # 4. BUILD PROJECT EVIDENCE
        # ========================================================

        project_text_parts = []

        projects = resume.get(
            "projects",
            []
        )

        if not isinstance(
            projects,
            list
        ):

            projects = [
                projects
            ]

        for project in projects:

            if isinstance(
                project,
                dict
            ):

                for key in [
                    "project_name",
                    "name",
                    "title",
                    "description",
                    "raw_text",
                    "technologies",
                    "skills",
                ]:

                    value = project.get(
                        key,
                        ""
                    )

                    if not value:
                        continue

                    if isinstance(
                        value,
                        list
                    ):

                        project_text_parts.extend(
                            [
                                str(item)
                                for item in value
                                if item
                            ]
                        )

                    else:

                        project_text_parts.append(
                            str(value)
                        )

            elif project:

                project_text_parts.append(
                    str(project)
                )

        project_text = " ".join(
            project_text_parts
        )

        # ========================================================
        # 5. NORMALIZE EVIDENCE
        # ========================================================

        role_text_normalized = (
            self._normalize_text(
                " ".join(
                    role_text_parts
                )
            )
        )

        candidate_skill_text_normalized = (
            self._normalize_text(
                candidate_skill_text
            )
        )

        project_text_normalized = (
            self._normalize_text(
                project_text
            )
        )

        # ========================================================
        # 6. ALIASES
        # ========================================================

        aliases = {
            "python": [
                "python",
                "py",
            ],

            "sql": [
                "sql",
                "mysql",
                "postgresql",
                "postgres",
            ],

            "machine learning": [
                "machine learning",
                "ml",
            ],

            "artificial intelligence": [
                "artificial intelligence",
                "ai",
            ],

            "deep learning": [
                "deep learning",
                "dl",
            ],

            "data analysis": [
                "data analysis",
                "data analytics",
            ],

            "data science": [
                "data science",
                "data scientist",
            ],

            "pandas": [
                "pandas",
                "panda",
            ],

            "scikit-learn": [
                "scikit-learn",
                "scikit learn",
                "sklearn",
                "scikit_learn",
            ],
        }

        # ========================================================
        # 7. RELATED SKILLS
        # ========================================================

        related_skills = {
            "python": {
                "machine learning",
                "data science",
                "data analysis",
                "artificial intelligence",
            },

            "machine learning": {
                "artificial intelligence",
                "deep learning",
                "data science",
            },

            "deep learning": {
                "machine learning",
                "artificial intelligence",
            },

            "artificial intelligence": {
                "machine learning",
                "deep learning",
                "data science",
            },

            "data analysis": {
                "data science",
            },

            "data science": {
                "data analysis",
                "machine learning",
                "artificial intelligence",
            },

            "pandas": {
                "data analysis",
                "data science",
            },

            "scikit-learn": {
                "machine learning",
                "data science",
            },

            "sql": {
                "data analysis",
                "data science",
            },
        }

        # ========================================================
        # 8. CHECK REQUIRED SKILLS
        # ========================================================

        matched_skills = []
        possible_skills = []
        unknown_skills = []

        for required_skill in required_skills:

            if not required_skill:
                continue

            original_skill = str(
                required_skill
            ).strip()

            if not original_skill:
                continue

            skill = self._normalize_text(
                original_skill
            )

            # ----------------------------------------------------
            # Direct / alias match
            # ----------------------------------------------------

            role_terms = aliases.get(
                skill,
                [skill]
            )

            direct_match = False

            for term in role_terms:

                if (
                    term in role_text_normalized
                    or
                    term in candidate_skill_text_normalized
                    or
                    term in project_text_normalized
                ):

                    direct_match = True
                    break

            if direct_match:

                matched_skills.append(
                    original_skill
                )

                continue

            # ----------------------------------------------------
            # Related skill match
            # ----------------------------------------------------

            related_match = False

            related_for_skill = (
                related_skills.get(
                    skill,
                    set()
                )
            )

            for related_skill in related_for_skill:

                related_terms = aliases.get(
                    related_skill,
                    [related_skill]
                )

                for term in related_terms:

                    if (
                        term in role_text_normalized
                        or
                        term in candidate_skill_text_normalized
                        or
                        term in project_text_normalized
                    ):

                        related_match = True
                        break

                if related_match:
                    break

            if related_match:

                possible_skills.append(
                    original_skill
                )

            else:

                unknown_skills.append(
                    original_skill
                )

        # ========================================================
        # 9. CALCULATE SCORE
        # ========================================================

        total_skills = (
            len(matched_skills)
            +
            len(possible_skills)
            +
            len(unknown_skills)
        )

        if total_skills == 0:

            score = 0.0

        else:

            score = (
                len(matched_skills)
                +
                (
                    0.50
                    *
                    len(possible_skills)
                )
            ) / total_skills

        # ========================================================
        # 10. SAFETY CLAMP
        # ========================================================

        score = max(
            0.0,
            min(
                1.0,
                score
            )
        )

        # ========================================================
        # 11. RETURN FOUR VALUES
        # ========================================================

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
        role: dict,
        target_title: str,
        required_skills: list,
        resume: dict | None = None
    ) -> dict:
        """
        Analyze relevance of one professional experience role.

        Employment duration is taken from the role's existing
        duration fields when available.

        Candidate-level skills and projects are used only for
        relevance evidence.
        """

        resume = resume or {}

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
            required_skills,
            resume
        )

        # ========================================================
        # ROLE RELEVANCE
        # ========================================================

        relevance_score = (
            (
                self.TITLE_WEIGHT
                *
                title_relevance
            )
            +
            (
                self.SKILL_WEIGHT
                *
                skill_relevance
            )
        )

        relevance_score = max(
            0.0,
            min(
                1.0,
                relevance_score
            )
        )

        status = self._get_relevance_status(
            relevance_score
        )

        # ========================================================
        # GET ROLE DURATION
        # ========================================================

        duration_months = role.get(
            "duration_months"
        )

        duration_years = role.get(
            "duration_years"
        )

        # If duration years is unavailable but months exist,
        # derive years from months.
        if (
            duration_years is None
            and
            duration_months is not None
        ):

            try:

                duration_years = (
                    float(duration_months)
                    /
                    12.0
                )

            except (
                TypeError,
                ValueError
            ):

                duration_years = 0.0

        if duration_months is None:

            if duration_years is not None:

                try:

                    duration_months = (
                        float(duration_years)
                        *
                        12.0
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    duration_months = 0.0

            else:

                duration_months = 0.0

        try:

            duration_months = float(
                duration_months
            )

        except (
            TypeError,
            ValueError
        ):

            duration_months = 0.0

        try:

            duration_years = float(
                duration_years
                if duration_years is not None
                else 0.0
            )

        except (
            TypeError,
            ValueError
        ):

            duration_years = 0.0

        # ========================================================
        # WEIGHTED RELEVANT EXPERIENCE
        # ========================================================

        relevant_years = (
            duration_years
            *
            relevance_score
        )

        # ========================================================
        # RETURN ROLE RESULT
        # ========================================================

        return {
            "company": role.get(
                "company"
            ),

            "job_title": role.get(
                "job_title"
            ),

            "location": role.get(
                "location"
            ),

            "start": (
                role.get("dates", {})
                .get("start")
                if isinstance(
                    role.get("dates"),
                    dict
                )
                else None
            ),

            "end": (
                role.get("dates", {})
                .get("end")
                if isinstance(
                    role.get("dates"),
                    dict
                )
                else None
            ),

            "current": (
                role.get("dates", {})
                .get("current", False)
                if isinstance(
                    role.get("dates"),
                    dict
                )
                else False
            ),

            "duration_months": round(
                duration_months,
                2
            ),

            "duration_years": round(
                duration_years,
                2
            ),

            "title_relevance": round(
                title_relevance,
                4
            ),

            "skill_relevance": round(
                skill_relevance,
                4
            ),

            "relevance_score": round(
                relevance_score,
                4
            ),

            "status": status,

            "matched_skills": matched_skills,

            "possible_skills": possible_skills,

            "unknown_skills": unknown_skills,

            "relevant_years": round(
                relevant_years,
                4
            ),
        }

    # ============================================================
    # ANALYZE ALL EXPERIENCE
    # ============================================================

    def analyze(
        self,
        resume: dict,
        job_title: str,
        required_skills: list,
        required_years: float
    ) -> dict:
        """
        Analyze all candidate experience against a target job.
        """

        resume = resume or {}

        experiences = resume.get(
            "experience",
            []
        )

        if not isinstance(
            experiences,
            list
        ):

            experiences = []

        try:

            required_years = float(
                required_years
            )

        except (
            TypeError,
            ValueError
        ):

            required_years = 0.0

        role_results = []

        for role in experiences:

            if not isinstance(
                role,
                dict
            ):
                continue

            role_result = self.analyze_role(
                role=role,
                target_title=job_title,
                required_skills=required_skills,
                resume=resume
            )

            role_results.append(
                role_result
            )

        # ========================================================
        # TOTAL DOCUMENTED EXPERIENCE
        # ========================================================

        total_experience_years = 0.0

        for role_result in role_results:

            total_experience_years += (
                role_result.get(
                    "duration_years",
                    0.0
                )
            )

        # ========================================================
        # TOTAL RELEVANT EXPERIENCE
        # ========================================================

        relevant_experience_years = 0.0

        for role_result in role_results:

            relevant_experience_years += (
                role_result.get(
                    "relevant_years",
                    0.0
                )
            )

        # ========================================================
        # LIMIT RELEVANT EXPERIENCE
        # ========================================================

        # Relevant experience cannot exceed the candidate's
        # documented total employment experience.
        relevant_experience_years = min(
            relevant_experience_years,
            total_experience_years
        )

        # ========================================================
        # REQUIRED EXPERIENCE SCORE
        # ========================================================

        if required_years <= 0:

            experience_score = 1.0

        else:

            experience_score = (
                relevant_experience_years
                /
                required_years
            )

            experience_score = max(
                0.0,
                min(
                    1.0,
                    experience_score
                )
            )

        # ========================================================
        # OVERALL STATUS
        # ========================================================

        if experience_score >= self.HIGH_THRESHOLD:

            overall_status = "high"

        elif experience_score >= self.MODERATE_THRESHOLD:

            overall_status = "moderate"

        elif relevant_experience_years > 0:

            overall_status = "partial"

        else:

            overall_status = "low"

        # ========================================================
        # RETURN FINAL RESULT
        # ========================================================

        return {
            "job_title": job_title,

            "required_years": round(
                required_years,
                2
            ),

            "candidate_years": round(
                total_experience_years,
                2
            ),

            "relevant_years": round(
                relevant_experience_years,
                2
            ),

            "experience_score": round(
                experience_score,
                4
            ),

            "status": overall_status,

            "roles": role_results,

            "experience_details": role_results,
        }