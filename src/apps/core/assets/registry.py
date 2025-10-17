import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Tuple, Type
from .base import PipelineStep

_REGISTRY: Dict[str, Type[PipelineStep]] = {}
_DISCOVERED = False

def register_step(name: str, order: int = 100):
    def _wrap(cls: Type[PipelineStep]) -> Type[PipelineStep]:
        cls.order = order
        _REGISTRY[name] = cls
        return cls
    return _wrap

def _auto_discover():
    global _DISCOVERED
    if _DISCOVERED:
        return
    pkg_dir = Path(__file__).parent
    for _, modname, _ in pkgutil.iter_modules([str(pkg_dir)]):
        if modname in {"base", "registry", "__init__"}:
            continue
        importlib.import_module(f"apps.core.assets.{modname}")
    _DISCOVERED = True

def get_steps() -> List[Tuple[str, Type[PipelineStep]]]:
    _auto_discover()
    return sorted(_REGISTRY.items(), key=lambda kv: kv[1].order)
