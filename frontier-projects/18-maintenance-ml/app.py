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


import random
def sigmoid(z): return 1/(1+math.exp(-max(-50,min(50,z))))
def fit_scaler(rows):
    means=[sum(r[j] for r in rows)/len(rows) for j in range(2)]
    scales=[max(1e-9,(sum((r[j]-means[j])**2 for r in rows)/len(rows))**.5) for j in range(2)]
    return means,scales
def run(d):
    seed=integer(d['seed'],'seed');n=integer(d['rows'],'rows',40);epochs=integer(d['epochs'],'epochs',1);lr=number(d['learning_rate'],'learning_rate',0);shift=number(d['drift_shift'],'drift_shift')
    if n>10000 or epochs>5000 or not 0<lr<=1: raise ValueError("Demo resource or learning-rate limit exceeded")
    rng=random.Random(seed);rows=[]
    for _ in range(n):
        temp=rng.gauss(60,8);vibration=rng.gauss(2,.7);noise=rng.gauss(0,.25)
        label=int((temp-60)/8+1.4*(vibration-2)/.7+noise>.6);rows.append([temp,vibration,label])
    rng.shuffle(rows);cut=int(.75*n);train,test=rows[:cut],rows[cut:];means,scales=fit_scaler(train)
    def transform(r): return [1]+[(r[j]-means[j])/scales[j] for j in range(2)]
    w=[0.,0.,0.];losses=[]
    for epoch in range(epochs):
        grad=[0.,0.,0.];loss=0
        for row in train:
            x=transform(row);p=sigmoid(sum(a*b for a,b in zip(w,x)));y=row[2]
            for j in range(3): grad[j]+=(p-y)*x[j]
            loss-=y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))
        w=[a-lr*g/len(train) for a,g in zip(w,grad)]
        if epoch%10==0 or epoch==epochs-1: losses.append({'epoch':epoch,'training_log_loss':loss/len(train)})
    cm={'tn':0,'fp':0,'fn':0,'tp':0}
    for row in test:
        pred=int(sigmoid(sum(a*b for a,b in zip(w,transform(row))))>=.5);cm[('tn','fp','fn','tp')[row[2]*2+pred]]+=1
    shifted=[[r[0]+shift*scales[0],r[1],r[2]] for r in test]
    drift=[abs(sum(r[j] for r in shifted)/len(shifted)-means[j])/scales[j] for j in range(2)]
    return {'weights':w,'scaler':{'means':means,'scales':scales},'confusion':cm,'drift_standardized_mean_shift':drift,'drift_review':any(x>1 for x in drift),'metrics':{'holdout_accuracy':(cm['tp']+cm['tn'])/len(test),'holdout_rows':len(test),'training_rows':len(train),'initial_log_loss':losses[0]['training_log_loss'],'final_log_loss':losses[-1]['training_log_loss']},'trace':losses,'scope':'Synthetic educational classifier; no real equipment predictive validation.'}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
