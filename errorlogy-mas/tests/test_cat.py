from mas.engine import acc, alpha, cat, fuzzy, pno, t4d, wms


def test_cat_rules(challenger_case):
    w = wms.detect(challenger_case)
    modes = fuzzy.score_candidates(challenger_case, top_n=10)
    ar = alpha.propagate(modes)
    p = pno.score_pno(ar.top_modes, propagated_mu=ar.propagated_mu)
    a = acc.score_clusters(ar.propagated_mu, challenger_case)
    t = t4d.build_topology(challenger_case, w)
    result = cat.evaluate(w, t, p, a)
    assert result.catastrophe_hypothesis.startswith("CAT")
    assert 0.0 <= result.bifurcation_risk <= 1.0
