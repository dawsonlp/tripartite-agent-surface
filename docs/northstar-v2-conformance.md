# NorthStar v2 Conformance Record

Status date: 2026-09-03. This is an implementation record, not a production-release claim. “Verified” means automated local tests and/or a successful live local deployment. “Partial” means the contract is present in part but a listed acceptance condition remains unproven or unimplemented.

## Evidence Run

- NorthStar static suite: `55 passed`.
- NorthStar exploration suite includes revision pinning across a changed `latest`, opaque continuation validation, ambiguity, native error envelopes, foreign dependency unavailability, resource limits, authorization rejection, paths, governing context, comparison, integrity, and parallel edges.
- Agent-surface suite: `11 passed, 1 skipped`; the enabled live MCP test passed after the NorthStar rebuild.
- Live local PostgreSQL authority: 84 nodes, 82 edges, revision `nsr-sha256:5e72ba319a42b8d01e48f0dc1d3a526af83625b40db571c78c1f8b1113367a37`.
- The revision remained identical across a second service restart with the same catalog content.
- The isolated `mcp-manager` installation listed and called all nine operations successfully against that revision.

## Requirement Traceability

| Requirement | Status | Evidence or remaining boundary |
| --- | --- | --- |
| NS-AE-001 | Verified | `get_nodes` returns generic native node envelopes and requested data. |
| NS-AE-002 | Verified | Node envelope includes URI, type, lifecycle, provenance, membership, revision, schema, and projection. |
| NS-AE-003 | Verified | First-class edges include ID, endpoints, verb, provenance, metadata, endpoint state, and revision. |
| NS-AE-004 | Verified | Parallel edge identity is unit-tested; reciprocal/self edges use the same first-class representation. |
| NS-AE-005 | Verified | Requested node data remains structured. |
| NS-AE-006 | Partial | Generic exploration preserves observed fields; legacy PostgreSQL graph loading still rejects unknown domain types. |
| NS-AE-007 | Verified | `describe_authority` returns runtime schemas, vocabularies, features, limits, and scopes. |
| NS-AE-008 | Partial | Runtime schemas now include observed types, requiredness, cardinality, meanings, allowed values where finite, and reference schemes; complete declared nested semantics remain future work. |
| NS-AE-009 | Verified | Runtime discovery reports unsupported semantic ranking and mutation. |
| NS-AE-010 | Verified | Every content operation resolves effective scope and a concrete revision. |
| NS-AE-011 | Verified | Effective scope and normalized request record defaults. |
| NS-AE-012 | Partial | Owned membership and global inheritance are explicit; governing/referenced/visible membership facts are not yet fully materialized. |
| NS-AE-013 | Partial | Authority returns unique, owned, inherited, and visible counts; governing/shared counts remain incomplete. |
| NS-AE-014 | Verified | Fixed revisions and continuations pin multi-call reads. |
| NS-AE-015 | Verified | Missing retained revisions return the structured `STALE_REVISION` envelope. |
| NS-AE-016 | Verified | Resolution and retrieval batches preserve independent results. |
| NS-AE-017 | Partial | Composable equality, presence, tag, relationship, type, scope, lifecycle, and provenance filters exist; range filters do not. |
| NS-AE-018 | Verified | Match reasons distinguish exact, structured, and lexical native matches. |
| NS-AE-019 | Partial | Multiple starts, directions, type/verb filters, depth, type stop conditions, scope, and hard budgets exist; structured start/stop match conditions do not. |
| NS-AE-020 | Verified | Paths retain ordered nodes and edge IDs. |
| NS-AE-021 | Verified | Nodes, edges, traversal, paths, and resolution are directly callable. |
| NS-AE-022 | Verified | Derived results expose stable native identifiers and revision metadata. |
| NS-AE-023 | Partial | Node and edge provenance granularity is explicit; field/document/import granularity is not yet represented. |
| NS-AE-024 | Verified | Envelopes and items label native, normalized, derived, and declared facts. |
| NS-AE-025 | Verified | Governing context, comparison, integrity, and coverage expose derivation rule/evidence. |
| NS-AE-026 | Verified | Tool and skill guidance explicitly prohibit treating reachability/declarations as proof. |
| NS-AE-027 | Verified | `SATISFIES` and `VERIFIES` stay `DECLARED` without separate evidence. |
| NS-AE-028 | Partial | Canonical collisions are rejected and underspecified versions return candidates; a general stored conflict-set model is not implemented. |
| NS-AE-029 | Verified | Foreign endpoints are first-class references, not copied records. |
| NS-AE-030 | Verified | Foreign resolution distinguishes `NOT_CHECKED`, `UNAUTHORIZED`, and `DEPENDENCY_UNAVAILABLE`; no foreign gateway is deployed. |
| NS-AE-031 | Verified | Foreign dependency failure cannot replace NorthStar native results. |
| NS-AE-032 | Verified | Native edges remain readable while foreign resolution is unavailable. |
| NS-AE-033 | Verified | Node and data-field projections are server-side. |
| NS-AE-034 | Partial | Search, traversal, paths, governing context, comparison, and integrity paginate; audit events have no query endpoint. |
| NS-AE-035 | Verified | Envelopes report completeness, truncation, stopping reason, limits, and continuation. |
| NS-AE-036 | Partial | Item/node/edge/path/depth/byte ceilings are enforced; wall-clock deadline termination is not yet enforced during every operation. |
| NS-AE-037 | Verified | Common identifier and context operations support batches. |
| NS-AE-038 | Verified | Structured results are canonical and governing Markdown is optional with omissions. |
| NS-AE-039 | Verified | Node bodies are deduplicated for batch retrieval and separated from graph paths. |
| NS-AE-040 | Partial | Raw Markdown requires an explicit authorized selection; a full large-field classification registry is pending. |
| NS-AE-041 | Verified | Common envelope states completeness for every v2 operation. |
| NS-AE-042 | Verified | Empty results are explicit data, not examples. |
| NS-AE-043 | Verified | Batch operations preserve successful items and structured failures. |
| NS-AE-044 | Partial | Core input, authorization, stale, resource, dependency, and internal-safe failure forms exist; timeout and unsupported-operation paths lack dedicated exercised cases. |
| NS-AE-045 | Verified | Failed envelopes contain no substitute graph data. |
| NS-AE-046 | Verified | Revision-bound reads are deterministic apart from identified operational metadata. |
| NS-AE-047 | Verified | Scope is resolved before query/derivation output and raw source is separately authorized. |
| NS-AE-048 | Verified | Static credential grants intersect caller-supplied scope. |
| NS-AE-049 | Partial | Filtering is applied before result construction and negative tests exist; complete cross-operation timing-leak testing is pending. |
| NS-AE-050 | Verified | v2 operations are read-only. |
| NS-AE-051 | Partial | Metadata-only audit events are emitted; durable audit sink, retention, and log inspection tests are pending. |
| NS-AE-052 | Verified | Runtime schemas, concise MCP descriptions, skill guidance, and examples are provided. |
| NS-AE-053 | Verified | Tool-selection guidance distinguishes native, derived, comparison, and integrity operations. |
| NS-AE-054 | Verified | OpenAPI and runtime JSON Schemas are machine-readable. |
| NS-AE-055 | Verified | MCP is a thin transport mapping of the public v2 contract. |
| NS-AE-056 | Verified | The examples document covers every operation, continuations, ambiguity, partial results, denial, stale revisions, and foreign unavailability. |

