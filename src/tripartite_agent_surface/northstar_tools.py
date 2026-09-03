"""Read-only NorthStar MCP tool implementations."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from tripartite_agent_surface.graph import (
    bounded_subgraph,
    find_paths_in_graph,
    graph_revision,
    matching_nodes,
    paginate,
    validate_graph,
)
from tripartite_agent_surface.northstar_client import NorthstarApiError, NorthstarClient


class ToolResult(TypedDict):
    status: str
    authority: str
    source_kind: str
    catalog_revision: str | None
    data: dict[str, Any]
    limitations: list[str]
    errors: list[dict[str, Any]]


TRANSITIONAL_LIMITATIONS = [
    "NorthStar does not yet expose an authoritative catalog revision; derived-sha256 is a content digest of one fetched graph.",
    "Tenant and solution membership are not enforced or represented canonically by the current read API.",
]


def _client() -> NorthstarClient:
    return NorthstarClient()


def _error(exc: Exception, *, limitations: list[str] | None = None) -> ToolResult:
    if isinstance(exc, NorthstarApiError):
        detail = {
            "kind": exc.kind,
            "message": str(exc),
            "status_code": exc.status_code,
            "details": exc.details,
        }
    else:
        detail = {"kind": "invalid_request", "message": str(exc)}
    return {
        "status": "error",
        "authority": "northstar",
        "source_kind": "live_api",
        "catalog_revision": None,
        "data": {},
        "limitations": limitations or [],
        "errors": [detail],
    }


def _success(
    data: dict[str, Any],
    *,
    revision: str | None,
    source_kind: str = "live_api",
    limitations: list[str] | None = None,
    status: str = "ok",
) -> ToolResult:
    return {
        "status": status,
        "authority": "northstar",
        "source_kind": source_kind,
        "catalog_revision": revision,
        "data": data,
        "limitations": limitations or [],
        "errors": [],
    }


def describe_authority() -> ToolResult:
    """Discover NorthStar's live graph vocabulary, scopes, API capabilities, and adapter limits."""
    try:
        client = _client()
        health = client.health()
        tenants = client.tenants()
        solutions = client.solutions()
        graph = client.graph()
        openapi = client.openapi()
        nodes, edges = validate_graph(graph)
        node_types = sorted(
            {str(record.get("type")) for record in nodes.values() if isinstance(record, dict)}
        )
        edge_verbs = sorted({str(edge.get("verb")) for edge in edges if edge.get("verb")})
        api_paths = sorted(str(path) for path in openapi.get("paths", {}))
        data = {
            "authority_boundary": "NorthStar owns intent and governance, not code structure or information meaning.",
            "health": health,
            "tenants": tenants.get("tenants", []),
            "solutions": solutions.get("solutions", []),
            "live_vocabulary": {"node_types": node_types, "edge_verbs": edge_verbs},
            "counts": {"nodes": len(nodes), "edges": len(edges)},
            "backend_api": {
                "title": openapi.get("info", {}).get("title"),
                "version": openapi.get("info", {}).get("version"),
                "paths": api_paths,
            },
            "mcp_tools": [
                "describe_authority",
                "resolve_references",
                "get_nodes",
                "search_nodes",
                "query_graph",
                "find_paths",
                "get_governing_context",
            ],
            "deferred_requirements": ["compare_revisions", "analyze_integrity"],
        }
        return _success(data, revision=graph_revision(graph), limitations=TRANSITIONAL_LIMITATIONS)
    except (NorthstarApiError, ValueError) as exc:
        return _error(exc)


def resolve_references(
    references: list[str],
    default_tenant: str = "tripartite",
    default_version: str = "latest",
) -> ToolResult:
    """Resolve up to 50 NorthStar URIs; preserve foreign references as unchecked external endpoints."""
    if not 1 <= len(references) <= 50:
        return _error(ValueError("references must contain between 1 and 50 values"))
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    client = _client()
    for reference in references:
        if reference.startswith("csi://"):
            results.append({
                "input": reference,
                "authority": "codemesh",
                "status": "not_checked",
                "canonical_uri": None,
            })
            continue
        if reference.startswith("data://"):
            results.append({
                "input": reference,
                "authority": "groundtruth",
                "status": "not_checked",
                "canonical_uri": None,
            })
            continue
        try:
            resolved = client.resolve_uri(
                reference,
                default_tenant=default_tenant,
                default_version=default_version,
            )
            results.append({"input": reference, "authority": "northstar", "status": "resolved", **resolved})
        except NorthstarApiError as exc:
            errors.append({
                "input": reference,
                "kind": exc.kind,
                "message": str(exc),
                "status_code": exc.status_code,
                "details": exc.details,
            })
    status = "partial" if errors and results else "error" if errors else "ok"
    return {
        "status": status,
        "authority": "northstar",
        "source_kind": "live_api",
        "catalog_revision": None,
        "data": {"results": results, "applied_defaults": {
            "tenant": default_tenant, "version": default_version,
        }},
        "limitations": [
            "Foreign references are classified but are not resolved until their owning authority is added.",
            "The current NorthStar resolver may normalize an identifier without proving that a node exists.",
        ],
        "errors": errors,
    }


