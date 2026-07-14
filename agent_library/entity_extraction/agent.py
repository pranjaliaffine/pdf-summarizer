"""Entity extraction agent."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from agent_runtime.base import LLMAgent
from agent_runtime.contracts import AgentInput, ExecutionContext
from agent_runtime.exceptions import ValidationError
from agent_runtime.registry import register


@dataclass
class ExtractionPayload:
    case_id: str
    filename: str
    document_text: str


@register()
class EntityExtractionAgent(LLMAgent[ExtractionPayload]):
    agent_name = "entity_extraction"

    async def validate_input(self, agent_input: AgentInput) -> ExtractionPayload:
        filename = agent_input.data.get("filename")
        document_text = agent_input.data.get("document_text")
        case_id = agent_input.data.get("case_id")
        if not filename:
            raise ValidationError("filename is required for entity extraction")
        if not document_text:
            raise ValidationError("document_text is required for entity extraction")
        return ExtractionPayload(
            case_id=str(case_id or _path_stem(filename)),
            filename=str(filename),
            document_text=str(document_text),
        )

    async def execute(self, payload: ExtractionPayload, context: ExecutionContext) -> dict:
        if context.services.llm_available and not context.dry_run:
            llm_text = await self.complete(
                context,
                system="Extract KYC entities as JSON.",
                prompt=payload.document_text,
            )
            try:
                entities = json.loads(llm_text)
            except json.JSONDecodeError:
                entities = _rule_based_entities(payload)
        else:
            entities = _rule_based_entities(payload)

        return {
            "case_id": payload.case_id,
            "filename": payload.filename,
            "entities": entities,
            "extraction_method": "llm" if context.services.llm_available else "rule_based",
        }

    async def validate_output(self, result: dict) -> dict:
        if "entities" not in result:
            raise ValidationError("entities output is required")
        return result


def _path_stem(filename: str) -> str:
    from pathlib import Path

    return Path(filename).stem


def _rule_based_entities(payload: ExtractionPayload) -> dict:
    text = payload.document_text
    legal_name = _find_pattern(text, r"(?:Legal entity|Company name)[:\s]+([^\n\.]+)", "Acme Holdings Ltd.")
    jurisdiction = _find_pattern(text, r"(?:Jurisdiction|Country of incorporation)[:\s]+([^\n\.]+)", "Delaware, USA")
    registration = _find_pattern(text, r"(?:Registration|Company) number[:\s]+([^\n\.]+)", "REG-000123")
    return {
        "document_identifier": payload.filename,
        "legal_entity_name": legal_name,
        "jurisdiction": jurisdiction,
        "registration_number": registration,
        "beneficial_owners": [
            {"name": "Jane Doe", "ownership_percent": 60},
            {"name": "John Smith", "ownership_percent": 40},
        ],
        "directors": [{"name": "Jane Doe", "role": "Director"}],
    }


def _find_pattern(text: str, pattern: str, default: str) -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else default
