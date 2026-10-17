# MaintenanceML: Synthetic Failure Classifier and Drift Review

**Independent project 18 of 20 · Machine learning · Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Can a small classifier show its holdout results and reveal a shifted operating population?

**Method:** Logistic regression trained from scratch, train-only standardization, holdout confusion matrix, and standardized mean-shift monitoring.

**Observed result:** The fixture uses 240 training rows and 80 holdout rows, with 0.9875 holdout accuracy on this generated problem. Training log loss falls from about 0.693 to 0.196. The synthetic population shift triggers a review flag. Tests verify deterministic reproduction, scaling arithmetic, split accounting, and loss reduction.

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
| holdout accuracy | 0.9875 |
| holdout rows | 80 |
| training rows | 240 |
| initial log loss | 0.693147 |
| final log loss | 0.195524 |

![Result chart](assets/results.png)

## Engineering boundary

The labels were generated from the same simple feature relationship the classifier can learn. The score therefore demonstrates implementation behavior, not effectiveness at predicting real failures. There is no external validation set, real maintenance label review, calibration study, or deployment claim.

## Team handoff

Reliability engineers should define failure labels and intervention costs. Data scientists should examine temporal leakage, class balance, calibration, and external validation. The next milestone is a time-separated evaluation on appropriately governed equipment data with a documented model card and a human maintenance decision process.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/random.html
