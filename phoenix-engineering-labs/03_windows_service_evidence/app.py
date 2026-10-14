"""Review complete or partial read-only Windows service collection results."""
from phoenix_common import InputError, Report, flag, identified, obj, rows, text


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    expected = rows(data.get("expected_services"), "expected_services")
    names = [text(x, "service name") for x in expected]
    if len({name.casefold() for name in names}) != len(names):
        raise InputError("duplicate expected service")
    hosts = identified(data.get("hosts"), "hosts")
    for host in hosts:
        ident = host["id"]
        if not flag(host.get("collection_ok"), "collection_ok"):
            report.gap(ident, "collection_failed", "Collection failed; host service health is unknown.")
            continue
        services = identified(host.get("services"), "services", key="name", nonempty=False)
        mapping = {text(s["name"], "service name").casefold(): s for s in services}
        if len(mapping) != len(services):
            raise InputError("duplicate case-insensitive service name")
        for name in names:
            key = name.casefold()
            if key not in mapping:
                report.gap(ident, "service_missing", "Expected service " + name + " was not collected.")
                continue
            state = text(mapping[key].get("state"), "service state")
            if state not in ("Running", "Stopped", "Paused", "Start Pending", "Stop Pending", "Continue Pending", "Pause Pending", "Unknown"):
                raise InputError("unrecognized Windows service state")
            if state == "Unknown":
                report.gap(ident, "state_unknown", "Service " + name + " needs fresh evidence.")
            elif state != "Running":
                report.issue(ident, "service_not_running", name + " is " + state + ".")
    return report.finish(hosts=len(hosts), policy_scope="Service-state review; application workflow validation remains separate.")

