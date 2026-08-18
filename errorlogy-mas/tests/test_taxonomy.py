from mas import taxonomy


def test_taxonomy_loads():
    data = taxonomy.load()
    assert "atomic_modes" in data
    assert len(data["atomic_modes"]) >= 200


def test_mode_ids_unique():
    modes = taxonomy.get_all_atomic_modes()
    ids = [m["id"] for m in modes]
    assert len(ids) == len(set(ids))


def test_alpha_edges_valid():
    edges = taxonomy.get_alpha_edges()
    assert len(edges) > 0
    index = taxonomy.get_mode_index()
    for e in edges[:50]:
        assert "from" in e and "to" in e


def test_acc_archetypes_loaded():
    arch = taxonomy.get_acc_archetypes()
    assert len(arch) >= 1
    assert "signature_modes" in arch[0]
