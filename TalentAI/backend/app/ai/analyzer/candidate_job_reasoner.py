from typing import Any, Dict, List, Optional


class CandidateJobReasoner:
    """
    Combine deterministic candidate/job matching results into a
    high-level explanation. This class does not perform skill matching.
    """

    def __init__(self) -> None:
        self.weights = {
            "skills": 0.35,
            "experience": 0.20,
            "relevant_experience": 0.15,
            "projects": 0.15,
            "education": 0.10,
            "evidence": 0.05,
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bool):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _safe_dict(value: Any) -> Dict:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _safe_list(value: Any) -> List:
        return value if isinstance(value, list) else []

    @staticmethod
    def _first_dict(source: Dict, *keys: str) -> Dict:
        """Return the first dict-valued field found in source."""
        for key in keys:
            value = source.get(key)
            if isinstance(value, dict):
                return value
        return {}

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def _get_skill_results(self, match_result: Dict) -> List[Dict]:
        """
        Support both:
          {"skills": {"required": {...}}}
        and the actual API response shape:
          {"match": {"skills": {"required": {...}}}}
        """
        root = self._safe_dict(match_result)
        match = self._safe_dict(root.get("match"))
        skills = self._first_dict(root, "skills")
        if not skills:
            skills = self._safe_dict(match.get("skills"))

        required = self._safe_dict(skills.get("required"))
        results: List[Dict] = []

        for status in ("matched", "possible", "unknown"):
            items = self._safe_list(required.get(status))
            for item in items:
                if isinstance(item, dict):
                    result = dict(item)
                    result.setdefault("status", status)
                    default_confidence = {
                        "matched": 1.0,
                        "possible": 0.5,
                        "unknown": 0.0,
                    }[status]
                    result.setdefault("confidence", default_confidence)
                else:
                    result = {
                        "requirement": item,
                        "status": status,
                        "confidence": {
                            "matched": 1.0,
                            "possible": 0.5,
                            "unknown": 0.0,
                        }[status],
                    }
                results.append(result)

        # Defensive fallback for older/high-level reasoner payloads
        # containing counts but no individual skill lists.
        if not results:
            reasoning = self._safe_dict(root.get("candidate_job_reasoning"))
            alignment = self._safe_dict(reasoning.get("skill_alignment"))
            if not alignment:
                alignment = self._safe_dict(root.get("skill_alignment"))
            for status in ("matched", "possible", "unknown"):
                count = max(0, int(self._safe_float(alignment.get(status), 0)))
                for _ in range(count):
                    results.append({"status": status, "confidence": {
                        "matched": 1.0, "possible": 0.5, "unknown": 0.0
                    }[status]})
        return results

    def _calculate_skill_alignment(self, match_result: Dict) -> Dict:
        results = self._get_skill_results(match_result)
        if not results:
            return {"score": 0.0, "matched": 0, "possible": 0,
                    "unknown": 0, "total": 0}

        counts = {"matched": 0, "possible": 0, "unknown": 0}
        confidences = []
        for result in results:
            status = str(result.get("status", "unknown")).lower()
            if status not in counts:
                status = "unknown"
            counts[status] += 1
            confidences.append(self._clamp(
                self._safe_float(result.get("confidence"), {
                    "matched": 1.0, "possible": 0.5, "unknown": 0.0
                }[status])
            ))

        total = len(results)
        status_score = (counts["matched"] + 0.5 * counts["possible"]) / total
        confidence_score = sum(confidences) / total if confidences else 0.0
        score = 0.60 * status_score + 0.40 * confidence_score
        return {
            "score": round(self._clamp(score), 4),
            "matched": counts["matched"],
            "possible": counts["possible"],
            "unknown": counts["unknown"],
            "total": total,
        }

    # ------------------------------------------------------------------
    # Experience
    # ------------------------------------------------------------------

    def _calculate_experience_alignment(self, match_result: Dict) -> Dict:
        root = self._safe_dict(match_result)
        reasoning = self._safe_dict(root.get("candidate_job_reasoning"))
        experience = self._first_dict(root, "experience")
        if not experience:
            experience = self._safe_dict(reasoning.get("experience_alignment"))

        candidate_years_raw = experience.get("candidate_years")
        required_years_raw = experience.get("required_years")
        candidate_years = (
            self._safe_float(candidate_years_raw)
            if candidate_years_raw is not None else None
        )
        required_years = (
            self._safe_float(required_years_raw)
            if required_years_raw is not None else None
        )
        status = str(experience.get("status", "unknown")).lower()

        if candidate_years is None or required_years is None:
            return {
                "score": self._clamp(self._safe_float(experience.get("score"))),
                "candidate_years": candidate_years,
                "required_years": required_years,
                "status": status,
            }

        if required_years <= 0:
            score = 1.0
        else:
            score = self._clamp(candidate_years / required_years)
        return {
            "score": round(score, 4),
            "candidate_years": candidate_years,
            "required_years": required_years,
            "status": status,
        }

    def _calculate_relevant_experience_alignment(self, match_result: Dict) -> Dict:
        root = self._safe_dict(match_result)
        reasoning = self._safe_dict(root.get("candidate_job_reasoning"))
        relevant = self._first_dict(root, "relevant_experience")
        if not relevant:
            relevant = self._safe_dict(reasoning.get("relevant_experience"))

        relevant_years = self._safe_float(relevant.get("relevant_years"))
        required_raw = relevant.get("required_years")
        required_years = self._safe_float(required_raw) if required_raw is not None else None
        if required_years is None:
            score = self._clamp(self._safe_float(relevant.get("score")))
        elif required_years <= 0:
            score = 1.0
        else:
            score = self._clamp(relevant_years / required_years)

        return {
            "score": round(score, 4),
            "relevant_years": relevant_years,
            "required_years": required_years if required_years is None or required_years > 0 else None,
        }

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def _calculate_project_alignment(
        self,
        job_title: str,
        match_result: Dict,
        context: Optional[Dict] = None,
        evidence: Optional[Dict] = None,
    ) -> Dict:
        root = self._safe_dict(match_result)
        reasoning = self._safe_dict(root.get("candidate_job_reasoning"))
        project = self._first_dict(root, "project_relevance", "projects")
        if not project:
            project = self._safe_dict(reasoning.get("project_alignment"))

        score_raw = project.get("overall_project_relevance")
        if score_raw is None:
            score_raw = project.get("score", 0.0)
        score = self._clamp(self._safe_float(score_raw))
        count = project.get("project_count", 0)
        try:
            count = max(0, int(count))
        except (TypeError, ValueError):
            count = 0

        status = project.get("status")
        if not status:
            projects = self._safe_list(project.get("relevant_projects"))
            valid_projects = [p for p in projects if isinstance(p, dict)]
            if valid_projects:
                best = max(
                    valid_projects,
                    key=lambda p: self._safe_float(p.get("relevance_score")),
                )
                status = best.get("status", best.get("relevance_level"))
        if not status:
            status = "unknown"

        return {"score": round(score, 4), "project_count": count,
                "status": str(status).lower()}

    # ------------------------------------------------------------------
    # Education
    # ------------------------------------------------------------------

    def _calculate_education_alignment(self, match_result: Dict) -> Dict:
        root = self._safe_dict(match_result)
        reasoning = self._safe_dict(root.get("candidate_job_reasoning"))
        education = self._first_dict(root, "education")
        if not education:
            education = self._safe_dict(reasoning.get("education_alignment"))

        status = str(education.get("status", "unknown")).lower()
        if status == "matched":
            score = 1.0
        elif status in ("partial", "possible"):
            score = 0.5
        elif status in ("not_required", "not required", "waived"):
            # A non-required criterion should not penalize the candidate.
            score = 1.0
        else:
            score = self._clamp(self._safe_float(education.get("score")))
        return {"score": round(score, 4), "status": status}

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    
    def _calculate_evidence_alignment(self, evidence: Dict) -> Dict:
        """Calculate evidence strength across all requirements."""
        evidence = self._safe_dict(evidence)

        if not evidence:
            return {
                "score": 0.0,
                "requirements_with_evidence": 0,
                "total_requirements": 0,
            }

        total_requirements = 0
        requirements_with_evidence = 0
        total_strength = 0.0

        for result in evidence.values():
            if not isinstance(result, dict):
                continue

            total_requirements += 1

            strength = self._clamp(
                self._safe_float(result.get("evidence_strength"))
            )

            items = result.get("evidence", [])
            has_evidence = (
                isinstance(items, (list, tuple)) and len(items) > 0
            )

            if has_evidence and strength > 0:
                requirements_with_evidence += 1
                total_strength += strength

        score = (
            total_strength / total_requirements
            if total_requirements > 0
            else 0.0
        )

        return {
            "score": round(self._clamp(score), 4),
            "requirements_with_evidence": requirements_with_evidence,
            "total_requirements": total_requirements,
        }


    # ------------------------------------------------------------------
    # Strengths, gaps, overall score and explanation
    # ------------------------------------------------------------------

    
    def _build_strengths(
        self,
        skill_alignment: Dict,
        experience_alignment: Dict,
        relevant_experience: Dict,
        project_alignment: Dict,
        evidence_alignment: Dict,
    ) -> List[str]:
        """Build strengths using only applicable criteria."""
        strengths = []

        if self._safe_float(skill_alignment.get("matched")) > 0:
            strengths.append(
                f'{skill_alignment["matched"]} required skill(s) are directly matched.'
            )

        # Overall experience: only report a strength when required.
        experience_status = str(
            experience_alignment.get("status", "")
        ).strip().lower()
        required_years = experience_alignment.get("required_years")

        if (
            experience_status not in {
                "not_required",
                "not required",
                "not applicable",
                "not_applicable",
                "n/a",
            }
            and required_years is not None
            and self._safe_float(required_years) > 0
            and self._safe_float(experience_alignment.get("score")) >= 0.80
        ):
            strengths.append(
                "The candidate has substantial overall experience relative to the job requirement."
            )

        # Relevant experience: only report a strength when required.
        relevant_status = str(
            relevant_experience.get("status", "")
        ).strip().lower()
        relevant_required_years = relevant_experience.get("required_years")

        if (
            relevant_status not in {
                "not_required",
                "not required",
                "not applicable",
                "not_applicable",
                "n/a",
            }
            and relevant_required_years is not None
            and self._safe_float(relevant_required_years) > 0
            and self._safe_float(relevant_experience.get("score")) >= 0.70
        ):
            strengths.append(
                "The candidate has strong relevant experience for the target role."
            )

        if self._safe_float(project_alignment.get("score")) >= 0.70:
            strengths.append(
                "Projects show strong alignment with the job requirements."
            )

        if self._safe_float(evidence_alignment.get("score")) >= 0.70:
            strengths.append(
                "The resume contains strong evidence supporting the required skills."
            )

        return strengths


    def _build_gaps(
        self, skill_alignment: Dict, experience_alignment: Dict,
        relevant_experience: Dict, project_alignment: Dict,
        education_alignment: Dict,
    ) -> List[str]:
        gaps = []
        if skill_alignment["unknown"] > 0:
            gaps.append(f'{skill_alignment["unknown"]} required skill(s) lack sufficient evidence.')

        candidate_years = experience_alignment["candidate_years"]
        required_years = experience_alignment["required_years"]
        if candidate_years is not None and required_years is not None and candidate_years < required_years:
            gaps.append("The candidate's documented overall experience is below the required experience.")

        relevant_years = relevant_experience["relevant_years"]
        relevant_required = relevant_experience["required_years"]
        if relevant_required is not None and relevant_years < relevant_required:
            gaps.append("Relevant experience is below the target requirement.")

        if project_alignment["project_count"] == 0:
            gaps.append("No relevant projects were identified.")
        if education_alignment["status"] == "unknown":
            gaps.append("Education alignment could not be reliably determined.")
        return gaps

    
    def _calculate_overall_score(
        self,
        skill_alignment: Dict,
        experience_alignment: Dict,
        relevant_experience: Dict,
        project_alignment: Dict,
        education_alignment: Dict,
        evidence_alignment: Dict,
    ) -> float:
        """Calculate a weighted score using applicable criteria."""

        components = [
            ("skills", skill_alignment),
            ("experience", experience_alignment),
            ("relevant_experience", relevant_experience),
            ("projects", project_alignment),
            ("education", education_alignment),
            ("evidence", evidence_alignment),
        ]

        non_applicable_statuses = {
            "not_required",
            "not applicable",
            "not_applicable",
            "n/a",
        }

        weighted_total = 0.0
        applicable_weight = 0.0

        for name, alignment in components:
            alignment = self._safe_dict(alignment)
            status = str(alignment.get("status", "")).strip().lower()

            if status in non_applicable_statuses:
                continue

            if name == "evidence":
                if self._safe_float(alignment.get("total_requirements")) <= 0:
                    continue

            if name == "skills":
                if self._safe_float(alignment.get("total")) <= 0:
                    continue

            if name == "relevant_experience":
                if self._safe_float(alignment.get("required_years")) <= 0:
                    continue

            weight = self._safe_float(self.weights.get(name))
            if weight <= 0:
                continue

            component_score = self._clamp(
                self._safe_float(alignment.get("score"))
            )

            weighted_total += component_score * weight
            applicable_weight += weight

        if applicable_weight <= 0:
            return 0.0

        return round(
            self._clamp(weighted_total / applicable_weight),
            4,
        )



    def _determine_status(self, overall_score: float) -> str:
        if overall_score >= 0.75:
            return "strong"
        if overall_score >= 0.50:
            return "moderate"
        return "weak"

    def _build_reason(
        self, status: str, skill_alignment: Dict,
        experience_alignment: Dict, relevant_experience: Dict,
        project_alignment: Dict,
    ) -> str:
        parts = [
            f'The candidate has {skill_alignment["matched"]} of '
            f'{skill_alignment["total"]} required skills directly matched.'
        ]
        candidate_years = experience_alignment["candidate_years"]
        if candidate_years is not None:
            parts.append(f"Documented overall experience is {candidate_years:.2f} years.")
        relevant_years = relevant_experience["relevant_years"]
        if relevant_years > 0:
            parts.append(f"Relevant experience is approximately {relevant_years:.2f} years.")
        if project_alignment["project_count"] > 0:
            parts.append(f'{project_alignment["project_count"]} relevant project(s) were identified.')
        return " ".join(parts)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reason(
        self,
        job_title: str,
        match_result: Dict,
        context: Optional[Dict] = None,
        evidence: Optional[Dict] = None,
    ) -> Dict:
        """Build candidate-job reasoning from deterministic match results."""
        root = self._safe_dict(match_result)
        context = self._safe_dict(context)
        evidence = self._safe_dict(evidence)

        # Accept either a full API response or the inner match-result object.
        skill_alignment = self._calculate_skill_alignment(root)
        experience_alignment = self._calculate_experience_alignment(root)
        relevant_experience = self._calculate_relevant_experience_alignment(root)
        project_alignment = self._calculate_project_alignment(
            job_title, root, context=context, evidence=evidence
        )
        education_alignment = self._calculate_education_alignment(root)
        evidence_alignment = self._calculate_evidence_alignment(evidence)

        overall_score = self._calculate_overall_score(
            skill_alignment, experience_alignment, relevant_experience,
            project_alignment, education_alignment, evidence_alignment,
        )
        status = self._determine_status(overall_score)
        strengths = self._build_strengths(
            skill_alignment, experience_alignment, relevant_experience,
            project_alignment, evidence_alignment,
        )
        gaps = self._build_gaps(
            skill_alignment, experience_alignment, relevant_experience,
            project_alignment, education_alignment,
        )
        reason = self._build_reason(
            status, skill_alignment, experience_alignment,
            relevant_experience, project_alignment,
        )

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


def reason_candidate_job(
    job_title: str,
    match_result: Dict,
    context: Optional[Dict] = None,
    evidence: Optional[Dict] = None,
) -> Dict:
    """Convenience wrapper around CandidateJobReasoner.reason()."""
    return CandidateJobReasoner().reason(
        job_title=job_title,
        match_result=match_result,
        context=context,
        evidence=evidence,
    )
