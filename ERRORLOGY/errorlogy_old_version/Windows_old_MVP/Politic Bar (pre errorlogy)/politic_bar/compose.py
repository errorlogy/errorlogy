"""Deterministic composition of the two free-text fields on a published card.

Pre-v0.6.x, `residual_uncertainty` and `analyst_notes` were carried over from
the Compiler agent's free output, which created a silent channel for
unattributed LLM-introduced claims into the published card. From v0.6.x onward
both fields are composed mechanically from upstream agent outputs only:

- residual_uncertainty ← counter_arguments + verifications
- analyst_notes        ← run metadata + counts

Any free LLM commentary the Compiler agent emits lives in
`08_compiler_raw.json` under `compiler_commentary` and is not published.

Kept in its own module so the composers can be imported and tested
without dragging in the rest of pipeline.py (and the anthropic SDK).
"""

from __future__ import annotations

from datetime import datetime


def compose_residual_uncertainty(counters, verifications) -> str:
    """Build residual_uncertainty from Red-Team and Verifier outputs only.

    METHODOLOGY §6: residual_uncertainty must record what the pipeline
    *did not resolve* — surviving counter-arguments, defeated claims, and
    any verifier warnings. We do not summarise; we report."""
    survived = [c for c in counters if c.does_it_survive]
    defeated = [c for c in counters if not c.does_it_survive]
    verifier_notes = [v for v in verifications if v.notes]

    parts: list[str] = []
    if survived:
        items = "; ".join(
            f"[{c.target_kind}:{c.targets}] {c.strongest_counter}"
            for c in survived
        )
        parts.append(
            f"{len(survived)} counter-argument(s) survived Red-Team and remain "
            f"on the record: {items}"
        )
    if defeated:
        items = ", ".join(f"{c.target_kind}:{c.targets}" for c in defeated)
        tests = sorted({t for c in defeated for t in (c.tests_run or [])})
        suffix = f" (tests applied: {', '.join(tests)})" if tests else ""
        parts.append(
            f"{len(defeated)} claim(s) dropped after Red-Team defeat: {items}"
            f"{suffix}."
        )
    if verifier_notes:
        items = "; ".join(f"[{v.source_id}] {v.notes}" for v in verifier_notes)
        parts.append(f"Verifier notes carried forward: {items}.")
    if not parts:
        parts.append(
            "No surviving counter-arguments, no defeated claims, no verifier "
            "notes. The card asserts what its citations support and nothing else."
        )
    return " ".join(parts)


def compose_analyst_notes(case_id, counters, classifications,
                          asymmetry_vectors, propagation_links) -> str:
    """Build analyst_notes from run metadata only — no agent free text.

    Format is a fixed template: timestamp, version, counts, pointer to the
    per-stage outputs. An analyst can append further notes by hand-editing
    the published card after publication; the pipeline itself never injects
    LLM-authored prose here."""
    from . import __version__

    n_class = len(classifications)
    n_av = len(asymmetry_vectors)
    n_prop = len(propagation_links)
    n_drop = sum(1 for c in counters if not c.does_it_survive)

    return (
        f"Pipeline run at {datetime.utcnow().isoformat()}Z "
        f"(politic_bar v{__version__}). "
        f"Card composed deterministically from upstream agent outputs: "
        f"{n_class} classification(s), {n_av} asymmetry vector(s), "
        f"{n_prop} propagation link(s); "
        f"{n_drop} claim(s) dropped after Red-Team defeat. "
        f"See cases/{case_id}/_pipeline/ for per-stage outputs."
    )
