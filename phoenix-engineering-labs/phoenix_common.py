"""Shared input validation and reporting for offline engineering demonstrations."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone


class InputError(ValueError):
    """The supplied evidence does not conform to the documented input contract."""


def obj(value, name="input"):
    if not isinstance(value, dict):
        raise InputError(f"{name} must be an object")
    return value


def rows(value, name="records", nonempty=True):
    if not isinstance(value, list) or (nonempty and not value):
        raise InputError(f"{name} must be a {'nonempty ' if nonempty else ''}list")
    return value


def text(value, name="text"):
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise InputError(f"{name} must be a nonempty string of at most 4096 characters")
    return value.strip()


def number(value, name="number", minimum=0, maximum=None, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"{name} must be a finite number")
    if value < minimum or (maximum is not None and value > maximum):
        raise InputError(f"{name} is outside its allowed range")
    if integer and not isinstance(value, int):
        raise InputError(f"{name} must be an integer")
    return value


def flag(value, name="flag", unknown=False):
    if value is None and unknown:
        return None
    if not isinstance(value, bool):
        raise InputError(f"{name} must be a boolean" + (" or null" if unknown else ""))
    return value


def stamp(value, name="timestamp"):
    value = text(value, name)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InputError(f"{name} must be an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise InputError(f"{name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def elapsed(value, now, name="timestamp"):
    age = (now - stamp(value, name)).total_seconds()
    if age < 0:
        raise InputError(f"{name} is later than the evaluation time")
    return age


def identified(value, name="records", key="id", nonempty=True):
    result = rows(value, name, nonempty=nonempty)
    seen = set()
    for item in result:
        obj(item, name + " item")
        ident = text(item.get(key), key)
        if ident in seen:
            raise InputError(f"duplicate {key}")
        seen.add(ident)
    return result


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, val in items:
            if key in result:
                raise InputError("duplicate JSON key")
            result[key] = val
        return result

    def constant(_):
        raise InputError("non-finite JSON number")

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as exc:
        raise InputError("invalid JSON syntax") from exc


class Report:
    def __init__(self):
        self.findings = []
        self.gaps = []

    def issue(self, ident, code, message):
        self.findings.append({"item": ident, "code": code, "message": message})

    def gap(self, ident, code, message):
        self.gaps.append({"item": ident, "code": code, "message": message})

    def observe(self, data, now):
        age = elapsed(data.get("observed_at"), now, "observed_at")
        maximum = number(data.get("max_age_minutes", 60), "max_age_minutes", minimum=1)
        if age > maximum * 60:
            self.gap("snapshot", "stale_evidence", "Collect current evidence; known findings are retained.")

    def finish(self, **details):
        status = "incomplete" if self.gaps else "issues" if self.findings else "clear"
        return {"status": status, "exit_code": {"clear": 0, "issues": 1, "incomplete": 2}[status],
                "findings": self.findings, "missing_evidence": self.gaps, **details}

