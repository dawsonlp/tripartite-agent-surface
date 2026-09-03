# NorthStar Result Semantics

## Source kinds

- `live_api`: returned directly by a current NorthStar read operation.
- `derived_from_live_graph`: deterministically computed by the agent adapter from one fetched graph.
- `live_api_derived_closure`: computed by NorthStar's current closure implementation.

None of these labels alone establishes that referenced code, data, tests, compliance, or realized outcomes were independently verified.

## Revisions

The current API does not expose an authoritative catalog revision. The adapter returns a `derived-sha256` digest for operations based on a single full-graph response. The digest identifies equal serialized graph content; it is not a durable historical revision and cannot support historical comparison.

## Foreign references

- `csi://` belongs to Codemesh.
- `data://` belongs to GroundTruth.
- `not_checked` means the owning authority was not queried.
- A NorthStar edge to a foreign reference is still valid evidence that NorthStar records the relationship, even when the target is unresolved.

## Completeness

- `ok` means the operation completed within its stated scope and limits.
- `partial` means useful data exists but some inputs failed or a limit was reached.
- `not_found` means requested exact native nodes were not present in the fetched graph.
- `error` means the request or dependency failed and no plausible fallback was substituted.

Always retain `limitations`, `errors`, `complete`, `truncated`, and continuation fields in downstream reasoning.
