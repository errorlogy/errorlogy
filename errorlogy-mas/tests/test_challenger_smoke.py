from mas.orchestrator import Orchestrator


def test_challenger_engine_smoke(challenger_case):
    orch = Orchestrator(init_llm=False)
    a1 = orch.run_engine_from_case(challenger_case)
    a2 = orch.run_engine_from_case(challenger_case)

    assert a1.metadata.get("engine_only") is True
    assert a1.wms.msi == a2.wms.msi
    assert a1.pno.dominant_pno == a2.pno.dominant_pno

    families = {m.mode_id.split("-")[0] for m in a1.top_modes[:5]}
    assert "CB" in families

    for m in a1.top_modes:
        if m.evidence_grade == "weak":
            assert m.mu <= 0.65
