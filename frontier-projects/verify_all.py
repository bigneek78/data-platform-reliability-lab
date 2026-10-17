from pathlib import Path
import subprocess,sys,json,re
home=Path(__file__).parent
catalog=json.loads((home/'catalog.json').read_text());failures=[];total=0
for record in catalog:
    folder=home/record['slug']
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=folder,capture_output=True,text=True)
    match=re.search(r'Ran (\d+) tests?',test.stdout+test.stderr)
    count=int(match.group(1)) if match else 0;total+=count
    demo=subprocess.run([sys.executable,'app.py'],cwd=folder,capture_output=True,text=True)
    print(record['slug'], 'tests=',count,'test_exit=',test.returncode,'demo_exit=',demo.returncode,flush=True)
    if test.returncode or demo.returncode or count!=8:
        failures.append(record['slug']);print(test.stdout+test.stderr+demo.stderr)
print(json.dumps({'projects':len(catalog),'tests':total,'failures':failures}))
raise SystemExit(bool(failures))
