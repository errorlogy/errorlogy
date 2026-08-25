---
type: flow_index
project: errorlogy
status: active
---

#FlowIndex

This folder is the “operational memory” of the project: hypotheses → experiments → conclusions → method updates.

## How to use

1. Create a hypothesis: `Flows/HYPO - <short name>.md`
2. Create experiments based on the hypothesis: `Flows/EXP - <short name>.md`
3. If an experiment changes the rules of the game, record the methodology: `Flows/METH - <short name>.md`

## Minimum contract (so as not to lose meaning)

- A **hypothesis** has: *thesis*, *what will be considered confirmation*, *what is the next step*.
- An **experiment** has: *input data*, *procedure*, *artifacts*, *metrics*, *result*.
- The **methodology** has: *rule*, *why*, *limits of applicability*, *how to check*.

## Link to taxonomy v16

Any experiment must explicitly state:
- which **layers** of the taxonomy it uses (minimum: `atomic_modes`, plus at least one of the MAX: `WMS/ACC/FPD/LBI`),
- what coverage/quality metric does it improve (for example: TPS/UA/ER).