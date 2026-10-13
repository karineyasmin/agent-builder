"""LLM Factory providing resilient chat model instances with automatic fallback."""

from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.core.config import settings
from app.core.exceptions import ConfigurationError
from app.infrastructure.logging.logger import logger


def get_llm_with_fallback(
    temperature: float = 0.2, gemini_model: str | None = None, local_model: str | None = None
) -> Runnable[LanguageModelInput, BaseMessage]:
    """Instantiate primary Gemini client with automatic local Ollama fallback.

    Args:
        temperature: Model sampling temperature.
        gemini_model: Optional override for default Gemini model identifier.
        local_model: Optional override for local fallback model identifier.

    Returns:
        Runnable[LanguageModelInput, BaseMessage]: LangChain runnable pipeline with configured fallbacks.

    Raises:
        ConfigurationError: If GOOGLE_API_KEY is missing from environment.
    """

    if not settings.GOOGLE_API_KEY:
        logger.error("Failed to initialize LLM provider: missing API key", provider="gemini")
        raise ConfigurationError("GOOGLE_API_KEY is required but was not provided.")

    logger.debug(
        "Initializing primary Gemini LLM client",
        model=gemini_model or settings.DEFAULT_GEMINI_MODEL,
        temperature=temperature,
    )

    primary_llm = ChatGoogleGenerativeAI(
        model=gemini_model or settings.DEFAULT_GEMINI_MODEL,
        api_key=SecretStr(settings.GOOGLE_API_KEY),
        temperature=temperature,
        request_timeout=30.0,
    )

    logger.debug(
        "Initializing local fallback LLM client",
        base_url=settings.LOCAL_LLM_BASE_URL,
        model=local_model or settings.LOCAL_LLM_MODEL,
        timeout=settings.LOCAL_LLM_TIMEOUT,
    )

    local_fallback_llm = ChatOpenAI(
        base_url=settings.LOCAL_LLM_BASE_URL,
        api_key=SecretStr("not-needed"),
        model=local_model or settings.LOCAL_LLM_MODEL,
        temperature=temperature,
        timeout=settings.LOCAL_LLM_TIMEOUT,
    )

    logger.info(
        "Configuring LLM client with automatic fallback",
        primary=gemini_model or settings.DEFAULT_GEMINI_MODEL,
        fallback=local_model or settings.LOCAL_LLM_MODEL,
    )

    return primary_llm.with_fallbacks([local_fallback_llm])
