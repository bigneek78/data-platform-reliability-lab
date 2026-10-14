# Executed validation — October 13, 2026

The fifteen core Python demonstrations passed **152 behavioral and command-line tests** on **Python 3.12.14, Linux**. All fifteen standalone fixture commands reproduced their documented exit codes and recorded JSON outputs.

Execution record: **2026-10-13T22:29:08.996335+00:00**. This is the test execution time; the synthetic fixtures use the fixed evaluation time **2026-10-13T12:00:00Z** for reproducibility.

## Reproduce the checks

```sh
python -m unittest discover -s tests -v
python tools/verify_samples.py
```

The complete test log is in `test_results.txt`; fixture reproduction is recorded in `fixture_verification.txt`; runtime and execution limits are recorded in `execution_record.json`.

## What was exercised

- Known failures retained when evidence is incomplete or a later operation succeeds.
- SLA-age, freshness, certificate-expiry, event-window, and maintenance-window boundaries.
- Invalid, duplicate, timezone-naive, and oversized input rejected through structured error handling.
- Failed host collection and missing Windows service evidence preserved.
- AD replication errors, timestamp contradictions, missing success evidence, and UTF-8 BOM exports.
- XCCDF failed and unverified outcomes, duplicate rules, stale scans, and unsafe XML declarations.
- Risk prioritization with provisional context and verified versus unverified remediation.
- Public IPv4/IPv6 administration paths, broad IAM grants, unknown Terraform values, deletions, and limited policy scope.
- Partial inventory distinguished from known drift, with raw attribute values excluded from findings.
- Kubernetes generation, availability, missing Pod/container evidence, progression deadlines, and failed containers.
- Real temporary-file backup/restore with checksum comparison, corrupt content, traversal/alias rejection, and existing-output preservation.
- Dependency order, missing task references, cycles, validation/rollback gaps, and reverse rollback order.
- Incident hypotheses labeled as unconfirmed; failed/conflicting validation and later failures prevent accepted closure.
- A reviewed AI-code-evaluation reference passes ten defined cases; deliberately defective candidates are detected.

SHA-256 comparisons establish content integrity relative to the supplied manifest. They do not establish a backup's trusted origin by themselves.

## Not executed here

The PowerShell collectors were not run against Windows or Active Directory. No Ansible runtime, Terraform provider runtime, Kubernetes cluster, Cursor IDE, or cloud/LLM API was invoked. Native integration examples are supplied with explicit prerequisites and limits.

The original local verification result applies to the stated Python 3.12.14 Linux runtime. After publication, [GitHub Actions run 38492575044](https://github.com/bigneek78/data-platform-reliability-lab/actions/runs/38492575044) completed successfully on October 14, 2026 (UTC), for source commit `1a0b29fecc0451cef83fa51e9f66cee3527890e3`. All four Linux/Windows and Python 3.12/3.13 configurations passed behavioral tests and fixture reproduction. Both Windows jobs also passed PowerShell syntax parsing. See `docs/PUBLISHING.md` for the publication record.

The sample thresholds, policies, identities, events, and configurations are demonstration assumptions. The results do not certify production security, employer experience, service recovery, or job suitability.
