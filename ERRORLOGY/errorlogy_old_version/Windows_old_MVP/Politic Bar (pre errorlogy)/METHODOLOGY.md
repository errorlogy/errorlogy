# errorlogy — methodology v0.6

**errorlogy** is the study of errors as first-class observable objects. It treats every decision a human system produces as a candidate for classification against a stable taxonomy of failure modes — cognitive, procedural, informational, structural. It does not ask whether the decider is good or bad. It asks what the decision did, what was claimed, what was known, and which documented failure modes the gap between those three matches.

**politic.bar** is the first applied product of errorlogy. It applies the errorlogy protocol to the decisions and inactions of government management, across all countries, branches, and levels.

This document defines the protocol. Everything the system ships — code, agents, cards, dashboards — is downstream of it. If the protocol is wrong, the product is wrong. The code is a harness; the methodology is the product.

---

## 1. Core axioms

The protocol rests on four claims that must be defensible on their own terms, independent of any particular government or decision.

**A1. Governance is management.** A head of state, a minister, a regulator, a mayor, a committee chair — each is a manager operating a system under uncertainty. They plan, decide, allocate, delegate, and report. They are subject to the same failure modes any manager is subject to.

**A2. Title is not competence.** Holding an office carries formal authority to act. It does not carry, and does not create, the cognitive or informational capacity to act well. The gap between the authority and the capacity is observable. It is what the system measures.

**A3. Errors are observable through gaps, not through outcomes.** An outcome can be bad for reasons outside the decider's control; a decision can be sound and still yield disaster. The system records the gap between (a) what was claimed or assumed at the time of the decision, (b) what was in fact known or knowable at the time, and (c) what was decided. Classification applies to the gap, not to the outcome.

**A4. A catalog beats an accusation.** A named failure mode drawn from a documented taxonomy is testable, replicable, and defensible. A moral judgment is none of those things. The protocol produces catalog entries, not verdicts.

---

## 2. What counts as a decision

The unit of analysis is a **decision-event**. A decision-event is any act or refusal-to-act by a person or body holding formal authority, where at least one of the following is true:

- A public record exists (statute, order, regulation, vote, transcript, release).
- An attributable public statement documents the choice or its justification.
- An identifiable body had jurisdiction and a duty-to-act that was not discharged (the inaction case).

A decision-event is recorded regardless of outcome. Inactions are recorded when the duty-to-act is established by law, mandate, or the body's own published scope.

A decision-event is **not** a personality trait, a rumor, an anonymous claim, a satire, a prediction of a decision, or a framing from a single partisan source. If the record is not locatable and attributable, there is no event.

### 2a. Event types (v0.5)

The default decision-event assumes a discrete act whose `claimed / known / decided` triplet is point-in-time. Two additional event types are recognized because the L5 mechanism-pathology layer (§5d) produces outputs that the default form cannot record.

**`event_type: decision`** — default. A discrete act (rule, ruling, vote, appointment, authorization, enforcement action) or a documented refusal-to-act with an identifiable duty-to-act. Evidence triplet is point-in-time.

**`event_type: non_decision`** — the mechanism failed to produce an output when one was structurally required. Admissible only if all three hold: (a) a mandated decision point is documentable (statutory deadline, scheduled vote, expiring authorization, court-ordered ruling window); (b) the window closed or passed with no output attributable to the body; (c) the absence has an institutional mechanism on the record (tie, procedural death, withdrawn motion, expired quorum, failed ratification) — not merely "they didn't get to it." The `decided` field records *the null output and the mechanism of its production*; `claimed` records the mandate; `known_or_knowable` records the evidence that was available at the window.

**`event_type: unstable_decision`** — a sequence of decisions on the same matter that reversed itself two or more times within a bounded window. Admissible only if all three hold: (a) ≥2 documented reversals on the same matter within a defined window; (b) the sequence is attributable to a single identifiable body or a tightly coupled set of bodies; (c) no material new information reached the decision-relevant record between reversals (if it did, the sequence is a series of distinct decision-events, not an unstable-decision event). `claimed / known / decided` is recorded per reversal; the `gap` field records the pattern as the fact, not any single reversal.

For `non_decision` and `unstable_decision` events, classifications across L1–L4 remain applicable where the evidence supports them (a non-decision can be caused by L2 groupthink as easily as by L5 deadlock); L5 is not privileged by event type. The event type changes *what counts as the decided output*, not *which layers can classify it*.

---

## 3. The error card

Every entry the system publishes is an **error card**. The schema is fixed. An entry missing any required field is not published.

```
id                    — stable, human-readable (e.g. US-FDA-2023-OPIOID-01)
country               — ISO 3166 code
branch                — executive | legislative | judicial | regulatory | other
level                 — national | subnational | local | supranational
event_type            — decision | non_decision | unstable_decision (§2a).
                        Default is decision. non_decision and unstable_decision
                        carry additional admissibility requirements.
decision_date         — ISO 8601; range if the decision unfolded over time.
                        For non_decision: the mandated window. For
                        unstable_decision: the window containing the reversals.
body                  — the institution that decided; not individual names unless
                        they are the institution (e.g. a head of state acting alone)
summary               — ≤ 3 sentences, descriptive, no adjectives of judgment
claimed               — what the body said, explicitly, about the decision and
                        its basis, at the time. Direct quotes preferred, cited.
known_or_knowable     — what was in the public record at the time, or available
                        through the body's own channels. Cited.
decision              — what was in fact decided or not done. Cited.
gap                   — the factual delta between claimed / known / decision.
                        Written as a neutral observation, not a charge.
classifications       — list of failure-mode ids from the taxonomies with
                        per-classification evidence, confidence, and layer
                        (L1 / L2 / L3 / L4 / L5). L1-L3 from
                        taxonomy/cognitive_biases.json (§5, §5a); L4 from
                        taxonomy/strategic_failure_modes.json (§5c); L5 from
                        taxonomy/mechanism_pathologies.json (§5d).
asymmetry_vectors     — list of {type ∈ AV1..AV5, between, evidence_excerpt,
                        source_ref}. Per §5b. Records which asymmetric
                        channels shaped the decision-event. Validity per
                        rules A1–A3.
propagated_from       — list of {card_id, channel ∈ AV1..AV5,
                        evidence_excerpt, source_ref}. Per §5b. Upstream
                        cards whose errors were carried into this one
                        through an asymmetric channel. Validity per P1–P3.
propagates_to         — list of {card_id, channel, evidence_excerpt,
                        source_ref}. Reverse links to downstream cards.
                        Maintained as the catalog grows; not required at
                        publish time of this card.
constitutive_roles    — list of {actor, action_or_inaction, contribution,
                        foreseeability ∈ {documented_in_record | partial |
                        absent}, evidence_excerpt, source_ref}. For each
                        named actor in the decision-event (and one entry
                        per distinct action by that actor), records what
                        they did or did not do that became a constitutive
                        part of the gap, and whether the constitutive
                        nature of the action was visible to them at
                        decision time from the record they had access to.
                        Records action and contribution. Does NOT record
                        motive (motive lives in §5c when added; until then
                        is out of scope). Per N6 (§4), an empty
                        constitutive_roles entry for an actor named in the
                        body or sources requires a positive justification —
                        the record was checked and yielded nothing —
                        recorded in analyst_notes.
counter_arguments     — the strongest case that each classification is wrong,
                        generated by an adversarial pass. Required; no entry
                        publishes without at least one serious counter.
                        Also covers asymmetry_vectors and propagation links.
residual_uncertainty  — what the record cannot resolve. Explicit.
sources               — primary sources first, secondary sources second.
                        Each source is linkable and dated.
analyst_notes         — process notes: what was excluded and why.
version               — card version; cards are revised, not deleted, when
                        new evidence enters the record.
```

