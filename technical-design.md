# NorthStar Agent Exploration API Technical Design

## Purpose

Define an implementable read-side design that brings NorthStar's public API and the Tripartite agent surface into conformance with [`docs/northstar-agent-api-requirements.md`](docs/northstar-agent-api-requirements.md).

The design preserves NorthStar as the sole authority for intent and governance while giving human interfaces, automation, and AI agents equal access to native records, graph relationships, revision-bound queries, and the evidence behind derived results.

## Scope

This design covers:

- the NorthStar read API contract;
- authorization-derived tenant and solution scope;
- canonical identifier resolution;
- immutable catalog revisions and reproducible reads;
- native node, edge, search, traversal, and path operations;
- evidence-backed governing context, revision comparison, and integrity analysis;
- pagination, continuation, projection, budgets, errors, and audit behavior;
- migration from the current `/api/v1` implementation;
- use of the same API through the MCP adapter.

This design does not define:

- public creation, modification, approval, publication, or deletion workflows;
- invariant execution against proposed code or data mutations;
- GroundTruth or CodeMesh internals;
- an authentication provider or credential format;
- semantic-search technology;
- production topology or final performance SLOs.

## Inputs Consulted

- [`docs/northstar-agent-api-requirements.md`](docs/northstar-agent-api-requirements.md), `NS-AE-001` through `NS-AE-056` and `AS-1` through `AS-12`.
- [`development-checklist.md`](development-checklist.md).
- NorthStar accepted ADRs 0001 through 0006 and ADR 0010.
- NorthStar design documents for the intent ontology, bounded-context components, relational intent graph, closure resolution, and executable invariants.
- NorthStar requirements-authority and URI-addressing specifications.
- Current NorthStar service, graph, URI, repository, PostgreSQL, closure, entity, provenance, and contract implementations.
- Live NorthStar API `0.2.0`, inspected through the MCP server on 2026-09-03.

## Governing Inputs

The following accepted decisions constrain this design:

1. NorthStar owns intent and governance; it does not own code structure or information meaning.
2. PostgreSQL-backed service APIs are the authoritative systems of record. Files are generated snapshots, not an authority fallback.
3. APIs are capability-oriented and equal across human, automation, and agent consumers.
4. Tenant is the root resource for content discovery, and global governance is inherited explicitly.
5. Canonical Option B identifiers use `scheme://tenant:solution/path@version#fragment`; contextual forms are aliases resolved against explicit context.
6. The intent model is a typed multigraph with first-class nodes and edges.
7. Presentation and MCP adapters contain no authority rules or hidden domain logic.

The human CTO approved the requirements, this technical design, and the recommended CTO decisions on 2026-09-03. No separate independent architect or implementation-engineer review is claimed; those perspectives remain useful release-quality checks rather than implied approvals.

## Current-State Findings That Drive the Design

The following are observations, not assumptions:

- The live service reported 84 nodes and 82 edges, but no authoritative revision. The MCP adapter computed a content digest after downloading the graph.
- Tenant enumeration is hardcoded, caller authentication is absent, and tenant path parameters do not filter the returned solution set.
- Solution membership is derived through string, domain, and component-name heuristics.
- The PostgreSQL `solutions.slug` constraint is globally unique rather than tenant-qualified.
- Stored node rows default tenant and solution values instead of requiring explicit scope.
- A solution-filtered graph load retrieves filtered nodes but every edge.
- Edge persistence keys `(source, verb, target)`, which cannot preserve parallel relationships.
- Edge provenance is stored but not restored by the PostgreSQL loader.
- Unknown persisted node types and relationship verbs are silently skipped.
- The service can silently fall back from PostgreSQL to filesystem state and can report successful writes after persistence errors.
- URI resolution normalizes canonical forms, but graph lookup and search use stored strings directly. Canonical and contextual forms therefore do not behave as one identity.
- Capability governance can appear in embedded fields without corresponding graph edges. Governing closure can consequently return constraints but omit declared decisions.
- The current graph endpoint has no projection, authorization, stable pagination, continuation, or size budget.
- OpenAPI describes several request models but does not provide a complete typed response contract for the exploration surface.
- All ten observed NorthStar `SATISFIES` links were declarations; none independently demonstrated conformance.

## Design Principles

1. **Resolve scope before data access.** Filtering a completed result is too late for authorization.
2. **Resolve one revision per request.** Every repository call in that request observes the same immutable snapshot.
3. **Canonical identity is semantic identity.** Aliases and input spelling never become competing graph keys.
4. **The graph is canonical for relationships.** Embedded relationship collections are validated projections.
5. **Native facts precede derived views.** Derived results cite native fields, nodes, edges, and paths.
6. **Declaration is not demonstration.** Provenance and evidence state remain visible and separate.
7. **Limits fail honestly.** Truncation and incompleteness are data, not prose or implicit behavior.
8. **Foreign references remain foreign.** NorthStar reports its own references and optional resolution observations without copying foreign authority into its truth model.
9. **One semantic API, multiple transports.** HTTP and MCP expose the same operations and result meaning.
10. **Fail closed on authority loss.** Loss of PostgreSQL authority produces an unready service, not a silent filesystem substitute.

