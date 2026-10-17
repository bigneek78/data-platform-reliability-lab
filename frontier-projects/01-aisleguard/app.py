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
def plan(grid, start, goal):
    if not isinstance(grid,list) or not grid or not all(isinstance(r,str) and r for r in grid): raise ValueError("Empty grid")
    h,w=len(grid),len(grid[0])
    if h*w>10000 or any(len(r)!=w or set(r)-set('.#') for r in grid): raise ValueError("Invalid rectangular grid")
    for point in (start,goal):
        if not isinstance(point,list) or len(point)!=2: raise ValueError("Coordinate pair required")
        for n in point: integer(n,"coordinate")
        if point[0]>=h or point[1]>=w or grid[point[0]][point[1]]=='#': raise ValueError("Blocked or out-of-bounds endpoint")
    home=Path(__file__).parent; build=home/'.build';build.mkdir(exist_ok=True)
    exe=build/'planner'
    if not exe.exists() or exe.stat().st_mtime < (home/'planner.cpp').stat().st_mtime:
        subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(home/'planner.cpp'),'-o',str(exe)],check=True,capture_output=True,text=True)
    text=f"{h} {w} {start[0]} {start[1]} {goal[0]} {goal[1]}\n"+'\n'.join(grid)+'\n'
    proc=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True)
    return json.loads(proc.stdout)
def run(d):
    initial=plan(d['grid'],d['start'],d['goal'])
    grid=[list(r) for r in d['grid']]
    for cell in d.get('closed',[]):
        if len(cell)!=2: raise ValueError("Closure needs two coordinates")
        r,c=cell;integer(r,'row');integer(c,'column')
        if r>=len(grid) or c>=len(grid[0]): raise ValueError("Closure outside grid")
        grid[r][c]='#'
    updated=plan([''.join(r) for r in grid],d['start'],d['goal'])
    return {'initial':initial,'updated':updated,'metrics':{'initial_steps':initial['cost'],'replanned_steps':updated['cost']},'trace':updated['path']}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
