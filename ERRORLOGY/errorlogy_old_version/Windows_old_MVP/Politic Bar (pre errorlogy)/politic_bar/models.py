"""Data contracts for the errorlogy pipeline (METHODOLOGY v0.6). # touch

Every agent reads and writes instances of these models. They are the interface
between stages; each model enforces the parts of the methodology that can be
enforced at the type level (e.g. no card ships without sources; every
classification carries its layer; every asymmetry vector carries its channel).

v0.6 schema reflects:
- §2a event types (decision / non_decision / unstable_decision)
- §3 full card schema with constitutive_roles, asymmetry_vectors,
  propagated_from / propagates_to
- §5 / §5a / §5c / §5d classifications across L1–L5 (three taxonomies)
- §7a actor profile (derived, Compiler-maintained)
- §7b attractor record (derived, analyst-authored on Compiler flag)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Literal, Optional


Branch = Literal["executive", "legislative", "judicial", "regulatory", "other"]
Level = Literal["national", "subnational", "local", "supranational"]
Confidence = Literal["high", "medium", "low"]
EventType = Literal["decision", "non_decision", "unstable_decision"]
Layer = Literal["L1", "L2", "L3", "L4", "L5"]
Foreseeability = Literal["documented_in_record", "partial", "absent"]
AsymmetryVectorType = Literal["AV1", "AV2", "AV3", "AV4", "AV5"]


# ---------------------------------------------------------------------------
# Sources and citations
# ---------------------------------------------------------------------------

@dataclass
class Source:
    """A linkable, dated source. Every factual claim in a card traces back
    to at least one Source."""

    title: str
    url: str
    published_date: Optional[str] = None   # ISO 8601
    accessed_date: Optional[str] = None    # ISO 8601
    source_type: Literal["primary", "secondary"] = "primary"
    notes: Optional[str] = None


@dataclass
class Citation:
    """A specific excerpt from a source, quoted verbatim, with a locator."""

    source_id: str                          # matches Source.title or an assigned id
    excerpt: str                            # the quoted material
    locator: Optional[str] = None           # e.g. "para 4", "§III.B", "p. 12"


# ---------------------------------------------------------------------------
# Pipeline stage outputs
# ---------------------------------------------------------------------------

@dataclass
class Skeleton:
    """Scout output. Everything the Framer needs to start writing."""

    country: str
    branch: Branch
    level: Level
    body: str                               # the institution, not an individual unless they are the institution
    decision_date: str                      # ISO 8601; range allowed ("2020-03-01/2020-04-15")
    event_type: EventType = "decision"      # §2a; default is discrete act
    sources: list[Source] = field(default_factory=list)


@dataclass
class ConstitutiveRole:
    """Per-actor entry in the Framer output. §3, N6.

    Records action/contribution without imputing motive. `foreseeability`
    classifies what the source bundle establishes was accessible to the actor
    at decision time. Empty entries are permitted only when the source bundle
    does not establish action; the analyst justification must then live in
    ErrorCard.analyst_notes (enforced by N6 in the Neutrality Auditor)."""

    actor: str
    action_or_inaction: str
    contribution: str
    foreseeability: Foreseeability
    evidence_excerpt: str
    source_ref: str


@dataclass
class FramedCase:
    """Framer output. The narrative core of the card, each field citable."""

    skeleton: Skeleton
    summary: str                                       # ≤ 3 sentences, descriptive
    claimed: str
    claimed_citations: list[Citation] = field(default_factory=list)
    known_or_knowable: str = ""
    known_citations: list[Citation] = field(default_factory=list)
    decision: str = ""
    decision_citations: list[Citation] = field(default_factory=list)
    gap: str = ""                                      # factual delta, neutral
    constitutive_roles: list[ConstitutiveRole] = field(default_factory=list)


@dataclass
class AsymmetryVector:
    """§5b. One documented asymmetric channel active in the decision-event.

    `type` is one of AV1-AV5 (vertical hierarchy, horizontal interagency,
    regulator-operator, state-citizen, temporal). `between` names the two
    parties across which the asymmetry was active. Validity enforced by
    A1–A3 in the Chain-Mapper prompt."""

    type: AsymmetryVectorType
    between: str
    evidence_excerpt: str
    source_ref: str


@dataclass
class PropagationLink:
    """§5b. Proposed upstream dependency on an existing catalog card.

    `channel` is the AV1–AV5 type through which the error propagated.
    Validity enforced by P1–P3 (cited channel, documented carry-forward,
    surviving lower-cause-sufficiency test) in the Chain-Mapper + Red-Team."""

    card_id: str
    channel: AsymmetryVectorType
    evidence_excerpt: str
    source_ref: str
    justification: str = ""


@dataclass
class Classification:
    """One classification against one of the three taxonomies.

    `layer` is L1/L2/L3 (cognitive_biases.json), L4 (strategic_failure_modes.json),
    or L5 (mechanism_pathologies.json). `mode_id` is the canonical id
    (CB-XXX, SF-XXX, MP-XXX). `bias_id` retained as legacy alias for
    backward compatibility with pre-v0.4 seed cards."""

    mode_id: str
    mode_name: str
    layer: Layer
    evidence_excerpt: str
    source_ref: str
    confidence: Confidence
    justification: str

    # Legacy alias: older seed cards used bias_id / bias_name. Populated
    # automatically so downstream code can read either shape.
    @property
    def bias_id(self) -> str:
        return self.mode_id

    @property
    def bias_name(self) -> str:
        return self.mode_name


@dataclass
class CounterArgument:
    """Adversarial rebuttal. Every classification, AV, propagation link, and
    foreseeability assignment gets at least one. §5a/§5c/§5d sufficiency
    tests are recorded in `tests_run` and their outcomes in the body of
    `strongest_counter` / `does_it_survive`.

    `targets` identifies what is under attack: a mode_id (CB-/SF-/MP-),
    an AV type, a propagation card_id, a role_actor, or "gap"."""

    targets: str
    target_kind: Literal[
        "classification", "asymmetry_vector", "propagation_link",
        "foreseeability", "gap"
    ] = "classification"
    strongest_counter: str = ""
    does_it_survive: bool = True
    tests_run: list[str] = field(default_factory=list)     # e.g. ["5a_lower_layer", "5d_S3_downward", "5d_S4_applicability"]
    notes: Optional[str] = None


@dataclass
class VerificationResult:
    """Verifier output for one citation."""

    source_id: str
    excerpt: str
    resolves: bool
    quote_matches: bool
    notes: Optional[str] = None


@dataclass
class NeutralityAudit:
    """Neutrality Auditor output. Blocking."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    rewrite_suggestions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Published artifact
