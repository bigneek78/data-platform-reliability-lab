"""Prioritize certificate metadata expiry and missing rotation ownership."""
from phoenix_common import InputError, Report, identified, number, obj, stamp, text


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    horizon = number(data.get("warning_days", 30), "warning_days", minimum=1)
    schedule = []
    for cert in identified(data.get("certificates"), "certificates"):
        ident = cert["id"]
        start, end = stamp(cert.get("valid_from")), stamp(cert.get("valid_to"))
        if end <= start:
            raise InputError("certificate validity interval is inverted")
        days = (end - now).total_seconds() / 86400
        if now < start:
            report.issue(ident, "not_yet_valid", "The validity interval has not started.")
        if days <= 0:
            report.issue(ident, "expired", "The supplied certificate validity has ended.")
        elif days <= horizon:
            report.issue(ident, "rotation_due", "Schedule reviewed rotation within the sample warning horizon.")
        owner = cert.get("rotation_owner")
        if owner is None:
            report.gap(ident, "rotation_owner_missing", "Identify the rotation and validation owner.")
        else:
            text(owner, "rotation_owner")
        schedule.append({"id": ident, "days_remaining": round(days, 3), "owner_assigned": owner is not None})
    schedule.sort(key=lambda r: (r["days_remaining"], r["id"]))
    return report.finish(rotation_order=schedule,
                         policy_scope="Supplied metadata dates only; no private keys, chain validation or certificate replacement.")

