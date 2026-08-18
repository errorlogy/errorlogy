from mas.engine import acc, alpha, fuzzy


def test_acc_clusters(challenger_case):
    modes = fuzzy.score_candidates(challenger_case, top_n=15)
    ar = alpha.propagate(modes)
    result = acc.score_clusters(ar.propagated_mu, challenger_case)
    assert len(result.clusters) >= 1
    assert result.max_contribution_cluster.cluster_id.startswith("ACC")
