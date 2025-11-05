"""Registry for asset pipeline steps."""

import importlib
import pkgutil
from collections.abc import Callable
from pathlib import Path

from .base import PipelineStep

_REGISTRY: dict[str, type[PipelineStep]] = {}
_DISCOVERED = False


def register_step(
    name: str, order: int = 100
) -> Callable[[type[PipelineStep]], type[PipelineStep]]:
    """Decorator to register a pipeline step."""

    def _wrap(cls: type[PipelineStep]) -> type[PipelineStep]:
        cls.order = order
        _REGISTRY[name] = cls
        return cls

    return _wrap


def _auto_discover() -> None:
    """Auto-discover all pipeline steps in this package."""
    global _DISCOVERED  # noqa: PLW0603
    if _DISCOVERED:
        return
    pkg_dir = Path(__file__).parent
    for _, modname, _ in pkgutil.iter_modules([str(pkg_dir)]):
        if modname in {"base", "registry", "__init__"}:
            continue
        importlib.import_module(f"apps.core.assets.{modname}")
    _DISCOVERED = True


def get_steps() -> list[tuple[str, type[PipelineStep]]]:
    """Get all registered pipeline steps, auto-discovering them if needed."""
    _auto_discover()
    return sorted(_REGISTRY.items(), key=lambda kv: kv[1].order)
