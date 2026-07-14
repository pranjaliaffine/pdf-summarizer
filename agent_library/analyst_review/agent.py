"""Human-in-the-loop analyst review placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from agent_runtime.base import RuleBasedAgent
from agent_runtime.contracts import AgentInput, ExecutionContext, ExecutionStatus
from agent_runtime.exceptions import ValidationError
from agent_runtime.registry import register


@dataclass
class AnalystReviewPayload:
    case_id: str
    filename: str
    entities: dict
    completeness_findings: dict
    analyst_disposition: str | None
    analyst_notes: str | None


@register()
class AnalystReviewAgent(RuleBasedAgent[AnalystReviewPayload]):
    agent_name = "analyst_review"

    async def validate_input(self, agent_input: AgentInput) -> AnalystReviewPayload:
        filename = agent_input.data.get("filename")
        entities = agent_input.data.get("entities")
        completeness = agent_input.data.get("completeness_findings")
        if not filename:
            raise ValidationError("filename is required for analyst review")
        if not entities:
            raise ValidationError("entities are required for analyst review")
        if not completeness:
            raise ValidationError("completeness_findings are required for analyst review")
        return AnalystReviewPayload(
            case_id=str(agent_input.data.get("case_id") or filename),
            filename=str(filename),
            entities=dict(entities),
            completeness_findings=dict(completeness),
            analyst_disposition=agent_input.data.get("analyst_disposition"),
            analyst_notes=agent_input.data.get("analyst_notes"),
        )

    async def execute(self, payload: AnalystReviewPayload, context: ExecutionContext) -> dict:
        settings = context.settings
        disposition = payload.analyst_disposition
        notes = payload.analyst_notes

        if not disposition and getattr(settings, "hitl_auto_approve", True):
            disposition = "approved"
            notes = notes or "Auto-approved in non-interactive mode for workflow completion"

        if not disposition:
            return {
                "_hitl_pending": True,
                "case_id": payload.case_id,
                "filename": payload.filename,
                "entities": payload.entities,
                "completeness_findings": payload.completeness_findings,
                "analyst_review_status": "pending",
            }

        return {
            "case_id": payload.case_id,
            "filename": payload.filename,
            "entities": payload.entities,
            "completeness_findings": payload.completeness_findings,
            "analyst_disposition": disposition,
            "analyst_notes": notes,
            "analyst_review_status": "completed",
        }

    async def validate_output(self, result: dict) -> dict:
        if result.get("_hitl_pending"):
            return result
        if not result.get("analyst_disposition"):
            raise ValidationError("analyst_disposition is required after review")
        return result

    async def run(self, agent_input: AgentInput, context: ExecutionContext):
        output = await super().run(agent_input, context)
        if output.data.get("_hitl_pending"):
            output.status = ExecutionStatus.PENDING_HITL
            output.data.pop("_hitl_pending", None)
        return output
