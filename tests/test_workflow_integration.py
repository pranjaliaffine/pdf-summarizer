"""Integration tests for the PDF KYC summarizer workflow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_runtime.contracts import AgentInput, ExecutionContext, ServiceContainer
from agent_runtime.executor import WorkflowExecutor
from agent_runtime.registry import AgentRegistry, discover_agents
from config import get_settings
from run_workflow import run_workflow


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "workflow_manifest.json"
SAMPLE_PDF = ROOT / "samples" / "sample_kyc.pdf"


@pytest.fixture
def manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def registry() -> AgentRegistry:
    reg = AgentRegistry()
    discover_agents(ROOT / "agent_library", reg)
    return reg


def test_agent_discovery_loads_all_packages(registry: AgentRegistry, manifest: dict) -> None:
    expected_agents = {step["agent"] for step in manifest["steps"]}
    discovered = set(registry.list_agents())
    assert expected_agents.issubset(discovered)
    assert len(discovered) == 6


def test_manifest_step_count_matches_executable_nodes(manifest: dict) -> None:
    graph_nodes = manifest["graph"]["nodes"]
    assert len(manifest["steps"]) == len(graph_nodes) == 6
    step_node_ids = {step["node_id"] for step in manifest["steps"]}
    graph_node_ids = {node["id"] for node in graph_nodes}
    assert step_node_ids == graph_node_ids


@pytest.mark.asyncio
async def test_mocked_workflow_run_completes(registry: AgentRegistry, manifest: dict) -> None:
    settings = get_settings()
    context = ExecutionContext(
        services=ServiceContainer(llm_available=False),
        settings=settings,
        workflow_id=manifest["workflow_id"],
        dry_run=True,
    )
    executor = WorkflowExecutor(registry)
    sample_input = dict(manifest["sampleInput"])
    result = await executor.run(
        manifest["workflow_id"],
        manifest["steps"],
        AgentInput(data=sample_input),
        context,
    )
    assert result.ok
    assert result.status.value == "success"
    assert result.failed_step is None
    assert "case_package" in result.state
    assert result.state["publication_status"] == "published"


@pytest.mark.asyncio
async def test_cli_run_with_sample_input() -> None:
    assert SAMPLE_PDF.exists()
    exit_code = await run_workflow(MANIFEST_PATH, dict(json.loads(MANIFEST_PATH.read_text())["sampleInput"]), dry_run=True)
    assert exit_code == 0
    result_path = ROOT / "output" / "workflow_result.json"
    assert result_path.exists()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["status"] == "success"
