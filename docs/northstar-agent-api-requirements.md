# NorthStar Agent Exploration API Requirements

## Purpose

Define the product requirements for a read-only, agent-facing NorthStar exploration API.

The API must let an AI agent inspect NorthStar as the intent graph that it actually is: typed intent nodes, typed relationships, nested operational contracts, lifecycle, provenance, versions, solution and tenant scope, and references to external authorities. It must also support efficient higher-level questions without replacing the underlying graph with summaries that hide evidence, ambiguity, or incompleteness.

This document defines what an agent must be able to learn and the behavioral contract the API must satisfy. It does not select HTTP, MCP, GraphQL, a query language, storage technology, indexing technology, or implementation structure.

## Scope

### In scope

- Read-only exploration of NorthStar's intent and governance authority.
- Discovery of the currently available ontology, scopes, revisions, and query capabilities.
- Lossless retrieval of native intent nodes and relationship edges.
- Structured search, filtering, traversal, path finding, and bounded subgraph retrieval.
- Exploration of capabilities, components, workflows, decisions, invariants, policies, quality requirements, and future NorthStar node types.
- Exploration of operational contracts, information dependencies, failure modes, actor grants, component boundaries, decision rationale, constraints, lifecycle, and provenance.
- Navigation from NorthStar records to referenced CodeMesh and GroundTruth identifiers without claiming authority over those external records.
- Derived exploratory views such as governing context, decision lineage, impact, coverage, and integrity findings, provided their supporting graph evidence is returned.
- Efficient use by an LLM through batching, pagination, projections, context budgets, stable schemas, and explicit completeness signals.
- Explicit authorization and tenant/solution scoping for every request.

### Out of scope for this requirements version

- Creating, editing, deleting, approving, superseding, or publishing intent.
- Executing invariant validators against proposed code or data changes.
- Applying code changes, schema changes, or policy changes.
- Defining GroundTruth information semantics or Codemesh computation semantics.
- Choosing the transport protocol or deployment topology.
- Choosing a graph query language, search engine, database, embedding model, or cache.
- Designing the eventual agent-facing mutation and approval workflow.

## Inputs Consulted

- The user's direction that agents should have close-to-native access to NorthStar without being boxed into a narrow collection of predetermined workflows.
- `PROJECT_ANALYSIS.md` and `development-checklist.md`.
- `skills/tripartite-solution-design/SKILL.md`.
- NorthStar's README, ADRs, design documentation, federation documentation, and requirements-authority specification.
- NorthStar's current entity, contract, provenance, URI, graph, query, catalog, validation, persistence, and service code.
- NorthStar's live OpenAPI document and live read-only graph responses on 2026-09-03.

## Governing Inputs

- NorthStar is the authority for intent, requirements, architectural decisions, policies, quality requirements, and constraints.
- NorthStar does not become the authority for code structure or information meaning merely because it references `csi://` or `data://` identifiers.
- Observation must be distinguishable from derivation, inference, and proposal.
- An agent must be able to inspect the native evidence behind any convenient summary or conclusion.
- The initial agent API is read-only.
- Tenant, solution, version, lifecycle, and provenance boundaries must be explicit rather than inferred from display labels or URI substrings.

## Supporting Context

The live NorthStar service reported 84 nodes and 82 edges during inspection. The live node types were `CapabilitySpec`, `ComponentSpec`, `DecisionSpec`, and `InvariantSpec`; the declared model also includes workflows, policies, and quality specifications. The live edge verbs were `SATISFIES`, `GOVERNED_BY`, `REQUIRES`, and `CONSTRAINS`; the declared relational vocabulary is broader.

The current full-graph response is the closest existing interface to native graph access. Other responses provide useful preassembled views, but the live OpenAPI document declares request schemas without declaring corresponding typed response schemas.

The live solution summaries can include overlapping records and collectively report more memberships than the number of unique graph nodes. An agent therefore cannot safely treat a solution label as proof of exclusive or canonical membership. This document requires the service to explain membership and inheritance rather than leaving the agent to infer them.

The existing `IntentClosure` Markdown rendering is useful for prompt injection, but it is a lossy presentation. It is not a substitute for structured nodes, edges, derivation paths, revision identity, and completeness metadata.

