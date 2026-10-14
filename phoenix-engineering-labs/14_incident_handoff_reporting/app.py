"""Produce an evidence-labeled incident handoff with conservative closure rules."""
import re

from phoenix_common import InputError, Report, flag, identified, obj, stamp, text


def redact(value):
    value = re.sub(r"(?i)(Bearer\s+)[A-Za-z0-9._~-]+", r"\1[redacted]", value)
    value = re.sub(r"(?i)((?:token|password|secret|api[_-]?key)\s*[=:]\s*)[^\s,;]+", r"\1[redacted]", value)
    value = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[email redacted]", value)
    value = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[address redacted]", value)
    return value.replace("\n", " ").replace("\r", " ")


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    ident = text(data.get("incident_id"), "incident_id")
    state = text(data.get("state"), "state")
    if state not in ("open", "resolved"):
        raise InputError("incident state must be open or resolved")
    impact = text(data.get("impact"), "impact")
    owner = data.get("owner")
    next_action = data.get("next_action")
    for key, value in (("owner", owner), ("next_action", next_action)):
        if value is None:
            report.gap(ident, key + "_missing", "Provide a clear " + key + ".")
        else:
            text(value, key)
    events = []
    for event in identified(data.get("events"), "events"):
        at = stamp(event.get("at"), "event at")
        if at > now:
            raise InputError("incident event occurs after evaluation time")
        kind = text(event.get("kind"), "kind")
        if kind not in ("finding", "hypothesis", "action", "validation"):
            raise InputError("unrecognized incident event kind")
        severity = text(event.get("severity", "info"), "severity")
        if severity not in ("info", "warning", "error"):
            raise InputError("unrecognized incident severity")
        body = text(event.get("summary"), "summary")
        successful = flag(event.get("successful"), "successful") if kind == "validation" else None
        events.append({"id": event["id"], "at": at, "kind": kind, "severity": severity, "summary": redact(body), "successful": successful})
    events.sort(key=lambda e: (e["at"], e["id"]))
    validations = [e for e in events if e["kind"] == "validation"]
    if state == "open":
        report.issue(ident, "incident_open", "Maintain ownership and the next action while the incident remains open.")
    elif not validations:
        report.gap(ident, "closure_unverified", "No workflow validation supports closure.")
    else:
        latest_time = max(e["at"] for e in validations)
        latest = [e for e in validations if e["at"] == latest_time]
        if len({e["successful"] for e in latest}) > 1:
            report.gap(ident, "validation_conflict", "Conflicting validation outcomes at the same timestamp need reconciliation.")
        elif not latest[0]["successful"]:
            report.issue(ident, "validation_failed", "The latest recorded workflow validation failed.")
        if any(e["kind"] == "finding" and e["severity"] == "error" and e["at"] > latest_time for e in events):
            report.issue(ident, "failure_after_validation", "A later error finding prevents accepting the recorded closure.")
    lines = ["# Incident " + redact(ident), "", "State: " + state, "Impact: " + redact(impact),
             "Owner: " + redact(owner or "Unassigned"), "Next action: " + redact(next_action or "Not supplied"), "", "## Evidence timeline", ""]
    for event in events:
        label = "hypothesis (unconfirmed)" if event["kind"] == "hypothesis" else event["kind"]
        lines.append("- " + event["at"].isoformat() + " | " + label + " | " + event["summary"])
    return report.finish(markdown="\n".join(lines) + "\n",
                         policy_scope="Supplied evidence only. Pattern redaction is limited; review any real report before sharing.")

