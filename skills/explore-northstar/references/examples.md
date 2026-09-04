# NorthStar Exploration Examples

## Pin an Investigation

1. Call `describe_authority(tenant="tripartite")`.
2. Copy `catalog_revision.revision_id` into later `revision` inputs.
3. Use `search_nodes(..., include_data=False)` to identify candidates.
4. Expand selected candidates with `get_nodes(..., include_data=True)`.
5. Use `query_graph` or `find_paths` only for the relevant neighborhood.

If a response has `page.continuation`, repeat the same request with that token. Do not change scope, filters, projection, revision, or budgets between pages.

## Resolve Without Overclaiming

Call:

```text
resolve_references(
  references=[
    "req://northstar/discover-solutions",
    "csi://northstar/service.app.create_app",
    "data://logical/northstar/Capability"
  ],
  foreign_resolution="SYNTAX_ONLY"
)
```

Interpret NorthStar `EXISTS` as an existence result. Interpret foreign `NOT_CHECKED` only as classification; it does not establish that CodeMesh or GroundTruth can resolve the identifier.

## Handle Ambiguity

When an item reports `AMBIGUOUS`, use only the returned authorized candidates. Retry with one explicit canonical URI and version. Do not select by list order or apparent recency.

## Handle Partial Success

For batched resolution or retrieval, preserve successful items. Inspect item statuses and top-level `errors`; a top-level `PARTIAL` is not equivalent to total failure.

## Handle Stale Revisions

On `STALE_REVISION`, stop the revision-bound investigation. Ask whether to restart from the new current revision if that would materially change the reasoning. Never repeat silently with `latest`.

## Handle Truncation

- `PAGE_LIMIT` with a continuation: resume the identical query.
- `RESOURCE_LIMIT` without a continuation: the hard total budget was exhausted; narrow the query or deliberately increase the budget.
- `INCOMPLETE_LIMIT_REACHED`: no negative path conclusion is justified.

## Handle Authorization Denial

Treat `UNAUTHORIZED` as the absence of permission, not evidence that a record does or does not exist. Do not infer other-tenant counts or candidates from timing or error wording.

## Handle Foreign Dependency Failure

On `DEPENDENCY_UNAVAILABLE`, retain NorthStar's native edge or field-reference declaration and its provenance. State that foreign existence or current state was not established.

## Distinguish Declaration From Demonstration

A `SATISFIES` edge with `epistemic_status="DECLARED"` records a claim. Report demonstrated coverage only when `coverage.assessment` identifies separate verification evidence at a revision.
