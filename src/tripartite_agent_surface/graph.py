"""Bounded, explicitly derived graph operations for the transitional adapter."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from collections.abc import Iterable
from typing import Any, Literal

Direction = Literal["incoming", "outgoing", "both"]


def graph_revision(graph: dict[str, Any]) -> str:
    """Return a content digest, not an authoritative NorthStar revision."""
    encoded = json.dumps(graph, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"derived-sha256:{hashlib.sha256(encoded).hexdigest()}"


def validate_graph(
    graph: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, dict) or not isinstance(edges, list):
        raise TypeError(
            "NorthStar graph must contain an object 'nodes' and an array 'edges'"
        )
    return nodes, [edge for edge in edges if isinstance(edge, dict)]


def paginate(
    items: list[Any], cursor: str | None, limit: int
) -> tuple[list[Any], str | None]:
    if not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200")
    try:
        offset = int(cursor or "0")
    except ValueError as exc:
        raise ValueError("cursor must be a non-negative integer string") from exc
    if offset < 0:
        raise ValueError("cursor must be non-negative")
    page = items[offset : offset + limit]
    next_cursor = str(offset + limit) if offset + limit < len(items) else None
    return page, next_cursor


def searchable_text(uri: str, record: dict[str, Any]) -> str:
    return f"{uri}\n{json.dumps(record, sort_keys=True, default=str)}".lower()


def matching_nodes(
    graph: dict[str, Any],
    *,
    query: str | None,
    node_types: list[str] | None,
    lifecycle_states: list[str] | None,
    tags: list[str] | None,
    uri_prefix: str | None,
) -> list[dict[str, Any]]:
    nodes, _ = validate_graph(graph)
    wanted_types = set(node_types or [])
    wanted_lifecycle = set(lifecycle_states or [])
    wanted_tags = set(tags or [])
    needle = query.lower().strip() if query else None
    results: list[dict[str, Any]] = []

    for uri in sorted(nodes):
        record = nodes[uri]
        if not isinstance(record, dict):
            continue
        record_data = record.get("data")
        data: dict[str, Any] = record_data if isinstance(record_data, dict) else {}
        node_type = str(record.get("type", ""))
        lifecycle = str(data.get("lifecycle", data.get("status", "")))
        record_tags = {str(tag) for tag in data.get("tags", []) if isinstance(tag, str)}
        if wanted_types and node_type not in wanted_types:
            continue
        if wanted_lifecycle and lifecycle not in wanted_lifecycle:
            continue
        if wanted_tags and not wanted_tags.issubset(record_tags):
            continue
        if uri_prefix and not uri.startswith(uri_prefix):
            continue
        if needle and needle not in searchable_text(uri, record):
            continue
        results.append({"uri": uri, "type": node_type, "data": data})
    return results


def adjacency(
    edges: Iterable[dict[str, Any]],
    direction: Direction,
) -> dict[str, list[tuple[str, dict[str, Any]]]]:
    result: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            continue
        if direction in {"outgoing", "both"}:
            result[source].append((target, edge))
        if direction in {"incoming", "both"}:
            result[target].append((source, edge))
    return result


def bounded_subgraph(
    graph: dict[str, Any],
    *,
    start_uris: list[str],
    direction: Direction,
    verbs: list[str] | None,
    node_types: list[str] | None,
    max_depth: int,
    max_nodes: int,
) -> dict[str, Any]:
    if not 0 <= max_depth <= 8:
        raise ValueError("max_depth must be between 0 and 8")
    if not 1 <= max_nodes <= 500:
        raise ValueError("max_nodes must be between 1 and 500")
    if direction not in {"incoming", "outgoing", "both"}:
        raise ValueError("direction must be incoming, outgoing, or both")
    if not start_uris:
        raise ValueError("at least one start URI is required")

    nodes, edges = validate_graph(graph)
    wanted_verbs = set(verbs or [])
    wanted_types = set(node_types or [])
    usable_edges = [
        edge for edge in edges if not wanted_verbs or edge.get("verb") in wanted_verbs
    ]
    neighbors = adjacency(usable_edges, direction)
    queue = deque((uri, 0) for uri in start_uris)
    visited: set[str] = set()
    selected_edges: dict[tuple[str, str, str], dict[str, Any]] = {}
    truncated = False

    while queue:
        uri, depth = queue.popleft()
        if uri in visited:
            continue
        if len(visited) >= max_nodes:
            truncated = True
            break
        record = nodes.get(uri)
        if (
            record
            and wanted_types
            and record.get("type") not in wanted_types
            and uri not in start_uris
        ):
            continue
        visited.add(uri)
        if depth >= max_depth:
            continue
        for adjacent_uri, edge in neighbors.get(uri, []):
            adjacent_record = nodes.get(adjacent_uri)
            if (
                wanted_types
                and isinstance(adjacent_record, dict)
                and adjacent_record.get("type") not in wanted_types
            ):
                continue
            key = (
                str(edge.get("source")),
                str(edge.get("verb")),
                str(edge.get("target")),
            )
            selected_edges[key] = edge
            if adjacent_uri not in visited:
                queue.append((adjacent_uri, depth + 1))

    native_nodes = {uri: nodes[uri] for uri in sorted(visited) if uri in nodes}
    external_references = sorted(uri for uri in visited if uri not in nodes)
    return {
        "start_uris": start_uris,
        "nodes": native_nodes,
        "edges": list(selected_edges.values()),
        "external_references": external_references,
        "missing_start_uris": [
            uri for uri in start_uris if uri not in nodes and uri not in neighbors
        ],
        "complete": not truncated,
        "truncated": truncated,
        "limits": {"max_depth": max_depth, "max_nodes": max_nodes},
    }


def find_paths_in_graph(
    graph: dict[str, Any],
    *,
    source_uri: str,
    target_uri: str,
    direction: Direction,
    verbs: list[str] | None,
    max_depth: int,
    max_paths: int,
) -> dict[str, Any]:
    if not 1 <= max_depth <= 8:
        raise ValueError("max_depth must be between 1 and 8")
    if not 1 <= max_paths <= 20:
        raise ValueError("max_paths must be between 1 and 20")
    _, edges = validate_graph(graph)
    wanted_verbs = set(verbs or [])
    usable_edges = [
        edge for edge in edges if not wanted_verbs or edge.get("verb") in wanted_verbs
    ]
    neighbors = adjacency(usable_edges, direction)
    queue: deque[tuple[str, list[str], list[dict[str, Any]]]] = deque(
        [(source_uri, [source_uri], [])]
    )
    paths: list[dict[str, Any]] = []
    exhausted = True

    while queue and len(paths) < max_paths:
        current, node_path, edge_path = queue.popleft()
        if len(edge_path) >= max_depth:
            continue
        for adjacent_uri, edge in neighbors.get(current, []):
            if adjacent_uri in node_path:
                continue
            next_nodes = [*node_path, adjacent_uri]
            next_edges = [*edge_path, edge]
            if adjacent_uri == target_uri:
                paths.append({"nodes": next_nodes, "edges": next_edges})
                if len(paths) >= max_paths:
                    exhausted = False
                    break
            else:
                queue.append((adjacent_uri, next_nodes, next_edges))

    return {
        "source_uri": source_uri,
        "target_uri": target_uri,
        "paths": paths,
        "complete": exhausted,
        "truncated": not exhausted,
        "limits": {"max_depth": max_depth, "max_paths": max_paths},
    }
