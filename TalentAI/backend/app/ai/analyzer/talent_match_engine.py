from typing import Dict, List

from app.ai.analyzer.hybrid_matcher import HybridMatcher
from app.ai.analyzer.context_matcher import ContextMatcher
from app.ai.analyzer.evidence_engine import EvidenceEngine
from app.ai.analyzer.decision_engine import DecisionEngine
from app.ai.analyzer.skill_experience_matcher import (
    SkillExperienceMatcher,
)
from app.ai.analyzer.project_relevance import (
    ProjectRelevanceAnalyzer,
)
from app.ai.analyzer.ats_scoring_engine import (
    calculate_ats_score,
    generate_score_summary,
)
from app.ai.analyzer.requirement_reasoner import (
    RequirementReasoner,
)
from app.ai.analyzer.candidate_job_reasoner import (
    CandidateJobReasoner,
)
from app.ai.analyzer.relevant_experience import (
    RelevantExperienceAnalyzer,
)

# ATS scoring engine
from app.ai.analyzer.ats_scoring_engine import (
    calculate_ats_score,
    generate_score_summary,
)


# ============================================================
# TALENT MATCH ENGINE
# ============================================================

class TalentMatchEngine:
    """
    Main TalentAI matching engine.

    Pipeline:

        Resume
          ↓
        Job Description
          ↓
        Candidate Skill Collection
          ↓
        Hybrid Skill Matching
          ↓
        Context-Aware Matching
          ↓
        Experience Matching
          ↓
        Skill-Specific Experience
          ↓
        Education Matching
          ↓
        Project Matching
          ↓
        Evidence
          ↓
        ATS Scoring
          ↓
        Decision
          ↓
        Final Match Result
    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        self.hybrid_matcher = HybridMatcher()

        self.context_matcher = ContextMatcher()

        self.evidence_engine = EvidenceEngine()

        self.decision_engine = DecisionEngine()

        self.skill_experience_matcher = (
            SkillExperienceMatcher()
        )

        self.project_relevance_analyzer = (
            ProjectRelevanceAnalyzer()
        )

        self.requirement_reasoner = (
            RequirementReasoner()
        )

        self.candidate_job_reasoner = (
            CandidateJobReasoner()
)
        self.relevant_experience_analyzer = (
            RelevantExperienceAnalyzer()
        )


    # ========================================================
    # RESUME SKILLS
    # ========================================================

    def _get_candidate_skills(
        self,
        resume: Dict
    ) -> List[str]:
        """
        Collect candidate skills from the complete resume.

        Sources:
            1. resume["skills"]
            2. project technologies

        The goal is to avoid losing skills that were extracted
        during project parsing but were not placed inside the
        main skills dictionary.
        """

        collected_skills = []

        # ====================================================
        # SOURCE 1: MAIN RESUME SKILLS
        # ====================================================

        skills = resume.get(
            "skills",
            []
        )

        if isinstance(skills, list):

            for skill in skills:

                if skill:

                    collected_skills.append(
                        str(skill).strip()
                    )

        elif isinstance(skills, dict):

            for category_skills in skills.values():

                if isinstance(
                    category_skills,
                    list
                ):

                    for skill in category_skills:

                        if skill:

                            collected_skills.append(
                                str(skill).strip()
                            )

                elif isinstance(
                    category_skills,
                    str
                ):

                    if category_skills.strip():

                        collected_skills.append(
                            category_skills.strip()
                        )

        # ====================================================
        # SOURCE 2: PROJECT TECHNOLOGIES
        # ====================================================

        projects = resume.get(
            "projects",
            []
        )

        if isinstance(projects, list):

            for project in projects:

                if not isinstance(
                    project,
                    dict
                ):

                    continue

                technologies = project.get(
                    "technologies",
                    []
                )

                if isinstance(
                    technologies,
                    list
                ):

                    for technology in technologies:

                        if technology:

                            collected_skills.append(
                                str(technology).strip()
                            )

                elif isinstance(
                    technologies,
                    str
                ):

                    if technologies.strip():

                        collected_skills.append(
                            technologies.strip()
                        )

        # ====================================================
        # DEDUPLICATION
        # ====================================================

        unique_skills = []

        seen = set()

        for skill in collected_skills:

            if not skill:
                continue

            normalized = (
                skill
                .lower()
                .strip()
                .rstrip(".,;:")
            )

            if normalized not in seen:

                seen.add(normalized)

                unique_skills.append(
                    skill
                )

        return unique_skills

    # ========================================================
    # EXPERIENCE
    # ========================================================

    def _get_experience_entries(
        self,
        resume: Dict
    ) -> List[Dict]:

        experience = resume.get(
            "experience",
            []
        )

        if not isinstance(
            experience,
            list
        ):

            return []

        return experience

    # ========================================================
    # EDUCATION
    # ========================================================

    def _get_education_entries(
        self,
        resume: Dict
    ) -> List[Dict]:

        education = resume.get(
            "education",
            []
        )

        if not isinstance(
            education,
            list
        ):

            return []

        return education

    # ========================================================
    # PROJECTS
    # ========================================================

    def _get_projects(
        self,
        resume: Dict
    ) -> List[Dict]:

        projects = resume.get(
            "projects",
            []
        )

        if not isinstance(
            projects,
            list
        ):

            return []

        return projects

    # ========================================================
    # ANALYZE ONE SKILL
    # ========================================================

    def analyze_requirement(
        self,
        requirement: str,
        candidate_skills: List[str]
    ) -> Dict:

        return self.hybrid_matcher.match_requirement(
            requirement,
            candidate_skills
        )

    # ========================================================
    # MATCH SKILL ALIAS
    # ========================================================

    def match_skill(
        self,
        requirement: str,
        candidate_skills: List[str]
    ) -> Dict:

        return self.hybrid_matcher.match_requirement(
            requirement,
            candidate_skills
        )

    # ========================================================
    # CONTEXT-AWARE MATCHING
    # ========================================================

    def analyze_context(
        self,
        requirement: str,
        resume: Dict,
        hybrid_result: Dict = None
    ) -> Dict:
        """
        Analyze where and how a requirement is demonstrated
        in the resume.

        HybridMatcher:
            Determines whether the requirement matches
            candidate skills.

        ContextMatcher:
            Determines where the requirement is demonstrated:
            skills, experience, projects, certifications,
            or education.
        """

        try:

            return self.context_matcher.match(
                requirement,
                resume,
                hybrid_result
            )

        except Exception as error:

            return {
                "requirement": requirement,

                "hybrid_status": (
                    hybrid_result.get(
                        "status",
                        "unknown"
                    )
                    if isinstance(
                        hybrid_result,
                        dict
                    )
                    else "unknown"
                ),

                "context_status": "unknown",

                "context_score": 0.0,

                "sources": [],

                "evidence": [],

                "reason": (
                    "Context matching failed: "
                    f"{str(error)}"
                ),
            }

    # ========================================================
    # REQUIRED SKILLS
    # ========================================================

    def analyze_required_skills(
        self,
        required_skills: List[str],
        candidate_skills: List[str],
        resume: Dict = None
    ) -> Dict:

        return self._analyze_skills(
            required_skills,
            candidate_skills,
            resume
        )

    # ========================================================
    # PREFERRED SKILLS
    # ========================================================

    def analyze_preferred_skills(
        self,
        preferred_skills: List[str],
        candidate_skills: List[str],
        resume: Dict = None
    ) -> Dict:

        return self._analyze_skills(
            preferred_skills,
            candidate_skills,
            resume
        )

    # ========================================================
    # GENERIC SKILL ANALYSIS
    # ========================================================

    def _analyze_skills(
        self,
        requirements: List[str],
        candidate_skills: List[str],
        resume: Dict = None
    ) -> Dict:
        """
        Analyze multiple skill requirements.

        Pipeline:

            HybridMatcher
                  ↓
            ContextMatcher
                  ↓
            Context reconciliation
                  ↓
            Final classification

        Context can strengthen an UNKNOWN hybrid result
        when the resume explicitly demonstrates the skill.

        Relationship-only matches are NOT upgraded by
        context automatically.
        """

        if not requirements:

            return {
                "matched": [],
                "possible": [],
                "unknown": []
            }

        matched = []
        possible = []
        unknown = []

        for requirement in requirements:

            # ------------------------------------------------
            # STEP 1: HYBRID MATCHING
            # ------------------------------------------------

            result = self.analyze_requirement(
                requirement,
                candidate_skills
            )

            status = result.get(
                "status",
                "unknown"
            )

            # ------------------------------------------------
            # STEP 2: CONTEXT MATCHING
            # ------------------------------------------------

            context_result = None

            if isinstance(
                resume,
                dict
            ):

                context_result = self.analyze_context(
                    requirement,
                    resume,
                    result
                )

            # ------------------------------------------------
            # STEP 3: ATTACH CONTEXT
            # ------------------------------------------------

            if context_result:

                result["context"] = context_result

            # ------------------------------------------------
            # STEP 4: CONTEXT-AWARE RECONCILIATION
            # ------------------------------------------------

            if context_result:

                context_status = context_result.get(
                    "context_status",
                    "unknown"
                )

                context_score = context_result.get(
                    "context_score",
                    0.0
                )

                context_sources = context_result.get(
                    "sources",
                    []
                )

                # ------------------------------------------------
                # STRONG CONTEXTUAL EVIDENCE
                # ------------------------------------------------
                #
                # If HybridMatcher says UNKNOWN but the resume
                # explicitly demonstrates the requirement,
                # upgrade it to MATCHED.
                #
                # Example:
                #
                # Python
                # Hybrid = unknown
                # Context = supported
                # Score = 1.0
                #
                # Final = matched
                # ------------------------------------------------

                if (
                    status == "unknown"
                    and context_status == "supported"
                    and context_score >= 0.85
                    and context_sources
                ):

                    status = "matched"

                    result["status"] = "matched"

                    result["confidence"] = round(
                        context_score,
                        4
                    )

                    result["match_source"] = "context"

                    result["context_match"] = True

                # ------------------------------------------------
                # MODERATE CONTEXTUAL EVIDENCE
                # ------------------------------------------------

                elif (
                    status == "unknown"
                    and context_status == "supported"
                    and context_score >= 0.60
                ):

                    status = "possible"

                    result["status"] = "possible"

                    result["confidence"] = round(
                        context_score,
                        4
                    )

                    result["match_source"] = "context"

                    result["context_match"] = True

                # ------------------------------------------------
            # STEP 5: EVIDENCE ANALYSIS
            # ------------------------------------------------

            evidence_result = self.analyze_evidence(
                requirement,
                resume
            )

            result["evidence"] = evidence_result

            # ------------------------------------------------
            # STEP 6: REQUIREMENT REASONING
            # ------------------------------------------------

            reasoning_result = self.reason_requirement(
                requirement=requirement,
                hybrid_result=result,
                context_result=context_result or {},
                evidence_result=evidence_result
            )

            result["reasoning"] = reasoning_result

            # ------------------------------------------------
            # STEP 7: FINAL CLASSIFICATION
            # ------------------------------------------------

            final_status = reasoning_result.get(
                "status",
                "unknown"
            )

            result["status"] = final_status

            result["confidence"] = reasoning_result.get(
                "confidence",
                result.get("confidence", 0.0)
            )

            if final_status == "matched":

                matched.append(
                    result
                )

            elif final_status == "possible":

                possible.append(
                    result
                )

            else:

                unknown.append(
                    result
                )


        return {
            "matched": matched,
            "possible": possible,
            "unknown": unknown
        }

    # ========================================================
    # EXPERIENCE MATCH
    # ========================================================

    # ========================================================
    # EXPERIENCE MATCH
    # ========================================================

    def analyze_experience(
        self,
        resume: Dict,
        job: Dict
    ) -> Dict:

        experience_matcher = (
            self._get_experience_matcher()
        )

        requirement = job.get(
            "experience",
            {}
        )

        if experience_matcher is None:

            return {
                "status": "unknown",
                "required_years": requirement.get(
                    "minimum_years"
                ),
                "candidate_years": None
            }

        try:

            return experience_matcher(
                resume,
                requirement
            )

        except TypeError:

            # Backward compatibility

            try:

                experience = (
                    self._get_experience_entries(
                        resume
                    )
                )

                return experience_matcher(
                    experience,
                    requirement
                )

            except Exception:

                return {
                    "status": "unknown",
                    "required_years": requirement.get(
                        "minimum_years"
                    ),
                    "candidate_years": None
                }

        except Exception:

            return {
                "status": "unknown",
                "required_years": requirement.get(
                    "minimum_years"
                ),
                "candidate_years": None
            }

    # ========================================================
    # RELEVANT EXPERIENCE
    # ========================================================

    def analyze_relevant_experience(
        self,
        resume: Dict,
        job: Dict
    ) -> Dict:
        """
        Analyze how much of the candidate's experience is
        relevant to the target job.

        RelevantExperienceAnalyzer handles:
            - job-title relevance
            - skill relevance
            - role duration
            - relevant years
            - relevant experience ratio
        """

        try:

            experience_requirement = (
                job.get("experience", {}) or {}
            )

            required_years = (
                experience_requirement.get(
                    "minimum_years",
                    0
                ) or 0
            )

            job_title = (
                job.get("title")
                or job.get("job_title")
                or ""
            )

            required_skills = (
                job.get("required_skills", [])
                or job.get("skills", [])
                or []
            )

            return self.relevant_experience_analyzer.analyze(
                resume=resume,
                job_title=job_title,
                required_skills=required_skills,
                required_years=float(required_years)
            )

        except Exception as error:

            return {
                "job_title": (
                    job.get("title")
                    or job.get("job_title")
                    or ""
                ),
                "required_years": 0.0,
                "candidate_years": 0.0,
                "relevant_years": 0.0,
                "experience_status": "unknown",
                "experience_requirement_ratio": 0.0,
                "relevant_experience_ratio": 0.0,
                "relevant_roles": [],
                "roles": [],
                "relevance_status": "unknown",
                "relevance_score": 0.0,
                "error": str(error)
            }

    # ========================================================
    # SKILL-SPECIFIC EXPERIENCE
    # ========================================================
    # SKILL-SPECIFIC EXPERIENCE
    # ========================================================

    def analyze_skill_experience(
        self,
        resume: Dict,
        skills: List[str]
    ) -> Dict:
        """
        Analyze practical experience for each required skill.

        This is different from normal skill matching.

        Skill matching answers:
            "Does the candidate have this skill?"

        Skill-specific experience answers:
            "Where has the candidate actually used this skill,
             and for how long?"
        """

        try:

            return self.skill_experience_matcher.analyze(
                skills,
                resume
            )

        except Exception as error:

            return {
                "skills": [],
                "matched": [],
                "possible": [],
                "unknown": [],
                "error": str(error)
            }

    # ========================================================
    # EXPERIENCE MATCHER LOADER
    # ========================================================

    def _get_experience_matcher(self):

        try:

            from app.matcher.experience_matcher import (
                match_experience
            )

            return match_experience

        except ImportError:

            return None

    # ========================================================
    # EDUCATION MATCH
    # ========================================================

    def analyze_education(
        self,
        resume: Dict,
        job: Dict
    ) -> Dict:

        requirements = job.get(
            "education",
            []
        )

        try:

            from app.matcher.education_matcher import (
                match_education
            )

            return match_education(
                resume,
                requirements
            )

        except ImportError:

            return {
                "status": "unknown",
                "matched": [],
                "unknown": requirements
            }

        except TypeError:

            # Backward compatibility

            try:

                education = (
                    self._get_education_entries(
                        resume
                    )
                )

                from app.matcher.education_matcher import (
                    match_education_requirement
                )

                matched = []
                unknown = []

                for requirement in requirements:

                    result = (
                        match_education_requirement(
                            requirement,
                            education
                        )
                    )

                    if result.get(
                        "status"
                    ) in (
                        "exact",
                        "related",
                        "matched"
                    ):

                        matched.append(
                            result
                        )

                    else:

                        unknown.append(
                            result
                        )

                return {
                    "status": (
                        "matched"
                        if matched
                        else "unknown"
                    ),
                    "matched": matched,
                    "unknown": unknown
                }

            except Exception:

                return {
                    "status": "unknown",
                    "matched": [],
                    "unknown": requirements
                }

        except Exception:

            return {
                "status": "unknown",
                "matched": [],
                "unknown": requirements
            }

    # ========================================================
    # PROJECT MATCH
    # ========================================================

    def analyze_projects(
        self,
        resume: Dict,
        job: Dict
    ) -> Dict:
        """
        Analyze whether the candidate's projects demonstrate
        the skills required by the target job.
        """

        projects = self._get_projects(resume)

        required_skills = job.get(
            "required_skills",
            []
        )

        matched_skills = []
        possible_skills = []
        unknown_skills = []

        # ====================================================
        # BUILD PROJECT SKILL LIST AND PROJECT TEXT
        # ====================================================

        project_skills = []
        project_texts = []

        for project in projects:

            if not isinstance(project, dict):
                continue

            project_name = project.get(
                "project_name",
                ""
            )

            description = project.get(
                "description",
                ""
            )

            raw_text = project.get(
                "raw_text",
                ""
            )

            technologies = project.get(
                "technologies",
                []
            )

            # ------------------------------------------------
            # Project technologies
            # ------------------------------------------------

            if isinstance(technologies, list):

                for technology in technologies:

                    if technology:
                        project_skills.append(
                            str(technology).strip()
                        )

            elif isinstance(technologies, str):

                if technologies.strip():
                    project_skills.append(
                        technologies.strip()
                    )

            # ------------------------------------------------
            # Project text
            # ------------------------------------------------

            text_parts = [
                str(project_name),
                str(description),
                str(raw_text)
            ]

            if isinstance(technologies, list):

                text_parts.extend(
                    str(x)
                    for x in technologies
                    if x
                )

            elif isinstance(technologies, str):

                text_parts.append(technologies)

            project_texts.append(
                " ".join(
                    part
                    for part in text_parts
                    if part and part != "None"
                )
            )

        # ====================================================
        # DEDUPLICATE PROJECT SKILLS
        # ====================================================

        unique_project_skills = []
        seen = set()

        for skill in project_skills:

            if not skill:
                continue

            normalized = (
                skill
                .lower()
                .strip()
                .rstrip(".,;:")
            )

            if normalized not in seen:

                seen.add(normalized)
                unique_project_skills.append(skill)

        # ====================================================
        # MATCH REQUIREMENTS AGAINST PROJECT SKILLS
        # ====================================================

        for requirement in required_skills:

            found = False

            # ------------------------------------------------
            # Direct technology matching
            # ------------------------------------------------

            result = self.hybrid_matcher.match_requirement(
                requirement,
                unique_project_skills
            )

            if result.get("status") == "matched":

                matched_skills.append(requirement)
                found = True

            elif result.get("status") == "possible":

                possible_skills.append(requirement)
                found = True

            # ------------------------------------------------
            # Fallback to project text
            # ------------------------------------------------

            if not found:

                for project_text in project_texts:

                    if not project_text:
                        continue

                    result = self.hybrid_matcher.match_requirement(
                        requirement,
                        [project_text]
                    )

                    if result.get("status") == "matched":

                        matched_skills.append(requirement)
                        found = True
                        break

                    elif result.get("status") == "possible":

                        possible_skills.append(requirement)
                        found = True
                        break

            # ------------------------------------------------
            # Unknown
            # ------------------------------------------------

            if not found:
                unknown_skills.append(requirement)

        return {
            "matched_skills": matched_skills,
            "possible_skills": possible_skills,
            "unknown_skills": unknown_skills
        }

    # ========================================================
    # PROJECT RELEVANCE
    # ========================================================

    def analyze_project_relevance(
        self,
        resume: Dict,
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Dict:
        """
        Analyze how relevant candidate projects are
        to the target job.
        """

        try:

            projects = resume.get(
                "projects",
                []
            )

            result = self.project_relevance_analyzer.analyze(
                projects=projects,
                required_skills=required_skills,
                preferred_skills=preferred_skills
            )

            # Normalize project relevance so downstream layers
            # receive a top-level status. The analyzer currently
            # stores status inside each relevant project.
            if not isinstance(result, dict):
                return {
                    "overall_project_relevance": 0.0,
                    "project_count": 0,
                    "relevant_projects": [],
                    "status": "unknown",
                }

            if "status" not in result:
                relevant_projects = result.get(
                    "relevant_projects", []
                )

                if isinstance(relevant_projects, list):
                    valid_projects = [
                        project
                        for project in relevant_projects
                        if isinstance(project, dict)
                    ]

                    if valid_projects:
                        def _project_relevance_score(project):
                            try:
                                return float(
                                    project.get(
                                        "relevance_score",
                                        0.0
                                    ) or 0.0
                                )
                            except (TypeError, ValueError):
                                return 0.0

                        best_project = max(
                            valid_projects,
                            key=_project_relevance_score
                        )

                        result["status"] = best_project.get(
                            "status",
                            "unknown"
                        )
                    else:
                        result["status"] = "unknown"
                else:
                    result["status"] = "unknown"

            return result

        except Exception as error:

            return {
                "overall_project_relevance": 0.0,
                "project_count": 0,
                "relevant_projects": [],
                "status": "unknown",
                "error": str(error)
            }

       # ========================================================
    # EVIDENCE
    # ========================================================

    def analyze_evidence(
        self,
        requirement: str,
        resume: Dict
    ) -> Dict:

        try:

            return self.evidence_engine.collect_evidence(
                requirement,
                resume
            )

        except AttributeError:

            try:

                return self.evidence_engine.find_evidence(
                    requirement,
                    resume
                )

            except AttributeError:

                try:

                    return self.evidence_engine.find(
                        requirement,
                        resume
                    )

                except Exception as error:

                    return {
                        "requirement": requirement,
                        "evidence": [],
                        "evidence_count": 0,
                        "best_source": None,
                        "best_weight": 0.0,
                        "evidence_strength": 0.0,
                        "source_coverage": 0.0,
                        "direct_evidence": False,
                        "indirect_evidence": False,
                        "evidence_quality": "none",
                        "status": "not_found",
                        "error": str(error)
                    }

            except Exception as error:

                return {
                    "requirement": requirement,
                    "evidence": [],
                    "evidence_count": 0,
                    "best_source": None,
                    "best_weight": 0.0,
                    "evidence_strength": 0.0,
                    "source_coverage": 0.0,
                    "direct_evidence": False,
                    "indirect_evidence": False,
                    "evidence_quality": "none",
                    "status": "not_found",
                    "error": str(error)
                }

        except Exception as error:

            return {
                "requirement": requirement,
                "evidence": [],
                "evidence_count": 0,
                "best_source": None,
                "best_weight": 0.0,
                "evidence_strength": 0.0,
                "source_coverage": 0.0,
                "direct_evidence": False,
                "indirect_evidence": False,
                "evidence_quality": "none",
                "status": "not_found",
                "error": str(error)
            }
    # ========================================================
    # BUILD MATCH RESULT
    # ========================================================

    def build_match_result(
        self,
        resume: Dict,
        job: Dict
    ) -> Dict:

        # ====================================================
        # COLLECT COMPLETE CANDIDATE SKILLS
        # ====================================================

        candidate_skills = (
            self._get_candidate_skills(
                resume
            )
        )

        # ----------------------------------------------------
        # Required skills
        # ----------------------------------------------------

        required_skills = job.get(
            "required_skills",
            []
        )

        required_result = (
            self.analyze_required_skills(
                required_skills,
                candidate_skills,
                resume
            )
        )

        # ----------------------------------------------------
        # Skill-specific experience
        # ----------------------------------------------------

        skill_experience_result = (
            self.analyze_skill_experience(
                resume,
                required_skills
            )
        )

        # ----------------------------------------------------
        # Preferred skills
        # ----------------------------------------------------

        preferred_skills = job.get(
            "preferred_skills",
            []
        )

        preferred_result = (
            self.analyze_preferred_skills(
                preferred_skills,
                candidate_skills,
                resume
            )
        )

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        experience_result = (
            self.analyze_experience(
                resume,
                job
            )
        )

        # ----------------------------------------------------
        # Relevant experience
        # ----------------------------------------------------

        # Use the central experience matcher as the single
        # source of employment duration. RelevantExperienceAnalyzer
        # evaluates relevance; it does not recalculate dates.
        relevant_resume = dict(resume)

        experience_details = experience_result.get(
            "experience_details",
            []
        )

        if not isinstance(experience_details, list):
            experience_details = []

        relevant_resume["experience"] = [
            dict(role)
            for role in experience_details
            if isinstance(role, dict)
        ]

        relevant_experience_result = (
            self.analyze_relevant_experience(
                relevant_resume,
                job
            )
        )

        # ----------------------------------------------------
        # Education
        # ----------------------------------------------------

        education_result = (
            self.analyze_education(
                resume,
                job
            )
        )

        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------

        project_result = (
            self.analyze_projects(
                resume,
                job
            )
        )

        # ----------------------------------------------------
        # Project relevance
        # ----------------------------------------------------

        project_relevance_result = (
            self.analyze_project_relevance(
                resume=resume,
                required_skills=required_skills,
                preferred_skills=preferred_skills
            )
        )

        return {

            "job_title": job.get(
                "job_title"
            ),

            "resume_skills": candidate_skills,

            "skills": {

                "required": required_result,

                "preferred": preferred_result

            },

            "skill_experience": skill_experience_result,

            "experience": experience_result,

            "relevant_experience": relevant_experience_result,
            
            "education": education_result,

            "projects": project_result,

            "project_relevance": project_relevance_result
        }

        # ========================================================
    # REQUIREMENT REASONING
    # ========================================================

    def reason_requirement(
        self,
        requirement: str,
        hybrid_result: Dict,
        context_result: Dict,
        evidence_result: Dict
    ) -> Dict:
        """
        Combine HybridMatcher, ContextMatcher, and
        EvidenceEngine results into one requirement-level
        reasoning result.
        """

        try:

            return self.requirement_reasoner.reason(
                requirement=requirement,
                hybrid_result=hybrid_result,
                context_result=context_result,
                evidence_result=evidence_result
            )

        except Exception as error:

            return {
                "requirement": requirement,
                "status": "unknown",
                "confidence": 0.0,
                "direct_match": False,
                "relationship_match": False,
                "context_supported": False,
                "evidence_found": False,
                "direct_evidence": False,
                "match_score": 0.0,
                "context_score": 0.0,
                "evidence_score": 0.0,
                "evidence_quality": "none",
                "best_source": None,
                "source_coverage": 0.0,
                "reason": (
                    "Requirement reasoning failed: "
                    f"{str(error)}"
                )
            }

        
    def reason_candidate_job(
        self,
        job_title: str,
        match_result: Dict,
        context: Dict,
        evidence: Dict
    ) -> Dict:
        
        try:

            return self.candidate_job_reasoner.reason(
                job_title=job_title,
                match_result=match_result,
                context=context,
                evidence=evidence
            )
        except Exception as error:
            return {
               "job_title": job_title,
               "status": "unknown",
               "overall_score": 0.0,
               "reason": (
                   "Candidate-job reasoning failed: "
                   f"{str(error)}"
                ),
            }
    # ========================================================
    # BUILD CONTEXT RESULT
    # ========================================================

    def build_context_result(
        self,
        match_result: Dict
    ) -> Dict:
        """
        Extract contextual information from the already
        calculated skill results.

        This prevents running ContextMatcher twice.
        """

        context = {}

        skills = match_result.get(
            "skills",
            {}
        )

        required = skills.get(
            "required",
            {}
        )

        for category in (
            "matched",
            "possible",
            "unknown"
        ):

            results = required.get(
                category,
                []
            )

            for result in results:

                if not isinstance(
                    result,
                    dict
                ):

                    continue

                requirement = result.get(
                    "requirement"
                )

                if not requirement:
                    continue

                context[requirement] = result.get(
                    "context",
                    {}
                )

        return context

    # ========================================================
    # ATS SCORE
    # ========================================================

    def calculate_ats_score(
        self,
        match_result: Dict
    ) -> Dict:

        try:

            return calculate_ats_score(
                match_result
            )

        except Exception as error:

            return {
                "score": 0.0,
                "breakdown": {},
                "classification": "poor",
                "error": str(error)
            }

    # ========================================================
    # ATS SCORE SUMMARY
    # ========================================================

    def generate_ats_summary(
        self,
        match_result: Dict
    ) -> Dict:

        try:

            return generate_score_summary(
                match_result
            )

        except Exception as error:

            return {
                "ats_score": 0.0,
                "classification": "poor",
                "breakdown": {},
                "matched_requirements": [],
                "missing_requirements": [],
                "error": str(error)
            }

    # ========================================================
    # DECISION
    # ========================================================

    def make_decision(
        self,
        match_result: Dict
    ) -> Dict:

        try:

            return self.decision_engine.evaluate(
                match_result
            )

        except AttributeError:

            try:

                return self.decision_engine.decide(
                    match_result
                )

            except Exception:

                return {
                    "decision": "review",
                    "confidence": 0.0,
                    "reason": (
                        "Decision engine could not "
                        "evaluate the match."
                    )
                }

        except Exception:

            return {
                "decision": "review",
                "confidence": 0.0,
                "reason": (
                    "Decision engine could not "
                    "evaluate the match."
                )
            }

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        resume: Dict,
        job: Dict
    ) -> Dict:

        if not isinstance(
            resume,
            dict
        ):

            raise TypeError(
                "resume must be a dictionary"
            )

        if not isinstance(
            job,
            dict
        ):

            raise TypeError(
                "job must be a dictionary"
            )

        # ----------------------------------------------------
        # STEP 1: Build match
        # ----------------------------------------------------

        match_result = (
            self.build_match_result(
                resume,
                job
            )
        )

        # ----------------------------------------------------
        # STEP 2: ATS scoring
        # ----------------------------------------------------

        ats_result = (
            self.calculate_ats_score(
                match_result
            )
        )

        # ----------------------------------------------------
        # STEP 3: ATS summary
        # ----------------------------------------------------

        ats_summary = (
            self.generate_ats_summary(
                match_result
            )
        )

        # ----------------------------------------------------
        # STEP 4: Context
        # ----------------------------------------------------

        context = (
            self.build_context_result(
                match_result
            )
        )

        # ----------------------------------------------------
        # STEP 5: Evidence
        # ----------------------------------------------------

        evidence = {}

        required_skills = job.get(
            "required_skills",
            []
        )

        for requirement in required_skills:

            evidence[requirement] = (
                self.analyze_evidence(
                    requirement,
                    resume
                )
            )

        # ----------------------------------------------------
        # STEP 6: Decision
        # ----------------------------------------------------

        decision = self.make_decision(
            match_result
        )

        print("\n" + "=" * 60)
        print("DEBUG: MATCH RESULT BEFORE CANDIDATE JOB REASONER")
        print("=" * 60)

        print("PROJECT RELEVANCE:")
        print(match_result.get("project_relevance"))

        print("\nEXPERIENCE:")
        print(match_result.get("experience"))

        print("\nRELEVANT EXPERIENCE:")
        print(match_result.get("relevant_experience"))

        print("\nEDUCATION:")
        print(match_result.get("education"))

        print("\nSKILLS:")
        print(match_result.get("skills"))

        print("=" * 60)
        
        candidate_job_reasoning = self.reason_candidate_job(
            job_title=job.get("job_title", ""),
            match_result=match_result,
            context=context,
            evidence=evidence,
        )

        print(
            "PROJECT STATUS:",
            match_result
            .get("project_relevance", {})
            .get("status")
        )

        
        print(
            "PROJECT RELEVANCE OBJECT ID:",
            id(match_result.get("project_relevance"))
        )
        

        return {
            "job_title": job.get("job_title"),
            "ats_score": ats_result.get("score", 0.0),
            "classification": ats_result.get(
                "classification",
                "poor"
            ),
             "score_breakdown": ats_result.get(
                "breakdown",
                {}
            ),
            "ats": ats_result,
            "score_summary": ats_summary,
            "match": match_result,
            "context": context,
            "evidence": evidence,
            "decision": decision,
            "candidate_job_reasoning": candidate_job_reasoning,
        }

       

# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def analyze_talent_match(
    resume: Dict,
    job: Dict
) -> Dict:

    engine = TalentMatchEngine()

    return engine.analyze(
        resume,
        job
    )
