"""Agent wrappers around Claude API calls (v0.6 pipeline).

Each agent is a thin function that (a) loads its prompt, (b) formats its
typed input into a user message, (c) calls the model with the agent's system
prompt, (d) parses the JSON response, (e) returns a typed output.

The orchestrator in pipeline.py composes these. Eight agents total,
matching ARCHITECTURE.md:

    Scout → Framer → Chain-Mapper → Failure-Mode Classifier → Red-Team →
    Verifier → Neutrality Auditor → Card Compiler
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Any

from . import prompts
from .models import (
    AsymmetryVector,
    Citation,
    Classification,
    ConstitutiveRole,
    CounterArgument,
    FramedCase,
    NeutralityAudit,
    PropagationLink,
    Skeleton,
    VerificationResult,
)


# ---------------------------------------------------------------------------
# Model invocation
# ---------------------------------------------------------------------------

def _call_claude(system_prompt: str, user_message: str, *, model: str | None = None) -> str:
    """Call Claude and return the raw text response.

    Reads ANTHROPIC_API_KEY from the environment. The caller is responsible
    for parsing JSON out of the response.

    The import is deferred so that the rest of this module (types, prompts,
    schemas) is usable without the anthropic SDK installed — useful for
    inspection, dashboard-only workflows, and unit tests on the seed cards.
    """
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError(
            "The 'anthropic' package is required to call agents. "
            "Install with: pip install anthropic"
        ) from e

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=model or os.environ.get("POLITIC_BAR_MODEL", "claude-sonnet-4-6"),
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    return "\n".join(parts)


def _extract_json(text: str) -> Any:
    """Best-effort JSON extraction from a model response."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def _dump(obj: Any) -> str:
    """Serialize dataclasses / lists of dataclasses to JSON for prompt context."""
    if hasattr(obj, "__dataclass_fields__"):
        return json.dumps(asdict(obj), indent=2, default=str)
    if isinstance(obj, list):
        return json.dumps(
            [asdict(x) if hasattr(x, "__dataclass_fields__") else x for x in obj],
            indent=2,
            default=str,
        )
    return json.dumps(obj, indent=2, default=str)


# ---------------------------------------------------------------------------
# 1. Scout
# ---------------------------------------------------------------------------

def scout(raw_source_bundle: str) -> dict:
    """Extract the decision-event skeleton from a raw source bundle.

    Returns either {"status": "ok", "skeleton": {...}} or
    {"status": "unqualified", "reason": "..."}. The skeleton carries
    `event_type` per §2a (decision | non_decision | unstable_decision)."""
    raw = _call_claude(
        prompts.SCOUT_PROMPT,
        f"SOURCE BUNDLE:\n\n{raw_source_bundle}",
    )
    return _extract_json(raw)


# ---------------------------------------------------------------------------
# 2. Framer
# ---------------------------------------------------------------------------

def framer(skeleton: Skeleton, raw_source_bundle: str) -> FramedCase:
    """Write the narrative fields of the card, each with citations, plus
    initial constitutive_roles entries for every named actor (N6)."""
    user = (
        f"SKELETON:\n{_dump(skeleton)}\n\n"
        f"SOURCES:\n\n{raw_source_bundle}"
    )
    parsed = _extract_json(_call_claude(prompts.FRAMER_PROMPT, user))
    return FramedCase(
        skeleton=skeleton,
        summary=parsed["summary"],
        claimed=parsed["claimed"],
        claimed_citations=[Citation(**c) for c in parsed.get("claimed_citations", [])],
        known_or_knowable=parsed["known_or_knowable"],
        known_citations=[Citation(**c) for c in parsed.get("known_citations", [])],
        decision=parsed["decision"],
        decision_citations=[Citation(**c) for c in parsed.get("decision_citations", [])],
        gap=parsed["gap"],
        constitutive_roles=[
            ConstitutiveRole(**r) for r in parsed.get("constitutive_roles", [])
        ],
    )