## Technical Decomposition

The design retains the existing NorthStar control-plane bounded context. These are internal subsystems, not new semantic authorities or independently deployable microservices.

| Subsystem | Responsibility | Must not do |
|---|---|---|
| HTTP capability adapter | Authenticate request context, validate transport schemas, invoke one application operation, serialize the canonical result | Query tables directly, infer membership, or construct closures |
| Exploration application service | Coordinate scope, revision, repository, budgets, and result assembly for the nine operations | Apply unrecorded authorization or persistence-specific logic |
| Effective-scope resolver | Convert verified identity claims plus requested tenant/solution/lifecycle/provenance scope into an immutable effective read scope | Trust caller-supplied tenant labels as authorization |
| Revision catalog | Resolve `latest` once, address historical revisions, and expose revision metadata | Substitute a different revision silently |
| Canonical identifier service | Parse, canonicalize, resolve aliases/defaults, and classify internal or foreign coordinates | Treat syntactic normalization as existence proof |
| Schema and capability registry | Publish live node schemas, edge vocabulary, lifecycle/provenance vocabularies, operation schemas, limits, and feature availability | Repeat static marketing text that differs from deployment |
| Revisioned graph repository | Retrieve native nodes, edges, memberships, aliases, and adjacency at one revision and effective scope | Return unauthorized rows for later filtering |
| Search service | Execute exact, structured, and lexical search over authorized revisioned records | Relabel ranking as evidence or return full large bodies by default |
| Graph query engine | Execute bounded traversal and path queries over the authorized snapshot | Flatten paths into prose or discard parallel edges |
| Evidence and derivation assembler | Produce governing context, comparisons, and integrity findings with inclusion rules and evidence paths | Invent missing relationships or resolve conflicts silently |
| Foreign-reference gateway | Optionally ask an owning authority whether a foreign identifier resolves | Make foreign availability a prerequisite for returning NorthStar facts |
| Audit sink | Record caller, operation, effective scope, revision, limits, result status, and timing | Log bearer tokens, secrets, unrestricted record bodies, or unauthorized candidates |
| MCP adapter | Map MCP tools to the public HTTP capability operations and preserve structured result semantics | Download the full graph for hidden client-side business logic after native operations exist |

### Placement in the current NorthStar structure

- `core` retains typed intent entities, relationship semantics, canonical coordinates, lifecycle, provenance, and result-neutral domain rules.
- `catalog` owns revision selection, immutable snapshot access, schema registry, and effective catalog views.
- `query` owns search planning, bounded graph execution, paths, governing context, comparison, and integrity rules.
- `adapters` contains PostgreSQL persistence, authentication/identity integration, optional foreign-authority clients, and audit integration.
- `service` contains HTTP routing and transport models only.
- `tripartite-agent-surface` remains a separate access adapter and skill package.

No route handler may inspect private graph dictionaries, issue SQL, or reconstruct solution membership.

## Authoritative Revision Model

### Revision semantics

A catalog revision is an immutable semantic snapshot of:

- native node records and type-specific content;
- native relationship edges and metadata;
- canonical URI aliases;
- tenant and solution memberships with their basis;
- schema-registry version;
- node, edge, and relationship provenance.

Operational metadata such as request logs, cache entries, health probes, and foreign live-resolution observations is not part of the semantic revision.

Each revision exposes:

| Field | Meaning |
|---|---|
| `revision_id` | Opaque stable identifier accepted by all read operations |
| `parent_revision_id` | Direct predecessor when one exists |
| `semantic_hash` | Deterministic hash of normalized semantic snapshot content |
| `schema_version` | Version of node, edge, scope, and result schemas |
| `committed_at` | Authority commit time |
| `committed_by` | Accountable principal or governed process |
| `record_counts` | Unique node, edge, alias, and membership counts |
| `status` | `CURRENT`, `HISTORICAL`, or `RETIRED`; retired content is not silently served |

`latest` is resolved to a concrete `revision_id` once at request admission. The concrete value, not `latest`, is passed to all downstream operations and returned to the caller.

### Initial persistence design

The first conforming implementation uses immutable full semantic snapshots in PostgreSQL. This favors recovery, comparison, and correctness at the current graph size. Copy-on-write or interval storage may replace the physical representation later without changing repository or API semantics.

Logical tables:

| Table | Key | Required content |
|---|---|---|
| `catalog_revisions` | `revision_id` | parent, semantic hash, schema version, commit provenance, status, counts |
| `node_versions` | `(revision_id, canonical_uri)` | type, tenant owner, lifecycle, provenance, typed data, content hash, optional source reference |
| `edge_versions` | `(revision_id, edge_id)` | source, verb, target, provenance, metadata, source/target resolution state, content hash |
| `record_memberships` | `(revision_id, canonical_uri, tenant, solution, membership_kind, basis)` | explicit ownership, inheritance, governance, reference, or visibility basis |
| `uri_aliases` | `(revision_id, alias_uri, context_key)` | canonical target, alias kind, required defaults, ambiguity group |
| `schema_registries` | `schema_version` | machine-readable node, edge, common-result, and operation schemas |

