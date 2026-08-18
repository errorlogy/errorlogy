# Attractor record — analyst-authored template

This file is a **template, not a published attractor**. Copy it to
`catalog/attractors/{attractor_id}.json` and fill in. METHODOLOGY §7b.

## What an attractor is

A connected sub-graph of cards that stabilizes at a suboptimal equilibrium
the system does not exit by its own motion — produced by the
attractor-generating mechanism cluster (Plott-McKelvey agenda chaos,
race-to-the-bottom, Schelling deadlock, group polarization, information
cascades, corruption-stable equilibria, coordination-trap lock-ins).

An attractor is **not** a per-card classification. It is a derived view
over the DAG, like an actor profile (§7a). The Compiler emits a
`candidate_attractor_flag` to `catalog/candidate_attractor_flags.jsonl`
when AT1–AT3 cross threshold; the analyst then authors AT4 (documented
exit) before publication.

## Validity gate (all four must hold)

| Test | Description | Source |
|------|-------------|--------|
| AT1  | Component boundary applied consistently across the DAG. | Compiler-supplied. |
| AT2  | ≥4 member cards share an L5 subtype OR a co-occurring asymmetry vector. | Compiler-computed. |
| AT3  | Majority of constitutive_roles entries across member cards carry foreseeability ∈ {documented_in_record, partial}. | Compiler-computed. |
| AT4  | Documented exit in an analog context — citation showing an equivalent component class achieved exit. **Analyst-authored.** | Required. |

Without AT4, the record is a candidate flag, not a published attractor.
The Neutrality Auditor will reject "the system is broken" framings;
acceptable framing is "component C meets AT1–AT3 on cards [...], and the
analog context X (citation) demonstrates exit from an equivalent component."

## JSON shape (mirrors `politic_bar.models.AttractorRecord`)

```json
{
  "attractor_id": "ATR-{descriptive-slug}",
  "scope": "geographic / functional / temporal boundary the attractor lives in",
  "member_cards": ["CASE-ID-1", "CASE-ID-2", "..."],
  "edges": [
    {"from_card": "...", "to_card": "...", "channel": "AV1|AV2|AV3|AV4|AV5"}
  ],
  "dominant_l5_subtypes": [{"subtype": "L5c", "count": 4}],
  "dominant_asymmetry_vectors": [{"type": "AV3", "count": 4}],
  "foreseeability_profile": {"documented_in_record": 6, "partial": 2},
  "compounding_signature": "what the per-card gaps add up to at the component level",
  "documented_exit": [
    {"source_id": "ostrom_1990",
     "excerpt": "exact verbatim quote — Verifier will check",
     "locator": "p. 90, Table 3.1"}
  ],
  "counter_arguments": [
    {"targets": "AT4",
     "target_kind": "gap",
     "strongest_counter": "the analog context's institutional preconditions are absent here",
     "does_it_survive": false,
     "tests_run": ["analog_class_match"]}
  ],
  "residual_uncertainty": "what the Red-Team and Verifier left unresolved",
  "version": 1
}
```

## Authoring workflow

1. Pull a candidate flag from `catalog/candidate_attractor_flags.jsonl`.
2. Verify AT1–AT3 against the cited cards (Compiler statistics are reproducible — recompute).
3. Author AT4: find the analog context. The match must be on **problem class**, not on surface features (S4 applicability, §5d).
4. Run Red-Team: attack AT1–AT4, especially AT4's analog-class match.
5. Run Neutrality Auditor: framing must satisfy N1–N7 plus the §7b "no editorial complaint" clause.
6. Save as `catalog/attractors/{attractor_id}.json` with `version: 1`.

## What to never write here

- "The system is broken" / "dysfunction is endemic" — fatalistic editorial.
- AT4 sourced to an analog that differs in problem class — fails S4.
- Members not actually connected in the DAG — fails AT1.
- Foreseeability inferred from outcome rather than from the source-bundle record — fails AT3.