## Decisions Made

1. The primary product is an explorable intent graph, not a collection of canned summaries.
2. Native graph primitives and derived convenience operations will coexist.
3. Derived results must identify the records and traversals that justify them.
4. The API must support unanticipated exploration by composing a small set of expressive operations rather than adding one endpoint for every anticipated question.
5. The API must expose the ontology and available capabilities at runtime; agents must not need a permanently hard-coded copy of NorthStar's vocabulary.
6. Full-fidelity structured data is canonical for agent use. Human-readable renderings are optional projections.
7. Every multi-call exploration must be able to bind to a stable catalog revision or snapshot.
8. Exact, lexical, and inferred/semantic matches must remain distinguishable.
9. An empty result, unresolved reference, incomplete traversal, or unsupported operation must be reported honestly and must never be replaced with plausible example data.
10. Read-only exploration is separated from validation and mutation so it can receive durable approval without silently authorizing state changes.

## Primary User

The primary user is an AI agent that must understand why a system exists, what behavior it promises, what governs it, how intent records relate, what evidence supports a conclusion, and where the intent graph is incomplete or contradictory.

Human architects and product owners are secondary users who must be able to inspect the same evidence and reproduce the agent's reasoning.

## Required User Outcomes

An authorized agent must be able to:

1. Discover what NorthStar contains before choosing a query.
2. Obtain an accurate map of a tenant, solution, component, or selected subgraph.
3. Retrieve one or many native records without losing type-specific fields.
4. Search by identifiers, titles, text, tags, type, lifecycle, provenance, scope, and relationship characteristics.
5. Start at any known NorthStar or external reference and explore connected intent in either direction.
6. Ask why a capability, component, constraint, or decision exists and receive its governing evidence.
7. Inspect operational contracts, data operations, failure modes, authorization intent, and quality expectations without parsing prose-only summaries.
8. Trace decision succession, refinement, conflicts, dependencies, satisfaction, verification, and constraint relationships.
9. Determine what may be affected when an intent record or referenced external artifact changes.
10. Identify missing, dangling, contradictory, stale, unimplemented, unverified, or otherwise incomplete intent relationships.
11. Compare two catalog revisions or two versions of an intent record.
12. Build compact context for another reasoning or coding task while retaining a path back to full evidence.
13. Know what the service did not inspect, could not resolve, or had to infer.

## Use-Case Inventory

| Use case | Example request | Successful result |
|---|---|---|
| Authority discovery | "What kinds of intent and relationships can NorthStar currently answer questions about?" | Current node types, edge verbs, fields, scopes, revisions, supported operations, limits, and authorization context. |
| Solution orientation | "Map the NorthStar solution for me." | A bounded subgraph with explicit membership reasons, important entry points, counts, and no duplicate records disguised as unique members. |
| Native record inspection | "Show the complete capability contract for resolving governing intent." | Lossless typed capability data, nested contract fields, provenance, lifecycle, revision, and directly connected edges. |
| Concept search | "Find intent concerning tenant isolation, even if it uses different wording." | Separately identified exact, lexical, and semantic matches with scores or match reasons and stable identifiers. |
| Relationship exploration | "What directly governs this component, and what does it govern?" | Incoming and outgoing typed edges, adjacent records, endpoint resolution state, and scope. |
| Open-ended traversal | "Explore outward from this decision until you reach capabilities or code references." | A bounded, reproducible traversal with paths, stopping reasons, truncation state, and continuation support. |
| Governing context | "What requirements, decisions, policies, and constraints apply to this code symbol?" | A convenient closure plus every supporting edge/path and explicit rules used to include each result. |
| Decision rationale | "Why was this architectural choice made, what alternatives were rejected, and what replaced it?" | Native decision content, consequences, alternatives, lifecycle, and complete supersession lineage. |
| Contract analysis | "What must be true before and after this capability, and how can it fail?" | Structured preconditions, postconditions, state transitions, failure modes, recovery expectations, and actor grants. |
| Information dependency | "Which capabilities read or mutate this GroundTruth entity?" | Referencing capabilities, operation type, supporting native fields or graph edges, and unresolved external status. |
| Coverage analysis | "Which active capabilities have no satisfying code or verifying tests?" | Reproducible gap set, criteria used, supporting absence checks, revision, and known blind spots. |
| Conflict analysis | "Are any active requirements or policies in conflict?" | Declared conflicts separated from newly inferred candidates, with evidence and confidence. |
| Impact analysis | "If this decision changes, what intent and external references could be affected?" | Directionally explained paths, bounded blast radius, categories of impact, and no claim that reachability proves actual consequence. |
| Revision comparison | "What changed in NorthStar since the last accepted revision?" | Added, removed, and changed nodes and edges with before/after values and lifecycle/provenance changes. |
| Integrity audit | "Where is the graph internally incomplete or ambiguous?" | Dangling references, invalid endpoints, ambiguous resolution, inconsistent embedded links, missing provenance, cycles, and scope anomalies. |
| Context preparation | "Give me the smallest evidence-complete context needed to work on this symbol." | Token-bounded structured context, omitted-section summary, continuation handles, and evidence references. |

