const test=require("node:test"),assert=require("node:assert/strict");
const {evaluateAudit,linkEntities}=require("./core.js");
test("audits show nominal/elevated/critical correctly",()=>{
 const p={task_id:"t",target_identifier:"k",primary_metric:1,secondary_metric:2,status_descriptor:"NOMINAL"};
 assert.equal(evaluateAudit(p).overall_urgency,"ROUTINE");
 assert.equal(evaluateAudit({...p,primary_metric:30}).overall_urgency,"ELEVATED_RISK");
 assert.equal(evaluateAudit({...p,is_critical_flag:true}).overall_urgency,"CRITICAL_STAT_PANIC");
 assert.equal(evaluateAudit(p).audit_hash,null);
});
test("reject nonfinite metrics",()=>assert.throws(()=>evaluateAudit({task_id:"t",target_identifier:"k",primary_metric:"",secondary_metric:3}),/finite/));
test("unique nodes, aliases, co-mentions",()=>{
 const r=linkEntities("EGFR is paired with erlotinib. Epidermal growth factor receptor.",[
 {id:"HGNC:3236",label:"EGFR",type:"Gene",aliases:["epidermal growth factor receptor"]},
 {id:"DRUG",label:"erlotinib",type:"Drug"}]);
 assert.equal(r.nodes.length,2);assert.equal(r.mentions.length,3);assert.equal(r.edges.length,1);
});
test("word boundaries and escaped regex",()=>{
 const r=linkEntities("notEGFR EGFR A+B",[{id:"g",label:"EGFR"},{id:"x",label:"A+B"}]);
 assert.equal(r.mentions.length,2);
});
test("duplicate dictionary IDs rejected",()=>assert.throws(()=>linkEntities("",[{id:"x",label:"one"},{id:"x",label:"two"}]),/Duplicate/));
