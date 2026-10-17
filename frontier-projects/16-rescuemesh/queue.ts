import fs from 'node:fs';
interface Message {id:string; body:string; expires:number; last:number; attempts:number; status:string;}
const d=JSON.parse(fs.readFileSync(0,'utf8'));const messages=new Map<string,Message>();const trace:object[]=[];let duplicate=0;
for(const e of d.events){
 for(const m of messages.values())if(m.status==='pending' && e.time>=m.expires){m.status='expired';trace.push({time:e.time,op:'expire',id:m.id});}
 if(e.op==='enqueue'){
  if(messages.has(e.id)){duplicate++;trace.push({time:e.time,op:'duplicate',id:e.id});}
  else messages.set(e.id,{id:e.id,body:e.body,expires:e.time+e.ttl,last:-Infinity,attempts:0,status:'pending'});
 }
 if(e.op==='tick'&&e.online)for(const m of messages.values())if(m.status==='pending'&&e.time-m.last>=d.retry){m.last=e.time;m.attempts++;trace.push({time:e.time,op:'send',id:m.id,attempt:m.attempts});}
 if(e.op==='ack'){
  const m=messages.get(e.id);if(m&&m.status==='pending'&&m.attempts>0){m.status='delivered';trace.push({time:e.time,op:'acknowledged',id:e.id});}
  else trace.push({time:e.time,op:'ignored_ack',id:e.id});
 }
}
const all=[...messages.values()];console.log(JSON.stringify({delivered:all.filter(m=>m.status==='delivered').map(m=>m.id),expired:all.filter(m=>m.status==='expired').map(m=>m.id),pending:all.filter(m=>m.status==='pending').map(m=>m.id),metrics:{send_attempts:all.reduce((s,m)=>s+m.attempts,0),acknowledged:all.filter(m=>m.status==='delivered').length,expired:all.filter(m=>m.status==='expired').length,duplicate_enqueues:duplicate},trace}));