This inventory is not intended to enumerate every phrasing or future question. The composable primitives below must allow agents to pursue reasonable new questions without requiring a new endpoint for each one.

## Required Logical API Surface

Operation names below express the required logical contract. Their final protocol names and transport mapping are deferred.

### 1. `describe_authority`

Allows the agent to discover:

- NorthStar's authority boundary;
- available tenants, solutions, global scopes, and inheritance rules;
- current catalog revision and available historical revisions;
- supported node types, field schemas, edge verbs, lifecycle values, and provenance vocabulary;
- supported query, search, traversal, rendering, and comparison capabilities;
- result-size, traversal, timeout, and context limits;
- the caller's effective read scope;
- intentionally unsupported capabilities.

This operation must describe the live service rather than repeat a static marketing description.

### 2. `resolve_references`

Resolves one or many supplied identifiers without requiring the agent to guess canonical forms.

For each input it must return:

- the original value;
- canonical identifier, if uniquely resolvable;
- parsed coordinates;
- record type, if known;
- tenant, solution, and version scope;
- exact, defaulted, alias, or ambiguous resolution status;
- all candidates when resolution is ambiguous;
- external-authority status for `csi://`, `data://`, or future foreign identifiers;
- a structured reason when resolution fails.

The service must not silently choose among ambiguous candidates.

### 3. `get_nodes`

Retrieves one or many nodes by stable identifier at a selected revision.

The caller must be able to request:

- full native data;
- selected fields;
- type-specific nested fields;
- directly connected edge summaries;
- raw authoritative source content when available and authorized;
- source location or source reference when available;
- inclusion or exclusion of deprecated, superseded, proposed, or inferred records.

Batch retrieval is required to reduce round trips. Each requested identifier must receive an independent result status.

### 4. `search_nodes`

Searches native records using composable filters. The supported filter dimensions must include:

- tenant and solution scope;
- node type;
- lifecycle state;
- provenance tier and confidence;
- URI and identifier;
- title and textual content;
- tags;
- type-specific fields such as component, rule type, metric, compliance framework, operated entity, actor role, or failure code;
- presence or absence of selected fields or relationships;
- revision or time boundary.

The agent must be able to distinguish exact identifier matching, structured filtering, lexical text matching, and semantic ranking. Semantic ranking, if supported, must be labeled as a ranking aid rather than authoritative evidence.

### 5. `query_graph`

Performs a bounded declarative query over the native graph. It must allow the caller to combine:

- one or many starting identifiers or node-match conditions;
- incoming, outgoing, or either-direction traversal;
- allowed or excluded edge verbs;
- allowed or excluded node types;
- minimum and maximum traversal depth;
- tenant, solution, lifecycle, provenance, and revision constraints;
- stop conditions;
- node, edge, path, and total-result limits;
- requested result projection;
- continuation from a truncated result.

The result must preserve nodes, edges, and paths as separate structured collections. It must not flatten the graph into prose or lose parallel relationships between the same endpoints.

### 6. `find_paths`

Finds one or more bounded paths between sets of identifiers or match conditions.

