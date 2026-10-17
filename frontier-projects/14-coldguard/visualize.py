"""Rebuild exact architecture, result chart, and animated execution trace.
Optional authoring dependency: Pillow. No network access or credentials.
"""
from pathlib import Path
import json, html, textwrap
from PIL import Image, ImageDraw, ImageFont
HOME=Path(__file__).parent
CFG=json.loads((HOME/'visual-config.json').read_text());R=json.loads((HOME/'results.json').read_text())
INK='#102638';TEAL='#007f80';GOLD='#d98e24';MUTED='#526878';PAPER='#f3f7f8'
def esc(x):return html.escape(str(x))
def font(size,bold=False):
    candidates=(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])+["C:/Windows/Fonts/arial.ttf","/System/Library/Fonts/Helvetica.ttc"]
    for p in candidates:
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()
def header(sub):
    im=Image.new('RGB',(1000,620),PAPER);dr=ImageDraw.Draw(im);dr.rectangle((0,0,1000,110),fill=INK)
    dr.text((35,20),CFG['name'],font=font(30,True),fill='white');dr.text((35,65),sub,font=font(18),fill='#b5d9dc');return im,dr
title='Cold-chain interval evidence accounting';unit='Y: minutes | X: evidence category';mode='bar';labels=['Within band','Excursion','Unknown'];series=[('Logged duration',[R['metrics']['within_minutes'],R['metrics']['outside_minutes'],R['metrics']['unknown_minutes']])]
im,dr=header(title+' | synthetic fixture')
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620" viewBox="0 0 1000 620"><rect width="1000" height="620" fill="{PAPER}"/><rect width="1000" height="110" fill="{INK}"/><g font-family="Arial,sans-serif"><text x="35" y="45" fill="white" font-size="30" font-weight="bold">{esc(CFG["name"])}</text><text x="35" y="82" fill="#b5d9dc" font-size="18">{esc(title)} | synthetic fixture</text>']
colors=[TEAL,GOLD,'#566ec7'];numbers=[v for _,ys in series for v in ys if v is not None];top=max(numbers+[1])*1.15
left,right,bottom,up=100,930,490,165;step=(right-left)/max(1,len(labels))
def xy(i,v):return left+(i+.5)*step,bottom-(bottom-up)*v/top
for tick in range(5):
    v=top*tick/4;y=xy(0,v)[1];dr.line((left,y,right,y),fill='#d3e0e3',width=1);dr.text((15,y-10),f'{v:.3g}',font=font(16),fill=MUTED)
    parts.append(f'<path d="M{left} {y} H{right}" stroke="#d3e0e3"/><text x="15" y="{y+5}" font-size="16" fill="{MUTED}">{v:.3g}</text>')
for k,(label,ys) in enumerate(series):
    color=colors[k%len(colors)];dr.rectangle((100+k*265,125,116+k*265,139),fill=color);dr.text((125+k*265,121),label,font=font(16),fill=INK)
    parts.append(f'<rect x="{100+k*265}" y="125" width="16" height="14" fill="{color}"/><text x="{125+k*265}" y="138" fill="{INK}" font-size="16">{esc(label)}</text>')
    prev=None
    for i,v in enumerate(ys):
        if v is None:prev=None;continue
        x,y=xy(i,v)
        if mode=='bar':
            width=min(100,step*.7/len(series));x1=x+(k-(len(series)-1)/2)*width-width*.45;x2=x1+width*.9
            dr.rectangle((x1,min(y,bottom-1),x2,bottom),fill=color);dr.text((x1,y-23),f'{v:.3g}',font=font(15),fill=INK)
            parts.append(f'<rect x="{x1}" y="{min(y,bottom-1)}" width="{width*.9}" height="{max(1,bottom-y)}" fill="{color}"/><text x="{x1}" y="{y-6}" font-size="15" fill="{INK}">{v:.3g}</text>')
        else:
            if prev:
                dr.line((*prev,x,y),fill=color,width=3);parts.append(f'<path d="M{prev[0]} {prev[1]} L{x} {y}" fill="none" stroke="{color}" stroke-width="3"/>')
            dr.ellipse((x-4,y-4,x+4,y+4),fill=color);parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>');prev=(x,y)
