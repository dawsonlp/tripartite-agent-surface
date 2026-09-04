# NorthStar Agent Exploration API Development Checklist

## Purpose

Restructure NorthStar's read API so an authorized AI agent can explore the native intent graph efficiently without confusing declarations with proof, inferred relationships with stored facts, or convenient summaries with complete evidence.

This checklist translates [`docs/northstar-agent-api-requirements.md`](docs/northstar-agent-api-requirements.md) into priority-ordered design, implementation, migration, and verification work. It also incorporates defects observed through the live MCP surface on 2026-09-03.

The evidence-backed implementation position is recorded in [`docs/northstar-v2-conformance.md`](docs/northstar-v2-conformance.md). Checked items are implemented or design-approved as stated; unchecked items are deliberately retained as remaining work.

## Scope

Included:

- NorthStar read-side authority discovery, identifier resolution, node retrieval, search, graph traversal, paths, governing context, revision comparison, and integrity analysis.
- Authoritative tenant, solution, lifecycle, provenance, revision, and membership semantics for every read.
- Evidence-preserving result envelopes, errors, pagination, continuation, projection, and context budgets.
- Reconciliation of embedded relationship fields, graph edges, and derived closures.
- NorthStar-to-CodeMesh and NorthStar-to-GroundTruth foreign-reference status without importing either authority's semantics.
- Migration of the current MCP adapter from full-graph client-side derivation to native NorthStar operations.
- Conformance, authorization, failure, restart, migration, performance, and agent-comprehension tests.

Excluded unless separately approved:

- NorthStar mutation, approval, supersession, publication, or invariant-execution APIs.
- GroundTruth or CodeMesh agent tools beyond reporting foreign-reference state.
- A choice of database, search engine, graph query language, cache, authentication provider, or deployment topology in this checklist.
- Treating a declared `SATISFIES` relationship as proof that an implementation conforms.

## Inputs Consulted

- [`docs/northstar-agent-api-requirements.md`](docs/northstar-agent-api-requirements.md), requirements `NS-AE-001` through `NS-AE-056` and acceptance scenarios `AS-1` through `AS-12`.
- The v0.1 NorthStar MCP server and `explore-northstar` skill in this repository.
- Live NorthStar MCP exploration on 2026-09-03 at API version `0.2.0`.
- The live graph observed at 84 nodes and 82 edges, identified only by adapter-derived digest `derived-sha256:a6c7e694d0b40bbc29e378e9889ef1566018134f5364edf31185a31e73c9e753`.
- Ten active NorthStar capability records and their direct graph neighborhoods.

## Governing Inputs

- NorthStar owns intent and governance.
- GroundTruth owns information meaning and state semantics.
- CodeMesh owns computation and code structure.
- Native records and relationships remain accessible behind every derived view.
- Every result distinguishes stored fact, normalization, deterministic derivation, heuristic inference, and agent interpretation.
- Read authorization is enforced by the authority; caller-supplied scope labels are not authorization.
- Read-only agent exploration is a separate permission boundary from validation and mutation.

The human CTO approved the requirements, technical design, and recommended CTO decisions on 2026-09-03. Phase 0 is therefore open for implementation. Unchecked items below remain real work; approval does not convert them into evidence of implementation or production fitness.

## Observed Baseline

- [x] The MCP server can discover and call the live NorthStar service.
- [x] Seven transitional tools expose discovery, resolution, retrieval, search, traversal, paths, and governing context.
- [x] The live graph exposes `CapabilitySpec`, `ComponentSpec`, `DecisionSpec`, and `InvariantSpec` with four edge verbs.
- [x] All ten NorthStar capabilities have one declared CodeMesh `SATISFIES` edge.
- [x] NorthStar exposes an authoritative catalog revision or addressable snapshot.
- [x] Tenant and solution membership are canonical and enforced by the read API.
- [x] Canonical and scoped URI forms behave identically across resolution, lookup, search, and traversal.
- [ ] Embedded governance references, graph edges, and closure results agree.
- [x] Governing-context results contain evidence paths.
- [x] Search and graph traversal execute natively with server-side projection, limits, and continuation.
- [x] Declared implementation relationships are distinguishable from demonstrated verification evidence.

