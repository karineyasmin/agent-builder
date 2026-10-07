"""Custom domain exceptions for the agent builder platform"""

from typing import Any


class AgentBuilderError(Exception):
    """Base configuration for all agent builder errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(AgentBuilderError):
    """Raised when an environment variable or critical configuration is missing/invalid"""


class LLMProviderError(AgentBuilderError):
    """Raised when a primary or a fallback LLM provider encounters an error."""


class ToolExecutionError(AgentBuilderError):
    """Raised when executing an OpenAPI or MCP tool fails."""


class WorkflowExecutionError(AgentBuilderError):
    """Raised when a error occurs during LangGraph state graph execution"""


class ResourceNotFountError(AgentBuilderError):
    """Raised when a requested resource (graph, agent, session) is not found."""
