
"""
Resume-only analysis orchestration service.

Coordinates:
1. Resume parsing
2. Resume Quality Engine
3. ATS Compatibility Engine

Does not modify database records.
"""

from app.ai.analyzer.resume_quality_engine import (
    ResumeQualityEngine,
)
from app.ai.analyzer.ats_compatibility_engine import (
    ATSCompatibilityEngine,
)
from app.parser.master_parser import parse_resume
from app.parser.section_detector import extract_sections


class ResumeAnalysisService:
    """Coordinates independent resume-only scoring engines."""

    def __init__(
        self,
        resume_quality_engine: ResumeQualityEngine | None = None,
        ats_compatibility_engine: ATSCompatibilityEngine | None = None,
    ) -> None:

        self.resume_quality_engine = (
            resume_quality_engine
            if resume_quality_engine is not None
            else ResumeQualityEngine()
        )

        self.ats_compatibility_engine = (
            ats_compatibility_engine
            if ats_compatibility_engine is not None
            else ATSCompatibilityEngine()
        )

    def analyze_resume(self, resume_text: str) -> dict:
        """
        Parse resume text and calculate two independent scores.

        Parsing is performed on each request in this initial version
        to avoid relying on potentially outdated stored parsed_data.
        """

        if not isinstance(resume_text, str) or not resume_text.strip():
            raise ValueError(
                "Valid extracted resume text is required."
            )

        # 1. Detect resume sections.
        sections = extract_sections(resume_text)

        # 2. Generate fresh structured resume data.
        parsed_data = parse_resume(sections)

        if not isinstance(parsed_data, dict) or not parsed_data:
            raise ValueError(
                "Resume parsing failed. Structured data is unavailable."
            )

        # 3. Calculate Resume Quality Score.
        resume_quality_result = (
            self.resume_quality_engine.analyze(parsed_data)
        )

        # 4. Calculate ATS Compatibility Score.
        ats_result = self.ats_compatibility_engine.analyze(
            resume_text=resume_text,
            parsed_data=parsed_data,
        )

        # 5. Return independent results.
        return {
            "resume_quality": resume_quality_result,
            "ats_compatibility": ats_result,
        }
