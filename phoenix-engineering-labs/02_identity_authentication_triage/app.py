"""Correlate certificate metadata and an authentication-event window."""
from phoenix_common import InputError, Report, elapsed, flag, identified, number, obj, rows, stamp, text


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    certificate = obj(data.get("certificate"), "certificate")
    start = stamp(certificate.get("valid_from"), "valid_from")
    end = stamp(certificate.get("valid_to"), "valid_to")
    if end <= start:
        raise InputError("certificate validity interval is inverted")
    if now < start:
        report.issue("certificate", "not_yet_valid", "Certificate validity has not started.")
    if now >= end:
        report.issue("certificate", "expired", "The supplied certificate validity interval has ended.")
    for key in ("chain_valid", "revocation_clear", "mapping_valid"):
        value = flag(certificate.get(key), key, unknown=True)
        if value is None:
            report.gap("certificate", key + "_unknown", "Obtain evidence for " + key + ".")
        elif not value:
            report.issue("certificate", key, "The supplied " + key + " check failed.")
    window = number(data.get("window_minutes", 30), "window_minutes", minimum=1)
    threshold = number(data.get("failure_threshold", 3), "failure_threshold", minimum=1, integer=True)
    failures = successes = 0
    events = identified(data.get("events"), "events")
    for event in events:
        outcome = text(event.get("outcome"), "outcome")
        if outcome not in ("failure", "success"):
            raise InputError("event outcome must be failure or success")
        age = elapsed(event.get("at"), now, "event at")
        if age <= window * 60:
            failures += outcome == "failure"
            successes += outcome == "success"
    if failures >= threshold:
        report.issue("authentication", "failure_cluster", "Investigate clustered failures even when a later login succeeds.")
    return report.finish(recent_failures=failures, recent_successes=successes,
                         policy_scope="Supplied evidence only; a successful login is not proof of application authorization.")

