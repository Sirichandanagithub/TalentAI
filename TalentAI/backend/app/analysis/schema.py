
"""
Schemas for TalentAI candidate-job analysis API.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, model_validator


class CandidateAnalysisRequest(BaseModel):
    """
    Request payload for candidate-job analysis.
    """

    resume: Dict[str, Any] = Field(
        ...,
        description="Structured candidate resume data.",
    )

    job: Dict[str, Any] = Field(
        ...,
        description="Structured job description data.",
    )

    @model_validator(mode="after")
    def validate_resume_and_job(self):
        resume = self.resume
        job = self.job

        # Reject empty or placeholder resume objects.
        valid_resume_fields = {
            "skills",
            "experience",
            "education",
            "projects",
            "work_experience",
            "technical_skills",
            "certifications",
            "summary",
        }

        if not any(
            key in resume
            and resume[key] not in (None, "", [], {})
            for key in valid_resume_fields
        ):
            raise ValueError(
                "Resume must contain meaningful candidate data, "
                "such as skills, experience, education, or projects."
            )

        # Reject empty or placeholder job objects.
        valid_job_fields = {
            "required_skills",
            "preferred_skills",
            "experience",
            "education",
            "job_title",
            "description",
            "responsibilities",
            "requirements",
        }

        if not any(
            key in job
            and job[key] not in (None, "", [], {})
            for key in valid_job_fields
        ):
            raise ValueError(
                "Job must contain meaningful job data, "
                "such as a title, description, skills, or requirements."
            )

        return self