The externally visible `edge_id` permits parallel edges. Identical endpoint and verb triples may coexist when their identity, provenance, or meaning differs.

Revision publication is atomic: all snapshot rows, validation results, counts, and semantic hash commit together, then the current-revision pointer advances. A failed publication never exposes a partial revision.

## Canonical Identity and Reference Resolution

### Coordinate model

All identifier handling uses one coordinate value:

- scheme;
- tenant;
- solution;
- version;
- local path;
- optional fragment.

The canonical serialized form contains explicit tenant and version. Contextual forms are aliases resolved using an explicit effective scope and revision. Storage, equality, hashing, membership, edge endpoints, and cache keys use canonical identity only.

### Resolution stages

1. Parse syntax without asserting existence.
2. Apply only documented defaults from the effective scope.
3. Resolve aliases at the selected revision.
4. Determine whether zero, one, or multiple canonical candidates exist.
5. Check caller authorization before returning candidate metadata.
6. Classify the coordinate as NorthStar-owned or foreign.
7. Optionally request live foreign resolution when explicitly requested and authorized.

Resolution statuses are:

- `EXACT`
- `DEFAULTED`
- `ALIAS`
- `AMBIGUOUS`
- `NOT_FOUND`
- `INVALID`
- `UNAUTHORIZED`
- `FOREIGN_NOT_CHECKED`
- `FOREIGN_RESOLVED`
- `FOREIGN_NOT_FOUND`
- `DEPENDENCY_UNAVAILABLE`

`canonical_uri` may be returned for a syntactically normalized nonexistent reference, but `existence_status` remains `NOT_FOUND`. Clients must not infer existence from normalization.

## Tenant, Solution, and Authorization Model

### Effective read scope

Every content operation receives an immutable effective scope produced from verified identity plus the request:

| Field | Meaning |
|---|---|
| `subject_ref` | Opaque authenticated subject reference for audit; not normally echoed |
| `tenant` | One authorized requested tenant |
| `solutions` | Authorized solution subset or wildcard grant |
| `include_global` | Whether approved global inheritance is applied |
| `lifecycles` | Visible lifecycle states |
| `provenance_tiers` | Visible provenance classes |
| `raw_source_access` | Whether raw source bodies may be returned |
| `foreign_resolution_access` | Which owning authorities may be queried |

The route tenant is a requested scope, not proof of access. The scope resolver intersects it with identity grants. An empty intersection returns `UNAUTHORIZED`; it does not run an unscoped query.

### Membership model

Membership is explicit and multi-valued:

- `OWNED`: the record belongs to the tenant and solution;
- `INHERITED_GLOBAL`: a global record applies through an approved inheritance rule;
- `GOVERNING`: a record governs an owned or inherited record through native graph evidence;
- `REFERENCED`: an owned record refers to it without importing ownership;
- `VISIBLE`: a derived union used only for result construction and accompanied by its basis.

One record may have multiple membership facts. Counts always identify which set is counted and whether the count is unique.

### Enforcement boundary

Repository operations receive the effective scope and revision as mandatory parameters. Queries join or filter by authorized membership before record bodies, snippets, candidates, counts, or adjacency are materialized. Derived services can only operate on the already-authorized snapshot view.

## Canonical Native Graph Contract

### Node representation

Every returned node contains:

- canonical `uri`;
- `type` discriminator;
- owning tenant and solution;
- applicable memberships and their basis;
- lifecycle;
- schema version;
- provenance;
- content hash;
- selected type-specific `data`;
- optional authorized source reference or raw source;
- selected direct-edge summaries when requested.

Unknown future fields remain inside `data`. Unknown future node types can be returned through the generic node envelope even before a client adds type-specific presentation.

### Edge representation

Every returned edge contains:

- stable `edge_id`;
- canonical source and target identifiers;
- verb;
- edge provenance;
- metadata;
- revision;
- endpoint authority classification;
- endpoint resolution state;
- optional verification-evidence references;
- scope or membership basis when relevant.

The graph relationship is canonical. Entity fields such as `governed_by`, `constraints`, `policies`, `quality_slos`, `exported_capabilities`, and `internal_capabilities` are projections generated from or validated against canonical relationships during revision publication.

Publication fails on an unexplained projection mismatch. During migration, unresolved mismatches are quarantined and returned by integrity analysis; they are never silently selected by precedence.

### Declaration and demonstration

A `SATISFIES`, `VERIFIES`, or similar edge states what its provenance says it states. It does not acquire demonstrated status because its endpoints resolve.

Coverage responses separate:

- `declarations`: native relationship edges;
- `evidence_references`: native references declaring what evidence should exist;
- `foreign_observations`: optional, time-bound results from the owning authority;
- `assessment`: deterministic classification such as `DECLARED_ONLY`, `EVIDENCE_REFERENCED`, `DEMONSTRATED_AT_REVISION`, `STALE`, or `CONTRADICTED`;
- `assessment_rule`: versioned rule and inputs used.

