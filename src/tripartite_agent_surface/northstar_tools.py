"""Thin, read-only MCP mappings to NorthStar's native v2 exploration API."""

from __future__ import annotations

from typing import Any, Literal

from tripartite_agent_surface.northstar_client import NorthstarApiError, NorthstarClient

ToolResult = dict[str, Any]
Direction = Literal["incoming", "outgoing", "both"]


def _client() -> NorthstarClient:
    return NorthstarClient()


def _error(exc: Exception, operation: str) -> ToolResult:
    if isinstance(exc, NorthstarApiError):
        detail = {
            "code": exc.kind.upper(),
            "message": str(exc),
            "http_status": exc.status_code,
            "details": exc.details,
            "retryable": exc.kind in {"timeout", "dependency_unavailable"},
        }
    else:
        detail = {"code": "INVALID_INPUT", "message": str(exc), "retryable": False}
    return {
        "request_id": None,
        "operation": f"{operation}@2.0",
        "status": "FAILED",
        "authority": "northstar",
        "source_kind": "NATIVE",
        "catalog_revision": None,
        "effective_scope": {},
        "normalized_query": {},
        "data": {},
        "completeness": {
            "complete": False,
            "truncated": False,
            "stopping_reason": "DEPENDENCY_FAILURE",
            "omitted_categories": [],
            "unchecked_dependencies": ["northstar"],
        },
        "page": {"continuation": None},
        "limits": {},
        "statistics": {"returned": 0, "inspected": 0, "elapsed_ms": None},
        "warnings": [],
        "errors": [detail],
    }


def _call(
    operation: str, tenant: str, action_path: str, payload: dict[str, Any]
) -> ToolResult:
    try:
        return _client().explore(tenant, action_path, payload)
    except (NorthstarApiError, ValueError) as exc:
        return _error(exc, operation)


def _scope(
    solutions: list[str] | None,
    include_global: bool,
    lifecycle_states: list[str] | None = None,
    provenance_tiers: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "solutions": solutions or [],
        "include_global": include_global,
        "lifecycle_states": lifecycle_states or [],
        "provenance_tiers": provenance_tiers or [],
    }


def _projection(
    include_data: bool,
    data_fields: list[str] | None = None,
    include_raw_source: bool = False,
) -> dict[str, Any]:
    return {
        "include_data": include_data,
        "data_fields": data_fields or [],
        "include_raw_source": include_raw_source,
    }


def describe_authority(tenant: str = "tripartite") -> ToolResult:
    """Discover the deployed contract, schemas, vocabularies, limits, scope, and retained revisions."""
    try:
        return _client().describe_authority(tenant)
    except (NorthstarApiError, ValueError) as exc:
        return _error(exc, "describe_authority")


def resolve_references(
    references: list[str],
    tenant: str = "tripartite",
    default_solution: str | None = None,
    default_version: str = "latest",
    revision: str = "latest",
    foreign_resolution: Literal["NONE", "SYNTAX_ONLY", "LIVE"] = "SYNTAX_ONLY",
    solutions: list[str] | None = None,
    include_global: bool = True,
) -> ToolResult:
    """Resolve aliases/defaults and classify foreign references without overstating existence."""
    return _call(
        "resolve_references",
        tenant,
        "references:resolve",
        {
            "references": references,
            "default_solution": default_solution,
            "default_version": default_version,
            "foreign_resolution": foreign_resolution,
            "revision": revision,
            "scope": _scope(solutions, include_global),
        },
    )


def get_nodes(
    uris: list[str],
    tenant: str = "tripartite",
    revision: str = "latest",
    solutions: list[str] | None = None,
    include_global: bool = True,
    include_data: bool = True,
    data_fields: list[str] | None = None,
    include_raw_source: bool = False,
    direct_edges: Literal["none", "incoming", "outgoing", "both"] = "none",
) -> ToolResult:
    """Batch-retrieve native records with projection and optional direct graph edges."""
    return _call(
        "get_nodes",
        tenant,
        "nodes:batchGet",
        {
            "uris": uris,
            "revision": revision,
            "scope": _scope(solutions, include_global),
            "projection": _projection(include_data, data_fields, include_raw_source),
            "direct_edges": direct_edges,
        },
    )


def search_nodes(
    query: str | None = None,
    tenant: str = "tripartite",
    revision: str = "latest",
    solutions: list[str] | None = None,
    include_global: bool = True,
    node_types: list[str] | None = None,
    lifecycle_states: list[str] | None = None,
    provenance_tiers: list[str] | None = None,
    tags: list[str] | None = None,
    uri_prefix: str | None = None,
    field_equals: dict[str, Any] | None = None,
    has_fields: list[str] | None = None,
    has_relationships: list[str] | None = None,
    include_data: bool = False,
    data_fields: list[str] | None = None,
    page_size: int = 50,
    continuation: str | None = None,
) -> ToolResult:
    """Run native structured and lexical search with revision-bound pagination."""
    return _call(
        "search_nodes",
        tenant,
        "nodes:search",
        {
            "query": query,
            "modes": ["STRUCTURED", "LEXICAL"] if query else ["STRUCTURED"],
            "node_types": node_types or [],
            "uri_prefix": uri_prefix,
            "tags": tags or [],
            "field_equals": field_equals or {},
            "has_fields": has_fields or [],
            "has_relationships": has_relationships or [],
            "revision": revision,
            "scope": _scope(
                solutions, include_global, lifecycle_states, provenance_tiers
            ),
            "projection": _projection(include_data, data_fields),
            "page": {"size": page_size, "continuation": continuation},
        },
    )


