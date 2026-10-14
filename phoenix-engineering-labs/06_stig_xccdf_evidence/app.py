"""Summarize an XCCDF TestResult without equating missing checks with compliance."""
import re
import xml.etree.ElementTree as ET

from phoenix_common import InputError, Report, elapsed, text


def local(tag):
    return tag.rsplit("}", 1)[-1]


def evaluate(raw, now):
    if re.search(r"<!\s*(DOCTYPE|ENTITY)", raw, re.IGNORECASE):
        raise InputError("DTD and entity declarations are not accepted")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise InputError("invalid XCCDF XML") from exc
    tests = [e for e in root.iter() if local(e.tag) == "TestResult"]
    if len(tests) != 1:
        raise InputError("select exactly one XCCDF TestResult")
    test = tests[0]
    report = Report()
    if elapsed(test.get("end-time"), now, "scan end-time") > 24 * 3600:
        report.gap("scan", "stale_evidence", "The scan is older than the sample 24-hour freshness limit.")
    counts = {}
    seen = set()
    for rule in test.iter():
        if local(rule.tag) != "rule-result":
            continue
        ident = text(rule.get("idref"), "idref")
        if ident in seen:
            raise InputError("duplicate XCCDF rule result")
        seen.add(ident)
        results = [r for r in rule if local(r.tag) == "result"]
        if len(results) != 1:
            raise InputError("each rule-result must have exactly one result")
        state = text(results[0].text, "result")
        allowed = {"pass", "fail", "fixed", "notapplicable", "notchecked", "notselected", "unknown", "error", "informational"}
        if state not in allowed:
            raise InputError("unrecognized XCCDF result")
        counts[state] = counts.get(state, 0) + 1
        if state == "fail":
            report.issue(ident, "rule_failed", "Review the failed control and document the approved remediation.")
        elif state not in ("pass", "notapplicable"):
            report.gap(ident, "rule_unverified", "Result " + state + " requires evidence or a current verification scan.")
    if not seen:
        raise InputError("XCCDF TestResult has no rule results")
    if not counts.get("pass", 0) and not counts.get("fail", 0):
        report.gap("scan", "no_assessed_controls", "No pass/fail control evidence was supplied.")
    return report.finish(rules=len(seen), result_counts=counts,
                         policy_scope="Results of this supplied scan only; no accreditation or complete baseline claim.")

