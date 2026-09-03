"""MCP entry point for the Tripartite NorthStar agent surface."""

from __future__ import annotations

import argparse
import os
from typing import Any, Literal, cast

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from tripartite_agent_surface import __version__
from tripartite_agent_surface.northstar_tools import TOOL_FUNCTIONS


Transport = Literal["stdio", "streamable-http"]
INSTRUCTIONS = (
    "NorthStar is the read-only authority for intent and governance. Start with describe_authority "
    "when scope or vocabulary is unknown. Prefer native nodes, edges, and evidence paths over summaries. "
    "Treat csi:// and data:// values as foreign references, and never treat reachability or a declared "
    "SATISFIES edge as independent proof. Preserve reported limitations, completeness, and revision state."
)

TOOL_DESCRIPTIONS = {
    "describe_authority": "Discover NorthStar's live graph vocabulary, available scopes, backend capabilities, counts, and known adapter limitations. Use first when the catalog or supported queries are unknown.",
    "resolve_references": "Resolve NorthStar URI coordinates in a batch and classify CodeMesh or GroundTruth references without pretending to resolve those foreign authorities.",
    "get_nodes": "Retrieve complete native NorthStar node records by exact URI, optionally with every directly connected edge. Use after search or traversal returns stable identifiers.",
    "search_nodes": "Find NorthStar nodes using lexical content plus exact type, lifecycle, tag, and URI-prefix filters. This is adapter-derived search, not semantic proof.",
    "query_graph": "Explore a bounded NorthStar subgraph in either direction with edge-verb and node-type filters. Use for open-ended relationship questions rather than a canned closure.",
    "find_paths": "Find ordered, bounded graph paths between two identifiers. Use when the evidence connecting two records matters.",
    "get_governing_context": "Retrieve NorthStar's current convenience closure for one or more requirements, code symbols, or data references. Inspect native graph evidence separately when conclusions depend on the path.",
}


def create_server() -> MCPServer:
    server = MCPServer(
        name="tripartite-northstar",
        title="Tripartite NorthStar",
        description="Read-only, graph-preserving agent access to NorthStar intent and governance.",
        instructions=INSTRUCTIONS,
        version=__version__,
    )
    annotations = cast(
        Any,
        ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=True,
        ),
    )
    for name, function in TOOL_FUNCTIONS.items():
        server.add_tool(
            function,
            name=name,
            title=name.replace("_", " ").title(),
            description=TOOL_DESCRIPTIONS[name],
            annotations=annotations,
            structured_output=True,
        )
    return server


def create_app():
    host = os.getenv("TRIPARTITE_AGENT_HOST", "127.0.0.1")
    return create_server().streamable_http_app(
        host=host,
        transport_security=_transport_security(host),
    )


def _transport_security(host: str) -> TransportSecuritySettings | None:
    security = None
    if host not in {"127.0.0.1", "localhost", "::1"}:
        allowed_hosts = [value.strip() for value in os.getenv("TRIPARTITE_AGENT_ALLOWED_HOSTS", "").split(",") if value.strip()]
        allowed_origins = [value.strip() for value in os.getenv("TRIPARTITE_AGENT_ALLOWED_ORIGINS", "").split(",") if value.strip()]
        if not allowed_hosts or not allowed_origins:
            raise ValueError("Non-loopback HTTP requires TRIPARTITE_AGENT_ALLOWED_HOSTS and TRIPARTITE_AGENT_ALLOWED_ORIGINS")
        security = TransportSecuritySettings(
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        )
    return security


def main() -> None:
    parser = argparse.ArgumentParser(description="Tripartite NorthStar MCP server")
    parser.add_argument("transport", nargs="?", choices=("stdio", "streamable-http"), default="stdio")
    args = parser.parse_args()
    server = create_server()
    if args.transport == "stdio":
        server.run("stdio")
        return
    host = os.getenv("TRIPARTITE_AGENT_HOST", "127.0.0.1")
    port = int(os.getenv("TRIPARTITE_AGENT_PORT", "9490"))
    server.run(
        "streamable-http",
        host=host,
        port=port,
        transport_security=_transport_security(host),
    )


if __name__ == "__main__":
    main()
