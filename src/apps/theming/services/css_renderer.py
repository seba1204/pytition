"""CSS rendering services for theming."""

from collections.abc import Mapping
from typing import Protocol


class HasTokens(Protocol):
    """Narrow contract required by the renderer."""

    tokens_css: Mapping[str, Mapping[str, str]]


def render_theme_tokens(theme: HasTokens) -> str:
    """
    Render the CSS for a given theme's tokens.

    Parameters
    ----------
    theme : Theme
        The Theme instance to render tokens for.

    Returns
    -------
    str
        The rendered CSS string.
    """
    chunks: list[str] = []
    for scope, tokens in theme.tokens_css.items():
        if not tokens:
            continue
        decls = [f"{k}: {v};" for k, v in tokens.items()]
        chunks.append(f"{scope} {{\n  " + "\n  ".join(decls) + "\n}")
    return "\n\n".join(chunks)
