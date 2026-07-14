"""Sequential workflow executor with input mapping."""

from __future__ import annotations

import time
from typing import Any, Sequence

from pydantic import BaseModel, Field

from agent_runtime.contracts import (
    AgentInput,
    AgentOutput,
    ExecutionContext,
    ExecutionStatus,
    StepTrace,
    WorkflowContext,
    WorkflowResult,
    WorkflowStatus,
)
from agent_runtime.registry import AgentRegistry


class WorkflowStep(BaseModel):
    agent: str
    node_id: str | None = None
    optional: bool = False
    max_attempts: int = 1
    input_map: dict[str, str] = Field(default_factory=dict)


class WorkflowExecutor:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def _normalize_step(self, step: str | WorkflowStep | dict[str, Any]) -> WorkflowStep:
        if isinstance(step, str):
            return WorkflowStep(agent=step)
        if isinstance(step, WorkflowStep):
            return step
        return WorkflowStep.model_validate(step)

    def _build_input(self, step: WorkflowStep, state: dict[str, Any]) -> AgentInput:
        if not step.input_map:
            return AgentInput(data=dict(state))
        mapped = {dst: state[src] for dst, src in step.input_map.items() if src in state}
        for key, value in state.items():
            mapped.setdefault(key, value)
        return AgentInput(data=mapped)

    async def run(
        self,
        workflow_id: str,
        steps: Sequence[str | WorkflowStep | dict[str, Any]],
        initial_input: AgentInput | dict[str, Any] | None,
        context: ExecutionContext,
        *,
        raise_on_error: bool = False,
    ) -> WorkflowResult:
        normalized = [self._normalize_step(step) for step in steps]
        for step in normalized:
            if step.agent not in self.registry.list_agents():
                raise ValueError(f"Unknown agent '{step.agent}' in workflow")

        if isinstance(initial_input, AgentInput):
            seed = dict(initial_input.data)
        elif isinstance(initial_input, dict):
            seed = dict(initial_input)
        else:
            seed = {}

        wf_context = WorkflowContext(workflow_id=workflow_id, state=seed)
        traces: list[StepTrace] = []
        outputs: list[AgentOutput] = []
        started = time.perf_counter()
        failed_step: str | None = None
        final_status = WorkflowStatus.SUCCESS

        for step in normalized:
            agent = self.registry.create(step.agent)
            agent_input = self._build_input(step, wf_context.state)
            output = await agent.run(agent_input, context)
            outputs.append(output)
            wf_context.outputs[step.agent] = output
            wf_context.history.append(output)
            traces.append(
                StepTrace(
                    agent=step.agent,
                    status=output.status,
                    duration_ms=output.duration_ms,
                    error=output.error,
                )
            )

            if output.status == ExecutionStatus.SUCCESS:
                wf_context.state.update(output.data)
                continue

            if output.status == ExecutionStatus.PENDING_HITL:
                final_status = WorkflowStatus.PENDING_HITL
                break

            if step.optional:
                final_status = WorkflowStatus.PARTIAL
                continue

            failed_step = step.agent
            final_status = WorkflowStatus.FAILED
            if raise_on_error:
                raise RuntimeError(output.error)
            break

        duration_ms = (time.perf_counter() - started) * 1000
        return WorkflowResult(
            workflow_id=workflow_id,
            status=final_status,
            outputs=outputs,
            state=wf_context.state,
            trace=traces,
            failed_step=failed_step,
            duration_ms=duration_ms,
        )
