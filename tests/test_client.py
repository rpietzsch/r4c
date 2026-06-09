from __future__ import annotations

import responses

from r4c.client import NamespaceClient, repository_url


def test_repository_url_encodes_repository_id() -> None:
    assert (
        repository_url("http://example.test/rdf4j-server/", "repo/id")
        == "http://example.test/rdf4j-server/repositories/repo%2Fid"
    )


@responses.activate
def test_list_parses_sparql_json() -> None:
    responses.get(
        "http://example.test/repositories/test/namespaces",
        json={
            "head": {"vars": ["prefix", "namespace"]},
            "results": {
                "bindings": [
                    {
                        "prefix": {"type": "literal", "value": "rdf"},
                        "namespace": {
                            "type": "literal",
                            "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        },
                    }
                ]
            },
        },
    )

    client = NamespaceClient("http://example.test/repositories/test")

    assert client.list() == {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}


@responses.activate
def test_list_parses_sparql_xml() -> None:
    responses.get(
        "http://example.test/repositories/test/namespaces",
        body="""<?xml version="1.0" encoding="UTF-8"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#">
  <head>
    <variable name="prefix"/>
    <variable name="namespace"/>
  </head>
  <results>
    <result>
      <binding name="prefix"><literal>schema</literal></binding>
      <binding name="namespace"><literal>https://schema.org/</literal></binding>
    </result>
  </results>
</sparql>
""",
        content_type="application/sparql-results+xml",
    )

    client = NamespaceClient("http://example.test/repositories/test")

    assert client.list() == {"schema": "https://schema.org/"}


@responses.activate
def test_set_and_delete_prefix() -> None:
    responses.put("http://example.test/repositories/test/namespaces/schema", status=204)
    responses.delete("http://example.test/repositories/test/namespaces/schema", status=204)

    client = NamespaceClient("http://example.test/repositories/test")

    client.set("schema", "https://schema.org/")
    client.delete("schema")

    assert responses.calls[0].request.body == "https://schema.org/"
    assert responses.calls[0].request.headers["Content-Type"] == "text/plain"
