"""
LLM provider abstraction for TalentAI.

This module is responsible only for creating/accessing
the configured LLM provider.

The rest of the application should not directly depend
on a specific LLM provider.
"""

from typing import Any

from app.core.config import settings


class LLMProvider:
    """
    Provider abstraction for TalentAI's LLM layer.

    Currently this class is prepared for Ollama through
    LangChain, using the existing TalentAI configuration.

    The provider is intentionally lazy: the actual LLM
    object is created only when get_llm() is called.
    """

    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
    ):
        self.model_name = (
            model_name
            or settings.OLLAMA_MODEL_NAME
        )

        self.base_url = (
            base_url
            or settings.OLLAMA_BASE_URL
        )

    def get_llm(self) -> Any:
        """
        Create and return the configured Ollama LLM.

        Returns:
            ChatOllama instance.

        Raises:
            ValueError:
                If Ollama model configuration is missing.
            ImportError:
                If langchain-ollama is not installed.
        """

        if not self.model_name:
            raise ValueError(
                "OLLAMA_MODEL_NAME is not configured. "
                "Set it in the .env file before creating the LLM."
            )

        try:
            from langchain_ollama import ChatOllama
        except ImportError as exc:
            raise ImportError(
                "langchain-ollama is not installed. "
                "Install it with: pip install langchain-ollama"
            ) from exc

        kwargs = {
            "model": self.model_name,
        }

        if self.base_url:
            kwargs["base_url"] = self.base_url

        return ChatOllama(**kwargs)


def get_llm_provider() -> LLMProvider:
    """
    Return the default TalentAI LLM provider.

    This function provides a simple entry point for
    other modules.
    """

    return LLMProvider()