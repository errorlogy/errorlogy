"""Catalog utilities: loading cards, actor-profile maintenance, back-ref
updates, and attractor-component detection (§7a, §7b).

Kept separate from pipeline.py so graph operations on the catalog are
testable in isolation and do not require the anthropic SDK.

Paths:
    cases/{case_id}/card.json           — the published error cards
    actors/{actor_id}.json              — derived actor profiles (§7a)
    catalog/attractors/{attractor_id}.json  — authored attractor records (§7b)
    catalog/candidate_attractor_flags.jsonl — Compiler-emitted flags
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import (
    ActorProfile,
    ActorProfileEntry,
    CandidateAttractorFlag,
    ErrorCard,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"
ACTORS_DIR = ROOT / "actors"
CATALOG_DIR = ROOT / "catalog"
ATTRACTORS_DIR = CATALOG_DIR / "attractors"
FLAGS_FILE = CATALOG_DIR / "candidate_attractor_flags.jsonl"


# Minimum cross-card pattern threshold for candidate attractor (AT2, v0.6).
ATTRACTOR_MIN_MEMBERS = 4


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_card(case_id: str) -> dict | None:
    """Load a published card by id. Returns None if not present."""
    path = CASES_DIR / case_id / "card.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog() -> list[dict]:
    """Load all published cards. Unordered."""
    if not CASES_DIR.exists():
        return []
    out: list[dict] = []
    for case_dir in CASES_DIR.iterdir():
        card_path = case_dir / "card.json"
        if card_path.exists():
            try:
                out.append(json.loads(card_path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue
    return out


def build_catalog_summary(catalog: list[dict]) -> list[dict]:
    """Lightweight catalog index for Chain-Mapper context. Keeps token
    footprint small while giving the agent enough to propose links."""
    out: list[dict] = []
    for card in catalog:
        summary = (card.get("summary") or "").strip()
        out.append(
            {
                "card_id": card.get("id"),
                "country": card.get("country"),
                "branch": card.get("branch"),
                "level": card.get("level"),
                "body": card.get("body"),
                "decision_date": card.get("decision_date"),
                "event_type": card.get("event_type", "decision"),
                "summary": summary,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Actor profiles (§7a)
# ---------------------------------------------------------------------------

_ID_SAFE = re.compile(r"[^A-Za-z0-9_-]+")
_UNICODE_WORD_SAFE = re.compile(r"[^\w-]+", re.UNICODE)


# ISO-9-ish / practical transliteration for Cyrillic scripts (Russian, Ukrainian,
# Belarusian). Lowercase keys only — table is applied after .lower().
# Digraphs (sh, ch, etc.) are standard English-reader forms, not strict ISO-9,
# because the slug is a filesystem id, not a linguistic transcription.
_CYRILLIC_TRANSLIT: dict[str, str] = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
    "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
    # Ukrainian additions
    "ґ": "g", "є": "ye", "і": "i", "ї": "yi",
    # Belarusian
    "ў": "w",
}

# Ukrainian-only letters. If any appear in the input, switch `и` → `y`
# (BGN/PCGN Ukrainian) instead of the default `и` → `i` (Russian).
# Without this, "Володимир Зеленський" would slug as "volodimir-zelenskiy"
# rather than the canonical English rendering "volodymyr-zelenskyy".
_UKRAINIAN_MARKERS: frozenset[str] = frozenset({"і", "ї", "є", "ґ"})


def _transliterate_cyrillic(s: str) -> str:
    """Apply Cyrillic → Latin transliteration. Non-Cyrillic chars pass through
    unchanged so mixed-script names like 'A. Иванов' survive.

    If Ukrainian-only letters (і/ї/є/ґ) appear anywhere in the input, the
    whole string is treated as Ukrainian and `и` is rendered `y` instead
    of `i`. This is a heuristic — a pure-Russian string containing these
    letters would be mistranslated, but in practice Russian text never
    contains `і`, `ї`, `є`, or `ґ`.
    """
    if any(ch in _UKRAINIAN_MARKERS for ch in s):
        table = dict(_CYRILLIC_TRANSLIT)
        table["и"] = "y"
        return "".join(table.get(ch, ch) for ch in s)
    return "".join(_CYRILLIC_TRANSLIT.get(ch, ch) for ch in s)


def _slugify_actor(name: str) -> str:
    """Stable, filesystem-safe id from a display name. AP2 identity
    discipline: conflations remain reversible because the profile file
    stores the display name verbatim.

    Strategy (v0.6.1):
    1. Lowercase + Cyrillic transliteration (Russian/Ukrainian/Belarusian).
    2. NFKD decomposition + ASCII fold for Latin diacritics (café → cafe).
    3. Replace anything not [A-Za-z0-9_-] with '-' and collapse dashes.
    4. If ASCII result is empty (pure non-Latin script — CJK, Arabic,
       Hebrew, etc.), fall back to a Unicode-word-preserving slug so the
       identity survives in the filename instead of colliding under
       'unnamed-actor'. Modern filesystems (NTFS, ext4, APFS) support
       Unicode filenames.
    5. Return 'unnamed-actor' only when the input is empty, whitespace,
       or pure punctuation — i.e. truly has no usable chars.
    """
    if not name or not name.strip():
        return "unnamed-actor"

    lowered = name.strip().lower()
    transliterated = _transliterate_cyrillic(lowered)
    normalized = unicodedata.normalize("NFKD", transliterated)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_slug = _ID_SAFE.sub("-", ascii_only).strip("-")
    if ascii_slug:
        return ascii_slug

    # Fallback for scripts we don't transliterate — preserve Unicode word chars
    # so a name like '李明' becomes '李明' rather than dropping to a collision.
    unicode_slug = _UNICODE_WORD_SAFE.sub("-", lowered).strip("-")
    return unicode_slug or "unnamed-actor"


def _collect_actors_from_card(card: dict) -> list[tuple[str, str, str]]:
    """Yield (actor_display_name, role, role_detail) for every actor named
    in body, constitutive_roles, or sources. Roles match §7a AP-semantics:
    `principal` when the actor IS the deciding body; `named_in_roles`
    otherwise; `quoted_in_sources` for source-quoted-only actors."""
    out: list[tuple[str, str, str]] = []

    body = card.get("body")
    if body:
        out.append((body, "principal", ""))

    for role in card.get("constitutive_roles", []) or []:
        actor = role.get("actor")
        if not actor:
            continue
        if actor == body:
            # Already captured as principal; don't double-count.
            continue
        out.append((actor, "named_in_roles", role.get("action_or_inaction", "")))

    # Sources: `notes` field on a Source may name an individual quoted-only;
    # v0.6 does not auto-extract these, so this is a placeholder for future
    # when the Framer emits a `quoted_actors` field. Left empty deliberately.

    return out


def update_actor_profiles(card: dict) -> list[str]:
    """Append a per-card entry to every relevant actor's profile. Returns
    the list of actor_ids touched. AP1: aggregation only — every field
    resolves to citations in the underlying card."""
    ACTORS_DIR.mkdir(parents=True, exist_ok=True)
    touched: list[str] = []

    actor_tuples = _collect_actors_from_card(card)
    if not actor_tuples:
        return touched

    foreseeability_by_actor: dict[str, str] = {}
    for role in card.get("constitutive_roles", []) or []:
        if role.get("actor") and role.get("foreseeability"):
            foreseeability_by_actor[role["actor"]] = role["foreseeability"]

    classification_labels = [
        f"{c.get('layer', '?')}:{c.get('mode_id', c.get('bias_id', '?'))}"
        for c in card.get("classifications", []) or []
    ]
    av_types = [v.get("type") for v in card.get("asymmetry_vectors", []) or [] if v.get("type")]
    prop_ids = [p.get("card_id") for p in card.get("propagated_from", []) or [] if p.get("card_id")]

    for actor_name, role, role_detail in actor_tuples:
        actor_id = _slugify_actor(actor_name)
        touched.append(actor_id)
        profile_path = ACTORS_DIR / f"{actor_id}.json"

        if profile_path.exists():
            raw = json.loads(profile_path.read_text(encoding="utf-8"))
            profile = ActorProfile(
                actor_id=raw["actor_id"],
                display_name=raw["display_name"],
                entries=[ActorProfileEntry(**e) for e in raw.get("entries", [])],
                possibly_same_as=raw.get("possibly_same_as", []),
                version=raw.get("version", 1),
            )
        else:
            profile = ActorProfile(actor_id=actor_id, display_name=actor_name)

        # Idempotent: if an entry for this card_id already exists, replace it.
        profile.entries = [e for e in profile.entries if e.card_id != card.get("id")]

        entry = ActorProfileEntry(
            card_id=card.get("id", ""),
            decision_date=card.get("decision_date", ""),
            body=card.get("body", ""),
            branch=card.get("branch", "other"),
            level=card.get("level", "national"),
            role=role,  # type: ignore[arg-type]
            role_detail=role_detail,
            classifications=classification_labels,
            foreseeability=foreseeability_by_actor.get(actor_name),  # type: ignore[arg-type]
            asymmetry_vectors=av_types,  # type: ignore[arg-type]
            propagated_from_ids=prop_ids,
        )
        profile.entries.append(entry)
        profile.entries.sort(key=lambda e: e.decision_date)
        profile.version = (profile.version or 1) + 1

        profile_path.write_text(
            json.dumps(asdict(profile), indent=2, default=str, ensure_ascii=False),
            encoding="utf-8",
        )

    return touched


# ---------------------------------------------------------------------------
# Propagation back-refs
# ---------------------------------------------------------------------------

def update_propagates_to(card: dict) -> list[str]:
    """For every `propagated_from[i].card_id` on the new card, append a
    corresponding `propagates_to` entry to the upstream card. Bumps the
    upstream card's version. Returns the list of upstream card_ids
    mutated."""
    downstream_id = card.get("id")
    if not downstream_id:
        return []

    touched: list[str] = []
    for link in card.get("propagated_from", []) or []:
        upstream_id = link.get("card_id")
        if not upstream_id:
            continue
        upstream = load_card(upstream_id)
        if upstream is None:
            continue

        back_ref = {
            "card_id": downstream_id,
            "channel": link.get("channel"),
            "evidence_excerpt": link.get("evidence_excerpt", ""),
            "source_ref": link.get("source_ref", ""),
            "justification": link.get("justification", ""),
        }

        existing = upstream.get("propagates_to", []) or []
        if any(e.get("card_id") == downstream_id for e in existing):
            existing = [e for e in existing if e.get("card_id") != downstream_id]
        existing.append(back_ref)
        upstream["propagates_to"] = existing
        upstream["version"] = (upstream.get("version") or 1) + 1

        upstream_path = CASES_DIR / upstream_id / "card.json"
        upstream_path.write_text(
            json.dumps(upstream, indent=2, default=str, ensure_ascii=False),
            encoding="utf-8",
        )
        touched.append(upstream_id)
    return touched


# ---------------------------------------------------------------------------
# Attractor-component detection (§7b, AT1–AT3)
# ---------------------------------------------------------------------------

def _card_neighbors(card: dict) -> set[str]:
    """Union of upstream (propagated_from) and downstream (propagates_to)
    card_ids — the edges we walk for connected-component detection."""
    ids: set[str] = set()
    for link in card.get("propagated_from", []) or []:
        if link.get("card_id"):
            ids.add(link["card_id"])
    for link in card.get("propagates_to", []) or []:
        if link.get("card_id"):
            ids.add(link["card_id"])
    return ids


def _connected_component(start_id: str, index: dict[str, dict]) -> set[str]:
    """BFS over the edge set, collecting every card reachable from start."""
    if start_id not in index:
        return set()
    seen: set[str] = {start_id}
    stack = [start_id]
    while stack:
        current = stack.pop()
        for nbr in _card_neighbors(index[current]):
            if nbr in index and nbr not in seen:
                seen.add(nbr)
                stack.append(nbr)
    return seen


def _aggregate_component(members: Iterable[dict]) -> dict:
    """Compute AT2/AT3 inputs: dominant L5 subtypes, asymmetry-vector
    co-occurrence, foreseeability distribution."""
    l5_subtypes: Counter[str] = Counter()
    av_types: Counter[str] = Counter()
    foreseeability: Counter[str] = Counter()

    for card in members:
        for c in card.get("classifications", []) or []:
            if c.get("layer") == "L5":
                # Subtype may be on the classification or derivable from mode_id;
                # v0.6 prompts emit mode_id (MP-XXX); taxonomy ties MP → L5<x>.
                subtype = c.get("subtype") or c.get("mode_id", "")
                l5_subtypes[subtype] += 1
        for v in card.get("asymmetry_vectors", []) or []:
            if v.get("type"):
                av_types[v["type"]] += 1
        for role in card.get("constitutive_roles", []) or []:
            if role.get("foreseeability"):
                foreseeability[role["foreseeability"]] += 1

    return {
        "dominant_l5_subtypes": [{"subtype": k, "count": v} for k, v in l5_subtypes.most_common()],
        "dominant_asymmetry_vectors": [{"type": k, "count": v} for k, v in av_types.most_common()],
        "foreseeability_profile": dict(foreseeability),
    }


def _meets_AT2(component_stats: dict) -> bool:
    """AT2 — ≥N member cards share an L5 subtype OR co-occurring AV.
    N is ATTRACTOR_MIN_MEMBERS (4 in v0.6)."""
    for entry in component_stats.get("dominant_l5_subtypes", []):
        if entry["count"] >= ATTRACTOR_MIN_MEMBERS:
            return True
    for entry in component_stats.get("dominant_asymmetry_vectors", []):
        if entry["count"] >= ATTRACTOR_MIN_MEMBERS:
            return True
    return False


def _meets_AT3(component_stats: dict) -> bool:
    """AT3 — majority of constitutive_roles entries across member cards
    carry foreseeability ∈ {documented_in_record, partial}."""
    dist = component_stats.get("foreseeability_profile", {})
    total = sum(dist.values())
    if total == 0:
        return False
    seen = dist.get("documented_in_record", 0) + dist.get("partial", 0)
    return seen * 2 > total  # strict majority


def _existing_attractor_covers(component_ids: set[str]) -> bool:
    """Return True if any published attractor already names this exact
    component (by member_card id-set). Keeps the Compiler from re-flagging."""
    if not ATTRACTORS_DIR.exists():
        return False
    for path in ATTRACTORS_DIR.glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if set(record.get("member_cards", [])) == component_ids:
            return True
    return False


def _component_signature(component_ids: set[str]) -> str:
    """Deterministic signature for the member-card set."""
    return "||".join(sorted(component_ids))


def detect_attractor_component(
    card: dict,
    catalog: list[dict] | None = None,
) -> CandidateAttractorFlag | None:
    """Walk the DAG from `card`, compute AT1–AT3, and emit a candidate flag
    if thresholds are crossed and no attractor record yet covers the
    component. Returns None when no flag is warranted.

    AT1 (component boundary) is satisfied by construction: the component is
    defined by the propagation DAG, which is a consistently applied
    criterion. AT2 and AT3 are computed from the aggregated statistics.
    AT4 is analyst-authored and cannot be emitted by the Compiler."""
    if catalog is None:
        catalog = load_catalog()

    index: dict[str, dict] = {c["id"]: c for c in catalog if c.get("id")}
    if card.get("id") not in index:
        index[card["id"]] = card

    component_ids = _connected_component(card["id"], index)
    if len(component_ids) < ATTRACTOR_MIN_MEMBERS:
        return None

    members = [index[i] for i in component_ids]
    stats = _aggregate_component(members)

    if not _meets_AT2(stats):
        return None
    if not _meets_AT3(stats):
        return None
    if _existing_attractor_covers(component_ids):
        return None

    flag = CandidateAttractorFlag(
        component_signature=_component_signature(component_ids),
        member_cards=sorted(component_ids),
        dominant_l5_subtypes=stats["dominant_l5_subtypes"],
        dominant_asymmetry_vectors=stats["dominant_asymmetry_vectors"],
        foreseeability_profile=stats["foreseeability_profile"],
        flagged_by_card=card.get("id", ""),
    )

    # Persist the flag for the analyst queue. Append-only log so history
    # is visible even when analyst authors (or does not author) the attractor.
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    with FLAGS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(flag), default=str, ensure_ascii=False) + "\n")

    return flag