def get_nodes(uris: list[str], include_edges: bool = False) -> ToolResult:
    """Retrieve up to 100 native nodes by exact graph identifier, optionally with direct edges."""
    if not 1 <= len(uris) <= 100:
        return _error(ValueError("uris must contain between 1 and 100 values"))
    try:
        graph = _client().graph()
        nodes, edges = validate_graph(graph)
        found = {uri: nodes[uri] for uri in uris if uri in nodes}
        missing = [uri for uri in uris if uri not in nodes]
        data: dict[str, Any] = {"nodes": found, "missing": missing}
        if include_edges:
            requested = set(uris)
            data["edges"] = [
                edge for edge in edges
                if edge.get("source") in requested or edge.get("target") in requested
            ]
        status = "partial" if found and missing else "not_found" if missing else "ok"
        return _success(
            data,
            revision=graph_revision(graph),
            limitations=TRANSITIONAL_LIMITATIONS,
            status=status,
        )
    except (NorthstarApiError, ValueError) as exc:
        return _error(exc)


def search_nodes(
    query: str | None = None,
    node_types: list[str] | None = None,
    lifecycle_states: list[str] | None = None,
    tags: list[str] | None = None,
    uri_prefix: str | None = None,
    limit: int = 25,
    cursor: str | None = None,
) -> ToolResult:
    """Lexically search native node JSON with exact structured filters and stable pagination."""
    try:
        graph = _client().graph()
        matches = matching_nodes(
            graph,
            query=query,
            node_types=node_types,
            lifecycle_states=lifecycle_states,
            tags=tags,
            uri_prefix=uri_prefix,
        )
        page, next_cursor = paginate(matches, cursor, limit)
        data = {
            "matches": page,
            "match_count": len(matches),
            "next_cursor": next_cursor,
            "match_mode": "case_insensitive_lexical_and_structured",
            "filters": {
                "query": query,
                "node_types": node_types or [],
                "lifecycle_states": lifecycle_states or [],
                "tags": tags or [],
                "uri_prefix": uri_prefix,
            },
        }
        return _success(
            data,
            revision=graph_revision(graph),
            source_kind="derived_from_live_graph",
            limitations=[
                *TRANSITIONAL_LIMITATIONS,
                "Search is performed by this adapter over one full-graph response; it is not authoritative semantic search.",
            ],
        )
    except (NorthstarApiError, ValueError) as exc:
        return _error(exc)


def query_graph(
    start_uris: list[str],
    direction: Literal["incoming", "outgoing", "both"] = "both",
    verbs: list[str] | None = None,
    node_types: list[str] | None = None,
    max_depth: int = 2,
    max_nodes: int = 100,
) -> ToolResult:
    """Traverse a bounded native subgraph from one or more exact identifiers."""
    try:
        graph = _client().graph()
        data = bounded_subgraph(
            graph,
            start_uris=start_uris,
            direction=direction,
            verbs=verbs,
            node_types=node_types,
            max_depth=max_depth,
            max_nodes=max_nodes,
        )
        return _success(
            data,
            revision=graph_revision(graph),
            source_kind="derived_from_live_graph",
            limitations=[
                *TRANSITIONAL_LIMITATIONS,
                "Traversal is performed by this adapter over one full-graph response until NorthStar provides a native bounded query.",
            ],
            status="ok" if data["complete"] else "partial",
        )
    except (NorthstarApiError, ValueError) as exc:
        return _error(exc)


def find_paths(
    source_uri: str,
    target_uri: str,
    direction: Literal["incoming", "outgoing", "both"] = "both",
    verbs: list[str] | None = None,
    max_depth: int = 5,
    max_paths: int = 5,
) -> ToolResult:
    """Find bounded, ordered evidence paths between two exact graph identifiers."""
    try:
        graph = _client().graph()
        data = find_paths_in_graph(
            graph,
            source_uri=source_uri,
            target_uri=target_uri,
            direction=direction,
            verbs=verbs,
            max_depth=max_depth,
            max_paths=max_paths,
        )
        return _success(
            data,
            revision=graph_revision(graph),
            source_kind="derived_from_live_graph",
            limitations=[
                *TRANSITIONAL_LIMITATIONS,
                "Path finding is performed by this adapter over one full-graph response.",
            ],
        )
    except (NorthstarApiError, ValueError) as exc:
        return _error(exc)


def get_governing_context(target_uris: list[str]) -> ToolResult:
    """Get NorthStar's current governing-intent closure for up to 20 native or foreign targets."""
    if not 1 <= len(target_uris) <= 20:
        return _error(ValueError("target_uris must contain between 1 and 20 values"))
    client = _client()
    contexts: dict[str, Any] = {}
    errors: list[dict[str, Any]] = []
    for target_uri in target_uris:
        try:
            contexts[target_uri] = client.governing_context(target_uri)
        except NorthstarApiError as exc:
            errors.append({
                "target_uri": target_uri,
                "kind": exc.kind,
                "message": str(exc),
                "status_code": exc.status_code,
                "details": exc.details,
            })
    status = "partial" if contexts and errors else "error" if errors else "ok"
    return {
        "status": status,
        "authority": "northstar",
        "source_kind": "live_api_derived_closure",
        "catalog_revision": None,
        "data": {"contexts": contexts},
        "limitations": [
            "The current NorthStar closure does not return evidence paths or an authoritative catalog revision.",
            "An empty closure means no governing context was returned; it does not prove none exists outside the loaded graph.",
        ],
        "errors": errors,
    }


TOOL_FUNCTIONS = {
    "describe_authority": describe_authority,
    "resolve_references": resolve_references,
    "get_nodes": get_nodes,
    "search_nodes": search_nodes,
    "query_graph": query_graph,
    "find_paths": find_paths,
    "get_governing_context": get_governing_context,
}
