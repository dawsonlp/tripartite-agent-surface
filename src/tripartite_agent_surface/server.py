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
    "describe_authority": "Discover NorthStar's deployed schemas, vocabulary, caller scope, limits, and retained revisions. Use first when the catalog contract is unknown.",
    "resolve_references": "Resolve NorthStar aliases and defaults in one batch, prove existence separately, and classify CodeMesh or GroundTruth references without inventing foreign results.",
    "get_nodes": "Retrieve revision-bound native NorthStar records by URI with field projection and optional direct edges.",
    "search_nodes": "Run NorthStar-native structured and lexical search with field-level match reasons and opaque continuation.",
    "query_graph": "Traverse the authorized NorthStar graph with direction, verb, type, scope, projection, and resource bounds.",
    "find_paths": "Find ordered, bounded graph paths and preserve the exact edge evidence connecting records.",
    "get_governing_context": "Derive governing intent for native or foreign targets with an evidence path or native field reference for every included item.",
    "compare_revisions": "Compare added, removed, and changed native facts across two retained semantic revisions under current authorization.",
    "analyze_integrity": "Run deterministic, versioned integrity rules over one authorized revision and return evidence-bearing findings.",
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
        allowed_hosts = [
            value.strip()
            for value in os.getenv("TRIPARTITE_AGENT_ALLOWED_HOSTS", "").split(",")
            if value.strip()
        ]
        allowed_origins = [
            value.strip()
            for value in os.getenv("TRIPARTITE_AGENT_ALLOWED_ORIGINS", "").split(",")
            if value.strip()
        ]
        if not allowed_hosts or not allowed_origins:
            raise ValueError(
                "Non-loopback HTTP requires TRIPARTITE_AGENT_ALLOWED_HOSTS and TRIPARTITE_AGENT_ALLOWED_ORIGINS"
            )
        security = TransportSecuritySettings(
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        )
    return security


def main() -> None:
    parser = argparse.ArgumentParser(description="Tripartite NorthStar MCP server")
    parser.add_argument(
        "transport", nargs="?", choices=("stdio", "streamable-http"), default="stdio"
    )
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
