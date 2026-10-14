"""Decide whether a supplied RHEL maintenance plan is ready for human review."""
from phoenix_common import InputError, Report, flag, identified, number, obj, stamp, text


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    window = obj(data.get("maintenance_window"), "maintenance_window")
    start, end = stamp(window.get("start")), stamp(window.get("end"))
    if end <= start:
        raise InputError("maintenance window is inverted")
    approved = flag(window.get("approved"), "approved", unknown=True)
    if approved is None:
        report.gap("window", "approval_unknown", "Confirm change approval with the responsible owner.")
    elif not approved:
        report.issue("window", "not_approved", "The supplied maintenance window is not approved.")
    if not start <= now < end:
        report.issue("window", "outside_window", "The evaluation time is outside the supplied maintenance window.")
    hosts = identified(data.get("hosts"), "hosts")
    for host in hosts:
        ident = host["id"]
        if text(host.get("os_family"), "os_family") != "RedHat":
            report.issue(ident, "unsupported_os", "This readiness policy is scoped to the RedHat family.")
        free = number(host.get("root_free_gib"), "root_free_gib")
        need = number(host.get("required_free_gib"), "required_free_gib", minimum=0.01)
        if free < need:
            report.issue(ident, "disk_capacity", "Available root space is below the supplied maintenance requirement.")
        for key in ("repository_reachable", "backup_verified", "rollback_reviewed"):
            value = flag(host.get(key), key, unknown=True)
            if value is None:
                report.gap(ident, key + "_unknown", "Obtain evidence for " + key + ".")
            elif not value:
                report.issue(ident, key, "Resolve the failed " + key + " prerequisite.")
        if flag(host.get("reboot_required"), "reboot_required") and not flag(host.get("reboot_authorized"), "reboot_authorized"):
            report.issue(ident, "reboot_not_authorized", "A required reboot is not authorized by this plan.")
    return report.finish(hosts=len(hosts), policy_scope="Plan review only; no patching, reboot, repository or backup operation is performed.")
