"""Agent registry and package discovery."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

from agent_runtime.base import BaseAgent
from agent_runtime.exceptions import AgentNotFoundError

if TYPE_CHECKING:
    from types import ModuleType


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, type[BaseAgent]] = {}

    def register(self, agent_cls: type[BaseAgent], *, replace: bool = False) -> type[BaseAgent]:
        name = agent_cls.agent_name
        if name in self._agents and not replace:
            raise ValueError(f"Agent '{name}' is already registered")
        self._agents[name] = agent_cls
        return agent_cls

    def get(self, name: str) -> type[BaseAgent]:
        if name not in self._agents:
            raise AgentNotFoundError(f"Agent '{name}' not found in registry")
        return self._agents[name]

    def create(self, name: str) -> BaseAgent:
        return self.get(name)()

    def list_agents(self) -> list[str]:
        return sorted(self._agents)

    def __len__(self) -> int:
        return len(self._agents)


def register(registry: AgentRegistry | None = None, *, replace: bool = False):
    """Decorator to register a concrete agent class."""

    def decorator(agent_cls: type[BaseAgent]) -> type[BaseAgent]:
        target = registry if registry is not None else default_registry
        target.register(agent_cls, replace=replace)
        return agent_cls

    return decorator


default_registry = AgentRegistry()


def _register_module_agents(module: ModuleType, registry: AgentRegistry) -> list[str]:
    registered: list[str] = []
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and issubclass(attr, BaseAgent)
            and attr is not BaseAgent
            and "agent_name" in attr.__dict__
        ):
            registry.register(attr, replace=True)
            registered.append(attr.agent_name)
    return registered


def discover_agents(root: str | Path, registry: AgentRegistry | None = None) -> list[str]:
    """Discover agent packages under agent_library and register concrete agents."""

    target = registry if registry is not None else default_registry
    root_path = Path(root)
    if not root_path.is_dir():
        return []

    registered: list[str] = []
    package_root = root_path.parent
    package_prefix = root_path.name

    import sys

    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

    module_names: list[str] = []
    for module_info in pkgutil.iter_modules([str(root_path)]):
        if not module_info.name.startswith("_"):
            module_names.append(module_info.name)

    if not module_names:
        module_names = [
            child.name
            for child in sorted(root_path.iterdir())
            if child.is_dir() and not child.name.startswith("_") and (child / "agent.py").exists()
        ]

    for name in module_names:
        module = importlib.import_module(f"{package_prefix}.{name}.agent")
        registered.extend(_register_module_agents(module, target))
    return sorted(set(registered))
