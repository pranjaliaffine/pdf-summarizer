"""Agent runtime exceptions."""


class AgentRuntimeError(Exception):
    """Base error for agent runtime."""


class ValidationError(AgentRuntimeError):
    """Raised when input or output validation fails."""


class AgentNotFoundError(AgentRuntimeError):
    """Raised when a requested agent is not registered."""
