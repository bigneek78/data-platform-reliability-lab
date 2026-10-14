"""Run a cataloged sample without installing packages or accessing a network."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from phoenix_common import InputError, stamp, strict_json

ROOT = Path(__file__).resolve().parent


def catalog():
    return json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))


def load_sample(ident):
    record = next((r for r in catalog() if r["id"] == ident), None)
    if record is None:
        raise InputError("sample is not in the catalog")
    path = ROOT / record["folder"] / "app.py"
    spec = importlib.util.spec_from_file_location(f"phoenix_sample_{ident}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return record, module


def execute(ident, path=None, now=None):
    record, module = load_sample(ident)
    source = Path(path) if path else ROOT / record["folder"] / record["fixture"]
    if source.stat().st_size > 2 * 1024 * 1024:
        raise InputError("input exceeds the 2 MiB demonstration limit")
    raw = source.read_text(encoding="utf-8-sig")
    evidence = raw if record["format"] in ("xml", "csv") else strict_json(raw)
    result = module.evaluate(evidence, now or datetime.now(timezone.utc))
    return {"sample": ident, "title": record["title"], **result}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=int, choices=range(1, 16))
    parser.add_argument("--input", type=Path)
    parser.add_argument("--now", help="Explicit timezone-aware ISO 8601 evaluation time")
    args = parser.parse_args(argv)
    try:
        result = execute(args.sample, args.input, stamp(args.now) if args.now else None)
    except (InputError, OSError, UnicodeError) as exc:
        result = {"sample": args.sample, "status": "invalid_input", "exit_code": 3, "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())

