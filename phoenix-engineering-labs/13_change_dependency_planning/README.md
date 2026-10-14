# Change Dependency and Rollback Planning

Unclear prerequisites, missing validation, or a dependency cycle can make a proposed maintenance plan unreliable.

## Engineering approach

Computes deterministic dependency waves and a reverse rollback order. Validates references and records missing owners, approval, acceptance checks, and rollback instructions.

## Run the supplied demonstration

From the repository root, using Python 3.11 or later:

```sh
python run_sample.py 13 --now 2026-10-13T12:00:00Z
```

The supplied fixture's expected exit code is **0**. A finding or incomplete result is intentional evidence in the fixture, not a failed test of the analyzer. See `expected_output.json` for the executed result. Use `--input PATH` to examine another approved JSON input; follow the fixture's schema and provide timezone-aware timestamps.

## Review and team handoff

Review the waves with the responsible technical owners, decide actual concurrency and maintenance timing, and confirm acceptance and rollback triggers.

## Input and result contract

The fixture.json file supplies synthetic input. `app.py` contains the implementation. Reports separate `findings` from `missing_evidence`; incomplete evidence preserves already known issues. Invalid input is rejected with exit code 3 through the shared runner. Policy thresholds and scope are explicit in the fixture, implementation, and output. Run all tests with `python -m unittest discover -s tests -v`.

## Scope and limits

A dependency order does not authorize work or guarantee safe concurrency. The tool schedules no real change and executes no rollback.

These are AI-assisted application demonstrations, created for review and learning. They are separate from employer production work. No employer configurations, credentials, government network data, or historical production logs are included.

## Interview discussion

Explain the failure that this sample is designed to prevent, which evidence changes the decision, and how another engineer can reproduce the result. Describe what the tool can establish and which workflow still needs independent validation.

Role relevance: **Change control; team delivery; dependency reasoning**.
