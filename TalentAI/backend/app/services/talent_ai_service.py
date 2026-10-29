
"""
TalentAI application service layer.

Coordinates candidate-job analysis and related AI services.
GitHub discovery and verification enrich project evidence only;
they do not change ATS scores.
"""

from typing import Any, Dict

from app.ai.analyzer.talent_match_engine import TalentMatchEngine
from app.ai.llm.explanation_generator import ExplanationGenerator
from app.ai.llm.resume_improvement import ResumeImprovementGenerator
from app.ai.llm.ats_optimizer import ATSOptimizer
from app.ai.llm.interview_generator import InterviewQuestionGenerator
from app.services.github_verification_service import GitHubVerificationService
from app.services.github_repository_discovery_service import (
    GitHubRepositoryDiscoveryService,
)


class TalentAIService:
    """Application-level orchestration service for TalentAI."""

    def __init__(
        self,
        match_engine: TalentMatchEngine | None = None,
        explanation_generator: ExplanationGenerator | None = None,
        resume_improvement_generator: ResumeImprovementGenerator | None = None,
        ats_optimizer: ATSOptimizer | None = None,
        interview_generator: InterviewQuestionGenerator | None = None,
        github_verification_service: GitHubVerificationService | None = None,
        github_repository_discovery_service: (
            GitHubRepositoryDiscoveryService | None
        ) = None,
    ) -> None:
        """Initialize dependencies, allowing injection for testing."""

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

        self.github_verification_service = (
            github_verification_service
            if github_verification_service is not None
            else GitHubVerificationService()
        )

        self.github_repository_discovery_service = (
            github_repository_discovery_service
            if github_repository_discovery_service is not None
            else GitHubRepositoryDiscoveryService()
        )

    # ------------------------------------------------------------------
    # GitHub evidence enrichment
    # ------------------------------------------------------------------

    @staticmethod
    def _get_required_skills(job: Dict[str, Any]) -> list[str]:
        """Return valid required skills from the job data."""
        skills = job.get("required_skills", [])

        if not isinstance(skills, list):
            return []

        return [
            skill
            for skill in skills
            if isinstance(skill, str) and skill.strip()
        ]

    def _discover_project_repositories(
        self,
        project: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Discover possible repositories without asserting ownership."""

        discovery_project = {
            "name": project.get("project_name", ""),
            "description": project.get("description", ""),
            "technologies": project.get("technologies", []),
        }

        try:
            discovery = (
                self.github_repository_discovery_service
                .discover_repositories(discovery_project)
            )

            if not isinstance(discovery, dict):
                discovery = {}

            candidates = discovery.get("candidates", [])
            if not isinstance(candidates, list):
                candidates = []

            # Do not automatically select the first or highest-ranked result.
            # Search results alone cannot establish repository ownership.
            return {
                "verification_status": "repository_not_identified",
                "repository_verified": False,
                "ownership_verified": False,
                "reason": (
                    "Repository ownership cannot be established from "
                    "search similarity alone."
                ),
                "discovery_status": discovery.get(
                    "discovery_status",
                    "unavailable",
                ),
                 "relevance_assessment": discovery.get(
                    "relevance_assessment",
                    "unavailable",
                ),
                "score_gap": discovery.get("score_gap"),
                "relevance_reason": discovery.get(
                    "relevance_reason",
                    "No relevance assessment was provided.",
                ),
                "candidate_count": discovery.get(
                    "candidate_count",
                    len(candidates),
                ),
                "candidates": candidates,
                "selected_repository": None,
            }

        except Exception:
            # GitHub discovery must never break candidate analysis.
            return {
                "verification_status": "repository_not_identified",
                "repository_verified": False,
                "ownership_verified": False,
                "discovery_status": "unavailable",
                "reason": "GitHub repository discovery failed.",
                "candidate_count": 0,
                "candidates": [],
                "selected_repository": None,
            }

    def _verify_project_repository(
        self,
        project: Dict[str, Any],
        github_url: str,
        required_skills: list[str],
    ) -> None:
        """Verify a provided repository URL and attach evidence safely."""

        try:
            verification = (
                self.github_verification_service.verify_repository(
                    github_url
                )
            )

            if not isinstance(verification, dict):
                verification = {
                    "verification_status": "unavailable",
                    "repository_verified": False,
                    "github_url": github_url,
                    "evidence": [],
                }

            try:
                comparison = (
                    self.github_verification_service.compare_required_skills(
                        verification,
                        required_skills,
                    )
                )
            except Exception:
                comparison = {
                    "comparison_status": "unavailable",
                    "skills": [],
                }

            verification["skill_comparison"] = comparison
            project["github_verification"] = verification

        except Exception:
            # Verification errors must not break candidate analysis.
            project["github_verification"] = {
                "verification_status": "unavailable",
                "repository_verified": False,
                "ownership_verified": False,
                "github_url": github_url,
                "evidence": [],
                "skill_comparison": {
                    "comparison_status": "unavailable",
                    "skills": [],
                },
            }

    # ------------------------------------------------------------------
    # Candidate analysis
    # ------------------------------------------------------------------

    def analyze_candidate(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run the existing matching pipeline and enrich relevant projects
        with GitHub verification or repository discovery evidence.

        GitHub evidence does not modify ATS scores or scoring weights.
        """

        # Step 1: Run the existing matching pipeline unchanged.
        result = self.match_engine.analyze(
            resume=resume,
            job=job,
        )

        if not isinstance(result, dict):
            return result

        match = result.get("match", {})
        if not isinstance(match, dict):
            return result

        project_relevance = match.get("project_relevance", {})
        if not isinstance(project_relevance, dict):
            return result

        projects = project_relevance.get("relevant_projects", [])
        if not isinstance(projects, list):
            return result

        required_skills = self._get_required_skills(job)

        # Step 2: Enrich up to three relevant projects.
        for project in projects[:3]:
            if not isinstance(project, dict):
                continue

            github_url = project.get("github_url")

            if isinstance(github_url, str) and github_url.strip():
                # A URL was provided in the resume: verify that repository.
                self._verify_project_repository(
                    project=project,
                    github_url=github_url.strip(),
                    required_skills=required_skills,
                )
            else:
                # No URL was provided: discover possible repositories,
                # but do not select one or claim ownership.
                project["github_discovery"] = (
                    self._discover_project_repositories(project)
                )

        # Step 3: Return the original matching result with added evidence.
        return result

    # ------------------------------------------------------------------
    # LLM explanation
    # ------------------------------------------------------------------

    def generate_explanation(
        self,
        match_result: Dict[str, Any],
        candidate_name: str | None = None,
        job_title: str | None = None,
    ) -> str:
        """Generate a natural-language explanation of a match."""
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
        """Generate resume improvement suggestions."""
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
        """Generate ATS optimization suggestions."""
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
        """Generate candidate-specific interview questions."""
        return self.interview_generator.generate(
            match_result=match_result,
            candidate_name=candidate_name,
            job_title=job_title,
        )
