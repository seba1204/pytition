import importlib
import pkgutil
from pathlib import Path
from typing import Type, Dict
from .base import Vendor

_REGISTRY: Dict[str, Type[Vendor]] = {}
_DISCOVERED = False

def _auto_discover():
    """Import all modules in this package to trigger @register decorators."""
    global _DISCOVERED
    if _DISCOVERED:
        return
    pkg_dir = Path(__file__).parent
    for _, modname, _ in pkgutil.iter_modules([str(pkg_dir)]):
        if modname not in ("base", "registry"):
            importlib.import_module(f"{__package__}.{modname}")
    _DISCOVERED = True

def register(name: str):
    def _wrap(cls: Type[Vendor]) -> Type[Vendor]:
        _REGISTRY[name.lower()] = cls
        return cls
    return _wrap

def get_vendor_class(name: str) -> Type[Vendor]:
    _auto_discover()
    key = name.lower()
    if key not in _REGISTRY:
        raise SystemExit(f"Vendor inconnu '{name}'. Disponibles: {', '.join(sorted(_REGISTRY))}")
    return _REGISTRY[key]
