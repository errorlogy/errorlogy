# politic.bar — multi-agent architecture

This document describes the implemented pipeline. It is downstream of `METHODOLOGY.md`; any mismatch between the two is a bug in this document.

## The eight-agent pipeline

A decision-event enters as a raw payload — one or more source URLs, quoted text, or file references. It exits as a published error card or an explicit rejection with reason. The pipeline is linear with one adversarial loop. The catalog is consulted by Chain-Mapper to discover upstream propagation links.

```
  raw_source                                       catalog (existing cards)
       │                                                    │
       ▼                                                    │
 ┌──────────┐                                               │
 │  Scout   │  extracts: country, branch, level, body,      │
 └──────────┘  decision_date, sources                       │
       │                                                    │
       ▼                                                    │
 ┌──────────┐                                               │
 │  Framer  │  writes: summary, claimed, known_or_knowable, │
 └──────────┘  decision, gap                                │
       │                                                    │
       ▼                                                    │
 ┌────────────────┐  reads framed case + catalog;           │
 │  Chain-Mapper  │◄─ identifies asymmetry vectors (AV1-5);─┘
 └────────────────┘  proposes propagated_from links
       │
       ▼
 ┌────────────────────────┐
 │ Failure-Mode Classifier│  nominates: classifications[] across L1/L2/L3/L4/L5
 └────────────────────────┘  with evidence + confidence + layer
       │
       ▼
 ┌──────────┐
 │ Red-Team │  writes: counter_arguments for each classification,
 └──────────┘  asymmetry vector, and propagation link;
       │       runs lower-layer-sufficiency (§5a) and
       │       lower-cause-sufficiency (§5b) tests
       │                 ↑
       │    loop: if Red-Team defeats ≥1 classification or link,
       │          relevant prior agent re-runs
       ▼
 ┌──────────┐
 │ Verifier │  every citation must resolve; quotes must be accurate;
 └──────────┘  asymmetry/propagation citations included
       │
       ▼
 ┌───────────────────┐
 │ Neutrality Auditor│  enforces §4 of METHODOLOGY. Has veto.
 └───────────────────┘  Special attention to asymmetry/propagation
       │                language (no imputation of intent).
       ▼
 ┌───────────────┐
 │ Card Compiler │  emits final JSON + Markdown; assigns id + version;
 └───────────────┘  updates propagates_to on referenced upstream cards
       │
       ▼
   error_card  +  catalog_topology_update
```

## Agent contracts

Every agent has (a) a fixed system prompt, (b) a typed input schema, (c) a typed output schema, (d) an explicit failure mode. Agents do not share hidden state. Intermediate outputs are persisted so any card can be rebuilt, audited, or branched.

**Scout.** Input: raw source bundle. Output: decision-event skeleton, including `event_type ∈ {decision, non_decision, unstable_decision}` per §2a. For `non_decision` the skeleton must establish (a) mandated decision window, (b) the window closed with no output, (c) the institutional mechanism of the null output. For `unstable_decision` the skeleton must establish ≥2 reversals within a defined window with no material new information between reversals. Failure mode: cannot establish attributable body or decision (or, for non/unstable events, the §2a admissibility conditions) — pipeline halts with "unqualified event."

**Framer.** Input: skeleton + source bundle. Output: the five narrative fields, each with at least one citation, plus initial `constitutive_roles` entries for every actor named in the body or sources (per `METHODOLOGY.md` §3 and N6). Each role entry classifies `foreseeability` against what the source bundle establishes was accessible to that actor at decision time. Empty role entries are permitted only when the source bundle does not establish action; the analyst justification must then be written into `analyst_notes`. Failure mode: cannot cite any of `claimed / known_or_knowable / decision` — pipeline halts with "insufficient record."

**Chain-Mapper.** Input: framed case + the existing card catalog. Output: `{asymmetry_vectors: [{type, between, evidence_excerpt, source_ref}], candidate_propagated_from: [{card_id, channel, evidence_excerpt, source_ref, justification}]}`. Implements `METHODOLOGY.md` §5b: tags asymmetry vectors per A1–A3 and proposes upstream propagation links per P1–P3. The catalog is queried by `country / branch / body / decision_date_range / topic_keywords`. Failure mode: none of structural significance — empty output is legitimate (the decision-event may be the upstream root of a chain, or the catalog may not yet contain its precedents). The only hard failure is producing an asymmetry claim with no documentable channel (A1), in which case that claim is dropped.