## Priority Model

- **P0 — authority correctness and security:** Without this work, responses may cross authorization boundaries, change during reasoning, or misrepresent graph truth.
- **P1 — complete native exploration:** Required to satisfy the approved agent-use cases without full-graph downloads or lossy summaries.
- **P2 — derived analysis and adoption:** Valuable after the underlying graph, scope, evidence, and revision contracts are trustworthy.
- **P3 — optimization:** Performance improvements that must not weaken completeness or epistemic labeling.

---

## Phase 0 — Architecture and Technical-Design Gate

### P0.1 Approve authority and revision semantics

- [x] Identify the authoritative source for a read: committed repository state, live database state, named snapshot, or an explicitly ordered combination.
- [x] Define the catalog revision identity and what content it covers: nodes, edges, embedded fields, membership, schemas, aliases, and provenance.
- [x] Define revision creation, retention, expiration, comparison, and stale-token behavior.
- [x] Define whether a multi-call session pins a snapshot or uses optimistic revision checks.
- [x] Define how global records are inherited into tenant and solution views.
- [x] Define `owned`, `inherited`, `governing`, `referenced`, and `visible` membership as distinct relations.
- [ ] Record the decisions in approved NorthStar or federation ADRs.

Suggested direction:

- Use an immutable, opaque revision token backed by a reproducible semantic snapshot.
- Require each query to report its effective revision and scope; never silently substitute `latest` for an unavailable requested revision.
- Represent membership and inheritance explicitly rather than deriving them from URI substrings or display labels.

Completion evidence:

- [ ] Two independent implementations can compute the same membership sets and revision identity from the approved rules.
- [x] The CTO has approved the authority, membership, inheritance, and retention decisions.

### P0.2 Approve authorization semantics

- [x] Define authenticated caller identity and effective tenant, solution, lifecycle, provenance, and raw-source grants.
- [x] Define global-administration and cross-tenant roles, if any.
- [x] Define denial behavior so counts, errors, ambiguity candidates, snippets, and continuation tokens do not leak unauthorized records.
- [x] Define audit fields and retention without logging secrets or unrestricted record bodies.
- [x] Decide whether authorization is evaluated before or during snapshot/query construction.

Suggested direction:

- Construct an immutable effective-read-scope object from verified credentials, then pass it through every repository and derivation operation.
- Reject caller scope that exceeds the credential-derived scope rather than merely filtering the final response.

Completion evidence:

- [ ] Threat model covers direct retrieval, search, graph traversal, aggregation, errors, timing-sensitive counts, and continuation.
- [x] Negative authorization scenarios are part of the approved technical design.

### P0.3 Approve the graph and relationship source of truth

- [ ] Inventory every embedded relationship field and graph edge representation.
- [x] Define which representation is authoritative for each relationship.
- [x] Define endpoint type rules, cardinality, parallel-edge semantics, foreign endpoint handling, and lifecycle behavior.
- [x] Define how projections such as `governed_by`, `constraints`, and `exported_capabilities` are generated and checked.
- [x] Define the evidence model for declared, observed, verified, contradicted, and stale relationships.

Suggested direction:

- Store one canonical relationship fact and derive secondary embedded projections transactionally.
- Give validation evidence its own typed records or edges; do not mutate `DECLARED` provenance into `VERIFIED` based only on reachability.

Completion evidence:

- [x] The technical design prevents embedded fields, native edges, and closures from silently disagreeing.
- [x] Relationship migration and rollback rules are approved.

### P0.4 Produce and approve the technical design