A card with no cited `claimed`, no cited `known_or_knowable`, or no cited `decision` is a draft, not an entry. Drafts do not publish.

---

## 4. The neutrality contract

The product's single most important commitment is **records, not accuses**. The contract is enforceable, not aspirational.

**N1. Descriptive language only.** No adjectives of moral judgment (`corrupt`, `reckless`, `brave`, `wise`), no verbs of intent without evidence (`schemed`, `ignored` — unless documented), no emotionally loaded framings. The Neutrality Auditor agent (§6) rejects cards that fail this check.

**N2. No imputation of motive.** A gap is recorded. A motive is not inferred unless the motive is itself in the record (e.g. a minister stated the reason). "We do not know why" is an acceptable card field; a speculated why is not.

**N3. Symmetry.** Every decision-event is eligible regardless of who made it. The protocol does not weight countries, parties, ideologies, or eras. Selection is driven by (a) the presence of a complete record and (b) the severity criterion in §7, nothing else.

**N4. Counter-arguments are mandatory.** No card publishes without an adversarial pass that attempts, in good faith, to defeat each classification. If the strongest counter-argument succeeds, the classification is downgraded or removed. Counter-arguments are published with the card.

**N5. Corrections over deletions.** If a card is shown to be wrong, it is versioned and annotated, not removed. The error log is an error log.

**N6. Participation is recorded; silence is a claim, not neutrality.** Every actor named in the body or sources of a decision-event has a `constitutive_roles` entry — describing what they did or did not do that contributed to the gap, with foreseeability classified per §3. An empty entry is itself a positive empirical claim ("the record was checked and yields no documented contribution") and must carry a justification in `analyst_notes`. The protocol refuses to record motive without evidence; it equally refuses to absolve participation through silence. The two refusals are symmetrical, and N6 makes the second one explicit. Recording action and contribution does not impute intent — that distinction is enforced by N1 and N2.

---

## 5. Bias classification (L1 — individual)

The cognitive-bias layer is one classification stream among several (others: procedural errors, information errors, incentive errors). Its catalog is the cognitive biases documented in the cognitive-science literature (see `taxonomy/cognitive_biases.json`). This section governs **L1** classifications — biases attributable to a specific decider's reasoning. The collective-deliberation layer (**L2**) and the information-environment layer (**L3**) are governed by §5a.

A classification is valid when three conditions are jointly satisfied:

**C1. Manifestation in the record.** There is a specific, citable element of the decision-event (a statement, a vote, a published rationale, a documented omission) that matches the bias's operational definition.

**C2. Stronger than the base rate.** The bias-based explanation fits the observed behavior better than a neutral procedural explanation (e.g. "they didn't know" / "the meeting ran out of time"). If the procedural explanation fully accounts for the behavior, no bias is added.

**C3. Survives the counter.** The adversarial pass (§6, Red-Team) does not produce a stronger alternative bias or a non-bias explanation that fits the evidence better.

Multiple classifications may apply to one card. Classifications carry a confidence band (`high | medium | low`) reflecting how cleanly C1–C3 are satisfied, and a short evidence string pointing at the exact record element that triggered the match.

**Out of scope for classification:** personality diagnosis, armchair psychiatry, partisan frames ("right-wing bias" / "left-wing bias" are not cognitive biases and are never classifications here), and biases that the record cannot distinguish from plain uncertainty.

---

## 5a. Layered classification: individual / group / environmental

A decision rarely fails at one layer. Classifying only individual cognitive bias when the deliberative process or the information environment did the actual work commits a methodological error of our own — a fundamental attribution error (CB-030) on the part of the analyst. The protocol therefore separates three layers of evidence and requires each to be classified on its own terms.

**L1 — Individual cognitive bias.** Governed by §5. The evidence is at the level of what one decider, or a specifiable subset, said, wrote, or omitted. Classification answers: *which documented bias does this person's reasoning match?*

**L2 — Group dynamics.** The failure is a property of how the group deliberated, not of any one mind in it. The same individuals, in a different room, would have produced a different output. The evidence lives in meeting structure, sign-off pattern, dissent record, agenda design, who-was-in-the-room, who-spoke-first, who held the veto.

**L3 — Informational closure (echo chamber).** The deliberating body operated inside an information environment that pre-filtered the inputs available to deliberation. The evidence lives in what the body could and could not see — the source diet, the briefing pipeline, the advisor composition, the channels by which inbound contradiction arrived or did not arrive.

Layers compound. A common failure pattern is L3 → L2 → L1: a closed information environment produces a homogenous briefing, which produces a unanimous meeting, which produces a decider who confidently asserts a view that no source in the room contradicts. Classifying only the L1 bias misses the load-bearing structure.

### L2 — Group dynamics

Group dynamics are the failure modes of collective deliberation. They are not the sum of the individual biases of the participants. They emerge from how the group is structured.

A group-dynamics classification is valid when:

**G1. Structural artifact in the record.** A deliberative artifact (minutes, transcript, sign-off sheet, vote tally, agenda) shows a feature consistent with the named dynamic — unanimity on contested matters, no registered dissent, single-source briefings, no devil's-advocate role, sequential sign-off without convergent debate, etc.

**G2. Process-bound, not person-bound (where testable).** The same individuals have produced contrary outputs in other rooms or at other times, or the dynamic survives across rotations of personnel in the same body. Where this counterfactual is unavailable in the record, the classification carries lower confidence and is flagged.

**G3. Catalog match.** The structural feature matches an entry in the taxonomy under `category: "group"`.

The system does not assert a group dynamic in the absence of any record of how the group deliberated. "We do not know how they decided" is residual uncertainty, not a classification.

### L3 — Informational closure (echo chamber)

In this protocol, *echo chamber* is not a metaphor and not a partisan label. It names a measurable structural condition: the deliberating body's accessible information set was narrower than the question required, in a way the body either created or failed to correct.

An L3 classification is valid when at least two of the following are present in the record:

**E1. Source monoculture.** Briefings, advisors, intelligence streams, or expert panels feeding the decision drew from a homogeneous origin (one agency, one ideological cluster, one contractor, one vetted list) and the homogeneity was not justified by the question.

