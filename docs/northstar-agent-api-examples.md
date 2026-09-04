# NorthStar Agent Exploration API Examples

These examples describe the deployed `/api/v2` read contract. Replace the tenant, identifiers, and revision with values returned by `describe_authority` and `resolve_references`.

Every content response uses the same envelope. Check `status`, `catalog_revision`, `effective_scope`, `completeness`, `page`, `warnings`, and `errors` before interpreting `data`.

## 1. Discover the Authority

```http
GET /api/v2/authority
X-Tenant-ID: tripartite
Authorization: Bearer <credential>
```

Use the returned request schemas, node schemas, vocabularies, permissions, feature availability, limits, and concrete current revision to formulate later calls. The schema is runtime evidence; this document is explanatory only.

## 2. Resolve References

```http
POST /api/v2/tenants/tripartite/references:resolve
Content-Type: application/json

{
  "references": [
    "req://northstar/discover-solutions",
    "req://tripartite:northstar/discover-solutions@latest",
    "csi://northstar/service.app.create_app",
    "data://logical/northstar/Capability"
  ],
  "foreign_resolution": "SYNTAX_ONLY"
}
```

NorthStar proves existence only for its own authorized records. `csi://` and `data://` results identify their owning authority and report `NOT_CHECKED` unless an explicitly authorized live resolution was actually performed. An underspecified NorthStar reference with multiple authorized versions returns `AMBIGUOUS` and candidates; it is never selected by undocumented precedence.

## 3. Retrieve Native Nodes

```http
POST /api/v2/tenants/tripartite/nodes:batchGet
Content-Type: application/json

{
  "revision": "nsr-sha256:<revision>",
  "uris": [
    "req://tripartite:northstar/discover-solutions@latest",
    "decision://global:arch/adr-0002-equal-capability-api@latest"
  ],
  "projection": {
    "include_data": true,
    "data_fields": ["title", "intent", "contract", "governed_by"]
  },
  "direct_edges": "both"
}
```

Node bodies are deduplicated in `data.nodes`; each item refers to one body through `node_ref`. A missing, unauthorized, or malformed item does not discard successful items.

## 4. Search Without Downloading the Graph

```http
POST /api/v2/tenants/tripartite/nodes:search
Content-Type: application/json

{
  "revision": "nsr-sha256:<revision>",
  "query": "provenance",
  "modes": ["STRUCTURED", "LEXICAL"],
  "node_types": ["CapabilitySpec", "InvariantSpec"],
  "has_relationships": ["SATISFIES"],
  "scope": {
    "solutions": ["northstar"],
    "include_global": true
  },
  "projection": {
    "include_data": false
  },
  "page": {
    "size": 25
  }
}
```

Use each `match_reasons` entry to distinguish exact, structured, and lexical matches. Search order is deterministic at the reported revision. Send the returned opaque continuation in an otherwise identical request for the next page.

## 5. Traverse the Native Graph

```http
POST /api/v2/tenants/tripartite/graph:query
Content-Type: application/json

{
  "revision": "nsr-sha256:<revision>",
  "start_uris": ["req://northstar/discover-solutions"],
  "direction": "both",
  "include_verbs": ["SATISFIES", "GOVERNED_BY", "CONSTRAINS"],
  "min_depth": 0,
  "budget": {
    "max_depth": 3,
    "max_nodes": 100,
    "max_edges": 300,
    "max_bytes": 1048576
  },
  "page": {
    "size": 25
  }
}
```

`data.nodes`, `data.edges`, and `data.paths` are separate native structures. A `PAGE_LIMIT` result can be resumed safely. A `RESOURCE_LIMIT` result is incomplete and has no continuation when resuming would violate the request's hard total budget.

## 6. Find Ordered Evidence Paths

```http
POST /api/v2/tenants/tripartite/graph:findPaths
Content-Type: application/json

{
  "revision": "nsr-sha256:<revision>",
  "source_uris": ["csi://northstar/service.app.create_app"],
  "target_uris": ["decision://arch/adr-0002-equal-capability-api"],
  "direction": "both",
  "budget": {
    "max_depth": 5,
    "max_paths": 10
  },
  "page": {
    "size": 5
  }
}
```

`NO_PATH` means the authorized bounded graph was exhausted. `INCOMPLETE_LIMIT_REACHED` means absence was not established. Ordered edge identifiers are evidence of graph reachability, not proof of causation or implementation.

## 7. Derive Governing Context

```http
POST /api/v2/tenants/tripartite/context:governing
Content-Type: application/json

{
  "revision": "nsr-sha256:<revision>",
  "target_uris": ["csi://northstar/service.app.create_app"],
  "projection": {
    "include_data": true,
    "data_fields": ["title", "intent", "decision_outcome", "rule_type"]
  },
  "include_compact_markdown": true
}
```

Every included item has an ordered `path_edge_ids` value or an exact `native_field_reference`. The optional Markdown is a rendering of the structured result; `compact_omissions` says what it left out.

## 8. Compare Revisions

```http
POST /api/v2/tenants/tripartite/revisions:compare
Content-Type: application/json

{
  "before_revision": "nsr-sha256:<before>",
  "after_revision": "nsr-sha256:<after>",
  "node_types": ["CapabilitySpec", "DecisionSpec"],
  "page": {
    "size": 50
  }
}
```

The response separates paged node, edge, alias, and membership changes and reports schema compatibility. Authorization is evaluated using current grants against both historical snapshots.

## 9. Analyze Integrity

```http
POST /api/v2/tenants/tripartite/integrity:analyze
Content-Type: application/json

{
  "revision": "nsr-sha256:<revision>",
  "finding_classes": [
    "RELATIONSHIP_PROJECTION_MISMATCH",
    "CAPABILITY_WITHOUT_VERIFICATION_EVIDENCE"
  ],
  "page": {
    "size": 50
  }
}
```

Integrity findings are deterministic derived evidence. They do not mutate catalog records and are not themselves NorthStar declarations.

## Multi-Call Investigation

1. Call `describe_authority` and retain the concrete revision.
2. Search using that revision and a summary projection.
3. Retrieve only selected candidate bodies at the same revision.
4. Traverse or find paths at the same revision.
5. Use governing context for a convenience closure, preserving its native evidence.
6. If a continuation is returned, repeat the same normalized query with that token. A token started at `latest` remains pinned to its original concrete revision even if a new revision is published.

## Failure and Partial-Result Cases

- `AMBIGUOUS`: inspect authorized candidates and retry with one explicit identifier.
- `NOT_FOUND`: normalization may have succeeded, but existence did not.
- `UNAUTHORIZED`: do not infer what may exist outside the effective scope.
- `STALE_REVISION`: stop or ask the user whether to restart from a newly discovered revision; never silently switch to `latest`.
- `DEPENDENCY_UNAVAILABLE`: NorthStar's own foreign-reference declaration remains usable, but no foreign existence claim was established.
- `PAGE_LIMIT`: continue with the opaque token and otherwise identical request.
- `RESOURCE_LIMIT` or `TIMEOUT`: treat negative conclusions as unproven; narrow scope or revise the explicit budget.
- Mixed item outcomes use `PARTIAL` while preserving successful items.

## Intentional Exclusions

The v2 exploration surface does not authorize catalog mutation, validation execution, approval, publication, semantic ranking, or foreign-authority record retrieval. CodeMesh and GroundTruth will receive separate authority surfaces.
