"""EGD + HM bridge stub tests."""

from mas.memetic.egd_hm_bridge import egd_to_memetic_propagation_snapshot
from mas.schemas.analysis import EGDResult, ModeScore


def test_egd_result_to_memetic_snapshot():
    egd = EGDResult(
        echo_room_pressure=0.62,
        hidden_signal_prior=0.41,
        likely_egd_modes=[
            ModeScore(
                mode_id="EGD-001",
                name="Closed briefing loop",
                mu=0.55,
                confidence=0.4,
                evidence_grade="weak",
                contributing_signals=["briefing_compression"],
            )
        ],
    )
    event = egd_to_memetic_propagation_snapshot("story-egd-1", egd)
    assert event["event_type"] == "memetic_propagation_snapshot"
    assert event["story_id"] == "story-egd-1"
    assert event["epistemic_label"] == "INSTITUTIONAL_MODEL"
    assert event["memetic_metrics"]["echo_room_pressure"] == 0.62
    assert event["memetic_metrics"]["egd_mode_count"] == 1
    assert "institution:parliament" in event["activated_layers"]
    assert event["egd_bridge"]["source"] == "egd_hm_bridge_stub"


def test_egd_dict_to_memetic_snapshot():
    event = egd_to_memetic_propagation_snapshot(
        "story-egd-2",
        {"echo_room_pressure": 0.3, "hidden_signal_prior": 0.2},
        hm_contour_hint="homo-mas echo contour",
    )
    assert event["contour_hint"] == "homo-mas echo contour"
    assert event["memetic_metrics"]["egd_mode_count"] == 0
