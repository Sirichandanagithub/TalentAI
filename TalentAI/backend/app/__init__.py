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

    print(
        "TalentAI Match Engine initialized successfully."
    )