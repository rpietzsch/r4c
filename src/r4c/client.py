from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote
from xml.etree import ElementTree

import requests


class NamespaceClientError(RuntimeError):
    """Raised when the RDF4J namespace API cannot complete a request."""


@dataclass
class NamespaceClient:
    repository_url: str
    username: str | None = None
    password: str | None = None
    token: str | None = None
    timeout: float = 30.0
    verify: bool = True
    session: requests.Session = field(default_factory=requests.Session)

    def list(self) -> dict[str, str]:
        response = self._request(
            "GET",
            "namespaces",
            headers={
                "Accept": "application/sparql-results+json, application/sparql-results+xml;q=0.9"
            },
        )
        return _parse_namespace_listing(response)

    def get(self, prefix: str) -> str | None:
        response = self._request(
            "GET",
            "namespaces",
            prefix,
            headers={"Accept": "text/plain"},
            allowed_statuses={200, 404},
        )
        if response.status_code == 404:
            return None
        return response.text.strip()

    def set(self, prefix: str, namespace: str) -> None:
        self._request(
            "PUT",
            "namespaces",
            prefix,
            data=namespace,
            headers={"Content-Type": "text/plain"},
            allowed_statuses={200, 204},
        )

    def delete(self, prefix: str) -> None:
        self._request(
            "DELETE",
            "namespaces",
            prefix,
            allowed_statuses={200, 204, 404},
        )

    def clear(self) -> None:
        self._request(
            "DELETE",
            "namespaces",
            allowed_statuses={200, 204},
        )

    def _request(
        self,
        method: str,
        *parts: str,
        allowed_statuses: set[int] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        allowed_statuses = allowed_statuses or {200}
        headers = dict(kwargs.pop("headers", {}) or {})
        if self.token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {self.token}"
        auth = None
        if self.username is not None:
            auth = (self.username, self.password or "")

        try:
            response = self.session.request(
                method,
                self._url(*parts),
                headers=headers,
                auth=auth,
                timeout=self.timeout,
                verify=self.verify,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise NamespaceClientError(str(exc)) from exc

        if response.status_code not in allowed_statuses:
            message = response.text.strip() or response.reason
            raise NamespaceClientError(
                f"{method} {response.url} failed with HTTP {response.status_code}: {message}"
            )
        return response

    def _url(self, *parts: str) -> str:
        encoded = "/".join(quote(part, safe="") for part in parts)
        return f"{self.repository_url.rstrip('/')}/{encoded}"


def repository_url(server_url: str, repository_id: str) -> str:
    return f"{server_url.rstrip('/')}/repositories/{quote(repository_id, safe='')}"


def _parse_namespace_listing(response: requests.Response) -> dict[str, str]:
    text = response.text.strip()
    if not text:
        return {}

    content_type = response.headers.get("Content-Type", "")
    if "json" in content_type or text.startswith("{"):
        return _parse_sparql_json(text)

    return _parse_sparql_xml(text)


def _parse_sparql_json(text: str) -> dict[str, str]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise NamespaceClientError(f"Invalid SPARQL JSON result: {exc}") from exc

    namespaces: dict[str, str] = {}
    for binding in payload.get("results", {}).get("bindings", []):
        prefix = binding.get("prefix", {}).get("value")
        namespace = binding.get("namespace", {}).get("value")
        if prefix is not None and namespace is not None:
            namespaces[prefix] = namespace
    return namespaces


def _parse_sparql_xml(text: str) -> dict[str, str]:
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        raise NamespaceClientError(f"Invalid SPARQL XML result: {exc}") from exc

    namespaces: dict[str, str] = {}
    xml_ns = {"sparql": "http://www.w3.org/2005/sparql-results#"}
    results = root.findall(".//sparql:result", xml_ns)
    if not results:
        results = root.findall(".//result")
    for result in results:
        values: dict[str, str] = {}
        bindings = result.findall("sparql:binding", xml_ns)
        if not bindings:
            bindings = result.findall("binding")
        for binding in bindings:
            name = binding.attrib.get("name")
            literal = binding.find("sparql:literal", xml_ns)
            if literal is None:
                literal = binding.find("literal")
            if name and literal is not None and literal.text is not None:
                values[name] = literal.text
        prefix = values.get("prefix")
        namespace = values.get("namespace")
        if prefix is not None and namespace is not None:
            namespaces[prefix] = namespace
    return namespaces