**E2. Suppressed or excluded contradiction.** Dissenting analyses existed within the body's reach (internal memos, alternative-views channels, minority reports, dissenting expert testimony) and were not surfaced in the deliberation record, were demoted, classified out of view, or routed past the deciders.

**E3. Closed feedback loop.** Outbound communications were primarily addressed to audiences that mirrored the inputs (friendly press, allied agencies, in-network experts), with no scheduled exposure to hostile-witness, red-team, or adversarial-review channels.

**E4. Selection-for-agreement in personnel.** Personnel changes preceding the decision systematically replaced dissenting voices with concurring ones, with the dissenting voices' published positions documented in the prior record.

E1–E4 are environmental, not psychological. They are observable from organizational records, calendars, distribution lists, briefing logs, and personnel actions. The classification names a property of the room, not of the people inside it.

### Avoiding double-count across layers

A card must not classify the same evidence at multiple layers. Rules:

- One decider's stated reasoning → **L1 only**.
- The structure of the meeting that produced the decision → **L2 only**.
- The information environment the meeting operated inside → **L3 only**.
- A card may carry classifications from all three layers when each layer rests on independently citable evidence.
- The Red-Team agent (§6) is required to attempt a **lower-layer sufficiency** defense: can the L1 evidence alone explain the failure without invoking L2 or L3? If yes, the higher layers are downgraded or removed. The same test runs L2 against L3.

### What L2 and L3 are not

They are not synonyms for "bad culture" or "captured agency." Both labels are conclusions the protocol does not draw. L2 and L3 record specific structural and informational features of a specific decision; they do not characterize the institution as a whole, do not impute motive, and do not predict future behavior. The Neutrality Auditor (§6) enforces this against L2/L3 cards with the same rigor it applies to L1.

---

## 5b. Information asymmetry and error compounding

§5 (L1) and §5a (L2, L3) classify failures as properties of a single decider, a single deliberation, or a single information environment. They treat each decision-event as an isolated unit. This section adds the cross-event structure: information rarely flows symmetrically between bodies, levels, or moments, and errors propagate along the asymmetric channels — compounding multiplicatively, not additively. Without this layer, the same error appears in many cards as many "individual" failures when in fact one structural failure is being expressed many times.

This is a methodological commitment: information asymmetry is not another classification category alongside L1–L3. It is the **generator** on which L1, L2, and L3 operationalize. An L1 bias is in many cases downstream of an asymmetry that protected the bias from correction; an L3 closure is often the *result* of an asymmetry that benefits whoever benefits from the closure. The asymmetry layer makes the upstream structural cause visible; the L1–L3 layers continue to record the local manifestations.

### Asymmetry vectors

Five vectors are tracked. They are not the only possible vectors — they are the ones the protocol commits to operationalizing in v0.3. New vectors may be added in later versions; existing ones are not redefined without a version bump.

**AV1 — Vertical (principal-agent across hierarchy levels).** Information held at one level of a hierarchy is not available at another, and the missing party holds decision authority. Classical: minister cannot see what inspector sees; inspector cannot see what operator sees; operator cannot see what front-line worker sees. The asymmetry is built into the chain of command and intensifies with the number of intermediating layers.

**AV2 — Horizontal (across bodies at the same level).** Two bodies of comparable standing operate on different information sets and either do not exchange or exchange too late. Classical: agency-to-agency intelligence walls; ministry-to-ministry siloed analyses; legislative-executive briefing gaps; central-bank vs. fiscal-authority data partitions.

**AV3 — Regulator-operator.** The regulated entity holds operational, technical, and tacit knowledge that the regulator cannot replicate, and the asymmetry grows with technological complexity. Classical: deepwater drilling, derivatives accounting, software-as-evidence in prosecutions, AI safety oversight. This vector is structurally distinct from the others because the asymmetry is a *constitutive feature* of the regulator-regulated relationship, not a contingent failure.

**AV4 — State-citizen.** The state cannot see how its decisions land in lived practice; the citizen cannot see how the state decides. The asymmetry is two-directional and asymmetric in both directions — the state has more aggregate information about most things, but less local-effect information. Both deficits are decision-relevant.

**AV5 — Temporal.** The decider at time T cannot access what was known at time T−k (institutional amnesia, document destruction, personnel turnover) or commits the institution to time T+k under information available only at T (irreversibilities written ahead of evidence). Decisions made before evidence becomes available become structurally locked-in regardless of subsequent learning.

### Validity rules for an asymmetry classification

An asymmetry vector classification is valid when:

**A1. Channel exists in the formal structure.** The asymmetry is not abstract — there is a specifiable channel (a reporting line, a briefing pipeline, a mandate boundary, a classification compartment, a statutory wall) where information should flow and either does not, flows distorted, or flows one-way only.

**A2. The asymmetry is decision-relevant.** The information held on the higher-information side is material to the specific decision — not "they knew more in general" but "they knew or could have known the specific fact whose absence shapes this decision."

**A3. Documentable from the record.** Org charts, briefing logs, classification markings, mandate texts, transcripts, distribution lists. The asymmetry is shown in the structure that existed at decision time. It is never inferred from the bad outcome.

### Error compounding

Errors do not stay where they originate. They propagate along the asymmetric channels and **compound multiplicatively** — not additively — at each node they pass through.

The simplest form: if a decision depends on N upstream signals each transmitted with reliability $r_i$, the joint reliability is $\prod r_i$ and the composite error rate is $1 - \prod r_i$. Six links of 0.90 reliability yield 0.53 composite reliability — coin-flip — even though every link individually was "responsible." Equivalently, in a hierarchy of $k$ briefing hops with per-hop information-loss rate $\ell$, the cumulative loss is $1 - (1-\ell)^k$ and grows non-linearly with $k$.

The protocol does not publish numerical reliability scores — the underlying record does not support that precision. It records the **topology** of the propagation, from which qualitative compounding is read. The compounding function is conceptual; the topology is empirical.

### Validity rules for a propagation link

A propagation link from upstream card U to downstream card D is valid when:

**P1. Formal dependency.** D's decision artifact (statute, mandate, budget line, instruction, prior ruling, organizational predecessor relationship) cites or operationally depends on U. Not "general context of the era" — a specifiable formal hook.

**P2. Asymmetric channel named.** The information transmission between U and D ran through one of AV1–AV5 and the channel is documented. The error in U was *carried* into D through that asymmetry, not as common knowledge available to anyone.

**P3. Survives lower-cause sufficiency.** Red-Team attempts to explain D's failure without invoking U. If a strictly local explanation suffices, the propagation link is dropped. (Same logic as the §5a lower-layer-sufficiency test.)

A card may carry zero or many `propagated_from` and `propagates_to` links. Cards collectively form a directed acyclic graph — the **error topology** — which is, properly, the catalog's primary output. Individual cards are nodes; the topology is the structure the catalog discovers.

### What this layer does not do

