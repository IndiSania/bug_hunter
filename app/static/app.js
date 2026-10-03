let data=null, chart=null;
const file=document.getElementById("file");
file.addEventListener("change",()=>{document.getElementById("filename").textContent=file.files[0]?.name||"Belum ada file dipilih"});
async function startScan(){
 const f=file.files[0]; if(!f){showError("Pilih file .py atau .zip terlebih dahulu.");return}
 document.getElementById("loading").hidden=false; document.getElementById("error").hidden=true;
 try{
  const fd=new FormData(); fd.append("file",f);
  const res=await fetch("/scan",{method:"POST",body:fd}); const json=await res.json();
  if(!res.ok) throw new Error(json.error||"Scan gagal");
  data=json; render(json);
 }catch(e){showError(e.message)}finally{document.getElementById("loading").hidden=true}
}
function showError(msg){const e=document.getElementById("error");e.textContent=msg;e.hidden=false}
function render(d){
 document.getElementById("results").hidden=false;
 document.getElementById("score").textContent=d.score;
 document.getElementById("files").textContent=d.files_scanned;
 document.getElementById("lines").textContent=d.lines.toLocaleString();
 document.getElementById("total").textContent=d.total;
 const c=d.counts;
 document.getElementById("summary").innerHTML=["critical","high","medium","low","info"].map(s=>`<div class="sev"><b class="${s}">${s}</b><strong>${c[s]||0}</strong></div>`).join("");
 if(chart) chart.destroy();
 chart=new Chart(document.getElementById("chart"),{type:"bar",data:{labels:["Critical","High","Medium","Low","Info"],datasets:[{data:[c.critical,c.high,c.medium,c.low,c.info],borderRadius:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:"#657185",font:{size:10}}},y:{beginAtZero:true,grid:{color:"#1a222d"},ticks:{color:"#657185",font:{size:9},stepSize:1}}}}});
 document.getElementById("download").href="/report/"+d.id;
 renderFindings();
 document.getElementById("results").scrollIntoView({behavior:"smooth"});
}
function renderFindings(){
 if(!data)return;
 const q=document.getElementById("search").value.toLowerCase(), sev=document.getElementById("severity").value;
 const items=data.findings.filter(x=>(!sev||x.severity===sev)&&JSON.stringify(x).toLowerCase().includes(q));
 const el=document.getElementById("findingList");
 if(!items.length){el.innerHTML='<div class="empty">Tidak ada temuan yang cocok.</div>';return}
 el.innerHTML=items.map(x=>`<div class="finding"><div class="badge ${x.severity}">${x.severity}</div><div><b>${escapeHtml(x.message)}</b><p>${escapeHtml(x.suggestion)}</p><small>${escapeHtml(x.file)} · line ${x.line} · ${x.rule}</small></div><span class="badge">${x.rule}</span></div>`).join("");
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