The caller must be able to constrain direction, verbs, node types, scope, lifecycle, path length, and number of returned paths. Every path must preserve ordered nodes and edges. The response must distinguish "no path exists in the selected revision and scope" from "the search limit was reached before a path was found."

### 7. `get_governing_context`

Returns a convenient, compact view of applicable intent for one or many targets. Targets may be NorthStar identifiers or foreign references.

The response must include:

- relevant capabilities, components, decisions, invariants, policies, workflows, and quality requirements;
- the exact graph path or native field reference that caused each item to be included;
- applicability rules and lifecycle filtering;
- unresolved or missing expected references;
- catalog revision and scope;
- structured data as the canonical result;
- optional compact human-readable rendering;
- completeness and truncation state.

This operation may simplify a common task but must not be the only way to explore governing intent.

### 8. `compare_revisions`

Compares two catalog revisions, two versions of selected records, or two bounded subgraphs.

It must return:

- added, removed, and changed nodes;
- added, removed, and changed edges;
- field-level before/after differences where supported;
- lifecycle and provenance changes;
- changed external references;
- scope and filtering used for the comparison;
- records that could not be compared losslessly.

### 9. `analyze_integrity`

Performs read-only integrity and coverage checks against a selected scope and revision.

The supported finding classes must include:

- dangling internal references;
- unresolved external references;
- ambiguous identifiers;
- invalid type/verb endpoint combinations;
- inconsistent duplicated relationships between embedded fields and graph edges;
- missing or insufficient provenance;
- invalid lifecycle or supersession chains;
- component dependency cycles;
- capabilities with no declared implementation or verification evidence;
- constraints with no observable applicability or enforcement path;
- solution membership or tenant-scope anomalies.

Each finding must state whether it is directly observed, deterministically derived, or heuristically inferred. It must include supporting records and the rule used.

## Functional Requirements

### Native graph fidelity

- **NS-AE-001:** The API must expose every authorized native NorthStar node type without reducing all nodes to a common lossy summary.
- **NS-AE-002:** Every node result must include a stable identifier, explicit type discriminator, lifecycle, provenance, scope, schema version, and all requested type-specific fields.
- **NS-AE-003:** The API must expose every authorized relationship as a first-class edge with source, verb, target, provenance, metadata, resolution state, and revision identity.
- **NS-AE-004:** Parallel edges, reciprocal edges, self-edges, and foreign endpoints must be preserved rather than deduplicated by display text.
- **NS-AE-005:** Nested structures—including operational contracts, operated entities, failure modes, actor grants, workflow steps, component dependencies, decision consequences, and invariant expressions—must remain structured.
- **NS-AE-006:** Unknown future node fields, edge metadata, node types, or verbs must be discoverable and retrievable without being silently discarded by older generic exploration clients.

### Schema and capability discovery

- **NS-AE-007:** The agent must be able to retrieve the live node schemas, edge vocabulary, lifecycle vocabulary, provenance vocabulary, and supported query features before querying content.
- **NS-AE-008:** Schema descriptions must explain field meaning, cardinality, requiredness, allowed values, reference targets, and whether a value is native, defaulted, normalized, or derived.
- **NS-AE-009:** The capability description must identify operations and result features unavailable in the current deployment.

### Scope and revision correctness

- **NS-AE-010:** Every content query must execute against an explicit effective tenant scope, solution scope, global-inheritance policy, and catalog revision.
- **NS-AE-011:** Omitted scope values may use documented defaults only when the response reports exactly which defaults were applied.
- **NS-AE-012:** Solution membership must be explicit and must include its basis, such as direct ownership, inherited global applicability, relationship reachability, or a derived projection.
- **NS-AE-013:** A solution summary must distinguish unique records from inherited, shared, or multiply classified records.
- **NS-AE-014:** Multi-call exploration must support a stable revision token so records cannot silently change midway through the agent's reasoning.
- **NS-AE-015:** When a requested revision is unavailable or has expired, the API must return a structured stale or unavailable result rather than substituting the latest revision.

### Retrieval, search, and composition