It does not assign personal responsibility along the chain. It does not score officials by "share of error." It does not predict failures outside the documented topology. It does not turn the catalog into a causal-inference engine — the topology is descriptive, not predictive. It records that a given error traveled along a given documented channel and was amplified by it. The verdict on what to do with that record is, as ever, downstream.

---

## 5c. Strategic / incentive-misalignment layer (L4)

§5–§5b assume actors deliberating in good faith — making cognitive mistakes (L1), trapped by group structure (L2), constrained by closed information environments (L3), or operating across asymmetric channels they did not design (§5b). That assumption fails for an entire class of real failures: actors whose effective objective function — what their behavior reveals they are optimizing — is misaligned with the institutional mandate they hold, *and* who proceed anyway. This is the **L4** layer.

L4 is not L1 with bad intent. L1 is honest misjudgment. L4 is misalignment between what the role is supposed to optimize and what the actor is observed to optimize. The protocol classifies L4 only on documented evidence of the misalignment, not on inferred motive. The discipline below is what keeps L4 from becoming the moralizing layer the protocol forbids.

### Validity rules for an L4 classification

An L4 classification is valid when **all four** of the following hold:

**M1. Documented payoff structure.** The actor's incentive structure relevant to the decision is in the record: compensation arrangement, future role / revolving-door pipeline, faction membership, electoral cycle, equity holding, family / network contracting, mandate boundary that ends short of the decision's footprint. The misalignment is not inferred — the structure that could produce it is documented.

**M2. Behavior-fit dominates mandate-fit.** The observed behavior is better explained by optimizing the documented payoff than by optimizing the institutional mandate. This is the C2 base-rate test transposed from cognition to incentive: if the mandate-aligned explanation fully accounts for the behavior, no L4 is added.

**M3. Lower-layer sufficiency tested.** Red-Team has attempted to explain the behavior without invoking incentive misalignment — as L1 (honest mistake), L2 (process trap), L3 (information closure), or §5b (asymmetry). If a strictly lower-layer explanation suffices, L4 is dropped or downgraded. The same logic as the §5a and §5b sufficiency tests, extended.

**M4. Corroboration.** Either (a) the actor's own statements (private if leaked into the record, public if available) corroborate the misalignment; or (b) the behavior is so off-mandate that no good-faith reading of the public record sustains. M4(b) is the high bar — it requires the gap between behavior and any plausible mandate-aligned reading to be wide enough that the Red-Team cannot find a defensible alternative.

If any of M1–M4 fails, no L4 classification is recorded. The card may still carry L1, L2, L3, and §5b classifications. Silence on L4 is, per N6, a positive empirical claim — recorded in `analyst_notes` as "L4 considered; M_n not met."

### Sub-types defined in v0.4

The clean sub-types — those whose evidence requirements do not require a moral verdict — are operationalized below. Sub-types adjacent to motive-imputation (status play, identity defense, performative-parity obstruction) are deferred to v0.5 pending a separate methodological pass on the moral layer.

**L4b — Career / legacy protection.** The actor's behavior optimizes their own future role, reputational position, or post-tenure prospects, where the relevant payoff is documented. Operational signature: documented memo trail constructed for plausible deniability; decision deferred to a successor or to a body with insulation; "delegation" to a channel from which return is structurally unlikely.

**L4c — Rent-seeking.** Private financial or material interest of the actor or of a documented closely-held network. Operational signature: revolving-door pipeline (specific named successor role); equity or beneficial ownership in a regulated counter-party; contracts concentrated in a documented family / professional / political network beyond what the qualification pool predicts.

**L4e — Tribal / factional loyalty over mandate.** Voting, appointment, or rule-making outcomes correlate with documented faction line in cases where the local evidence supports a different outcome. Operational signature: divergence between the actor's stated reasoning and the available evidence runs in the direction of the faction; cross-faction votes by the same actor on technically similar matters show the inverse pattern.

**L4g — Bounded-mandate externality.** The actor optimizes their formal mandate; foreseeable damage outside that mandate is either unacknowledged or dismissed without analysis. Operational signature: (a) decision falls inside formal mandate; (b) downstream cost is large and was foreseeable from documented analysis; (c) downstream cost is absent from decision rationale, or is mentioned and dismissed without engagement. Theoretical base: incomplete-contracting (Hart-Holmström) and externality theory.

**L4h — Persistent claim without competence-deferral.** The actor lacks the documented technical, factual, or jurisdictional capacity for the call but persists, using procedural standing as the justifying mechanism. Distinct from L1 Dunning-Kruger (which is honest unconscious overestimation) — the operational test is whether the record contains a deferral path the actor declined. Operational signature: (a) actor's qualification gap is documentable from the record; (b) procedural / equality-of-voice argument is invoked instead of substantive engagement; (c) a deferral channel (referral to expert body, recusal, request for technical opinion) was available and was not used.

### Sub-types reserved (deferred to v0.5)

**L4a — Status play / ego performance.** Sits at the boundary of motive imputation. Requires resolution of the "moral classification" question separately from the protocol's discipline.

**L4d — Identity defense.** Same boundary issue: the position-as-self-concept reading risks armchair psychology in the absence of much stricter evidence rules.

**L4f — Performative-parity / standing-claim obstruction.** Likely collapses into L4h plus L4a once the moral question is resolved; held in reserve to avoid premature splitting.

These three are NOT classifiable in v0.4. Cards that appear to fit them carry no L4 classification (or carry only L4b/L4c/L4e/L4g/L4h, whichever cleanly fits) until v0.5 establishes the evidence rules.

### What L4 is not

It is not a verdict on the actor's character. It is a record of misalignment between role and observed optimization, validated against M1–M4. It is not a finding of corruption — corruption is a legal category with its own evidentiary standards which the protocol does not satisfy and does not claim to. It is not a substitute for an inspector general, a court, or an audit. It is what the documented record shows about whose function the behavior fits.

The Neutrality Auditor enforces this strictly: "Minister X voted Y, and the documented payoff structure favors Y" passes; "Minister X is corrupt" does not.

---

## 5d. Mechanism pathology (L5)

L1–L3 record how individuals and groups err. §5b records how asymmetric channels distort what reaches the decision. §5c records how an actor's incentives may be misaligned with their mandate. L5 records a distinct thing: **outcomes that no actor in the system selected and that would persist under informed, good-faith participation, because the aggregation mechanism has a documented constraint**.

The theoretical ground is well-established and is not a single field. Social choice theory (Arrow 1951, Gibbard 1973, Satterthwaite 1975, Sen 1970) shows that no preference-aggregation rule satisfies simultaneously a reasonable set of fairness requirements, and that any non-dictatorial rule with ≥3 outcomes is susceptible to strategic manipulation. Plott (1967) and McKelvey (1976) show that in multidimensional policy space, majority rule produces coalition cycles and the output is agenda-sensitive rather than preference-sensitive. Algorithmic game theory (Koutsoupias-Papadimitriou 1999, Roughgarden 2005) formalizes the gap between Nash equilibrium and social optimum. Hardin (1968), Olson (1965), and Ostrom (1990) characterize the conditions under which common-pool resources and large-group public goods fail — and the institutional designs that prevent the failure. Coase (1937, 1960) and Williamson (1975) show that transaction costs can block Pareto-improving reallocations that are theoretically available. Schelling (1960, 1966) characterizes deadlock and brinkmanship equilibria. Federalism theory (Oates 1972, Weingast 1995) characterizes jurisdictional-scope mismatches. These results are not competing theories of one phenomenon; they are independent results, each operative in its own problem class.

