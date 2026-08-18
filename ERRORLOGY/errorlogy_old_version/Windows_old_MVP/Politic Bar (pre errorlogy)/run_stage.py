"""Resumable single-stage pipeline runner for politic.bar v0.6.

Runs the next unfinished stage of the 8-agent pipeline for a given case,
then exits. This lets long pipelines complete across multiple short
shell calls (useful in sandboxes with per-call timeouts).

Usage:
    python run_stage.py <case_id> <source_bundle.txt>

Internally identifies the next stage by inspecting cases/<case_id>/_pipeline/
for existing stage JSONs. If all stages complete, assembles and writes the
ErrorCard + runs catalog side-effects (same output as run.py).
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from politic_bar import agents, catalog as catalog_mod
from politic_bar.models import (
    AsymmetryVector,
    Citation,
    Classification,
    ConstitutiveRole,
    CounterArgument,
    ErrorCard,
    FramedCase,
    NeutralityAudit,
    PropagationLink,
    Skeleton,
    Source,
    VerificationResult,
)
from politic_bar.pipeline import (
    CASES_DIR,
    _default_analyst_notes,
    _persist,
    _skeleton_from_dict,
    load_taxonomies,
)


STAGES = [
    "01_scout",
    "02_framed",
    "03_chain_mapper",
    "04_classifications",
    "05_counter_arguments",
    "06_verifications",
    "07_neutrality_audit",
    "08_compiler_raw",
    "99_final_card",
]


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _skeleton(case_id: str) -> Skeleton:
    scout = _read(CASES_DIR / case_id / "_pipeline" / "01_scout.json")
    return _skeleton_from_dict(scout["skeleton"])


def _framed(case_id: str) -> FramedCase:
    d = _read(CASES_DIR / case_id / "_pipeline" / "02_framed.json")
    return FramedCase(
        skeleton=_skeleton_from_dict(d["skeleton"]),
        summary=d["summary"],
        claimed=d["claimed"],
        claimed_citations=[Citation(**c) for c in d.get("claimed_citations", [])],
        known_or_knowable=d["known_or_knowable"],
        known_citations=[Citation(**c) for c in d.get("known_citations", [])],
        decision=d["decision"],
        decision_citations=[Citation(**c) for c in d.get("decision_citations", [])],
        gap=d["gap"],
        constitutive_roles=[ConstitutiveRole(**r) for r in d.get("constitutive_roles", [])],
    )


def _chain_mapper(case_id: str):
    d = _read(CASES_DIR / case_id / "_pipeline" / "03_chain_mapper.json")
    return (
        [AsymmetryVector(**v) for v in d.get("asymmetry_vectors", [])],
        [PropagationLink(**p) for p in d.get("propagation_links", [])],
    )


def _classifications(case_id: str):
    raw = _read(CASES_DIR / case_id / "_pipeline" / "04_classifications.json")
    return [Classification(**c) for c in raw]


def _counters(case_id: str):
    raw = _read(CASES_DIR / case_id / "_pipeline" / "05_counter_arguments.json")
    return [CounterArgument(**c) for c in raw]


def _verifications(case_id: str):
    raw = _read(CASES_DIR / case_id / "_pipeline" / "06_verifications.json")
    return [VerificationResult(**v) for v in raw]


def _audit(case_id: str):
    d = _read(CASES_DIR / case_id / "_pipeline" / "07_neutrality_audit.json")
    return NeutralityAudit(
        passed=d["passed"],
        violations=d.get("violations", []),
        rewrite_suggestions=d.get("rewrite_suggestions", []),
    )


def _compiled(case_id: str):
    return _read(CASES_DIR / case_id / "_pipeline" / "08_compiler_raw.json")


def _stage_exists(case_id: str, stage: str) -> bool:
    return (CASES_DIR / case_id / "_pipeline" / f"{stage}.json").exists()


def _next_stage(case_id: str) -> str | None:
    """Return the next stage name that still needs to run, or None if done."""
    for stage in STAGES:
        if not _stage_exists(case_id, stage):
            return stage
    return None


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python run_stage.py <case_id> <source_bundle.txt>", file=sys.stderr)
        return 2
    case_id, bundle_path = sys.argv[1], Path(sys.argv[2])
    bundle = bundle_path.read_text(encoding="utf-8")

    stage = _next_stage(case_id)
    if stage is None:
        print(f"[{case_id}] all stages complete — card already assembled")
        return 0

    t0 = datetime.utcnow().isoformat()
    print(f"[{case_id}] running stage {stage} @ {t0}Z")

    if stage == "01_scout":
        out = agents.scout(bundle)
        _persist(case_id, "01_scout", out)
        if out.get("status") != "ok":
            print(f"[{case_id}] Scout halted: {out.get('reason')}")
            return 1

    elif stage == "02_framed":
        skeleton = _skeleton(case_id)
        framed = agents.framer(skeleton, bundle)
        _persist(case_id, "02_framed", framed)
        if not (framed.claimed_citations and framed.known_citations and framed.decision_citations):
            print(f"[{case_id}] Framer: missing citations — would halt in full pipeline")

    elif stage == "03_chain_mapper":
        framed = _framed(case_id)
        catalog = catalog_mod.load_catalog()
        catalog = [c for c in catalog if c.get("id") != case_id]
        catalog_summary = catalog_mod.build_catalog_summary(catalog)
        avs, links = agents.chain_mapper(framed, catalog_summary)
        _persist(case_id, "03_chain_mapper", {
            "asymmetry_vectors": [asdict(v) for v in avs],
            "propagation_links": [asdict(p) for p in links],
        })

    elif stage == "04_classifications":
        framed = _framed(case_id)
        avs, links = _chain_mapper(case_id)
        cb, sf, mp = load_taxonomies()

        # Compress taxonomies for the classifier — keep id/name/category/
        # definition, drop the long operational cues. Cuts input context from
        # ~90KB to ~20KB and brings response time under the sandbox timeout.
        def _trim(tax: dict, modes_key: str, fields: tuple[str, ...]) -> dict:
            out = {k: v for k, v in tax.items() if k != modes_key}
            out[modes_key] = [
                {f: m[f] for f in fields if f in m}
                for m in tax.get(modes_key, [])
            ]
            return out

        cb_trim = _trim(cb, "biases", ("id", "name", "category", "definition"))
        sf_trim = _trim(sf, "modes", ("id", "name", "subtype", "definition"))
        mp_trim = _trim(mp, "modes", ("id", "name", "subtype", "definition"))

        classifications = agents.failure_mode_classifier(
            framed, avs, links, cb_trim, sf_trim, mp_trim
        )
        _persist(case_id, "04_classifications", classifications)

    elif stage == "05_counter_arguments":
        framed = _framed(case_id)
        avs, links = _chain_mapper(case_id)
        classifications = _classifications(case_id)
        counters = agents.red_team(framed, classifications, avs, links)
        _persist(case_id, "05_counter_arguments", counters)

    elif stage == "06_verifications":
        framed = _framed(case_id)
        avs, links = _chain_mapper(case_id)
        classifications = _classifications(case_id)
        counters = _counters(case_id)
        # drop defeated (same logic as run_pipeline)
        defeated = {(c.target_kind, c.targets) for c in counters if not c.does_it_survive}
        classifications = [c for c in classifications if ("classification", c.mode_id) not in defeated]
        avs = [v for v in avs if ("asymmetry_vector", v.type) not in defeated]
        links = [p for p in links if ("propagation_link", p.card_id) not in defeated]
        verifications = agents.verifier(framed, classifications, avs, links)
        _persist(case_id, "06_verifications", verifications)

    elif stage == "07_neutrality_audit":
        framed = _framed(case_id)
        avs, links = _chain_mapper(case_id)
        classifications = _classifications(case_id)
        counters = _counters(case_id)
        defeated = {(c.target_kind, c.targets) for c in counters if not c.does_it_survive}
        classifications = [c for c in classifications if ("classification", c.mode_id) not in defeated]
        avs = [v for v in avs if ("asymmetry_vector", v.type) not in defeated]
        links = [p for p in links if ("propagation_link", p.card_id) not in defeated]
        audit = agents.neutrality_auditor(framed, classifications, avs, links, counters)
        _persist(case_id, "07_neutrality_audit", audit)

    elif stage == "08_compiler_raw":
        skeleton = _skeleton(case_id)
        framed = _framed(case_id)
        avs, links = _chain_mapper(case_id)
        classifications = _classifications(case_id)
        counters = _counters(case_id)
        verifications = _verifications(case_id)
        audit = _audit(case_id)
        defeated = {(c.target_kind, c.targets) for c in counters if not c.does_it_survive}
        classifications = [c for c in classifications if ("classification", c.mode_id) not in defeated]
        avs = [v for v in avs if ("asymmetry_vector", v.type) not in defeated]
        links = [p for p in links if ("propagation_link", p.card_id) not in defeated]
        compiled = agents.card_compiler(
            case_id=case_id, version=1,
            skeleton=skeleton, framed=framed,
            classifications=classifications,
            asymmetry_vectors=avs, propagation_links=links,
            counters=counters, verifications=verifications, audit=audit,
        )
        _persist(case_id, "08_compiler_raw", compiled)

    elif stage == "99_final_card":
        skeleton = _skeleton(case_id)
        framed = _framed(case_id)
        avs, links = _chain_mapper(case_id)
        classifications = _classifications(case_id)
        counters = _counters(case_id)
        verifications = _verifications(case_id)
        audit = _audit(case_id)
        compiled = _compiled(case_id)
        defeated = {(c.target_kind, c.targets) for c in counters if not c.does_it_survive}
        classifications = [c for c in classifications if ("classification", c.mode_id) not in defeated]
        avs = [v for v in avs if ("asymmetry_vector", v.type) not in defeated]
        links = [p for p in links if ("propagation_link", p.card_id) not in defeated]

        card = ErrorCard(
            id=case_id, version=1,
            country=skeleton.country, branch=skeleton.branch,
            level=skeleton.level, body=skeleton.body,
            decision_date=skeleton.decision_date, event_type=skeleton.event_type,
            summary=framed.summary, claimed=framed.claimed,
            known_or_knowable=framed.known_or_knowable, decision=framed.decision,
            gap=framed.gap,
            classifications=classifications, asymmetry_vectors=avs,
            propagated_from=links, propagates_to=[],
            constitutive_roles=framed.constitutive_roles,
            counter_arguments=counters,
            residual_uncertainty=str(compiled.get("residual_uncertainty", "")),
            sources=skeleton.sources,
            analyst_notes=str(compiled.get("analyst_notes", _default_analyst_notes(counters))),
        )
        card_path = CASES_DIR / case_id / "card.json"
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_dict = card.to_dict()
        card_path.write_text(
            json.dumps(card_dict, indent=2, default=str, ensure_ascii=False),
            encoding="utf-8",
        )
        upstream = catalog_mod.update_propagates_to(card_dict)
        actors = catalog_mod.update_actor_profiles(card_dict)
        attr = catalog_mod.detect_attractor_component(card_dict)
        _persist(case_id, "99_final_card", {
            "card_written": str(card_path),
            "propagates_to_updated": upstream,
            "actor_profiles_updated": actors,
            "candidate_attractor_flag": asdict(attr) if attr else None,
            "compiled_at": datetime.utcnow().isoformat() + "Z",
        })

    t1 = datetime.utcnow().isoformat()
    print(f"[{case_id}] stage {stage} complete @ {t1}Z")
    nxt = _next_stage(case_id)
    if nxt:
        print(f"[{case_id}] next: {nxt}")
    else:
        print(f"[{case_id}] ALL DONE — card at cases/{case_id}/card.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
