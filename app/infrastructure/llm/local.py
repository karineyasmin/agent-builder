"""Local LLM provider client wrapper using OpenAI-compatible endpoints."""

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.core.config import settings
from app.infrastructure.logging.logger import logger


def get_local_client(
    model_name: str | None = None,
    temperature: float = 0.2,
    base_url: str | None = None,
    timeout: float | None = None,
) -> ChatOpenAI:
    """Instantiate a local chat model client (Ollama/vLLM) via OpenAI-compatible API.

    Args:
        model_name: Local model identifier (e.g., 'qwen2.5:3b'). Defaults to config.
        temperature: Sampling temperature between 0.0 and 2.0.
        base_url: Endpoint URL for the local inference engine. Defaults to config.
        timeout: HTTP request timeout in seconds optimized for CPU execution.

    Returns:
        ChatOpenAI: Configured chat client pointing to local inference engine.
    """
    selected_model = model_name or settings.LOCAL_LLM_MODEL
    selected_url = base_url or settings.LOCAL_LLM_BASE_URL
    selected_timeout = timeout or settings.LOCAL_LLM_TIMEOUT

    logger.debug(
        "Instantiating local LLM client",
        model=selected_model,
        base_url=selected_url,
        timeout=selected_timeout,
    )

    return ChatOpenAI(
        base_url=selected_url,
        api_key=SecretStr("not-needed"),
        model=selected_model,
        temperature=temperature,
        timeout=selected_timeout,
    )
