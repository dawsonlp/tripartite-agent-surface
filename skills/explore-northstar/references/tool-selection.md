# NorthStar Tool Selection

## Start here

| Need | Tool | Why |
|---|---|---|
| Learn the live vocabulary and limits | `describe_authority` | Avoid assuming that every declared node type or verb is loaded. |
| Normalize several NorthStar URIs | `resolve_references` | Returns applied defaults and preserves per-item failures. |
| Inspect known records exactly | `get_nodes` | Returns native type-specific data without fuzzy identifier selection. |
| Discover candidate records | `search_nodes` | Combines lexical search with exact structured filters. |
| Explore around one or more records | `query_graph` | Preserves a bounded subgraph rather than reducing it to prose. |
| Establish how two records connect | `find_paths` | Returns ordered nodes and edges as evidence. |
| Get applicable governing intent | `get_governing_context` | Returns a structured derivation with exact path or native-field evidence. |
| Establish what changed | `compare_revisions` | Compares retained semantic snapshots under current authorization. |
| Find catalog defects | `analyze_integrity` | Runs deterministic, versioned rules and returns evidence-bearing findings. |

## Common compositions

### Understand a solution

1. Discover the deployed vocabulary and pin its concrete revision.
2. Search for its components and capabilities.
3. Expand selected components through `query_graph`.
4. Retrieve full records only for the nodes material to the question.

### Explain why code has a structure

1. Get governing context for the `csi://` identifier.
2. Retrieve the returned capabilities, decisions, and constraints.
3. Find or query the supporting paths.
4. Say whether the relationship is merely declared or independently demonstrated.

### Explore possible impact

Traverse in both directions with a strict depth and node budget. Describe the result as graph reachability unless separate evidence establishes actual operational impact.

### Audit a change

1. Compare the explicit before and after revisions.
2. Retrieve full records only for material changes.
3. Run integrity analysis against the after revision.
4. Separate changed declarations, changed evidence references, and independently demonstrated effects.
