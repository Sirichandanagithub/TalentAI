class TalentAIException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str = "TALENTAI_ERROR",
    ):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class ResumeNotFoundException(TalentAIException):
    def __init__(
        self,
        message: str = "Resume not found.",
    ):
        super().__init__(
            message=message,
            error_code="RESUME_NOT_FOUND",
        )


class AIServiceException(TalentAIException):
    def __init__(
        self,
        message: str = "AI service is temporarily unavailable.",
    ):
        super().__init__(
            message=message,
            error_code="AI_SERVICE_UNAVAILABLE",
        )
