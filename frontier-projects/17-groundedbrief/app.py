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


import re
from collections import Counter
STOP={'the','a','an','and','in','is','for','to','of','how','what','it','when','its','after'}
def tokens(s): return [x for x in re.findall(r'[a-z0-9]+',s.lower()) if x not in STOP]
def run(d):
    docs=d['documents'];unique(docs);threshold=number(d['threshold'],'threshold',0)
    if not docs or not isinstance(d['query'],str) or threshold>1: raise ValueError("Documents, query and threshold in [0,1] required")
    if any(not isinstance(x['text'],str) or not x['text'].strip() for x in docs): raise ValueError("Nonempty document text required")
    bags=[Counter(tokens(x['text'])) for x in docs];query=Counter(tokens(d['query']));vocab=set().union(*bags,query)
    idf={w:math.log((1+len(docs))/(1+sum(w in b for b in bags)))+1 for w in vocab}
    def vector(b): return {w:c*idf[w] for w,c in b.items()}
    qv=vector(query);qn=sum(x*x for x in qv.values())**.5;scored=[]
    for doc,bag in zip(docs,bags):
        v=vector(bag);norm=sum(x*x for x in v.values())**.5;score=sum(qv.get(w,0)*x for w,x in v.items())/(qn*norm) if qn and norm else 0
        scored.append({'id':doc['id'],'score':score})
    ranked=sorted(scored,key=lambda x:(-x['score'],x['id']));top=ranked[0];supported=top['score']>=threshold and top['score']>0
    if supported:
        doc=next(x for x in docs if x['id']==top['id']);sentences=[s.strip() for s in re.split(r'(?<=[.!?])\s+',doc['text']) if s.strip()]
        evidence=min(sentences,key=lambda s:(-len(set(tokens(s))&set(query)),len(s)))
        answer={'citation':top['id'],'quote':evidence}
    else: answer=None
    return {'decision':'EVIDENCE_FOUND' if supported else 'ABSTAIN','evidence':answer,'metrics':{'top_similarity':top['score'],'documents_scored':len(docs),'evidence_passages':int(supported)},'trace':ranked,'scope':'Extractive lexical retrieval; no generative language model is called.'}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
