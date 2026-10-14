"""Review three security-relevant Terraform plan resource types offline."""
import ipaddress

from phoenix_common import InputError, Report, number, obj, rows, strict_json, text

TYPES = {"aws_security_group", "aws_s3_bucket_acl", "aws_iam_policy"}


def unknown(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return any(unknown(v) for v in value.values())
    if isinstance(value, list):
        return any(unknown(v) for v in value)
    return False


def evaluate(data, now):
    obj(data)
    version = text(data.get("format_version"), "format_version")
    if version.split(".")[0] != "1":
        raise InputError("unsupported Terraform plan format major version")
    report = Report()
    examined = 0
    seen = set()
    excluded = set()
    for resource in rows(data.get("resource_changes"), "resource_changes", nonempty=False):
        obj(resource, "resource")
        ident = text(resource.get("address"), "address")
        if ident in seen:
            raise InputError("duplicate Terraform resource address")
        seen.add(ident)
        typ = text(resource.get("type"), "type")
        change = obj(resource.get("change"), "change")
        actions = rows(change.get("actions"), "actions")
        if any(a not in ("no-op", "create", "read", "update", "delete", "forget") for a in actions):
            raise InputError("unrecognized Terraform action")
        mode = resource.get("mode", "managed")
        if mode not in ("managed", "data"):
            raise InputError("unrecognized Terraform resource mode")
        if typ not in TYPES or mode == "data":
            excluded.add(typ)
            continue
        if actions in (["delete"], ["forget"]):
            continue
        examined += 1
        after = change.get("after")
        uncertain = change.get("after_unknown", {})
        if not isinstance(uncertain, (dict, bool)):
            raise InputError("after_unknown must be an object or boolean")
        field = {"aws_security_group": "ingress", "aws_s3_bucket_acl": "acl", "aws_iam_policy": "policy"}[typ]
        unknown_field = uncertain if isinstance(uncertain, bool) else uncertain.get(field, False)
        if unknown(unknown_field):
            report.gap(ident, "security_value_unknown", "Security-relevant values are unknown until apply.")
        if after is None:
            report.gap(ident, "after_missing", "No proposed resource values were supplied.")
            continue
        obj(after, "after")
        if field not in after:
            report.gap(ident, "security_field_missing", "The modeled security field is absent.")
            continue
        if after[field] is None and unknown(unknown_field):
            continue
        if typ == "aws_security_group":
            for rule in rows(after["ingress"], "ingress", nonempty=False):
                obj(rule, "ingress rule")
                protocol = text(rule.get("protocol"), "protocol")
                if protocol not in ("tcp", "6", "-1", "udp", "17", "icmp", "1", "58", "icmpv6"):
                    report.gap(ident, "protocol_unmodeled", "Review a protocol outside this sample policy.")
                    continue
                if protocol in ("icmp", "1", "58", "icmpv6"):
                    continue
                low = number(rule.get("from_port"), "from_port", maximum=65535, integer=True)
                high = number(rule.get("to_port"), "to_port", maximum=65535, integer=True)
                if high < low:
                    raise InputError("ingress port interval is inverted")
                ranges = []
                for field_name in ("cidr_blocks", "ipv6_cidr_blocks"):
                    values = rule.get(field_name, [])
                    if values is None:
                        report.gap(ident, "cidr_values_unresolved", "A proposed CIDR set has no known values.")
                        continue
                    ranges += rows(values, field_name, nonempty=False)
                for cidr in ranges:
                    try:
                        network = ipaddress.ip_network(text(cidr, "CIDR"), strict=False)
                    except ValueError as exc:
                        raise InputError("invalid ingress CIDR") from exc
                    admin_ports = protocol == "-1" or (protocol in ("tcp", "6") and any(low <= p <= high for p in (22, 3389)))
                    if network.prefixlen == 0 and admin_ports:
                        report.issue(ident, "public_admin_ingress", "Review unrestricted SSH/RDP or all-protocol ingress.")
        elif typ == "aws_s3_bucket_acl":
            acl = text(after["acl"], "acl")
            if acl in ("public-read", "public-read-write", "authenticated-read"):
                report.issue(ident, "broad_bucket_acl", "The proposed canned ACL grants broad access.")
            elif acl not in ("private", "bucket-owner-read", "bucket-owner-full-control", "log-delivery-write"):
                report.gap(ident, "acl_unmodeled", "Review an ACL outside the sample policy.")
        else:
            policy = strict_json(after["policy"]) if isinstance(after["policy"], str) else obj(after["policy"], "policy")
            statements = policy.get("Statement")
            if isinstance(statements, dict):
                statements = [statements]
            for statement in rows(statements, "Statement", nonempty=False):
                obj(statement, "statement")
                effect = text(statement.get("Effect"), "Effect")
                if effect not in ("Allow", "Deny"):
                    raise InputError("invalid IAM Effect")
                action, scope = statement.get("Action"), statement.get("Resource")
                if action is None or scope is None:
                    report.gap(ident, "iam_statement_unmodeled", "Review statements using constructs outside the Action/Resource check.")
                    continue
                actions_list = [action] if isinstance(action, str) else rows(action, "Action", nonempty=False)
                scope_list = [scope] if isinstance(scope, str) else rows(scope, "Resource", nonempty=False)
                if effect == "Allow" and "*" in actions_list and "*" in scope_list:
                    report.issue(ident, "wildcard_allow_review", "Review wildcard Allow and all constraints; full policy authorization is not modeled.")
    if not examined:
        report.gap("plan", "no_modeled_resources", "No proposed values for the three supported resource types were examined.")
    return report.finish(examined_resources=examined, excluded_resource_types=sorted(excluded),
                         policy_scope="Three resource types and specific checks only; no Terraform apply or comprehensive cloud-security assessment.")

