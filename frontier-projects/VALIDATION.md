# Validation boundary

All twenty applications and 160 tests executed successfully on the local Linux host. The saved logs list the assertions. The tests include known answers, boundary conditions, malformed evidence, conservation checks, and small exhaustive comparisons where applicable.

These tests demonstrate the published implementations on synthetic cases. They do not prove physical safety, medical efficacy, regulatory compliance, real-world AI accuracy, flight readiness, production reliability, or compatibility with every listed platform.

The native C/C++ programs are invoked through validated Python entry points. Direct unvalidated native stdin is outside the input contract. TypeScript execution uses Node 24 type stripping; it is execution evidence, not a static TypeScript type-check result. Java executes through the Java 17 source-file launcher. No cloud resource, paid API, production system, patient data, or hardware was used.

Eight tests are present in every independent project. Root verify_all.py runs them in separate subprocesses to avoid cross-project module collisions. CI configurations are supplied for GitHub and GitLab; service results are reported only after observed completion. Standalone workflows inside project folders are inactive in the hub and become active only if that folder is extracted as a repository root.

Optional visual generation uses Pillow. Images are computed from results.json; animated GIFs replay the actual trace. Some diagrams explain the decision flow, not a deployed architecture. Each result chart uses one stated measurement unit and is not evidence of broader real-world performance.

All full articles include scope, tradeoffs, team responsibilities, and the next validation step. Files are prepared for publication; a file named ARTICLE.md is not evidence of a live Medium publication.
