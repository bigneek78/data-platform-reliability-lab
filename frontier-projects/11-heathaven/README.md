# HeatHaven: Cooling-Center Coverage Planning

**Independent project 11 of 20 · Community infrastructure · Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Which small set of candidate cooling centers covers the most synthetic neighborhood demand?

**Method:** Exact budgeted maximum coverage with a greedy comparison and transparent uncovered demand.

**Observed result:** Two selected centers cover 110 of 125 synthetic demand units. Area E remains explicitly uncovered. Greedy ties the exact result on this fixture, so the project does not claim a heuristic improvement. Tests cover zero budget, radius equality, overlapping coverage, and negative demand rejection.

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
| covered demand | 110 |
| total demand | 125 |
| greedy covered demand | 110 |

![Result chart](assets/results.png)

## Engineering boundary

The model does not include center capacity, staffing, public transit, accessible entrances, weather forecasts, or individual medical vulnerability. Aggregate weights are invented; no real person is ranked or assigned access. The exact search is bounded to 18 candidates.

## Team handoff

Community organizations should define the service objective with residents. Facilities and accessibility teams should validate candidate sites, while analysts evaluate unmet coverage and capacity. The next milestone is an independently reviewed capacity-and-travel model using appropriate aggregate data and a documented process for community feedback.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/itertools.html
