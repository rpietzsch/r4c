from __future__ import annotations

from pathlib import Path

import click

from .client import NamespaceClient, NamespaceClientError, repository_url
from .defaults import DEFAULT_PREFIXES, DEFAULT_PROFILES, PROFILE_NOTES
from .formats import LIST_FORMATS, format_namespaces, parse_namespaces


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option(
    "--server",
    envvar="RDF4J_SERVER_URL",
    default="http://localhost:7200",
    show_default=True,
    help="RDF4J or GraphDB server root URL.",
)
@click.option(
    "--repository",
    "-r",
    envvar="RDF4J_REPOSITORY",
    help="Repository ID. Not needed when --repository-url is set.",
)
@click.option(
    "--repository-url",
    envvar="RDF4J_REPOSITORY_URL",
    help="Full repository URL, for example http://host/repositories/myrepo.",
)
@click.option(
    "--username",
    "-u",
    envvar="RDF4J_USERNAME",
    show_envvar=True,
    help="HTTP basic auth username.",
)
@click.option(
    "--password",
    envvar="RDF4J_PASSWORD",
    show_envvar=True,
    help="HTTP basic auth password.",
)
@click.option("--token", envvar="RDF4J_TOKEN", help="Bearer token for Authorization.")
@click.option(
    "--timeout",
    envvar="RDF4J_TIMEOUT",
    default=30.0,
    show_default=True,
    type=click.FloatRange(min=0.1),
    help="HTTP request timeout in seconds.",
)
@click.option(
    "--verify/--no-verify",
    default=True,
    show_default=True,
    help="Verify TLS certificates.",
)
@click.version_option()
@click.pass_context
def main(
    ctx: click.Context,
    server: str,
    repository: str | None,
    repository_url: str | None,
    username: str | None,
    password: str | None,
    token: str | None,
    timeout: float,
    verify: bool,
) -> None:
    """Manage RDF4J and GraphDB repository namespaces."""
    if ctx.resilient_parsing:
        return
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()

    if repository_url is None:
        if repository is None:
            ctx.obj = None
            return
        repository_url = globals()["repository_url"](server, repository)

    ctx.obj = NamespaceClient(
        repository_url=repository_url,
        username=username,
        password=password,
        token=token,
        timeout=timeout,
        verify=verify,
    )


@main.command("list")
@click.option(
    "--format",
    "format_",
    type=click.Choice(LIST_FORMATS),
    default="table",
    show_default=True,
    help="Output format.",
)
@click.pass_obj
def list_namespaces(client: NamespaceClient | None, format_: str) -> None:
    """List repository namespaces."""
    client = _require_client(client)
    namespaces = _call(client.list)
    if format_ == "table":
        _echo_table(namespaces)
    else:
        click.echo(format_namespaces(namespaces), nl=False)


@main.command("export")
@click.argument("path", required=False, type=click.Path(dir_okay=False, path_type=Path))
@click.pass_obj
def export_namespaces(client: NamespaceClient | None, path: Path | None) -> None:
    """Export repository namespaces as Turtle prefix declarations."""
    client = _require_client(client)
    output = format_namespaces(_call(client.list))
    if path is None or str(path) == "-":
        click.echo(output, nl=False)
    else:
        path.write_text(output, encoding="utf-8")
        click.echo(f"Exported namespaces to {path}")


