"""KYC policy completeness validator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from agent_runtime.base import RuleBasedAgent
from agent_runtime.contracts import AgentInput, ExecutionContext
from agent_runtime.exceptions import ValidationError
from agent_runtime.registry import register

POLICY_PATH = Path(__file__).resolve().parents[2] / "templates" / "kyc_ingestion_policy.json"


@dataclass
class ValidationPayload:
    case_id: str
    filename: str
    entities: dict


@register()
class KycCompletenessValidationAgent(RuleBasedAgent[ValidationPayload]):
    agent_name = "kyc_completeness_validation"

    async def validate_input(self, agent_input: AgentInput) -> ValidationPayload:
        entities = agent_input.data.get("entities")
        filename = agent_input.data.get("filename")
        if not entities:
            raise ValidationError("entities are required for completeness validation")
        if not filename:
            raise ValidationError("filename is required for completeness validation")
        return ValidationPayload(
            case_id=str(agent_input.data.get("case_id") or Path(filename).stem),
            filename=str(filename),
            entities=dict(entities),
        )

    async def execute(self, payload: ValidationPayload, context: ExecutionContext) -> dict:
        policy = _load_policy()
        required_fields = policy.get("required_fields", [])
        missing_fields: list[str] = []
        present_fields: list[str] = []

        for field_spec in required_fields:
            field_name = field_spec["field"]
            if _field_present(payload.entities, field_name):
                present_fields.append(field_name)
            else:
                missing_fields.append(field_name)

        completeness_score = len(present_fields) / len(required_fields) if required_fields else 1.0
        is_complete = len(missing_fields) == 0

        return {
            "case_id": payload.case_id,
            "filename": payload.filename,
            "entities": payload.entities,
            "completeness_findings": {
                "policy_template": policy.get("template_name", "standard_corporate_kyc"),
                "is_complete": is_complete,
                "completeness_score": round(completeness_score, 2),
                "present_fields": present_fields,
                "missing_fields": missing_fields,
                "required_field_count": len(required_fields),
            },
        }

    async def validate_output(self, result: dict) -> dict:
        if "completeness_findings" not in result:
            raise ValidationError("completeness_findings output is required")
        return result


def _load_policy() -> dict:
    if POLICY_PATH.exists():
        return json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    return {
        "template_name": "standard_corporate_kyc",
        "required_fields": [
            {"field": "legal_entity_name", "label": "Legal entity name"},
            {"field": "jurisdiction", "label": "Jurisdiction"},
            {"field": "registration_number", "label": "Registration number"},
            {"field": "beneficial_owners", "label": "Beneficial owners"},
        ],
    }


def _field_present(entities: dict, field_name: str) -> bool:
    value = entities.get(field_name)
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return bool(value)
    return True
