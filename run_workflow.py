#!/usr/bin/env python3
"""CLI entry point to execute the PDF KYC summarizer workflow."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from config import get_settings
from agent_runtime.contracts import AgentInput, ExecutionContext, ServiceContainer
from agent_runtime.executor import WorkflowExecutor
from agent_runtime.registry import AgentRegistry, discover_agents


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_input(args: argparse.Namespace, manifest: dict) -> dict:
    if args.input:
        raw = args.input
        if Path(raw).exists():
            return json.loads(Path(raw).read_text(encoding="utf-8"))
        return json.loads(raw)

    sample = dict(manifest.get("sampleInput", {}))
    if args.pdf:
        sample["pdf_path"] = args.pdf
        sample.setdefault("filename", Path(args.pdf).name)
    return sample


async def run_workflow(
    manifest_path: Path,
    initial_data: dict,
    *,
    dry_run: bool = False,
) -> int:
    manifest = _load_manifest(manifest_path)
    settings = get_settings()

    registry = AgentRegistry()
    library_root = manifest.get("agent_library_root", settings.agent_library_root)
    discovered = discover_agents(library_root, registry)
    if not discovered:
        print("No agents discovered", file=sys.stderr)
        return 1

    services = ServiceContainer(llm_available=settings.llm_available)
    context = ExecutionContext(
        services=services,
        settings=settings,
        workflow_id=manifest.get("workflow_id", "workflow"),
        dry_run=dry_run or settings.dry_run,
    )

    executor = WorkflowExecutor(registry)
    result = await executor.run(
        manifest.get("workflow_id", "workflow"),
        manifest.get("steps", []),
        AgentInput(data=initial_data),
        context,
    )

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "workflow_result.json"
    output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    print(json.dumps({"status": result.status.value, "failed_step": result.failed_step}, indent=2))
    print(f"Full result written to {output_path}")
    return 0 if result.ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the PDF KYC summarizer workflow")
    parser.add_argument("--manifest", default=None, help="Path to workflow_manifest.json")
    parser.add_argument("--input", help="Inline JSON or path to JSON input file")
    parser.add_argument("--pdf", help="Path to uploaded PDF (overrides sampleInput.pdf_path)")
    parser.add_argument("--dry-run", action="store_true", help="Use mock LLM/rule-based paths")
    args = parser.parse_args()

    settings = get_settings()
    manifest_path = Path(args.manifest or settings.workflow_manifest_path)
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = _load_manifest(manifest_path)
    initial_data = _resolve_input(args, manifest)
    pdf_path = Path(initial_data.get("pdf_path", ""))
    if not pdf_path.exists():
        print(f"Sample PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    return asyncio.run(run_workflow(manifest_path, initial_data, dry_run=args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
