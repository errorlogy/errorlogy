# politic.bar

> **STATUS: OLD SKETCH** — historical MVP for idea development, not the active product codebase.  
> Project docs: `ERRORLOGY_MVP_OBSIDIAN/` · repo `README.md` / `AGENTS.md`

*The first applied product of **errorlogy** — the study of errors as first-class observable objects.*

politic.bar is a multi-agent system that records, against a stable taxonomy, the gap between what governing bodies claim, what is in the public record at the time, and what they decide. It does not accuse. It records. Every entry is citation-backed, adversarially reviewed, and neutrality-audited. Every entry is versioned rather than deleted. The catalog is the product.

This repository is the MVP (v0.1). It contains the methodology, the taxonomy, the multi-agent pipeline, five hand-analyzed seed cases, and a static catalog dashboard.

## Start here

- [**`METHODOLOGY.md`**](METHODOLOGY.md) — the protocol. Read this first. Everything else is downstream.
- [**`dashboard.html`**](dashboard.html) — open in any browser. Filterable catalog of the seed cases.
- [**`ARCHITECTURE.md`**](ARCHITECTURE.md) — the eight-agent pipeline (with the Chain-Mapper added in v0.3) and why it has this shape.
- [**`taxonomy/cognitive_biases.json`**](taxonomy/cognitive_biases.json) — 189 failure modes across three layers (L1 individual cognitive bias, L2 group dynamics, L3 informational closure / echo chamber), with operational definitions and government-decision detection cues. See `METHODOLOGY.md` §5 and §5a.
- [**`taxonomy/strategic_failure_modes.json`**](taxonomy/strategic_failure_modes.json) — 14 strategic / incentive-misalignment failure modes (L4: career protection, rent-seeking, factional loyalty over mandate, bounded-mandate externality, persistent claim without competence-deferral). See `METHODOLOGY.md` §5c.
- [**`taxonomy/mechanism_pathologies.json`**](taxonomy/mechanism_pathologies.json) — 14 mechanism / aggregation-pathology modes (L5: social-choice impossibility, price-of-anarchy, common-pool failure, transaction-cost veto, agenda cycling, jurisdictional mismatch, temporal compounding / oscillation, deadlock). See `METHODOLOGY.md` §5d.

## What is errorlogy

errorlogy is a framing, not a brand. Four claims:

1. Governance is management — presidents, ministers, regulators, committees are managers operating under uncertainty, and subject to the same failure modes any manager is subject to.
2. Title is not competence. Holding an office grants authority to act. It does not grant the capacity to act well. The gap between the two is observable.
3. Errors are observable through gaps, not through outcomes. The system records the delta between claimed / known / decided, not the outcome.
4. A catalog beats an accusation. A named failure mode from a documented taxonomy is testable. A moral verdict is not.

See `METHODOLOGY.md` §1 for the detailed form.

## Repository layout

```
POLITIC.BAR/
├── METHODOLOGY.md              The protocol. The thing the product is.
├── ARCHITECTURE.md              Pipeline design; implementation notes.
├── README.md                    This file.
├── dashboard.html               Single-file catalog viewer (open in browser).
│
├── taxonomy/
│   ├── cognitive_biases.json    189 failure modes × {id, name, definition,
│   │                             category, government_decision_cue, layer}.
│   │                             L1 individual / L2 group / L3 informational
│   │                             closure (see METHODOLOGY.md §5 and §5a).
│   ├── strategic_failure_modes.json
│   │                             14 strategic / incentive-misalignment modes
│   │                             (L4) × {id, name, subtype, definition,
│   │                             operational_signature}. Sub-types L4b /
│   │                             L4c / L4e / L4g / L4h (see METHODOLOGY.md §5c).
│   └── mechanism_pathologies.json
│                                 14 mechanism / aggregation-pathology modes
│                                 (L5) × {id, name, subtype, definition,
│                                 operational_signature}. Sub-types L5a–L5h
│                                 (see METHODOLOGY.md §5d).
│
├── politic_bar/                 Multi-agent pipeline implementation (Python).
│   ├── __init__.py
│   ├── models.py                Dataclasses: Skeleton, FramedCase,
│   │                            Classification, ErrorCard, etc.
│   ├── prompts.py               Per-agent system prompts (Scout, Framer,
│   │                            Chain-Mapper, Failure-Mode Classifier,
│   │                            Red-Team, Verifier, Neutrality Auditor,
│   │                            Compiler).
│   ├── agents.py                Thin Claude-API wrappers, one per agent.
│   └── pipeline.py              Orchestrator; composes agents into the full
│                                pipeline and persists every stage.
│
├── cases/                       One directory per case.
│   ├── US-NASA-1986-CHALLENGER-01/
│   │   └── card.json            Final error card.
│   ├── SU-USSR-1986-CHERNOBYL-01/
│   ├── US-IC-2002-IRAQ-WMD-01/
│   ├── GB-POL-1999-HORIZON-01/
│   └── US-MMS-2010-DEEPWATER-01/
│
├── actors/                      Derived actor profiles (§7a). Regenerated
│                                by the Card Compiler from the cards; no
│                                propositions introduced beyond AP1–AP3.
│
├── catalog/
│   └── attractors/              Authored anti-consensus attractor records
│                                (§7b). Candidate-attractor flags emitted
│                                by the Compiler when AT1–AT3 thresholds
│                                cross; AT4 (documented exit) requires
│                                analyst authoring. Reviewed by Red-Team
│                                and Neutrality Auditor before publication.
│
└── run.py                       CLI: python run.py <case_id> <source_bundle.txt>
```

