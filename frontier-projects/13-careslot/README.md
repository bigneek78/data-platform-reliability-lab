# CareSlot: Clinic Resource Scheduling

**Independent project 13 of 20 · Healthcare operations · Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Can an appointment desk book more requests when available resources differ by slot?

**Method:** Exact subset dynamic programming maximizing bookings before minimizing total wait.

**Observed result:** Three of four fixture requests are booked, with a total wait of 6 abstract time units. The specialized Q2 request receives S1, and the unavailable Q4 request remains unbooked. Tests cover slot uniqueness, resource preservation, inclusive time boundaries, empty capacity, and invalid windows.

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
| booked | 3 |
| unbooked | 1 |
| total wait units | 6 |

![Result chart](assets/results.png)

## Engineering boundary

The objective is an operations illustration. It does not assess symptoms, urgency, insurance, protected characteristics, or access eligibility. It ignores appointment durations, staffing overlap, cancellations, and patient preferences beyond the supplied window. It is bounded to 16 requests and slots.

## Team handoff

Scheduling staff and clinical operations should define a reviewed service policy before any real data is introduced. Engineering should preserve exceptions and explain unbooked outcomes. The next milestone is a validated duration-and-resource model with human scheduling authority and explicit accommodation workflows.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/functools.html
