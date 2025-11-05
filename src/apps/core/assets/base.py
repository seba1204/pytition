"""Base classes for asset pipeline steps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Context:
    """
    Context passed to all pipeline steps.

    Attributes:
    -----------
        project_dir: Path to the root of the project.
        assets_dir: Path to the assets directory.
        static_root: Path to the static root directory.
        settings: Django settings module.
        stdout: Standard output stream.
        stderr: Standard error stream.
        verbosity: Verbosity level for logging.
    """

    assets_dir: Path
    static_root: Path
    settings: Any
    stdout: Any
    stderr: Any
    verbosity: int = 1


class PipelineStep:
    """
    Base for all pipeline steps.

    Implements `run(self, ctx: Context) -> None`.

    Attributes:
    -----------
        name: Name of the step.
        order: Order of execution (lower runs first).
    """

    order: int = 100

    def __init__(self, name: str):
        self.name = name

    def log(self, ctx: Context, msg: str, level: int = 1) -> None:
        """Log a message if verbosity level is sufficient."""
        if ctx.verbosity >= level:
            ctx.stdout.write(f"[{self.name}] {msg}")

    def run(self, ctx: Context) -> None:
        """Run the pipeline step."""
        raise NotImplementedError
