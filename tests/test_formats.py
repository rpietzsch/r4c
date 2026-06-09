from __future__ import annotations

from r4c.formats import format_namespaces, parse_namespaces


def test_turtle_round_trip() -> None:
    namespaces = {"schema": "https://schema.org/", "rdf": "http://example.test/rdf#"}

    assert parse_namespaces(format_namespaces(namespaces)) == namespaces


def test_format_uses_rdf11_prefix_style() -> None:
    assert format_namespaces({"schema": "https://schema.org/"}) == (
        "PREFIX schema: <https://schema.org/>\n"
    )


def test_parse_legacy_turtle_prefixes() -> None:
    text = """
    @prefix schema: <https://schema.org/> .
    @prefix : <http://example.test/default#> .
    """

    assert parse_namespaces(text) == {
        "schema": "https://schema.org/",
        "": "http://example.test/default#",
    }


def test_parse_sparql_prefixes() -> None:
    text = """
    PREFIX schema: <https://schema.org/>
    PREFIX : <http://example.test/default#>
    """

    assert parse_namespaces(text) == {
        "schema": "https://schema.org/",
        "": "http://example.test/default#",
    }
