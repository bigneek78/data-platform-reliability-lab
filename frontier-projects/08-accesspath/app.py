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


import heapq
def run(d):
    nodes=d['nodes'];edges=d['edges'];unique(edges)
    slope=number(d['max_slope'],'max_slope',0);width=number(d['min_width'],'min_width',0)
    if len(set(nodes))!=len(nodes) or d['start'] not in nodes or d['goal'] not in nodes: raise ValueError("Invalid nodes")
    graph={n:[] for n in nodes};excluded=[]
    for e in edges:
        for k in ('length','slope','width'): number(e[k],k,0)
        if e['source'] not in graph or e['target'] not in graph or not isinstance(e['stairs'],bool): raise ValueError("Invalid edge")
        reasons=[]
        if e['stairs']: reasons.append('stairs')
        if e['slope']>slope: reasons.append('slope')
        if e['width']<width: reasons.append('width')
        if reasons: excluded.append({'id':e['id'],'reasons':reasons})
        else: graph[e['source']].append(e)
    q=[(0,d['start'])];dist={d['start']:0};parent={};settled=[]
    while q:
        cost,u=heapq.heappop(q)
        if cost!=dist[u]: continue
        settled.append({'node':u,'distance':cost})
        if u==d['goal']: break
        for e in graph[u]:
            v=e['target'];alt=cost+e['length']
            if alt<dist.get(v,math.inf): dist[v]=alt;parent[v]=u;heapq.heappush(q,(alt,v))
    path=[];u=d['goal']
    if u in dist:
        while True:
            path.append(u)
            if u==d['start']: break
            u=parent[u]
        path.reverse()
    return {'path':path,'excluded':excluded,'metrics':{'route_length':dist.get(d['goal']),'excluded_edges':len(excluded)},'trace':settled}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
