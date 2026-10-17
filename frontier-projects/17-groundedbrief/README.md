# GroundedBrief: Retrieval With Evidence and Abstention

**Independent project 17 of 20 · AI systems · Python**

Prepared for Neco Thomas with AI assistance. Synthetic portfolio prototype; no production, clinical, physical-hardware, or employer-delivery claim.

Can a support assistant retrieve a relevant passage and refuse a query with insufficient evidence?

**Method:** Local TF-IDF cosine retrieval with a relevance threshold and verbatim evidence extraction.

**Observed result:** The restore-drill question selects RB-01 with a top similarity of approximately 0.496. The quoted answer is asserted to be an exact span of the selected source. An unrelated geology query and an empty query both abstain. No generative model or remote model API is called.

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
| top similarity | 0.495637 |
| documents scored | 3 |
| evidence passages | 1 |

![Result chart](assets/results.png)

## Engineering boundary

Lexical relevance is not a guarantee of factual support or completeness. The threshold is illustrative, the corpus is tiny, and synonymous wording can be missed. A passage containing misleading content would still require source governance; the implementation is not a prompt-injection defense or a semantic entailment engine.

## Team handoff

Support specialists should own runbook accuracy and permissions. AI engineers should build a separately labeled answerability benchmark; security should review retrieval boundaries. The next milestone is a blinded evaluation of source selection, refusal behavior, and answer coverage before introducing any generation stage.

Read the [complete article](ARTICLE.md), inspect the [tests](tests/test_project.py), or view the [animated result trace](assets/replay.gif). The [manifest](project.json) identifies this standalone project. Configurations for CI and containers are supplied as configurations; their status is tracked separately from local execution.

Primary reference: https://docs.python.org/3/library/collections.html
