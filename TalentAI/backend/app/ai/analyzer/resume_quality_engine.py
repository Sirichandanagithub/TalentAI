
import re
from typing import Any

from app.ai.analyzer.scoring_utils import (
    clamp_score,
    classify_score,
    safe_dict,
    safe_list,
    weighted_score,
)


class ResumeQualityEngine:
    """
    Evaluates overall resume quality independently of any job description.

    Measures:
    - Experience presentation
    - Project quality
    - Skills presentation
    - Professional summary
    - Education and certifications
    - Achievement impact
    - Resume completeness
    - Content clarity

    This score is independent of ATS Compatibility Score
    and Job Match Score.
    """

    WEIGHTS = {
        "experience_quality": 20,
        "project_quality": 20,
        "skills_presentation": 15,
        "professional_summary": 10,
        "education_certifications": 10,
        "achievements_impact": 10,
        "resume_completeness": 10,
        "content_clarity": 5,
    }

    # ============================================================
    # ACHIEVEMENT AND IMPACT EVIDENCE
    # ============================================================

    def _score_impact_evidence(self, text: str) -> float:
        """
        Evaluate achievement evidence.

        Maximum score: 25 points.

        Action evidence: 10 points
        Outcome evidence: 7 points
        Measurable evidence: 8 points

        This is a deterministic text heuristic.
        It does not verify whether a resume claim is genuine.
        """

        if not isinstance(text, str) or not text.strip():
            return 0.0

        text_lower = text.casefold()
        score = 0

        action_words = {
            "developed",
            "implemented",
            "created",
            "designed",
            "built",
            "managed",
            "optimized",
            "improved",
            "automated",
            "reduced",
            "increased",
            "achieved",
            "delivered",
            "led",
            "launched",
            "engineered",
            "deployed",
            "established",
            "streamlined",
            "generated",
        }

        words = set(re.findall(r"\b[\w+#.-]+\b", text_lower))

        if words.intersection(action_words):
            score += 10

        outcome_phrases = {
            "resulting in",
            "which improved",
            "which reduced",
            "which increased",
            "leading to",
            "resulted in",
            "successfully delivered",
            "improved performance",
            "reduced costs",
            "increased efficiency",
            "enhanced performance",
            "improved accuracy",
        }

        if any(
            phrase in text_lower
            for phrase in outcome_phrases
        ):
            score += 7

        # Reward measurable metrics, not arbitrary years or dates.
        metric_pattern = (
            r"\b\d+(?:\.\d+)?\s*"
            r"(?:%|percent\b|x\b|"
            r"hours?\b|days?\b|weeks?\b|months?\b|"
            r"years?\b|users?\b|customers?\b|"
            r"projects?\b|incidents?\b|records?\b|"
            r"transactions?\b|employees?\b|"
            r"requests?\b|reports?\b)"
        )

        currency_pattern = r"[$₹€£]\s*\d[\d,]*(?:\.\d+)?"

        if (
            re.search(metric_pattern, text_lower)
            or re.search(currency_pattern, text)
        ):
            score += 8

        return clamp_score(score)

    # ============================================================
    # EXPERIENCE QUALITY
    # ============================================================

    def _score_experience(self, experience: list) -> float:
        """
        Evaluate professional experience quality.

        Job title: 15
        Company: 10
        Description: 20
        Employment dates: 15
        Technologies: 15
        Achievement and impact evidence: 25

        Total: 100
        """

        if not experience:
            return 0.0

        scores = []

        for item in experience:
            item = safe_dict(item)

            score = 0

            # Job title: 15 points
            if item.get("job_title"):
                score += 15

            # Company: 10 points
            if item.get("company"):
                score += 10

            # Description: 20 points
            description = (
                item.get("description")
                or item.get("raw_text")
                or ""
            )

            if (
                isinstance(description, str)
                and description.strip()
            ):
                score += 20

            # Employment dates: 15 points
            dates = safe_dict(item.get("dates"))

            start_date = (
                dates.get("start")
                or item.get("start_date")
            )

            end_date = (
                dates.get("end")
                or item.get("end_date")
            )

            currently_working = (
                dates.get("current") is True
                or item.get("currently_working") is True
            )

            if start_date:
                score += 10

            if end_date or currently_working:
                score += 5

            # Technologies: 15 points
            technologies = safe_list(
                item.get("technologies")
            )

            if technologies:
                score += 15

            # Achievement and impact evidence: 25 points
            achievements = safe_list(
                item.get("achievements")
            )

            responsibilities = safe_list(
                item.get("responsibilities")
            )

            evidence_parts = [description]

            evidence_parts.extend(
                str(value)
                for value in achievements + responsibilities
                if value
            )

            evidence_text = " ".join(
                str(value)
                for value in evidence_parts
                if value
            )

            score += self._score_impact_evidence(
                evidence_text
            )

            scores.append(clamp_score(score))

        return round(sum(scores) / len(scores), 2)

    # ============================================================
    # PROJECT QUALITY
    # ============================================================

    def _score_projects(self, projects: list) -> float:
        """
        Evaluate project quality.

        Project name: 15
        Description: 30
        Technologies and skills: 20
        Role and contribution: 10
        Achievement and impact evidence: 25

        Total: 100

        GitHub URL is deliberately excluded.
        Missing GitHub links should not penalize candidates.
        """

        if not projects:
            return 0.0

        scores = []

        for project in projects:
            project = safe_dict(project)

            score = 0

            # Project name: 15 points
            project_name = (
                project.get("project_name")
                or project.get("name")
                or project.get("title")
            )

            if project_name:
                score += 15

            # Description: 30 points
            description = (
                project.get("description")
                or project.get("raw_text")
                or ""
            )

            if (
                isinstance(description, str)
                and description.strip()
            ):
                score += 30

            # Technologies and skills: 20 points
            technologies = safe_list(
                project.get("technologies")
            )

            skills = safe_list(
                project.get("skills")
            )

            if technologies or skills:
                score += 20

            # Role and contribution: 10 points
            if (
                project.get("role")
                or project.get("contribution")
            ):
                score += 10

            # Achievement and impact evidence: 25 points
            achievements = safe_list(
                project.get("achievements")
            )

            outcomes = safe_list(
                project.get("outcomes")
            )

            evidence_parts = [description]

            evidence_parts.extend(
                str(value)
                for value in achievements + outcomes
                if value
            )

            evidence_text = " ".join(
                str(value)
                for value in evidence_parts
                if value
            )

            score += self._score_impact_evidence(
                evidence_text
            )

            scores.append(clamp_score(score))

        return round(sum(scores) / len(scores), 2)

    # ============================================================
    # SKILLS PRESENTATION
    # ============================================================

    def _score_skills(self, skills: Any) -> float:
        if isinstance(skills, dict):
            skill_count = sum(
                len(safe_list(value))
                for value in skills.values()
            )
        else:
            skill_count = len(safe_list(skills))

        if skill_count == 0:
            return 0.0

        if skill_count < 5:
            return 40.0

        if skill_count <= 10:
            return 65.0

        if skill_count <= 25:
            return 85.0

        return 100.0

    # ============================================================
    # PROFESSIONAL SUMMARY
    # ============================================================

    def _score_summary(self, summary: Any) -> float:
        if not isinstance(summary, str) or not summary.strip():
            return 0.0

        word_count = len(summary.split())

        if word_count < 15:
            return 40.0

        if word_count <= 30:
            return 70.0

        if word_count <= 80:
            return 100.0

        if word_count <= 120:
            return 80.0

        return 60.0

    # ============================================================
    # EDUCATION AND CERTIFICATIONS
    # ============================================================

    def _score_education_certifications(
        self,
        education: list,
        certifications: list,
    ) -> float:
        score = 0

        valid_education = [
            safe_dict(item)
            for item in education
            if isinstance(item, dict)
        ]

        if valid_education:
            score += 60

            # Match the actual parser field: program.
            complete_education = any(
                (
                    item.get("program")
                    or item.get("degree")
                )
                and item.get("institution")
                for item in valid_education
            )

            if complete_education:
                score += 20

            # Match the actual parser field: years.end_year.
            has_graduation_date = False

            for item in valid_education:
                years = safe_dict(item.get("years"))

                if (
                    years.get("end_year")
                    or item.get("graduation_year")
                    or item.get("end_date")
                ):
                    has_graduation_date = True
                    break

            if has_graduation_date:
                score += 20

        elif certifications:
            score += 40

        if certifications and valid_education:
            score = min(100, score + 10)

        return clamp_score(score)

    # ============================================================
    # ACHIEVEMENTS
    # ============================================================

    
    def _score_achievements(
        self,
        achievements: list,
        experience: list = None,
        projects: list = None,
    ) -> float:
        """
    Evaluate achievement and impact evidence.

    If a dedicated achievements section is missing,
    inspect experience and project descriptions instead.

    This avoids penalizing candidates simply because
    their achievements are documented under other sections.
    """

    # Prefer a dedicated achievements section when available.
        if achievements:
            scores = []

            for achievement in achievements:
                if isinstance(achievement, dict):
                    text = str(
                        achievement.get("description")
                        or achievement.get("title")
                        or ""
                    )
                else:
                    text = str(achievement)

                text = text.strip()

                if not text:
                    continue

                score = 50
                impact_score = self._score_impact_evidence(text)
                score += impact_score * 2

                scores.append(clamp_score(score))

            return (
                round(sum(scores) / len(scores), 2)
                if scores else 0.0
            )

    # No dedicated achievements section:
    # inspect evidence in experience and projects.
        evidence_texts = []

        for item in safe_list(experience):
            item = safe_dict(item)

            parts = [
                item.get("description"),
                item.get("raw_text"),
            ]

            parts.extend(safe_list(item.get("achievements")))
            parts.extend(safe_list(item.get("responsibilities")))

            text = " ".join(
                str(part).strip()
                for part in parts
                if part and str(part).strip()
            )

            if text:
                evidence_texts.append(text)

        for item in safe_list(projects):
            item = safe_dict(item)

            parts = [
                item.get("description"),
                item.get("raw_text"),
            ]

            parts.extend(safe_list(item.get("achievements")))
            parts.extend(safe_list(item.get("outcomes")))

            text = " ".join(
                str(part).strip()
                for part in parts
                if part and str(part).strip()
            )

            if text:
                evidence_texts.append(text)

        if not evidence_texts:
            return 0.0

        scores = [
            self._score_impact_evidence(text) * 4
            for text in evidence_texts
        ]

        return round(sum(scores) / len(scores), 2)


    # ============================================================
    # RESUME COMPLETENESS
    # ============================================================

    def _score_completeness(self, resume: dict) -> float:
        """
        Evaluate essential resume sections.

        Freshers can receive full completeness credit
        through projects without professional experience.

        Professional experience and projects are alternatives
        for this completeness check.
        """

        personal = safe_dict(resume.get("personal"))

        has_personal = bool(
            personal.get("name")
            or personal.get("email")
            or personal.get("phone")
        )

        has_education = bool(
            safe_list(resume.get("education"))
        )

        has_skills = bool(
            resume.get("skills")
        )

        has_experience_or_projects = bool(
            safe_list(resume.get("experience"))
            or safe_list(resume.get("projects"))
        )

        has_summary = bool(
            isinstance(resume.get("summary"), str)
            and resume.get("summary").strip()
        )

        checks = [
            (has_personal, 20),
            (has_education, 20),
            (has_skills, 20),
            (has_experience_or_projects, 25),
            (has_summary, 15),
        ]

        score = sum(
            weight
            for condition, weight in checks
            if condition
        )

        return clamp_score(score)

    # ============================================================
    # CONTENT CLARITY
    # ============================================================

    def _score_clarity(self, resume: dict) -> float:
        """
        Initial structural clarity heuristic.

        This does not use an LLM or grammar checker.
        It evaluates available parsed text volume only.
        """

        text_parts = []

        def collect_text(value):
            if isinstance(value, str):
                if value.strip():
                    text_parts.append(value)

            elif isinstance(value, dict):
                for nested_value in value.values():
                    collect_text(nested_value)

            elif isinstance(value, (list, tuple)):
                for nested_value in value:
                    collect_text(nested_value)

        collect_text(resume)

        if not text_parts:
            return 0.0

        # Avoid counting identical text multiple times.
        unique_parts = list(dict.fromkeys(text_parts))

        text = " ".join(unique_parts).strip()

        if not text:
            return 0.0

        word_count = len(text.split())

        if word_count < 50:
            return 30.0

        if word_count < 150:
            return 60.0

        if word_count <= 1000:
            return 100.0

        if word_count <= 1500:
            return 80.0

        return 60.0

    # ============================================================
    # MAIN ANALYSIS
    # ============================================================

    def analyze(self, resume: dict) -> dict:
        """
        Generate the Resume Quality Score and component breakdown.
        """

        if not isinstance(resume, dict) or not resume:
            raise ValueError(
                "A valid parsed resume dictionary is required."
            )

        experience = safe_list(
            resume.get("experience")
        )

        projects = safe_list(
            resume.get("projects")
        )

        education = safe_list(
            resume.get("education")
        )

        certifications = safe_list(
            resume.get("certifications")
        )

        achievements = safe_list(
            resume.get("achievements")
        )

        skills = resume.get("skills", {})

        summary = resume.get("summary", "")

        components = {
            "experience_quality": self._score_experience(
                experience
            ),

            "project_quality": self._score_projects(
                projects
            ),

            "skills_presentation": self._score_skills(
                skills
            ),

            "professional_summary": self._score_summary(
                summary
            ),

            "education_certifications": (
                self._score_education_certifications(
                    education,
                    certifications,
                )
            ),

            "achievements_impact": self._score_achievements(
                achievements,
                experience,
                projects,
            ),

            "resume_completeness": self._score_completeness(
                resume
            ),

            "content_clarity": self._score_clarity(
                resume
            ),
        }

        # Reuse the common weighted scoring utility.
        total_score = weighted_score(
            components,
            self.WEIGHTS,
        )

        strengths = [
            name
            for name, score in components.items()
            if score >= 80
        ]

        improvement_areas = [
            name
            for name, score in components.items()
            if score < 60
        ]

        return {
            "resume_quality_score": total_score,

            "classification": classify_score(
                total_score
            ),

            "score_breakdown": components,

            "strengths": strengths,

            "improvement_areas": improvement_areas,

            "weight_distribution": self.WEIGHTS.copy(),
        }
