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


def run(d):
    bundle=d['bundle'];findings=[];trace=[]
    if bundle.get('resourceType')!='Bundle' or bundle.get('type')!='collection': raise ValueError("Only collection Bundle subset supported")
    entries=bundle.get('entry',[])
    if not isinstance(entries,list): raise ValueError("entry must be a list")
    fulls=set();keys=set();refs=[]
    for i,e in enumerate(entries):
        r=e.get('resource',{});typ=r.get('resourceType');ident=r.get('id');full=e.get('fullUrl')
        issues=[]
        if typ not in ('Patient','Observation'): issues.append('UNSUPPORTED_RESOURCE')
        if not isinstance(ident,str) or not ident or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.' for c in ident): issues.append('INVALID_ID')
        key=f"{typ}/{ident}"
        if key in keys: issues.append('DUPLICATE_RESOURCE_ID')
        keys.add(key)
        if not isinstance(full,str) or not (full.startswith('urn:uuid:') or full.startswith('https://')): issues.append('MISSING_OR_INVALID_FULLURL')
        elif full in fulls: issues.append('DUPLICATE_FULLURL')
        fulls.add(full)
        if typ=='Observation':
            if r.get('status') not in ('registered','preliminary','final','amended','corrected','cancelled','entered-in-error','unknown'): issues.append('INVALID_OBSERVATION_STATUS')
            if not isinstance(r.get('code'),dict) or not r['code']: issues.append('MISSING_CODE')
            ref=r.get('subject',{}).get('reference')
            if not isinstance(ref,str) or not ref: issues.append('MISSING_SUBJECT')
            else: refs.append((i,ref))
        findings.extend({'entry':i,'code':code} for code in issues)
        trace.append({'entry':i,'resource':key,'initial_findings':len(issues)})
    for i,ref in refs:
        if ref not in keys and ref not in fulls: findings.append({'entry':i,'code':'UNRESOLVED_LOCAL_REFERENCE'})
    return {'subset_pass':not findings,'findings':findings,'metrics':{'entries':len(entries),'findings':len(findings),'resolved_references':sum(ref in keys or ref in fulls for _,ref in refs)},'trace':trace,'scope':'Subset preflight, not a full FHIR validator or clinical validation.'}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
