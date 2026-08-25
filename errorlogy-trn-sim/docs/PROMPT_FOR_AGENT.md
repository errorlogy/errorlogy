# Prompt for another agent

You are a research agent. Your task is to run synthetic TRN agent modeling using the attached package.

Constraints:

- Do not use real personal data.
- Do not connect real social networks, SDKs, ad accounts, CRM, banking systems, or platform APIs.
- Do not generate applied instructions for influencing real people.
- Treat TRN only as an abstract information environment for analyzing resilience, polarization, and anticonsensus.
- Do not treat as AGI/ASI.

Tasks:

1. Read THEORY.md and MATHEMATICAL_MODEL.md.
2. Run `python run_experiments.py --config configs/default_config.json --out outputs`.
3. Run `python run_experiments.py --config configs/sweep_config.json --out outputs --sweep`.
4. Produce tables:
   - baseline metrics;
   - lambda sweep;
   - q/r grid;
   - chi/h sweep.
5. Plot:
   - metrics over time;
   - final opinion distribution;
   - lambda sweep;
   - q/r heatmap.
6. Find anticonsensus threshold:

\[
C<0.45,\quad Pol>0.44,\quad Ext>0.35
\]

7. Compare analytical index:

\[
R_{TRN}=\frac{\lambda\bar m(1-\bar r)(1-\bar q)\chi}{\bar h+\epsilon}
\]

with observed anticonsensus frequency.

8. Write a short report: parameters, metrics, threshold, comparison with \(R_{TRN}\), limitations.

See SAFETY_AND_SCOPE.md before any experiment design change.
