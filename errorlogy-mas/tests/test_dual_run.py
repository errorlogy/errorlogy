from mas.dual_run import apply_dual_run_flags, compute_dual_run_diff, dual_run_red_team_hints
from mas.schemas.analysis import (
    ACCResult, AlphaResult, CaseAnalysis, CATResult, ClusterResult,
    EGDResult, FPDResult, LBIResult, ModeScore, PNOResult, T4DResult, WMSResult,
)


def _minimal_analysis(
    *,
    case_id: str = "TEST-01",
    top_mode_ids: list[str],
    dominant_pno: str = "PNO-001",
    cat: str = "CAT-003",
) -> CaseAnalysis:
    modes = [
        ModeScore(mode_id=m, name=m, mu=0.7, confidence=0.5, evidence_grade="moderate")
        for m in top_mode_ids
    ]
    cluster = ClusterResult(
        cluster_id="ACC-001",
        name="Test cluster",
        score=0.5,
        signature_modes=top_mode_ids[:2],
        explanation="test",
    )
    return CaseAnalysis(
        case_id=case_id,
        top_modes=modes,
        wms=WMSResult(msi=0.5, cep=0.4, active_signals=[], early_warning_hypothesis=""),
        alpha=AlphaResult(initial_mu={}, propagated_mu={}, activated_edges=[], top_modes=modes),
        pno=PNOResult(dominant_pno=dominant_pno, scores={"PNO-001": 0.6}, explanation=""),
        acc=ACCResult(max_contribution_cluster=cluster, clusters=[cluster]),
        egd=EGDResult(echo_room_pressure=0.3, hidden_signal_prior=0.2, likely_egd_modes=[]),
        t4d=T4DResult(worldline=[], warning_to_action_latency_risk=0.3, intervention_window_loss=0.2, irreversibility_threshold_risk=0.1),
        cat=CATResult(catastrophe_hypothesis=cat, bifurcation_risk=0.4, hysteresis_risk=0.3, explanation=""),
        fpd=FPDResult(horizon="near", mode_forecasts=[], pno_transition_forecast="", early_warnings=[], confidence=0.5),
        lbi=LBIResult(alternatives=[]),
        public_explanation="",
    )


def test_dual_run_divergence_flags():
    engine = _minimal_analysis(top_mode_ids=["CB-001", "CB-002", "CB-003"], dominant_pno="PNO-001", cat="CAT-003")
    full = _minimal_analysis(top_mode_ids=["CB-010", "CB-011", "CB-012"], dominant_pno="PNO-007", cat="CAT-015")

    diff = compute_dual_run_diff(engine, full)
    assert diff["needs_human_review"] is True
    assert diff["pno_match"] is False
    assert diff["cat_match"] is False
    assert diff["top_modes_jaccard"] == 0.0

    hints = dual_run_red_team_hints(diff)
    assert len(hints) >= 2
    assert all(h.startswith("[dual-run review]") for h in hints)

    flagged = apply_dual_run_flags(full, diff)
    assert flagged.metadata.get("dual_run_red_team_flagged") is True
    assert any("[dual-run review]" in n for n in flagged.red_team_notes)


def test_dual_run_match_no_flags():
    engine = _minimal_analysis(top_mode_ids=["CB-001", "CB-002", "CB-003"])
    full = _minimal_analysis(top_mode_ids=["CB-001", "CB-002", "CB-003"])

    diff = compute_dual_run_diff(engine, full)
    assert diff["needs_human_review"] is False
    assert dual_run_red_team_hints(diff) == []
    assert apply_dual_run_flags(full, diff).red_team_notes == []
