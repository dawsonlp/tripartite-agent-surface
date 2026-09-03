---
name: explore-northstar
description: Explore NorthStar intent and governance as an evidence-backed graph. Use when a task asks why software exists, what governs or constrains it, how requirements and decisions relate, what intent may be affected, or where the intent graph is incomplete. Do not use it to modify NorthStar or to treat CodeMesh and GroundTruth references as locally authoritative.
---

# Explore NorthStar

Use the NorthStar MCP tools to inspect live intent while preserving the distinction between stored evidence and interpretation.

## Authority boundary

- NorthStar owns intent: capabilities, components, workflows, decisions, invariants, policies, and quality expectations.
- A `csi://` value is a reference to Codemesh computation authority. A `data://` value is a reference to GroundTruth information authority.
- NorthStar can declare relationships to foreign identifiers; that declaration does not prove the foreign artifact exists or satisfies the intent.
- All current tools are read-only. Do not imply that exploration authorizes validation, approval, publication, or mutation.

## Working method

1. Call `describe_authority` when the live vocabulary, catalog size, scope, or backend capability is unknown.
2. Use `search_nodes` to obtain candidate identifiers. Treat lexical matching as discovery, not evidence.
3. Use `get_nodes` for full native records and direct edges.
4. Use `query_graph` for open-ended neighborhood exploration and `find_paths` when the connecting evidence matters.
5. Use `get_governing_context` for a compact common-case view, then inspect native nodes and paths before making a consequential claim.
6. Carry the returned catalog revision or content digest through the analysis. Report when the backend cannot provide authoritative revision consistency.
7. Preserve empty, partial, truncated, ambiguous, unresolved, and unavailable outcomes. Do not fill gaps from examples or general expectations.

## Evidence language

State conclusions using the strongest supported verb:

- `records` or `declares` for native fields and edges;
- `derives` for deterministic adapter results;
- `suggests` for interpretation;
- `does not establish` when reachability or declared linkage is being mistaken for implementation, verification, compliance, or impact.

## References

- Read [tool-selection.md](references/tool-selection.md) when choosing among search, traversal, path, or closure operations.
- Read [result-semantics.md](references/result-semantics.md) when interpreting provenance, revisions, external references, limitations, or partial results.
