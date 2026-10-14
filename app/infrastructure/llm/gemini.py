"""Gemini LLM provider client wrapper with strict typing."""

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from app.core.config import settings
from app.core.exceptions import ConfigurationError
from app.infrastructure.logging.logger import logger


def get_gemini_client(
    model_name: str | None = None, temperature: float = 0.2, request_timeout: float = 30.0
) -> ChatGoogleGenerativeAI:
    """Instantiate a ChatGoogleGenerativeAI model client.

    Args:
        model_name: Gemini model ID override. Defaults to config value.
        temperature: MOdel samling temperature between 0.0 and 2.0.
        request_timeout: HTTP request timeout in seconds.

    Returns:
        ChatGoogleGenerativeAI: Configured LangChain chat model.

    Raises:
        ConfigurationError: If GOOGLE_API_KEY is not defined.
    """

    if not settings.GOOGLE_API_KEY:
        logger.error("Failed to initialize Gemini: GOOGLE_API_KEY is missing")
        raise ConfigurationError("GOOGLE_API_KEY is required but was not provided.")

    selected_model = model_name or settings.DEFAULT_GEMINI_MODEL
    logger.debug(
        "Instantiating Gemini client",
        model=selected_model,
        temperature=temperature,
    )

    return ChatGoogleGenerativeAI(
        model=selected_model,
        api_key=SecretStr(settings.GOOGLE_API_KEY),
        temperature=temperature,
        request_timeout=request_timeout,
    )