- **NS-AE-016:** All identifier-based retrieval must support batches with independent per-item statuses.
- **NS-AE-017:** Search filters must be composable rather than limited to one predetermined field or node type.
- **NS-AE-018:** Search must return match reasons and must distinguish authoritative stored fields from inferred relevance rankings.
- **NS-AE-019:** Graph traversal must support multiple starting points, both directions, typed edge filters, node filters, bounded depth, stop conditions, and hard resource limits.
- **NS-AE-020:** Path results must preserve the ordered evidence connecting their endpoints.
- **NS-AE-021:** The agent must be able to request native primitives directly even when a higher-level convenience operation exists.
- **NS-AE-022:** Derived operations must be composable with subsequent native retrieval or traversal using stable identifiers and revision tokens.

### Evidence, provenance, and epistemic status

- **NS-AE-023:** Every returned fact must retain the finest provenance granularity available from the authoritative source, and the response must disclose that granularity.
- **NS-AE-024:** A result must distinguish stored facts, normalized representations, deterministic derivations, heuristic inferences, and agent-authored interpretations.
- **NS-AE-025:** A derived result must identify its derivation rule and supporting nodes, fields, edges, and paths.
- **NS-AE-026:** Reachability must not be presented as proof of causation, satisfaction, compliance, implementation, verification, or realized impact.
- **NS-AE-027:** Declared `SATISFIES`, `VERIFIES`, or similar edges must be returned as declarations with provenance; the API must not relabel them as independently validated facts unless separate validation evidence exists.
- **NS-AE-028:** Conflicting facts must be returned as conflicts rather than resolved by undocumented precedence.

### External references and authority boundaries

- **NS-AE-029:** NorthStar must expose references to CodeMesh, GroundTruth, and other authorities as typed foreign references without copying foreign records into NorthStar's authority.
- **NS-AE-030:** Each foreign reference must report whether it is syntactically valid, known to NorthStar, resolved by its owning authority, unresolved, stale, or not checked.
- **NS-AE-031:** Failure or unavailability of another authority must not cause NorthStar to fabricate or silently cache an authoritative-looking foreign result.
- **NS-AE-032:** An agent must be able to retrieve the NorthStar records that refer to a foreign identifier even when the foreign authority is unavailable.

### Agent efficiency and context control

- **NS-AE-033:** The API must support field projection so the agent can request identifiers and summaries first, then expand selected records.
- **NS-AE-034:** List, search, traversal, path, comparison, and audit results must support pagination or continuation.
- **NS-AE-035:** Responses must report truncation, omitted categories, continuation state, and the limits that caused termination.
- **NS-AE-036:** The agent must be able to supply result-size and traversal budgets. The service must enforce server-side maximums even when larger values are requested.
- **NS-AE-037:** Common multi-record operations must support batching to minimize tool calls and repeated serialization.
- **NS-AE-038:** Structured data must be canonical. Compact Markdown or other text renderings may be requested as optional projections and must identify omitted information.
- **NS-AE-039:** Responses must avoid repeating identical node bodies for every path; stable references may be used when a node is already present in the response.
- **NS-AE-040:** Large native fields such as raw decision documents must be independently selectable so their size does not crowd out graph structure.

### Completeness and failure behavior

- **NS-AE-041:** Every response must state whether it is complete for the stated query, scope, revision, and limits.
- **NS-AE-042:** Empty results must be returned as valid empty results with applied filters, not as generic errors or examples.
- **NS-AE-043:** Partial success must preserve successful items and provide structured failure information for unsuccessful items.
- **NS-AE-044:** Error classes must distinguish invalid input, ambiguous reference, unauthorized scope, not found, stale revision, unsupported operation, resource limit, timeout, dependency unavailable, and internal failure.
- **NS-AE-045:** No error or dependency failure may produce plausible substitute graph content.
- **NS-AE-046:** Repeating the same read at the same revision and scope must produce semantically equivalent results, excluding explicitly identified operational metadata.

### Authorization and read safety

- **NS-AE-047:** The server must enforce the caller's tenant, solution, lifecycle, and source-content access before retrieving or deriving results.
- **NS-AE-048:** Caller-supplied scope labels must never be sufficient authorization and must not relabel records from another scope.
- **NS-AE-049:** Aggregate counts, search snippets, errors, inferred matches, and continuation state must not leak unauthorized records.
- **NS-AE-050:** Every operation in this version must be free of catalog, source, cache-visible semantic, or external side effects.
- **NS-AE-051:** Exploration requests must be auditable by caller, operation, effective scope, revision, limits, and result status without logging secrets or unrestricted record bodies.