# ---------------------------------------------------------------------------
# 3. Chain-Mapper
# ---------------------------------------------------------------------------

def chain_mapper(
    framed: FramedCase,
    catalog_summary: list[dict],
) -> tuple[list[AsymmetryVector], list[PropagationLink]]:
    """Identify asymmetry vectors (A1–A3) and propose propagated_from links
    (P1–P3) against the existing catalog. Catalog summary is a list of
    {card_id, country, branch, body, decision_date, topic_keywords}
    derived from published cards."""
    user = (
        f"FRAMED CASE:\n{_dump(framed)}\n\n"
        f"CATALOG SUMMARY (existing cards):\n{json.dumps(catalog_summary, indent=2)}"
    )
    parsed = _extract_json(_call_claude(prompts.CHAIN_MAPPER_PROMPT, user))
    avs = [AsymmetryVector(**v) for v in parsed.get("asymmetry_vectors", [])]
    links = [
        PropagationLink(**link)
        for link in parsed.get("candidate_propagated_from", [])
    ]
    return avs, links


# ---------------------------------------------------------------------------
# 4. Failure-Mode Classifier
# ---------------------------------------------------------------------------

def failure_mode_classifier(
    framed: FramedCase,
    asymmetry_vectors: list[AsymmetryVector],
    propagation_links: list[PropagationLink],
    cognitive_biases: dict,
    strategic_failure_modes: dict,
    mechanism_pathologies: dict,
) -> list[Classification]:
    """Nominate classifications across L1–L5 from the three taxonomies.
    Returns [] if none apply on the record (a legitimate output)."""
    user = (
        f"FRAMED CASE:\n{_dump(framed)}\n\n"
        f"CHAIN-MAPPER OUTPUT:\n"
        f"  asymmetry_vectors: {_dump(asymmetry_vectors)}\n"
        f"  propagation_links: {_dump(propagation_links)}\n\n"
        f"TAXONOMY — cognitive_biases (L1/L2/L3):\n"
        f"{json.dumps(cognitive_biases, indent=2)}\n\n"
        f"TAXONOMY — strategic_failure_modes (L4):\n"
        f"{json.dumps(strategic_failure_modes, indent=2)}\n\n"
        f"TAXONOMY — mechanism_pathologies (L5):\n"
        f"{json.dumps(mechanism_pathologies, indent=2)}"
    )
    parsed = _extract_json(_call_claude(prompts.FAILURE_MODE_CLASSIFIER_PROMPT, user))
    return [Classification(**c) for c in parsed.get("classifications", [])]


# ---------------------------------------------------------------------------
# 5. Red-Team
# ---------------------------------------------------------------------------

def red_team(
    framed: FramedCase,
    classifications: list[Classification],
    asymmetry_vectors: list[AsymmetryVector],
    propagation_links: list[PropagationLink],
) -> list[CounterArgument]:
    """Adversarial pass over every claim: classifications (L1–L5),
    asymmetry vectors, propagation links, constitutive_roles foreseeability,
    and the gap. Runs §5a/§5b/§5c-M3/§5d-S3 bidirectional/§5d-S4 sufficiency
    tests; records them in `tests_run` on each CounterArgument."""
    user = (
        f"FRAMED CASE:\n{_dump(framed)}\n\n"
        f"CLASSIFICATIONS (L1–L5):\n{_dump(classifications)}\n\n"
        f"ASYMMETRY VECTORS:\n{_dump(asymmetry_vectors)}\n\n"
        f"PROPAGATION LINKS:\n{_dump(propagation_links)}"
    )
    parsed = _extract_json(_call_claude(prompts.RED_TEAM_PROMPT, user))
    out: list[CounterArgument] = []
    for c in parsed.get("counter_arguments", []):
        out.append(
            CounterArgument(
                targets=c["targets"],
                target_kind=c.get("target_kind", "classification"),
                strongest_counter=c.get("strongest_counter", ""),
                does_it_survive=c.get("does_it_survive", True),
                tests_run=c.get("tests_run", []),
                notes=c.get("notes"),
            )
        )
    return out


