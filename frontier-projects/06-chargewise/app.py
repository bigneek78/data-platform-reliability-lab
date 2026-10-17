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
    prices,cap,vs=d['prices'],d['capacity'],d['vehicles'];unique(vs);n=len(prices)
    if not n or len(cap)!=n: raise ValueError("Aligned nonempty hourly series required")
    for x in prices: number(x,'price',0)
    for x in cap: integer(x,'capacity')
    for v in vs:
        for key in ('arrival','departure','need','rate'): integer(v[key],key)
        if not v['arrival']<v['departure']<=n or v['rate']==0: raise ValueError("Invalid availability or rate")
    count=2+len(vs)+n;s=count-2;t=count-1;g=[[] for _ in range(count)]
    def edge(a,b,c,w):
        g[a].append([b,len(g[b]),c,w,c]);g[b].append([a,len(g[a])-1,0,-w,0]);return g[a][-1]
    tracks=[]
    for i,v in enumerate(vs):
        edge(s,i,v['need'],0)
        for h in range(v['arrival'],v['departure']): tracks.append((i,h,edge(i,len(vs)+h,v['rate'],prices[h])))
    for h in range(n): edge(len(vs)+h,t,cap[h],0)
    flow=0;cost=0
    while True:
        dist=[math.inf]*count;dist[s]=0;prev=[None]*count
        for _ in range(count-1):
            changed=False
            for u in range(count):
                if not math.isfinite(dist[u]): continue
                for k,e in enumerate(g[u]):
                    if e[2]>0 and dist[u]+e[3]<dist[e[0]]-1e-10:
                        dist[e[0]]=dist[u]+e[3];prev[e[0]]=(u,k);changed=True
            if not changed: break
        if prev[t] is None: break
        amount=10**18;x=t
        while x!=s:
            u,k=prev[x];amount=min(amount,g[u][k][2]);x=u
        x=t
        while x!=s:
            u,k=prev[x];e=g[u][k];e[2]-=amount;g[x][e[1]][2]+=amount;x=u
        flow+=amount;cost+=amount*dist[t]
    schedule=[{'vehicle':vs[i]['id'],'hour':h,'kwh':e[4]-e[2]} for i,h,e in tracks if e[4]>e[2]]
    trace=[sum(e['kwh'] for e in schedule if e['hour']==h) for h in range(n)]
    return {'schedule':schedule,'unmet_by_vehicle':{v['id']:v['need']-sum(e['kwh'] for e in schedule if e['vehicle']==v['id']) for v in vs},'metrics':{'delivered_kwh':flow,'unmet_kwh':sum(v['need'] for v in vs)-flow,'cost_units':cost},'trace':trace}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
