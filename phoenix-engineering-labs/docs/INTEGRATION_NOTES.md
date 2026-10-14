# Native integration and review notes

All fifteen core sample commands operate on supplied local fixtures. No command in the default sample runner contacts a Windows host, Active Directory, cloud API, Kubernetes cluster, or AI model.

## Windows service collection

`03_windows_service_evidence/collect_windows_services.ps1` requires an approved Windows/CIM environment. The computer names and service names are explicit parameters. It collects service state, keeps per-host/per-service collection errors, and returns an incomplete exit when evidence could not be collected. It restarts no service.

To write an approved lab collection as UTF-8 JSON in PowerShell:

```powershell
.\collect_windows_services.ps1 -ComputerName 'lab-win-a.example.invalid' -ServiceName 'W32Time','EventLog' | Out-File -FilePath '.\services.json' -Encoding utf8
$collectorExit = $LASTEXITCODE
```

The example hostname is fictional; replace it with an approved lab target. Preserve `$LASTEXITCODE`; a pipeline or later successful command must not overwrite the collector's outcome. The Python runner accepts UTF-8 files with or without a BOM. Windows PowerShell's default redirection encoding can differ, so specify UTF-8.

Collection proves only the collected service state. Check the application's own dependencies and user workflow separately before claiming restoration.

## Active Directory collection

`04_ad_replication_review/collect_ad_replication.ps1` requires the ActiveDirectory PowerShell module and approved domain-controller access. It collects **inbound** links, normalizes timestamps to UTC, and emits a new CSV only when collection has completed without controller errors. Existing output files are not overwritten. A failed controller collection returns exit 2 instead of silently exporting a partial inventory.

Partner identifiers can be directory distinguished names; the analyzer treats them as link identifiers, not as proof of a DNS hostname. The analyzer's four-hour last-success policy and 60-minute collection freshness limit are sample settings that must be adapted to the actual topology and replication expectations.

## RHEL / Ansible

`05_rhel_patch_readiness/collect_readonly_facts.yml` is written in JSON, which is valid YAML, and includes only the `setup` and `debug` modules. Supply an approved `lab` inventory and use `ansible-playbook --check` for a controlled facts exercise. This example collects the OS family and mount facts; it does not establish every patch prerequisite in the readiness JSON.

Repository reachability, backup verification, rollback review, maintenance approval, and reboot permission must come from their responsible owners or actual verified checks. No Ansible runtime or SSH session was executed during preparation.

## Terraform

`08_terraform_plan_review/reference/main.tf.json` demonstrates a JSON-based configuration for a lab security group. Its CIDR is a documentation-only example. Native `terraform init` and `terraform validate` require Terraform and provider downloads; those runtimes were not available locally. No resources were deployed.

The Python analyzer uses a synthetic `terraform show -json` style fixture and checks only three supported resource types and specific properties. Do not publish raw plans or state from a real environment: they can contain sensitive values even when a terminal display hides them. The analyzer reports findings without echoing complete policy bodies.

## Kubernetes

Supply the correct namespaced Deployment and Pod objects using a verified label/owner selection. Controller and replica counters are rollout evidence; they do not independently prove user traffic, backend behavior, authorization, or business acceptance. The sample performs no `kubectl` operation.

## Cursor / AI review exercise

Open this repository in an approved Cursor environment to use `.cursor/rules/reliability.mdc`. Start with sample 15, inspect the deliberately defective `last_result` or `false_success` function, predict its failed cases, make a small reviewed correction, and rerun the tests. Compare the result with the strict reference candidate and explain the failure-handling decision.

The project rule and local evaluation harness are supplied artifacts. The Cursor IDE and any model API were not invoked during preparation.

## Recovery demonstration

The default sample 12 run creates its own temporary source files, a ZIP manifest, and a new restore directory, then verifies restored bytes. Its reusable functions reject existing destinations and unsafe or inconsistent archive content. Limits are deliberately small: 2 MiB of source data and 200 files. This is an integrity and error-handling exercise, not a production backup platform or measured recovery SLA.
