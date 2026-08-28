"""EGD + HM bridge stub — maps echo-room state to memetic propagation snapshot.

INSTITUTIONAL_MODEL routing only; does not invent HM-xxx mode IDs or claim verdict authority.
Joins EGD echo-room pressure with homo-mas contour signals as a cross-layer envelope stub.
"""

from __future__ import annotations

from typing import Any

from mas.institutional.activation import frame_cross_layer_event
from mas.schemas.analysis import EGDResult

_DEFAULT_EPISTEMIC = "INSTITUTIONAL_MODEL"


def _egd_fields(egd: EGDResult | dict[str, Any]) -> tuple[float, float, int]:
    if isinstance(egd, EGDResult):
        return (
            egd.echo_room_pressure,
            egd.hidden_signal_prior,
            len(egd.likely_egd_modes),
        )
    return (
        float(egd.get("echo_room_pressure", 0.0)),
        float(egd.get("hidden_signal_prior", 0.0)),
        len(egd.get("likely_egd_modes") or []),
    )


def egd_to_memetic_propagation_snapshot(
    story_id: str,
    egd: EGDResult | dict[str, Any],
    *,
    hm_contour_hint: str | None = None,
    epistemic_label: str = _DEFAULT_EPISTEMIC,
) -> dict[str, Any]:
    """Map EGD echo-room state → ``memetic_propagation_snapshot`` cross-layer event dict."""
    sid = story_id.strip()
    if not sid:
        raise ValueError("story_id is required")

    echo_pressure, hidden_prior, mode_count = _egd_fields(egd)
    payload: dict[str, Any] = {
        "story_id": sid,
        "event_type": "memetic_propagation_snapshot",
        "epistemic_label": epistemic_label,
    }

    framed = frame_cross_layer_event(payload)
    framed["memetic_metrics"] = {
        "echo_room_pressure": round(echo_pressure, 4),
        "hidden_signal_prior": round(hidden_prior, 4),
        "egd_mode_count": mode_count,
    }
    if hm_contour_hint:
        framed["contour_hint"] = hm_contour_hint.strip()
    framed["egd_bridge"] = {
        "source": "egd_hm_bridge_stub",
        "echo_room_pressure": round(echo_pressure, 4),
        "hidden_signal_prior": round(hidden_prior, 4),
    }
    return framed