## Acceptance Scenario Traceability

| Scenario | Status | Evidence |
| --- | --- | --- |
| AS-1 Runtime discovery | Verified | Authority/OpenAPI contract test and live MCP discovery. |
| AS-2 Lossless capability retrieval | Verified | Native projected retrieval and structured contract fixture. |
| AS-3 Unanticipated graph question | Verified | Native search, traversal, and path operations. |
| AS-4 Evidence-complete governing context | Verified | Context test asserts edge/field evidence. |
| AS-5 Ambiguous reference | Verified | Two-version ambiguity test. |
| AS-6 Stable multi-call exploration | Verified | `latest` advance between graph pages is tested. |
| AS-7 Honest truncation | Verified | Hard graph limit test and continuation tests. |
| AS-8 External authority unavailable | Verified | Live foreign status is `DEPENDENCY_UNAVAILABLE` without losing native content. |
| AS-9 Authorization isolation | Partial | Static cross-tenant denial is tested; full matrix remains pending. |
| AS-10 No fabricated fallback | Verified | Stale and invalid common-envelope tests plus authority readiness behavior. |
| AS-11 Native and compact views agree | Verified | Governing-context compact projection derives from structured nodes. |
| AS-12 Declared versus demonstrated coverage | Verified | Coverage assessment keeps declarations distinct from verification evidence. |

## Production Gates Still Open

1. Complete the partial requirement rows above, especially authorization coverage, audit durability, deadline enforcement, generic future-type loading, conflict sets, and structured range/match filters.
2. Perform a deterministic legacy relationship/membership migration and a shadow-read comparison before retiring v1 behavior.
3. Exercise database outage, publication failure, restart/recovery, token expiration, and rollback paths against the deployed service.
4. Set and measure real latency, payload, concurrency, revision-retention, and continuation-expiry targets.
5. Configure production authentication, key management, secret rotation, audit retention, TLS/trusted proxies, and a live foreign-resolution gateway only when its owning authority is ready.
