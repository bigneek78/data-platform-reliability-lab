# FoodBridge: Perishable Inventory Allocation

**Independent project 12 of 20 · Food systems · SQL + Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Can a food-rescue desk fulfill timed requests while keeping expired lots out of allocations?

**Method:** Transactional SQLite first-expiring-first-out allocation using parameterized queries.

**Observed result:** The demonstration fulfills 16 requested units, leaves 1 unit, and reports that remaining unit as expired at the reporting horizon. Tests reconcile supply and demand, verify expiry and availability boundaries, and prove that a punctuation-heavy identifier is treated as data rather than SQL.

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
| allocated units | 16 |
| unmet units | 0 |
| remaining units | 1 |
| expired remaining units | 1 |

![Result chart](assets/results.png)

## Engineering boundary

This is a desk allocation model, not a food-safety certification or delivery optimizer. Food types, allergens, handling temperature, nutrition, vehicle routes, and recipient preferences are absent. First-expiring-first-out is not a global proof of minimum waste across all possible future requests.

## Team handoff

Warehouse staff should own lot evidence, partner organizations should validate requests, and logistics staff should supply transport constraints. The next milestone is a replay with item compatibility and delivery windows, followed by reconciliation between promised, picked, delivered, and rejected units.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/sqlite3.html