NorthStar remains authoritative for the intent and the declaration. CodeMesh remains authoritative for code identity and observed computation evidence.

## Public HTTP Capability API

The conforming contract is introduced under `/api/v2`. Existing `/api/v1` routes remain compatibility endpoints during migration and do not define v2 semantics.

### Common headers

| Header | Requirement |
|---|---|
| `Authorization` | Required except for explicitly configured local development; interpreted by the authentication adapter |
| `X-Request-ID` | Optional caller identifier; validated or generated and always returned |
| `X-Catalog-Revision` | Optional concrete revision or `latest`; body value takes precedence only when the schema explicitly allows it |
| `X-Tenant-ID` | Permitted only on non-hierarchical discovery; tenant-root content routes remain canonical |

### Operation routes

| Logical operation | HTTP capability route | Method |
|---|---|---|
| `describe_authority` | `/api/v2/authority` | `GET` |
| `resolve_references` | `/api/v2/tenants/{tenant}/references:resolve` | `POST` |
| `get_nodes` | `/api/v2/tenants/{tenant}/nodes:batchGet` | `POST` |
| `search_nodes` | `/api/v2/tenants/{tenant}/nodes:search` | `POST` |
| `query_graph` | `/api/v2/tenants/{tenant}/graph:query` | `POST` |
| `find_paths` | `/api/v2/tenants/{tenant}/graph:findPaths` | `POST` |
| `get_governing_context` | `/api/v2/tenants/{tenant}/context:governing` | `POST` |
| `compare_revisions` | `/api/v2/tenants/{tenant}/revisions:compare` | `POST` |
| `analyze_integrity` | `/api/v2/tenants/{tenant}/integrity:analyze` | `POST` |

Colon actions identify bounded capabilities rather than persistence resources. No route accepts SQL, storage predicates, or an unrestricted graph language.

## Common Request Controls

All operations that return content accept applicable forms of:

| Control | Fields |
|---|---|
| `scope` | solutions, include-global policy, lifecycle states, provenance tiers |
| `revision` | concrete revision or `latest` |
| `projection` | selected envelope fields, selected `data` paths, include raw source, include large fields, direct-edge mode |
| `budget` | maximum items, nodes, edges, paths, depth, serialized bytes, and elapsed milliseconds |
| `page` | requested page size and opaque continuation token |
| `foreign_resolution` | `NONE`, `SYNTAX_ONLY`, or explicitly authorized owning authorities |

Caller budgets are ceilings, not demands. The service applies the lower of requested and configured limits and reports both.

Initial safe defaults, advertised dynamically by `describe_authority`, are:

- batch identifiers: 100;
- page size: 50, maximum 200;
- traversal depth: 3, maximum 8;
- traversal nodes: 200, maximum 500;
- traversal edges: 1,000, maximum 2,000;
- paths: 10, maximum 20;
- serialized response: 2 MiB;
- operation deadline: 10 seconds.

These are deployment defaults, not approved SLOs. Load testing may change them without changing semantics.

## Common Result Envelope

Every successful or partial operation returns the same top-level fields:

| Field | Meaning |
|---|---|
| `request_id` | Correlation identifier |
| `operation` | Logical operation name and contract version |
| `status` | `OK`, `PARTIAL`, or `FAILED` |
| `authority` | Always `northstar` for this API |
| `source_kind` | `NATIVE`, `NORMALIZED`, `DERIVED`, or `MIXED` |
| `catalog_revision` | Concrete revision metadata |
| `effective_scope` | Authorized tenant, solution, inheritance, lifecycle, and provenance scope |
| `normalized_query` | Stable machine-readable description of what executed |
| `data` | Operation-specific structured result |
| `completeness` | Complete flag, truncation flag, stopping reason, omitted categories, and unchecked dependencies |
| `page` | Applied size, continuation token, and token expiry when present |
| `limits` | Requested and enforced budgets |
| `statistics` | Returned and inspected counts plus elapsed time |
| `warnings` | Structured non-fatal conditions |
| `errors` | Structured operation or per-item failures |

An error contains stable `code`, safe `message`, affected input reference, retryability, and optional details. Supported codes include invalid input, ambiguous reference, unauthorized, not found, stale revision, unsupported operation, resource limit, timeout, dependency unavailable, and internal failure.

HTTP status reflects the request as a whole. A syntactically valid batch with mixed item outcomes returns a successful HTTP transport status and `PARTIAL`; authentication failure, invalid top-level syntax, or inability to establish an authoritative revision fails the request.

Transport status mapping:

| HTTP status | Use |
|---|---|
| `200` | Complete or partial operation with item-level outcomes in the envelope |
| `400` | Invalid transport syntax, malformed identifier syntax, or invalid continuation token |
| `401` | Missing or invalid authentication |
| `403` | Authenticated caller cannot request the tenant, solution, lifecycle, provenance, raw source, or foreign resolution scope |
| `404` | Tenant-scoped singleton route does not exist or is intentionally indistinguishable from unauthorized under policy |
| `409` | Ambiguous top-level reference or incompatible query/revision state that requires caller choice |
| `410` | Requested revision or continuation is known but no longer retained |
| `413` | Request or projected response cannot fit configured hard limits without a valid bounded form |
| `422` | Syntactically valid request violates operation semantics |
| `429` | Caller or tenant rate/concurrency limit reached |
| `503` | NorthStar cannot establish authoritative repository, revision, schema, or authorization readiness |

