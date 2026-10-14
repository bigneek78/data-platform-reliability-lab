# Certificate Rotation Planning

Expiry monitoring is actionable only when the validity interval, evidence age, and rotation owner are known.

## Engineering approach

Sorts a certificate inventory by time remaining, flags expired/not-yet-valid intervals and a configurable warning horizon, and retains missing ownership.

## Run the supplied demonstration

From the repository root, using Python 3.11 or later:

```sh
python run_sample.py 11 --now 2026-10-13T12:00:00Z
```

The supplied fixture's expected exit code is **2**. A finding or incomplete result is intentional evidence in the fixture, not a failed test of the analyzer. See `expected_output.json` for the executed result. Use `--input PATH` to examine another approved JSON input; follow the fixture's schema and provide timezone-aware timestamps.

## Review and team handoff

Coordinate rotation with identity, application, and infrastructure owners; validate the replacement certificate and the user workflow in a controlled change.

## Input and result contract

The fixture.json file supplies synthetic input. `app.py` contains the implementation. Reports separate `findings` from `missing_evidence`; incomplete evidence preserves already known issues. Invalid input is rejected with exit code 3 through the shared runner. Policy thresholds and scope are explicit in the fixture, implementation, and output. Run all tests with `python -m unittest discover -s tests -v`.

## Scope and limits

Supplied dates only. No private keys, issuance, trust-chain validation, or certificate replacement. A 30-day warning is a sample setting.

These are AI-assisted application demonstrations, created for review and learning. They are separate from employer production work. No employer configurations, credentials, government network data, or historical production logs are included.

## Interview discussion

Explain the failure that this sample is designed to prevent, which evidence changes the decision, and how another engineer can reproduce the result. Describe what the tool can establish and which workflow still needs independent validation.

Role relevance: **PKI inventory; maintenance planning; ownership**.