@main.command("import")
@click.argument("path", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--replace", is_flag=True, help="Clear all existing namespaces before import.")
@click.option("--dry-run", is_flag=True, help="Parse and report without changing the repository.")
@click.pass_obj
def import_namespaces(
    client: NamespaceClient | None,
    path: Path,
    replace: bool,
    dry_run: bool,
) -> None:
    """Import repository namespaces from Turtle prefix declarations."""
    client = _require_client(client)
    text = click.get_text_stream("stdin").read() if str(path) == "-" else path.read_text("utf-8")
    try:
        namespaces = parse_namespaces(text)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    if dry_run:
        click.echo(f"Parsed {len(namespaces)} namespaces from {path}")
        return

    if replace:
        _call(client.clear)
    for prefix, namespace in namespaces.items():
        _call(client.set, prefix, namespace)
    click.echo(f"Imported {len(namespaces)} namespaces")


@main.command("add")
@click.argument("prefix")
@click.argument("namespace")
@click.pass_obj
def add_namespace(client: NamespaceClient | None, prefix: str, namespace: str) -> None:
    """Add or update one namespace."""
    client = _require_client(client)
    _call(client.set, prefix, namespace)
    click.echo(f"Set {prefix or '(default)'} -> {namespace}")


@main.command("delete")
@click.argument("prefix", required=False)
@click.option("--all", "delete_all", is_flag=True, help="Delete all repository namespaces.")
@click.pass_obj
def delete_namespace(
    client: NamespaceClient | None, prefix: str | None, delete_all: bool
) -> None:
    """Delete one namespace, or all namespaces with --all."""
    client = _require_client(client)
    if delete_all and prefix is not None:
        raise click.UsageError("Use either PREFIX or --all, not both.")
    if not delete_all and prefix is None:
        raise click.UsageError("Provide PREFIX or use --all.")

    if delete_all:
        _call(client.clear)
        click.echo("Deleted all namespaces")
        return

    assert prefix is not None
    _call(client.delete, prefix)
    click.echo(f"Deleted {prefix or '(default)'}")


@main.command("prune")
@click.option("--dry", is_flag=True, help="Report unused namespaces without deleting them.")
@click.option(
    "--exclude",
    multiple=True,
    metavar="PREFIX",
    help="Keep a prefix even if unused. Repeat or comma-separate.",
)
@click.option(
    "--keep-defaults",
    is_flag=True,
    help="Keep prefixes from the built-in default profiles.",
)
@click.pass_obj
def prune_namespaces(
    client: NamespaceClient | None,
    dry: bool,
    exclude: tuple[str, ...],
    keep_defaults: bool,
) -> None:
    """Delete namespaces that are not used by any stored IRI."""
    client = _require_client(client)
    namespaces = _call(client.list)
    if not namespaces:
        click.echo("No namespaces found")
        return

    kept_prefixes = _parse_excluded_prefixes(exclude)
    if keep_defaults:
        kept_prefixes.update(DEFAULT_PREFIXES)

    unused: list[tuple[str, str]] = []
    kept = 0
    for prefix, namespace in sorted(namespaces.items()):
        if prefix in kept_prefixes:
            kept += 1
            continue
        if not _call(client.namespace_used, namespace):
            unused.append((prefix, namespace))

    if dry:
        _echo_prune_result("Would delete", unused, kept)
        return

    for prefix, _namespace in unused:
        _call(client.delete, prefix)
    _echo_prune_result("Deleted", unused, kept)


@main.command("defaults")
@click.argument(
    "profile",
    type=click.Choice(tuple(DEFAULT_PROFILES.keys())),
    default="graphdb",
)
@click.option("--skip-existing", is_flag=True, help="Do not overwrite existing prefixes.")
@click.option("--dry-run", is_flag=True, help="Show the defaults without changing the repository.")
@click.pass_obj
def defaults(
    client: NamespaceClient | None, profile: str, skip_existing: bool, dry_run: bool
) -> None:
    """Populate a known namespace default profile."""
    client = _require_client(client)
    namespaces = DEFAULT_PROFILES[profile]
    if dry_run:
        click.echo(format_namespaces(namespaces), nl=False)
        return

    existing = _call(client.list) if skip_existing else {}
    written = 0
    skipped = 0
    for prefix, namespace in namespaces.items():
        if prefix in existing:
            skipped += 1
            continue
        _call(client.set, prefix, namespace)
        written += 1

    note = PROFILE_NOTES.get(profile)
    if note:
        click.echo(note)
    click.echo(f"Populated {written} namespaces ({skipped} skipped)")


def _echo_table(namespaces: dict[str, str]) -> None:
    if not namespaces:
        click.echo("No namespaces found")
        return

    labels = {_display_prefix(prefix): namespace for prefix, namespace in namespaces.items()}
    width = max(len("prefix"), *(len(prefix) for prefix in labels))
    click.echo(f"{'prefix'.ljust(width)}  namespace")
    click.echo(f"{'-' * width}  {'-' * 9}")
    for prefix, namespace in sorted(labels.items()):
        click.echo(f"{prefix.ljust(width)}  {namespace}")


def _display_prefix(prefix: str) -> str:
    return prefix if prefix else "(default)"


def _parse_excluded_prefixes(exclude: tuple[str, ...]) -> set[str]:
    prefixes: set[str] = set()
    for value in exclude:
        if value == "":
            prefixes.add("")
            continue
        for raw_prefix in value.split(","):
            prefix = raw_prefix.strip()
            if prefix == "(default)":
                prefixes.add("")
            elif prefix:
                prefixes.add(prefix)
    return prefixes


def _echo_prune_result(
    action: str, namespaces: list[tuple[str, str]], kept: int
) -> None:
    noun = "namespace" if len(namespaces) == 1 else "namespaces"
    suffix = f" ({kept} kept)" if kept else ""
    click.echo(f"{action} {len(namespaces)} unused {noun}{suffix}")
    for prefix, namespace in namespaces:
        click.echo(f"{_display_prefix(prefix)} -> {namespace}")


def _require_client(client: NamespaceClient | None) -> NamespaceClient:
    if client is None:
        raise click.UsageError("Set --repository or --repository-url.")
    return client


def _call(function, *args):
    try:
        return function(*args)
    except NamespaceClientError as exc:
        raise click.ClickException(str(exc)) from exc
