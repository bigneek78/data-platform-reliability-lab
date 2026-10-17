# MedTrace: Synthetic FHIR Bundle Preflight

**Independent project 15 of 20 · Healthcare data engineering · Python + JSON**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Can a small preflight catch duplicate identities and unresolved references before a synthetic bundle enters a pipeline?

**Method:** Restricted FHIR R4 collection-bundle identity and local-reference validation.

**Observed result:** The synthetic two-entry fixture passes the subset and resolves one reference. Tests intentionally introduce duplicate fullUrls, duplicate resource identities, an unresolved subject, a missing status, and an unsupported resource type. A URN reference is also checked for successful local resolution.

![Architecture](assets/architecture.svg)

## Run this project on its own

Requirements: Python 3.12 or newer. No other project folder is imported.

```bash
python3 app.py
python3 -m unittest discover -s tests -v
```

**Local validation: 8 tests passed.** The CLI and all required native components executed on Linux. See [validation.log](validation.log) and [results.json](results.json). Optional figures need Pillow; application/tests otherwise use standard-library Python plus the named native toolchain.

| Metric | Result |
| --- | ---: |
| entries | 2 |
| findings | 0 |
| resolved references | 1 |

![Result chart](assets/results.png)

## Engineering boundary

This is not a full FHIR validator, server, terminology service, conformance statement, privacy control, or clinical-quality check. The simplified fullUrl and ID rules are narrower than the complete specification, and many required semantic constraints are outside scope. No real patient records are used.

## Team handoff

Interoperability engineers should own profile selection and terminology bindings. Clinical informatics should review meaning; privacy and security teams should review real-data handling separately. The next milestone is a comparison against an official FHIR validator and a documented implementation guide before any real integration is considered.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://hl7.org/fhir/R4/bundle.html
