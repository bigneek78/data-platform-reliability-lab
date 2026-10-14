"""Compute dependency waves and reverse rollback order for a proposed change."""
from phoenix_common import InputError, Report, flag, identified, obj, rows, text


def evaluate(data, now):
    obj(data)
    report = Report()
    approved = flag(data.get("approved"), "approved", unknown=True)
    if approved is None:
        report.gap("change", "approval_unknown", "Confirm the change approval state.")
    elif not approved:
        report.issue("change", "not_approved", "This proposed plan has not been approved.")
    tasks = identified(data.get("tasks"), "tasks")
    index = {t["id"]: t for t in tasks}
    dependencies = {}
    for task in tasks:
        ident = task["id"]
        deps = [text(d, "dependency") for d in rows(task.get("depends_on"), "depends_on", nonempty=False)]
        if len(set(deps)) != len(deps):
            raise InputError("duplicate dependency")
        if any(d not in index for d in deps):
            raise InputError("dependency references a missing task")
        dependencies[ident] = set(deps)
        risk = text(task.get("risk"), "risk")
        if risk not in ("low", "medium", "high"):
            raise InputError("risk must be low, medium or high")
        if task.get("owner") is None:
            report.gap(ident, "owner_missing", "Assign a task owner.")
        else:
            text(task["owner"], "owner")
        checks = rows(task.get("validation", []), "validation", nonempty=False)
        if not checks:
            report.gap(ident, "validation_missing", "Define workflow acceptance checks.")
        for check in checks:
            text(check, "validation step")
        if task.get("rollback") is None:
            report.gap(ident, "rollback_missing", "Document the rollback decision and action.")
        else:
            text(task["rollback"], "rollback")
    pending = set(index)
    completed = set()
    waves = []
    while pending:
        ready = sorted(t for t in pending if dependencies[t] <= completed)
        if not ready:
            report.issue("change", "dependency_cycle", "Resolve the dependency cycle before scheduling work.")
            return report.finish(graph_valid=False, execution_waves=[], rollback_order=[], policy_scope="Dependency planning only; no partial schedule is authorized.")
        waves.append(ready)
        completed.update(ready)
        pending.difference_update(ready)
    order = [item for wave in waves for item in wave]
    return report.finish(graph_valid=True, execution_waves=waves, rollback_order=list(reversed(order)),
                         policy_scope="Dependency waves do not grant approval or guarantee safe parallel execution; responsible owners review sequencing.")