- [x] Define versioned request and response schemas for all nine logical operations.
- [x] Define the common result envelope, per-item result, error taxonomy, continuation token, projection syntax, and budget syntax.
- [x] Define repository, query, authorization, snapshot, and audit boundaries without exposing persistence details publicly.
- [x] Define REST and MCP mappings while keeping one semantic contract.
- [x] Define backward compatibility and deprecation for current `/api/v1` consumers.
- [x] Define migration sequencing, rollback, observability, and conformance testing.
- [ ] Review the design as both a systems architecture and implementation-buildability artifact.

Completion evidence:

- [ ] Approved technical design maps every `NS-AE-*` requirement and `AS-*` scenario to a component and test.
- [x] No implementation phase below depends on an unresolved design decision.

---

## Phase 1 — P0 Authority, Scope, and Result Integrity

Depends on Phase 0 approval.

### P0.5 Introduce authoritative snapshots and revision-bound reads

- [x] Generate a revision when authoritative semantic content changes.
- [x] Make revisions addressable for all content operations.
- [x] Include revision and schema version in native nodes and edges.
- [x] Reject stale or unavailable revisions with a structured error.
- [x] Ensure pagination and continuation remain bound to the originating scope, query, and revision.
- [x] Detect and reject token reuse under a different caller or scope.
- [x] Expose current revision and supported historical range through `describe_authority`.

Verification:

- [ ] Repeated reads at one revision are semantically identical.
- [x] A catalog mutation between two pages cannot mix revisions.
- [ ] Expired, forged, and cross-tenant continuation tokens fail without leakage.
- [x] `compare_revisions` can reproduce a known controlled change.

### P0.6 Enforce canonical tenant and solution scope

- [x] Persist or deterministically materialize explicit record membership and inheritance reasons.
- [x] Enforce authorization before retrieving native bodies or computing derived results.
- [x] Report effective caller scope, requested scope, defaults, and inheritance policy in every response.
- [ ] Replace ambiguous `total_nodes` with separately defined unique, owned, inherited, governing, and visible counts.
- [x] Make foreign endpoints retain the NorthStar edge without importing or exposing foreign-authority content.

Verification:

- [ ] Tenant A cannot infer Tenant B records through search, counts, errors, paths, or timing-visible continuation behavior.
- [ ] Global records appear only under the approved inheritance rules and are labeled inherited rather than owned.
- [ ] Solution counts are independently reproducible from native membership facts.

### P0.7 Establish the common result and error contract

- [x] Return request identifier, normalized query, effective scope, revision, structured data, completeness, defaults, warnings, unresolved references, limits, statistics, and continuation consistently.
- [ ] Give each batched item an independent success, not-found, ambiguous, unauthorized, stale, unsupported, dependency-unavailable, timeout, resource-limit, or internal-error status.
- [x] Preserve successful items during partial failure.
- [x] Make empty results valid and explicit; never substitute examples or stale cached content.
- [ ] Mark every non-native result with derivation rule and supporting evidence identifiers.

Verification:

- [ ] Contract tests cover every error class and partial-success combination.
- [ ] Failure injection proves that no failed request returns plausible substitute graph data.

---

## Phase 2 — P0 Graph and Identifier Coherence

### P0.8 Normalize canonical identifiers everywhere

- [x] Use one semantic coordinate model for parsing, equality, hashing, storage lookup, search filtering, and serialization.
- [x] Make scoped shorthand and fully qualified canonical forms resolve to the same record.
- [x] Preserve input form and aliases separately from canonical identity.
- [x] Define tenant/version defaulting and ambiguity rules.
- [x] Require resolution to distinguish syntactic normalization from existence proof.
- [ ] Version the URI grammar and maintain conformance vectors.

Immediate regression to fix:

- [x] `req://tripartite:northstar/...` canonical prefixes and `req://northstar/...` stored prefixes return the same authorized records.

Verification:

- [ ] `parse(canonicalize(x))` is stable.
- [x] Equivalent forms produce equal coordinates and graph keys.
- [x] Canonical lookup, search, traversal, and path finding agree.
- [x] Normalizing a nonexistent URI does not report the record as existing.

### P0.9 Reconcile embedded relationships, graph edges, and closure

- [ ] Migrate current embedded relationship references into the approved canonical representation.
- [ ] Generate or validate projections atomically.
- [ ] Reject or quarantine invalid endpoint types, missing internal targets, ambiguous aliases, and unauthorized cross-scope links.
- [x] Repair governing-context traversal so embedded governance cannot disappear from `decisions`.
- [x] Return the exact field reference or ordered edge path that includes every closure item.
- [x] Detect inconsistent duplicates as integrity findings until migration completes.

Immediate regression to fix:

- [ ] `req://validators/validate-code-ast` returns its two declared governing ADRs consistently through native retrieval, graph traversal, and governing context.

Verification:

- [ ] A generated integrity report contains zero unexplained embedded/edge disagreements.
- [ ] Removing an evidence edge causes the relevant closure test to fail.
- [x] Parallel and reciprocal edges survive serialization without deduplication.

### P0.10 Separate declarations from verification evidence

- [x] Define provenance granularity and required fields for nodes, edges, and evidence.
- [ ] Require authorship or accountable source identity for publishable declarations.
- [x] Represent implementation observation and verification separately from `SATISFIES` declarations.
- [ ] Attach test run, artifact revision, verifier, time, and scope to demonstrated evidence.
- [ ] Define contradiction and staleness behavior.

Verification:

- [ ] The current ten `SATISFIES` edges remain labeled `DECLARED` until independent evidence is attached.
- [x] An agent can query capabilities with declaration but no current verification.
- [ ] Revoked or stale evidence does not silently remain demonstrated coverage.

---

## Phase 3 — P1 Native Agent Exploration Operations

### P1.1 Complete `describe_authority`

- [x] Return live node and edge schemas, requiredness, cardinality, reference targets, allowed values, and native/defaulted/derived status.
- [x] Return supported scopes, revisions, lifecycle and provenance vocabularies, operations, projections, filters, limits, and caller permissions.
- [x] Report unavailable features explicitly.
- [x] Include future node types and fields without requiring an MCP release.

Verification:

- [ ] A newly connected generic client can formulate valid requests without reading source code or static skill text.
- [ ] Runtime discovery changes when a schema or capability is deployed.

### P1.2 Complete `resolve_references`

- [x] Batch inputs and preserve independent statuses.
- [x] Return original input, canonical identity, parsed coordinates, type, scope, version, match basis, ambiguity candidates, and existence status.
- [x] Classify CodeMesh and GroundTruth references without claiming foreign resolution unless the owning authority was queried.
- [x] Report `not_checked` separately from `not_found` and `dependency_unavailable`.

Verification:

- [ ] Exact, defaulted, alias, ambiguous, nonexistent, malformed, unauthorized, and unavailable-foreign cases pass.

### P1.3 Complete `get_nodes`

- [x] Support batch retrieval at one explicit revision.
- [x] Support field projection, nested-field selection, raw-source inclusion, and direct-edge summaries.
- [x] Preserve unknown fields and type discriminators.
- [x] Apply lifecycle, provenance, and source-content authorization.
- [x] Avoid repeating identical node bodies unnecessarily.

Verification:

- [ ] A full capability contract round-trips without field loss.
- [ ] Projection materially reduces payload size while preserving stable identifiers.
- [x] One missing item does not fail successful batch items.

### P1.4 Move `search_nodes` into NorthStar

- [x] Implement server-side exact identifier, structured, lexical, and optional semantic search as separately labeled modes.
- [x] Support tenant, solution, type, lifecycle, provenance, tags, relationship presence, and type-specific field filters.
- [x] Return match reason and matched field without promoting semantic rank to evidence.
- [ ] Add field projection, sorting, stable pagination, context budgets, and hard server limits.
- [x] Ensure search cannot leak unauthorized counts or snippets.