## The seed cases

Five cases are shipped with v0.1. All have been analyzed end-to-end by hand-application of the methodology. They exist to (a) demonstrate that the protocol produces coherent, comparable cards across very different decision-events and (b) serve as regression fixtures when the pipeline is changed.

| ID | Country | Branch | Year(s) | What is recorded |
|---|---|---|---|---|
| `US-NASA-1986-CHALLENGER-01` | US | executive | 1986 | Pre-launch teleconference and authorization of STS-51L. |
| `SU-USSR-1986-CHERNOBYL-01` | SU | executive | 1986 | Unit 4 rundown-coast-down test. |
| `US-IC-2002-IRAQ-WMD-01` | US | executive | 2002–2003 | October 2002 NIE on Iraqi WMD programs. |
| `GB-POL-1999-HORIZON-01` | GB | regulatory | 1999–2015 | Post Office private prosecutions on Horizon evidence. |
| `US-MMS-2010-DEEPWATER-01` | US | regulatory | 2003–2010 | MMS oversight of deepwater drilling pre-Macondo. |

Open `dashboard.html` to browse them.

## Running the pipeline

The pipeline is runnable with an Anthropic API key. It takes a plain-text *source bundle* — the analyst's curated collection of primary-source excerpts and URLs — and produces a full error card through the seven stages.

```bash
pip install anthropic

export ANTHROPIC_API_KEY=sk-...

# optional — defaults to claude-sonnet-4-6
export POLITIC_BAR_MODEL=claude-sonnet-4-6

python run.py MY-CASE-ID path/to/source_bundle.txt
```

Output:
- `cases/MY-CASE-ID/card.json` — the final error card (if all stages pass).
- `cases/MY-CASE-ID/_pipeline/01_scout.json` through `06_neutrality_audit.json` — the intermediate stage outputs. Every decision the pipeline made is inspectable.

If the pipeline halts — unqualified event, insufficient record, unresolved citation, or blocked by the Neutrality Auditor — no `card.json` is written. The stage outputs tell you why.

## What v0.1 does not do

- No automated source discovery. The source bundle is hand-curated. v0.2 is designed around retrieval over primary-source feeds (government releases, official gazettes, court filings, legislative records).
- No cross-case duplicate detection.
- No writeable public layer.
- No retrospective re-analysis when the taxonomy is upgraded. The plumbing exists (pipeline is stateless and replayable) but is not yet exposed.

## How to extend

- **Add a bias.** Append to `taxonomy/cognitive_biases.json`. Classifier picks it up on next run.
- **Add a classification stream.** The current taxonomy is cognitive. Procedural and informational error taxonomies are planned; the pipeline is parameterized to accept additional taxonomies.
- **Tighten an agent.** Edit the prompt in `politic_bar/prompts.py`. Re-run seed cases as a regression check.
- **Add a card.** Drop a directory in `cases/` with a `card.json` matching the schema in `METHODOLOGY.md §3`. The dashboard picks it up on next regeneration.

## Status

v0.6 — methodology extended with `METHODOLOGY.md` §7b: **anti-consensus attractor pattern** as a derived view over the card DAG. An attractor is not a new per-card classification; it is a catalog-topology object that captures systemic compounding of suboptimality — stable equilibria from which the system does not exit by its own motion, produced by the attractor-generating mechanism cluster (Plott-McKelvey agenda chaos, race-to-the-bottom, Schelling deadlock, group polarization, information cascades, corruption-stable equilibria, coordination-trap lock-ins). Validity requires all of AT1 (component boundary), AT2 (cross-card pattern threshold, N≥4), AT3 (majority `foreseeability ≥ partial`), AT4 (documented exit in an analog context — the Ostrom-style refutation structure). Unlike actor profiles (§7a), attractors are not fully auto-generated: the Card Compiler runs component detection and emits a `candidate_attractor_flag`; the analyst authors the AT4 exit claim; Red-Team and Neutrality Auditor review before publication to `catalog/attractors/{attractor_id}.json`. §5d also gains an explicit **invariant-residual clarification**: every consensus carries a lower-bounded gap from theoretical optimum sourced in seven independent results (Arrow, Gibbard-Satterthwaite, price-of-anarchy, FLP impossibility, Coase-Williamson, Simon, §5b) whose joint non-minimizability is the baseline; L5 classifies only the avoidable excess over the residual, protected operationally by S4. No prior cards are invalidated.

