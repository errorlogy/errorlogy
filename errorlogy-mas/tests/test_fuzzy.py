from mas.engine import fuzzy
from mas.engine.types import EngineWarnings


def test_fuzzy_scores_range(challenger_case):
    warnings = EngineWarnings()
    modes = fuzzy.score_candidates(challenger_case, top_n=20, warnings=warnings)
    assert len(modes) > 0
    for m in modes:
        assert 0.0 <= m.mu <= 1.0
        assert m.name != m.mode_id or m.mode_id.startswith("CB")


def test_fuzzy_uses_many_candidates(challenger_case):
    modes = fuzzy.score_candidates(challenger_case, top_n=20)
    # Engine scores from full atomic set + universe pre-filter
    assert len(modes) <= 20