Error bodies still use the common envelope where it is safe to construct one. Server errors do not expose stack traces, SQL details, candidate identifiers outside scope, or authentication internals.

## Operation Designs

### 1. `describe_authority`

Behavior:

- resolves the caller's effective discoverable scope without returning unauthorized catalog content;
- reports current and retained revisions;
- returns JSON Schemas for node envelopes, known node types, edges, common results, and operation requests/results;
- reports vocabularies, operations, filters, projections, limits, feature flags, and intentionally unavailable functions;
- reports the service's authority boundary and foreign-authority rules.

The schema registry is generated from the deployed domain and transport models and checked against OpenAPI in CI. Static documentation may explain it but cannot override it.

### 2. `resolve_references`

Input:

- one to 100 identifier strings;
- explicit default solution and version when contextual forms require them;
- selected revision;
- optional foreign-resolution mode.

Output contains one independent result per input with original value, parsed coordinates, canonical form, alias/default basis, candidate list, NorthStar existence status, foreign authority, foreign observation, and errors.

Ambiguous candidates are filtered for authorization before being counted or returned.

### 3. `get_nodes`

Input:

- one to 100 identifiers;
- revision and scope;
- projection;
- direct-edge mode: none, summaries, incoming, outgoing, or both.

Each item returns its own resolution status and node. Full native data is available when requested and authorized. The default projection returns identity, type, title/name, lifecycle, scope, provenance summary, and content hash; large raw ADR or policy bodies require explicit selection.

### 4. `search_nodes`

Search modes:

- `EXACT`: canonical identity or explicitly selected exact fields;
- `STRUCTURED`: composable equality, membership, range, presence, and relationship filters over declared schema fields;
- `LEXICAL`: text matching with matched fields and score explanation;
- `SEMANTIC`: not part of the first conforming release; when added, it is labeled ranking rather than evidence.

The initial implementation uses PostgreSQL-native indexes behind a search-repository port. Exact and structured filters execute before lexical ranking and before snippets are produced. Default results use summary projection and never include raw decision documents.

Search pagination is stable at a revision using a deterministic sort tuple containing explicit sort fields and canonical identity.

### 5. `query_graph`

The bounded query model contains:

- start URIs and/or a structured node-match condition;
- incoming, outgoing, or both directions;
- included and excluded verbs and node types;
- minimum and maximum depth;
- lifecycle, provenance, membership, and solution constraints;
- stop conditions expressed through the same structured match vocabulary;
- requested projection and hard budgets;
- optional continuation.

The result contains deduplicated node bodies keyed by canonical URI, first-class edge objects keyed by `edge_id`, and ordered path references. Parallel edges remain distinct. Traversal records frontier state so continuation does not repeat completed work.

Authorization is applied to the traversable graph. The engine does not traverse through unauthorized nodes even when both visible endpoints would otherwise be returned.

### 6. `find_paths`

Path requests specify source and target URI sets or structured match conditions, direction, allowed verbs/types, maximum length, maximum paths, and revision.

Results preserve ordered node and edge identifiers, then include projected node/edge dictionaries once. Ordering is deterministic by path length, then edge and canonical identifier order. `NO_PATH` is returned only after the authorized bounded graph is exhausted; budget termination returns `INCOMPLETE_LIMIT_REACHED`.

### 7. `get_governing_context`

The operation is implemented as a versioned derivation over native graph and projected-field evidence, not as a separate authority model.

For every included capability, component, decision, invariant, policy, workflow, or quality record, the result includes:

- item identifier and projected native record;
- applicability and lifecycle rule;
- ordered evidence path or exact native field reference;
- membership/inheritance basis;
- derivation-rule identifier and version;
- unresolved expected evidence;
- declaration and demonstration status where relevant.

Compact Markdown is an optional projection generated from the structured result. It lists omitted categories and retains the request, revision, and continuation identifiers.

### 8. `compare_revisions`

Inputs identify two concrete revisions and either a record set, structured match, or bounded graph query. Output separates added, removed, and changed nodes, edges, aliases, and memberships. Changed records include field-level before/after values when both schemas support lossless comparison.

If schemas differ, the comparison reports the schema transition and fields that cannot be compared. Authorization is evaluated independently against both revisions using current access policy; inaccessible historical content is not revealed through differences.

### 9. `analyze_integrity`

The integrity engine runs versioned, read-only rules against one authorized revision. First-release deterministic rules cover:

- dangling internal references;
- unresolved or unchecked foreign references;
- ambiguous aliases;
- invalid node/verb endpoint combinations;
- embedded projection versus canonical-edge disagreement;
- missing required provenance;
- lifecycle and supersession inconsistency;
- component dependency cycles;
- capability declarations without implementation or verification evidence;
- constraints without an applicability or enforcement path;
- tenant and solution membership anomalies;
- contract fields that are missing versus explicitly not applicable.