Immediate regression to fix:

- [ ] A broad `northstar` search can return identifiers and titles without serializing more than 40,000 tokens of full ADR bodies.

Verification:

- [ ] Exact, structured, lexical, and semantic results are distinguishable.
- [x] Pages are stable at a pinned revision.
- [x] Search works identically with equivalent canonical URI forms.

### P1.5 Move `query_graph` into NorthStar

- [ ] Support multiple starts or match conditions, direction, verb and node filters, depth, stop conditions, scope, lifecycle, provenance, projection, and budgets.
- [x] Return separate node, edge, and path collections.
- [x] Report visited counts, omitted categories, stopping reason, completeness, and continuation.
- [x] Preserve foreign endpoints and parallel edges.
- [x] Enforce authorization during traversal, not only on final serialization.

Verification:

- [ ] A novel question not represented by a convenience endpoint is answerable through composable traversal.
- [x] Limit termination is distinguishable from graph exhaustion.
- [ ] Traversal cannot bridge through an unauthorized node to reveal an authorized endpoint relationship.

### P1.6 Move `find_paths` into NorthStar

- [ ] Support source and target sets or match conditions, direction, allowed verbs and types, scope, maximum length, path count, and revision.
- [x] Preserve ordered nodes and edges with per-edge provenance.
- [x] Distinguish no path from incomplete search.
- [x] Define deterministic ordering for equivalent paths.

Verification:

- [ ] Known direct, multi-hop, absent, cyclic, truncated, foreign-endpoint, and unauthorized cases pass.

---

## Phase 4 — P1 Evidence-Backed Derived Operations

### P1.7 Rebuild `get_governing_context` over native primitives

- [x] Include capabilities, components, decisions, invariants, policies, workflows, and qualities supported by evidence.
- [x] Return inclusion rule and exact native field or path for each item.
- [x] Apply lifecycle, scope, inheritance, and provenance rules explicitly.
- [x] Report missing expected relationships and unresolved foreign endpoints.
- [x] Make structured data canonical and compact rendering optional.
- [x] Include revision, completeness, truncation, and continuation.

Verification:

- [x] Every compact item can be retrieved at the same revision.
- [x] Every omission is identified by category.
- [x] Native retrieval and governing context do not disagree silently.

### P1.8 Implement `compare_revisions`

- [ ] Compare catalog revisions, selected record versions, and bounded subgraphs.
- [x] Return added, removed, and field-level changed nodes and edges.
- [x] Include lifecycle, provenance, membership, schema, and foreign-reference changes.
- [x] Identify values that cannot be compared losslessly.
- [x] Preserve before/after revision and scope metadata.

Verification:

- [ ] Controlled fixtures exercise every change class and schema-version transition.
- [x] Authorization prevents comparison from revealing inaccessible prior content.

### P1.9 Implement `analyze_integrity`

- [ ] Detect dangling internal references, unresolved foreign references, ambiguity, invalid endpoints, embedded/edge inconsistency, insufficient provenance, lifecycle faults, supersession faults, dependency cycles, membership anomalies, and missing evidence.
- [ ] Label each rule deterministic or heuristic.
- [ ] Return supporting records, paths, rule version, severity, scope, and revision.
- [x] Allow finding-class filters and bounded continuation.
- [x] Keep advisory findings separate from authority facts.

Verification:

- [ ] Seed one defect of every supported class and prove detection.
- [ ] A clean fixture produces no fabricated findings.
- [x] Heuristic changes cannot rewrite native records or deterministic results.

---

## Phase 5 — P1 Ontology and Requirement Quality

### P1.10 Make the live vocabulary match published claims

- [ ] Decide and document whether `CapabilitySpec` is the sole requirement primitive or whether a separate requirement abstraction exists.
- [ ] Decide whether `PolicySpec`, workflow, and quality specifications are supported now, planned, or removed from current capability claims.
- [ ] Expose the live schema status and maturity of each node and relationship type.
- [ ] Preserve unknown future types through generic graph operations.

