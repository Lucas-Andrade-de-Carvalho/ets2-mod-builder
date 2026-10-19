
(function(){
"use strict";
const el=id=>document.getElementById(id),ui={map:el("mapFile"),cargo:el("cargoFile"),run:el("generate"),message:el("status"),bar:el("bar"),report:el("report"),detail:el("detail")};
const names=["milho","soja","adubo","madeira","pluma de algodão","cimento","sacos de batata","sacos de laranja","bobinas 2","cimento em palete","cimento em cinta","cerveja","tijolos","pedra de granito","pedra de granito","palete alto","ração mineral","xerém ração","sacaria de ração","sacaria de ração","soja alta","milho alto","sorgo para ração"];
const patterns=[
["racao",/\b(racao|xerem|alimento para gado|feed animal)\b/],["sorgo",/\bsorgo\b/],["milho",/\bmilho\b/],["soja",/\bsoja\b/],
["adubo",/\b(adubo|fertilizante)\b/],["algodao",/\b(pluma|algodao)\b/],["batata",/\bbatata\b/],["laranja",/\blaranja\b/],
["cerveja",/\b(cerveja|beer)\b/],["cimento",/\bcimento\b/],["tijolo",/\btijolo[s]?\b/],["granito",/\bgranito\b/],
["madeira",/\b(madeira|madeirame)\b/],["aco",/\b(bobina de aco|bobina de chapa|steel coil)\b/],["palete",/\b(palete vazio|palete de madeira)\b/]
];
const sectors=[
["silo",/(silo|cooperativa|cerealista|armazem de graos|grain storage)/],
["fazenda",/(fazenda|faz0|faz1|faz2|faz3|faz4|faz5|agropecuaria|sitio agricola|cultivo agricola|farm|plantacao)/],
["pecuaria",/(pecuaria|granja|criatorio de gado|confinamento)/],
["racoes",/(fabrica de racao|industria de racao|nutricao animal|feed mill)/],
["moinho",/(moinho|esmagadora de soja|beneficiadora de graos)/],
["adubeira",/(industria de fertilizantes|fabrica de adubo|yara|mosaic)/],
["serraria",/(serraria|industria madeireira|sawmill)/],
["floresta",/(florestal|reflorestamento|extracao de madeira)/],
["textil",/(textil|tecelagem|fiacao|fabrica de tecidos)/],
["algodoeira",/(algodoeira|beneficiamento de algodao)/],
["ceramica",/(olaria|ceramica|tijolaria|fabrica de tijolos)/],
["cimenteira",/(cimenteira|fabrica de cimento|industria de cimento)/],
["pedreira",/(pedreira|extracao de granito|quarry)/],
["obras",/(construtora|obra civil|canteiro|construcao|empreiteira)/],
["materiais",/(material de construcao|deposito de materiais|loja de materiais)/],
["cervejaria",/(ambev|heineken|cervejaria|brewery)/],
["bebidas",/(distribuidora de bebidas|deposito de bebidas)/],
["supermercado",/(supermercado|hipermercado|supermarket|mercearia)/],
["hortifruti",/(ceasa|hortifruti|entreposto de frutas)/],
["alimentos",/(distribuidora de alimentos|atacado de alimentos)/],
["siderurgica",/(siderurgica|siderurgia|gerdau|usiminas|csn)/],
["metalurgica",/(metalurgica|industria mecanica|fabrica de maquinas)/],
["paletes",/(fabrica de paletes|fabricante de pallets)/],
["posto",/(posto|refinaria|petrobras|fuel station)/],
["concessionaria",/(concessionaria|dealership|revenda de carros)/],
["correios",/(correios|correio|sedex)/]
];
const flows={
 milho:{out:["fazenda"],in:["silo","moinho","racoes"]},
 soja:{out:["fazenda"],in:["silo","moinho"]},
 sorgo:{out:["fazenda"],in:["silo","racoes","pecuaria"]},
 adubo:{out:["adubeira"],in:["fazenda","pecuaria"]},
 madeira:{out:["serraria","floresta"],in:["obras","materiais"]},
 algodao:{out:["fazenda","algodoeira"],in:["textil"]},
 cimento:{out:["cimenteira"],in:["obras","materiais"]},
 batata:{out:["fazenda"],in:["hortifruti","alimentos","supermercado"]},
 laranja:{out:["fazenda"],in:["hortifruti","alimentos","supermercado"]},
 cerveja:{out:["cervejaria"],in:["bebidas","supermercado"]},
 tijolo:{out:["ceramica"],in:["obras","materiais"]},
 granito:{out:["pedreira"],in:["obras","materiais"]},
 racao:{out:["racoes"],in:["fazenda","pecuaria"]},
 aco:{out:["siderurgica"],in:["metalurgica","obras"]},
 palete:{out:["paletes"],in:["alimentos","bebidas","materiais"]}
};
const norm=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[_-]/g," ");
const pathNorm=s=>String(s).replace(/\\/g,"/").replace(/^\/+/,"").replace(/^\.\/+/,"");
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const yieldUI=()=>new Promise(r=>setTimeout(r,0));
const say=(msg,pct)=>{ui.message.textContent=msg;ui.bar.style.width=Math.max(0,Math.min(100,pct))+"%"};
const known=(id,label)=>{const x=norm(id)+" "+norm(label);for(const [r,re] of sectors)if(re.test(x))return r;const flat=norm(id).replace(/ /g,"");if(/^silos?/.test(flat))return"silo";if(/^ceasa/.test(flat))return"hortifruti";if(/^olaria/.test(flat))return"ceramica";if(/^fazenda/.test(flat))return"fazenda";if(/^posto/.test(flat))return"posto";return"desconhecida"};
const kind=name=>{const x=norm(name);for(const [k,re] of patterns)if(re.test(x))return k;return null};
const companyPath=raw=>{
 const p=pathNorm(raw);
 const m=p.match(/(?:^|\/)(?:def\/)?company\/(.+)$/i);
 if(m)return"def/company/"+m[1];
 const reg=p.match(/(?:^|\/)(company(?:\.[a-z0-9_-]+)?\.sii)$/i);
 return reg?"def/"+reg[1]:null
};
const cargoPath=raw=>{
 const p=pathNorm(raw);
 const m=p.match(/(?:^|\/)(?:def\/)?(cargo\/.+|vehicle\/.+|cargo\.[a-z0-9_-]+\.sii)$/i);
 return m?"def/"+m[1]:null
};
const companyMeta=path=>{
 const a=path.match(/^def\/company\/([a-z0-9_]+)\/(in|out|editor)\/(.+)$/i);
 if(a)return{id:a[1].toLowerCase(),type:a[2].toLowerCase(),name:a[3]};
 const b=path.match(/^def\/company\/([a-z0-9_]+)\.sii$/i);
 return b?{id:b[1].toLowerCase(),type:"permanent",name:b[1]}:null
};
function zipRead(file){
 return file.slice(0,6).arrayBuffer().then(arr=>{
  const a=new Uint8Array(arr);
  if(a[0]!==80||a[1]!==75)throw Error("O arquivo "+file.name+" não está em ZIP/SCS ZIP. Se for HashFS, extraia a DEF.");
  return JSZip.loadAsync(file,{createFolders:false,checkCRC32:false})
 })
}
function entries(zip){return Object.entries(zip.files).filter(([,o])=>!o.dir)}
async function loadMap(zip){
 const companies=new Map(),files=new Map();
 for(const [raw,obj] of entries(zip)){
  const p=companyPath(raw);if(!p)continue;
  const key=p.toLowerCase();if(files.has(key))throw Error("Caminho duplicado no mapa: "+p);
  files.set(key,{p,obj});
  const m=companyMeta(p);if(!m)continue;
  if(!companies.has(m.id))companies.set(m.id,{id:m.id,name:"",role:"desconhecida",old:[],editor:0});
  const c=companies.get(m.id);
  if(m.type==="editor")c.editor++;
  if(m.type==="in"||m.type==="out")c.old.push({p,dir:m.type,stem:m.name.replace(/\.sii$/i,"")});
 }
 if(!companies.size)throw Error("Nenhuma empresa na Company informada.");
 let i=0;
 for(const v of files.values()){
  const m=companyMeta(v.p);if(!m||m.type!=="permanent")continue;
  const c=companies.get(m.id);if(!c)continue;
  const txt=await v.obj.async("text"),name=txt.match(/^\s*name\s*:\s*"([^"]+)"/mi);
  if(name)c.name=name[1];
  if((++i)%100===0)await yieldUI();
 }
 for(const c of companies.values())c.role=known(c.id,c.name);
 return{companies,files}
}
async function loadCargo(zip){
 const files=new Map(),cargos=new Map(),manifests=[],trailer=new Map();
 for(const [raw,obj] of entries(zip)){
  const p=cargoPath(raw);if(!p)continue;
  if(files.has(p.toLowerCase()))throw Error("Caminho duplicado na DEF de cargas: "+p);
  files.set(p.toLowerCase(),{p,obj})
 }
 if(!files.size)throw Error("A DEF do Librelato não contém cargo/ nem vehicle/.");
 let i=0;
 for(const f of files.values()){
  if(!/\.(sii|sui)$/i.test(f.p))continue;
  if((f.obj._data?.uncompressedSize||0)>500000)continue;
  const txt=await f.obj.async("text"),p=f.p;
  if(/^def\/cargo\.[a-z0-9_-]+\.sii$/i.test(p))manifests.push(p);
  const id=(txt.match(/\bcargo_data\s*:\s*cargo\.([a-z0-9_]+)/i)||[])[1];
  if(id){
   let label=(txt.match(/^\s*name\s*:\s*"([^"]+)"/mi)||[])[1]||"";
   if(!label||label.includes("@@")){const n=id.match(/^carga(\d+)$/i);label=n?names[Number(n[1])-1]||id:id}
   const bs=[...txt.matchAll(/^\s*body_types\s*(?:\[\s*\d*\s*\])?\s*:\s*["']?([a-z0-9_]+)/gim)].map(x=>x[1].toLowerCase());
   cargos.set(id.toLowerCase(),{id:id.toLowerCase(),unit:"cargo."+id.toLowerCase(),name:label,body:[...new Set(bs)],path:p});
  }
  const ca=p.match(/^def\/cargo\/([a-z0-9_]+)\//i);
  if(ca&&/\btrailer_def\s*:/i.test(txt)){
   const bs=[...txt.matchAll(/^\s*body_type\s*:\s*["']?([a-z0-9_]+)/gim)].map(x=>x[1].toLowerCase());
   if(!trailer.has(ca[1]))trailer.set(ca[1],new Set());
   for(const b of bs)trailer.get(ca[1]).add(b)
  }
  if((++i)%100===0)await yieldUI();
 }
 for(const c of cargos.values())c.trailer=trailer.get(c.id)||new Set();
 return{files,cargos,manifests}
}
function simulate(map,cargo){
 const byRole=new Map(),plan=new Map(),skipped=[];
 for(const c of map.companies.values()){if(!byRole.has(c.role))byRole.set(c.role,[]);byRole.get(c.role).push(c)}
 const grouped={alta:0,baixa:0,outros:0};
 for(const info of cargo.cargos.values()){
  const type=kind(info.name),spec=flows[type],problems=[];
  if(!spec)problems.push("identificação de carga incerta");
  if(!info.body.length)problems.push("sem body_types");
  const allowed=info.body.filter(b=>!info.trailer.size||info.trailer.has(b));
  if(!allowed.length)problems.push("carroceria incompatível");
  const out=spec?spec.out.flatMap(r=>byRole.get(r)||[]):[];
  const inn=spec?spec.in.flatMap(r=>byRole.get(r)||[]):[];
  if(!out.length)problems.push("sem produtor reconhecido");
  if(!inn.length)problems.push("sem destinatário reconhecido");
  if(out.some(a=>inn.some(b=>a.id===b.id)))problems.push("empresa consta em origem e destino");
  if(problems.length){skipped.push({id:info.id,name:info.name,problems});continue}
  for(const c of out){if(!plan.has(c.id))plan.set(c.id,{in:new Set(),out:new Set()});plan.get(c.id).out.add(info.id)}
  for(const c of inn){if(!plan.has(c.id))plan.set(c.id,{in:new Set(),out:new Set()});plan.get(c.id).in.add(info.id)}
  for(const b of allowed)if(b==="alta"||b==="baixa")grouped[b]++;else grouped.outros++;
 }
 return{plan,skipped,grouped}
}
const cargoSii=id=>"SiiNunit\n{\n cargo_def : ."+id+" {\n  cargo: \"cargo."+id+"\"\n }\n}\n";
const emptySii=name=>"SiiNunit\n{\n cargo_def : ."+(name.match(/^[a-z0-9_]{1,60}$/i)?name:"v11empty")+" {\n  cargo: \"\"\n }\n}\n";
async function build(map,cargo,sim){
 const out=new JSZip(),keys=new Set(),generate=new Map();
 function put(p,v){const key=p.toLowerCase();if(keys.has(key))throw Error("Colisão de caminho "+p);keys.add(key);out.file(p,v,{createFolders:true})}
 for(const [co,ps] of sim.plan)for(const dir of ["in","out"])for(const id of ps[dir])generate.set("def/company/"+co+"/"+dir+"/"+id+".sii",cargoSii(id));
 for(const x of map.files.values()){
  const m=companyMeta(x.p),gen=generate.has(x.p);
  if(m&&(m.type==="in"||m.type==="out")){if(!gen)put(x.p,emptySii(m.name.replace(/\.sii$/i,"")))}
  else put(x.p,x.obj)
 }
 for(const [p,t] of generate)put(p,t);
 for(const x of cargo.files.values())put(x.p,x.obj);
 put("description.txt","Company Logistics Universal. Requer o reboque Librelato. Nao habilitar as DEF Companies 1 e 2.\n");
 const blob=await out.generateAsync({type:"blob",compression:"DEFLATE",compressionOptions:{level:4},streamFiles:true},m=>say("Compactando… "+Math.round(m.percent)+"%",60+Math.round(m.percent*.3)));
 const check=await JSZip.loadAsync(blob,{createFolders:false});
 for(const p of generate.keys())if(!check.file(p))throw Error("Falha ao validar "+p);
 return{blob,count:generate.size}
}
function audit(map,cargo,sim){
 const companies=[...map.companies.values()],assigned=[...sim.plan.values()].reduce((n,p)=>n+p.in.size+p.out.size,0);
 const warning=[];
 if(sim.grouped.baixa===0)warning.push("Grade baixa sem cargas correspondentes.");
 if(sim.grouped.alta===0)warning.push("Grade alta sem cargas correspondentes.");
 const unknown=companies.filter(c=>c.role==="desconhecida").length;
 if(unknown)warning.push(unknown+" empresas não identificadas permanecerão sem cargas.");
 if(!cargo.manifests.length)warning.push("DEF sem arquivo de registro cargo.*.sii identificado.");
 ui.report.innerHTML="<div class='metrics'>"+
 [["Empresas",companies.length],["Cargas do Librelato",cargo.cargos.size],["Cargas rejeitadas",sim.skipped.length],["Grade baixa",sim.grouped.baixa],["Grade alta",sim.grouped.alta],["Relações IN/OUT",assigned]]
 .map(([t,v])=>"<div class='metric'><span>"+escapeHTML(t)+"</span><strong>"+v+"</strong></div>").join("")+"</div>"+
 (warning.length?"<p class='warning'>"+warning.map(escapeHTML).join("<br>")+"</p>":"");
 ui.detail.innerHTML="<details><summary>Diagnóstico detalhado</summary>"+
 sim.skipped.map(x=>"<div class='audit'><b>"+escapeHTML(x.id+" — "+x.name)+"</b> <span>"+escapeHTML(x.problems.join(", "))+"</span></div>").join("")+
 "</details>"
}
let busy=false;
async function generate(){
 if(busy)return;
 const one=ui.map.files?.[0],two=ui.cargo.files?.[0];
 if(!one||!two){say("Anexe a Company do mapa e a DEF das cargas do Librelato.",0);return}
 busy=true;ui.run.disabled=true;ui.report.innerHTML="";ui.detail.innerHTML="";
 try{
  say("Identificando empresas do mapa…",8);
  const map=await loadMap(await zipRead(one));await yieldUI();
  say("Identificando cargas e carrocerias…",28);
  const cargo=await loadCargo(await zipRead(two));if(!cargo.cargos.size)throw Error("A DEF do Librelato não contém unidades cargo_data reconhecidas.");
  say("Simulando logística…",43);const sim=simulate(map,cargo);audit(map,cargo,sim);
  if(!sim.plan.size)throw Error("Sem cadeias de carga verificadas. Confira o diagnóstico. Não vou gerar SCS vazio.");
  if(!sim.grouped.alta||!sim.grouped.baixa)throw Error("Uma das grades ficou sem cargas. Confira a auditoria antes de gerar.");
  say("Criando DEF Company completa…",60);
  const out=await build(map,cargo,sim);
  const clean=(one.name.replace(/\.(scs|zip)$/i,"").replace(/[^a-z0-9_-]/gi,"_").slice(0,55)||"Mapa");
  const a=document.createElement("a"),url=URL.createObjectURL(out.blob);
  a.href=url;a.download="DEF_Company_Librelato_"+clean+"_Universal.scs";document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),55000);
  say("Concluído! "+out.count+" definições novas geradas para o mapa e ambas as grades.",100);
 }catch(e){say("Erro: "+(e?.message||String(e)),0)}
 finally{busy=false;ui.run.disabled=false}
}
ui.run.addEventListener("click",generate);
for(const id of ["mapFile","cargoFile"])el(id).addEventListener("change",()=>{const input=el(id),label=el(id+"Name");label.textContent=input.files?.[0]?.name||"Selecione um arquivo ZIP/SCS";say("Arquivo selecionado.",0)});
window.CompanyLogisticsTest={kind,known,companyPath,cargoPath,companyMeta,flows,loadMap,loadCargo,simulate,build};
})();
