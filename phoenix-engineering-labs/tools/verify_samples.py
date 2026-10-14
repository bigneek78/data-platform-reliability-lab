"""Check, or explicitly record, all fifteen deterministic CLI fixture results."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-10-13T12:00:00Z"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true", help="Write executed fixture outputs after independent behavioral tests pass")
    args=parser.parse_args()
    records=json.loads((ROOT/"catalog.json").read_text(encoding="utf-8"))
    failures=[]
    for record in records:
        command=[sys.executable,str(ROOT/"run_sample.py"),str(record["id"]),"--now",NOW]
        result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=15)
        try:
            output=json.loads(result.stdout)
        except json.JSONDecodeError:
            failures.append({"sample":record["id"],"error":"CLI did not return JSON"})
            continue
        if result.returncode!=record["expected_fixture_exit"] or output.get("exit_code")!=result.returncode:
            failures.append({"sample":record["id"],"error":"Fixture exit code differs from the documented outcome","actual":result.returncode})
            continue
        target=ROOT/record["folder"]/"expected_output.json"
        if args.record:
            target.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
        elif not target.exists() or json.loads(target.read_text(encoding="utf-8"))!=output:
            failures.append({"sample":record["id"],"error":"Executed output differs from the recorded fixture result"})
        print(json.dumps({"sample":record["id"],"status":output["status"],"exit_code":result.returncode,"recorded" if args.record else "reproduced":not any(f["sample"]==record["id"] for f in failures)}))
    if failures:
        print(json.dumps({"failures":failures},indent=2),file=sys.stderr)
        return 1
    print(json.dumps({"samples_verified":len(records),"evaluation_time":NOW}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