**Failure-Mode Classifier.** (Renamed from "Bias Classifier" in v0.4.) Input: full framed case + three taxonomies (`taxonomy/cognitive_biases.json` for L1/L2/L3, `taxonomy/strategic_failure_modes.json` for L4, `taxonomy/mechanism_pathologies.json` for L5). Output: zero or more classifications, each with `{mode_id, layer, evidence_excerpt, source_ref, confidence, justification}`. The `layer` is one of `L1` (individual cognitive bias), `L2` (group dynamic), `L3` (informational closure), `L4` (strategic / incentive-misalignment), `L5` (mechanism / aggregation pathology); see `METHODOLOGY.md` §5, §5a, §5c, §5d. The Classifier nominates across all five layers in the same pass and is required to keep their evidence sets distinct (L1 = a decider's stated reasoning; L2 = the meeting structure; L3 = the information environment; L4 = misalignment between documented payoff and observed behavior; L5 = documented constraint of the aggregation mechanism on the problem class). Classifies conservatively. Empty output is a legitimate output. L4 classifications additionally require all of M1–M4 (§5c) on the record before nomination; L5 classifications additionally require all of S1–S4 (§5d). For non_decision and unstable_decision events (§2a), the Classifier reads the `event_type` field and adjusts evidence-frame accordingly: a non-decision's `decided` is null and the mechanism of its production is the fact under classification; an unstable-decision's `decided` is the oscillation pattern.

**Red-Team.** Input: the full case plus all classifications (L1–L5), asymmetry vectors, propagation links, and constitutive_roles entries. Output: for each classification, the strongest alternative explanation; for each asymmetry vector and propagation link, the strongest case that the channel was symmetric or the dependency local; for each foreseeability assignment, the strongest case that the cited record was not in fact accessible to the actor at decision time; for the overall gap, an attempt to dissolve it. Runs the §5a **lower-layer-sufficiency test** (L1 sufficient → L2/L3 drop; L2 sufficient → L3 drops). Runs the §5b **lower-cause-sufficiency test** against propagation links. Runs the §5c **L4 lower-layer test (M3)**: can the behavior be explained at L1/L2/L3 or §5b without invoking incentive misalignment? If yes, L4 drops. Runs the §5d **L5 bidirectional sufficiency test (S3)** in both directions: (a) can the outcome be explained at L1/L2/L3/L4/§5b without invoking mechanism pathology? If yes, L5 drops. (b) Does the named mechanism pathology make a nominated lower-layer classification redundant on the same evidence? If so, the redundant lower-layer drops; co-classification requires distinct evidence sets. Runs the §5d **alternative-existence test (S4)**: the cited alternative mechanism must be applicable to the problem class, not merely named; if applicability conditions differ, S4 fails and L5 drops. Failure mode: any defeated classification, link, or claim is downgraded or dropped; card is re-versioned.

**Verifier.** Input: the case plus every citation. Output: per-citation {resolves, quote_matches, notes}. Failure mode: any citation does not resolve → card reverts to draft.

**Neutrality Auditor.** Input: the full assembled case text (or authored attractor). Output: {pass/fail, violations[], rewrite_suggestions[]}. Has veto over the Compiler: cannot publish until pass. Pays particular attention to L5 language (mechanism constraint, not editorial complaint), the S4 documented-alternative clause (absent S4 an L5 entry is fatalistic editorial), non_decision / unstable_decision framings (the null or oscillation is the fact; Auditor rejects language that narrates an intent behind the absence), and **attractor** framings per §7b (AT4 documented-exit clause required; "the system is broken" or "dysfunction is endemic" rejected; "component C meets AT1–AT3 on the recorded cards, and the analog context X [citation] demonstrates exit from an equivalent component" passes). Failure mode: none — the Auditor is designed to fail cards; that is the feature.

**Card Compiler.** Input: the final approved case. Output: canonical JSON card + rendered Markdown + assigned id + version 1. Persists prior stages. **Catalog side-effects:** (a) for every approved `propagated_from[i].card_id`, appends a corresponding `propagates_to` entry to that upstream card and bumps its version — the error topology (the DAG of cards) is always two-way navigable. (b) For every actor in `body`, `constitutive_roles`, or named-in-sources of the new card, appends or updates a row in `actors/{actor_id}.json` per `METHODOLOGY.md` §7a — actor profiles are derived, never authored, and contain no propositions not already in the underlying cards (AP1). (c) Runs attractor-component detection per `METHODOLOGY.md` §7b: walks `propagated_from` / `propagates_to` from the new card, identifies the connected component, recomputes dominant L5 sub-types, asymmetry-vector co-occurrence, and foreseeability distribution; if AT1–AT3 thresholds are crossed and no attractor record exists for the component, emits a `candidate_attractor_flag` to the analyst queue. **Attractors are not auto-published** — AT4 (documented exit citation) requires analyst authoring. An authored attractor is routed back through Red-Team (attacks AT1–AT4, especially AT4's applicability) and Neutrality Auditor (rejects "system is broken" language; accepts "this component meets AT1–AT4 thresholds, and the Ostrom-analog in context X shows exit was available") before publication to `catalog/attractors/{attractor_id}.json`.

## Why this shape

Five properties of the pipeline are load-bearing:

1. **Adversarial separation.** The Classifier and the Red-Team are run as separate invocations with separate prompts. The Red-Team is not asked "is this right"; it is asked "destroy this." That is the engineered asymmetry the methodology requires.

2. **Citation-first.** No agent downstream of the Framer can introduce new factual claims. If a later agent needs a fact, it is a routing instruction back to the Scout or Framer, not a free-write. This keeps the card grounded in a fixed evidence set and makes re-audit deterministic.

3. **Neutrality as veto, not suggestion.** The Neutrality Auditor runs last and has blocking authority. Every card that ships has passed this gate. Gate outputs are logged; violations caught and fixed are retained as quality data on the pipeline itself.

4. **Stateless, replayable.** Each stage reads persisted inputs and writes persisted outputs. Re-running a card under an updated taxonomy or an updated prompt is a matter of replaying from the relevant stage. The pipeline is an error log for itself.

5. **Topology, not just nodes.** Chain-Mapper plus the Compiler's two-way link maintenance turn the catalog into a navigable DAG of decision-events, not a flat list. The catalog's value scales super-linearly with size: every new card potentially closes propagation links to many existing ones. Patterns emerge as repeated topologies, not as repeated keywords.

## Where the model runs

The reference implementation in `politic_bar/` calls the Anthropic API with a single key. Each agent is a Claude invocation with a role-specific system prompt and a strict JSON output contract. Any LLM with strong instruction-following and long-context ingestion can be substituted; agent contracts are the interface, not the model family.

## Out of scope for v0.1

- Automated source discovery (v0.1 accepts a hand-curated bundle; v0.2 adds retrieval).
- Automatic duplicate detection across cards.
- A writeable public comment layer. The dashboard in v0.1 is read-only.
- Retrospective re-analysis on taxonomy upgrades (designed for but not yet implemented).
