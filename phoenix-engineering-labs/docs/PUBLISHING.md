# Publication record

Owner: **Neco Thomas / bigneek78**.

Repository: [data-platform-reliability-lab](https://github.com/bigneek78/data-platform-reliability-lab).

Collection: [phoenix-engineering-labs](https://github.com/bigneek78/data-platform-reliability-lab/tree/main/phoenix-engineering-labs).

The fifteen samples are organized as an independent collection inside the existing portfolio repository. The collection's README links to each implementation, synthetic fixture, executed output, and engineering discussion. Existing reliability-lab files remain outside this collection.

The root `.github/workflows/phoenix-python-tests.yml` workflow runs the collection's behavioral tests and fixture verification on Linux and Windows with Python 3.12 and 3.13. It also parses the PowerShell collectors on Windows. Live workflow results are the authority for GitHub CI status; the original local execution record is in `VALIDATION.md` and `execution_record.json`.

## Verified GitHub publication

Published source commit: [`1a0b29f`](https://github.com/bigneek78/data-platform-reliability-lab/commit/1a0b29fecc0451cef83fa51e9f66cee3527890e3).

All **88 collection files** were verified against their local Git blob hashes, all **15 sample folders** were present, and the twelve pre-existing source files outside the root README retained their original hashes.

The [initial GitHub Actions run](https://github.com/bigneek78/data-platform-reliability-lab/actions/runs/38492575044) completed successfully on **October 14, 2026 (UTC)**. All four Linux/Windows and Python 3.12/3.13 configurations passed behavioral tests and reproduced all fifteen recorded fixtures. Both Windows jobs also passed the PowerShell syntax checks. These checks do not mean the collectors were exercised against a live Windows or Active Directory environment.

This collection contains no additional license grant. The repository owner can select a license separately.
