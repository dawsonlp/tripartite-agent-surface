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

1. Call `describe_authority` when the deployed schemas, vocabulary, current revision, caller scope, or limits are unknown.
2. Pin material multi-call investigations to the concrete returned revision. Never silently restart at `latest` after a stale-revision or continuation failure.
3. Use `resolve_references` when aliases, contextual URI forms, existence, or foreign ownership matter. Syntactic normalization is not existence proof.
4. Use `search_nodes` to obtain candidate identifiers. Treat lexical matching as discovery, not evidence; use structured filters to narrow before requesting large bodies.
5. Use `get_nodes` for native records and direct edges, selecting only fields needed for the task.
6. Use `query_graph` for bounded neighborhood exploration and `find_paths` when the exact connecting evidence matters.
7. Use `get_governing_context` for the common governance derivation. Preserve its path or field-reference evidence and unresolved expected references.
8. Use `compare_revisions` for change claims and `analyze_integrity` for deterministic catalog defects. An integrity finding is derived evidence, not a stored declaration.
9. Preserve empty, partial, truncated, ambiguous, unauthorized, unresolved, stale, and unavailable outcomes. Do not fill gaps from examples or general expectations.

## Evidence language

State conclusions using the strongest supported verb:

- `records` or `declares` for native fields and edges;
- `derives` for deterministic adapter results;
- `suggests` for interpretation;
- `does not establish` when reachability or declared linkage is being mistaken for implementation, verification, compliance, or impact.

## References

- Read [tool-selection.md](references/tool-selection.md) when choosing among search, traversal, path, or closure operations.
- Read [result-semantics.md](references/result-semantics.md) when interpreting provenance, revisions, external references, limitations, or partial results.
- Read [examples.md](references/examples.md) when handling ambiguity, continuation, authorization denial, stale revisions, or dependency failure.