v0.5 — methodology extended with `METHODOLOGY.md` §5d: **L5 mechanism / aggregation pathology layer**. Records outcomes that no actor in the system selected and that would persist under informed, good-faith participation, because the aggregation mechanism has a documented constraint. Eight sub-types: L5a (social-choice impossibility — Arrow / Condorcet / Gibbard-Satterthwaite / Sen), L5b (price-of-anarchy Nash-Pareto gap), L5c (common-pool / collective-action failure without enforcement — Hardin / Olson / Ostrom), L5d (transaction-cost veto — Coase / Williamson), L5e (agenda control / cycling — Plott-McKelvey), L5f (jurisdictional-scope mismatch — Oates / Weingast), L5g (temporal compounding / oscillation without new information), L5h (deadlock / mutual-veto / procedural-parity stalemate — Schelling). L5 validity requires all of S1–S4; Red-Team gains the §5d bidirectional sufficiency test (S3: lower-layer ↔ mechanism-layer co-dominance check) and the alternative-existence test (S4: cited alternative must apply to the problem class, not merely be named — prevents fatalistic editorializing). New taxonomy file [`taxonomy/mechanism_pathologies.json`](taxonomy/mechanism_pathologies.json) with 14 modes (MP-001…MP-014). §2 extended with §2a: two additional event types `non_decision` (mandated window closed with no output; institutional mechanism of the null is the fact) and `unstable_decision` (≥2 reversals within a window with no material new information; pattern is the fact), alongside the default `decision`. Card schema gains `event_type`. Classifier now runs three taxonomies in the same pass. No prior cards are invalidated; existing cards default to `event_type: decision`.

v0.4 — methodology extended with `METHODOLOGY.md` §5c: **L4 strategic / incentive-misalignment layer**. Operationalizes the clean sub-types L4b (career / legacy protection), L4c (rent-seeking), L4e (tribal / factional loyalty over mandate), L4g (bounded-mandate externality), L4h (persistent claim without competence-deferral). Sub-types L4a (status play), L4d (identity defense), L4f (performative-parity obstruction) are named but reserved for v0.5 pending a separate pass on the moral layer. L4 validity requires all of M1–M4; Red-Team gains the §5c M3 lower-layer test — any lower-layer or §5b-level explanation sufficient → L4 drops. New taxonomy file [`taxonomy/strategic_failure_modes.json`](taxonomy/strategic_failure_modes.json) with 14 modes (SF-001…SF-014). Bias Classifier is renamed **Failure-Mode Classifier** and now runs against both taxonomies in the same pass, nominating across all four layers. Card `classifications[]` gains an `L4` slot. No prior cards are invalidated.

v0.3.1 — methodology gains `METHODOLOGY.md` §7a: **actor profile as a derived view**. Profiles aggregate across cards only; they contain no propositions not already in the underlying cards (AP1), no behavior-summaries that would constitute a moral verdict (AP2), and are regenerated rather than hand-edited (AP3). The Card Compiler gains a second side-effect: updating `actors/{actor_id}.json` for every actor named on a new card. No prior cards are invalidated.

v0.3 — methodology extended with `METHODOLOGY.md` §5b: **information asymmetry** as the generator on which L1–L3 manifest, with five operationalized vectors (vertical, horizontal, regulator-operator, state-citizen, temporal) and the **error-compounding** function that turns the catalog from a flat list into a directed acyclic graph of propagated errors. Card schema gains `asymmetry_vectors`, `propagated_from`, `propagates_to`, and `constitutive_roles` (per-actor, per-action records of what was done and whether the contribution was foreseeable to the actor at decision time). §4 gains N6 — silence about an actor's role is a positive empirical claim, not neutrality. Pipeline gains the **Chain-Mapper** agent (between Framer and Classifier); Framer now writes initial constitutive_roles; Red-Team validates foreseeability. v0.2 cards remain valid and can be revised to add the new fields without re-versioning their classifications. Implementation in `politic_bar/` lags the methodology — Chain-Mapper agent, constitutive-roles writer, L4 classifier, and actor-profile maintenance are the next implementation pass.

v0.2 — methodology extended with the layered classification model (`METHODOLOGY.md` §5a): individual cognitive bias (L1), group dynamics (L2), and informational closure / echo chamber (L3). Taxonomy gains a new `informational_environment` category and 9 new entries (CB-182 through CB-189). Existing cards remain valid; their L1 classifications are unchanged.

v0.1 — initial release. Seed catalog. Pipeline implemented and runnable; seed cases produced by hand-application of the methodology to anchor the taxonomy and validate the card schema against real decision-events.

The product is the methodology. The code is a harness.
