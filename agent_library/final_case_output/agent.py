"""Final case output publisher."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from agent_runtime.base import RuleBasedAgent
from agent_runtime.contracts import AgentInput, ExecutionContext
from agent_runtime.exceptions import ValidationError
from agent_runtime.registry import register


@dataclass
class FinalOutputPayload:
    case_id: str
    filename: str
    entities: dict
    completeness_findings: dict
    analyst_disposition: str
    analyst_notes: str | None


@register()
class FinalCaseOutputAgent(RuleBasedAgent[FinalOutputPayload]):
    agent_name = "final_case_output"

    async def validate_input(self, agent_input: AgentInput) -> FinalOutputPayload:
        filename = agent_input.data.get("filename")
        entities = agent_input.data.get("entities")
        completeness = agent_input.data.get("completeness_findings")
        disposition = agent_input.data.get("analyst_disposition")
        if not filename:
            raise ValidationError("filename is required for final case output")
        if not entities:
            raise ValidationError("entities are required for final case output")
        if not completeness:
            raise ValidationError("completeness_findings are required for final case output")
        if not disposition:
            raise ValidationError("analyst_disposition is required for final case output")
        return FinalOutputPayload(
            case_id=str(agent_input.data.get("case_id") or filename),
            filename=str(filename),
            entities=dict(entities),
            completeness_findings=dict(completeness),
            analyst_disposition=str(disposition),
            analyst_notes=agent_input.data.get("analyst_notes"),
        )

    async def execute(self, payload: FinalOutputPayload, context: ExecutionContext) -> dict:
        published_at = datetime.now(timezone.utc).isoformat()
        case_package = {
            "case_id": payload.case_id,
            "document_identifier": payload.filename,
            "extracted_entities": payload.entities,
            "completeness_assessment": payload.completeness_findings,
            "analyst_disposition": payload.analyst_disposition,
            "analyst_notes": payload.analyst_notes,
            "published_at": published_at,
            "status": "finalized",
        }
        summary = (
            f"Case {payload.case_id} finalized with disposition '{payload.analyst_disposition}'. "
            f"Completeness score: {payload.completeness_findings.get('completeness_score', 'n/a')}."
        )
        return {
            "case_id": payload.case_id,
            "filename": payload.filename,
            "case_package": case_package,
            "summary": summary,
            "publication_status": "published",
        }

    async def validate_output(self, result: dict) -> dict:
        if "case_package" not in result:
            raise ValidationError("case_package is required")
        return result