# ---------------------------------------------------------------------------

@dataclass
class ErrorCard:
    """The final published artifact. See METHODOLOGY.md §3."""

    id: str
    version: int
    country: str
    branch: Branch
    level: Level
    body: str
    decision_date: str
    event_type: EventType
    summary: str
    claimed: str
    known_or_knowable: str
    decision: str
    gap: str
    classifications: list[Classification] = field(default_factory=list)
    asymmetry_vectors: list[AsymmetryVector] = field(default_factory=list)
    propagated_from: list[PropagationLink] = field(default_factory=list)
    propagates_to: list[PropagationLink] = field(default_factory=list)
    constitutive_roles: list[ConstitutiveRole] = field(default_factory=list)
    counter_arguments: list[CounterArgument] = field(default_factory=list)
    residual_uncertainty: str = ""
    sources: list[Source] = field(default_factory=list)
    analyst_notes: str = ""
    compiled_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Derived views (§7a, §7b)
# ---------------------------------------------------------------------------

@dataclass
class ActorProfileEntry:
    """One card's contribution to an actor's profile. §7a AP1: pure
    aggregation — every field resolves to a citation in the underlying card."""

    card_id: str
    decision_date: str
    body: str
    branch: Branch
    level: Level
    role: Literal["principal", "named_in_roles", "quoted_in_sources"]
    role_detail: str = ""                                  # e.g. the specific constitutive_roles.action_or_inaction
    classifications: list[str] = field(default_factory=list)   # list of "<layer>:<mode_id>"
    foreseeability: Optional[Foreseeability] = None
    asymmetry_vectors: list[AsymmetryVectorType] = field(default_factory=list)
    propagated_from_ids: list[str] = field(default_factory=list)


@dataclass
class ActorProfile:
    """Per-actor aggregated view. Compiler-maintained (§7a AP3)."""

    actor_id: str
    display_name: str
    entries: list[ActorProfileEntry] = field(default_factory=list)
    possibly_same_as: list[str] = field(default_factory=list)
    version: int = 1

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AttractorRecord:
    """§7b. Analyst-authored derived object describing a connected sub-graph
    of cards that stabilizes at a suboptimal equilibrium. Published only
    when AT1–AT4 all hold; AT4 (documented_exit) is the analyst-authored
    citation that the Compiler cannot generate."""

    attractor_id: str
    scope: str                                             # geographic / functional / temporal boundary
    member_cards: list[str] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)        # [{from_card, to_card, channel}]
    dominant_l5_subtypes: list[dict] = field(default_factory=list)          # [{subtype, count}]
    dominant_asymmetry_vectors: list[dict] = field(default_factory=list)    # [{type, count}]
    foreseeability_profile: dict = field(default_factory=dict)              # {documented_in_record: n, partial: n, absent: n}
    compounding_signature: str = ""
    documented_exit: list[Citation] = field(default_factory=list)           # AT4; REQUIRED for publication
    counter_arguments: list[CounterArgument] = field(default_factory=list)
    residual_uncertainty: str = ""
    version: int = 1
    compiled_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidateAttractorFlag:
    """Compiler side-effect (§6, §7b): emitted when AT1–AT3 are met but AT4
    is not yet authored. Not published; queued for analyst."""

    component_signature: str                               # stable hash of the member-card set
    member_cards: list[str] = field(default_factory=list)
    dominant_l5_subtypes: list[dict] = field(default_factory=list)
    dominant_asymmetry_vectors: list[dict] = field(default_factory=list)
    foreseeability_profile: dict = field(default_factory=dict)
    flagged_by_card: str = ""                              # the card whose publication triggered the flag
    flagged_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
