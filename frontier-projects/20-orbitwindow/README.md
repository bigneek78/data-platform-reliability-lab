# OrbitWindow: Synthetic Ground-Station Scheduling

**Independent project 20 of 20 · Space systems planning · Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Which nonoverlapping synthetic contact opportunities maximize mission value around antenna blackouts?

**Method:** Weighted interval scheduling with half-open time intervals, blackout exclusion, and an exact dynamic program.

**Observed result:** The demonstration selects SAT-A, SAT-C, and SAT-F for a total value of 18 across 19 scheduled minutes. Two opportunities are excluded by blackout overlap. An independent exhaustive subset test confirms the optimal value for the fixture, while boundary tests check a contact ending exactly at a blackout start.

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
| total value | 18 |
| selected contacts | 3 |
| selected minutes | 19 |
| blackout excluded | 2 |

![Result chart](assets/results.png)

## Engineering boundary

The input windows are invented. The code performs no orbit propagation, antenna pointing, link-budget calculation, Doppler prediction, spectrum coordination, or live spacecraft control. Value is a user-defined score rather than a guaranteed mission outcome.

## Team handoff

Mission planning should define priority and continuity requirements. RF and ground-system engineers should validate contact feasibility, while operations should own maintenance windows. The next milestone is an independently validated opportunity generator and multi-antenna scheduling model, with all command authority kept outside this prototype.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/bisect.html