Each finding contains rule identity and version, severity, epistemic class, affected identifiers, evidence, scope, revision, and remediation guidance. Heuristic rules, if later enabled, are separately requested and labeled `INFERRED`.

## Pagination and Continuation

Continuation tokens are opaque, integrity-protected capabilities containing or referencing:

- operation and contract version;
- concrete catalog revision;
- normalized-query hash;
- effective-scope hash and caller binding;
- deterministic cursor or traversal frontier;
- applied projection and limits;
- issued and expiration times;
- key identifier for rotation.

The token contains no unrestricted record bodies or secrets. Any mismatch in caller, scope, operation, query, revision, or projection returns an invalid-continuation error. Expiration never causes a silent restart at `latest`.

## Evidence, Provenance, and Conflict Handling

NorthStar retains the finest provenance it has and reports its granularity: node, edge, field, document, or import batch. Missing granularity is explicit.

The result vocabulary distinguishes:

- `STORED`: direct snapshot content;
- `NORMALIZED`: canonical representation of stored content;
- `DERIVED`: deterministic rule output with evidence;
- `INFERRED`: heuristic result with confidence and model/rule identity;
- `OBSERVED_FOREIGN`: time-bound response from another authority;
- `AGENT_INTERPRETATION`: never stored or returned as NorthStar authority by this API.

Conflicting stored facts are returned as a conflict set with their provenance. The read API does not choose a winner through undocumented recency, confidence, or source ordering.

## Foreign-Authority Behavior

NorthStar always returns its own authorized edge or field reference even when the foreign endpoint cannot be resolved.

Foreign live resolution is optional and bounded:

1. classify the scheme and owning authority;
2. confirm caller permission for that authority;
3. make a deadline-bounded batched request through the gateway;
4. attach the result as `OBSERVED_FOREIGN` with authority revision and observation time when supplied;
5. preserve `DEPENDENCY_UNAVAILABLE`, `NOT_CHECKED`, and `NOT_FOUND` as distinct states.

Foreign responses are not copied into the NorthStar native node collection. Failure of GroundTruth or CodeMesh cannot turn a successful NorthStar native read into fabricated or missing NorthStar evidence.

## Caching

Immutable revision data may be cached by revision, effective-scope hash, normalized query, and projection. `latest` is never a cache key; it is resolved first. Authorization-sensitive negative results and ambiguity candidates follow the same scope binding.

Caches may improve operation but never become a semantic source. Cache loss changes latency only. Cache contents are not written into exported snapshots or semantic hashes.

## Audit and Observability

Every operation emits an audit event containing:

- request identifier;
- authenticated subject reference;
- logical operation and contract version;
- effective scope hash and non-sensitive scope labels;
- concrete revision;
- requested and applied limits;
- status and structured error codes;
- returned/inspected counts;
- elapsed time and dependency status.

Metrics distinguish exact, structured, lexical, native graph, derived, comparison, and integrity work. Logs never include credentials, raw unrestricted record bodies, or filtered ambiguity candidates.

Health is split:

- liveness: the process can serve;
- readiness: the authoritative PostgreSQL repository, revision catalog, schema registry, and authorization integration are usable;
- dependency status: optional foreign authorities are reported separately and do not determine native-read readiness.

The service does not advertise `status: ok` for authoritative reads when it is operating from a filesystem fallback.

## MCP Mapping

The `tripartite-agent-surface` MCP server remains a separate deployment unit but becomes a thin semantic adapter:

- each MCP tool maps one-to-one to the public v2 capability operation;
- tool input and structured output schemas are generated or contract-tested against the HTTP schemas;
- the MCP process passes the configured credential and never accepts a tool argument that widens its credential scope;
- NorthStar response `status`, `source_kind`, revision, scope, completeness, limits, warnings, and errors are preserved;
- tool descriptions explain selection differences but contain no hidden query policy;
- `compare_revisions` and `analyze_integrity` are registered only after the backend supports them;
- existing adapter-side search, traversal, and path logic is removed after semantic parity tests pass.

Codex, Antigravity, portal, CLI, and automation therefore use the same NorthStar capability contract. Their presentation and transport details may differ; authority behavior may not.

## Backward Compatibility and Migration

### Stage 1: preserve and characterize

- Export the current authoritative PostgreSQL graph and restore it into a clean database.
- Record current nodes, edges, tenant/solution rows, aliases implied by stored URIs, and known projection mismatches.
- Compute a reproducible initial semantic hash.
- Reject migration if record counts or representative closures cannot be reproduced.

### Stage 2: canonicalize without hiding conflict

- Parse every stored identifier under the approved grammar.
- Create canonical rows and explicit aliases for contextual forms.
- Backfill tenant, solution, lifecycle, and membership without using silent defaults.
- Assign stable edge identities and restore stored edge provenance.
- Convert embedded relationships into canonical edges or record quarantined mismatches.
- Publish the result as the first addressable revision.

### Stage 3: introduce v2 shadow reads