### P1.11 Establish contract completeness rules

- [ ] Define when actor grants, operated entities, failure modes, policies, quality SLOs, preconditions, postconditions, and state transitions are required or explicitly not applicable.
- [ ] Replace empty arrays of unknown meaning with explicit `not_applicable`, `not_yet_specified`, or populated values where the schema permits.
- [ ] Define machine-checkable acceptance and evidence references without forcing all intent into executable code.
- [ ] Add deterministic integrity findings for incomplete active contracts.

Immediate records to reassess:

- [ ] Tenant discovery and isolation identify authorized actors and authorization failures.
- [ ] Export defines write target, collision, permission, serialization, and partial-failure behavior.
- [ ] URI resolution defines malformed, ambiguous, unsupported-scheme, unavailable-version, and nonexistent-record outcomes.
- [ ] Closure defines cycles, limits, missing targets, incomplete foreign resolution, and stale revisions.
- [ ] Quality expectations receive measurable targets or are explicitly deferred.

Verification:

- [ ] Active requirements cannot appear complete merely because optional-looking arrays are empty.
- [ ] Integrity analysis identifies incomplete contracts using documented rules.

---

## Phase 6 — P2 MCP and Client Migration

### P2.1 Replace transitional adapter derivations

- [x] Add new NorthStar client methods against the approved native API operations.
- [x] Preserve the existing seven tool names where compatible to avoid unnecessary client churn.
- [x] Add `compare_revisions` and `analyze_integrity` only when the backend contracts are real.
- [x] Remove full-graph client-side search, traversal, and path computation after parity is demonstrated.
- [x] Preserve explicit `source_kind`, scope, revision, completeness, limits, and error information through MCP.
- [x] Do not allow the MCP adapter to invent missing membership, authorization, evidence, or provenance.

Verification:

- [ ] MCP and direct HTTP conformance fixtures return semantically equivalent results.
- [x] Tool payloads respect requested projections and token budgets.
- [x] Existing Codex and Antigravity discovery and read-only calls continue to work.

### P2.2 Update agent guidance

- [x] Update `explore-northstar` tool-selection guidance for native operations, revisions, evidence, and continuation.
- [x] Add examples for ambiguity, partial success, stale revision, truncation, authorization denial, and foreign-authority unavailability.
- [x] Explain declared versus demonstrated coverage explicitly.
- [x] Validate that tool descriptions remain concise enough for discovery while full schemas remain machine-readable.

---

## Phase 7 — Verification and Release Gates

### P1.12 Build the requirements conformance suite

- [ ] Map every `NS-AE-001` through `NS-AE-056` requirement to at least one automated or explicitly manual verification.
- [ ] Implement `AS-1` through `AS-12` as end-to-end acceptance scenarios.
- [ ] Run the same semantic fixtures through direct NorthStar and MCP transports.
- [ ] Test representative, empty, ambiguous, stale, unauthorized, truncated, timeout, dependency-failure, and partial-success cases.
- [ ] Add restart tests proving revision and authorization behavior survives process replacement.
- [ ] Add deterministic schema and URI compatibility fixtures.

### P1.13 Add security and failure-injection tests

- [ ] Exercise horizontal and vertical authorization failures across every operation.
- [ ] Exercise dependency loss during foreign-reference status checks.
- [ ] Exercise persistence or snapshot failure during revision creation.
- [ ] Exercise continuation after catalog change and token expiration.
- [ ] Exercise large and cyclic graph inputs against hard budgets.
- [ ] Verify logs and traces contain no secrets or unauthorized record bodies.

### P2.3 Establish performance budgets