### Agent comprehension and portability

- **NS-AE-052:** Each operation must have a concise purpose, selection guidance, input contract, output contract, limits, side-effect classification, and representative examples.
- **NS-AE-053:** Similar operations must explain their distinctions, especially native graph retrieval versus derived governing context or integrity analysis.
- **NS-AE-054:** The complete operation and schema contracts must be machine-readable.
- **NS-AE-055:** The semantic contract must remain usable across agent clients and must not depend on one model understanding undocumented server conventions.
- **NS-AE-056:** The service must provide direct and indirect example requests for every supported use-case class and must identify intentional exclusions.

## Common Result Requirements

Every successful or partially successful operation must return or make available:

- request identifier;
- effective caller scope;
- effective tenant and solution scope;
- catalog revision or snapshot identifier;
- operation and normalized query description;
- structured result data;
- completeness status;
- applied defaults;
- warnings and unresolved references;
- pagination or continuation information;
- derivation and evidence information when the result is not a direct native read;
- response statistics sufficient to understand result size and limits.

The response must not require the agent to parse prose to determine whether it is complete, current, scoped correctly, or based on inference.

## Acceptance Scenarios

### AS-1: Runtime discovery

Given a newly connected agent with no hard-coded NorthStar vocabulary, when it asks what the authority supports, it can discover all live node types, verbs, lifecycle values, scopes, schemas, operations, and limits in machine-readable form.

### AS-2: Lossless capability retrieval

Given a capability with preconditions, postconditions, state transitions, failure modes, actor grants, operated entities, governance references, lifecycle, and provenance, the agent can retrieve all fields without consulting a raw database or source file.

### AS-3: Unanticipated graph question

Given a question not represented by a dedicated convenience operation, the agent can express it through bounded search and graph traversal, receive paths and native records, and continue the exploration without a new server release.

### AS-4: Evidence-complete governing context

Given a code or data reference, the agent can request governing context and trace every included requirement, component, decision, constraint, policy, workflow, or quality item back through returned native fields or graph edges.

### AS-5: Ambiguous reference

Given an underspecified identifier matching multiple versions or scopes, the API returns all candidates and does not silently select one.

### AS-6: Stable multi-call exploration

Given a revision token from an initial query, subsequent retrieval, traversal, and comparison calls observe that revision or explicitly report that it is no longer available.

### AS-7: Honest truncation

Given a traversal larger than the requested budget, the API returns the bounded result, explains which limit stopped it, reports that the result is incomplete, and provides continuation where safe.

### AS-8: External authority unavailable

Given a NorthStar edge referring to CodeMesh or GroundTruth while that authority is unavailable, the agent still receives the NorthStar edge and its provenance, with the foreign endpoint marked `not_checked` or `dependency_unavailable` rather than missing or falsely resolved.

### AS-9: Authorization isolation

Given credentials for Tenant A, search, counts, traversal, ambiguity candidates, errors, and derived analyses reveal no Tenant B records.

### AS-10: No fabricated fallback

Given an empty, stale, invalid, unsupported, or failed query, the response contains no example or seed result presented as live authority data.

### AS-11: Native and compact views agree

Given a compact governing-context rendering, every represented item exists in the accompanying structured result or can be retrieved at the same revision, and every omission is identified by category.

### AS-12: Declared versus demonstrated coverage

Given a declared `SATISFIES` or `VERIFIES` relationship, the API reports the declaration and provenance separately from any independent validation evidence, allowing the agent to avoid treating assertion as proof.

## Success Criteria

The requirements are satisfied when:

- an agent can orient itself without reading NorthStar source code;
- an agent can inspect the complete authorized native graph through bounded operations;
- common questions require few round trips but retain evidence;
- novel graph questions can be expressed through composable primitives;
- all results identify scope, revision, provenance, completeness, and derivation status;
- no derived view prevents access to the underlying graph evidence;
- unauthorized or unavailable information is not leaked or fabricated;
- a conformance suite verifies the acceptance scenarios with representative, empty, ambiguous, stale, unauthorized, truncated, and dependency-failure cases.

