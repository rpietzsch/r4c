from __future__ import annotations

import base64

import responses
from click.testing import CliRunner

from r4c.cli import main


def test_subcommand_help_does_not_require_repository() -> None:
    result = CliRunner().invoke(main, ["export", "--help"])

    assert result.exit_code == 0
    assert "Export repository namespaces as Turtle prefix declarations." in result.output


def test_help_shows_auth_envvars() -> None:
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "RDF4J_USERNAME" in result.output
    assert "RDF4J_PASSWORD" in result.output


@responses.activate
def test_add_sets_namespace() -> None:
    responses.put("http://example.test/repositories/test/namespaces/schema", status=204)

    result = CliRunner().invoke(
        main,
        [
            "--server",
            "http://example.test",
            "--repository",
            "test",
            "add",
            "schema",
            "https://schema.org/",
        ],
    )

    assert result.exit_code == 0
    assert "Set schema -> https://schema.org/" in result.output


@responses.activate
def test_auth_envvars_set_basic_auth() -> None:
    responses.put("http://example.test/repositories/test/namespaces/schema", status=204)

    result = CliRunner().invoke(
        main,
        [
            "--server",
            "http://example.test",
            "--repository",
            "test",
            "add",
            "schema",
            "https://schema.org/",
        ],
        env={"RDF4J_USERNAME": "admin", "RDF4J_PASSWORD": "root"},
    )

    encoded = base64.b64encode(b"admin:root").decode("ascii")
    assert result.exit_code == 0
    assert responses.calls[0].request.headers["Authorization"] == f"Basic {encoded}"


@responses.activate
def test_delete_all_clears_namespaces() -> None:
    responses.delete("http://example.test/repositories/test/namespaces", status=204)

    result = CliRunner().invoke(
        main,
        ["--server", "http://example.test", "--repository", "test", "delete", "--all"],
    )

    assert result.exit_code == 0
    assert "Deleted all namespaces" in result.output


@responses.activate
def test_import_replace_clears_and_sets_namespaces(tmp_path) -> None:
    path = tmp_path / "namespaces.ttl"
    path.write_text("PREFIX schema: <https://schema.org/>\n", encoding="utf-8")
    responses.delete("http://example.test/repositories/test/namespaces", status=204)
    responses.put("http://example.test/repositories/test/namespaces/schema", status=204)

    result = CliRunner().invoke(
        main,
        [
            "--server",
            "http://example.test",
            "--repository",
            "test",
            "import",
            str(path),
            "--replace",
        ],
    )

    assert result.exit_code == 0
    assert "Imported 1 namespaces" in result.output
    assert len(responses.calls) == 2


@responses.activate
def test_defaults_graphdb_populates_known_prefixes() -> None:
    responses.put("http://example.test/repositories/test/namespaces/gn", status=204)
    responses.put("http://example.test/repositories/test/namespaces/owl", status=204)
    responses.put("http://example.test/repositories/test/namespaces/path", status=204)
    responses.put("http://example.test/repositories/test/namespaces/rdf", status=204)
    responses.put("http://example.test/repositories/test/namespaces/rdfs", status=204)
    responses.put("http://example.test/repositories/test/namespaces/wgs", status=204)
    responses.put("http://example.test/repositories/test/namespaces/xsd", status=204)
    responses.put("http://example.test/repositories/test/namespaces/fn", status=204)
    responses.put("http://example.test/repositories/test/namespaces/ofn", status=204)
    responses.put("http://example.test/repositories/test/namespaces/spif", status=204)
    responses.put("http://example.test/repositories/test/namespaces/afn", status=204)
    responses.put("http://example.test/repositories/test/namespaces/list", status=204)
    responses.put("http://example.test/repositories/test/namespaces/agg", status=204)
    responses.put("http://example.test/repositories/test/namespaces/apf", status=204)
    responses.put("http://example.test/repositories/test/namespaces/geof", status=204)
    responses.put("http://example.test/repositories/test/namespaces/geoext", status=204)
    responses.put("http://example.test/repositories/test/namespaces/omgeo", status=204)
    responses.put("http://example.test/repositories/test/namespaces/math", status=204)
    responses.put("http://example.test/repositories/test/namespaces/map", status=204)
    responses.put("http://example.test/repositories/test/namespaces/array", status=204)
    responses.put("http://example.test/repositories/test/namespaces/rep", status=204)
    responses.put("http://example.test/repositories/test/namespaces/sr", status=204)
    responses.put("http://example.test/repositories/test/namespaces/sail", status=204)
    responses.put("http://example.test/repositories/test/namespaces/graphdb", status=204)

    result = CliRunner().invoke(
        main,
        ["--server", "http://example.test", "--repository", "test", "defaults", "graphdb"],
    )

    assert result.exit_code == 0
    assert "Populated 24 namespaces" in result.output
    list_call = next(call for call in responses.calls if call.request.url.endswith("/list"))
    assert list_call.request.body == "http://jena.apache.org/ARQ/list#"
