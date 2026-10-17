import fs from 'node:fs';
const d=JSON.parse(fs.readFileSync(0,'utf8')), closed=new Set(d.closed??[]);
const dist=new Map(d.nodes.map(n=>[n,Infinity])), parent=new Map(),settled=[],pending=new Set(d.nodes);
dist.set(d.start,0);
while(pending.size){const u=[...pending].sort((a,b)=>dist.get(a)-dist.get(b)||a.localeCompare(b))[0];if(!Number.isFinite(dist.get(u)))break;pending.delete(u);settled.push({node:u,cost:dist.get(u)});if(u===d.goal)break;
 for(const e of d.edges){if(e.source!==u||closed.has(e.id)||!pending.has(e.target))continue;const alt=dist.get(u)+e.cost;if(alt<dist.get(e.target)){dist.set(e.target,alt);parent.set(e.target,u);}}}
let path=[];if(Number.isFinite(dist.get(d.goal))){let u=d.goal;while(u!==undefined){path.unshift(u);u=parent.get(u);}}
console.log(JSON.stringify({cost:Number.isFinite(dist.get(d.goal))?dist.get(d.goal):null,path,settled}));
