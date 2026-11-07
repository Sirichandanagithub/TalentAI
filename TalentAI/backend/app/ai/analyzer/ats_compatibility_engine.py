
import re
from typing import Any

from app.ai.analyzer.scoring_utils import (
    clamp_score,
    classify_score,
    safe_dict,
    safe_list,
    weighted_score,
)


class ATSCompatibilityEngine:
    """
    Deterministic assessment of resume parsing and ATS compatibility.

    This score measures how reliably resume content can be extracted
    and interpreted. It does not predict job selection or guarantee
    compatibility with every ATS platform.
    """

    WEIGHTS = {
        "contact_extraction": 20,
        "section_recognition": 25,
        "date_readability": 15,
        "skills_extraction": 20,
        "parsing_completeness": 20,
    }

    SECTION_ALIASES = {
        "summary": [
            "summary",
            "professional summary",
            "career objective",
            "profile",
            "professional profile",
        ],
        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "internships",
        ],
        "education": [
            "education",
            "educational qualifications",
            "academic qualifications",
            "academic background",
        ],
        "projects": [
            "projects",
            "academic projects",
            "personal projects",
            "project experience",
        ],
        "skills": [
            "skills",
            "technical skills",
            "key skills",
            "skills summary",
            "core competencies",
        ],
        "certifications": [
            "certifications",
            "certificates",
            "licenses and certifications",
        ],
        "achievements": [
            "achievements",
            "accomplishments",
            "awards",
            "honors",
        ],
    }

    def _normalize_heading(self, value: str) -> str:
        value = re.sub(r"^[\W_]+", "", value)
        value = re.sub(r"[\W_]+$", "", value)
        return " ".join(value.lower().split())

    def _detect_sections(self, resume_text: str) -> set[str]:
        detected = set()

        for line in resume_text.splitlines():
            heading = self._normalize_heading(line)

            if not heading:
                continue

            for section, aliases in self.SECTION_ALIASES.items():
                if heading in aliases:
                    detected.add(section)

        return detected

    def _score_contact_extraction(
        self,
        resume_text: str,
        personal: dict,
    ) -> float:
        score = 0.0

        email = personal.get("email")
        phone = personal.get("phone")
        name = personal.get("name")

        email_found = bool(
            isinstance(email, str)
            and re.search(
                r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
                email,
            )
        )

        phone_found = bool(
            isinstance(phone, str)
            and len(re.sub(r"\D", "", phone)) >= 7
        )

        name_found = bool(
            isinstance(name, str) and len(name.strip()) >= 2
        )

        if not email_found and re.search(
            r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
            resume_text,
        ):
            email_found = True

        if not phone_found and re.search(
            r"\+?\d[\d\s().-]{7,}\d",
            resume_text,
        ):
            phone_found = True

        score += 40 if email_found else 0
        score += 35 if phone_found else 0
        score += 25 if name_found else 0

        return clamp_score(score)

    def _score_section_recognition(
        self,
        resume_text: str,
        parsed_data: dict,
    ) -> float:
        detected = self._detect_sections(resume_text)

        populated = set()

        section_fields = {
            "summary": bool(parsed_data.get("summary")),
            "experience": bool(safe_list(parsed_data.get("experience"))),
            "education": bool(safe_list(parsed_data.get("education"))),
            "projects": bool(safe_list(parsed_data.get("projects"))),
            "skills": bool(safe_dict(parsed_data.get("skills"))),
            "certifications": bool(
                safe_list(parsed_data.get("certifications"))
            ),
            "achievements": bool(
                safe_list(parsed_data.get("achievements"))
            ),
        }

        for section, exists in section_fields.items():
            if exists and section in detected:
                populated.add(section)

        if not detected:
            return 0.0

        # Evaluate recognized headings against populated parsed sections.
        relevant_sections = {
            section
            for section, exists in section_fields.items()
            if exists
        }

        if not relevant_sections:
            return 0.0

        recognized = len(populated)
        return clamp_score(
            recognized / len(relevant_sections) * 100
        )

    def _score_date_readability(
        self,
        resume_text: str,
        parsed_data: dict,
    ) -> float:
        date_pattern = re.compile(
            r"\b(?:"
            r"(?:19|20)\d{2}"
            r"|"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*[\s,.-]+(?:19|20)\d{2}"
            r")\b",
            re.IGNORECASE,
        )

        extracted_dates = date_pattern.findall(resume_text)

        entries = (
            safe_list(parsed_data.get("experience"))
            + safe_list(parsed_data.get("education"))
        )

        if not entries:
            return 100.0

        if not extracted_dates:
            return 0.0

        readable_entries = 0

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            dates = safe_dict(entry.get("dates"))

            if dates:
                start = dates.get("start")
                end = dates.get("end")

                if start or end:
                    readable_entries += 1
                    continue

            years = safe_dict(entry.get("years"))

            if years.get("start_year") or years.get("end_year"):
                readable_entries += 1
                continue

            if entry.get("year") or entry.get("date"):
                readable_entries += 1

        valid_entries = [
            entry for entry in entries
            if isinstance(entry, dict)
        ]

        if not valid_entries:
            return 100.0

        return clamp_score(
            readable_entries / len(valid_entries) * 100
        )

    def _collect_skill_strings(self, skills: Any) -> list[str]:
        results = []

        if isinstance(skills, dict):
            for value in skills.values():
                if isinstance(value, list):
                    results.extend(
                        item for item in value
                        if isinstance(item, str)
                    )
                elif isinstance(value, str):
                    results.append(value)

        elif isinstance(skills, list):
            results.extend(
                item for item in skills
                if isinstance(item, str)
            )

        return results

    
    def _score_skills_extraction(
        self,
        resume_text: str,
        parsed_data: dict,
    ) -> float:
        skills = self._collect_skill_strings(
            parsed_data.get("skills", {})
        )

        if not skills:
            return 0.0

        def normalize_skill(value: str) -> str:
            return re.sub(
                r"[^a-z0-9]",
                "",
                value.lower(),
            )

    # Equivalent spellings used in resumes.
        aliases = {
            "javascript": ["javascript"],
            "mysql": ["mysql"],
            "microsoftexcel": ["microsoftexcel", "msexcel"],
        }

        normalized_text = normalize_skill(resume_text)

        matched = 0

        for skill in skills:
            normalized_skill = normalize_skill(skill)

            candidates = aliases.get(
                normalized_skill,
                [normalized_skill],
            )

            if any(
                candidate in normalized_text
                for candidate in candidates
            ):
                matched += 1

        return clamp_score(
            matched / len(skills) * 100
        )


    def _score_parsing_completeness(
        self,
        parsed_data: dict,
    ) -> float:
        personal = safe_dict(parsed_data.get("personal"))

        checks = [
            bool(personal.get("name")),
            bool(personal.get("email")),
            bool(personal.get("phone")),
            bool(
                safe_list(parsed_data.get("education"))
            ),
            bool(
                safe_dict(parsed_data.get("skills"))
            ),
            bool(
                parsed_data.get("summary")
                or safe_list(parsed_data.get("experience"))
                or safe_list(parsed_data.get("projects"))
            ),
        ]

        return clamp_score(
            sum(checks) / len(checks) * 100
        )

    def analyze(
        self,
        resume_text: str,
        parsed_data: dict,
    ) -> dict:
        """
        Calculate ATS compatibility from extracted text
        and structured parser output.
        """

        if not isinstance(resume_text, str):
            raise ValueError("Resume text must be a string.")

        if not isinstance(parsed_data, dict) or not parsed_data:
            raise ValueError(
                "Valid structured resume data is required."
            )

        personal = safe_dict(parsed_data.get("personal"))

        components = {
            "contact_extraction": self._score_contact_extraction(
                resume_text,
                personal,
            ),
            "section_recognition": self._score_section_recognition(
                resume_text,
                parsed_data,
            ),
            "date_readability": self._score_date_readability(
                resume_text,
                parsed_data,
            ),
            "skills_extraction": self._score_skills_extraction(
                resume_text,
                parsed_data,
            ),
            "parsing_completeness": self._score_parsing_completeness(
                parsed_data,
            ),
        }

        total_score = weighted_score(
            components,
            self.WEIGHTS,
        )

        strengths = [
            name for name, score in components.items()
            if score >= 80
        ]

        improvement_areas = [
            name for name, score in components.items()
            if score < 60
        ]

        return {
            "ats_compatibility_score": total_score,
            "classification": classify_score(total_score),
            "score_breakdown": components,
            "strengths": strengths,
            "improvement_areas": improvement_areas,
            "weight_distribution": self.WEIGHTS.copy(),
        }
