"""CLI entrypoint. Run `prd "one-line idea"` after `pip install -e .`."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .pipeline import generate_prd

console = Console()


@click.command()
@click.argument("idea", nargs=-1, required=True)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Write PRD markdown to this file.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of markdown.")
def main(idea: tuple[str, ...], output: Path | None, as_json: bool) -> None:
    """Turn a one-line product idea into a structured PRD."""
    one_liner = " ".join(idea).strip()
    if not one_liner:
        console.print("[red]Provide a one-line idea.[/red]")
        sys.exit(2)

    console.print(Panel(one_liner, title="Idea", border_style="cyan"))
    with console.status("[bold cyan]Generating PRD…[/]"):
        prd = generate_prd(one_liner)

    if as_json:
        out = prd.model_dump_json(indent=2)
    else:
        out = prd.to_markdown()

    if output:
        output.write_text(out, encoding="utf-8")
        console.print(f"[green]Wrote[/] {output}")
    else:
        if as_json:
            console.print(out)
        else:
            console.print(Markdown(out))


if __name__ == "__main__":
    main()
