from mas.engine import acc, alpha, cat, fpd, fuzzy, pno, t4d, wms


def test_fpd_trajectory(challenger_case):
    w = wms.detect(challenger_case)
    modes = fuzzy.score_candidates(challenger_case, top_n=10)
    ar = alpha.propagate(modes)
    p = pno.score_pno(ar.top_modes, propagated_mu=ar.propagated_mu)
    a = acc.score_clusters(ar.propagated_mu, challenger_case)
    t = t4d.build_topology(challenger_case, w)
    c = cat.evaluate(w, t, p, a)
    result = fpd.forecast(ar, w, p, c)
    assert result.horizon in ("near", "short", "medium", "long")
    for mf in result.mode_forecasts:
        assert 0.0 <= mf.mu_forecast <= 1.0
