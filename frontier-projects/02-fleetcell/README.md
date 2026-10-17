# FleetCell: Capability-Aware Robot Assignment

**Independent project 02 of 20 · Robotics · Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Which robot should take each task when capabilities and travel costs conflict?

**Method:** Exact subset dynamic programming for minimum-cost one-to-one task assignment.

**Observed result:** The optimal complete allocation costs 3 distance units. The fixture-order greedy comparator cannot complete this workload, so its result is explicitly null rather than an invented numeric improvement. A permutation-based test independently checks the optimum for the demonstration.

![Architecture](assets/architecture.svg)

## Run this project on its own

Requirements: Python 3.12 or newer. No other project folder is imported.

```bash
python3 app.py
python3 -m unittest discover -s tests -v
```

**Local validation: 8 tests passed.** The CLI and all required native components executed on Linux. See [validation.log](validation.log) and [results.json](results.json). Optional figures need Pillow; application/tests otherwise use standard-library Python plus the named native toolchain.

| Metric | Result |
| --- | ---: |
| optimal distance | 3 |
| greedy distance | None |

![Result chart](assets/results.png)

## Engineering boundary

The exact method is deliberately small, with at most 16 robots. It is not a continuous fleet dispatcher and does not model battery charge, collision avoidance, task durations, or a robot taking several sequential jobs. Those omissions define the next engineering questions.

## Team handoff

The operations team should define mandatory capabilities; robotics engineers should supply validated travel estimates; a planning owner should approve how workload priorities are represented. Before a larger pilot, benchmark a scalable solver against the exact small-case oracle and add execution-time and failure-reassignment constraints.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/functools.html
