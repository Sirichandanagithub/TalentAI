
"""
Schemas for TalentAI candidate-job analysis API.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, model_validator


class CandidateAnalysisRequest(BaseModel):
    """
    Request payload for candidate-job analysis.
    """

    resume_id: int = Field(
        ...,
        gt=0,
        description="ID of the uploaded resume to analyze.",
    )

    job: Dict[str, Any] = Field(
        ...,
        description="Structured job description data.",
    )

    @model_validator(mode="after")
    def validate_job(self):
        job = self.job

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
