# Customer Service Demand & Insights — Synthetic Portfolio Demonstration

**Independent work sample by Neco Thomas.** Not affiliated with Netflix or any employer. No customer data, private information, or production forecasting system is involved.

## Decision question

How can a service-operations analyst connect demand changes to launches, incidents, and contact drivers, explain forecast variance, and produce a decision-ready brief?

## What this demo does

- Applies transparent event and deflection overlays to a baseline forecast.
- Computes WAPE and signed forecast bias (negative = underforecast).
- Summarizes a synthetic customer-contact driver taxonomy.
- Validates behavior using standard-library Python unit tests.

## Run

```bash
python portfolio/cs-demand-insights/cs_insights.py
cd portfolio/cs-demand-insights && python -m unittest discover -s tests -v
```

## Example (illustrative, not measured)

10,000 baseline contacts × 1.12 event uplift × 0.92 after self-service deflection = **10,304 projected contacts**. Low/high assumption scenarios: **9,450–11,400 contacts**. These are scenario bounds, not statistical confidence intervals. Staffing would additionally require arrival distribution, handle time, occupancy, shrinkage and service-level targets.

## Operational controls

1. Segment forecast error by market, channel, event, horizon, and contact driver.
2. Preserve the original model forecast and analyst overlay rationale.
3. Review data freshness, taxonomy drift, missing events, and alternative causal explanations.
4. Use GenAI only with approved, minimized data and human-reviewed evidence.
5. Report a decision owner, uncertainty, recommendation, and next validation point.

**What this shows:** coding, QA, analytical reasoning, documentation, and a forecast-judgment framework. **What it does not show:** production contact-center forecast ownership, deployed models, Netflix systems access, or employer results.
