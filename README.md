# r4c

`r4c` is a small `uv`-managed CLI for managing RDF4J and GraphDB repository namespaces through the RDF4J REST API.

## Install

Install directly from the public GitHub repository with `uv`:

```sh
uv tool install "r4c @ git+https://github.com/rpietzsch/r4c.git@develop"
```

Then run:

```sh
r4c --help
```

If the command is not on your `PATH`, run:

```sh
uv tool update-shell
```

To upgrade an existing install:

```sh
uv tool upgrade r4c
```

## Usage

```sh
uv run r4c --repository myrepo list
uv run r4c --repository myrepo add schema https://schema.org/
uv run r4c --repository myrepo export namespaces.ttl
uv run r4c --repository myrepo import namespaces.ttl --replace
uv run r4c --repository myrepo delete schema
uv run r4c --repository myrepo delete --all
uv run r4c --repository myrepo prune --dry
uv run r4c --repository myrepo prune --exclude rdf,rdfs,owl,xsd --keep-defaults
uv run r4c --repository myrepo defaults graphdb
```

The default server URL is GraphDB's usual local URL, `http://localhost:7200`. For RDF4J Server, pass the server root:

```sh
uv run r4c --server http://localhost:8080/rdf4j-server --repository myrepo list
```

You can also use environment variables:

```sh
export RDF4J_SERVER_URL=http://localhost:7200
export RDF4J_REPOSITORY=myrepo
export RDF4J_USERNAME=admin
export RDF4J_PASSWORD=root
uv run r4c list
```

Import/export uses a Turtle prefix section only. Exports use RDF 1.1-style directives:

```turtle
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://schema.org/>
```

Imports accept the same form, and also tolerate legacy `@prefix ... .` declarations. Use `-` as the import/export path for stdin/stdout.

`prune` removes namespace declarations whose namespace IRI is not used by stored IRIs in subjects, predicates, objects, literal datatypes, or named graph IRIs. Use `--dry` to preview, `--exclude PREFIX` to keep specific prefixes, and `--keep-defaults` to retain prefixes from the built-in default profiles even if they are unused.

## Defaults

`r4c defaults graphdb` installs the predefined GraphDB repository prefixes from the GraphDB 11.3 documentation.

Plain RDF4J Server does not appear to document a GraphDB-style repository namespace bootstrap set. RDF4J does expose repository namespace management via both the Java API and REST API, and RDF4J Rio defines `Namespaces.DEFAULT_RDF4J` for parser defaults. `r4c defaults rdf4j` applies that Rio/parser set when you explicitly want a broad RDF4J-provided prefix baseline.

Sources:

- GraphDB predefined repository namespaces: https://graphdb.ontotext.com/documentation/11.3/configuring-a-repository.html#namespaces-defined-for-the-repository
- RDF4J REST namespace endpoints: https://rdf4j.org/documentation/reference/rest-api/
- RDF4J `RepositoryConnection` namespace methods: https://rdf4j.org/javadoc/latest/org/eclipse/rdf4j/repository/RepositoryConnection.html
- RDF4J `Namespaces.DEFAULT_RDF4J`: https://rdf4j.org/javadoc/latest/org/eclipse/rdf4j/model/util/Namespaces.html
