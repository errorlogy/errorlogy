"""Compare engine_only vs full MAS pipeline results."""

from __future__ import annotations

from .schemas.analysis import CaseAnalysis


def _top_mode_ids(result: CaseAnalysis, n: int = 5) -> set[str]:
    return {m.mode_id for m in result.top_modes[:n]}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return round(len(a & b) / len(union), 4)


def compute_dual_run_diff(engine: CaseAnalysis, full: CaseAnalysis) -> dict:
    eng_top = _top_mode_ids(engine)
    full_top = _top_mode_ids(full)
    overlap = eng_top & full_top

    flags: list[str] = []
    if engine.pno.dominant_pno != full.pno.dominant_pno:
        flags.append(
            f"PNO mismatch: engine={engine.pno.dominant_pno} full={full.pno.dominant_pno}"
        )
    if engine.cat.catastrophe_hypothesis != full.cat.catastrophe_hypothesis:
        flags.append(
            f"CAT mismatch: engine={engine.cat.catastrophe_hypothesis} "
            f"full={full.cat.catastrophe_hypothesis}"
        )
    if _jaccard(eng_top, full_top) < 0.3:
        flags.append("Low top-5 mode overlap — review recommended")

    return {
        "top_modes_jaccard": _jaccard(eng_top, full_top),
        "top_modes_overlap": sorted(overlap),
        "engine_only_top5": sorted(eng_top),
        "full_top5": sorted(full_top),
        "pno_match": engine.pno.dominant_pno == full.pno.dominant_pno,
        "cat_match": engine.cat.catastrophe_hypothesis == full.cat.catastrophe_hypothesis,
        "red_team_flags": flags,
        "needs_human_review": len(flags) > 0,
    }


def dual_run_red_team_hints(diff: dict) -> list[str]:
    if not diff.get("needs_human_review"):
        return []
    return [f"[dual-run review] {f}" for f in diff.get("red_team_flags", [])]


def apply_dual_run_flags(full: CaseAnalysis, diff: dict) -> CaseAnalysis:
    hints = dual_run_red_team_hints(diff)
    if not hints:
        return full
    meta = dict(full.metadata or {})
    meta["dual_run_red_team_flagged"] = True
    return full.model_copy(update={
        "red_team_notes": list(full.red_team_notes) + hints,
        "metadata": meta,
    })