for i,label in enumerate(labels):
    if len(labels)>12 and i%max(1,len(labels)//8):continue
    x,_=xy(i,0);text=str(label);dr.text((x-min(35,len(text)*4),510),text,font=font(14),fill=MUTED)
    parts.append(f'<text x="{x}" y="525" text-anchor="middle" fill="{MUTED}" font-size="14">{esc(text)}</text>')
dr.text((35,570),unit,font=font(18),fill=INK);dr.text((35,598),'Source: results.json | illustrative results, not operational performance',font=font(14),fill=MUTED)
parts.append(f'<text x="35" y="580" font-size="18" fill="{INK}">{esc(unit)}</text><text x="35" y="607" font-size="14" fill="{MUTED}">Source: results.json | synthetic evidence</text></g></svg>')
im.save(HOME/'assets/results.png');(HOME/'assets/results.svg').write_text(''.join(parts))
nodes=CFG['nodes'];parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620" viewBox="0 0 1000 620"><rect width="1000" height="620" fill="{PAPER}"/><rect width="1000" height="110" fill="{INK}"/><g font-family="Arial,sans-serif"><text x="35" y="48" fill="white" font-size="30" font-weight="bold">{esc(CFG["name"])}</text><text x="35" y="82" fill="#b5d9dc" font-size="18">Architecture | local prototype</text>']
positions=[(70,160),(540,160),(70,360),(540,360)]
for i,(label,(x,y)) in enumerate(zip(nodes,positions)):
    parts.append(f'<rect x="{x}" y="{y}" width="390" height="120" rx="16" fill="white" stroke="{TEAL}" stroke-width="3"/><text x="{x+20}" y="{y+35}" font-size="18" fill="{TEAL}">{i+1:02d}</text><text x="{x+20}" y="{y+80}" font-size="23" fill="{INK}">{esc(label)}</text>')
parts.append(f'<path d="M460 220 L525 220 M520 214 L530 220 L520 226 M735 285 L735 320 L265 320 L265 347 M259 342 L265 352 L271 342 M460 420 L525 420 M520 414 L530 420 L520 426" fill="none" stroke="{MUTED}" stroke-width="3"/><text x="70" y="555" fill="{MUTED}" font-size="19">Fixture input → executable decision → inspectable evidence</text></g></svg>')
(HOME/'assets/architecture.svg').write_text(''.join(parts))
trace=R.get('trace',[]);frames=[];limit=min(40,max(1,len(trace)))
indices=list(range(len(trace))) if len(trace)<=40 else [round(i*(len(trace)-1)/39) for i in range(40)]
if not indices:indices=[0]
if len(indices)==1:indices=indices*4
for pos,i in enumerate(indices):
    frame,draw=header('Execution replay | actual results.json trace')
    draw.text((35,140),f'Step {i+1} / {len(trace)}',font=font(25,True),fill=TEAL)
    record=trace[i] if trace else {'note':'No trace records'};lines=json.dumps(record,indent=2,ensure_ascii=False).splitlines()
    rendered=[]
    for line in lines:rendered.extend(textwrap.wrap(line,75) or [''])
    for j,line in enumerate(rendered[:12]):
        if len(trace)<=1 and j==pos%max(1,len(rendered)):draw.rectangle((35,192+j*25,960,216+j*25),fill='#d6ebeb')
        draw.text((40,195+j*25),line,font=font(18),fill=INK)
    draw.rounded_rectangle((35,530,965,544),radius=6,fill='#dbe6e8');draw.rounded_rectangle((35,530,35+int(930*(pos+1)/len(indices)),544),radius=6,fill=TEAL)
    draw.text((35,574),'Synthetic evidence replay. No live hardware, clinical or production claim.',font=font(16),fill=MUTED)
    frames.append(frame.quantize(colors=64))
frames[0].save(HOME/'assets/replay.gif',save_all=True,append_images=frames[1:],duration=600,loop=0,optimize=True)
print('Rebuilt 4 assets from results.json and visual-config.json')
