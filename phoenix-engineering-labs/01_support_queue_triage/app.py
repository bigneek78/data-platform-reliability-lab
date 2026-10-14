"""Evaluate queue ownership, sample SLAs, and closure evidence."""
from phoenix_common import InputError, Report, elapsed, flag, identified, number, obj, text


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    policy = obj(data.get("sla_hours"), "sla_hours")
    for severity, value in policy.items():
        text(severity, "severity")
        number(value, "SLA hours", minimum=0.01)
    tickets = identified(data.get("tickets"), "tickets")
    for ticket in tickets:
        ident = ticket["id"]
        state = text(ticket.get("state"), "state")
        if state not in ("open", "closed"):
            raise InputError("ticket state must be open or closed")
        age = elapsed(ticket.get("opened_at"), now, "opened_at")
        severity = text(ticket.get("severity"), "severity")
        if severity not in policy:
            raise InputError("ticket severity has no SLA policy")
        owner = ticket.get("owner")
        if owner is not None:
            text(owner, "owner")
        if state == "open":
            if owner is None:
                report.issue(ident, "unassigned", "Assign an accountable case owner.")
            if age >= policy[severity] * 3600:
                report.issue(ident, "sla_threshold", "The sample response-age threshold has been reached.")
            queue = text(ticket.get("queue"), "queue")
            proposed = ticket.get("proposed_queue")
            if proposed is not None and text(proposed, "proposed_queue") != queue:
                report.issue(ident, "routing_review", "Review the proposed routing with the receiving team.")
        elif not flag(ticket.get("resolution_verified"), "resolution_verified"):
            report.issue(ident, "unverified_closure", "Obtain workflow validation before accepting closure.")
    return report.finish(records=len(tickets), policy_scope="Synthetic response-age thresholds; no ticket integration.")

