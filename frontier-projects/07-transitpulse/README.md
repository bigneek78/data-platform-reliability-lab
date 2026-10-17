# TransitPulse: Bus Headway Holding Simulation

**Independent project 07 of 20 · Transportation · Java 17 + Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Can bounded holding reduce departure bunching without hiding passenger delay?

**Method:** Bounded terminal holding policy with before/after headway error and total hold time.

**Observed result:** For the fixture, headway error falls from approximately 6.455 to 1.528 minutes, while the policy adds 20 total vehicle-minutes of hold. The expected departure sequence is asserted directly. Tests also check zero holding, a single bus, empty data, and invalid arrival ordering.

![Architecture](assets/architecture.svg)

## Run this project on its own

Requirements: Python 3.12 or newer and Java 17 source-file launcher. No other project folder is imported.

```bash
python3 app.py
python3 -m unittest discover -s tests -v
```

**Local validation: 8 tests passed.** The CLI and all required native components executed on Linux. See [validation.log](validation.log) and [results.json](results.json). Optional figures need Pillow; application/tests otherwise use standard-library Python plus the named native toolchain.

| Metric | Result |
| --- | ---: |
| arrival headway rmse | 6.45497 |
| departure headway rmse | 1.52753 |
| total hold minutes | 20 |

![Result chart](assets/results.png)

## Engineering boundary

This is a terminal policy demonstration, not a city-network optimization. Passenger counts, transfer reliability, dwell time, traffic feedback, driver constraints, and downstream stops are absent. The measured improvement applies to this synthetic arrival sequence only.

## Team handoff

Transit operations should define allowable holding and service recovery policy. Analysts should measure passenger-weighted outcomes, while software engineers preserve replayability. The next step is a scenario panel that compares regularity, total passenger delay, missed transfers, and robustness across multiple demand patterns.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.oracle.com/en/java/javase/17/
