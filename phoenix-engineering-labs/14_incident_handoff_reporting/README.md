# Incident Timeline and Handoff

Teams need a short account of impact, confirmed evidence, hypotheses, actions, validation, ownership, and the next step.

## Engineering approach

Builds a sorted Markdown timeline, labels hypotheses explicitly, preserves conflicting or failed validation, and rejects unsupported closure when a later error is recorded.

## Run the supplied demonstration

From the repository root, using Python 3.11 or later:

```sh
python run_sample.py 14 --now 2026-10-13T12:00:00Z
```

The supplied fixture's expected exit code is **1**. A finding or incomplete result is intentional evidence in the fixture, not a failed test of the analyzer. See `expected_output.json` for the executed result. Use `--input PATH` to examine another approved JSON input; follow the fixture's schema and provide timezone-aware timestamps.

## Review and team handoff

Use the handoff to agree on the next evidence or correction, retain an accountable owner, and confirm the customer workflow before closure.

## Input and result contract

The fixture.json file supplies synthetic input. `app.py` contains the implementation. Reports separate `findings` from `missing_evidence`; incomplete evidence preserves already known issues. Invalid input is rejected with exit code 3 through the shared runner. Policy thresholds and scope are explicit in the fixture, implementation, and output. Run all tests with `python -m unittest discover -s tests -v`.

## Scope and limits

Pattern redaction has limited coverage; review any real output before sharing. The public fixture contains no customer or employer incident data.

These are AI-assisted application demonstrations, created for review and learning. They are separate from employer production work. No employer configurations, credentials, government network data, or historical production logs are included.

## Interview discussion

Explain the failure that this sample is designed to prevent, which evidence changes the decision, and how another engineer can reproduce the result. Describe what the tool can establish and which workflow still needs independent validation.

Role relevance: **Executive communication; incident ownership; documentation**.
