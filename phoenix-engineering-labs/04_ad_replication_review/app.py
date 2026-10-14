"""Analyze a normalized, timezone-aware AD replication CSV export."""
import csv
import io

from phoenix_common import InputError, Report, elapsed, stamp, text

REQUIRED = {"source", "destination", "partition", "last_success", "last_attempt", "result", "observed_at"}


def evaluate(raw, now):
    reader = csv.DictReader(io.StringIO(raw.lstrip("\ufeff")))
    if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
        raise InputError("replication CSV is missing required columns")
    if len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise InputError("duplicate CSV column")
    report = Report()
    count = 0
    seen = set()
    for row in reader:
        if None in row:
            raise InputError("CSV row has extra fields")
        source, target, partition = (text(row.get(k), k) for k in ("source", "destination", "partition"))
        ident = source + " -> " + target + " / " + partition
        if ident in seen:
            raise InputError("duplicate replication link")
        seen.add(ident)
        count += 1
        if elapsed(row.get("observed_at"), now, "observed_at") > 3600:
            report.gap(ident, "stale_evidence", "Replication export is older than the sample 60-minute freshness limit.")
        try:
            result = int(row["result"])
        except (ValueError, TypeError) as exc:
            raise InputError("replication result must be an integer") from exc
        if result < 0:
            raise InputError("replication result cannot be negative")
        attempt = stamp(row.get("last_attempt"), "last_attempt")
        elapsed(row.get("last_attempt"), now, "last_attempt")
        if result != 0:
            report.issue(ident, "replication_error", "Replication reported error " + str(result) + "; determine its cause from evidence.")
        if not row.get("last_success"):
            report.gap(ident, "success_unknown", "No last-success timestamp is available.")
        else:
            success = stamp(row["last_success"], "last_success")
            if success > attempt:
                raise InputError("last_success is later than last_attempt")
            if elapsed(row["last_success"], now, "last_success") >= 4 * 3600:
                report.issue(ident, "success_age", "No successful replication within the sample four-hour interval.")
    if not count:
        raise InputError("replication CSV contains no records")
    return report.finish(links=count, policy_scope="Normalized CSV, sample freshness and age limits; no domain changes.")

