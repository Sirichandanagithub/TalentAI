from typing import Dict, List


class CandidateJobReasoner:
    """
    Reason about the overall alignment between a candidate and a job.

    This layer does NOT perform matching itself.

    It consumes results produced by:
        - RequirementReasoner
        - ExperienceMatcher
        - SkillExperienceMatcher
        - EducationMatcher
        - ProjectRelevanceAnalyzer
        - EvidenceEngine

    Its responsibility is to combine those signals into
    candidate-job level reasoning.
    """

    def __init__(self):
        self.weights = {
            "skills": 0.35,
            "experience": 0.20,
            "relevant_experience": 0.15,
            "projects": 0.15,
            "education": 0.10,
            "evidence": 0.05,
        }

    # =========================================================
    # Utility methods
    # =========================================================

    @staticmethod
    def _safe_float(
        value,
        default: float = 0.0
    ) -> float:
        """
        Safely convert a value to float.
        """
        try:
            if value is None:
                return default

            return float(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(
        value: float
    ) -> float:
        """
        Keep score between 0 and 1.
        """
        return max(
            0.0,
            min(1.0, value)
        )

    @staticmethod
    def _safe_list(
        value
    ) -> List:
        """
        Safely return a list.
        """
        return (
            value
            if isinstance(value, list)
            else []
        )

    # =========================================================
    # Requirement analysis
    # =========================================================

    def _get_skill_results(
        self,
        match_result: Dict,
    ) -> List[Dict]:
        """
        Extract required-skill results from the structure
        produced by TalentMatchEngine.

        Expected structure:

        match_result = {
            "skills": {
                "required": {
                    "matched": [...],
                    "possible": [...],
                    "unknown": [...]
                }
            }
        }

        The three lists are converted into one unified list
        so the candidate-job reasoner can calculate:
            - matched count
            - possible count
            - unknown count
            - total count
        """

        if not isinstance(
            match_result,
            dict
        ):
            return []

        skills = match_result.get(
            "skills",
            {}
        )

        if not isinstance(
            skills,
            dict
        ):
            return []

        required = skills.get(
            "required",
            {}
        )

        if not isinstance(
            required,
            dict
        ):
            return []

        results = []

        # -----------------------------------------------------
        # Matched skills
        # -----------------------------------------------------

        matched_skills = required.get(
            "matched",
            []
        )

        if isinstance(
            matched_skills,
            list
        ):
            for item in matched_skills:

                if isinstance(
                    item,
                    dict
                ):
                    result = dict(item)

                    # Ensure status exists.
                    result.setdefault(
                        "status",
                        "matched"
                    )

                    # Ensure confidence exists.
                    result.setdefault(
                        "confidence",
                        1.0
                    )

                    results.append(result)

                else:
                    results.append({
                        "requirement": item,
                        "status": "matched",
                        "confidence": 1.0,
                    })

        # -----------------------------------------------------
        # Possible skills
        # -----------------------------------------------------

        possible_skills = required.get(
            "possible",
            []
        )

        if isinstance(
            possible_skills,
            list
        ):
            for item in possible_skills:

                if isinstance(
                    item,
                    dict
                ):
                    result = dict(item)

                    result.setdefault(
                        "status",
                        "possible"
                    )

                    result.setdefault(
                        "confidence",
                        0.5
                    )

                    results.append(result)

                else:
                    results.append({
                        "requirement": item,
                        "status": "possible",
                        "confidence": 0.5,
                    })

        # -----------------------------------------------------
        # Unknown / missing skills
        # -----------------------------------------------------

        unknown_skills = required.get(
            "unknown",
            []
        )

        if isinstance(
            unknown_skills,
            list
        ):
            for item in unknown_skills:

                if isinstance(
                    item,
                    dict
                ):
                    result = dict(item)

                    result.setdefault(
                        "status",
                        "unknown"
                    )

                    result.setdefault(
                        "confidence",
                        0.0
                    )

                    results.append(result)

                else:
                    results.append({
                        "requirement": item,
                        "status": "unknown",
                        "confidence": 0.0,
                    })

        return results

    def _calculate_skill_alignment(
        self,
        match_result: Dict,
    ) -> Dict:
        """
        Calculate overall required-skill alignment.

        Uses the final status produced by the
        requirement matching/reasoning layer.
        """

        results = self._get_skill_results(
            match_result
        )

        if not results:
            return {
                "score": 0.0,
                "matched": 0,
                "possible": 0,
                "unknown": 0,
                "total": 0,
            }

        matched = 0
        possible = 0
        unknown = 0

        confidence_values = []

        for result in results:

            status = str(
                result.get(
                    "status",
                    "unknown"
                )
            ).lower()

            if status == "matched":
                matched += 1

            elif status == "possible":
                possible += 1

            else:
                unknown += 1

            confidence = self._safe_float(
                result.get(
                    "confidence"
                )
            )

            confidence_values.append(
                self._clamp(
                    confidence
                )
            )

        total = len(results)

        # -----------------------------------------------------
        # Status-based coverage
        # -----------------------------------------------------

        status_score = (
            matched
            + (possible * 0.50)
        ) / total

        # -----------------------------------------------------
        # Confidence-based support
        # -----------------------------------------------------

        confidence_score = (
            sum(confidence_values) / total
            if confidence_values
            else 0.0
        )

        # -----------------------------------------------------
        # Combined skill score
        # -----------------------------------------------------

        score = (
            status_score * 0.60
            + confidence_score * 0.40
        )

        return {
            "score": round(
                self._clamp(score),
                4
            ),
            "matched": matched,
            "possible": possible,
            "unknown": unknown,
            "total": total,
        }

    # =========================================================
    # Experience analysis
    # =========================================================

    def _calculate_experience_alignment(
        self,
        match_result: Dict,
    ) -> Dict:
        """
        Calculate alignment with required total experience.
        """

        experience = match_result.get(
            "experience",
            {}
        )

        if not isinstance(
            experience,
            dict
        ):
            experience = {}

        candidate_years = experience.get(
            "candidate_years"
        )

        required_years = experience.get(
            "required_years"
        )

        status = experience.get(
            "status",
            "unknown"
        )

        candidate_years_value = (
            self._safe_float(
                candidate_years
            )
            if candidate_years is not None
            else None
        )

        required_years_value = (
            self._safe_float(
                required_years
            )
            if required_years is not None
            else None
        )

        if (
            candidate_years_value is None
            or required_years_value is None
            or required_years_value <= 0
        ):
            return {
                "score": 0.0,
                "candidate_years": candidate_years_value,
                "required_years": required_years_value,
                "status": status,
            }

        ratio = (
            candidate_years_value
            / required_years_value
        )

        score = self._clamp(
            ratio
        )

        return {
            "score": round(
                score,
                4
            ),
            "candidate_years": candidate_years_value,
            "required_years": required_years_value,
            "status": status,
        }

    # =========================================================
    # Relevant experience
    # =========================================================

    def _calculate_relevant_experience_alignment(
        self,
        match_result: Dict,
    ) -> Dict:
        """
        Calculate alignment based on experience that is
        specifically relevant to the target job.
        """

        relevant_experience = match_result.get(
            "relevant_experience",
            {}
        )

        if not isinstance(
            relevant_experience,
            dict
        ):
            relevant_experience = {}

        relevant_years = self._safe_float(
            relevant_experience.get(
                "relevant_years"
            )
        )

        required_years = self._safe_float(
            relevant_experience.get(
                "required_years"
            )
        )

        if required_years <= 0:
            score = 0.0

        else:
            score = self._clamp(
                relevant_years
                / required_years
            )

        return {
            "score": round(
                score,
                4
            ),
            "relevant_years": relevant_years,
            "required_years": (
                required_years
                if required_years > 0
                else None
            ),
        }

    # =========================================================
    # Project analysis
    # =========================================================

    def _calculate_project_alignment(
        self,
        job_title: str,
        match_result: Dict,
        context: Dict | None = None,
        evidence: Dict | None = None,
    ) -> Dict:
        """
        Calculate project alignment from project relevance.

        The preferred input contains a top-level ``status``.
        For backward compatibility, if that key is missing,
        derive the status from the most relevant project.
        """

        project_relevance = match_result.get(
            "project_relevance",
            {}
        )

        if not isinstance(
            project_relevance,
            dict
        ):
            project_relevance = {}

        score = self._safe_float(
            project_relevance.get(
                "overall_project_relevance"
            )
        )

        project_count = project_relevance.get(
            "project_count",
            0
        )

        status = project_relevance.get(
            "status"
        )

        # -----------------------------------------------------
        # Backward compatibility
        # -----------------------------------------------------
        # Older ProjectRelevanceAnalyzer results stored the
        # status only inside relevant_projects[].
        # -----------------------------------------------------

        if not status:

            relevant_projects = project_relevance.get(
                "relevant_projects",
                []
            )

            if isinstance(
                relevant_projects,
                list
            ):

                valid_projects = [
                    project
                    for project in relevant_projects
                    if isinstance(project, dict)
                ]

                if valid_projects:

                    best_project = max(
                        valid_projects,
                        key=lambda project: self._safe_float(
                            project.get(
                                "relevance_score",
                                0.0
                            )
                        )
                    )

                    status = best_project.get(
                        "status",
                        "unknown"
                    )

        if not status:
            status = "unknown"

        return {
            "score": round(
                self._clamp(score),
                4
            ),
            "project_count": project_count,
            "status": str(status).lower(),
        }

    # =========================================================
    # Education analysis
    # =========================================================

    def _calculate_education_alignment(
        self,
        match_result: Dict,
    ) -> Dict:
        """
        Calculate education alignment from the existing
        education matcher result.
        """

        education = match_result.get(
            "education",
            {}
        )

        if not isinstance(
            education,
            dict
        ):
            education = {}

        status = str(
            education.get(
                "status",
                "unknown"
            )
        ).lower()

        if status == "matched":
            score = 1.0

        elif status == "partial":
            score = 0.5

        elif status == "possible":
            score = 0.5

        else:
            score = 0.0

        return {
            "score": score,
            "status": status,
        }

    # =========================================================
    # Evidence analysis
    # =========================================================

    def _calculate_evidence_alignment(
        self,
        evidence: Dict,
    ) -> Dict:
        """
        Calculate overall evidence strength across
        required skills.

        Evidence is passed separately by TalentMatchEngine
        because it is available at the top-level result.
        """

        if not isinstance(
            evidence,
            dict
        ):
            evidence = {}

        values = []

        for requirement, result in evidence.items():

            if not isinstance(
                result,
                dict
            ):
                continue

            strength = self._safe_float(
                result.get(
                    "evidence_strength"
                )
            )

            values.append(
                self._clamp(
                    strength
                )
            )

        if not values:
            return {
                "score": 0.0,
                "requirements_with_evidence": 0,
            }

        score = (
            sum(values)
            / len(values)
        )

        return {
            "score": round(
                self._clamp(score),
                4
            ),
            "requirements_with_evidence": len(
                values
            ),
        }

    # =========================================================
    # Strengths
    # =========================================================

    def _build_strengths(
        self,
        skill_alignment: Dict,
        experience_alignment: Dict,
        relevant_experience: Dict,
        project_alignment: Dict,
        evidence_alignment: Dict,
    ) -> List[str]:

        strengths = []

        if skill_alignment["matched"] > 0:
            strengths.append(
                f"{skill_alignment['matched']} required "
                "skill(s) are directly matched."
            )

        if (
            experience_alignment["score"]
            >= 0.80
        ):
            strengths.append(
                "The candidate has substantial "
                "overall experience relative to "
                "the job requirement."
            )

        if (
            relevant_experience["score"]
            >= 0.70
        ):
            strengths.append(
                "The candidate has strong relevant "
                "experience for the target role."
            )

        if (
            project_alignment["score"]
            >= 0.70
        ):
            strengths.append(
                "Projects show strong alignment with "
                "the job requirements."
            )

        if (
            evidence_alignment["score"]
            >= 0.70
        ):
            strengths.append(
                "The resume contains strong evidence "
                "supporting the required skills."
            )

        return strengths

    # =========================================================
    # Gaps
    # =========================================================

    def _build_gaps(
        self,
        skill_alignment: Dict,
        experience_alignment: Dict,
        relevant_experience: Dict,
        project_alignment: Dict,
        education_alignment: Dict,
    ) -> List[str]:

        gaps = []

        if skill_alignment["unknown"] > 0:
            gaps.append(
                f"{skill_alignment['unknown']} required "
                "skill(s) lack sufficient evidence."
            )

        if (
            experience_alignment["required_years"]
            is not None
            and experience_alignment["candidate_years"]
            is not None
            and experience_alignment["candidate_years"]
            < experience_alignment["required_years"]
        ):
            gaps.append(
                "The candidate's documented overall "
                "experience is below the required "
                "experience."
            )

        if (
            relevant_experience["required_years"]
            is not None
            and relevant_experience["relevant_years"]
            < relevant_experience["required_years"]
        ):
            gaps.append(
                "Relevant experience is below the "
                "target requirement."
            )

        if (
            project_alignment["project_count"]
            == 0
        ):
            gaps.append(
                "No relevant projects were identified."
            )

        if (
            education_alignment["status"]
            == "unknown"
        ):
            gaps.append(
                "Education alignment could not be "
                "reliably determined."
            )

        return gaps

    # =========================================================
    # Overall score
    # =========================================================

    def _calculate_overall_score(
        self,
        skill_alignment: Dict,
        experience_alignment: Dict,
        relevant_experience: Dict,
        project_alignment: Dict,
        education_alignment: Dict,
        evidence_alignment: Dict,
    ) -> float:

        score = (
            skill_alignment["score"]
            * self.weights["skills"]

            + experience_alignment["score"]
            * self.weights["experience"]

            + relevant_experience["score"]
            * self.weights["relevant_experience"]

            + project_alignment["score"]
            * self.weights["projects"]

            + education_alignment["score"]
            * self.weights["education"]

            + evidence_alignment["score"]
            * self.weights["evidence"]
        )

        return round(
            self._clamp(score),
            4
        )

    # =========================================================
    # Status
    # =========================================================

    def _determine_status(
        self,
        overall_score: float,
    ) -> str:

        if overall_score >= 0.75:
            return "strong"

        if overall_score >= 0.50:
            return "moderate"

        return "weak"

    # =========================================================
    # Reason
    # =========================================================

    def _build_reason(
        self,
        status: str,
        skill_alignment: Dict,
        experience_alignment: Dict,
        relevant_experience: Dict,
        project_alignment: Dict,
    ) -> str:

        parts = []

        parts.append(
            f"The candidate has "
            f"{skill_alignment['matched']} "
            f"of "
            f"{skill_alignment['total']} "
            "required skills directly matched."
        )

        if (
            experience_alignment["candidate_years"]
            is not None
        ):
            parts.append(
                f"Documented overall experience is "
                f"{experience_alignment['candidate_years']:.2f} "
                "years."
            )

        if (
            relevant_experience["relevant_years"]
            > 0
        ):
            parts.append(
                f"Relevant experience is approximately "
                f"{relevant_experience['relevant_years']:.2f} "
                "years."
            )

        if (
            project_alignment["project_count"]
            > 0
        ):
            parts.append(
                f"{project_alignment['project_count']} "
                "relevant project(s) were identified."
            )

        return " ".join(parts)

    # =========================================================
    # Public API
    # =========================================================

    def reason(
        self,
        job_title: str,
        match_result: Dict,
        context: Dict | None = None,
        evidence: Dict | None = None,
    ) -> Dict:

        if not isinstance(
            match_result,
            dict
        ):
            match_result = {}

        if not isinstance(
            context,
            dict
        ):
            context = {}

        if not isinstance(
            evidence,
            dict
        ):
            evidence = {}

        # -----------------------------------------------------
        # Skill alignment
        # -----------------------------------------------------

        skill_alignment = (
            self._calculate_skill_alignment(
                match_result
            )
        )

        # -----------------------------------------------------
        # Experience alignment
        # -----------------------------------------------------

        experience_alignment = (
            self._calculate_experience_alignment(
                match_result
            )
        )

        # -----------------------------------------------------
        # Relevant experience
        # -----------------------------------------------------

        relevant_experience = (
            self._calculate_relevant_experience_alignment(
                match_result
            )
        )

        # -----------------------------------------------------
        # Project alignment
        # -----------------------------------------------------

        project_alignment = (
            self._calculate_project_alignment(
                job_title=job_title,
                match_result=match_result,
                context=context,
                evidence=evidence,
            )
        )

        # -----------------------------------------------------
        # Education alignment
        # -----------------------------------------------------

        education_alignment = (
            self._calculate_education_alignment(
                match_result
            )
        )

        # -----------------------------------------------------
        # Evidence alignment
        # -----------------------------------------------------

        evidence_alignment = (
            self._calculate_evidence_alignment(
                evidence
            )
        )

        # -----------------------------------------------------
        # Overall score
        # -----------------------------------------------------

        overall_score = (
            self._calculate_overall_score(
                skill_alignment,
                experience_alignment,
                relevant_experience,
                project_alignment,
                education_alignment,
                evidence_alignment,
            )
        )

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        status = self._determine_status(
            overall_score
        )

        # -----------------------------------------------------
        # Strengths
        # -----------------------------------------------------

        strengths = self._build_strengths(
            skill_alignment,
            experience_alignment,
            relevant_experience,
            project_alignment,
            evidence_alignment,
        )

        # -----------------------------------------------------
        # Gaps
        # -----------------------------------------------------

        gaps = self._build_gaps(
            skill_alignment,
            experience_alignment,
            relevant_experience,
            project_alignment,
            education_alignment,
        )

        # -----------------------------------------------------
        # Reason
        # -----------------------------------------------------

        reason = self._build_reason(
            status,
            skill_alignment,
            experience_alignment,
            relevant_experience,
            project_alignment,
        )

        # -----------------------------------------------------
        # Final result
        # -----------------------------------------------------

        return {
            "job_title": job_title,
            "status": status,
            "overall_score": overall_score,
            "skill_alignment": skill_alignment,
            "experience_alignment": experience_alignment,
            "relevant_experience": relevant_experience,
            "project_alignment": project_alignment,
            "education_alignment": education_alignment,
            "evidence_alignment": evidence_alignment,
            "strengths": strengths,
            "gaps": gaps,
            "reason": reason,
        }


# ============================================================
# Convenience function
# ============================================================

def reason_candidate_job(
    job_title: str,
    match_result: Dict,
    context: Dict | None = None,
    evidence: Dict | None = None,
) -> Dict:

    reasoner = CandidateJobReasoner()

    return reasoner.reason(
        job_title=job_title,
        match_result=match_result,
        context=context,
        evidence=evidence,
    )