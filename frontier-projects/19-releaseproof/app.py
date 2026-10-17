import json, math, sys
from pathlib import Path

def number(x, name, minimum=None):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError(name + " must be a finite number")
    if minimum is not None and x < minimum:
        raise ValueError(name + " is below its minimum")
    return x

def integer(x, name, minimum=0):
    number(x, name, minimum)
    if not isinstance(x, int):
        raise ValueError(name + " must be an integer")
    return x

def unique(items, name="id"):
    values = [x[name] for x in items]
    if any(not isinstance(x, str) or not x for x in values) or len(set(values)) != len(values):
        raise ValueError("Identifiers must be nonempty unique strings")


import subprocess
def run(d):
    number(d['now'],'now',0);number(d['max_age'],'max_age',0)
    if not isinstance(d['commit'],str) or not d['commit']: raise ValueError("Commit identifier required")
    if not isinstance(d['artifacts'],list) or not d['artifacts']: raise ValueError("Artifact manifest required")
    unique([{'id':x['path']} for x in d['artifacts']])
    for artifact in d['artifacts']:
        digest=artifact['sha256']
        if not isinstance(digest,str) or len(digest)!=64 or set(digest)-set('0123456789abcdef'): raise ValueError("Lowercase SHA-256 digest required")
    base=Path(d['base'])
    if not base.is_absolute(): base=Path(__file__).parent/base
    payload={**d,'base':str(base)}
    proc=subprocess.run(['node',str(Path(__file__).parent/'gate.ts')],input=json.dumps(payload),capture_output=True,text=True,check=True)
    return json.loads(proc.stdout)

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
