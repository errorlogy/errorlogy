from mas.engine import alpha, fuzzy
from mas.schemas.analysis import ModeScore


def test_alpha_propagation_range(challenger_case):
    modes = fuzzy.score_candidates(challenger_case, top_n=10)
    result = alpha.propagate(modes)
    for mu in result.propagated_mu.values():
        assert 0.0 <= mu <= 1.0


def test_alpha_empty_input():
    result = alpha.propagate([])
    assert result.propagated_mu == {}
    assert result.top_modes == []


def test_alpha_graph_used(challenger_case):
    modes = fuzzy.score_candidates(challenger_case, top_n=5)
    result = alpha.propagate(modes)
    assert isinstance(result.activated_edges, list)
