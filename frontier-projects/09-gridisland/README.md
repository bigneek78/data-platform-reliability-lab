# GridIsland: Reserve-Constrained Microgrid Dispatch

**Independent project 09 of 20 · Energy · Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

When should an idealized battery charge or discharge while retaining a stated reserve?

**Method:** Discrete-state dynamic programming with power limits, energy balance, and terminal reserve.

**Observed result:** The fixture dispatch costs 36 units versus 57 with no battery operation, and ends at state of charge 2. Tests verify each energy-balance equation, reserve and rate bounds, terminal state, a tiny independently known optimum, and explicit failure when grid limits make service impossible.

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
| dispatch cost units | 36 |
| no battery cost units | 57 |
| terminal soc | 2 |
| imported kwh | 12 |

![Result chart](assets/results.png)

## Engineering boundary

The model assumes ideal 100-percent battery efficiency. It excludes degradation, conversion losses, forecasts, ramping limits, outages, and power-flow constraints. The cost difference is an algorithm demonstration, not a forecast of a real site savings or a purchasing recommendation.

## Team handoff

Energy engineers should own the physical battery model and safety limits. Facilities should define critical load, while operations and finance should approve resilience and cost priorities. Before a pilot, add efficiency and degradation, then test forecast error and outage scenarios against measured site demand.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/itertools.html
