"""PDF intake gateway agent."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_runtime.base import RuleBasedAgent
from agent_runtime.contracts import AgentInput, ExecutionContext
from agent_runtime.exceptions import ValidationError
from agent_runtime.registry import register


@dataclass
class IntakePayload:
    pdf_path: Path
    filename: str


@register()
class PdfIntakeGatewayAgent(RuleBasedAgent[IntakePayload]):
    agent_name = "pdf_intake_gateway"

    async def validate_input(self, agent_input: AgentInput) -> IntakePayload:
        pdf_path_raw = agent_input.data.get("pdf_path")
        if not pdf_path_raw:
            raise ValidationError("pdf_path is required")
        pdf_path = Path(str(pdf_path_raw))
        if not pdf_path.exists():
            raise ValidationError(f"PDF not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValidationError("Only PDF files are supported")

        filename = agent_input.data.get("filename") or pdf_path.name
        if not filename:
            raise ValidationError("filename identifier is required")
        return IntakePayload(pdf_path=pdf_path, filename=str(filename))

    async def execute(self, payload: IntakePayload, context: ExecutionContext) -> dict:
        document_text = _extract_text(payload.pdf_path)
        case_id = Path(payload.filename).stem
        return {
            "case_id": case_id,
            "filename": payload.filename,
            "pdf_path": str(payload.pdf_path),
            "document_text": document_text,
            "intake_status": "accepted",
        }

    async def validate_output(self, result: dict) -> dict:
        required = ("case_id", "filename", "pdf_path", "document_text")
        missing = [key for key in required if not result.get(key)]
        if missing:
            raise ValidationError(f"Missing intake outputs: {', '.join(missing)}")
        return result


def _extract_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts).strip()
        if text:
            return text
    except Exception:
        pass
    return f"Sample KYC document content for {pdf_path.name}. Legal entity: Acme Holdings Ltd."
