# Tripartite Agent Surface

This sub-project packages agent-facing MCP servers and skills for the Tripartite Semantic Federation.

Version 0.2 contains a read-only NorthStar MCP server and the `explore-northstar` skill. GroundTruth and Codemesh will be added as separate authority surfaces so their semantics and permissions remain distinct.

## Boundary

This project is an adapter, not a semantic authority. NorthStar owns intent. The adapter calls NorthStar's native `/api/v2` exploration operations and preserves their result envelopes, revisions, nodes, edges, evidence paths, and failures. It must not silently invent intent, resolve foreign-authority facts, or mutate NorthStar.

The MCP server exposes nine operations: authority discovery, reference resolution, native node retrieval, native search, graph traversal, path finding, governing context, revision comparison, and integrity analysis. The complete HTTP examples and failure semantics are in [`docs/northstar-agent-api-examples.md`](docs/northstar-agent-api-examples.md).

## Run

NorthStar defaults to `http://127.0.0.1:9480`. Override it with `NORTHSTAR_BASE_URL`.

```bash
uv run --locked tripartite-agent-surface stdio
uv run --locked tripartite-agent-surface streamable-http
```

The Streamable HTTP server defaults to `127.0.0.1:9490` and serves MCP at `/mcp`.

## Verify

```bash
uv run --locked --extra dev pytest
```

Set `RUN_NORTHSTAR_LIVE=1` to include the read-only live-service test.

## Planned authority surfaces

- NorthStar: available in version 0.2.
- GroundTruth: planned; no tools are declared yet.
- Codemesh: planned; no tools are declared yet.

Each future authority will receive its own MCP server and skill while remaining part of this one installable plugin.
