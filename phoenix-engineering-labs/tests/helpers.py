import json
from pathlib import Path
from run_sample import ROOT, load_sample
from phoenix_common import stamp

NOW = stamp("2026-10-13T12:00:00Z")


def sample(ident):
    record, module = load_sample(ident)
    raw = (ROOT / record["folder"] / record["fixture"]).read_text(encoding="utf-8")
    data = raw if record["format"] in ("xml", "csv") else json.loads(raw)
    return module, data


def codes(result):
    return {f["code"] for f in result["findings"] + result["missing_evidence"]}