The L5 taxonomy (`taxonomy/mechanism_pathologies.json`) enumerates 14 operationalized modes across 8 sub-types.

### Sub-types defined in v0.5

- **L5a** — Social-choice impossibility (Arrow / Condorcet / Gibbard-Satterthwaite / Sen).
- **L5b** — Price-of-anarchy Nash-Pareto gap with no coordination mechanism attempted.
- **L5c** — Common-pool / collective-action failure without enforcement institution.
- **L5d** — Transaction-cost veto of an available Pareto move.
- **L5e** — Agenda control / Plott-McKelvey cycling.
- **L5f** — Jurisdictional-scope / externality-scope mismatch, or concurrent-jurisdiction conflict without coordination.
- **L5g** — Temporal compounding / oscillation without new information.
- **L5h** — Deadlock / mutual-veto / procedural-parity stalemate without tie-break.

### Validity rules for an L5 classification

A classification is admissible only if **all four** of S1–S4 are met. The Red-Team rejects any L5 nomination failing any.

**S1. Mechanism named, result cited.** The specific mechanism must be identified by class (which aggregation rule, which game structure, which commons configuration, which jurisdictional arrangement), and the theoretical result establishing its pathology must be cited. A generic claim ("the process was broken") does not qualify; "the body used pairwise elimination over alternatives whose aggregate preference structure contains the cycle [evidence], a known Condorcet configuration" qualifies.

**S2. Applicability conditions satisfied.** The cited theoretical result applies only under specified conditions (Arrow requires ≥3 alternatives and universal domain; price-of-anarchy requires identifiable agents with payoff structure; Hardin requires rivalry and non-excludability; agenda control requires multidimensional preferences). The record must establish the conditions for the cited result. A card that invokes Arrow in a binary yes/no vote fails S2 regardless of outcome.

**S3. Lower-layer sufficiency.** If any L1, L2, L3, or L4 classification, alone or in combination, is sufficient to explain the observed outcome, L5 drops and the lower-layer classification stands. The Red-Team runs this test in both directions: it also asks whether a mechanism-level explanation makes the lower-layer classifications redundant, and downgrades whichever is weaker on the evidence. L5 is not an umbrella that absorbs actor-level failures; an actor-level failure is not an umbrella that absorbs a mechanism-level failure. Co-classification across layers is admissible when each satisfies its own validity rules on distinct evidence.

**S4. Documented alternative exists.** An L5 claim must identify a mechanism — in the literature, in the body's own procedural framework, or in an analogous institution's practice — that would have avoided the pathology for the problem class at hand. Without S4, the claim collapses to "no mechanism could have worked," which is unfalsifiable and amounts to fatalism. "Alternative exists" does not mean "alternative was politically available"; it means the alternative is documented as applicable to the problem class. The political cost of adopting it is a separate question.

### What L5 is not

It is not a claim that every suboptimal outcome is a mechanism pathology. It is not a claim that aggregation mechanisms are always or usually broken. It is not a way to absolve actors: S3 ensures that where an actor-level failure is sufficient, the actor-level classification stands, and §5c L4 classifications survive independent of L5. It is not a claim that a better mechanism was *easy* to adopt — the political economy of mechanism change is outside the protocol's scope. It is a record that *this class of decision, in this body, under this rule, has a documented constraint that produced this class of outcome, and a documented alternative exists*.

### Why L5 is separated from L4

L4 records actor-level misalignment between role and optimization. L5 records mechanism-level constraint even under aligned actors. The distinction matters because:

1. A body can be filled with actors whose incentives are perfectly aligned with their mandate and still produce a suboptimal consensus — if the aggregation rule is pathological for the problem class. Recording such cases as L4 would impute misalignment that the record does not support. Recording them as L3 would impute informational closure that the record does not support.
2. A body can have documented L4 misalignment *and* a pathological mechanism — the two co-exist. Collapsing them into one layer would hide the fact that fixing the actors would not fix the output if the mechanism is still broken, and fixing the mechanism would not fix the output if the actors are still misaligned.
3. The intervention implied by each is different. L4 implies actor-replacement, incentive redesign, or recusal. L5 implies mechanism change. A protocol that conflates the two produces incoherent implied-intervention footprints.

The four of §5b (asymmetry) / L1–L3 / L4 / L5 are now the full lattice for v0.5: channel, judgment, incentive, aggregation. Any future layer must show it is independent of all four on the evidence.

### Invariant residual vs classifiable pathology (v0.6 clarification)

Every real consensus carries a lower-bounded gap from any theoretical optimum, sourced in at least seven independent results: Arrow (no fair aggregation rule), Gibbard-Satterthwaite (all non-dictatorial rules strategically manipulable), price of anarchy (PoA > 1 for most interesting game classes), FLP impossibility (no deterministic consensus in async distributed systems with one possible failure), Coase-Williamson (transaction costs block Pareto-reachable reallocations), Simon (bounded rationality — agents satisfice, not optimize), and information asymmetry (our §5b — unrecoverable at aggregation). These residuals interact and are not jointly minimizable — reducing one typically increases another. This **invariant residual** is the baseline condition of any aggregation mechanism, not a pathology.

The protocol therefore does not classify the invariant residual as L5. An L5 classification is admissible only when the observed suboptimality *exceeds* what the residual predicts, and a documented alternative mechanism (S4) shows the excess was avoidable for this problem class. The difference matters operationally: without this clause every consensus would trivially satisfy L5 and the methodology would collapse. S4 is the enforced operational form of this principle: "if no alternative is documented as applicable, the claim dissolves into the invariant residual." This is what the Red-Team's S4 test enforces.

The practical consequence: a card comparing an observed outcome to a *theoretical optimum* fails the Red-Team. A card comparing it to a *reachable documented alternative* passes. The invariant residual is context; the avoidable excess is content.

---

## 6. The agent pipeline

The error card is assembled by a pipeline of specialized agents. Each has a fixed role, a structured input, a structured output, and a failure mode that is visible to the next stage. The full design is in `ARCHITECTURE.md`. The methodological roles are:

