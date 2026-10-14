# Backup and Restore Verification

A backup artifact is useful only if its declared files can be restored and verified without overwriting unrelated data.

## Engineering approach

Runs real temporary-file snapshot and restore operations with a SHA-256 manifest. Rejects unsafe member paths, aliases, undeclared entries, corrupt content, and existing restore destinations.

## Run the supplied demonstration

From the repository root, using Python 3.11 or later:

```sh
python run_sample.py 12 --now 2026-10-13T12:00:00Z
```

The supplied fixture's expected exit code is **0**. A finding or incomplete result is intentional evidence in the fixture, not a failed test of the analyzer. See `expected_output.json` for the executed result. Use `--input PATH` to examine another approved JSON input; follow the fixture's schema and provide timezone-aware timestamps.

## Review and team handoff

Review the recovered files and workflow before accepting restoration. The reusable functions require explicitly supplied local paths and conservative size limits.

## Input and result contract

The fixture.json file supplies synthetic input. `app.py` contains the implementation. Reports separate `findings` from `missing_evidence`; incomplete evidence preserves already known issues. Invalid input is rejected with exit code 3 through the shared runner. Policy thresholds and scope are explicit in the fixture, implementation, and output. Run all tests with `python -m unittest discover -s tests -v`.

## Scope and limits

The default demonstration operates only on synthetic temporary files. It is not a production backup product, a live application recovery test, or proof of an RPO/RTO target.

These are AI-assisted application demonstrations, created for review and learning. They are separate from employer production work. No employer configurations, credentials, government network data, or historical production logs are included.

## Interview discussion

Explain the failure that this sample is designed to prevent, which evidence changes the decision, and how another engineer can reproduce the result. Describe what the tool can establish and which workflow still needs independent validation.

Role relevance: **Recovery; integrity checks; filesystem engineering**.
