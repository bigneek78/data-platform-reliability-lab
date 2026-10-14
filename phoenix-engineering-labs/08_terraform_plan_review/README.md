# Terraform Plan Security Review

Known public administration paths and broad grants need review, while unknown plan values must not be treated as safe.

## Engineering approach

Reviews proposed security-group ingress, S3 canned ACLs, and IAM wildcard Allow statements. Understands Terraform resource changes, modeled unknown values, deletions, and excluded types.

## Run the supplied demonstration

From the repository root, using Python 3.11 or later:

```sh
python run_sample.py 08 --now 2026-10-13T12:00:00Z
```

The supplied fixture's expected exit code is **1**. A finding or incomplete result is intentional evidence in the fixture, not a failed test of the analyzer. See `expected_output.json` for the executed result. Use `--input PATH` to examine another approved JSON input; follow the fixture's schema and provide timezone-aware timestamps.

## Review and team handoff

Review the flagged change, access constraints, and complete policy context with the infrastructure/security owners before deployment.

## Input and result contract

The fixture.json file supplies synthetic input. `app.py` contains the implementation. Reports separate `findings` from `missing_evidence`; incomplete evidence preserves already known issues. Invalid input is rejected with exit code 3 through the shared runner. Policy thresholds and scope are explicit in the fixture, implementation, and output. Run all tests with `python -m unittest discover -s tests -v`.

## Scope and limits

Three resource types and specific checks only. No apply, cloud API access, full IAM evaluator, or broad claim of cloud compliance. Terraform runtime validation was not available locally.

These are AI-assisted application demonstrations, created for review and learning. They are separate from employer production work. No employer configurations, credentials, government network data, or historical production logs are included.

## Interview discussion

Explain the failure that this sample is designed to prevent, which evidence changes the decision, and how another engineer can reproduce the result. Describe what the tool can establish and which workflow still needs independent validation.

Role relevance: **Terraform; cloud security; reviewable changes**.
