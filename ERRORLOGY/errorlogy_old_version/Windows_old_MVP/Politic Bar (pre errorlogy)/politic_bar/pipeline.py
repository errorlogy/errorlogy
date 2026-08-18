"""Pipeline orchestrator (v0.6).

Composes the eight agents in agents.py according to ARCHITECTURE.md:

    Scout → Framer → Chain-Mapper → Failure-Mode Classifier → Red-Team →
    Verifier → Neutrality Auditor → Card Compiler

Persists intermediate outputs so cards can be audited, replayed, or
branched. Card Compiler publication triggers catalog side-effects
(propagates_to back-refs, actor-profile maintenance, attractor-component
detection) handled by catalog.py.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import agents, catalog as catalog_mod
from .compose import compose_analyst_notes, compose_residual_uncertainty
from .models import (
    AsymmetryVector,
    Citation,
    Classification,
    ConstitutiveRole,
    ErrorCard,
    FramedCase,
    PropagationLink,
    Skeleton,
    Source,
)


ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_DIR = ROOT / "taxonomy"
CASES_DIR = ROOT / "cases"


# ---------------------------------------------------------------------------
# Taxonomy loading
# ---------------------------------------------------------------------------

def load_taxonomies() -> tuple[dict, dict, dict]:
    """Load all three v0.6 taxonomies. Returns
    (cognitive_biases, strategic_failure_modes, mechanism_pathologies)."""
    cb = json.loads((TAXONOMY_DIR / "cognitive_biases.json").read_text(encoding="utf-8"))
    sf = json.loads((TAXONOMY_DIR / "strategic_failure_modes.json").read_text(encoding="utf-8"))
    mp = json.loads((TAXONOMY_DIR / "mechanism_pathologies.json").read_text(encoding="utf-8"))
    return cb, sf, mp


# Legacy alias retained for any external caller that used the v0.2 API.
def load_taxonomy() -> dict:
    cb, _, _ = load_taxonomies()
    return cb


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _persist(case_id: str, stage: str, payload) -> None:
    case_dir = CASES_DIR / case_id / "_pipeline"
    case_dir.mkdir(parents=True, exist_ok=True)
    path = case_dir / f"{stage}.json"
    if hasattr(payload, "__dataclass_fields__"):
        data = asdict(payload)
    elif isinstance(payload, list):
        data = [asdict(p) if hasattr(p, "__dataclass_fields__") else p for p in payload]
    else:
        data = payload
    path.write_text(
        json.dumps(data, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )


def _skeleton_from_dict(d: dict) -> Skeleton:
    return Skeleton(
        country=d["country"],
        branch=d["branch"],
        level=d["level"],
        body=d["body"],
        decision_date=d["decision_date"],
        event_type=d.get("event_type", "decision"),
        sources=[Source(**s) if isinstance(s, dict) else s for s in d.get("sources", [])],
    )


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(case_id: str, raw_source_bundle: str) -> Optional[ErrorCard]:
    """End-to-end: raw source bundle → published ErrorCard.

    Returns None when the pipeline halts with a qualification failure,
    insufficient record, or a blocking neutrality / verification failure.
    The persisted _pipeline/ directory always contains whatever was
    produced, including failure notes."""

    # ---- 1. Scout ------------------------------------------------------
    scout_out = agents.scout(raw_source_bundle)
    _persist(case_id, "01_scout", scout_out)
    if scout_out.get("status") != "ok":
        return None

    skeleton = _skeleton_from_dict(scout_out["skeleton"])

    # ---- 2. Framer -----------------------------------------------------
    framed = agents.framer(skeleton, raw_source_bundle)
    _persist(case_id, "02_framed", framed)
    if not (framed.claimed_citations and framed.known_citations and framed.decision_citations):
        # §3: a card with no cited claimed / known / decided is a draft.
        return None

    # ---- 3. Chain-Mapper -----------------------------------------------
    catalog = catalog_mod.load_catalog()
    # Exclude the card we are writing in case of re-run against an existing id.
    catalog = [c for c in catalog if c.get("id") != case_id]
    catalog_summary = catalog_mod.build_catalog_summary(catalog)
    asymmetry_vectors, propagation_links = agents.chain_mapper(framed, catalog_summary)
    _persist(case_id, "03_chain_mapper", {
        "asymmetry_vectors": [asdict(v) for v in asymmetry_vectors],
        "propagation_links": [asdict(p) for p in propagation_links],
    })

    # ---- 4. Failure-Mode Classifier ------------------------------------
    cb, sf, mp = load_taxonomies()
    classifications = agents.failure_mode_classifier(
        framed, asymmetry_vectors, propagation_links, cb, sf, mp
    )
    _persist(case_id, "04_classifications", classifications)

    # ---- 5. Red-Team ---------------------------------------------------
    counters = agents.red_team(framed, classifications, asymmetry_vectors, propagation_links)
    _persist(case_id, "05_counter_arguments", counters)

    # Drop classifications / links / AVs the Red-Team defeated.
    defeated = {(c.target_kind, c.targets) for c in counters if not c.does_it_survive}

    classifications = [
        c for c in classifications
        if ("classification", c.mode_id) not in defeated
    ]
    asymmetry_vectors = [
        v for v in asymmetry_vectors
        if ("asymmetry_vector", v.type) not in defeated
    ]
    propagation_links = [
        p for p in propagation_links
        if ("propagation_link", p.card_id) not in defeated
    ]

    # ---- 6. Verifier ---------------------------------------------------
    verifications = agents.verifier(framed, classifications, asymmetry_vectors, propagation_links)
    _persist(case_id, "06_verifications", verifications)
    unresolved = [v for v in verifications if not v.resolves or not v.quote_matches]
    if unresolved:
        # §8 falsifiability: unresolved citation → card reverts to draft.
        return None

    # ---- 7. Neutrality Auditor -----------------------------------------
    audit = agents.neutrality_auditor(
        framed, classifications, asymmetry_vectors, propagation_links, counters
    )
    _persist(case_id, "07_neutrality_audit", audit)
    if not audit.passed:
        return None  # veto — does not publish

    # ---- 8. Card Compiler ----------------------------------------------
    compiled = agents.card_compiler(
        case_id=case_id,
        version=1,
        skeleton=skeleton,
        framed=framed,
        classifications=classifications,
        asymmetry_vectors=asymmetry_vectors,
        propagation_links=propagation_links,
        counters=counters,
        verifications=verifications,
        audit=audit,
    )
    _persist(case_id, "08_compiler_raw", compiled)

    # Every field on the published card is deterministically assembled from
    # upstream agent outputs. residual_uncertainty and analyst_notes are
    # composed from counter_arguments + verifications + run metadata — NOT
    # from free LLM text. The Compiler agent's own prose lands in
    # 08_compiler_raw.json as `compiler_commentary` and stays there:
    # excluded from the published card by design (drift prevention).
    card = ErrorCard(
        id=case_id,
        version=1,
        country=skeleton.country,
        branch=skeleton.branch,
        level=skeleton.level,
        body=skeleton.body,
        decision_date=skeleton.decision_date,
        event_type=skeleton.event_type,
        summary=framed.summary,
        claimed=framed.claimed,
        known_or_knowable=framed.known_or_knowable,
        decision=framed.decision,
        gap=framed.gap,
        classifications=classifications,
        asymmetry_vectors=asymmetry_vectors,
        propagated_from=propagation_links,
        propagates_to=[],  # back-refs are maintained by downstream publications
        constitutive_roles=framed.constitutive_roles,
        counter_arguments=counters,
        residual_uncertainty=compose_residual_uncertainty(counters, verifications),
        sources=skeleton.sources,
        analyst_notes=compose_analyst_notes(case_id, counters, classifications,
                                            asymmetry_vectors, propagation_links),
    )

    # Persist the card.
    card_path = CASES_DIR / case_id / "card.json"
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_dict = card.to_dict()
    card_path.write_text(
        json.dumps(card_dict, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )

    # ---- Catalog side-effects (§6, §7a, §7b) ---------------------------
    upstream_touched = catalog_mod.update_propagates_to(card_dict)
    actors_touched = catalog_mod.update_actor_profiles(card_dict)
    attractor_flag = catalog_mod.detect_attractor_component(card_dict)

    _persist(case_id, "09_catalog_side_effects", {
        "propagates_to_updated": upstream_touched,
        "actor_profiles_updated": actors_touched,
        "candidate_attractor_flag": asdict(attractor_flag) if attractor_flag else None,
        "compiled_at": datetime.utcnow().isoformat() + "Z",
    })

    return card


# compose_residual_uncertainty / compose_analyst_notes live in compose.py
# (imported above). They are the only deterministic composers on the
# pipeline output path.