1. **Scout** — ingests the raw source, extracts candidate decision-events, fills `country / branch / level / body / decision_date / sources`.
2. **Framer** — writes `summary / claimed / known_or_knowable / decision / gap`, citation-first. Also writes the initial `constitutive_roles` entries for every actor named in the body or sources, classifying each actor's `foreseeability` against the source bundle. Empty entries are permitted only when the source bundle does not establish action; in that case the analyst justification is recorded in `analyst_notes` per N6.
3. **Chain-Mapper** — runs against the framed case and the existing card catalog. Identifies the asymmetry vectors active in the decision-event per A1–A3, and proposes `propagated_from` links to upstream cards per P1–P3. Writes `asymmetry_vectors` and the candidate propagation links. Does not classify biases. May return empty results — many decision-events have no upstream catalog dependency yet.
4. **Failure-Mode Classifier** — nominates candidate classifications across all five layers from three taxonomies. From `taxonomy/cognitive_biases.json`: L1 (individual cognitive bias), L2 (group dynamics), L3 (informational closure). From `taxonomy/strategic_failure_modes.json`: L4 (strategic / incentive-misalignment, sub-types L4b/L4c/L4e/L4g/L4h per §5c). From `taxonomy/mechanism_pathologies.json`: L5 (mechanism / aggregation pathology, sub-types L5a–L5h per §5d). Each nomination carries layer, evidence excerpt, source ref, confidence band, and justification. Validity rules per layer: C1/C2 for L1; G1–G3 for L2; at-least-two-of-E1–E4 for L3; all-of-M1–M4 for L4; all-of-S1–S4 for L5. Reads the Chain-Mapper output as context: an asymmetry vector is often the upstream cause of an L1/L2/L3/L4/L5 manifestation, and the Classifier records the connection in its `justification` field. (Renamed from "Bias Classifier" in v0.4 to reflect the broader scope.)
5. **Red-Team** — attempts to defeat each classification (L1–L5), each asymmetry vector, each propagation link, and each `constitutive_roles` foreseeability assignment. Runs the §5a lower-layer-sufficiency test (L1 sufficient → L2/L3 drop; L2 sufficient → L3 drops). Runs the §5b lower-cause-sufficiency test (local explanation sufficient → propagation link drops). Runs the §5c **L4 lower-layer test (M3)** — can the behavior be explained as L1/L2/L3/§5b without invoking incentive misalignment? If yes, the L4 classification is downgraded or dropped. Runs the §5d **L5 bidirectional sufficiency test (S3)** — (a) can the outcome be explained at L1/L2/L3/L4/§5b without invoking mechanism pathology? If yes, L5 drops. (b) Does the named mechanism pathology make any nominated lower-layer classification redundant on the evidence? If so, the redundant classification drops. Co-classification across layers is admissible only when each layer's evidence set is distinct. Separately, Red-Team runs the §5d **alternative-existence test (S4)** — does the documented alternative mechanism actually apply to the problem class at hand? If the alternative is cited but the applicability conditions differ, S4 fails and L5 drops. For each `constitutive_roles` entry, attempts to defeat the foreseeability claim against the source bundle. Writes `counter_arguments`.
6. **Verifier** — checks every citation resolves to the stated source and that quoted material is quoted correctly. This includes citations attached to asymmetry vectors and propagation links.
7. **Neutrality Auditor** — enforces §4. Rewrites or rejects violating language. Has veto. Pays particular attention to asymmetry, propagation, constitutive-role, L4, and L5 language. "The channel was structured such that …" passes; "they hid the information" without documented intent does not. For `constitutive_roles`, the test is: does the entry describe action and contribution without imputing motive? "Director X did not halt the test when conditions Y were no longer met" passes; "Director X recklessly continued" does not. For L4, the test is sharper: does the entry record misalignment between documented payoff and observed behavior, or does it impute character? "Minister X voted Y; the documented holding favors Y" passes; "Minister X is corrupt" does not. For L5, the test is: does the entry describe a mechanism and a documented constraint on it, without transferring mechanism pathology to actor character? "The body's amendment sequence on decision D meets the conditions of Plott-McKelvey [cite], and the chosen ordering [cite] was not justified substantively" passes; "the system is broken" or "the legislature is dysfunctional" does not — those are not L5 claims, they are editorial complaints. The auditor also flags any L5 entry that lacks the S4 documented-alternative clause, since without S4 an L5 claim is a fatalistic editorial, not a record. Empty `constitutive_roles` entries that lack the N6 justification fail audit.
8. **Card Compiler** — assembles the final card, assigns `id` and `version`, fills `residual_uncertainty` and `analyst_notes`. Updates `propagates_to` on referenced upstream cards (forward index maintained at the catalog level). Also maintains the **actor profiles** (§7a): for every actor named in `body`, `constitutive_roles`, or `sources`, the Compiler appends or updates a row in `actors/{actor_id}.json` with the card_id, role, layer-classifications, and foreseeability — strictly aggregation, no new claims (per AP1). Also runs **attractor-component detection** (§7b): for each card published, the Compiler walks the `propagated_from` / `propagates_to` edges to identify the connected component the card now belongs to, recomputes component-level statistics (dominant L5 sub-types, asymmetry-vector co-occurrence, foreseeability distribution), and — if thresholds AT1–AT3 are crossed and no attractor record yet exists for the component — emits a **candidate-attractor flag** to the analyst for authoring. The Compiler does not publish attractor records; AT4 requires a documented exit citation that the Compiler cannot generate. An authored attractor is passed through the Red-Team and Neutrality Auditor before publication, like any card.

No agent can overwrite upstream citations. No agent can add evidence that was not surfaced by the Scout. The pipeline is adversarial by design — the Red-Team and the Neutrality Auditor are expected to reject output from earlier stages, and their rejections are part of the record.

---

## 7. Selection and severity

The system will always see more candidate decision-events than it can responsibly publish. Selection is governed by a severity signal, not by topicality or controversy.

A decision-event is prioritized when it scores on at least two of:

- **Scale.** The decision's population, fiscal, rights, or safety footprint is large.
- **Reversibility.** The decision is hard to undo.
- **Record quality.** The public record is rich enough to support a defensible card.
- **Pattern value.** The event exemplifies a failure mode that recurs across the broader catalog and is instructive.

Severity does not mean "bad outcome." A decision with a good outcome but a gap between claim / knowledge / action is still eligible.

---

## 7a. Actor profile (derived view)

The decision-event is the protocol's primary unit of analysis: every card is one event. But actors recur across events, and a record built event-by-event scatters cross-event patterns that a reader could otherwise see at a glance. The **actor profile** is a derived analytical unit that solves this without introducing any new classification.

A profile is *not* a card. It contains no original utterances and makes no claims that are not already in the cards it aggregates. It is a generated index — one page per actor — that lists every card in which the actor appears, the actor's role in each (drawn from `body`, `constitutive_roles`, and named-source quotations), and the classifications carried by those cards. The protocol assigns no character description, no tally, no score. The reader reads the cards in aggregated form, and the cards speak for themselves.

### Why this exists

Two reasons, both methodological, neither moral.

First: without an actor index, a recurring failure pattern across one official's career splinters into N unconnected cards, and the catalog effectively under-records what it has otherwise correctly recorded. The data is there; the pattern is invisible. Aggregation surfaces the pattern without inventing new claims.