- [ ] Approve latency, payload, node, edge, path, raw-body, and token-budget targets per operation.
- [ ] Benchmark small projections separately from full native retrieval.
- [ ] Benchmark authorization and revision pinning under realistic graph sizes.
- [ ] Prove broad searches do not serialize full decision documents unless requested.
- [ ] Treat performance as a constraint on implementation, not permission to omit evidence silently.

### P2.4 Perform staged migration

- [ ] Capture representative current responses and known inconsistencies before migration.
- [ ] Migrate relationships, memberships, aliases, and provenance with deterministic reports.
- [ ] Run old and new read paths in comparison mode without presenting disagreement as success.
- [ ] Publish incompatibilities and deprecation dates.
- [ ] Update portal and other consumers only after contract tests pass.
- [ ] Retain a tested rollback to the last coherent revision.

Release completion criteria:

- [ ] All P0 and P1 tasks are complete.
- [ ] All twelve acceptance scenarios pass over the deployed API and MCP server.
- [ ] No known cross-tenant leakage, revision mixing, canonical-URI mismatch, or unexplained graph/projection inconsistency remains.
- [ ] Declared and demonstrated coverage are queryable as distinct facts.
- [ ] NorthStar, the MCP adapter, Codex, and Antigravity agree on operation schemas and observed behavior.
- [ ] Documentation describes deployed behavior rather than intended future behavior.
- [ ] Rollback and recovery have been exercised.

---

## Decisions Made

- Security, revision identity, membership, and graph coherence precede query richness.
- Native bounded operations precede derived integrity and context conveniences.
- MCP client-side derivations remain transitional and are removed only after behavioral parity.
- Verification requires consequence-bearing tests; declarations and passing schema validation are insufficient.
- The v0.1 MCP tool names are retained where the approved semantic contract permits.

## Decisions Explicitly Deferred

- Production authentication provider and token format.
- Semantic-ranking technology.
- Revision retention duration and exact performance SLO values.
- Field/document-level provenance and a general conflict-set model.
- Whether policies, workflows, and qualities become independently persisted future node types.
- Mutation, validation, approval, and publication APIs.

## Remaining Questions

- Can one node be owned by multiple solutions, or only visible through inheritance and governance?
- What evidence qualifies a declared implementation link as demonstrated?
- Which raw ADR and policy sources may agents retrieve under finer-grained classifications?
- When do production evidence and owning-authority readiness justify live CodeMesh/GroundTruth resolution?

## CTO Decisions Recorded

The human CTO approved the authority, revision, membership, authorization, relationship, v2-route, and first-release search decisions on 2026-09-03. Revision-retention and production performance targets remain explicit release gates rather than implicit approvals.

## Decision Record

- Requirements and technical design: approved for implementation.
- Current implementation status: partial conformance, with the open gaps recorded in the conformance document.
- Production release: not approved by this checklist; its gates remain unchecked.

## Recommended Next Step

Use the conformance record to close the remaining P0/P1 evidence gaps before declaring production readiness. Do not conflate local live validation with migration, recovery, load, or production-security evidence.

## Approval Status

implementation-approved; production release blocked on remaining unchecked evidence gates

## CTO Review

Approved by the human CTO on 2026-09-03 for implementation.

## Sign-Off

### Author

- Signer: Senior Implementation Engineer Agent
- Signer Type: agent
- Role: Development checklist author
- Review Perspective: implementation sequencing and verification
- Disposition: submitted-for-review
- Summary Notes: Design-gated checklist for bringing the NorthStar read API to the approved agent-exploration standard while preserving authority and evidence boundaries.
- Date: 2026-09-03

### Review Entries

- Reviewer: CTO (Human)
- Disposition: approved for implementation
- Evidence: The user stated, "I approve all of the CTO decisions, as you advised. I am good with the technical design."
- Date: 2026-09-03

### CTO Sign-Off

- Signer: CTO (Human)
- Signer Type: human
- Status: approved for implementation
- Date: 2026-09-03

### Workflow Status

- Current Status: implementation in progress; production gates remain open
