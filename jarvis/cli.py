from __future__ import annotations

from dataclasses import asdict

import sys

import typer
from rich import print

from jarvis.agent.runtime import build_runtime

cli = typer.Typer(help="JARVIS local assistant CLI", invoke_without_command=True)


def execute(command: str) -> None:
    """Execute one natural-language command."""
    runtime = build_runtime()
    plan, results = runtime.handle_text(command)
    print(f"[bold]Plan:[/bold] {plan.summary}")
    for step in plan.steps:
        print({"tool": step.tool, "args": step.args, "safety": step.safety.value})
    print("[bold]Results:[/bold]")
    for result in results:
        print(asdict(result))


@cli.callback()
def callback(ctx: typer.Context, command: list[str] | None = typer.Argument(None)) -> None:
    if ctx.invoked_subcommand is None and command:
        execute(" ".join(command))


@cli.command()
def run(command: str) -> None:
    execute(command)


@cli.command()
def apps() -> None:
    """List detected applications."""
    runtime = build_runtime()
    for app in runtime.apps.list():
        print(app)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "apps", "--help", "-h"}:
        execute(" ".join(sys.argv[1:]))
        return
    cli()


if __name__ == "__main__":
    main()
