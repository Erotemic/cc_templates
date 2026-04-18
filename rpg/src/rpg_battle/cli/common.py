from __future__ import annotations

"""Shared helpers for interactive classroom CLIs."""

import os
from pathlib import Path
from typing import Iterable, Sequence, TypeVar

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

T = TypeVar("T")

console = Console()


def configure_headless_pygame() -> None:
    """Configure pygame to run without opening a real window or audio device."""

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def default_output_path(filename: str) -> Path:
    """Return an output path rooted in the current working directory."""

    return Path.cwd() / filename


def ensure_output_path(path: str | Path) -> Path:
    """Create parent directories for an output path and return its absolute form."""

    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def choose_from_registry(
    title: str,
    options: Sequence[str],
    *,
    description: str | None = None,
    default: str | None = None,
) -> str:
    """Show a rich table of options and prompt the user to pick one."""

    if not options:
        raise ValueError(f"No options available for {title}")

    if len(options) == 1:
        return options[0]

    table = Table(title=title)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("id", style="magenta")
    if description:
        table.caption = description
    for index, option in enumerate(options, start=1):
        table.add_row(str(index), option)
    console.print(table)

    prompt_default = str(options.index(default) + 1) if default in options else "1"
    while True:
        response = Prompt.ask(
            f"Choose {title.lower()} by number",
            default=prompt_default,
            console=console,
        )
        if response.isdigit():
            selected = int(response) - 1
            if 0 <= selected < len(options):
                return options[selected]
        console.print("[red]Please enter a valid menu number.[/red]")


def choose_yes_no(prompt: str, *, default: bool = False) -> bool:
    """Prompt for a boolean choice using rich."""

    return Confirm.ask(prompt, default=default, console=console)


def render_registry_table(title: str, rows: Iterable[tuple[str, str]]) -> None:
    """Print a simple id/summary table for inspectable registries."""

    table = Table(title=title)
    table.add_column("id", style="magenta")
    table.add_column("summary", style="white")
    for key, summary in rows:
        table.add_row(key, summary)
    console.print(table)
