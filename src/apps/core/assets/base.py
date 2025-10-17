from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class Context:
    assets_dir: Path
    static_root: Path
    settings: Any
    stdout: Any  # file-like
    stderr: Any  # file-like
    verbosity: int = 1

class PipelineStep:
    """
    Base de toutes les étapes du pipeline.
    Implémente `run(self, ctx: Context) -> None`.
    """
    order: int = 100  # ordre par défaut si non spécifié

    def __init__(self, name: str):
        self.name = name

    def log(self, ctx: Context, msg: str, level: int = 1):
        if ctx.verbosity >= level:
            ctx.stdout.write(f"[{self.name}] {msg}")

    def run(self, ctx: Context) -> None:
        raise NotImplementedError
