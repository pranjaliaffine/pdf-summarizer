"""Base agent classes and lifecycle."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from agent_runtime.contracts import AgentInput, AgentOutput, ExecutionContext, ExecutionStatus
from agent_runtime.exceptions import ValidationError

TIn = TypeVar("TIn")


class BaseAgent(ABC, Generic[TIn]):
    """Template-method agent with validate → execute → validate lifecycle."""

    agent_name: ClassVar[str]
    __abstract_agent__: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.__abstract_agent__:
            return
        if not getattr(cls, "agent_name", None):
            raise TypeError(f"{cls.__name__} must define agent_name")

    @abstractmethod
    async def validate_input(self, agent_input: AgentInput) -> TIn:
        """Validate and parse incoming workflow state."""

    @abstractmethod
    async def execute(self, payload: TIn, context: ExecutionContext) -> Any:
        """Run the agent's core logic."""

    @abstractmethod
    async def validate_output(self, result: Any) -> dict[str, Any]:
        """Validate and serialize agent output."""

    async def run(self, agent_input: AgentInput, context: ExecutionContext) -> AgentOutput:
        started = time.perf_counter()
        try:
            payload = await self.validate_input(agent_input)
            result = await self.execute(payload, context)
            data = await self.validate_output(result)
            duration_ms = (time.perf_counter() - started) * 1000
            return AgentOutput(
                agent=self.agent_name,
                status=ExecutionStatus.SUCCESS,
                data=data,
                attempts=context.attempt,
                duration_ms=duration_ms,
            )
        except ValidationError as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            return AgentOutput(
                agent=self.agent_name,
                status=ExecutionStatus.FAILED,
                data={},
                error={"type": "ValidationError", "message": str(exc)},
                attempts=context.attempt,
                duration_ms=duration_ms,
            )
        except Exception as exc:  # noqa: BLE001 - surface step failures to executor
            duration_ms = (time.perf_counter() - started) * 1000
            return AgentOutput(
                agent=self.agent_name,
                status=ExecutionStatus.FAILED,
                data={},
                error={"type": type(exc).__name__, "message": str(exc)},
                attempts=context.attempt,
                duration_ms=duration_ms,
            )


class RuleBasedAgent(BaseAgent[TIn], ABC):
    """Deterministic agent without LLM dependency."""

    __abstract_agent__ = True


class LLMAgent(BaseAgent[TIn], ABC):
    """LLM-backed agent with mock fallback when credentials are absent."""

    __abstract_agent__ = True

    async def complete(
        self,
        context: ExecutionContext,
        *,
        system: str,
        prompt: str,
    ) -> str:
        if context.dry_run or not context.services.llm_available:
            return f"[mock-llm] {prompt[:200]}"
        raise NotImplementedError("Live LLM calls require Azure OpenAI configuration")