Second: silence about an actor's record across a catalog is the same kind of soft absolution that N6 (§4) prohibits within a single card. If the catalog has 12 cards in which an actor figures with `foreseeability: documented_in_record`, refusing to assemble that index is itself a methodological choice — and the wrong one. The profile makes the index machine-derivable so the choice is not analyst discretion.

### What a profile contains

For each actor (named individual or named body), the profile lists, in chronological order:
- card_id, decision_date, body, branch, level
- the actor's role in that card (`principal` if they were the deciding body, `named_in_roles` with the specific `constitutive_roles` entry otherwise, `quoted_in_sources` if they appear only as a quoted source)
- the classifications the card carries, with layer
- the foreseeability assignment from `constitutive_roles` (if present)
- the asymmetry vectors and propagation links the card carries (so chain position is visible)

The profile carries no `summary`, no `claimed`, no `gap` of its own — those live only on the underlying cards. The profile carries no aggregate verdict and no count of "how many L4-classifications this actor has." A reader who wants to count counts; the protocol does not pre-count, because the choice of what to count is itself a value-laden choice the protocol refuses.

### Validity rules

A profile is valid when:

**AP1. Aggregation only.** Every line of a profile resolves to a citation in an underlying card. The profile introduces no new propositions.

**AP2. Identity discipline.** Aggregation by actor identity is conservative. When the record does not establish that two name-mentions refer to the same actor, they are kept as separate profiles with a `possibly_same_as` cross-reference. Conflations are reversible.

**AP3. Maintained by Compiler, not by analyst.** Profiles are a side-effect of the Card Compiler (§6). An analyst does not edit a profile directly; corrections to a profile are corrections to the underlying cards. This keeps the profile derivable from the catalog at any point.

### What a profile is not

It is not a dossier. It does not record private life, biography, character assessment, or any information about the actor that is not already in a card's cited record. It is not a ranking — actors are not compared. It is not predictive — past appearances do not entail future behavior.

The profile is a convenience for the reader of the catalog. The catalog is the product.

---

## 7b. Anti-consensus attractor pattern (derived view)

L1–L5 classify what happened in a single decision-event. §5b records how errors propagate between events through asymmetric channels. §7a aggregates by actor. None of these capture a distinct phenomenon the catalog makes visible only at scale: a connected sub-graph of cards in which the aggregation mechanism does not merely carry the invariant residual (see §5d), but **compounds suboptimality over iterations and stabilizes in a state worse than any individual card would predict on its own**. Call this sub-graph an **anti-consensus attractor**.

The distinction from L5 is sharp. L5 records a single-event pathology: one decision, one mechanism, one documented alternative. An attractor records a systemic pattern: N events linked by propagation, compounding across time, producing a stable equilibrium from which the system does not escape by its own motion. A reader who reads an L5-classified card sees one broken decision. A reader who sees the attractor view sees that the broken decision is a sample from a trajectory, and that the trajectory's equilibrium is further from the optimum than any single decision's gap.

This matters methodologically because the intervention implied by L5 on a single card ("use the documented alternative mechanism") is not the intervention implied by an attractor ("the system is in a stable equilibrium that any single-mechanism change will not exit"). Conflating the two would misrepresent what the catalog records.

The theoretical ground for calling such equilibria attractors is independent of L5's per-card literature. Plott-McKelvey chaos shows agenda control can drive majority rule from any starting point to any target. Race-to-the-bottom equilibria in jurisdictional competition are strictly worse than any party's standalone choice. Schelling deadlocks are stable lose-lose. Group polarization (Sunstein) moves discussion groups past their prior mean toward the extreme. Information cascades (Banerjee, Bikhchandari-Hirshleifer-Welch) can lock a system into a wrong consensus from a single early signal. Corruption-stable equilibria (Olken and others, mutual-monitoring literature) are stable because exposure is mutual. Coordination-trap lock-ins (Arthur, David) keep systems on dominated trajectories because switching costs exceed per-period losses. These are the attractor-generating mechanisms; each produces outputs that no participant individually selected, and each is documented in analog contexts to have been overcome — which is what makes calling them attractors, rather than fatalistic editorializing, defensible.

### What an attractor record contains

An attractor is a derived object, stored as `catalog/attractors/{attractor_id}.json`. For each attractor:

- `attractor_id` — stable, human-readable (e.g. `SU-NUCLEAR-SAFETY-1970-1986`)
- `scope` — geographic, functional, temporal boundary of the pattern (country, policy area, time range)
- `member_cards` — list of card_ids forming the connected component, with the edge-set from `propagated_from` / `propagates_to`
- `dominant_l5_subtypes` — L5 sub-types (§5d) appearing in ≥N member cards, with counts
- `dominant_asymmetry_vectors` — asymmetry vectors from §5b appearing across the component, with counts
- `foreseeability_profile` — aggregated `foreseeability` field from `constitutive_roles` across the component (distribution over {documented_in_record, partial, absent})
- `compounding_signature` — the record's evidence that the gap is growing over time or that reversals occur without new information (the quantitative shape of the trajectory where extractable)
- `documented_exit` — the analog context — another country, another period, another body — in which this attractor is known to have been exited or avoided. *Required.* Includes citations. An attractor without a documented exit is not recorded; see AT4.
- `counter_arguments` — the strongest case that the component is not an attractor but a coincidence of separately-caused events, or that the "exit" does not actually apply. Required.
- `residual_uncertainty` — what the topology cannot resolve.
- `version` — attractor records are versioned; they are revised, not deleted, as the catalog grows.

### Validity rules

An attractor is admissible only if **all four** of AT1–AT4 are met.

**AT1. Component boundary defined with a criterion.** The membership rule of the component is stated (topical, jurisdictional, temporal) and applied consistently. Cards that do not match the criterion are not included in the component, and cards that match it are not excluded by analyst discretion.

**AT2. Cross-card pattern threshold met.** ≥N member cards (threshold defined per attractor, minimum N=4 in v0.6) share L5 sub-type(s) or co-occurring asymmetry vectors. Mere topical clustering is not sufficient; the same mechanism or the same channel must recur.

**AT3. Foreseeability threshold met.** A majority of `constitutive_roles` entries across member cards carry `foreseeability ∈ {partial, documented_in_record}`. This distinguishes an attractor from systemic inertia or genuine ignorance: an attractor persists despite participants being in a position to see what is happening. If most cards show `foreseeability: absent`, the component is not an attractor — it is something else (possibly an asymmetry-driven blindness field per §5b, which is a different object).

**AT4. Documented exit exists in analog context.** The strictest rule. An analog context — another country, another time period, another body — where an equivalent attractor was exited or avoided must be named and cited in `documented_exit`. This is the exact structural equivalent of S4 for L5 but at the systemic scale: an attractor claim without an exit collapses to "no system could have avoided this," which is unfalsifiable and amounts to fatalism. Ostrom's refutation of the strong form of Hardin is the paradigm case — commons-collapse is not universal, because analog commons with documented governance produce sustained resource flows. If no such analog is documented, the attractor is not recorded; the cards stand individually.

