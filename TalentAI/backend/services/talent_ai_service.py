"""
TalentAI application service layer.

This module acts as the orchestration layer between
the API layer and the AI/matching components.

Responsibilities:
- Run candidate-job analysis.
- Generate candidate explanations.
- Generate resume improvements.
- Generate ATS optimization suggestions.
- Generate interview questions.

The service does not implement matching or LLM logic itself.
It coordinates the existing components.
"""

from typing import Any, Dict

from app.ai.analyzer.talent_match_engine import TalentMatchEngine
from app.ai.llm.explanation_generator import ExplanationGenerator
from app.ai.llm.resume_improvement import ResumeImprovementGenerator
from app.ai.llm.ats_optimizer import ATSOptimizer
from app.ai.llm.interview_generator import InterviewQuestionGenerator


class TalentAIService:
    """
    Application-level orchestration service for TalentAI.

    The service keeps API routes thin by centralizing
    interaction with the matching and GenAI layers.
    """

    def __init__(
        self,
        match_engine: TalentMatchEngine | None = None,
        explanation_generator: ExplanationGenerator | None = None,
        resume_improvement_generator: ResumeImprovementGenerator | None = None,
        ats_optimizer: ATSOptimizer | None = None,
        interview_generator: InterviewQuestionGenerator | None = None,
    ) -> None:
        """
        Initialize the TalentAI service.

        Dependencies can be injected for testing.
        If they are not provided, the production implementations
        are created automatically.
        """

        self.match_engine = (
            match_engine
            if match_engine is not None
            else TalentMatchEngine()
        )

        self.explanation_generator = (
            explanation_generator
            if explanation_generator is not None
            else ExplanationGenerator()
        )

        self.resume_improvement_generator = (
            resume_improvement_generator
            if resume_improvement_generator is not None
            else ResumeImprovementGenerator()
        )

        self.ats_optimizer = (
            ats_optimizer
            if ats_optimizer is not None
            else ATSOptimizer()
        )

        self.interview_generator = (
            interview_generator
            if interview_generator is not None
            else InterviewQuestionGenerator()
        )

    # ------------------------------------------------------------------
    # Core candidate analysis
    # ------------------------------------------------------------------

    def analyze_candidate(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run the deterministic candidate-job matching pipeline.

        This delegates all matching and scoring logic to
        TalentMatchEngine.

        Parameters
        ----------
        resume:
            Structured resume data.

        job:
            Structured job description data.

        Returns
        -------
        Dict[str, Any]
            Complete structured match result.
        """

        return self.match_engine.analyze(
            resume=resume,
            job=job,
        )

    # ------------------------------------------------------------------
    # LLM explanation
    # ------------------------------------------------------------------

    def generate_explanation(
        self,
        match_result: Dict[str, Any],
        candidate_name: str | None = None,
        job_title: str | None = None,
    ) -> str:
        """
        Generate a natural-language explanation of the match result.

        The deterministic match result remains the source of truth.
        The LLM only explains the supplied result.
        """

        return self.explanation_generator.generate(
            match_result=match_result,
            candidate_name=candidate_name,
            job_title=job_title,
        )

    # ------------------------------------------------------------------
    # Resume improvement
    # ------------------------------------------------------------------

    def generate_resume_improvements(
        self,
        match_result: Dict[str, Any],
        candidate_name: str | None = None,
        job_title: str | None = None,
    ) -> str:
        """
        Generate resume improvement suggestions based on
        the deterministic match result.
        """

        return self.resume_improvement_generator.generate(
            match_result=match_result,
            candidate_name=candidate_name,
            job_title=job_title,
        )

    # ------------------------------------------------------------------
    # ATS optimization
    # ------------------------------------------------------------------

    def generate_ats_optimization(
        self,
        match_result: Dict[str, Any],
        candidate_name: str | None = None,
        job_title: str | None = None,
    ) -> str:
        """
        Generate ATS optimization suggestions.

        The ATS score and deterministic classifications remain
        authoritative.
        """

        return self.ats_optimizer.generate(
            match_result=match_result,
            candidate_name=candidate_name,
            job_title=job_title,
        )

    # ------------------------------------------------------------------
    # Interview questions
    # ------------------------------------------------------------------

    def generate_interview_questions(
        self,
        match_result: Dict[str, Any],
        candidate_name: str | None = None,
        job_title: str | None = None,
    ) -> str:
        """
        Generate candidate-specific interview questions
        from the structured match result.
        """

        return self.interview_generator.generate(
            match_result=match_result,
            candidate_name=candidate_name,
            job_title=job_title,
        )