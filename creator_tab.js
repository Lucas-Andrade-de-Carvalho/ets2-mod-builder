
(function(){
"use strict";
const el=id=>document.getElementById(id),ui={map:el("companyCreateMapFile"),cargo:el("companyCreateCargoFile"),run:el("companyCreateGenerate"),message:el("companyCreateStatus"),bar:el("companyCreateBar"),report:el("companyCreateReport"),detail:el("companyCreateDetail")};
const names=["milho","soja","adubo","madeira","pluma de algodão","cimento","sacos de batata","sacos de laranja","bobinas 2","cimento em palete","cimento em cinta","cerveja","tijolos","pedra de granito","pedra de granito","palete alto","ração mineral","xerém ração","sacaria de ração","sacaria de ração","soja alta","milho alto","sorgo para ração"];
const patterns=[
["sorgo",/\bsorgo\b/],["racao",/\b(racao|xerem|alimento para gado|feed animal)\b/],["milho",/\bmilho\b/],["soja",/\bsoja\b/],
["adubo",/\b(adubos?|fertilizantes?)\b/],["algodao",/\b(pluma|algodao)\b/],["batata",/\bbatatas?\b/],["laranja",/\blaranjas?\b/],
["cerveja",/\b(cervejas?|beer)\b/],["cimento",/\bcimento\b/],["tijolo",/\btijolo[s]?\b/],["granito",/\b(granito|granitto)\b/],
["madeira",/\b(madeira|madeirame)\b/],["aco",/\b(bobina de aco|bobina de chapa|steel coil)\b/],["bobinas_industriais",/\bbobinas?\b/],["palete_vazio",/\b(paletes? vazios?|pallets? vazios?|paletes? de madeira|pallets? de madeira)\b/],
["paletizado",/\b(paletes?|pallets?)\b/]
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
["mineracao",/(mineracao|mineradora|minera de pedra|extracao mineral|mining company)/],
["obras",/(construtora|obra civil|canteiro|construcao|empreiteira)/],
["materiais",/(material de construcao|materiais de construcao|deposito de materiais|deposito de material|loja de materiais|casa de materiais|building supplies)/],
["logistica",/(centro logistico|centro de distribuicao|distribuidora geral|transportadora|armazem geral|warehouse|logistics hub)/],
["cervejaria",/(ambev|heineken|cervejaria|brewery)/],
["bebidas",/(distribuidora de bebidas|deposito de bebidas)/],
["supermercado",/(supermercado|hipermercado|supermarket|mercearia)/],
["hortifruti",/(ceasa|hortifruti|entreposto de frutas)/],
["alimentos",/(distribuidora de alimentos|atacado de alimentos)/],
["siderurgica",/(siderurgica|siderurgia|gerdau|usiminas|csn)/],
["metalurgica",/(metalurgica|industria mecanica|fabrica de maquinas|centro de servicos do aco|comercio de aco)/],
["paletes",/(fabrica de paletes|fabricante de pallets)/],
["agroinsumos",/(loja agropecuaria|insumos agricolas|distribuidora de adubo|casa do agricultor|agrotec)/],
["posto",/(posto|refinaria|petrobras|fuel station)/],
["concessionaria",/(concessionaria|dealership|revenda de carros)/],
["correios",/(correios|correio|sedex)/]
];
const flows={
 // O ETS2 usa OUT (expedição) e IN (recebimento), não apenas fábricas e consumidores.
 // Um distribuidor/depósito pode ter IN e OUT da mesma mercadoria.
 milho:{out:["fazenda"],in:["silo","moinho","racoes","pecuaria"]},
 soja:{out:["fazenda"],in:["silo","moinho"]},
 sorgo:{out:["fazenda"],in:["silo","racoes","pecuaria"]},
 adubo:{out:["adubeira","agroinsumos","materiais","logistica"],in:["fazenda","pecuaria","agroinsumos","materiais","logistica"]},
 madeira:{out:["serraria","floresta","materiais","logistica"],in:["obras","materiais","logistica","metalurgica"]},
 algodao:{out:["fazenda","algodoeira","logistica"],in:["textil","algodoeira","logistica"]},
 cimento:{out:["cimenteira","materiais","logistica"],in:["obras","materiais","logistica"]},
 batata:{out:["fazenda","hortifruti","alimentos","logistica"],in:["hortifruti","alimentos","supermercado","logistica"]},
 laranja:{out:["fazenda","hortifruti","alimentos","logistica"],in:["hortifruti","alimentos","supermercado","logistica"]},
 cerveja:{out:["cervejaria","bebidas","alimentos","logistica"],in:["bebidas","supermercado","alimentos","logistica"]},
 tijolo:{out:["ceramica","materiais","logistica"],in:["obras","materiais","logistica"]},
 granito:{out:["pedreira","mineracao","materiais","logistica"],in:["obras","materiais","logistica"]},
 racao:{out:["racoes","logistica","alimentos"],in:["fazenda","pecuaria","logistica","alimentos"]},
 aco:{out:["siderurgica","metalurgica","materiais","logistica"],in:["metalurgica","obras","materiais","logistica"]},
 bobinas_industriais:{out:["siderurgica","metalurgica","logistica"],in:["metalurgica","obras","logistica"]},
 // Paletes vazios: fabricantes e operadores logísticos expedem, várias empresas recebem.
 palete_vazio:{out:["paletes","logistica","materiais"],in:["fazenda","racoes","moinho","serraria","textil","ceramica","materiais","cervejaria","bebidas","hortifruti","alimentos","supermercado","logistica"]},
 // Pallets Alto/mercadoria paletizada sem conteúdo detalhado: uso amplo, mas não irrestrito.
 paletizado:{out:["fazenda","pecuaria","racoes","moinho","adubeira","agroinsumos","serraria","textil","algodoeira","ceramica","cimenteira","materiais","cervejaria","bebidas","hortifruti","alimentos","siderurgica","metalurgica","paletes","logistica"],in:["fazenda","pecuaria","racoes","moinho","serraria","textil","algodoeira","ceramica","materiais","obras","cervejaria","bebidas","hortifruti","alimentos","supermercado","siderurgica","metalurgica","logistica"]}
};
const norm=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[_-]/g," ");
const pathNorm=s=>String(s).replace(/\\/g,"/").replace(/^\/+/,"").replace(/^\.\/+/,"");
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const yieldUI=()=>new Promise(r=>setTimeout(r,0));
const say=(msg,pct)=>{ui.message.textContent=msg;ui.bar.style.width=Math.max(0,Math.min(100,pct))+"%"};
const known=(id,label)=>{
 const x=norm(id)+" "+norm(label);
 for(const [r,re] of sectors)if(re.test(x))return r;
 const flat=norm(id).replace(/ /g,"");
 // Regras de abreviações atestáveis, sem tornar empresas genéricas em produtoras.
 const prefixes=[
 ["silo",/^(silos?|coop(?:erativa)?|cerealista|graos)/],
 ["racoes",/^(racoes?|feedmill|nutricaoanimal)/],
 ["adubeira",/^(fertilizantes?|adubeira)/],
 ["fazenda",/^(faz(?:enda|[_0-9])|farm|finca|hacienda|agropec|agricol|agricult|rural|plantacao|plantation|cultivo|rancho)/],
 ["pecuaria",/^(arnasuino|pecuaria|granja|ganaderia|gado)/],
 ["floresta",/^(florestal|reflorestamento)/],
 ["serraria",/^(araserr|serraria|serradero|sawmill)/],
 ["moinho",/^(moinho|molino)/],
 ["hortifruti",/^(ceasa|hortifruti)/],
 ["ceramica",/^(olaria|ceramica|tijolaria)/],
 ["cimenteira",/^(cimenteira|fabrica.?cimento)/],
 ["obras",/^(abconstru|construtora|construcao|construc|construction|obra|canteiro)/],
 ["pedreira",/^(pedreira|quarry|cantera|marmoraria)/],
 ["cervejaria",/^(ambev|heineken|cervejaria)/],
 ["supermercado",/^(supermercado|hipermercado|atacadao|assai|carrefour)/],
 ["siderurgica",/^(belgo|gerdau|usiminas|siderurgica)/],
 ["mineracao",/^(mineracao|mineradora|mining)/],
 ["materiais",/^(materiais|materialconstrucao|matconstrucao|matconst|depositomaterial|depomaterial|casamaterial)/],
 ["metalurgica",/^(acero(?:[0-9]+)?$|metalurgica|acos?comercial)/],
 ["agroinsumos",/^(agrotec|agroinsumos|insumosagricolas)/],
 ["logistica",/^(arralog|transportadora|centrologistico|centrodistribuicao|armazemgeral|logistica)/],
 ["posto",/^(posto|refinaria|petrobras|ipiranga)/],
 ["concessionaria",/^(concessionaria|dealer)/],
 ["correios",/^(correios|sedex)/],
 ];
 for(const [r,re] of prefixes)if(re.test(flat))return r;
 return"desconhecida";
};
const ALLOWED_ROLES=new Set(["agroinsumos","mineracao","logistica","fazenda","silo","pecuaria","racoes","moinho","adubeira","serraria","floresta","textil","algodoeira","ceramica","cimenteira","pedreira","obras","materiais","cervejaria","bebidas","supermercado","hortifruti","alimentos","siderurgica","metalurgica","paletes","posto","concessionaria","correios"]);
function applyCompanyOverrides(map){
 const field=el("companyCreateOverrides"),raw=field?.value?.trim()||"";
 const accepted=[],errors=[];
 if(!raw)return{accepted};
 for(const [i,row]of raw.split(/\r?\n/).entries()){
  const line=row.trim();if(!line||line.startsWith("#"))continue;
  const m=line.match(/^([a-z0-9_-]+)\s*[=:]\s*([a-z_]+)$/i);
  if(!m){errors.push("Linha "+(i+1)+": formato esperado ID = setor");continue}
  const id=m[1].toLowerCase(),role=m[2].toLowerCase();
  if(!ALLOWED_ROLES.has(role)){errors.push("Setor inválido: "+role);continue}
  const c=map.companies.get(id);
  if(!c){errors.push("Empresa não encontrada no mapa: "+id);continue}
  c.role=role;c.evidence="classificação informada pelo usuário";
  accepted.push(id+" = "+role)
 }
 if(errors.length)throw Error("Corrija o campo de classificação: "+errors.slice(0,5).join("; "));
 return{accepted}
}
const kind=name=>{
 const x=norm(name)
   .replace(/\b(soja|milho|sorgo)alto\b/g,"$1 alto")
   .replace(/\b(soja|milho|sorgo)alta\b/g,"$1 alta")
   .replace(/\b(batata|laranja|cerveja)s\b/g,"$1");
 for(const [k,re] of patterns)if(re.test(x))return k;
 return null;
};
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

function inferRoleFromHistoricalFreights(company){
 // O histórico serve somente para identificar setor; nunca é copiado como logística.
 const cargoSet=new Set(company.old.map(x=>x.stem.toLowerCase()));
 if(!cargoSet.size||cargoSet.size>10||company.old.length>14)return null;
 const has=(dir,re)=>company.old.some(x=>x.dir===dir&&re.test(x.stem.replace(/[_-]/g," ")));
 const out=re=>has("out",re),inn=re=>has("in",re);
 const grain=/(wheat|trigo|maize|corn|milho|soybean|soja|barley|cevada|sunflower|girassol|rapeseed|canola|sorghum|sorgo|rice|arroz|grain|graos)/i;
 const crop=/(potat|batata|beet|beterraba|cotton|algodao|orange|laranja|vegetable|hortalica|fruit|fruta|cereals?|sementes?|seeds?)/i;
 const fert=/(fertiliz|adubo|seed|sement|pesticid|defensivo)/i;
 const reGrain=company.old.filter(x=>x.dir==="out"&&grain.test(x.stem)).map(x=>x.stem.toLowerCase());
 const inGrain=new Set(company.old.filter(x=>x.dir==="in"&&grain.test(x.stem)).map(x=>x.stem.toLowerCase()));
 const sharedGrain=reGrain.some(x=>inGrain.has(x));
 const evidence=[
 ["silo",sharedGrain],
 ["fazenda",out(grain)&&!inn(grain)&&(inn(fert)||out(crop)||reGrain.length>=2)],
 ["fazenda",out(crop)&&!inn(crop)&&inn(fert)],
 ["pecuaria",out(/(cattle|gado|sheep|ovelha|wool|la|animals?|livestock|milk|leite)/i)&&inn(/(feed|racao|hay|feno)/i)],
 ["racoes",out(/(animal.?feed|racao|feedmeal|farelo|xerem)/i)&&inn(grain)],
 ["moinho",out(/(flour|farinha|bran|farelo|meal)/i)&&inn(grain)],
 ["adubeira",out(/(fertiliz|adubo|ammoni|ureia)/i)&&inn(/(chemical|quimic|phosphate|fosfato)/i)],
 ["serraria",out(/(lumber|planks?|boards?|madeira.?serrada|timber)/i)&&inn(/(logs?|toras?|wood)/i)],
 ["ceramica",out(/(bricks?|tijolos?|tiles?|telhas?|ceramic)/i)&&inn(/(clay|argila)/i)],
 ["cimenteira",out(/(cement|cimento)/i)&&inn(/(limestone|calcario|clay|argila)/i)],
 ["cervejaria",out(/(beer|cervejas?)/i)&&inn(/(barley|cevada|hops|lupulo|malt|malte)/i)],
 ["siderurgica",out(/(steel|aco|coils?|bobinas?)/i)&&inn(/(iron|ferro|ore|minerio|coal|carvao)/i)]
 ];
 for(const [role,ok] of evidence)if(ok)return{role,method:"combinação IN/OUT anterior"};
 return null;
}
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
 for(const c of companies.values()){
  c.role=known(c.id,c.name);
  c.evidence=c.role==="desconhecida"?"nenhuma":"identificador/nome";
  if(c.role==="desconhecida"&&typeof rawClassification==="function"&&typeof finalizeClassification==="function"){
   const raw=rawClassification({id:c.id,localMeta:c.name||"",globalMeta:"",externalDef:""});
   const rank=finalizeClassification({id:c.id},raw);
   const supported={agro:"fazenda",coop:"silo"};
   if(rank.score>=90&&rank.gap>=25&&supported[rank.category]){
    c.role=supported[rank.category];
    c.evidence="categoria específica por ID da base original";
   }
  }
  if(c.role==="desconhecida"){
   const guess=inferRoleFromHistoricalFreights(c);
   if(guess){c.role=guess.role;c.evidence=guess.method+" (catálogo enxuto)";}
  }
 }

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
  if(id&&/^carga\d+$/i.test(id)){
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

const LEGACY_EVIDENCE={
 cimento:/^(?:vg_)?(?:cement|cimento|cement_b|cement_pallet|cement_bag)$/i,
 tijolo:/^(?:vg_)?(?:bricks?|tijolos?|tijolaria|ceramic_bricks?)$/i,
 granito:/^(?:vg_)?(?:granite|granito|marble|marmore|marble_blocks?)$/i,
 adubo:/^(?:vg_)?(?:fertilizers?|fertilizantes?|adubo|ureia|fertilizer_b)$/i,
 madeira:/^(?:vg_)?(?:lumber|wood|timber|planks?|boards?|logs?|toras?|madeira)$/i,
 algodao:/^(?:vg_)?(?:cotton|cotton_bales?|algodao|pluma|cottonlint)$/i,
 bobinas_industriais:/^(?:vg_)?(?:steel_coils?|steelcoil|metal_coils?|bobinas?|chapa_aco|rolled_steel)$/i
};
function legacyEvidence(c,type,dir){
 // Um catálogo antigo com dezenas de cargos atribuídos a tudo não é prova de atividade.
 if(!c||!Array.isArray(c.old)||!c.old.length||c.old.length>14)return false;
 if(new Set(c.old.map(x=>x.stem)).size>10)return false;
 const re=LEGACY_EVIDENCE[type];
 return !!re&&c.old.some(x=>x.dir===dir&&re.test(x.stem));
}
const BUILDING_REDEPLOY=new Set(["cimento","tijolo","madeira","granito"]);
function getCandidateMap(map){
 const companies=[...map.companies.values()],byRole=new Map();
 for(const c of companies){if(!byRole.has(c.role))byRole.set(c.role,[]);byRole.get(c.role).push(c)}
 return{companies,byRole};
}
function chooseEndpoints(map,type,spec){
 const {companies,byRole}=getCandidateMap(map);
 const out=new Set(spec.out.flatMap(r=>byRole.get(r)||[]));
 const inn=new Set(spec.in.flatMap(r=>byRole.get(r)||[]));
 const notes=[];
 // Trabalhar com as permissões antigas como evidência pontual, não como regra a preservar.
 let historyOut=0,historyIn=0;
 for(const c of companies){
  if(legacyEvidence(c,type,"out")){if(!out.has(c)){out.add(c);historyOut++}}
  if(legacyEvidence(c,type,"in")){if(!inn.has(c)){inn.add(c);historyIn++}}
 }
 if(historyOut||historyIn)notes.push("histórico limitado: "+historyOut+" expedidores e "+historyIn+" recebedores adicionais");
 // Canteiros e construtoras podem redistribuir estoque para outras obras,
 // mas apenas quando não há expedidor melhor. Nunca tornam posto ou concessionária fonte.
 if(!out.size&&BUILDING_REDEPLOY.has(type)){
  const works=(byRole.get("obras")||[]).filter(c=>c.id&&c.evidence!=="nenhuma");
  if(works.length>=2){out.add(works[0]);notes.push("remanejamento eventual de estoque entre construtoras/obras; hipótese logística")}
 }
 // Cooperativas agrícolas costumam fornecer insumos, mas não basta ser silo de grãos.
 if(!out.size&&type==="adubo"){
  const coop=(byRole.get("silo")||[]).filter(c=>/coop|cooperativ|agro/.test(norm(c.id+" "+c.name)));
  for(const c of coop.slice(0,3))out.add(c);
  if(coop.length)notes.push("fornecimento de insumos por cooperativa; hipótese de estoque");
 }
 return{out:[...out],inn:[...inn],notes}
}

function simulate(map,cargo){
 const plan=new Map(),skipped=[],proof=[],assumptions=[];
 const grouped={alta:0,baixa:0,outros:0};
 for(const info of cargo.cargos.values()){
  const type=kind(info.name),spec=flows[type],problems=[];
  if(!spec)problems.push("identificação econômica da carga incerta");
  if(!info.body.length)problems.push("sem body_types");
  const allowed=info.body.filter(b=>!info.trailer.size||info.trailer.has(b));
  if(!allowed.length)problems.push("carroceria incompatível");
  const chosen=spec?chooseEndpoints(map,type,spec):{out:[],inn:[],notes:[]};
  let outs=chosen.out,ins=chosen.inn;
  if(!outs.length&&spec)problems.push("sem expedidor compatível ou estoque comprovado (setores: "+spec.out.join(" / ")+")");
  if(!ins.length&&spec)problems.push("sem recebedor compatível ou estoque comprovado (setores: "+spec.in.join(" / ")+")");
  if(outs.length===1&&ins.length===1&&outs[0].id===ins[0].id)
   problems.push("única origem e destino são a mesma empresa; nenhuma viagem identificável");
  if(problems.length){skipped.push({id:info.id,name:info.name,problems});continue}
  if(type==="bobinas_industriais")chosen.notes.push("Bobinas 2 tratadas provisoriamente como bobinas industriais; conteúdo 3D não confirmado");
  if(type==="paletizado")chosen.notes.push("paletes de conteúdo não identificado: distribuição industrial/comercial plausível");
  if(chosen.notes.length)assumptions.push({id:info.id,notes:chosen.notes});
  for(const c of outs){
    if(!plan.has(c.id))plan.set(c.id,{in:new Set(),out:new Set()});
    plan.get(c.id).out.add(info.id);
  }
  for(const c of ins){
    if(!plan.has(c.id))plan.set(c.id,{in:new Set(),out:new Set()});
    plan.get(c.id).in.add(info.id);
  }
  for(const b of allowed)if(b==="alta"||b==="baixa")grouped[b]++;else grouped.outros++;
  proof.push({id:info.id,name:info.name,type,origins:outs.length,destinations:ins.length,sourceIds:outs.map(c=>c.id),destIds:ins.map(c=>c.id),notes:chosen.notes});
 }
 return{plan,skipped,grouped,proof,assumptions}
}

const cargoSii=id=>"SiiNunit\n{\n cargo_def : ."+id+" {\n  cargo: \"cargo."+id+"\"\n }\n}\n";
const emptySii=name=>"SiiNunit\n{\n cargo_def : ."+(name.match(/^[a-z0-9_]{1,60}$/i)?name:"v11empty")+" {\n  cargo: \"\"\n }\n}\n";
async function build(map,cargo,sim){
 const out=new JSZip(),keys=new Set(),generated=new Map(),removed=[];
 async function put(p,v){
  const key=p.toLowerCase();if(keys.has(key))throw Error("Duas definições com mesmo caminho: "+p);
  const bytes=v&&typeof v.async==="function"?await v.async("uint8array"):v;
  keys.add(key);out.file(p,bytes,{createFolders:true});
 }
 for(const [co,ps] of sim.plan){
  for(const dir of ["in","out"])for(const id of ps[dir]){
   const p="def/company/"+co+"/"+dir+"/"+id+".sii";
   generated.set(p.toLowerCase(),cargoSii(id));
  }
 }
 let count=0;
 for(const x of map.files.values()){
  const m=companyMeta(x.p);
  if(m&&(m.type==="in"||m.type==="out")){removed.push(x.p);continue}
  if(m?.type==="permanent"&&((x.obj._data?.uncompressedSize||0)<300000)){
   const txt=await x.obj.async("text");
   if(/^\s*(?:in_cargo|out_cargo)(?:\[\s*\d*\s*\])?\s*:/mi.test(txt))
     throw Error("Lista de cargas dentro do arquivo da empresa "+x.p+" exige conversão específica; geração bloqueada.");
  }
  await put(x.p,x.obj);
  if((++count)%150===0){say("Preservando arquivos do mapa… "+count,54);await yieldUI()}
 }
 for(const [p,t]of generated)await put(p,t);
 await put("description.txt","DEF Company personalizada por mapa. Requer mod principal do Librelato ativo. Nao usar DEF Companies genericas 1/2.\n");
 const blob=await out.generateAsync({type:"blob",compression:"DEFLATE",compressionOptions:{level:4},streamFiles:true},info=>say("Compactando Company… "+Math.round(info.percent)+"%",62+Math.round(info.percent*.28)));
 const check=await JSZip.loadAsync(blob,{createFolders:false});
 for(const p of generated.keys()){
  const obj=check.file(p);
  if(!obj)throw Error("Faltou carga gerada: "+p);
  if(!/cargo\s*:\s*"cargo\./i.test(await obj.async("text")))throw Error("Cargo não registrado corretamente em "+p);
 }
 for(const p of removed)if(check.file(p)&&!generated.has(p.toLowerCase()))throw Error("Cargo original permaneceu no arquivo: "+p);
 for(const x of map.files.values())if(companyMeta(x.p)?.type==="editor"&&!check.file(x.p))throw Error("Arquivo editor perdido: "+x.p);
 return{blob,count:generated.size,removed:removed.length}
}
function audit(map,cargo,sim){
 const companies=[...map.companies.values()],assigned=[...sim.plan.values()].reduce((n,p)=>n+p.in.size+p.out.size,0);
 const warning=[];
 if(sim.grouped.baixa===0)warning.push("Grade baixa sem cargas correspondentes.");
 if(sim.grouped.alta===0)warning.push("Grade alta sem cargas correspondentes.");
 const unknown=companies.filter(c=>c.role==="desconhecida").length;
 const producerSectors=new Set(["fazenda","adubeira","racoes","serraria","floresta","algodoeira","cimenteira","ceramica","pedreira","mineracao","cervejaria","siderurgica","paletes","materiais","logistica"]);
 const producers=companies.filter(c=>producerSectors.has(c.role));
 const exampleUnknown=companies.filter(c=>c.role==="desconhecida").slice(0,24).map(c=>c.id);
 const inferred=companies.filter(c=>c.evidence==="combinação IN/OUT anterior").length;
 if(unknown)warning.push(unknown+" empresas sem atividade identificada.");
 if(inferred)warning.push(inferred+" empresas classificadas por produtos históricos IN/OUT, além dos nomes e IDs.");
 const manual=companies.filter(c=>c.evidence==="classificação informada pelo usuário").length;
 if(manual)warning.push(manual+" empresas classificadas manualmente.");
 if(!producers.length)warning.push("Nenhum ponto de expedição foi identificado neste mapa. Confira o diagnóstico.");
 if(!cargo.manifests.length)warning.push("DEF sem arquivo de registro cargo.*.sii identificado.");
 const reasons=new Map();
 for(const item of sim.skipped)for(const reason of item.problems)reasons.set(reason,(reasons.get(reason)||0)+1);
 const ranked=[...reasons].sort((a,b)=>b[1]-a[1]);
 const roles=new Map();
 for(const item of companies)roles.set(item.role,(roles.get(item.role)||0)+1);
 ui.report.innerHTML="<div class='metrics'>"+
 [["Empresas",companies.length],["Cargas do Librelato",cargo.cargos.size],["Cargas rejeitadas",sim.skipped.length],["Hipóteses auditadas",sim.assumptions.length],["Grade baixa",sim.grouped.baixa],["Grade alta",sim.grouped.alta],["Relações IN/OUT",assigned]]
 .map(([t,v])=>"<div class='metric'><span>"+escapeHTML(t)+"</span><strong>"+v+"</strong></div>").join("")+"</div>"+
 (warning.length?"<p class='warning'>"+warning.map(escapeHTML).join("<br>")+"</p>":"")+
 (ranked.length?"<div class='warning'><b>Por que as cargas foram rejeitadas?</b><div style='margin-top:9px'>"+ranked.map(([reason,count])=>"<div style='padding:3px 0'><strong>"+count+"x</strong> "+escapeHTML(reason)+"</div>").join("")+"</div></div>":"")+
 "<p class='muted'>Empresas reconhecidas por atividade: "+
 [...roles].filter(([k])=>k!=="desconhecida").sort((a,b)=>b[1]-a[1]).map(([role,n])=>escapeHTML(role)+": "+n).join(" · ")+
 ". Empresas ainda sem classificação (amostra): "+escapeHTML(exampleUnknown.join(", "))+ ". Não reconhecer a atividade de uma empresa não significa que ela não tenha cargas no mundo real.</p>";
 ui.detail.innerHTML="<details"+(sim.skipped.length===cargo.cargos.size?" open":"")+"><summary>Diagnóstico detalhado de cada carga</summary>"+
 "<p class='muted'>Cargas distribuídas (expedidores → recebedores): "+sim.proof.map(p=>escapeHTML(p.name)+": "+p.origins+" → "+p.destinations).join("; ")+"</p>"+
 "<p class='muted'>Exemplos de relações do mapa (não garante oferta no ETS2):</p>"+
 sim.proof.map(p=>"<div class='audit'><b>"+escapeHTML(p.name)+"</b><span>OUT: "+escapeHTML(p.sourceIds.slice(0,6).join(", "))+" | IN: "+escapeHTML(p.destIds.slice(0,6).join(", "))+"</span></div>").join("")+
 (sim.assumptions.length?"<p class='warning'><b>Hipóteses usadas, sujeitas à confirmação:</b><br>"+sim.assumptions.map(p=>escapeHTML(p.id+": "+p.notes.join("; "))).join("<br>")+"</p>":"")+
 sim.skipped.map(x=>"<div class='audit'><b>"+escapeHTML(x.id+" — "+x.name)+"</b> <span>"+escapeHTML(x.problems.join(", "))+"</span></div>").join("")+
 "</details>";
}

let latestDiagnostic=null;
function createDiagnosticText(map,cargo,sim){
 const rows=[
  "ETS2 COMPANY LOGISTICS - DIAGNÓSTICO DE ARQUIVOS",
  "Empresas: "+map.companies.size,
  "Cargas personalizadas do Librelato: "+cargo.cargos.size,
  "Definições de carroceria: "+[...cargo.cargos.values()].map(c=>c.id+" = "+(c.body.join("|")||"SEM BODY_TYPES")).join(", "),
  "",
  "EMPRESAS (ID | SETOR IDENTIFICADO | EVIDÊNCIA | CARGAS IN ANTIGAS | CARGAS OUT ANTIGAS)"
 ];
 for(const c of map.companies.values()){
  const ins=c.old.filter(x=>x.dir==="in").map(x=>x.stem);
  const outs=c.old.filter(x=>x.dir==="out").map(x=>x.stem);
  rows.push([c.id,c.role,c.evidence||"nenhuma",ins.join(","),outs.join(",")].join(" | "));
 }
 rows.push("","CARGAS REJEITADAS (ID | NOME | MOTIVOS)");
 for(const x of sim.skipped)rows.push([x.id,x.name,x.problems.join("; ")].join(" | "));
 rows.push("","CARGAS LIBERADAS E RAZÕES (ID | NOME | EXPEDIDORES | RECEBEDORES | HIPÓTESES)");
 for(const p of sim.proof)rows.push([p.id,p.name,p.sourceIds.join(","),p.destIds.join(","),p.notes.join("; ")].join(" | "));
 rows.push("","CARGAS DESTINADAS A EMPRESAS (ID | IN | OUT)");
 for(const [id,p] of sim.plan)rows.push([id,[...p.in].join(","),[...p.out].join(",")].join(" | "));
 return rows.join("\n");
}
function downloadDiagnostic(){
 if(!latestDiagnostic)return;
 const blob=new Blob([latestDiagnostic],{type:"text/plain;charset=utf-8"});
 const u=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=u;a.download="ETS2_Company_Logistics_Diagnostico.txt";
 document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),50000);
}
let busy=false;
async function generate(){
 if(busy)return;
 const one=ui.map.files?.[0],two=ui.cargo.files?.[0];
 if(!one||!two){say("Anexe a Company do mapa e a DEF das cargas do Librelato.",0);return}
 busy=true;ui.run.disabled=true;ui.report.innerHTML="";ui.detail.innerHTML="";latestDiagnostic=null;
 try{
  say("Identificando empresas do mapa…",8);
  const map=await loadMap(await zipRead(one));applyCompanyOverrides(map);await yieldUI();
  say("Identificando cargas e carrocerias…",28);
  const cargo=await loadCargo(await zipRead(two));if(!cargo.cargos.size)throw Error("A DEF do Librelato não contém unidades cargo_data reconhecidas.");
  say("Simulando logística…",43);const sim=simulate(map,cargo);audit(map,cargo,sim);
  latestDiagnostic=createDiagnosticText(map,cargo,sim);const diag=el("companyCreateSaveDiagnostic");if(diag)diag.hidden=false;
  if(!sim.plan.size)throw Error("Sem cadeias de carga verificadas. Confira o diagnóstico. Não vou gerar SCS vazio.");
  if(!sim.grouped.alta||!sim.grouped.baixa)throw Error("Uma das grades ficou sem cargas. Confira a auditoria antes de gerar.");
  say("Criando DEF Company completa…",60);
  const out=await build(map,cargo,sim);
  const clean=(one.name.replace(/\.(scs|zip)$/i,"").replace(/[^a-z0-9_-]/gi,"_").slice(0,55)||"Mapa");
  const a=document.createElement("a"),url=URL.createObjectURL(out.blob);
  a.href=url;a.download="DEF_Company_Librelato_"+clean+"_Universal.scs";document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),55000);
  say("Arquivo gerado: "+out.count+" IN/OUT novos, "+out.removed+" permissões antigas retiradas do ZIP. Teste dentro do ETS2 ainda necessário.",100);
 }catch(e){say("Erro: "+(e?.message||String(e)),0)}
 finally{busy=false;ui.run.disabled=false}
}
ui.run.addEventListener("click",generate);
if(el("companyCreateSaveDiagnostic"))el("companyCreateSaveDiagnostic").addEventListener("click",downloadDiagnostic);
for(const id of ["companyCreateMapFile","companyCreateCargoFile"])el(id).addEventListener("change",()=>{const input=el(id),label=el(id+"Name");label.textContent=input.files?.[0]?.name||"Selecione um arquivo ZIP/SCS";say("Arquivo selecionado.",0)});
window.CompanyCreatorTest={kind,known,inferRoleFromHistoricalFreights,createDiagnosticText,companyPath,cargoPath,companyMeta,flows,loadMap,loadCargo,simulate,build};
})();
