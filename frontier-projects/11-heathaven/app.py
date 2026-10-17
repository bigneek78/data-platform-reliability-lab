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


import itertools
def run(d):
    areas,centers=d['areas'],d['centers'];unique(areas);unique(centers)
    budget=integer(d['budget'],'budget');radius=number(d['radius'],'radius',0)
    if len(centers)>18 or budget>len(centers): raise ValueError("Exact search limited to 18 candidates")
    for item in areas+centers:
        number(item['x'],'x');number(item['y'],'y')
    for a in areas: number(a['weight'],'demand',0)
    coverage=[{j for j,a in enumerate(areas) if abs(c['x']-a['x'])+abs(c['y']-a['y'])<=radius} for c in centers]
    def covered(chosen): return set().union(*(coverage[i] for i in chosen)) if chosen else set()
    def score(chosen): return sum(areas[j]['weight'] for j in covered(chosen))
    choices=[c for k in range(budget+1) for c in itertools.combinations(range(len(centers)),k)]
    best=min(choices,key=lambda c:(-score(c),len(c),tuple(centers[i]['id'] for i in c)))
    greedy=[]
    for _ in range(budget):
        remaining=[i for i in range(len(centers)) if i not in greedy]
        if not remaining: break
        i=min(remaining,key=lambda i:(-score(greedy+[i]),centers[i]['id']))
        if score(greedy+[i])==score(greedy): break
        greedy.append(i)
    return {'selected_centers':[centers[i]['id'] for i in best],'uncovered_areas':[a['id'] for j,a in enumerate(areas) if j not in covered(best)],'metrics':{'covered_demand':score(best),'total_demand':sum(a['weight'] for a in areas),'greedy_covered_demand':score(greedy)},'trace':[{'area':a['id'],'weight':a['weight'],'covered':j in covered(best)} for j,a in enumerate(areas)]}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