- Deploy v2 authority discovery, resolution, and batch node retrieval first.
- Add native search, traversal, and paths.
- Run v1 and v2 against the same catalog and compare intended overlapping semantics.
- Return discrepancies to migration telemetry and integrity reports; do not make v2 emulate known v1 errors.

### Stage 4: add derived operations

- Rebuild governing context over v2 native evidence.
- Add revision comparison and deterministic integrity analysis.
- Validate all twelve acceptance scenarios over direct HTTP.

### Stage 5: migrate consumers

- Switch MCP tools to v2 and run HTTP/MCP semantic conformance tests.
- Move portal and CLI reads to v2.
- Publish v1 deprecation behavior and dates.
- Retain v1 only for explicitly identified consumers during the compatibility window.

### Stage 6: retire unsafe paths

- Remove silent filesystem authority fallback.
- Remove heuristic solution-bundle membership from public behavior.
- Remove full unbounded graph downloads from routine agent workflows; retain an authorized bounded export capability if separately required.
- Remove adapter-side graph derivations after parity is demonstrated.

Rollback returns the current-revision pointer and consumers to the last validated revision and API deployment. It never reverses by reconstructing authority from client caches or unverified files.

## Verification Strategy

### Contract verification

- Generate OpenAPI schemas and compare them with the machine-readable registry.
- Contract-test HTTP and MCP request/result equivalence.
- Test unknown future fields and generic future node types for lossless retrieval.
- Test every common error and partial-success shape.

### Revision verification

- Repeat one query at a fixed revision before and after publication of a new revision.
- Continue a page and traversal after `latest` advances.
- Exercise expired, forged, caller-mismatched, and scope-mismatched tokens.
- Restore the initial revision and reproduce its semantic hash.

### Authorization verification

- Test direct node access, exact search, lexical snippets, counts, ambiguity, traversal, paths, comparison, integrity findings, and continuations across two tenants.
- Verify the engine cannot bridge through an unauthorized intermediate node.
- Verify audit data does not contain filtered bodies or secrets.

### Graph verification

- Preserve parallel, reciprocal, self, internal, and foreign edges.
- Prove embedded projections agree with canonical edges.
- Remove one evidence edge and show the derived closure changes or reports missing evidence.
- Exercise cycles and hard resource limits.

### Epistemic verification

- Confirm a `DECLARED` `SATISFIES` edge remains declared without verification evidence.
- Confirm foreign authority loss changes only foreign observation status.
- Confirm conflicts and unresolved records are returned rather than silently resolved.
- Confirm compact rendering never contains an item absent from the structured result.

### Acceptance traceability

| Acceptance scenario | Primary design sections |
|---|---|
| AS-1 Runtime discovery | Schema registry; `describe_authority` |
| AS-2 Lossless capability retrieval | Native graph contract; `get_nodes` |
| AS-3 Unanticipated graph question | `search_nodes`; `query_graph`; `find_paths` |
| AS-4 Evidence-complete governing context | Evidence assembler; `get_governing_context` |
| AS-5 Ambiguous reference | Canonical resolution; `resolve_references` |
| AS-6 Stable multi-call exploration | Revision model; continuation |
| AS-7 Honest truncation | Request budgets; common envelope; continuation |
| AS-8 External authority unavailable | Foreign-authority behavior |
| AS-9 Authorization isolation | Effective scope; repository enforcement |
| AS-10 No fabricated fallback | Common errors; readiness; migration |
| AS-11 Native and compact views agree | Governing context; MCP mapping |
| AS-12 Declared versus demonstrated coverage | Declaration and demonstration model |

### Requirement traceability

| Requirement group | Design coverage |
|---|---|
| NS-AE-001–006 | Canonical native graph contract and schema registry |
| NS-AE-007–009 | `describe_authority` |
| NS-AE-010–015 | Revision, effective scope, and membership models |
| NS-AE-016–022 | Native operation designs |
| NS-AE-023–028 | Evidence, provenance, conflict, and coverage model |
| NS-AE-029–032 | Foreign-authority behavior |
| NS-AE-033–040 | Projection, pagination, continuation, and budgets |
| NS-AE-041–046 | Common result and error contract |
| NS-AE-047–051 | Authorization enforcement and audit |
| NS-AE-052–056 | Schema registry, MCP mapping, and examples/conformance |

## Operational Considerations

- PostgreSQL authority failure makes the service unready for semantic reads.
- Optional foreign-authority failure is isolated and reported per reference.
- Revision publication and schema migration are observable, atomic operations.
- Search indexes are derived from one revision and must declare freshness against it.
- A search index that does not match the requested revision is unavailable rather than silently queried.
- Large raw source documents require explicit projection and authorization.
- Resource limits are enforced before serialization and echoed in results.
- Backups must include revision, schema-registry, alias, membership, node, and edge tables and must be restore-tested.
- Browser access uses an explicit origin allowlist. Credentialed requests never combine with wildcard origins.
- TLS termination and trusted-forwarded-header handling are deployment responsibilities with explicit trusted-proxy configuration; the application never trusts arbitrary forwarded identity headers.
- Authentication middleware produces verified identity claims. Route handlers and request bodies cannot manufacture or override those claims.
- Per-caller and per-tenant concurrency limits protect the graph and search engines independently from response-size budgets.

