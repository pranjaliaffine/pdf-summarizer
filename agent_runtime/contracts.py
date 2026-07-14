"""Shared contracts for agent I/O and workflow execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING_HITL = "pending_hitl"


class WorkflowStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING_HITL = "pending_hitl"


class AgentInput(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)
    source_agent: str | None = None


class AgentOutput(BaseModel):
    agent: str
    status: ExecutionStatus
    data: dict[str, Any] = Field(default_factory=dict)
    error: dict[str, Any] | None = None
    attempts: int = 1
    duration_ms: float = 0.0


class StepTrace(BaseModel):
    agent: str
    status: ExecutionStatus
    duration_ms: float
    error: dict[str, Any] | None = None


class WorkflowResult(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    outputs: list[AgentOutput] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
    trace: list[StepTrace] = Field(default_factory=list)
    failed_step: str | None = None
    duration_ms: float = 0.0

    @property
    def ok(self) -> bool:
        return self.status in {WorkflowStatus.SUCCESS, WorkflowStatus.PENDING_HITL}


class WorkflowContext(BaseModel):
    workflow_id: str
    state: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, AgentOutput] = Field(default_factory=dict)
    history: list[AgentOutput] = Field(default_factory=list)


@dataclass
class ServiceContainer:
    """Lightweight DI container for optional external services."""

    llm_available: bool = False
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    services: ServiceContainer
    settings: Any
    workflow_id: str | None = None
    attempt: int = 1
    dry_run: bool = False
