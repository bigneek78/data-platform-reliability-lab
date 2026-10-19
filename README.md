# Data Platform Reliability & Support Engineering Lab

## Latest project — Phoenix Evidence Workbench

[Read the public research overview](phoenix-evidence-workbench/) and [view the LinkedIn announcement](https://www.linkedin.com/feed/update/urn:li:activity:7517989661223329792/).

This early research project uses synthetic device-support data and focuses on explanations for a human reviewer. The implementation, model and detailed technical materials remain private while ownership options and customer needs are evaluated.


## Project Phoenix — 20 separate frontier engineering projects

[Explore the new twenty-project portfolio](frontier-projects/) for robotics, transportation, energy, healthcare operations, resilient communications, AI, release evidence, and space-systems scheduling.

Each project runs independently and contains source code, a synthetic fixture, eight tests, recorded results, an individual article, an architecture diagram, a chart, and an animated trace. **All 20 demos and 160 new tests passed locally on Linux.** AI assistance and prototype limits are disclosed in every project. These are additional projects alongside the earlier fifteen samples.

## Project Phoenix — 15 engineering work samples

[Explore the complete collection](phoenix-engineering-labs/) for executable examples in support operations, Windows and Active Directory, RHEL maintenance, security evidence, Terraform review, Kubernetes reliability, recovery verification, and incident communication.

The collection includes synthetic fixtures, recorded outputs, **152 passing local behavioral and CLI tests**, and a Linux/Windows GitHub Actions validation workflow. These AI-assisted demonstration projects make engineering assumptions, evidence gaps, ownership, and recovery decisions available for technical review. See the [validation record](phoenix-engineering-labs/VALIDATION.md) for the executed scope and integration limits.

## Overview

This repository demonstrates a structured approach to scaling engineering support for distributed data platforms using controlled failure injection, observability-driven validation, automation, and runbook standardization.

The objective is to model operational maturity practices that reduce support friction, improve incident resolution efficiency, and strengthen platform resilience.

---

## Architecture Summary

The lab simulates a Kafka-based distributed ingestion system with:

- Synthetic event producers
- Controlled broker failure testing
- Consumer lag impact validation
- Automated evidence collection
- Structured runbook-driven remediation
- Post-incident documentation workflows
- Infrastructure-as-Code extension via Terraform

---

## Reliability Testing Workflow

1. Start the platform with Docker Compose
2. Generate controlled event load
3. Simulate Kafka broker failure
4. Capture structured incident evidence
5. Quantify consumer lag impact
6. Generate automated incident summary
7. Document findings via runbook + postmortem templates

---

## Repository Structure

```
data-platform-reliability-lab/
  scripts/        → Failure simulation & automation
  runbooks/       → Standardized incident response procedures
  docs/           → Incident + postmortem templates
  terraform/      → Infrastructure-as-Code skeleton
```

---

## Why This Matters

Reliable platforms are not sustained by architecture alone.  
They are strengthened through measurable feedback loops, disciplined documentation, and automation-driven support workflows.

---

## Project Owner

**Neco Thomas**  
Cloud & Reliability Engineer  
Specializing in distributed data platforms, support automation, and operational maturity engineering.

This project models scalable support patterns for Kafka-based systems, emphasizing observability-driven triage and infrastructure-as-code design.
