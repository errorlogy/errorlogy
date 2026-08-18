from mas.engine import alpha, fuzzy, pno


def test_pno_scores(challenger_case):
    modes = fuzzy.score_candidates(challenger_case, top_n=10)
    ar = alpha.propagate(modes)
    result = pno.score_pno(ar.top_modes, propagated_mu=ar.propagated_mu)
    assert len(result.scores) == 7
    assert all(0.0 <= v <= 1.0 for v in result.scores.values())
    assert result.dominant_pno.startswith("PNO-")


def test_pno_id_normalization():
    assert pno.display_pno_id("PNO-001") == "PNO-1"
    assert pno.display_pno_id("PNO-7") == "PNO-7"
    assert pno.taxonomy_pno_id("PNO-1") == "PNO-001"
    assert pno.taxonomy_pno_id("PNO-007") == "PNO-007"
