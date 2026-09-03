# Tripartite Agent Surface

This sub-project packages agent-facing MCP servers and skills for the Tripartite Semantic Federation.

Version 0.1 contains a read-only NorthStar MCP server and the `explore-northstar` skill. GroundTruth and Codemesh will be added as separate authority surfaces so their semantics and permissions remain distinct.

## Boundary

This project is an adapter, not a semantic authority. NorthStar owns intent. The adapter calls NorthStar's service, preserves native nodes and edges, and labels any client-side search or traversal it performs. It must not silently invent intent, resolve foreign-authority facts, or mutate NorthStar.

The current NorthStar API lacks several operations required by [`docs/northstar-agent-api-requirements.md`](docs/northstar-agent-api-requirements.md). Version 0.1 therefore provides a useful transitional surface over the existing read API and reports the missing revision, membership, evidence-path, and historical capabilities as limitations.

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

- NorthStar: available in version 0.1.
- GroundTruth: planned; no tools are declared yet.
- Codemesh: planned; no tools are declared yet.

Each future authority will receive its own MCP server and skill while remaining part of this one installable plugin.
