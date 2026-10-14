# Project Phoenix — Engineering Labs

**Neco Thomas · Systems, cloud, security, automation, and support operations**

[![Project Phoenix validation](https://github.com/bigneek78/data-platform-reliability-lab/actions/workflows/phoenix-python-tests.yml/badge.svg)](https://github.com/bigneek78/data-platform-reliability-lab/actions/workflows/phoenix-python-tests.yml)

Fifteen engineering demonstrations that make technical judgment reviewable: collect evidence, preserve known failures, clarify ownership, and validate the workflow before accepting success.

These samples were created with AI assistance for learning, technical review, and job-application discussion. The fixtures are synthetic. They are separate from employer production work and contain no employer configurations, credentials, or government network exports.

## Start here

Python **3.11 or later** is the only requirement for the fifteen core demonstrations. No package installation, cloud account, paid API, or live infrastructure connection is required.

In the published `data-platform-reliability-lab` repository, first change into the `phoenix-engineering-labs` directory. The commands below run from that directory.

```sh
python -m unittest discover -s tests -v
python tools/verify_samples.py
python run_sample.py 01 --now 2026-10-13T12:00:00Z
```

The explicit evaluation time makes the supplied fixtures reproducible. Many fixtures intentionally contain an issue or missing evidence, so an analyzer exit of 1 or 2 is expected. The behavioral tests and fixture verifier succeed when those findings are correctly preserved.

Each folder includes an implementation, a focused README, a synthetic fixture, and an executed `expected_output.json`. See [the validation record](VALIDATION.md) for the measured test result and runtime limits.

## Fifteen samples

| Sample | Engineering focus | Evidence or failure handled |
| --- | --- | --- |
| [01 — Support Queue Triage](01_support_queue_triage/) | Support workflow ownership | Unassigned cases, sample SLA age, routing review, unverified closure |
| [02 — Identity and Authentication Triage](02_identity_authentication_triage/) | Identity/PKI and troubleshooting | Expired certificates, unknown trust/mapping checks, failures followed by success |
| [03 — Windows Service Evidence](03_windows_service_evidence/) | Windows and PowerShell | Failed host collection, missing expected services, stopped or unknown service states |
| [04 — AD Replication Review](04_ad_replication_review/) | Active Directory operations | Replication errors, missing success evidence, contradictory or old timestamps |
| [05 — RHEL Patch Readiness](05_rhel_patch_readiness/) | Linux, Ansible, controlled maintenance | Change windows, capacity, repository/recovery prerequisites, reboot permission |
| [06 — STIG / XCCDF Evidence](06_stig_xccdf_evidence/) | Security control review | Failed, skipped, fixed, unknown, and stale scan results |
| [07 — Vulnerability Prioritization](07_vulnerability_prioritization/) | Risk and remediation ownership | Exploitation/exposure context, critical assets, provisional risk, unverified remediation |
| [08 — Terraform Plan Review](08_terraform_plan_review/) | Cloud/IaC review | Public administrative ingress, broad ACLs, wildcard grants, unknown plan values |
| [09 — Cloud Inventory Drift](09_cloud_inventory_drift/) | Inventory and declared state | Known differences, incomplete collection, unobserved and undeclared resources |
| [10 — Kubernetes Rollout Review](10_kubernetes_rollout_review/) | Platform reliability | Controller generation, replica state, progression deadlines, container failures |
| [11 — Certificate Rotation Planning](11_certificate_rotation_planning/) | PKI lifecycle and ownership | Expired/not-yet-valid dates, approaching expiry, missing rotation owners |
| [12 — Backup and Restore Verification](12_backup_restore_verification/) | Recovery and integrity | Real temporary-file restore, checksums, corrupt/unsafe archives, overwrite prevention |
| [13 — Change Dependency Planning](13_change_dependency_planning/) | Change control and team delivery | Dependency waves, cycles, missing owners/validation/rollback, reverse rollback order |
| [14 — Incident Timeline and Handoff](14_incident_handoff_reporting/) | Technical and executive communication | Confirmed evidence versus hypothesis, failed/conflicting validation, later failures |
| [15 — AI Code Review Harness](15_ai_code_review_harness/) | Python evaluation and failure preservation | Ten defined cases, a reviewed reference function, and two deliberately defective candidates |

## Report contract

| Exit | Status | Meaning |
| --- | --- | --- |
| 0 | `clear` | No finding in the sample's explicitly declared scope |
| 1 | `issues` | Known findings require attention |
| 2 | `incomplete` | Evidence is missing or stale; already known findings are retained |
| 3 | `invalid_input` | The input contract or evaluation timestamp is invalid |

`clear` is scoped to supplied evidence and the implemented checks. It is not a declaration that a real service, cloud account, or security baseline is completely healthy. Reports keep `findings` and `missing_evidence` separate, and avoid emitting complete raw inventory or policy values.

## Team operating approach

- Start with the affected workflow and the available evidence.
- Make the next technical decision explicit and involve the responsible owners.
- Preserve failures and uncertainty through automation and handoffs.
- Review the change and recovery path before acting.
- Validate the actual workflow and leave a useful record for the next engineer.

The sample READMEs connect each result to a practical team handoff and identify what still requires independent validation.

## Native integration examples

The Windows and AD folders include read-only PowerShell collectors. The RHEL folder includes a read-only Ansible facts playbook. The Terraform folder includes a JSON configuration reference, and `.cursor/rules/reliability.mdc` supplies a Cursor review rule.

The core Python implementations were executed locally. The native collectors, Ansible runtime, Terraform provider runtime, and Cursor IDE were not run against live systems during preparation. The published repository's `Project Phoenix validation` workflow runs Python tests and fixture reproduction on Linux and Windows and parses the PowerShell collectors on Windows. Check the live workflow results and the publication record for the verified CI state.

Review the [integration notes](docs/INTEGRATION_NOTES.md) before using any native example. The default fixture run changes no infrastructure. Sample 12 creates and verifies only its own temporary demonstration files.

## Review exercises

1. Explain the first finding and the evidence that changes its priority.
2. Show how stale or incomplete data affects the result without removing known failures.
3. Change a fixture, predict the outcome, run it, and explain any difference.
4. Describe the owner, correction, rollback decision, and workflow validation needed for a real case.
5. Review sample 15's defective candidates, demonstrate the failure, and explain the corrected behavior.

These are useful starting points for a technical discussion. A reviewer should assess the implementation, assumptions, tests, and remaining limits directly.

Public profile: [github.com/bigneek78](https://github.com/bigneek78)

Primary technical references are listed in [REFERENCES.md](REFERENCES.md). Publication status is recorded separately in [PUBLISHING.md](docs/PUBLISHING.md).
