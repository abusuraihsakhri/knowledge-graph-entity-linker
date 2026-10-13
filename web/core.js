(function(root) {
"use strict";
function metric(v,name) {
  const n=Number(v);
  if(v==="" || v===null || !Number.isFinite(n)) throw Error(name+" must be a finite number.");
  return n;
}
function evaluateAudit(p) {
  if(!p || !String(p.task_id||"").trim() || !String(p.target_identifier||"").trim()) throw Error("Task ID and target are required.");
  const primary=metric(p.primary_metric,"Primary metric"), secondary=metric(p.secondary_metric,"Secondary metric");
  const descriptor=String(p.status_descriptor||"");
  const alerts=[];
  if(primary>25) alerts.push({origin_worker:"InvariantQCWorker",urgency:"ELEVATED_RISK",summary:"Primary metric exceeds 25"});
  if(secondary>12 || p.is_critical_flag===true) alerts.push({origin_worker:"SafetyEscalationWorker",urgency:p.is_critical_flag===true?"CRITICAL_STAT_PANIC":"ELEVATED_RISK",summary:"Secondary metric exceeds 12 or critical flag is set"});
  if(["DISCORDANT","ANOMALY","MUTANT","VIOLATION","FAIL","REJECT"].some(w=>descriptor.toUpperCase().includes(w)))
    alerts.push({origin_worker:"ProtocolConformanceWorker",urgency:"ELEVATED_RISK",summary:"Flagged descriptor keyword"});
  const critical=alerts.some(x=>x.urgency==="CRITICAL_STAT_PANIC");
  return {mode:"local-unsigned-demo",task_id:String(p.task_id),target_identifier:String(p.target_identifier),
    overall_urgency:critical?"CRITICAL_STAT_PANIC":alerts.length?"ELEVATED_RISK":"ROUTINE",
    integrity_status:critical?"RECALIBRATION_REQUIRED":alerts.length?"DISCORDANT_ANOMALY":"VALIDATED_OPTIMAL",
    total_alerts:alerts.length,critical_alerts_count:critical?1:0,alerts,audit_hash:null,
    notice:"Deterministic demonstration only; no signed audit, clinical validation or standards certification."};
}
function escaped(s){return s.replace(/[.*+?^$()|[\]{}\\]/g,"\\$&").replace(/\s+/g,"\\s+");}
function linkEntities(text,vocabulary) {
  if(typeof text!=="string" || text.length>100000) throw Error("Text must be a string up to 100,000 characters.");
  if(!Array.isArray(vocabulary) || vocabulary.length>500) throw Error("Vocabulary must be an array of up to 500 entities.");
  const nodes=[],matches=[],seen=new Set();
  for(const item of vocabulary) {
    if(!item || typeof item!=="object" || Array.isArray(item)) throw Error("Invalid vocabulary entity.");
    const id=String(item.id||"").trim(),label=String(item.label||"").trim(),type=String(item.type||"Unspecified").trim();
    if(!id || !label || id.length>100 || label.length>200) throw Error("Every entity needs an ID and label.");
    if(seen.has(id)) throw Error("Duplicate entity ID: "+id);
    seen.add(id);
    if(item.aliases!=null && !Array.isArray(item.aliases)) throw Error("Aliases must be an array.");
    const aliases=[...new Set([label,...(item.aliases||[])].map(a=>String(a).trim()).filter(Boolean))];
    if(aliases.length>30 || aliases.some(a=>a.length>200)) throw Error("Too many or overly long aliases.");
    nodes.push({id,label,type});
    for(const alias of aliases) {
      const re=new RegExp("(^|[^\\p{L}\\p{N}_])("+escaped(alias)+")(?=$|[^\\p{L}\\p{N}_])","giu");
      for(const m of text.matchAll(re)) {
        const start=m.index+m[1].length;
        matches.push({id,label,type,start,end:start+m[2].length,matched_text:m[2]});
        if(matches.length>20000) throw Error("Too many mentions.");
      }
    }
  }
  matches.sort((a,b)=>a.start-b.start || (b.end-b.start)-(a.end-a.start) || a.id.localeCompare(b.id));
  const mentions=[];
  for(const match of matches) if(!mentions.some(m=>match.start<m.end && m.start<match.end)) mentions.push(match);
  const found=new Set(mentions.map(m=>m.id)),filtered=nodes.filter(n=>found.has(n.id));
  const edges=[];
  for(let i=0;i<filtered.length;i++) for(let j=i+1;j<filtered.length;j++)
    edges.push({source:filtered[i].id,target:filtered[j].id,relation:"co_mentioned_with"});
  return {mode:"local-lexical-matching",nodes:filtered,mentions,edges,
    statistics:{entities:filtered.length,mentions:mentions.length,co_mentions:edges.length},
    notice:"Lexical matches and co-mentions are not evidence of biological relations."};
}
const api={evaluateAudit,linkEntities};
if(typeof module!=="undefined" && module.exports) module.exports=api; else root.LinkerCore=api;
})(typeof globalThis!=="undefined"?globalThis:this);
