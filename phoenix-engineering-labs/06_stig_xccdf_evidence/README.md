# STIG / XCCDF Evidence Review

A scan report can contain failed, skipped, or unverified controls; a numerical score alone is not sufficient evidence.

## Engineering approach

Selects one TestResult, summarizes individual rule outcomes, rejects duplicate rules and unsafe XML declarations, and retains unverified outcomes and scan age.

## Run the supplied demonstration

From the repository root, using Python 3.11 or later:

```sh
python run_sample.py 06 --now 2026-10-13T12:00:00Z
```

The supplied fixture's expected exit code is **2**. A finding or incomplete result is intentional evidence in the fixture, not a failed test of the analyzer. See `expected_output.json` for the executed result. Use `--input PATH` to examine another approved XML input; follow the fixture's schema and provide timezone-aware timestamps.

## Review and team handoff

Review failed controls with the appropriate security and system owners, document exceptions, and obtain a current validation scan after remediation.

## Input and result contract

The fixture.xml file supplies synthetic input. `app.py` contains the implementation. Reports separate `findings` from `missing_evidence`; incomplete evidence preserves already known issues. Invalid input is rejected with exit code 3 through the shared runner. Policy thresholds and scope are explicit in the fixture, implementation, and output. Run all tests with `python -m unittest discover -s tests -v`.

## Scope and limits

The XML fixture is synthetic. The parser checks selected fields and outcomes, not the complete XCCDF schema, accreditation status, or an entire DISA baseline.

These are AI-assisted application demonstrations, created for review and learning. They are separate from employer production work. No employer configurations, credentials, government network data, or historical production logs are included.

## Interview discussion

Explain the failure that this sample is designed to prevent, which evidence changes the decision, and how another engineer can reproduce the result. Describe what the tool can establish and which workflow still needs independent validation.

Role relevance: **STIG evidence; security validation; exceptions**.
