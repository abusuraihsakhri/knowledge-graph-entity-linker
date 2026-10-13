"use strict";
const get=id=>document.getElementById(id);
let last=null;
const sample=[
 {id:"HGNC:3236",label:"EGFR",type:"Gene",aliases:["epidermal growth factor receptor"]},
 {id:"EXAMPLE-DRUG-1",label:"erlotinib",type:"Drug",aliases:["Tarceva"]},
 {id:"EXAMPLE-DISEASE-1",label:"non-small cell lung cancer",type:"Disease",aliases:["NSCLC"]}
];
get("vocabulary").value=JSON.stringify(sample,null,2);
get("text").value="EGFR is mentioned with erlotinib in non-small cell lung cancer. EGFR appears twice.";
function result(output,error=false){
 get("result").textContent=typeof output==="string"?output:JSON.stringify(output,null,2);
 get("result").classList.toggle("error",error);
 get("status").textContent=error?"Input error":"Local evaluation completed";
 last=error||typeof output==="string"?null:output;
 get("export").disabled=!last;
}
document.querySelectorAll("[data-tab]").forEach(b=>b.addEventListener("click",()=>{
 const tab=b.dataset.tab;
 document.querySelectorAll("[data-tab]").forEach(x=>x.setAttribute("aria-selected",String(x===b)));
 get("linkPanel").hidden=tab!=="link";
 get("auditPanel").hidden=tab!=="audit";
 last=null;get("export").disabled=true;
 get("result").textContent="Run a tool to see results.";
 get("status").textContent="No current result";
}));
get("linkForm").addEventListener("submit",e=>{
 e.preventDefault();
 try{result(LinkerCore.linkEntities(get("text").value,JSON.parse(get("vocabulary").value)));}
 catch(err){result(err.message,true);}
});
get("auditForm").addEventListener("submit",e=>{
 e.preventDefault();
 try{result(LinkerCore.evaluateAudit({
  task_id:get("task_id").value,target_identifier:get("target_id").value,
  primary_metric:get("primary").value,secondary_metric:get("secondary").value,
  status_descriptor:get("descriptor").value,is_critical_flag:get("critical").checked
 }));}
 catch(err){result(err.message,true);}
});
get("export").addEventListener("click",()=>{
 if(!last)return;
 const url=URL.createObjectURL(new Blob([JSON.stringify(last,null,2)+"\n"],{type:"application/json"}));
 const anchor=document.createElement("a");
 anchor.href=url;anchor.download="graph-linker-result.json";anchor.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
});
