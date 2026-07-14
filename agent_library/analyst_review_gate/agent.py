"""Analyst review routing gateway."""

from __future__ import annotations

from dataclasses import dataclass

from agent_runtime.base import RuleBasedAgent
from agent_runtime.contracts import AgentInput, ExecutionContext
from agent_runtime.exceptions import ValidationError
from agent_runtime.registry import register


@dataclass
class ReviewGatePayload:
    case_id: str
    filename: str
    entities: dict
    completeness_findings: dict


@register()
class AnalystReviewGateAgent(RuleBasedAgent[ReviewGatePayload]):
    agent_name = "analyst_review_gate"

    async def validate_input(self, agent_input: AgentInput) -> ReviewGatePayload:
        filename = agent_input.data.get("filename")
        entities = agent_input.data.get("entities")
        completeness = agent_input.data.get("completeness_findings")
        if not filename:
            raise ValidationError("filename is required at analyst review gate")
        if not entities:
            raise ValidationError("entities are required at analyst review gate")
        if not completeness:
            raise ValidationError("completeness_findings are required at analyst review gate")
        return ReviewGatePayload(
            case_id=str(agent_input.data.get("case_id") or filename),
            filename=str(filename),
            entities=dict(entities),
            completeness_findings=dict(completeness),
        )

    async def execute(self, payload: ReviewGatePayload, context: ExecutionContext) -> dict:
        route = "mandatory_human_review"
        reason = "Per-case compliance and quality handling requires analyst review"
        if not payload.completeness_findings.get("is_complete", False):
            reason = "Incomplete KYC data requires analyst review before finalization"

        return {
            "case_id": payload.case_id,
            "filename": payload.filename,
            "entities": payload.entities,
            "completeness_findings": payload.completeness_findings,
            "review_route": route,
            "route_reason": reason,
            "requires_human_review": True,
        }

    async def validate_output(self, result: dict) -> dict:
        if not result.get("requires_human_review"):
            raise ValidationError("Analyst review gate must route to human review")
        return result
