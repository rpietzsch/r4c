from __future__ import annotations


GRAPHDB_DEFAULTS: dict[str, str] = {
    "gn": "http://www.geonames.org/ontology#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "path": "http://www.ontotext.com/path#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "wgs": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "fn": "http://www.w3.org/2005/xpath-functions",
    "ofn": "http://www.ontotext.com/sparql/functions/",
    "spif": "http://spinrdf.org/spif#",
    "afn": "http://jena.apache.org/ARQ/function#",
    "list": "http://jena.apache.org/ARQ/list#",
    "agg": "http://jena.apache.org/ARQ/function/aggregate#",
    "apf": "http://jena.apache.org/ARQ/property#",
    "geof": "http://www.opengis.net/def/function/geosparql/",
    "geoext": "http://rdf.useekm.com/ext#",
    "omgeo": "http://www.ontotext.com/owlim/geo#",
    "math": "http://www.w3.org/2005/xpath-functions/math",
    "map": "http://www.w3.org/2005/xpath-functions/map",
    "array": "http://www.w3.org/2005/xpath-functions/array",
    "rep": "http://www.openrdf.org/config/repository#",
    "sr": "http://www.openrdf.org/config/repository/sail#",
    "sail": "http://www.openrdf.org/config/sail#",
    "graphdb": "http://www.ontotext.com/config/graphdb#",
}


RDF4J_RDFA11_DEFAULTS: dict[str, str] = {
    "as": "https://www.w3.org/ns/activitystreams#",
    "csvw": "http://www.w3.org/ns/csvw#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dqv": "http://www.w3.org/ns/dqv#",
    "duv": "https://www.w3.org/TR/vocab-duv#",
    "grddl": "http://www.w3.org/2003/g/data-view#",
    "jsonld": "http://www.w3.org/ns/json-ld#",
    "ldp": "http://www.w3.org/ns/ldp#",
    "ma": "http://www.w3.org/ns/ma-ont#",
    "oa": "http://www.w3.org/ns/oa#",
    "odrl": "http://www.w3.org/ns/odrl/2/",
    "org": "http://www.w3.org/ns/org#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "prov": "http://www.w3.org/ns/prov#",
    "qb": "http://purl.org/linked-data/cube#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfa": "http://www.w3.org/ns/rdfa#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rif": "http://www.w3.org/2007/rif#",
    "rr": "http://www.w3.org/ns/r2rml#",
    "sd": "http://www.w3.org/ns/sparql-service-description#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "skosxl": "http://www.w3.org/2008/05/skos-xl#",
    "ssn": "http://www.w3.org/ns/ssn/",
    "sosa": "http://www.w3.org/ns/sosa/",
    "time": "http://www.w3.org/2006/time#",
    "void": "http://rdfs.org/ns/void#",
    "wdr": "http://www.w3.org/2007/05/powder#",
    "wdrs": "http://www.w3.org/2007/05/powder-s#",
    "xhv": "http://www.w3.org/1999/xhtml/vocab#",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "earl": "http://www.w3.org/ns/earl#",
    "cc": "http://creativecommons.org/ns#",
    "ctag": "http://commontag.org/ns#",
    "dc": "http://purl.org/dc/terms/",
    "dc11": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "gr": "http://purl.org/goodrelations/v1#",
    "ical": "http://www.w3.org/2002/12/cal/icaltzd#",
    "og": "http://ogp.me/ns#",
    "rev": "http://purl.org/stuff/rev#",
    "sioc": "http://rdfs.org/sioc/ns#",
    "v": "http://rdf.data-vocabulary.org/#",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "schema": "http://schema.org/",
    "describedby": "http://www.w3.org/2007/05/powder-s#describedby",
    "license": "http://www.w3.org/1999/xhtml/vocab#license",
    "role": "http://www.w3.org/1999/xhtml/vocab#role",
}


RDF4J_RIO_DEFAULTS: dict[str, str] = {
    **RDF4J_RDFA11_DEFAULTS,
    "cat": "http://www.w3.org/ns/dcat#",
    "cnt": "http://www.w3.org/2008/content#",
    "gldp": "http://www.w3.org/ns/people#",
    "ht": "http://www.w3.org/2006/http#",
    "ptr": "http://www.w3.org/2009/pointers#",
}


DEFAULT_PROFILES: dict[str, dict[str, str]] = {
    "graphdb": GRAPHDB_DEFAULTS,
    "rdf4j": RDF4J_RIO_DEFAULTS,
    "rdf4j-rio": RDF4J_RIO_DEFAULTS,
    "rdfa11": RDF4J_RDFA11_DEFAULTS,
}


PROFILE_NOTES: dict[str, str] = {
    "rdf4j": (
        "Applied RDF4J Rio parser defaults. Plain RDF4J Server does not "
        "document a GraphDB-style repository namespace bootstrap set."
    ),
    "rdf4j-rio": (
        "Applied RDF4J Rio parser defaults. Plain RDF4J Server does not "
        "document a GraphDB-style repository namespace bootstrap set."
    ),
    "rdfa11": "Applied RDFa 1.1 initial context defaults.",
}