## Decisions Explicitly Deferred

- Whether the agent interface is delivered through MCP, HTTP, both, or another protocol.
- Whether NorthStar exposes the interface directly or through an adapter.
- Final operation and tool names.
- The concrete graph-query representation or language.
- Storage, search, indexing, caching, and snapshot implementation.
- Whether semantic search is implemented and, if so, which ranking technology it uses.
- Exact pagination and continuation representation.
- Exact compact-rendering formats.
- Performance targets and service-level objectives.
- Historical retention duration and revision-token lifetime.
- Whether field-level provenance is added where the current model only has node- or edge-level provenance.
- Mutation, validation, approval, and publication APIs.
- Cross-authority orchestration beyond reporting and resolving foreign references.

## Open Questions

- What constitutes the authoritative catalog revision when NorthStar has both a live database and repository exports?
- Is solution membership an owned property, a derived classification, a graph projection, or some combination of these?
- May one node be a first-class member of multiple solutions, and how should counts represent that?
- What are the precise rules for inheriting global intent into a tenant and solution query?
- Which lifecycle states should be included by default for agents?
- Which provenance classes are visible by default, especially inferred and proposed records?
- Is the raw authoritative source for an ADR or policy part of NorthStar's readable authority, or only a referenced external artifact?
- What evidence is sufficient to distinguish a declared satisfaction or verification relationship from a demonstrated one?
- How long must a revision remain addressable for multi-step agent work?
- Which integrity checks are authoritative deterministic rules, and which are advisory heuristics?

## Questions For CTO

1. Do you approve read-only agent exploration as the complete scope of the first NorthStar agent API release?
2. What source and revision mechanism is authoritative for a read: live PostgreSQL state, accepted repository state, or a named snapshot?
3. What are the canonical solution-membership and global-inheritance rules?
4. Should external `csi://` and `data://` references appear as foreign graph endpoints even when their owning authority cannot resolve them?
5. Should inferred and proposed intent be visible by default, visible only when requested, or excluded from the initial release?
6. Does NorthStar need provenance below node and edge granularity before this API can be considered trustworthy?
7. Is semantic search required in the first release, or are exact, structured, and lexical search sufficient initially?
8. What revision-retention and latency targets should become acceptance gates?
9. Which source documents may be returned in full, and which require separate access controls?
10. Should coverage and integrity operations be part of the first release, or should the first release contain only native retrieval and traversal primitives?

## Decisions Requested

- Approve the read-only exploration boundary.
- Approve graph-native primitives plus evidence-backed derived views as the product shape.
- Define the authoritative revision and snapshot semantics.
- Define tenant, solution-membership, and global-inheritance semantics.
- Define default lifecycle and provenance visibility.
- Decide whether semantic search and integrity analysis belong in the first release.
- Define which raw sources are within NorthStar's readable authority.

## Recommended Next Step

Implement and verify the approved technical design, then use the conformance record to separate behavior proven in this release from production gates that remain open. The implementation must not reduce the design to one-for-one wrappers over the old REST endpoints or import authority from GroundTruth or CodeMesh.

## Approval Status

approved as the governing product scope on 2026-09-03

## Architect Review

Not separately performed. No independent architect review is claimed.

## CTO Review

Approved by the human CTO on 2026-09-03 together with the recommended technical-design decisions.

## Sign-Off

### Author

- Signer: Product Owner Agent
- Signer Type: agent
- Role: Requirements author
- Review Perspective: requirements drafting for agent-native NorthStar exploration
- Disposition: submitted-for-review
- Summary Notes: Defines a read-only, graph-native, evidence-preserving exploration contract while deferring transport and implementation decisions.
- Date: 2026-09-03

### Review Entries

- Reviewer: CTO (Human)
- Disposition: approved
- Evidence: The user stated, "I approve all of the CTO decisions, as you advised. I am good with the technical design."
- Date: 2026-09-03

### CTO Sign-Off

- Signer: CTO (Human)
- Signer Type: human
- Status: approved
- Date: 2026-09-03

### Workflow Status

- Current Status: approved
