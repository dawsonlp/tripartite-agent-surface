# NorthStar Result Semantics

## Source kinds

- `NATIVE`: stored NorthStar node or edge facts at the reported revision.
- `NORMALIZED`: canonical identifiers or other lossless normalization.
- `DERIVED`: deterministic output with a rule and supporting evidence.
- `MIXED`: a response that deliberately contains more than one of these classes.

None of these labels alone establishes that referenced code, data, tests, compliance, or realized outcomes were independently verified.

## Revisions

Every successful content operation reports a concrete immutable `revision_id`. Use it for subsequent calls when consistency matters. `latest` is resolved once per request; it is not a session pin. Historical reads are evaluated under the caller's current access policy.

## Foreign references

- `csi://` belongs to Codemesh.
- `data://` belongs to GroundTruth.
- `FOREIGN_NOT_CHECKED` means the owning authority was not queried.
- `DEPENDENCY_UNAVAILABLE` means a requested live check could not reach the owning authority; it does not mean the reference is absent.
- A NorthStar edge to a foreign reference is still valid evidence that NorthStar records the relationship, even when the target is unresolved.

## Completeness

- `OK` means the operation completed within its stated scope and limits.
- `PARTIAL` means useful data exists but some inputs failed or a limit was reached.
- `FAILED` means the request or dependency failed and no plausible fallback was substituted.

Always retain `errors`, `warnings`, `completeness`, effective scope, concrete revision, and continuation fields in downstream reasoning. `NO_PATH` is conclusive only when the authorized bounded graph was exhausted; `INCOMPLETE_LIMIT_REACHED` is not.