# ---------------------------------------------------------------------------
# 6. Verifier
# ---------------------------------------------------------------------------

def verifier(
    framed: FramedCase,
    classifications: list[Classification],
    asymmetry_vectors: list[AsymmetryVector],
    propagation_links: list[PropagationLink],
) -> list[VerificationResult]:
    """Confirm every citation resolves and every quote matches, across
    narrative fields, classifications, asymmetry vectors, propagation
    links, and constitutive_roles."""
    user = (
        f"FRAMED CASE (with citations):\n{_dump(framed)}\n\n"
        f"CLASSIFICATIONS:\n{_dump(classifications)}\n\n"
        f"ASYMMETRY VECTORS:\n{_dump(asymmetry_vectors)}\n\n"
        f"PROPAGATION LINKS:\n{_dump(propagation_links)}"
    )
    parsed = _extract_json(_call_claude(prompts.VERIFIER_PROMPT, user))
    return [VerificationResult(**v) for v in parsed.get("verifications", [])]


# ---------------------------------------------------------------------------
# 7. Neutrality Auditor
# ---------------------------------------------------------------------------

def neutrality_auditor(
    framed: FramedCase,
    classifications: list[Classification],
    asymmetry_vectors: list[AsymmetryVector],
    propagation_links: list[PropagationLink],
    counters: list[CounterArgument],
) -> NeutralityAudit:
    """Block publication if any N1–N6 rule is violated. Has veto.
    Applies layer-specific language tests for L4, L5, and attractor
    framings (§7b)."""
    user = (
        f"FRAMED CASE:\n{_dump(framed)}\n\n"
        f"CLASSIFICATIONS:\n{_dump(classifications)}\n\n"
        f"ASYMMETRY VECTORS:\n{_dump(asymmetry_vectors)}\n\n"
        f"PROPAGATION LINKS:\n{_dump(propagation_links)}\n\n"
        f"COUNTER-ARGUMENTS:\n{_dump(counters)}"
    )
    parsed = _extract_json(_call_claude(prompts.NEUTRALITY_PROMPT, user))
    return NeutralityAudit(
        passed=parsed["passed"],
        violations=parsed.get("violations", []),
        rewrite_suggestions=parsed.get("rewrite_suggestions", []),
    )


# ---------------------------------------------------------------------------
# 8. Card Compiler
# ---------------------------------------------------------------------------

def card_compiler(
    case_id: str,
    version: int,
    skeleton: Skeleton,
    framed: FramedCase,
    classifications: list[Classification],
    asymmetry_vectors: list[AsymmetryVector],
    propagation_links: list[PropagationLink],
    counters: list[CounterArgument],
    verifications: list[VerificationResult],
    audit: NeutralityAudit,
) -> dict:
    """Compiler fills residual_uncertainty and analyst_notes by reasoning
    over upstream outputs. Returns the FINAL ErrorCard as a plain dict
    (the orchestrator adds catalog side-effects and persists the card).

    The compiler is deterministic for everything except residual_uncertainty
    and analyst_notes, which are authored by Claude based on the signals
    in the pipeline record."""
    payload = {
        "case_id": case_id,
        "version": version,
        "skeleton": asdict(skeleton),
        "framed": asdict(framed),
        "classifications": [asdict(c) for c in classifications],
        "asymmetry_vectors": [asdict(v) for v in asymmetry_vectors],
        "propagation_links": [asdict(p) for p in propagation_links],
        "counter_arguments": [asdict(c) for c in counters],
        "verifications": [asdict(v) for v in verifications],
        "neutrality_audit": asdict(audit),
    }
    user = f"PIPELINE RECORD:\n{json.dumps(payload, indent=2, default=str)}"
    return _extract_json(_call_claude(prompts.CARD_COMPILER_PROMPT, user))
