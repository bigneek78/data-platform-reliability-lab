# Active Directory Replication Review

An old last-success timestamp and a recent error need a clear handoff without an unsupported root-cause diagnosis.

## Engineering approach

Reads normalized source/destination/partition links, checks result codes and timestamp consistency, and preserves stale or absent evidence. Includes a PowerShell normalization example.

## Run the supplied demonstration

From the repository root, using Python 3.11 or later:

```sh
python run_sample.py 04 --now 2026-10-13T12:00:00Z
```

The supplied fixture's expected exit code is **1**. A finding or incomplete result is intentional evidence in the fixture, not a failed test of the analyzer. See `expected_output.json` for the executed result. Use `--input PATH` to examine another approved CSV input; follow the fixture's schema and provide timezone-aware timestamps.

## Review and team handoff

Correlate the reported result with AD/DNS/RPC evidence and the affected partition; validate subsequent replication rather than clearing the alert alone.

## Input and result contract

The fixture.csv file supplies synthetic input. `app.py` contains the implementation. Reports separate `findings` from `missing_evidence`; incomplete evidence preserves already known issues. Invalid input is rejected with exit code 3 through the shared runner. Policy thresholds and scope are explicit in the fixture, implementation, and output. Run all tests with `python -m unittest discover -s tests -v`.

## Scope and limits

The four-hour age and 60-minute freshness policies are demonstration thresholds. CSV fields are normalized; this is not a direct parser for every repadmin output variant.

These are AI-assisted application demonstrations, created for review and learning. They are separate from employer production work. No employer configurations, credentials, government network data, or historical production logs are included.

## Interview discussion

Explain the failure that this sample is designed to prevent, which evidence changes the decision, and how another engineer can reproduce the result. Describe what the tool can establish and which workflow still needs independent validation.

Role relevance: **Active Directory; replication; technical handoffs**.
