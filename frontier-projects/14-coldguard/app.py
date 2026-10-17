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


import xml.etree.ElementTree as ET
def run(d):
    name=d['policy_xml']
    if name!='policy.xml': raise ValueError("Use the bundled illustrative policy")
    policy=ET.parse(Path(__file__).parent/name).getroot()
    low=float(policy.attrib['low']);high=float(policy.attrib['high']);maxgap=float(policy.attrib['maxGapMinutes'])
    if not all(math.isfinite(x) for x in (low,high,maxgap)) or high<=low or maxgap<=0: raise ValueError("Invalid policy")
    readings=d['readings']
    for r in readings:
        number(r['minute'],'minute',0)
        if r['temp'] is not None: number(r['temp'],'temperature')
    if any(a['minute']>=b['minute'] for a,b in zip(readings,readings[1:])): raise ValueError("Strictly increasing sample times required")
    trace=[];outside=0;unknown=0;within=0
    for a,b in zip(readings,readings[1:]):
        duration=b['minute']-a['minute']
        if a['temp'] is None or b['temp'] is None or duration>maxgap: state='UNKNOWN';unknown+=duration
        elif not low<=a['temp']<=high: state='EXCURSION';outside+=duration
        else: state='WITHIN_BAND';within+=duration
        trace.append({'from':a['minute'],'to':b['minute'],'duration':duration,'state':state})
    status='INSUFFICIENT_EVIDENCE' if not trace else 'HOLD_FOR_REVIEW' if outside or unknown else 'WITHIN_ILLUSTRATIVE_BAND'
    return {'status':status,'metrics':{'outside_minutes':outside,'unknown_minutes':unknown,'within_minutes':within,'elapsed_minutes':outside+unknown+within},'trace':trace,'policy_note':'Illustrative synthetic band; not a product release or medical disposition rule.'}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