## Decisions Made

1. Introduce a versioned `/api/v2` capability surface while preserving `/api/v1` temporarily.
2. Use PostgreSQL immutable semantic snapshots as the initial revision implementation.
3. Resolve `latest` once per request and pass a concrete revision through every subsystem.
4. Make canonical graph edges authoritative; embedded relationship fields are checked projections.
5. Require repository-level scope enforcement before bodies, snippets, counts, or adjacency are materialized.
6. Use exact, structured, and lexical search for the first conforming release; semantic ranking remains deferred.
7. Use opaque integrity-protected continuation tokens bound to caller, scope, revision, query, and projection.
8. Preserve declarations and verification observations as separate result structures.
9. Keep foreign live resolution optional so NorthStar native reads do not depend on another authority's availability.
10. Keep MCP as a thin adapter to the equalized HTTP capability API.

## Decisions Explicitly Deferred

- Authentication provider, token format, and identity-claim mapping.
- Production key management for continuation tokens.
- Revision retention duration and archival storage.
- Final performance SLOs and capacity targets.
- Semantic search and embedding/ranking technology.
- Physical optimization from full snapshots to copy-on-write or interval storage.
- Whether verification evidence becomes a first-class intent node type in a later ontology revision.
- Public mutation, validation, approval, and publication contracts.
- Production deployment topology.

## Production-Gate Questions

- Historical reads use current grants in this release; a separately approved audit use case may introduce historical-grant semantics later.
- Raw ADR, policy, and source content requires the explicit raw-source grant until a finer classification is approved.
- How long must revisions and continuation tokens remain addressable for real agent workflows?
- The first release deterministically materializes ownership and global inheritance; richer human-authored membership bases remain future ontology work.
- Live foreign resolution is not required for the first release. The API must preserve `NOT_CHECKED` and `DEPENDENCY_UNAVAILABLE` honestly until the owning authority surfaces are integrated.
- Which current v1 consumers require a compatibility interval, and for how long?

## CTO Decisions Approved on 2026-09-03

1. Immutable PostgreSQL semantic snapshots are the first revision mechanism.
2. Canonical graph edges are relationship authority; embedded fields are validated projections.
3. Historical reads use current-policy authorization.
4. Exact, structured, and lexical search are sufficient for the first release.
5. The `/api/v2/tenants/{tenant}/...` capability route family and staged v1 migration are approved.
6. Revision retention and final performance targets remain production-release gates; the implementation defaults are not SLOs.
7. Typed foreign-reference status is sufficient for the first release; live foreign resolution remains optional and unavailable until an owning-authority gateway is integrated.

## Decision Record

- The requirements specification is approved as governing product scope.
- The subsystem, revision, scope, relationship, interface, persistence, and migration design is approved for implementation.
- The human CTO explicitly authorized implementation. Formal independent architect and senior implementation-engineer reviews were not performed and must not be inferred from that approval.

## Recommended Next Step

Review this design from two perspectives:

1. architecture fidelity—especially authority, equalized capability access, tenant inheritance, and graph semantics;
2. implementation buildability—especially revision publication, authorization-before-query, migrations, continuation, and failure behavior.

Complete conformance, migration, restart/recovery, and performance evidence, then decide whether the release is fit for production. Implementation status is tracked in [`development-checklist.md`](development-checklist.md).

## Approval Status

approved for implementation on 2026-09-03; production release gates remain open

## Architect Review

Not separately performed. No independent architect approval is claimed. A future review should focus on:

- consistency with accepted ADRs 0001–0006;
- whether internal subsystem boundaries remain inside the NorthStar authority;
- whether relationship and evidence semantics preserve the federation authority split;
- whether any deferred choice is actually architectural and must be decided before approval.

## Senior Implementation Engineer Review

Not separately performed. No independent implementation-engineer approval is claimed. A future review should focus on:

- migration safety from the current tables and in-memory graph;
- buildability of immutable revision snapshots and authorization-first repository calls;
- completeness and consistency of operation schemas;
- continuation, resource-limit, failure-injection, and rollback behavior;
- whether the design leaves adequate implementation discretion.

## CTO Review

Approved by the human CTO on 2026-09-03.

## Sign-Off

### Author

- Signer: Senior Systems Engineer Agent
- Signer Type: agent
- Role: Technical design author
- Review Perspective: systems engineering technical design
- Disposition: submitted-for-review
- Summary Notes: Defines a revision-bound, authorization-first, graph-native NorthStar read API and a thin MCP mapping while preserving accepted authority boundaries.
- Date: 2026-09-03

### Review Entries

- Reviewer: CTO (Human)
- Disposition: approved for implementation
- Evidence: The user stated, "I approve all of the CTO decisions, as you advised. I am good with the technical design."
- Date: 2026-09-03

### CTO Sign-Off

- Signer: CTO (Human)
- Signer Type: human
- Status: approved
- Date: 2026-09-03

### Workflow Status

- Current Status: implementation-approved
