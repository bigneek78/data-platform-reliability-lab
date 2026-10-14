"""Compare declared attributes with a complete or partial inventory snapshot."""
from phoenix_common import InputError, Report, flag, obj, rows, text


def index(value, name, nonempty):
    result = {}
    for record in rows(value, name, nonempty=nonempty):
        obj(record, name + " item")
        ident = text(record.get("id"), "id")
        if ident in result:
            raise InputError("duplicate inventory resource")
        obj(record.get("attributes"), "attributes")
        result[ident] = record
    return result


def evaluate(data, now):
    obj(data)
    report = Report()
    report.observe(data, now)
    complete = flag(data.get("inventory_complete"), "inventory_complete")
    if not complete:
        report.gap("inventory", "partial_collection", "The inventory is incomplete; unobserved resources need confirmation.")
    desired = index(data.get("desired"), "desired", True)
    observed = index(data.get("observed"), "observed", False)
    for ident, expected in sorted(desired.items()):
        if ident not in observed:
            method = report.issue if complete else report.gap
            method(ident, "resource_not_observed", "The desired resource is absent from the supplied inventory.")
            continue
        actual = observed[ident]["attributes"]
        for key, value in sorted(expected["attributes"].items()):
            if key not in actual:
                report.gap(ident, "attribute_missing", "Expected attribute " + key + " was not collected.")
            elif value != actual[key]:
                report.issue(ident, "attribute_drift", "The declared and observed " + key + " values differ.")
    for ident in sorted(observed.keys() - desired.keys()):
        report.issue(ident, "undeclared_resource", "Review a resource outside the declared inventory.")
    return report.finish(desired_resources=len(desired), observed_resources=len(observed),
                         policy_scope="Declared attributes only; no cloud API access, deletions or secret values in findings.")

