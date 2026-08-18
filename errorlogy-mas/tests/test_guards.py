from mas.engine.guards import apply_mode_guards
from mas.schemas.analysis import ModeScore


def test_weak_evidence_caps_mu():
    modes = [
        ModeScore(
            mode_id="SF-007",
            name="Test",
            mu=0.99,
            confidence=0.5,
            evidence_grade="weak",
        )
    ]
    out = apply_mode_guards(modes)
    assert out[0].mu <= 0.65
