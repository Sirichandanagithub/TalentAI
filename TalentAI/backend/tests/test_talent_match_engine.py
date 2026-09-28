from pprint import pprint

from app.ai.analyzer.talent_match_engine import (
    TalentMatchEngine,
)


# ============================================================
# SAMPLE RESUME
# ============================================================

resume = {
    "skills": [
        "Python",
        "JavaScript",
        "MySQL",
        "MongoDB",
        "NoSQL",
        "Data Analysis",
        "Statistical Analysis",
        "Classification",
        "Regression",
        "Deep Learning",
        "Git",
        "Docker",
        "HTML",
        "CSS",
    ],

    "experience": [

        {

            "job_title": "Associate AI Engineer",
            "company": "Novum Labs",
            "location": "Hyderabad",
            "dates": {

               "start": "January 2025",
               "end": "Present",
               "current": True,
            },
        }
    ],


    "education": [
        {
            "institution": "Vignan Institute of Technology and Science",
            "degree": "B.Tech",
            "field": "CSE_AI&DS",
            "year": "2026",
        }
    ],

    "projects": [
        {
            "project_name": "AI Crime Prediction System",
            "description": (
                "Developed an AI-powered crime prediction system "
                "using machine learning and Python."
            ),
            "technologies": [
                "Python",
                "Pandas",
                "Scikit-learn",
                "Django",
            ],
        }
    ],

    "certifications": [],

    "summary": (
        "Data professional with experience in Python "
        "and machine learning."
    ),
}


# ============================================================
# SAMPLE JOB
# ============================================================

job = {
    "job_title": "Data Scientist",

    "required_skills": [
        "Python",
        "SQL",
        "Machine Learning",
        "Pandas",
        "Scikit-learn",
        "Data Analysis",
        "Artificial Intelligence",
    ],

    "preferred_skills": [
        "TensorFlow",
        "AWS",
    ],

    "experience": {
        "minimum_years": 3,
    },

    "education": [
        "computer science",
        "data science",
        "artificial intelligence",
    ],
}


# ============================================================
# TEST
# ============================================================

