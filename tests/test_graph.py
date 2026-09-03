from tripartite_agent_surface.graph import bounded_subgraph, find_paths_in_graph, matching_nodes


GRAPH = {
    "nodes": {
        "req://demo/checkout": {
            "type": "CapabilitySpec",
            "data": {"title": "Checkout", "lifecycle": "ACTIVE", "tags": ["sales"]},
        },
        "decision://demo/adr-001-choice": {
            "type": "DecisionSpec",
            "data": {"title": "Choose a boundary", "status": "ACTIVE", "tags": []},
        },
        "constraint://demo/no-leak": {
            "type": "InvariantSpec",
            "data": {"title": "No tenant leak", "status": "ACTIVE", "tags": ["security"]},
        },
    },
    "edges": [
        {"source": "req://demo/checkout", "verb": "GOVERNED_BY", "target": "decision://demo/adr-001-choice"},
        {"source": "constraint://demo/no-leak", "verb": "CONSTRAINS", "target": "req://demo/checkout"},
        {"source": "csi://demo/checkout", "verb": "SATISFIES", "target": "req://demo/checkout"},
    ],
}


def test_search_preserves_native_records_and_filters():
    matches = matching_nodes(
        GRAPH,
        query="tenant",
        node_types=["InvariantSpec"],
        lifecycle_states=["ACTIVE"],
        tags=["security"],
        uri_prefix="constraint://",
    )
    assert [match["uri"] for match in matches] == ["constraint://demo/no-leak"]


def test_bounded_subgraph_preserves_external_references():
    result = bounded_subgraph(
        GRAPH,
        start_uris=["req://demo/checkout"],
        direction="both",
        verbs=None,
        node_types=None,
        max_depth=1,
        max_nodes=10,
    )
    assert result["complete"] is True
    assert "csi://demo/checkout" in result["external_references"]
    assert len(result["edges"]) == 3


def test_find_paths_returns_ordered_evidence():
    result = find_paths_in_graph(
        GRAPH,
        source_uri="constraint://demo/no-leak",
        target_uri="decision://demo/adr-001-choice",
        direction="outgoing",
        verbs=None,
        max_depth=3,
        max_paths=3,
    )
    assert result["paths"][0]["nodes"] == [
        "constraint://demo/no-leak",
        "req://demo/checkout",
        "decision://demo/adr-001-choice",
    ]