def query_graph(
    start_uris: list[str],
    tenant: str = "tripartite",
    revision: str = "latest",
    solutions: list[str] | None = None,
    include_global: bool = True,
    direction: Direction = "both",
    include_verbs: list[str] | None = None,
    exclude_verbs: list[str] | None = None,
    include_node_types: list[str] | None = None,
    exclude_node_types: list[str] | None = None,
    stop_node_types: list[str] | None = None,
    min_depth: int = 0,
    max_depth: int = 3,
    max_nodes: int = 200,
    max_edges: int = 1000,
    include_data: bool = False,
    data_fields: list[str] | None = None,
    page_size: int = 50,
    continuation: str | None = None,
) -> ToolResult:
    """Traverse the authorized native graph under explicit filters and hard budgets."""
    return _call(
        "query_graph",
        tenant,
        "graph:query",
        {
            "start_uris": start_uris,
            "direction": direction,
            "include_verbs": include_verbs or [],
            "exclude_verbs": exclude_verbs or [],
            "include_node_types": include_node_types or [],
            "exclude_node_types": exclude_node_types or [],
            "stop_node_types": stop_node_types or [],
            "min_depth": min_depth,
            "revision": revision,
            "scope": _scope(solutions, include_global),
            "projection": _projection(include_data, data_fields),
            "budget": {
                "max_depth": max_depth,
                "max_nodes": max_nodes,
                "max_edges": max_edges,
            },
            "page": {"size": page_size, "continuation": continuation},
        },
    )


def find_paths(
    source_uris: list[str],
    target_uris: list[str],
    tenant: str = "tripartite",
    revision: str = "latest",
    solutions: list[str] | None = None,
    include_global: bool = True,
    direction: Direction = "both",
    include_verbs: list[str] | None = None,
    include_node_types: list[str] | None = None,
    max_depth: int = 5,
    max_paths: int = 10,
    include_data: bool = False,
    page_size: int = 10,
    continuation: str | None = None,
) -> ToolResult:
    """Find ordered paths and the exact native edge evidence they use."""
    return _call(
        "find_paths",
        tenant,
        "graph:findPaths",
        {
            "source_uris": source_uris,
            "target_uris": target_uris,
            "direction": direction,
            "include_verbs": include_verbs or [],
            "include_node_types": include_node_types or [],
            "revision": revision,
            "scope": _scope(solutions, include_global),
            "projection": _projection(include_data),
            "budget": {"max_depth": max_depth, "max_paths": max_paths},
            "page": {"size": page_size, "continuation": continuation},
        },
    )


def get_governing_context(
    target_uris: list[str],
    tenant: str = "tripartite",
    revision: str = "latest",
    solutions: list[str] | None = None,
    include_global: bool = True,
    include_data: bool = False,
    data_fields: list[str] | None = None,
    include_compact_markdown: bool = False,
    max_depth: int = 3,
    page_size: int = 50,
    continuation: str | None = None,
) -> ToolResult:
    """Derive governing intent with every inclusion path or native field reference."""
    return _call(
        "get_governing_context",
        tenant,
        "context:governing",
        {
            "target_uris": target_uris,
            "revision": revision,
            "scope": _scope(solutions, include_global),
            "projection": _projection(include_data, data_fields),
            "include_compact_markdown": include_compact_markdown,
            "budget": {"max_depth": max_depth},
            "page": {"size": page_size, "continuation": continuation},
        },
    )


def compare_revisions(
    before_revision: str,
    after_revision: str,
    tenant: str = "tripartite",
    solutions: list[str] | None = None,
    include_global: bool = True,
    uris: list[str] | None = None,
    node_types: list[str] | None = None,
    page_size: int = 50,
    continuation: str | None = None,
) -> ToolResult:
    """Compare retained semantic revisions under the caller's current authorization."""
    return _call(
        "compare_revisions",
        tenant,
        "revisions:compare",
        {
            "before_revision": before_revision,
            "after_revision": after_revision,
            "uris": uris or [],
            "node_types": node_types or [],
            "scope": _scope(solutions, include_global),
            "page": {"size": page_size, "continuation": continuation},
        },
    )


def analyze_integrity(
    tenant: str = "tripartite",
    revision: str = "latest",
    solutions: list[str] | None = None,
    include_global: bool = True,
    finding_classes: list[str] | None = None,
    page_size: int = 50,
    continuation: str | None = None,
) -> ToolResult:
    """Run deterministic integrity rules without treating declarations as proof."""
    return _call(
        "analyze_integrity",
        tenant,
        "integrity:analyze",
        {
            "revision": revision,
            "scope": _scope(solutions, include_global),
            "finding_classes": finding_classes or [],
            "page": {"size": page_size, "continuation": continuation},
        },
    )


TOOL_FUNCTIONS = {
    "describe_authority": describe_authority,
    "resolve_references": resolve_references,
    "get_nodes": get_nodes,
    "search_nodes": search_nodes,
    "query_graph": query_graph,
    "find_paths": find_paths,
    "get_governing_context": get_governing_context,
    "compare_revisions": compare_revisions,
    "analyze_integrity": analyze_integrity,
}