def test_talent_match_engine():

    print()
    print("=" * 60)
    print("TALENT MATCH ENGINE TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # TEST 1: INITIALIZE ENGINE
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 1: ENGINE INITIALIZATION")
    print("-" * 60)

    engine = TalentMatchEngine()

    assert engine is not None

    print("✅ TalentMatchEngine initialized.")

    # --------------------------------------------------------
    # TEST 2: RUN ANALYSIS
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 2: RUN ANALYSIS")
    print("-" * 60)

    result = engine.analyze(
        resume=resume,
        job=job,
    )

    assert isinstance(result, dict)

    print("✅ Analysis completed.")

    # --------------------------------------------------------
    # TEST 3: TOP LEVEL RESULT
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 3: TOP LEVEL RESULT")
    print("-" * 60)

    required_keys = [
        "job_title",
        "ats_score",
        "classification",
        "score_breakdown",
        "ats",
        "score_summary",
        "match",
        "context",
        "evidence",
        "decision",
        "candidate_job_reasoning",
    ]

    for key in required_keys:
        assert key in result, (
            f"Missing top-level key: {key}"
        )

    print("✅ Final result structure exists.")

    # --------------------------------------------------------
    # TEST 4: JOB
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 4: JOB")
    print("-" * 60)

    assert result["job_title"] == "Data Scientist"

    print(
        "Job title:",
        result["job_title"]
    )

    # --------------------------------------------------------
    # TEST 5: ATS
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 5: ATS")
    print("-" * 60)

    ats_score = result["ats_score"]

    assert isinstance(
        ats_score,
        (int, float)
    )

    assert 0 <= ats_score <= 100

    print(
        "ATS Score:",
        ats_score
    )

    print(
        "Classification:",
        result["classification"]
    )

    # --------------------------------------------------------
    # TEST 6: MATCH STRUCTURE
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 6: MATCH STRUCTURE")
    print("-" * 60)

    match_result = result["match"]

    assert isinstance(
        match_result,
        dict
    )

    match_keys = [
        "skills",
        "skill_experience",
        "experience",
        "education",
        "projects",
        "project_relevance",
    ]

    for key in match_keys:
        assert key in match_result, (
            f"Missing match key: {key}"
        )

    print(
        "✅ Match structure is valid."
    )

    # --------------------------------------------------------
    # TEST 7: REQUIRED SKILLS
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 7: REQUIRED SKILLS")
    print("-" * 60)

    required_result = (
        match_result["skills"]["required"]
    )

    pprint(required_result)

    assert "matched" in required_result
    assert "possible" in required_result
    assert "unknown" in required_result

    print("Matched:",required_result["matched"])
    

    print(
        "Possible:",
        required_result["possible"]
    )

    print(
        "Missing:",
        required_result["unknown"]
    )

    # --------------------------------------------------------
    # TEST 8: PREFERRED SKILLS
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 8: PREFERRED SKILLS")
    print("-" * 60)

    preferred_result = (
        match_result["skills"]["preferred"]
    )

    pprint(preferred_result)

    assert "matched" in preferred_result
    assert "possible" in preferred_result
    assert "unknown" in preferred_result

    # --------------------------------------------------------
    # TEST 9: SKILL-SPECIFIC EXPERIENCE
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 9: SKILL-SPECIFIC EXPERIENCE")
    print("-" * 60)

    skill_experience = (
        match_result["skill_experience"]
    )

    pprint(skill_experience)

    assert "skills" in skill_experience
    assert "matched" in skill_experience
    assert "possible" in skill_experience
    assert "unknown" in skill_experience

    print(
        "Matched Skills:",
        skill_experience["matched"]
    )

    print(
        "Possible Skills:",
        skill_experience["possible"]
    )

    print(
        "Unknown Skills:",
        skill_experience["unknown"]
    )

    print(
        "✅ Skill-specific experience "
        "layer connected."
    )

    # --------------------------------------------------------
    # TEST 10: EXPERIENCE
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 10: EXPERIENCE")
    print("-" * 60)

    experience_result = (
        match_result["experience"]
    )

    pprint(experience_result)

    assert "status" in experience_result
    assert "required_years" in experience_result

    print(
        "Status:",
        experience_result["status"]
    )

    print(
        "Required Years:",
        experience_result["required_years"]
    )

    print(
        "Candidate Years:",
        experience_result.get(
            "candidate_years"
        )
    )

    # --------------------------------------------------------
    # TEST 11: EDUCATION
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 11: EDUCATION")
    print("-" * 60)

    education_result = (
        match_result["education"]
    )

    pprint(education_result)

    assert isinstance(
        education_result,
        dict
    )

    # --------------------------------------------------------
    # TEST 12: PROJECT MATCHING
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 12: PROJECT MATCHING")
    print("-" * 60)

    project_result = (
        match_result["projects"]
    )

    print(project_result)

    assert "matched_skills" in project_result
    assert "possible_skills" in project_result
    assert "unknown_skills" in project_result

    print(
        "Matched Skills:",
        project_result["matched_skills"]
    )

    print(
        "Possible Skills:",
        project_result["possible_skills"]
    )

    print(
        "Unknown Skills:",
        project_result["unknown_skills"]
    )

    # --------------------------------------------------------
    # TEST 13: PROJECT RELEVANCE
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 13: PROJECT RELEVANCE")
    print("-" * 60)

    project_relevance = (
        match_result["project_relevance"]
    )

    print(project_relevance)

    assert isinstance(
        project_relevance,
        dict
    )

    assert (
        "overall_project_relevance"
        in project_relevance
    )

    assert (
        "project_count"
        in project_relevance
    )

    assert (
        "relevant_projects"
        in project_relevance
    )

    overall_relevance = (
        project_relevance[
            "overall_project_relevance"
        ]
    )

    project_count = (
        project_relevance[
            "project_count"
        ]
    )

    relevant_projects = (
        project_relevance[
            "relevant_projects"
        ]
    )

    assert isinstance(
        overall_relevance,
        (int, float)
    )

    assert 0 <= overall_relevance <= 1

    assert project_count == len(
        resume["projects"]
    )

    assert isinstance(
        relevant_projects,
        list
    )

    print(
        "Overall Project Relevance:",
        overall_relevance
    )

    print(
        "Project Count:",
        project_count
    )

    print(
        "Relevant Projects:",
        len(relevant_projects)
    )

    # --------------------------------------------------------
    # INDIVIDUAL PROJECTS
    # --------------------------------------------------------

    for project in relevant_projects:

        print()
        print(
            "Project:",
            project.get(
                "project_name"
            )
        )

        print(
            "Relevance Score:",
            project.get(
                "relevance_score"
            )
        )

        print(
            "Status:",
            project.get(
                "status"
            )
        )

        print(
            "Required Skill Score:",
            project.get(
                "required_skill_score"
            )
        )

        print(
            "Preferred Skill Score:",
            project.get(
                "preferred_skill_score"
            )
        )

        print(
            "Title Relevance:",
            project.get(
                "title_relevance"
            )
        )

        print(
            "Matched Required:",
            project.get(
                "matched_required"
            )
        )

        print(
            "Possible Required:",
            project.get(
                "possible_required"
            )
        )

        print(
            "Unknown Required:",
            project.get(
                "unknown_required"
            )
        )

        print(
            "Evidence:",
            project.get(
                "evidence"
            )
        )

        assert (
            "project_name"
            in project
        )

        assert (
            "relevance_score"
            in project
        )

        assert (
            "status"
            in project
        )

        assert 0 <= project[
            "relevance_score"
        ] <= 1

    print()
    print(
        "✅ Project relevance layer connected."
    )

    # --------------------------------------------------------
    # TEST 14: CONTEXT
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 14: CONTEXT")
    print("-" * 60)

    context_result = result["context"]

    print(context_result)

    assert isinstance(
        context_result,
        dict
    )

    print(
        "✅ Context layer connected."
    )

    # --------------------------------------------------------
    # TEST 15: EVIDENCE
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 15: EVIDENCE")
    print("-" * 60)

    evidence_result = result["evidence"]

    print(evidence_result)

    assert isinstance(
        evidence_result,
        dict
    )

    print(
        "✅ Evidence layer connected."
    )

    # --------------------------------------------------------
    # TEST 16: DECISION
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 16: DECISION")
    print("-" * 60)

    decision_result = result["decision"]

    print(decision_result)

    assert "decision" in decision_result
    assert "confidence" in decision_result
    assert "reason" in decision_result

    assert 0 <= decision_result[
        "confidence"
    ] <= 1

    print(
        "Decision:",
        decision_result["decision"]
    )

    print(
        "Confidence:",
        decision_result["confidence"]
    )

    print(
        "Reason:",
        decision_result["reason"]
    )

    print(
        "✅ Decision layer connected."
    )

    # --------------------------------------------------------
    # TEST 17: CANDIDATE-JOB REASONING
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 17: CANDIDATE-JOB REASONING")
    print("-" * 60)

    candidate_job_reasoning = (
        result["candidate_job_reasoning"]
    )

    pprint(candidate_job_reasoning)

    assert isinstance(
        candidate_job_reasoning,
        dict
    )

    assert (
        "job_title"
        in candidate_job_reasoning
    )

    assert (
        "status"
        in candidate_job_reasoning
    )

    assert (
        "overall_score"
        in candidate_job_reasoning
    )

    assert (
        "skill_alignment"
        in candidate_job_reasoning
    )

    assert (
        "experience_alignment"
        in candidate_job_reasoning
    )

    assert (
        "relevant_experience"
        in candidate_job_reasoning
    )

    assert (
        "project_alignment"
        in candidate_job_reasoning
    )

    assert (
        "education_alignment"
        in candidate_job_reasoning
    )

    assert (
        "evidence_alignment"
        in candidate_job_reasoning
    )

    assert (
        "strengths"
        in candidate_job_reasoning
    )

    assert (
        "gaps"
        in candidate_job_reasoning
    )

    assert (
        "reason"
        in candidate_job_reasoning
    )

    overall_score = (
        candidate_job_reasoning[
            "overall_score"
        ]
    )

    assert isinstance(
        overall_score,
        (int, float)
    )

    assert 0 <= overall_score <= 1

    print(
        "Job:",
        candidate_job_reasoning[
            "job_title"
        ]
    )

    print(
        "Status:",
        candidate_job_reasoning[
            "status"
        ]
    )

    print(
        "Overall Score:",
        overall_score
    )

    print(
        "Skill Alignment:"
    )

    pprint(
        candidate_job_reasoning[
            "skill_alignment"
        ]
    )

    print(
        "Experience Alignment:"
    )

    pprint(
        candidate_job_reasoning[
            "experience_alignment"
        ]
    )

    print(
        "Relevant Experience:"
    )

    pprint(
        candidate_job_reasoning[
            "relevant_experience"
        ]
    )

    print(
        "Project Alignment:"
    )

    pprint(
        candidate_job_reasoning[
            "project_alignment"
        ]
    )

    print(
        "Education Alignment:"
    )

    pprint(
        candidate_job_reasoning[
            "education_alignment"
        ]
    )

    print(
        "Evidence Alignment:"
    )

    pprint(
        candidate_job_reasoning[
            "evidence_alignment"
        ]
    )

    print(
        "Strengths:"
    )

    pprint(
        candidate_job_reasoning[
            "strengths"
        ]
    )

    print(
        "Gaps:"
    )

    pprint(
        candidate_job_reasoning[
            "gaps"
        ]
    )

    print(
        "Reason:"
    )

    print(
        candidate_job_reasoning[
            "reason"
        ]
    )

    print(
        "✅ Candidate-job reasoning layer "
        "connected."
    )

    # --------------------------------------------------------
    # TEST 18: DEBUG MATCH RESULT
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # CandidateJobReasoner currently expects certain
    # structures inside match_result.
    #
    # We print the actual structure here so we can compare
    # what TalentMatchEngine produces with what
    # CandidateJobReasoner consumes.
    #
    # This is intentionally diagnostic and does not change
    # the TalentMatchEngine itself.
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("TEST 18: DEBUG MATCH RESULT STRUCTURE")
    print("-" * 60)

    print()
    print("MATCH RESULT KEYS:")
    pprint(
        list(match_result.keys())
    )

    print()
    print("MATCH RESULT:")
    pprint(
        match_result
    )

    print()
    print("MATCH RESULT - SKILLS:")
    pprint(
        match_result.get(
            "skills"
        )
    )

    print()
    print("MATCH RESULT - EXPERIENCE:")
    pprint(
        match_result.get(
            "experience"
        )
    )

    print()
    print("MATCH RESULT - EDUCATION:")
    pprint(
        match_result.get(
            "education"
        )
    )

    print()
    print("MATCH RESULT - PROJECT RELEVANCE:")
    pprint(
        match_result.get(
            "project_relevance"
        )
    )

    print()
    print("TOP LEVEL EVIDENCE:")
    pprint(
        result.get(
            "evidence"
        )
    )

    print()
    print("TOP LEVEL CONTEXT:")
    pprint(
        result.get(
            "context"
        )
    )

    print(
        "✅ Diagnostic structure printed."
    )

    # --------------------------------------------------------
    # TEST 19: FINAL SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("TEST 19: FINAL SUMMARY")
    print("=" * 60)

    print(
        "Job:",
        result["job_title"]
    )

    print(
        "ATS Score:",
        result["ats_score"]
    )

    print(
        "Classification:",
        result["classification"]
    )

    print(
        "Project Relevance:",
        project_relevance[
            "overall_project_relevance"
        ]
    )

    print(
        "Decision:",
        result["decision"]["decision"]
    )

    print()
    print(
        "Candidate-Job Reasoning:"
    )

    pprint(
        result[
            "candidate_job_reasoning"
        ]
    )

    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)

    print(
        "✅ Final result structure is valid."
    )

    print(
        "✅ Job title detected:",
        result["job_title"]
    )

    print(
        "✅ ATS score:",
        result["ats_score"]
    )

    print(
        "✅ Classification:",
        result["classification"]
    )

    print(
        "✅ Skill-specific experience "
        "layer connected."
    )

    print(
        "✅ Project relevance "
        "layer connected."
    )

    print(
        "✅ Context layer connected."
    )

    print(
        "✅ Evidence layer connected."
    )

    print(
        "✅ Decision layer connected."
    )

    print(
        "✅ Candidate-job reasoning "
        "layer connected."
    )

    print()
    print("=" * 60)
    print(
        "TALENTAI MATCH ENGINE TEST PASSED"
    )
    print("=" * 60)


# ============================================================
# RUN TEST DIRECTLY
# ============================================================

if __name__ == "__main__":
    test_talent_match_engine()