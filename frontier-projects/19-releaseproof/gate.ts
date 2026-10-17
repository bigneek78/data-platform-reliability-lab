import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
interface Finding{code:string;path?:string;}
const d=JSON.parse(fs.readFileSync(0,'utf8'));const findings:Finding[]=[];const trace:object[]=[];
let base:string;try{base=fs.realpathSync(d.base);}catch{console.log(JSON.stringify({eligible:false,findings:[{code:'MISSING_BASE'}],metrics:{checked_artifacts:0,findings:1},trace:[]}));process.exit(0);}
for(const a of d.artifacts){
 const candidate=path.resolve(base,a.path);if(path.isAbsolute(a.path)||candidate===base||!candidate.startsWith(base+path.sep)){findings.push({code:'UNSAFE_PATH',path:a.path});continue;}
 try{const resolved=fs.realpathSync(candidate);if(!resolved.startsWith(base+path.sep)||fs.lstatSync(candidate).isSymbolicLink()||!fs.statSync(resolved).isFile()){findings.push({code:'UNSAFE_PATH',path:a.path});continue;}
 const digest=crypto.createHash('sha256').update(fs.readFileSync(candidate)).digest('hex');const ok=digest===a.sha256;trace.push({artifact:a.path,hash_match:ok});if(!ok)findings.push({code:'HASH_MISMATCH',path:a.path});
 }catch{findings.push({code:'MISSING_OR_UNREADABLE_ARTIFACT',path:a.path});}
}
const t=d.test_record;if(!t||![t.total,t.passed,t.failed].every(Number.isInteger)||t.total<=0||t.passed!==t.total||t.failed!==0)findings.push({code:'TEST_EVIDENCE_INVALID'});
if(!t||t.commit!==d.commit)findings.push({code:'COMMIT_MISMATCH'});
if(!t||!Number.isFinite(t.time)||t.time>d.now||d.now-t.time>d.max_age)findings.push({code:'EVIDENCE_AGE_INVALID'});
console.log(JSON.stringify({eligible:findings.length===0,findings,metrics:{checked_artifacts:trace.length,findings:findings.length,claimed_tests:t?.total??0},trace,scope:'Local digest and record checks; not a signed provenance verifier.'}));