### How the attractor is authored

Unlike actor profiles (§7a), attractor records are **not fully auto-generated** from the catalog. The Card Compiler (§6) runs component detection on each card publication and flags candidate attractors when AT1–AT3 thresholds are crossed. AT4 — the documented exit — requires analyst input, because the exit is a claim about an analog context outside the catalog and carries its own citations. The analyst authors the attractor file; the Compiler flags when authorship is due; the Red-Team and Neutrality Auditor review the authored attractor before it publishes.

This asymmetry is deliberate. Actor profiles are pure aggregation — no new citations are introduced, AP1 holds, full automation is appropriate. Attractors introduce the `documented_exit` clause, which is a new citation; the protocol admits the new citation only through the same adversarial gates that cards pass, not as a Compiler side-effect. The attractor's exit-citation is part of the attractor object, not of any underlying card.

### What an attractor is not

It is not a prediction. An attractor says "this system stabilized at a suboptimal equilibrium and did not exit by its own motion during the recorded window"; it does not claim the system will not exit in the future, and it does not claim that any particular intervention would cause exit. It is not a causal theory — the AT4 analog is a *demonstration* that exit is possible, not a theory of how. It is not a verdict on any individual actor; actor-level records live on the member cards. It is not an aggregate score — attractors are not compared, ranked, or severity-weighted across the catalog. And it is not a substitute for cards: every claim an attractor makes beyond the cited exit resolves back to a card.

The attractor is what the catalog shows when you zoom out. The catalog is the product.

---

## 8. Falsifiability

Every card makes claims that could, in principle, be shown wrong. The standing rules for revision:

- **New primary sources** that change `claimed` or `known_or_knowable` → card is revised, prior version archived.
- **A successful counter-argument** that arrives post-publication → classification downgraded or removed, card re-versioned.
- **A citation that does not resolve** → card reverted to draft until fixed.
- **A neutrality violation** reported and confirmed → corrected without deletion.

A card that accumulates three successful refutations of its core classifications is retired with a visible retirement note. The retirement is itself data.

---

## 9. What this protocol is not

It is not an accountability mechanism. It does not recommend sanctions, removals, or reforms. It does not rank officials. It does not endorse or oppose parties, movements, or policy positions. It does not predict.

It records what was claimed, what was known, what was decided, and which documented failure modes fit the gap. Every downstream use — journalism, academic study, civic tooling, legal discovery, training data for better institutions — is someone else's job.

The discipline is errorlogy. The product is a catalog. The posture is a librarian's.

---

*Version 0.6 — adds §7b (anti-consensus attractor pattern) as a derived view over the card DAG, and an invariant-residual clarification in §5d. The attractor is not a new per-card classification; it is a catalog-topology object that captures systemic compounding of suboptimality — stable equilibria worse than any single card would predict. Validity requires all of AT1 (component boundary with criterion), AT2 (cross-card pattern threshold, minimum N=4), AT3 (majority foreseeability ≥ partial), AT4 (documented exit in analog context with citation). Unlike actor profiles, attractors are not fully auto-generated: the Card Compiler runs component detection and flags candidates; the analyst authors the AT4 exit claim with citation; Red-Team and Neutrality Auditor review before publication to `catalog/attractors/{attractor_id}.json`. §5d gains an explicit invariant-residual clause naming seven independent sources (Arrow, Gibbard-Satterthwaite, PoA, FLP, Coase-Williamson, Simon, §5b) whose joint non-minimizability is the baseline condition of any aggregation mechanism; S4 is the operational form of the principle that L5 classifies only the avoidable excess over the residual, not the residual itself. No prior cards are invalidated.*

*Version 0.5 — adds §5d (L5: mechanism / aggregation pathology layer). Records outcomes that no actor in the system selected and that would persist under informed, good-faith participation, because the aggregation mechanism has a documented constraint. Sub-types L5a (social-choice impossibility), L5b (price-of-anarchy), L5c (common-pool / collective-action failure), L5d (transaction-cost veto), L5e (agenda control / cycling), L5f (jurisdictional mismatch), L5g (temporal compounding / oscillation), L5h (deadlock / brinkmanship). L5 validity requires all of S1–S4; Red-Team gains the §5d bidirectional sufficiency test (S3) and the alternative-existence test (S4). New taxonomy file `taxonomy/mechanism_pathologies.json` (14 modes MP-001…MP-014). §2 extended with §2a: two additional event types `non_decision` and `unstable_decision` recognized alongside the default `decision`, each with its own admissibility conditions; card schema gains `event_type` field. Classifier now runs three taxonomies in the same pass. No prior cards are invalidated; existing cards default to `event_type: decision`.*

*Version 0.4 — adds §5c (L4: strategic / incentive-misalignment layer). Operationalizes the clean sub-types L4b (career / legacy protection), L4c (rent-seeking), L4e (tribal / factional loyalty), L4g (bounded-mandate externality), L4h (persistent claim without competence-deferral). Sub-types L4a (status play), L4d (identity defense), L4f (performative-parity obstruction) are named but reserved for v0.5 pending a separate pass on the moral layer. L4 validity requires all of M1–M4; Red-Team gains the §5c M3 lower-layer test (any lower-layer or §5b explanation sufficient → L4 drops). New taxonomy file `taxonomy/strategic_failure_modes.json` (14 modes SF-001…SF-014). Bias Classifier is renamed **Failure-Mode Classifier** and runs against both taxonomies in the same pass. Card schema gains an `L4` slot inside `classifications[]`. No prior cards are invalidated.*

*Version 0.3.1 — adds §7a (actor profile as a derived view). Actor profiles aggregate across cards only; they contain no propositions not already in the underlying cards (AP1), no behavior-summaries that would constitute a moral verdict (AP2), and are regenerated rather than hand-edited (AP3). The Card Compiler gains a second side-effect: updating `actors/{actor_id}.json` for every actor named on a new card. No prior cards are invalidated.*

*Version 0.3 — adds §5b (information asymmetry as the generator on which L1–L3 manifest, plus error compounding). Card schema gains `asymmetry_vectors`, `propagated_from`, `propagates_to`, and `constitutive_roles`. §4 gains N6 — silence about role is a positive empirical claim, not neutrality. Pipeline gains the **Chain-Mapper** agent (between Framer and Bias Classifier) and a Compiler side-effect that maintains the reverse propagation index; Framer now writes initial constitutive_roles; Red-Team validates foreseeability assignments. No prior cards are invalidated; v0.2 cards may be revised to add the new fields without re-versioning their classifications.*

*Version 0.2 — adds §5a (layered classification: individual / group / environmental) and the L2/L3 evidence rules. §5 retitled as L1. §6 Red-Team gains the lower-layer-sufficiency check. No prior cards are invalidated; existing L1 classifications remain valid as L1.*

*Version 0.1 — initial protocol. This document is itself subject to revision. Breaking changes bump the version; clarifying changes add notes.*
