
(function(){
"use strict";
const el=id=>document.getElementById(id),ui={map:el("companyCreateMapFile"),cargo:el("companyCreateCargoFile"),run:el("companyCreateGenerate"),message:el("companyCreateStatus"),bar:el("companyCreateBar"),report:el("companyCreateReport"),detail:el("companyCreateDetail"),download:el("companyCreateDownload"),downloadInfo:el("companyCreateDownloadInfo")};
const names=["milho","soja","adubo","madeira","pluma de algodão","cimento","sacos de batata","sacos de laranja","bobinas 2","cimento em palete","cimento em cinta","cerveja","tijolos","pedra de granito","pedra de granito","palete alto","ração mineral","xerém ração","sacaria de ração","sacaria de ração","soja alta","milho alto","sorgo para ração"];
const patterns=[
["sorgo",/\bsorgo\b/],["racao",/\b(racao|xerem|alimento para gado|feed animal)\b/],["milho",/\bmilho\b/],["soja",/\bsoja\b/],
["adubo",/\b(adubos?|fertilizantes?)\b/],["algodao",/\b(pluma|algodao)\b/],["batata",/\bbatatas?\b/],["laranja",/\blaranjas?\b/],
["cerveja",/\b(cervejas?|beer)\b/],["cimento",/\bcimento\b/],["tijolo",/\btijolo[s]?\b/],["granito",/\b(granito|granitto)\b/],
["madeira",/\b(madeira|madeirame)\b/],["aco",/\b(bobina de aco|bobina de chapa|steel coil)\b/],["bobinas_industriais",/\bbobinas?\b/],["palete_vazio",/\b(paletes? vazios?|pallets? vazios?|paletes? de madeira|pallets? de madeira)\b/],
["paletizado",/\b(paletes?|pallets?)\b/]
];
// Catálogo somente de metadados. Nenhuma empresa/carga é criada a partir desta lista.
const SCS_REFERENCE_URLS={"forum2014":"https://forum.scssoft.com/viewtopic.php?p=195482","forum2020":"https://forum.scssoft.com/viewtopic.php?t=285506","forum2013":"https://forum.scssoft.com/viewtopic.php?t=3897","wiki":"https://trucksimulator.wiki.gg/wiki/Companies/Euro_Truck_Simulator_2"};
const SCS_COMPANY_CATALOG=[{"name":"EuroGoodies","role":"logistica","source":"forum2014"},{"name":"LKWLog GmbH","role":"logistica","source":"forum2014"},{"name":"LKW","role":"logistica","source":"forum2014"},{"name":"Stokes","role":"logistica","source":"forum2014"},{"name":"Tradeaux","role":"logistica","source":"forum2014"},{"name":"TransiNet","role":"logistica","source":"forum2014"},{"name":"Posped","role":"logistica","source":"forum2014","note":"Listas antigas divergem: há menção a logística e a processamento de alimentos. Priorizar IN/OUT do mapa."},{"name":"Trameri","role":"logistica","source":"forum2014"},{"name":"ACI SRL","role":"logistica","source":"forum2020"},{"name":"Cargotras","role":"logistica","source":"forum2020"},{"name":"FLE","role":"logistica","source":"forum2020"},{"name":"Lisette Logistics","role":"logistica","source":"forum2020"},{"name":"Polaris Lines","role":"logistica","source":"forum2020"},{"name":"RT Log","role":"logistica","source":"forum2020"},{"name":"Container Port","role":"logistica","source":"forum2020"},{"name":"Drekkar Trans","role":"logistica","source":"forum2020"},{"name":"GNT","role":"logistica","source":"forum2020"},{"name":"Norrsken","role":"logistica","source":"forum2020"},{"name":"Renar Logistik","role":"logistica","source":"forum2020"},{"name":"Eolo Lines","role":"logistica","source":"forum2020"},{"name":"Gallia Ferries","role":"logistica","source":"forum2020"},{"name":"Globeur","role":"logistica","source":"forum2020"},{"name":"Port de Conteneur","role":"logistica","source":"forum2020"},{"name":"Wilnet Transports","role":"logistica","source":"forum2020"},{"name":"Exomar","role":"logistica","source":"forum2020"},{"name":"TE Logistica","role":"logistica","source":"forum2020"},{"name":"Terminal Container","role":"logistica","source":"forum2020"},{"name":"Transporti Mediterraneo","role":"logistica","source":"forum2020"},{"name":"AeroBaltica","role":"logistica","source":"forum2020"},{"name":"Baltic Logistic Transport","role":"logistica","source":"forum2020"},{"name":"Nordic Cargo Handling","role":"logistica","source":"forum2020"},{"name":"Rosmark","role":"logistica","source":"forum2020"},{"name":"Sininen Aurinko Logistiikka","role":"logistica","source":"forum2020"},{"name":"Balkan Loco","role":"logistica","source":"forum2020"},{"name":"Baltrak Lojistik","role":"logistica","source":"forum2020"},{"name":"Brawen Transport","role":"logistica","source":"forum2020"},{"name":"Fallow Cargo","role":"logistica","source":"forum2020"},{"name":"Log n Stick","role":"logistica","source":"forum2020"},{"name":"Trade Market Istanbul","role":"logistica","source":"forum2020"},{"name":"TTK","role":"logistica","source":"forum2020"},{"name":"Almacenes y Paquetería Pablo","role":"logistica","source":"forum2020"},{"name":"Logística Atlântica","role":"logistica","source":"forum2020"},{"name":"Transportes Caballería","role":"logistica","source":"forum2020"},{"name":"TS Atlas","role":"logistica","source":"forum2020"},{"name":"APP","role":"logistica","source":"wiki"},{"name":"Adrica","role":"logistica","source":"wiki"},{"name":"Associated Nordic Ports","role":"logistica","source":"wiki"},{"name":"EuroAcres","role":"fazenda","source":"forum2014"},{"name":"Agronord","role":"fazenda","source":"forum2020"},{"name":"Dans le Jardin","role":"fazenda","source":"forum2020"},{"name":"Agrominta UAB","role":"fazenda","source":"forum2020"},{"name":"Evikši ZS","role":"fazenda","source":"forum2020"},{"name":"Lateds AS","role":"fazenda","source":"forum2020"},{"name":"Maatila Egres","role":"fazenda","source":"forum2020"},{"name":"Noskonitta","role":"fazenda","source":"forum2020"},{"name":"Agrominta","role":"fazenda","source":"forum2020"},{"name":"Nordic Crown","role":"pecuaria","source":"forum2020"},{"name":"Ateria AS","role":"pecuaria","source":"forum2020"},{"name":"Õnnelik Talu","role":"pecuaria","source":"forum2020"},{"name":"Tesoro Gustoso","role":"alimentos","source":"forum2020"},{"name":"Kolico","role":"alimentos","source":"forum2020"},{"name":"Subse","role":"alimentos","source":"forum2020"},{"name":"FUISpA","role":"alimentos","source":"forum2020"},{"name":"ARIA Food","role":"laticinio","source":"forum2020"},{"name":"Nos Pâturages","role":"laticinio","source":"forum2020"},{"name":"Fattoria Felice","role":"laticinio","source":"forum2020"},{"name":"Polar Fish","role":"pescado","source":"forum2020"},{"name":"Kaarfor","role":"supermercado","source":"forum2014"},{"name":"Cesare Supermercato","role":"supermercado","source":"forum2020"},{"name":"Norrfood","role":"supermercado","source":"forum2020"},{"name":"Suprema","role":"supermercado","source":"forum2020"},{"name":"Suprema RU","role":"supermercado","source":"forum2020"},{"name":"Cesta","role":"supermercado","source":"forum2020"},{"name":"SuperCesta","role":"supermercado","source":"forum2020"},{"name":"SellPlan","role":"varejo","source":"forum2014"},{"name":"Ika Bohag","role":"varejo","source":"forum2020"},{"name":"Renat","role":"varejo","source":"forum2020"},{"name":"BCP","role":"automotiva","source":"forum2014"},{"name":"FCP","role":"automotiva","source":"forum2014"},{"name":"Scout","role":"automotiva","source":"forum2014"},{"name":"BHV","role":"automotiva","source":"forum2020"},{"name":"Libellula","role":"automotiva","source":"forum2020"},{"name":"Spinelli","role":"automotiva","source":"forum2020"},{"name":"Voitureux","role":"automotiva","source":"forum2020"},{"name":"VPC","role":"automotiva","source":"forum2020"},{"name":"Gomme du Monde","role":"automotiva","source":"forum2020"},{"name":"AA - Auto di Alonso","role":"automotiva","source":"forum2020"},{"name":"Cantiere Navale","role":"automotiva","source":"forum2020"},{"name":"Comoto","role":"automotiva","source":"forum2020"},{"name":"PIAC","role":"automotiva","source":"forum2020"},{"name":"Balteus Yachts","role":"automotiva","source":"forum2020"},{"name":"Finnish Tyres","role":"automotiva","source":"forum2020"},{"name":"Ladoga Auto","role":"automotiva","source":"forum2020"},{"name":"Latvijas Vagonu Rūpnīca","role":"automotiva","source":"forum2020"},{"name":"Dulcis","role":"automotiva","source":"forum2020"},{"name":"Ocean Solution Group","role":"automotiva","source":"forum2020"},{"name":"Rump","role":"automotiva","source":"forum2020"},{"name":"Sporklift","role":"automotiva","source":"forum2020"},{"name":"The Train Foundry","role":"automotiva","source":"forum2020"},{"name":"Ortiz","role":"automotiva","source":"forum2020"},{"name":"TDC Auto Terminal","role":"automotiva","source":"forum2020"},{"name":"AI Automotive","role":"automotiva","source":"wiki"},{"name":"SanBuilders","role":"obras","source":"forum2014"},{"name":"Bâtisse","role":"obras","source":"forum2020"},{"name":"Konstnorr","role":"obras","source":"forum2020"},{"name":"Construzione di Edifici","role":"obras","source":"forum2020"},{"name":"Cemeltex","role":"obras","source":"forum2020"},{"name":"Cemeltex RU","role":"obras","source":"forum2020"},{"name":"Construcciones Elcano","role":"obras","source":"forum2020"},{"name":"Domdepo","role":"materiais","source":"forum2020"},{"name":"Domdepo RU","role":"materiais","source":"forum2020"},{"name":"Stein-Bruch","role":"pedreira","source":"forum2014"},{"name":"MS Stein","role":"pedreira","source":"forum2020"},{"name":"Nordic Stenbrott","role":"pedreira","source":"forum2020"},{"name":"MVM Carrière","role":"pedreira","source":"forum2020"},{"name":"Vanha Kivi","role":"pedreira","source":"forum2020"},{"name":"MarmoSpA","role":"marmoraria","source":"forum2020"},{"name":"QuadrelliSpA","role":"marmoraria","source":"forum2020"},{"name":"ACC","role":"metalurgica","source":"wiki"},{"name":"Alumcore","role":"metalurgica","source":"wiki"},{"name":"Aluxion Metal Solution","role":"metalurgica","source":"wiki"},{"name":"Oțel Impecabil","role":"metalurgica","source":"forum2020"},{"name":"Stomanena Roza","role":"metalurgica","source":"forum2020"},{"name":"Agregados, S.A.","role":"cimenteira","source":"wiki"},{"name":"Radus","role":"cimenteira","source":"forum2020"},{"name":"Radus RU","role":"cimenteira","source":"forum2020"},{"name":"NBFC","role":"quimica","source":"forum2014"},{"name":"WGCC","role":"quimica","source":"forum2014"},{"name":"ITCC","role":"industrial","source":"forum2014"},{"name":"Vitas Power","role":"industrial","source":"forum2020"},{"name":"Nucléon","role":"industrial","source":"forum2020"},{"name":"Severoatom","role":"industrial","source":"forum2020"},{"name":"UKKO Voima","role":"industrial","source":"forum2020"},{"name":"Engeron","role":"industrial","source":"forum2020"},{"name":"Iberatómica","role":"industrial","source":"forum2020"},{"name":"CGLA","role":"industrial","source":"forum2020"},{"name":"SCS Paper","role":"industrial","source":"forum2020"},{"name":"Estonian Paper AS","role":"industrial","source":"forum2020"},{"name":"Viljo paperitehdas Oy","role":"industrial","source":"forum2020"},{"name":"Vilniaus Popieriaus Fabrikas","role":"industrial","source":"forum2020"},{"name":"TREE-ET","role":"floresta","source":"forum2014"},{"name":"BHB - La Raffinerie","role":"petroleo","source":"wiki"},{"name":"NS Oil RU","role":"petroleo","source":"forum2020"}];
const SCS_CATALOG_ALIASES={"eurogoodies":"eurogoodies","euroacres":"euroacres","lkwlog":"lkwloggmbh","lkw":"lkwloggmbh","treeet":"treeet","steinbruch":"steinbruch","sanbuilders":"sanbuilders","sellplan":"sellplan","kaarfor":"kaarfor","lognstick":"lognstick","nbfc":"nbfc","wgcc":"wgcc"};
function scsKey(value){return String(value||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]/g,"")}
const SCS_CATALOG_BY_NAME=new Map(SCS_COMPANY_CATALOG.map(x=>[scsKey(x.name),x]));
function scsCatalogLookup(id,displayName){
 for(const candidate of [id,displayName]){
  const key=scsKey(candidate);
  if(!key)continue;
  const actual=SCS_CATALOG_ALIASES[key]||key;
  const item=SCS_CATALOG_BY_NAME.get(actual);
  if(item)return item;
 }
 return null;
}

// Consulta por empresa REAL do mapa: nunca itera o catálogo para criar empresas.
function catalogForMapCompany(company){
 if(!company||!company.id)return null;
 const byId=scsCatalogLookup(company.id,"");
 if(byId)return{...byId,matchBy:"ID"};
 const byName=company.name?scsCatalogLookup("",company.name):null;
 return byName?{...byName,matchBy:"nome exato"}:null;
}
function checkMapCompanyAgainstSCS(company){
 const reference=catalogForMapCompany(company);
 company.catalogConsulted=true;
 if(!reference){company.catalog=null;return null}
 company.catalog=reference;
 company.role=reference.role;
 company.evidence="empresa padrão SCS reconhecida por "+reference.matchBy+": "+reference.name+" ("+reference.source+")";
 return reference;
}
function consultCatalogForMapDistribution(map){
 let consulted=0,matched=0;
 for(const company of map.companies.values()){
  consulted++;
  if(checkMapCompanyAgainstSCS(company))matched++;
 }
 return{consulted,matched};
}

const sectors=[
["cooperativa",/(cooperativa|cooperativa agricola|agrocooperativa|agrocoop|cooperagro|coopercentro)/],
["silo",/(silo|cerealista|armazem de graos|grain storage)/],
["fazenda",/(fazenda|faz0|faz1|faz2|faz3|faz4|faz5|agropecuaria|sitio agricola|cultivo agricola|farm|plantacao)/],
["pecuaria",/(pecuaria|granja|criatorio de gado|confinamento)/],
["racoes",/(fabrica de racao|industria de racao|nutricao animal|feed mill)/],
["moinho",/(moinho|esmagadora de soja|beneficiadora de graos)/],
["adubeira",/(industria de fertilizantes|fabrica de adubo|yara|mosaic)/],
["serraria",/(serraria|industria madeireira|sawmill)/],
["madeireira",/(madeireira|madeiraria|deposito de madeira|comercio de madeira|loja de madeira|deposito madeireiro)/],
["floresta",/(florestal|reflorestamento|extracao de madeira)/],
["textil",/(textil|tecelagem|fiacao|fabrica de tecidos)/],
["algodoeira",/(algodoeira|beneficiamento de algodao)/],
["ceramica",/(olaria|ceramica|tijolaria|fabrica de tijolos)/],
["cimenteira",/(cimenteira|fabrica de cimento|industria de cimento)/],
["pedreira",/(pedreira|extracao de granito|quarry)/],
["mineracao",/(mineracao|mineradora|minera de pedra|extracao mineral|mining company)/],
["materiais",/((?:material|materiais)(?: de )?construcao|deposito (?:de )?(?:material|materiais)|loja (?:de )?(?:material|materiais)(?: de construcao)?|casa (?:de )?(?:material|materiais)(?: de construcao)?|revenda de (?:material|materiais)(?: de construcao)?|building supplies)/],
["obras",/(construtora|obra civil|canteiro|construcao|empreiteira)/],
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
 milho:{out:["fazenda"],in:["cooperativa","silo","moinho","racoes","pecuaria"]},
 soja:{out:["fazenda"],in:["cooperativa","silo","moinho"]},
 sorgo:{out:["fazenda"],in:["cooperativa","silo","racoes","pecuaria"]},
 adubo:{out:["adubeira","agroinsumos","logistica"],in:["fazenda","cana","pecuaria","agroinsumos","logistica"]},
 madeira:{out:["madeireira","serraria","floresta","materiais","logistica"],in:["obras","madeireira","materiais","logistica"]},
 algodao:{out:["fazenda","algodoeira","logistica"],in:["cooperativa","algodoeira","textil","logistica"]},
 cimento:{out:["materiais","logistica","cimenteira"],in:["obras","materiais","logistica"]},
 batata:{out:["fazenda","hortifruti","alimentos","logistica"],in:["supermercado","hortifruti","alimentos","logistica"]},
 laranja:{out:["fazenda","hortifruti","alimentos","logistica"],in:["supermercado","hortifruti","alimentos","logistica"]},
 cerveja:{out:["cervejaria","bebidas","alimentos","logistica"],in:["bebidas","supermercado","alimentos","logistica"]},
 tijolo:{out:["materiais","logistica","ceramica"],in:["obras","materiais","logistica"]},
 granito:{out:["pedreira","mineracao","marmoraria","materiais","logistica"],in:["obras","marmoraria","materiais","logistica"]},
 racao:{out:["racoes","logistica","alimentos"],in:["fazenda","pecuaria","logistica","alimentos"]},
 aco:{out:["siderurgica","metalurgica","materiais","logistica"],in:["metalurgica","obras","materiais","logistica"]},
 bobinas_industriais:{out:["siderurgica","metalurgica","logistica"],in:["metalurgica","siderurgica","logistica"]},
 // Paletes vazios: fabricantes e operadores logísticos expedem, várias empresas recebem.
 palete_vazio:{out:["madeireira","serraria","paletes"],in:["cooperativa","logistica","silo","materiais","alimentos","supermercado","racoes","cervejaria","hortifruti","textil"]},
 // Pallets Alto do Librelato: a logística será centrada no setor madeireiro,
 // sujeita à confirmação da natureza exata da carga no modelo 3D.
 paletizado:{out:["madeireira","serraria","paletes"],in:["cooperativa","logistica","silo","materiais","alimentos","supermercado","racoes","cervejaria","hortifruti","textil"]}
};
const norm=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[_-]/g," ");
const pathNorm=s=>String(s).replace(/\\/g,"/").replace(/^\/+/,"").replace(/^\.\/+/,"");
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const yieldUI=()=>new Promise(r=>setTimeout(r,0));
const say=(msg,pct)=>{ui.message.textContent=msg;ui.bar.style.width=Math.max(0,Math.min(100,pct))+"%"};
const known=(id,label)=>{
 const x=norm(id)+" "+norm(label);
 const compact=norm(id).replace(/ /g,"");
 if(/^(canavial|usinaluciana|usina.?cana|sucroalco)/.test(compact))return "cana";
 if(/^(marmor|marmol|marbol|jbpedras)/.test(compact))return "marmoraria";
 for(const [r,re] of sectors)if(re.test(x))return r;
 const flat=norm(id).replace(/ /g,"");
 // Regras de abreviações atestáveis, sem tornar empresas genéricas em produtoras.
 const prefixes=[
 ["cooperativa",/^(coop(?:erativa)?|cooper|agrocoop)/],
 ["silo",/^(silos?|cerealista|graos)/],
 ["racoes",/^(racoes?|feedmill|nutricaoanimal)/],
 ["adubeira",/^(fertilizantes?|adubeira)/],
 ["fazenda",/^(faz(?:enda|[_0-9])|farm|finca|hacienda|agropec|agricol|agricult|rural|plantacao|plantation|cultivo|rancho)/],
 ["pecuaria",/^(arnasuino|pecuaria|granja|ganaderia|gado)/],
 ["floresta",/^(florestal|reflorestamento)/],
 ["serraria",/^(araserr|serraria|serradero|sawmill)/],
 ["madeireira",/^(madeireira|madeiraria|lojamadeira|depomadeira|betimmadeira)/],
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
 ["materiais",/^(materiais|materialconstrucao|matconstrucao|matconst|matconstr|lojamat|lojamaterial|lojamateriais|depositomaterial|depomaterial|casamaterial|depoconst)/],
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
const ALLOWED_ROLES=new Set(["cooperativa","madeireira","cana","marmoraria","agroinsumos","mineracao","logistica","fazenda","silo","pecuaria","racoes","moinho","adubeira","serraria","floresta","textil","algodoeira","ceramica","cimenteira","pedreira","obras","materiais","cervejaria","bebidas","supermercado","hortifruti","alimentos","siderurgica","metalurgica","paletes","posto","concessionaria","correios"]);
function applyCompanyOverrides(map){
 const field=el("companyCreateOverrides"),raw=field?.value?.trim()||"";
 const accepted=[],errors=[];
 if(!raw)return{accepted};
 for(const [i,row]of raw.split(/\r?\n/).entries()){
  const line=row.trim();if(!line||line.startsWith("#"))continue;
  const m=line.match(/^([a-z0-9_.-]+)\s*[=:]\s*([a-z_]+)$/i);
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
// Os arquivos podem vir compactados a partir de def/company, company ou
// diretamente do CONTEÚDO de company (<empresa>/editor, in, out).
// Formato sem prefixo só é aceito se o pacote demonstrar estrutura de Company.
function discoverBareCompanyRoots(zip){
 const roots=new Map();
 for(const raw of Object.keys(zip.files)){
  const p=pathNorm(raw);
  if(p.split("/").some(x=>x==="."||x===".."))throw Error("Caminho inseguro dentro da DEF: "+raw);
  const match=p.match(/^(.+?)\/(editor|in|out)\/[^/]+\.sii$/i);
  if(!match)continue;
  const root=match[1],segments=root.split("/");
  if(segments.length>5||!segments.every(x=>/^[a-z0-9_.-]+$/i.test(x)))continue;
  const key=root.toLowerCase();
  if(!roots.has(key))roots.set(key,{root,editor:0,in:0,out:0});
  roots.get(key)[match[2].toLowerCase()]++;
 }
 // Um modelo pode conter pasta "editor", mas uma DEF Company deve demonstrar
 // empresas com editor e permissões de carga no mesmo diretório.
 return new Set([...roots].filter(([,r])=>r.editor>0&&(r.in>0||r.out>0)).map(([key])=>key));
}
const companyPath=(raw,bareRoots=null)=>{
 const p=pathNorm(raw);
 if(p.split("/").some(x=>x===".."||x==="."))throw Error("Caminho inválido no ZIP de empresas: "+raw);
 // Formato canônico com prefixo explícito.
 const canonical=p.match(/(?:^|\/)(?:def\/)?company\/(.+)$/i);
 if(canonical)return"def/company/"+canonical[1];
 // ZIPs gerados a partir do interior de "company/" perdem seu prefixo.
 // Só aceitar diretorios confirmados por editor E in/out.
 if(bareRoots?.size){
  const match=p.match(/^(.+?)\/(editor|in|out)\/([^/]+\.sii)$/i);
  if(match&&bareRoots.has(match[1].toLowerCase())){
   const id=match[1].split("/").pop();
   return"def/company/"+id+"/"+match[2]+"/"+match[3];
  }
  const permanent=p.match(/^(.+?)\.sii$/i);
  if(permanent&&bareRoots.has(permanent[1].toLowerCase())){
   return"def/company/"+permanent[1].split("/").pop()+".sii";
  }
 }
 const manifest=p.match(/(?:^|\/)(company(?:\.[a-z0-9_-]+)?\.sii)$/i);
 return manifest?"def/"+manifest[1]:null;
};
const cargoPath=raw=>{
 const p=pathNorm(raw);
 if(p.split("/").some(x=>x===".."||x==="."))throw Error("Caminho inválido na DEF de cargas: "+raw);
 const m=p.match(/(?:^|\/)(?:def\/)?(cargo\/.+|vehicle\/.+|cargo\.[a-z0-9_-]+\.sii)$/i);
 return m?"def/"+m[1]:null;
};
const companyMeta=path=>{
 // Caminhos de empresas customizadas podem conter hífen e ponto.
 const a=path.match(/^def\/company\/([a-z0-9_.-]+)\/(in|out|editor)\/([^/]+\.sii)$/i);
 if(a)return{id:a[1].toLowerCase(),rawId:a[1],type:a[2].toLowerCase(),name:a[3]};
 const b=path.match(/^def\/company\/([a-z0-9_.-]+)\.sii$/i);
 return b?{id:b[1].toLowerCase(),rawId:b[1],type:"permanent",name:b[1]}:null;
};
async function mapFingerprint(map){
 // Impressão digital de caminhos E conteúdo. Arquivos recém-criados ainda
 // não possuem CRC32 no JSZip, por isso recebem hash direto de seus bytes.
 let hash=2166136261;
 const addByte=n=>{hash^=n;hash=Math.imul(hash,16777619)};
 const addText=text=>{
  for(let i=0;i<text.length;i++){
   const n=text.charCodeAt(i);
   addByte(n&255);addByte(n>>>8);
  }
 };
 for(const c of [...map.companies.values()].sort((a,b)=>a.id.localeCompare(b.id)))addText("C:"+c.id);
 for(const f of [...map.files.values()].sort((a,b)=>a.p.localeCompare(b.p))){
  addText("P:"+f.p.toLowerCase());
  const data=f.obj?._data;
  if(typeof data?.crc32==="number"&&typeof data?.uncompressedSize==="number"){
   addText("S:"+data.uncompressedSize+":CRC:"+data.crc32);
  }else{
   const bytes=await f.obj.async("uint8array");
   addText("B:"+bytes.byteLength);
   for(const x of bytes)addByte(x);
  }
 }
 return(hash>>>0).toString(16).padStart(8,"0");
}
// Leitor de pacotes ZIP, inclusive SCS/ZIP guardados dentro de outro ZIP.
// Mantém os nomes internos: prefixos de pastas só são removidos na projeção
// canonizada de def/company e def/cargo, nunca nos dados originais.
const ARCHIVE_LIMITS=Object.freeze({
 maxDepth:3,
 maxNestedFiles:32,
 maxEntries:120000,
 maxNestedBytes:320*1024*1024
});
const ARCHIVE_FILE=/\.(?:zip|scs)$/i;
const ZIP_SIGNATURES=new Set(["504b0304","504b0506","504b0708"]);
function isZipMagic(data){
 const a=data instanceof Uint8Array?data:new Uint8Array(data);
 if(a.length<4)return false;
 return ZIP_SIGNATURES.has(Array.from(a.slice(0,4),v=>v.toString(16).padStart(2,"0")).join(""));
}
async function zipRead(file){
 if(!file||typeof file.slice!=="function")throw Error("Selecione um ZIP/SCS válido.");
 if(file.size>700*1024*1024)throw Error("Arquivo maior que 700 MB. Envie apenas a DEF Company ou a DEF das cargas, sem modelos e texturas.");
 const header=new Uint8Array(await file.slice(0,4).arrayBuffer());
 if(!isZipMagic(header)){
  throw Error("O arquivo "+file.name+" não é ZIP/SCS ZIP legível. Pacotes HashFS precisam ser extraídos com ferramenta compatível antes do upload.");
 }
 return JSZip.loadAsync(file,{createFolders:false,checkCRC32:false});
}
async function resolveEntries(zip,kind){
 const matched=[],stack=[{zip,level:0,source:"arquivo enviado"}];
 let entryCount=0,nestedCount=0,skippedHashFS=0;
 const isRelevant=kind==="map"?companyPath:cargoPath;
 while(stack.length){
  const frame=stack.pop();
  const nested=[];
  const bareRoots=kind==="map"?discoverBareCompanyRoots(frame.zip):null;
  let matchedHere=0;
  for(const [raw,obj] of Object.entries(frame.zip.files)){
   if(obj.dir)continue;
   if(++entryCount>ARCHIVE_LIMITS.maxEntries)throw Error("Pacote muito grande: limite de "+ARCHIVE_LIMITS.maxEntries+" entradas alcançado. Selecione só a DEF do mapa.");
   if(obj.unsafeOriginalName&&/(?:^|[\\/])\.\.(?:[\\/]|$)/.test(obj.unsafeOriginalName))
     throw Error("Caminho inseguro encontrado no arquivo "+frame.source);
   const name=pathNorm(raw);
   const canonical=kind==="map"?companyPath(name,bareRoots):isRelevant(name);
   if(canonical){
    matched.push([name,obj,frame.source,bareRoots]);
    if(kind!=="map"||companyMeta(canonical))matchedHere++;
   }else if(frame.level<ARCHIVE_LIMITS.maxDepth&&ARCHIVE_FILE.test(name)){
    nested.push({name,obj});
   }
  }
  // Quando este nível já tem Company, os SCS/ZIP extras não fazem parte
  // dela. Evita colisões e leitura custosa de mods de veículos/modelos.
  if(matchedHere>0)continue;
  for(const entry of nested){
   if(++nestedCount>ARCHIVE_LIMITS.maxNestedFiles)
     throw Error("O arquivo contém muitos pacotes internos. Separe a DEF do mapa (máximo "+ARCHIVE_LIMITS.maxNestedFiles+").");
   const size=entry.obj._data?.uncompressedSize;
   if(size&&size>ARCHIVE_LIMITS.maxNestedBytes)
     throw Error("Arquivo interno grande demais: "+entry.name+". Envie somente a DEF do mapa.");
   const data=await entry.obj.async("uint8array");
   if(data.byteLength>ARCHIVE_LIMITS.maxNestedBytes)
     throw Error("Pacote interno excede o limite de tamanho: "+entry.name);
   if(!isZipMagic(data)){skippedHashFS++;continue}
   let inner;
   try{
    inner=await JSZip.loadAsync(data,{createFolders:false,checkCRC32:false});
   }catch(err){
    throw Error("Falha ao abrir ZIP/SCS interno "+entry.name+": "+(err?.message||err));
   }
   stack.push({zip:inner,level:frame.level+1,source:entry.name});
   if(nestedCount%4===0)await yieldUI();
  }
 }
 return {matched,nestedCount,skippedHashFS};
}

function inferRoleFromHistoricalFreights(company){
 // O histórico serve somente para identificar setor; nunca é copiado como logística.
 const cargoSet=new Set(company.old.map(x=>String(x.unit||x.stem).toLowerCase()));
 if(!cargoSet.size||cargoSet.size>10||company.old.length>14)return null;
 const has=(dir,re)=>company.old.some(x=>x.dir===dir&&re.test(String(x.unit||x.stem).replace(/[_-]/g," ")));
 const out=re=>has("out",re),inn=re=>has("in",re);
 const grain=/(wheat|trigo|maize|corn|milho|soybean|soja|barley|cevada|sunflower|girassol|rapeseed|canola|sorghum|sorgo|rice|arroz|grain|graos)/i;
 const crop=/(potat|batata|beet|beterraba|cotton|algodao|orange|laranja|vegetable|hortalica|fruit|fruta|cereals?|sementes?|seeds?)/i;
 const fert=/(fertiliz|adubo|seed|sement|pesticid|defensivo)/i;
 const reGrain=company.old.filter(x=>x.dir==="out"&&grain.test(x.unit||x.stem)).map(x=>String(x.unit||x.stem).toLowerCase());
 const inGrain=new Set(company.old.filter(x=>x.dir==="in"&&grain.test(x.unit||x.stem)).map(x=>String(x.unit||x.stem).toLowerCase()));
 const sharedGrain=reGrain.some(x=>inGrain.has(x));
 const evidence=[
 ["silo",sharedGrain],
 ["cooperativa",out(/(cotton|algodao|pluma)/i)&&inn(/(fertiliz|adubo|racao|feed)/i)],
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
const SCS_CARGO_CATEGORY_MAP=[
 ["milho",/(?:^|[_ ]|\.)(?:corn(?:_b)?|maize|milho(?:alto)?)(?:$|[_ ]|\.)/],
 ["soja",/(?:^|[_ ]|\.)(?:soybeans?(?:_b)?|soja(?:alto)?)(?:$|[_ ]|\.)/],
 ["sorgo",/(?:^|[_ ]|\.)(?:sorghum|sorgo(?:alto)?)(?:$|[_ ]|\.)/],
 ["batata",/(?:^|[_ ]|\.)(?:potatoes?(?:_b)?|batatas?)(?:$|[_ ]|\.)/],
 ["laranja",/(?:^|[_ ]|\.)(?:oranges?|laranjas?|citrus)(?:$|[_ ]|\.)/],
 ["adubo",/(?:^|[_ ]|\.)(?:fertilizers?|fertilizantes?|adubo|ureia|urea)(?:$|[_ ]|\.)/],
 ["madeira",/(?:^|[_ ]|\.)(?:logs?|lumber|timber|wood|planks?|boards?|madeira|toras?)(?:$|[_ ]|\.)/],
 ["algodao",/(?:^|[_ ]|\.)(?:cotton(?:_bales?)?|algodao|pluma)(?:$|[_ ]|\.)/],
 ["cimento",/(?:^|[_ ]|\.)(?:cement(?:_bag|_pallet)?|cimento)(?:$|[_ ]|\.)/],
 ["tijolo",/(?:^|[_ ]|\.)(?:bricks?|tijolos?)(?:$|[_ ]|\.)/],
 ["telha",/(?:^|[_ ]|\.)(?:tiles?|telhas?|roof(?:ing)?)(?:$|[_ ]|\.)/],
 ["granito",/(?:^|[_ ]|\.)(?:granite|granito|marble|marmore)(?:$|[_ ]|\.)/],
 ["cerveja",/(?:^|[_ ]|\.)(?:beer|cervejas?)(?:$|[_ ]|\.)/],
 ["racao",/(?:^|[_ ]|\.)(?:animal_?feed|feedmeal|racao|xerem)(?:$|[_ ]|\.)/],
 ["bobinas_industriais",/(?:^|[_ ]|\.)(?:steel_?coils?|metal_?coils?|bobinas?)(?:$|[_ ]|\.)/],
 ["combustivel",/(?:^|[_ ]|\.)(?:gasoline|diesel|petrol|fuel|combustivel)(?:$|[_ ]|\.)/],
 ["maquinas",/(?:^|[_ ]|\.)(?:excavators?|tractors?|machinery|equipment|digger)(?:$|[_ ]|\.)/],
 ["quimicos",/(?:^|[_ ]|\.)(?:chemical|chemicals|acids?|quimicos?)(?:$|[_ ]|\.)/],
 ["alimentos",/(?:^|[_ ]|\.)(?:food|groceries|processed_food|comida|alimentos)(?:$|[_ ]|\.)/]
];
function oldCargoCategory(stemOrUnit){
 const x=norm(String(stemOrUnit||"").replace(/^cargo[.:]/i,"")).replace(/\s+/g,"_");
 for(const [k,re] of SCS_CARGO_CATEGORY_MAP)if(re.test(x))return k;
 return null;
}
function categorizeExistingCompanyLoads(c){
 const result={in:new Map(),out:new Map(),unknownIn:0,unknownOut:0};
 for(const x of c.old){
  const role=oldCargoCategory(x.unit)||oldCargoCategory(x.stem);
  x.category=role;
  if(role)result[x.dir].set(role,(result[x.dir].get(role)||0)+1);
  else if(x.dir==="in")result.unknownIn++;
  else result.unknownOut++;
 }
 return result;
}

// Uma mercadoria pode ser expedida de um estabelecimento de estoque ou revenda,
// sem existir uma fábrica no mapa. Identificamos o ramo pelas cargas REAIS da DEF.
const CONSTRUCTION_CARGO_MARKERS=[
 ["areia",/\b(areias?|sand)\b/],
 ["brita",/\b(brita|britas|gravel|cascalho)\b/],
 ["tijolo",/\b(tijolos?|bricks?|ceramic ?bricks?)\b/],
 ["piso",/\b(pisos?|floor(?:ing)?|azulejos?|revestimentos?)\b/],
 ["telha",/\b(telhas?|roof(?:ing)?|roof ?tiles?)\b/],
 ["tubo",/\b(tubos?|tubos? ?concret|tubos? ?mg|concrete ?pipes?|pipes?|tubulacoes?)\b/],
 ["ferragem",/\b(ferro ?const|b ?reforco|vergalhoes?|rebars?|armaduras?|ferragens?)\b/],
 ["calha",/\b(calhas?|gutters?)\b/],
 ["madeira",/\b(madeira|madeirame|wood|timber|lumber|tabuas?|planks?)\b/],
 ["granito",/\b(pedras?|granito|granite|marmore|marble|calcario|limestone)\b/],
 ["cimento",/\b(cimento|cement|argamassa|reboco|blocos? ?concret|concrete ?blocks?)\b/],
 ["aco",/\b(chapa ?aco|chapas? ?aco|steel ?plates?|sua?luminio)\b/]
];
const CONSTRUCTION_FINISHED=new Set(["tijolo","piso","telha","tubo","ferragem","calha","madeira","cimento","aco"]);
function semanticConstructionType(raw){
 const val=norm(String(raw||"").replace(/^cargo[.:]/i,"")).replace(/[^a-z0-9 ]/g," ").trim();
 for(const [type,re]of CONSTRUCTION_CARGO_MARKERS)if(re.test(val))return type;
 return null;
}
function constructionStockEvidence(company){
 const results={in:new Set(),out:new Set(),otherIn:0,otherOut:0};
 for(const item of company.old||[]){
  const cargo=item.unit||item.stem;
  const kind=semanticConstructionType(cargo);
  if(kind)results[item.dir].add(kind);
  else if(item.dir==="out")results.otherOut++;
  else if(item.dir==="in")results.otherIn++;
 }
 const outKinds=results.out;
 const totalOut=outKinds.size+results.otherOut;
 const variety=outKinds.size>=2&&[...outKinds].some(x=>CONSTRUCTION_FINISHED.has(x));
 const hasStockMovement=results.in.size>=1||outKinds.size>=3;
 const concentration=totalOut>0?outKinds.size/totalOut:0;
 return{
  ...results,
  isRetailProfile:variety&&hasStockMovement&&concentration>=.45,
  category:"materiais_construcao",
  outCount:outKinds.size,
  inCount:results.in.size
 };
}
function categoryOutletCandidate(company,type,direction){
 if(!company||!["cimento","tijolo","granito","madeira"].includes(type))return false;
 if(company.catalog&&company.role!=="materiais")return false;
 if(["posto","correios","concessionaria","cana","cervejaria","supermercado","pecuaria","siderurgica","metalurgica","mineracao","pedreira","marmoraria","fazenda","ceramica"].includes(company.role))return false;
 const profile=constructionStockEvidence(company);
 if(direction==="out"){
  return profile.isRetailProfile&&["materiais","obras","desconhecida","logistica"].includes(company.role);
 }
 // Recebedor por ramo: obras, depósitos e revendas com IN compatível,
 // mesmo quando o ID da empresa é opaco.
 return profile.inCount>=2&&
        ["obras","materiais","desconhecida","logistica"].includes(company.role);
}
function inferConstructionSupplyFromINOUT(company){
 if(!company||company.catalog||!(company.role==="obras"||company.role==="desconhecida"))return false;
 const p=constructionStockEvidence(company);
 if(!p.isRetailProfile)return false;
 company.role="materiais";
 company.evidence="ramo de materiais confirmado pela variedade IN/OUT: OUT "+[...p.out].join(", ")+"; IN "+[...p.in].join(", ");
 company.supplyProof=[...p.out];
 return true;
}

// Reconciliar ramos pela mercadoria REAL antes de confiar em nomes comerciais.
// Casos reais: "acero" no mapa recebe/expede adubo e ração, não bobinas de aço.
function reconcileSectorWithEvidence(c){
 if(!c||c.catalog||!c.old?.length)return false;
 const out=new Set(c.old.filter(x=>x.dir==="out").map(x=>String(x.unit||x.stem).toLowerCase()));
 const incoming=new Set(c.old.filter(x=>x.dir==="in").map(x=>String(x.unit||x.stem).toLowerCase()));
 const agInput=["adubo","fertilizante","fertilizer","ureia"].filter(x=>out.has(x));
 const agricultural=out.has("racao")||out.has("equipagrico")||out.has("aramefar")||out.has("sementes");
 // Exigir sinais independentes de catálogo: nome sozinho não decide o ramo.
 if(agInput.length>=2&&agricultural&&
    ["metalurgica","siderurgica","desconhecida","logistica"].includes(c.role)){
   c.role="agroinsumos";
   c.evidence="categoria agroinsumos inferida de OUT "+agInput.join(", ")+" e mercadorias agrícolas";
   return true;
 }
 const metalGoods=["b_reforco","ferroconst","chapaaco","tubosmg","aramefar"].filter(x=>out.has(x));
 if(c.role==="desconhecida"&&metalGoods.length>=2&&
    [...incoming].some(x=>metalGoods.includes(x))){
   c.role="metalurgica";
   c.evidence="metalurgia identificada por IN/OUT de ferragens e chapas: "+metalGoods.join(", ");
   return true;
 }

 // IDs opacos em mapas diferentes: inferência apenas quando IN e OUT
 // demonstram uma operação econômica coerente, não pelo nome inventado.
 const metallic=/^(?:b_reforco|ferroconst|chapaaco|sumetal|sualuminio|bobinas?|steel_coils?)$/;
 const stone=/^(?:pedra|granito|marmore|granite|marble|lajotas?)$/;
 const metalOut=[...out].filter(x=>metallic.test(x));
 const metalIn=[...incoming].filter(x=>metallic.test(x));
 if(c.role==="desconhecida"&&metalOut.length>=2&&metalIn.length>=1){
  c.role="metalurgica";
  c.evidence="metalurgia por IN/OUT observados: OUT "+metalOut.join(", ")+"; IN "+metalIn.join(", ");
  return true;
 }
 const stoneOut=[...out].filter(x=>stone.test(x));
 const stoneIn=[...incoming].filter(x=>stone.test(x));
 if(c.role==="desconhecida"&&stoneOut.length>=2&&stoneIn.length>=1){
  c.role="marmoraria";
  c.evidence="beneficiamento de pedras por IN/OUT observados: OUT "+stoneOut.join(", ");
  return true;
 }
 if(c.role==="desconhecida"&&out.has("racao")&&(incoming.has("milho")||incoming.has("soja")||incoming.has("feijao"))){
   c.role="racoes";c.evidence="fábrica/distribuidora de ração identificada por OUT ração e IN grãos";return true;
 }
 return false;
}
function oldSpecificEvidence(c,type,dir){
 // Priorizar o cargo efetivamente citado no arquivo cargo_def da própria empresa.
 const aliases={
  cerveja:/^(cervejas?|beer|ambev|amstel|antarctica|brahma|budweiser|devassa|heineken|schin|skol)$/,
  algodao:/^(algodao|cotton|pluma|cotton_bales?)$/,
  racao:/^(racao|animal_?feed|xerem|farelo|feedmeal)$/,
  bobinas_industriais:/^(bobinas?|steel_?coils?|metal_?coils?)$/,
  granito:/^(granito|granite|marmore|marble|pedra)$/,
  tijolo:/^(tijolos?|bricks?)$/,
  madeira:/^(madeira|lumber|timber|planks?)$/,
  cimento:/^(cimento|cement|cement_b|cement_pallet|cement_bag)$/
 };
 return(c.old||[]).some(x=>{
  if(x.dir!==dir)return false;
  const identifier=String(x.unit||x.stem).toLowerCase();
  if(oldCargoCategory(identifier)===type)return true;
  return !!aliases[type]?.test(identifier);
 });
}
function farmCargoEvidence(c,type){
 const special=specificFarmCrop(c);
 if(special&&special!==type)return false;
 if(!c.old?.length)return true;
 return oldSpecificEvidence(c,type,"out");
}

async function loadMap(zip){
 const companies=new Map(),files=new Map();
 const resolution=await resolveEntries(zip,"map");
 for(const [raw,obj,source,bareRoots] of resolution.matched){
  const p=companyPath(raw,bareRoots);if(!p)continue;
  const key=p.toLowerCase();if(files.has(key))throw Error("Definição duplicada: "+p+" (em "+files.get(key).source+" e "+source+"). Remova um dos pacotes repetidos; nenhuma entrada será sobrescrita.");
  files.set(key,{p,obj,source});
  const m=companyMeta(p);if(!m)continue;
  if(!companies.has(m.id))companies.set(m.id,{id:m.id,folder:m.rawId,name:"",role:"desconhecida",old:[],editor:0});
  const c=companies.get(m.id);
  if(m.type==="editor")c.editor++;
  if(m.type==="in"||m.type==="out")c.old.push({p,dir:m.type,stem:m.name.replace(/\.sii$/i,""),unit:null,category:null});
 }
 if(!companies.size){
  const sample=Object.keys(zip.files).filter(p=>!zip.files[p].dir).slice(0,6);
  throw Error("Nenhuma DEF Company reconhecida. Estruturas aceitas: def/company/<empresa>/editor|in|out, company/<empresa>/editor|in|out ou <empresa>/editor|in|out (editor e IN/OUT no mesmo diretório). Pacotes internos lidos: "+resolution.nestedCount+"; HashFS não legíveis: "+resolution.skippedHashFS+". Exemplos do ZIP: "+(sample.join(", ")||"nenhum")+".");
 }
 let i=0;
 for(const v of files.values()){
  const m=companyMeta(v.p);if(!m||m.type!=="permanent")continue;
  const c=companies.get(m.id);if(!c)continue;
  const txt=await v.obj.async("text"),name=txt.match(/^\s*name\s*:\s*"([^"]+)"/mi);
  if(name)c.name=name[1];
  if((++i)%100===0)await yieldUI();
 }
 let parsedRelations=0,scannedRelations=0;
 for(const item of files.values()){
  const m=companyMeta(item.p);
  if(!m||(m.type!=="in"&&m.type!=="out"))continue;
  const obj=item.obj;
  if((obj._data?.uncompressedSize||0)>100000)continue;
  const raw=await obj.async("text");
  const match=raw.replace(/\/\/[^\n]*/g,"").match(/\bcargo\s*:\s*["']?cargo\.([a-z0-9_]+)/i);
  if(match){
   const c=companies.get(m.id);
   const relation=c?.old.find(x=>x.p===item.p);
   if(relation){relation.unit=match[1].toLowerCase();parsedRelations++}
  }
  if(++scannedRelations%180===0)await yieldUI();
 }
 for(const c of companies.values())c.categories=categorizeExistingCompanyLoads(c);
 for(const c of companies.values()){
  if(checkMapCompanyAgainstSCS(c))continue;
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
  // Evidência específica da DEF supera palpites pelo nome da pasta.
  reconcileSectorWithEvidence(c);
  // A DEF pode indicar um depósito de materiais mesmo com ID de construtora.
  inferConstructionSupplyFromINOUT(c);
 }

 return{companies,files,parsedRelations,catalogMatched:[...companies.values()].filter(c=>c.catalog).length,archivesRead:resolution.nestedCount}
}
async function loadCargo(zip){
 const files=new Map(),cargos=new Map(),manifests=[],trailer=new Map();
 const resolution=await resolveEntries(zip,"cargo");
 for(const [raw,obj,source] of resolution.matched){
  const p=cargoPath(raw);if(!p)continue;
  if(files.has(p.toLowerCase()))throw Error("Definição de carga duplicada: "+p+" (em "+files.get(p.toLowerCase()).source+" e "+source+").");
  files.set(p.toLowerCase(),{p,obj,source})
 }
 if(!files.size)throw Error("Não foi localizada a DEF das cargas. Procure cargo/, vehicle/ ou def/cargo/ dentro do ZIP/SCS, inclusive pacotes internos.");
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
 return{files,cargos,manifests,archivesRead:resolution.nestedCount}
}

const LEGACY_EVIDENCE={
 milho:/^(?:vg_)?(?:corn(?:_b)?|maize|milho|milhoalto)$/i,
 soja:/^(?:vg_)?(?:soybean(?:_b)?|soja|sojaalto)$/i,
 sorgo:/^(?:vg_)?(?:sorghum|sorgo|sorgoalto)$/i,
 batata:/^(?:vg_)?(?:potato(?:es)?(?:_b)?|batatas?)$/i,
 laranja:/^(?:vg_)?(?:oranges?|laranjas?)$/i,
 cimento:/^(?:vg_)?(?:cement|cimento|cement_b|cement_pallet|cement_bag)$/i,
 tijolo:/^(?:vg_)?(?:bricks?|tijolos?|tijolaria|ceramic_bricks?)$/i,
 granito:/^(?:vg_)?(?:granite|granito|marble|marmore|marble_blocks?)$/i,
 adubo:/^(?:vg_)?(?:fertilizers?|fertilizantes?|adubo|ureia|fertilizer_b)$/i,
 madeira:/^(?:vg_)?(?:lumber|wood|timber|planks?|boards?|logs?|toras?|madeira)$/i,
 algodao:/^(?:vg_)?(?:cotton|cotton_bales?|algodao|pluma|cottonlint)$/i,
 bobinas_industriais:/^(?:vg_)?(?:steel_coils?|steelcoil|metal_coils?|bobinas?|chapa_aco|rolled_steel)$/i
};
const SPECIAL_CROPS=new Set(["milho","soja","sorgo","batata","laranja","algodao"]);
const PERISHABLE_CROPS=new Set(["batata","laranja"]);
const LEGACY_INCOMPATIBLE_ROLES=new Set(["posto","correios","concessionaria","cana"]);
function cargoSpecificName(c,type){
 const text=norm([c.id,c.name].join(" "));
 const hints={
  milho:/\b(milho|corn|maize)\b/,
  soja:/\b(soja|soybean)\b/,
  sorgo:/\b(sorgo|sorghum)\b/,
  batata:/\b(batata|potato)\b/,
  laranja:/\b(laranja|orange|citric|citrus)\b/,
  algodao:/\b(algodao|cotton)\b/
 };
 return !!hints[type]?.test(text);
}
function legacyEvidence(c,type,dir){
 // Histórico IN/OUT funciona como comprovante de expedição/recebimento,
 // nunca como obrigação de encontrar fabricante no mapa.
 if(!c||!Array.isArray(c.old)||!c.old.length||c.old.length>14)return false;
 const distinct=new Set(c.old.map(x=>String(x.unit||x.stem).toLowerCase()));
 if(distinct.size>9)return false; // Bloqueia company genérica cheia de todos os cargos.
 if(LEGACY_INCOMPATIBLE_ROLES.has(c.role))return false;
 const match=c.old.some(x=>x.dir===dir&&
   ((x.unit&&oldCargoCategory(x.unit)===type)||
    (!x.unit&&(oldCargoCategory(x.stem)===type||LEGACY_EVIDENCE[type]?.test(x.stem)))));
 if(!match)return false;
 if(!roleSuitableForSpecificCargo(c,type,dir))return false;
 if(c.role!=="desconhecida"){
  const sectors=flows[type]?.[dir]||[];
  return sectors.includes(c.role);
 }
 // Se o setor do ID é opaco, uma associação ESPECÍFICA de cargo: dentro do SII
 // é evidência direta do tipo de atividade, sem fabricar empresas.
 return c.old.some(x=>x.dir===dir&&x.unit&&oldCargoCategory(x.unit)===type);
}
function getCandidateMap(map){
 const companies=[...map.companies.values()],byRole=new Map();
 for(const c of companies){
  if(!byRole.has(c.role))byRole.set(c.role,[]);
  byRole.get(c.role).push(c);
 }
 return{companies,byRole};
}
function specificFarmCrop(c){
 const value=norm((c.id||"")+" "+(c.name||"")).replace(/[_-]/g," ");
 const special=[
 ["batata",/(?:batata|potato)/],
 ["laranja",/(?:laranja|citrus|orange)/],
 ["algodao",/(?:algodao|cotton)/],
 ["soja",/(?:soja|soybean)/],
 ["milho",/(?:milho|maize|corn)/],
 ["sorgo",/(?:sorgo|sorghum)/]
 ];
 const found=special.filter(([,re])=>re.test(value)).map(([type])=>type);
 return found.length===1?found[0]:null;
}
function roleSuitableForSpecificCargo(c,type,direction){
 // Avalia o ramo e especializações reais, não a existência de uma fábrica.
 if(c.role==="cana"&&SPECIAL_CROPS.has(type))return false;
 if(c.role==="cana"&&type==="adubo")return direction==="in";
 if(c.role==="marmoraria"&&type==="tijolo")return oldSpecificEvidence(c,"tijolo",direction)&&constructionStockEvidence(c).isRetailProfile;
 if(c.role==="fazenda"&&direction==="out"&&SPECIAL_CROPS.has(type)){
  const specific=specificFarmCrop(c);
  // Uma fazenda explicitamente de batatas não vira fornecedora de laranja e milho.
  // Fazenda genérica pode expedir batatas, laranjas ou pluma quando há destinatários reais.
  if(specific&&specific!==type)return false;
 }
 return true;
}

const RELATED_FREIGHT_PATTERNS={
 stone:/^(?:granito|granite|marmore|marble|pedras?|blocos?pedra|lajotas?)$/i,
 stoneReceiver:/^(?:pedras?|marmore|granito|granite|tijolos?|areias?|brita|tubosconcret|pisos?|telhas?|revestimentos?)$/i,
 feed:/^(?:racao|racoes|xerem|farelo|animal_?feed|feedmeal|nutricaoanimal|suplementomineral|salmineral)$/i,
 feedInput:/^(?:milho|soja|sorgo|trigo|graos?|farelo|racao|racoes|feno|alfafa|salmineral|leite)$/i,
 grain:/^(?:milho|soja|sorgo|trigo|cevada|arroz|wheat|corn|soybean|sorghum|grain|graos?)$/i,
 cotton:/^(?:algodao|pluma|cotton|cotton_?bales?)$/i,
 cottonReceive:/^(?:pluma|algodao|cotton|cotton_?bales?|fibra|fios?|tecidos?|adubo|racao|milho|soja)$/i,
 steel:/^(?:bobinas?|steel_?coils?|metal_?coils?|chapaaco|chapasaco|ferroconst|b_reforco|vergalhao|vergalhoes|sumetal|sualuminio|steel|aco)$/i
};
function countRelated(c,dir,pattern){
 return new Set((c.old||[]).filter(x=>x.dir===dir&&pattern.test(String(x.unit||x.stem).toLowerCase()))
  .map(x=>String(x.unit||x.stem).toLowerCase())).size;
}
// IN/OUT é a evidência principal. IDs e nomes servem apenas de contexto.
// A leitura privilegia "cargo:" real; só usa o nome do arquivo se esse campo faltar.
function freightEvidence(c,dir,re){
 const hits=new Set();
 for(const x of c.old||[]){
  if(x.dir!==dir)continue;
  const unit=String(x.unit||x.stem||"").toLowerCase();
  if(re.test(unit))hits.add(unit);
 }
 return hits.size;
}
function relatedCargoCandidate(c,type,dir){
 if(!c||["posto","correios","concessionaria","cana"].includes(c.role))return null;
 const n=(pattern,d=dir)=>freightEvidence(c,d,pattern);
 const exact={
  granito:/^(?:granito|granite|marmore|marble|pedras?)$/i,
  racao:/^(?:racao|racoes|xerem|animal_?feed|feedmeal|salmineral|suplementomineral)$/i,
  sorgo:/^(?:sorgo|sorghum)$/i,
  algodao:/^(?:algodao|pluma|cotton|cotton_?bales?)$/i,
  bobinas_industriais:/^(?:bobinas?|steel_?coils?|metal_?coils?)$/i
 };
 const exactCount=n(exact[type]||/$^/);
 if(exactCount)return{company:c,score:110+exactCount*10,reason:"mercadoria correspondente declarada no "+dir.toUpperCase()+" da própria DEF"};
 let score=0,reason="";
 // Evidência de produtos relacionados: exigir coerência da operação IN e OUT,
 // evitando inventar uma fábrica só por um nome semelhante.
 if(type==="granito"){
  const stone=n(RELATED_FREIGHT_PATTERNS.stone);
  if(dir==="out"&&stone){score=90+stone*5;reason="expedição documentada de rochas similares"}
  if(dir==="in"&&n(RELATED_FREIGHT_PATTERNS.stoneReceiver)>=2){
   score=75+n(RELATED_FREIGHT_PATTERNS.stoneReceiver)*3;reason="recebimento documentado de materiais de construção";
  }
 }
 if(type==="racao"){
  const feed=n(RELATED_FREIGHT_PATTERNS.feed);
  if(feed){score=85+feed*5;reason="movimentação documentada de farelo/insumo para alimentação animal"}
  else if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.feedInput,"in")>=2&&n(RELATED_FREIGHT_PATTERNS.feed,"out")){
   score=75;reason="recebe insumos e expede alimentação animal";
  }
 }
 if(type==="sorgo"){
  if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.grain)>=2&&n(RELATED_FREIGHT_PATTERNS.feedInput,"in")===0){
   score=65;reason="expede múltiplos cereais";
  }
  if(dir==="in"&&n(RELATED_FREIGHT_PATTERNS.grain)){
   score=70;reason="recebe cereais";
  }
 }
 if(type==="algodao"){
  if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.grain)>=2&&n(RELATED_FREIGHT_PATTERNS.feedInput,"in")===0&&c.role==="fazenda"){
   score=55;reason="produção agrícola diversificada, compatibilidade hipotética";
  }
  if(dir==="in"&&n(RELATED_FREIGHT_PATTERNS.cottonReceive)&&["textil","algodoeira","cooperativa"].includes(c.role)){
   score=75;reason="recebe fibras ou mercadorias agrícolas relacionadas";
  }
 }
 if(type==="bobinas_industriais"){
  const steel=n(RELATED_FREIGHT_PATTERNS.steel);
  if(steel>=2){score=88+steel*4;reason="movimentação de vários produtos siderúrgicos"}
  else if(steel&&["siderurgica","metalurgica"].includes(c.role)){
   score=78;reason="produto siderúrgico e setor compatível";
  }
 }
 // Um setor ou catálogo isolado não autoriza frete não presente nem relacionado.
 return score?{company:c,score,reason}:null;
}

const CATEGORY_FALLBACK_LIMITS={granito:{out:6,in:9},racao:{out:5,in:12},sorgo:{out:6,in:9},algodao:{out:6,in:10},bobinas_industriais:{out:6,in:9}};
function relatedCargoFallback(companies,type,dir){
 const limit=CATEGORY_FALLBACK_LIMITS[type]?.[dir]||0;
 if(!limit)return{companies:[],notes:[]};
 const matches=companies.map(c=>relatedCargoCandidate(c,type,dir)).filter(Boolean);
 matches.sort((a,b)=>b.score-a.score||a.company.id.localeCompare(b.company.id));
 const choices=matches.slice(0,limit);
 return{
  companies:choices.map(x=>x.company),
  notes:choices.length?[dir.toUpperCase()+" por categoria: "+choices.map(x=>x.company.id+" ("+x.reason+")").join("; ")]:[]
 };
}

function chooseEndpoints(map,type,spec){
 const {companies,byRole}=getCandidateMap(map);
 const allowed=(c,dir)=>roleSuitableForSpecificCargo(c,type,dir);
 const out=new Set(),inn=new Set(),notes=[],categoryReasons=[];
 const specificOut=[],specificIn=[];
 const hardWrong=new Set(["posto","correios","concessionaria"]);
 for(const c of companies){
   if(hardWrong.has(c.role)||!allowed(c,"out"))continue;
   if(oldSpecificEvidence(c,type,"out")){
     // Setor conhecido incompatível precisa de múltiplos indícios do mesmo ramo.
     const compatible=spec.out.includes(c.role)||
       (["cimento","tijolo","madeira","granito"].includes(type)&&constructionStockEvidence(c).isRetailProfile)||
       c.role==="desconhecida";
     if(compatible)specificOut.push(c);
   }
 }
 for(const c of companies){
   if(hardWrong.has(c.role)||!allowed(c,"in"))continue;
   if(oldSpecificEvidence(c,type,"in")){
     const compatible=spec.in.includes(c.role)||
       (["cimento","tijolo","madeira","granito"].includes(type)&&constructionStockEvidence(c).inCount>=2)||
       c.role==="desconhecida";
     if(compatible)specificIn.push(c);
   }
 }
 // Preferência 1: empresas com evidência do MESMO cargo na DEF.
 // Preferência 2: categoria ou atividade de fato compatível, só se faltar evidência.
 for(const c of specificOut)out.add(c);
 for(const c of specificIn)inn.add(c);
 if(!out.size){
   const related=relatedCargoFallback(companies,type,"out");
   for(const c of related.companies)if(allowed(c,"out"))out.add(c);
   notes.push(...related.notes);
   if(!out.size&&["cimento","tijolo","madeira","granito"].includes(type)){
     for(const c of companies)if(allowed(c,"out")&&categoryOutletCandidate(c,type,"out")){
       out.add(c);
       const proof=constructionStockEvidence(c);
       categoryReasons.push(c.id+": OUT de materiais relacionados ("+[...proof.out].join(", ")+")");
     }
   }
   // Fallback por setor quando a carga não aparece explicitamente na DEF.
   if(!out.size)for(const role of spec.out){
     for(const c of byRole.get(role)||[]){
       if(!allowed(c,"out")||hardWrong.has(c.role))continue;
       if(c.role==="fazenda"&&["milho","soja","sorgo","batata","laranja"].includes(type)&&!farmCargoEvidence(c,type))continue;
       if(c.role==="logistica"&&c.old?.length&&!oldSpecificEvidence(c,type,"out")&&
          !(["cimento","tijolo","madeira","granito"].includes(type)&&categoryOutletCandidate(c,type,"out")))continue;
       if(c.role==="materiais"&&c.old?.length&&!categoryOutletCandidate(c,type,"out")&&!oldSpecificEvidence(c,type,"out"))continue;
       if(c.role==="racoes"&&type!=="racao"&&!oldSpecificEvidence(c,type,"out"))continue;
       if(c.role==="agroinsumos"&&["racao","adubo"].includes(type)&&c.old?.length&&!oldSpecificEvidence(c,type,"out"))continue;
       if(type==="granito"&&["mineracao","pedreira","marmoraria"].includes(c.role)&&c.old?.length){
         const stones=c.old.filter(x=>x.dir==="out").some(x=>/^(pedra|marmore|granito|granite|marble)$/.test(String(x.unit||x.stem).toLowerCase()));
         if(!stones)continue;
       }
       if(type==="bobinas_industriais"&&c.old?.length&&!c.old.some(x=>
         x.dir==="out"&&/^(b_reforco|ferroconst|chapaaco|steel_coils?|metal_coils?|bobinas?)$/i.test(String(x.unit||x.stem))))continue;
       if(type==="cerveja"&&c.old?.length&&!c.old.some(x=>
         x.dir==="out"&&/^(cervejas?|beer|amstel|antarctica|brahma|budweiser|devassa|heineken|schin|skol)$/i.test(String(x.unit||x.stem))))continue;
       if(type==="tijolo"&&c.role==="ceramica"&&c.old?.length&&
           !oldSpecificEvidence(c,"tijolo","out")&&!constructionStockEvidence(c).isRetailProfile)continue;
       if(c.role==="fazenda"&&type==="algodao"&&c.old?.length){
         const crops=c.old.filter(x=>x.dir==="out").map(x=>oldCargoCategory(x.unit||x.stem));
         if(!crops.some(x=>["milho","soja","sorgo","algodao"].includes(x)))continue;
       }
       out.add(c);
     }
   }
 }
 if(!inn.size){
   const related=relatedCargoFallback(companies,type,"in");
   for(const c of related.companies)if(allowed(c,"in"))inn.add(c);
   notes.push(...related.notes);
   if(!inn.size&&["cimento","tijolo","madeira","granito"].includes(type))
      for(const c of companies)if(allowed(c,"in")&&categoryOutletCandidate(c,type,"in"))inn.add(c);
   if(!inn.size)for(const role of spec.in){
     for(const c of byRole.get(role)||[]){
       if(!allowed(c,"in")||hardWrong.has(c.role))continue;
       if(c.role==="logistica"&&c.old?.length&&!oldSpecificEvidence(c,type,"in")&&
           !(["cimento","tijolo","madeira","granito"].includes(type)&&categoryOutletCandidate(c,type,"in")))continue;
       if(c.role==="materiais"&&c.old?.length&&!oldSpecificEvidence(c,type,"in")&&
           !(["cimento","tijolo","madeira","granito"].includes(type)&&categoryOutletCandidate(c,type,"in")))continue;
       if(type==="bobinas_industriais"&&c.old?.length&&!c.old.some(x=>
         x.dir==="in"&&/^(b_reforco|ferroconst|chapaaco|steel_coils?|metal_coils?|bobinas?)$/i.test(String(x.unit||x.stem))))continue;
       if(c.role==="supermercado"&&["batata","laranja","cerveja"].includes(type)&&c.old?.length&&!oldSpecificEvidence(c,type,"in"))continue;
       inn.add(c);
     }
   }
 }
 // Não inferir entrada e saída da MESMA mercadoria na mesma empresa
 // só porque ela já recebe matérias-primas relacionadas.
 // Revendas e depósitos podem ter ambas, ou quando IN explícito existe.
 if(["racao","sorgo","algodao","bobinas_industriais"].includes(type)){
   for(const c of [...inn]){
     if(!out.has(c))continue;
     if(["materiais","logistica","cooperativa"].includes(c.role))continue;
     if(oldSpecificEvidence(c,type,"in"))continue;
     inn.delete(c);
   }
 }
 if(categoryReasons.length)notes.push("expedição compatível por categoria da DEF: "+categoryReasons.join("; "));
 // Confiança: evidência direta > mercadorias da mesma categoria > inferência setorial.
 return{out:[...out],inn:[...inn],notes,categoryReasons,directOut:specificOut.length,directIn:specificIn.length};
}

// Paletes têm distribuição intencionalmente restrita, para não dominarem
// o mercado de fretes por centenas de combinações entre empresas.
// Limites aplicados somente às cargas cujo tipo é palete/paletizado.
// Não alterar cargas paletizadas de mercadoria identificada (ex.: cimento pallet).
const PALLET_MAX_ORIGINS=3;
const PALLET_MAX_DESTINATIONS=6;
const PALLET_MAX_DESTINATIONS_PER_SECTOR=2;
const PALLET_OUT_PATTERN=/(?:^|[^a-z0-9])(?:paletes?|pallets?|supaletes|pallet_?wood|wood_?pallets?)(?:$|[^a-z0-9])/i;
const PALLET_PACKING_PATTERN=/(?:^|[^a-z0-9])(?:paletes?|pallets?|supaletes|caixa_?vazia|embalagens?|caixotes?|pallet_?wood)(?:$|[^a-z0-9])/i;
const PALLET_WOOD_PATTERN=/(?:^|[^a-z0-9])(?:madeira|lumber|wood|tabuas?|ripas?|serragem|sawmill|planks?|toras?)(?:$|[^a-z0-9])/i;
function hasCargoInDirection(company,direction,pattern){
 return(company.old||[]).some(x=>x.dir===direction&&
  pattern.test(String(x.unit||x.stem||"").toLowerCase()));
}
function rankedLimitedCompanies(items,count,score,perSector=Infinity){
 const ranked=[...items].sort((a,b)=>score(b)-score(a)||a.id.localeCompare(b.id));
 const result=[],sectorCount=new Map();
 for(const co of ranked){
  const n=sectorCount.get(co.role)||0;
  if(n>=perSector)continue;
  result.push(co);sectorCount.set(co.role,n+1);
  if(result.length>=count)break;
 }
 return result;
}
function palletEndpoints(map,type){
 const firms=[...map.companies.values()];
 const excludes=new Set(["posto","correios","concessionaria","cana","desconhecida"]);
 const woodRoles=new Set(["madeireira","serraria","paletes"]);
 const recipients=new Set(["cooperativa","logistica","silo","materiais","alimentos","supermercado","racoes","cervejaria","hortifruti","textil"]);
 // Não aceitar transportadora como origem só por trabalhar com transporte:
 // apenas com paletes realmente declarados em OUT pela própria DEF.
 const originCandidates=firms.filter(c=>
  !excludes.has(c.role)&&
  (woodRoles.has(c.role)||
   (c.role==="logistica"&&hasCargoInDirection(c,"out",PALLET_OUT_PATTERN))));
 const sources=rankedLimitedCompanies(originCandidates,PALLET_MAX_ORIGINS,c=>
  (hasCargoInDirection(c,"out",PALLET_OUT_PATTERN)?100:0)+
  (c.role==="madeireira"?60:c.role==="serraria"?55:c.role==="paletes"?50:0)+
  (hasCargoInDirection(c,"out",PALLET_WOOD_PATTERN)?25:0)+
  (hasCargoInDirection(c,"in",PALLET_WOOD_PATTERN)?12:0));
 const sourceIds=new Set(sources.map(c=>c.id));
 const destinationCandidates=firms.filter(c=>
  !sourceIds.has(c.id)&&recipients.has(c.role)&&!excludes.has(c.role));
 const destinations=rankedLimitedCompanies(destinationCandidates,PALLET_MAX_DESTINATIONS,c=>
  (hasCargoInDirection(c,"in",PALLET_OUT_PATTERN)?100:0)+
  (hasCargoInDirection(c,"in",PALLET_PACKING_PATTERN)?45:0)+
  (c.role==="logistica"?25:0)+
  (c.role==="cooperativa"?20:0)+
  (c.role==="materiais"?15:0)+
  (c.role==="supermercado"?12:0)+
  (c.old?.length?8:0),PALLET_MAX_DESTINATIONS_PER_SECTOR);
 const notes=[
  "paletes: origens prioritariamente madeireiras/serrarias; até "+
    PALLET_MAX_ORIGINS+" expedidores e "+PALLET_MAX_DESTINATIONS+
    " recebedores (máx. "+PALLET_MAX_ORIGINS*PALLET_MAX_DESTINATIONS+
    " pares teóricos) para não dominar o mercado",
 ];
 if(type==="paletizado")notes.push("nome da carga genérico: verificar no modelo 3D se são paletes de madeira");
 return{out:sources,inn:destinations,notes,categoryReasons:[],directOut:sources.filter(c=>hasCargoInDirection(c,"out",PALLET_OUT_PATTERN)).length,directIn:destinations.filter(c=>hasCargoInDirection(c,"in",PALLET_OUT_PATTERN)).length};
}

function simulate(map,cargo){
 // Verifica cada empresa PRESENTE no mapa ao iniciar a distribuição.
 // Se houver coincidência exata com empresa SCS, usa o setor do catálogo.
 // Empresas customizadas mantêm a classificação específica do mapa.
 const catalogChecks=consultCatalogForMapDistribution(map);
 const plan=new Map(),skipped=[],proof=[],assumptions=[];
 const grouped={alta:0,baixa:0,outros:0};
 for(const info of cargo.cargos.values()){
  const type=kind(info.name)||(info.id==="carga9"?"bobinas_industriais":null),spec=flows[type],problems=[];
  if(!spec)problems.push("identificação econômica da carga incerta");
  if(!info.body.length)problems.push("sem body_types");
  const allowed=info.body.filter(b=>!info.trailer.size||info.trailer.has(b));
  if(!allowed.length)problems.push("carroceria incompatível");
  const chosen=spec?((type==="paletizado"||type==="palete_vazio")?palletEndpoints(map,type):chooseEndpoints(map,type,spec)):{out:[],inn:[],notes:[]};
  let outs=chosen.out,ins=chosen.inn;
  if(!outs.length&&spec)problems.push("não foi encontrada nenhuma empresa com atividade ou categoria de expedição compatível: "+spec.out.join(" / "));
  if(!ins.length&&spec)problems.push("sem recebedor compatível ou estoque comprovado (setores: "+spec.in.join(" / ")+")");
  if(outs.length===1&&ins.length===1&&outs[0].id===ins[0].id)
   problems.push("única origem e destino são a mesma empresa; nenhuma viagem identificável");
  if(problems.length){skipped.push({id:info.id,name:info.name,problems});continue}
  if(type==="bobinas_industriais")chosen.notes.push("Bobinas 2 tratadas provisoriamente como bobinas industriais; conteúdo 3D não confirmado");
  // A limitação da carga de paletes já consta das observações do setor madeireiro.
  if(outs.every(c=>c.role==="logistica"))chosen.notes.push("expedição baseada em capacidade logística presumida; estoque específico não confirmado");
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
  proof.push({id:info.id,name:info.name,type,origins:outs.length,destinations:ins.length,sourceIds:outs.map(c=>c.id),destIds:ins.map(c=>c.id),notes:chosen.notes,categoryReasons:chosen.categoryReasons||[],directOut:chosen.directOut||0,directIn:chosen.directIn||0,scsSourceIds:outs.filter(c=>c.catalog).map(c=>c.id),scsDestIds:ins.filter(c=>c.catalog).map(c=>c.id)});
 }
 return{plan,skipped,grouped,proof,assumptions,catalogChecks}
}

const cargoSii=id=>"SiiNunit\n{\n cargo_def : ."+id+" {\n  cargo: \"cargo."+id+"\"\n }\n}\n";
async function build(map,cargo,sim){
 const out=new JSZip(),keys=new Set(),generated=new Map(),removed=[];
 async function put(p,v){
  const key=p.toLowerCase();if(keys.has(key))throw Error("Duas definições com mesmo caminho: "+p);
  const bytes=v&&typeof v.async==="function"?await v.async("uint8array"):v;
  keys.add(key);out.file(p,bytes,{createFolders:true});
 }
 for(const [co,ps] of sim.plan){
  for(const dir of ["in","out"])for(const id of ps[dir]){
   const folder=map.companies.get(co)?.folder||co;
   const p="def/company/"+folder+"/"+dir+"/"+id+".sii";
   generated.set(p,cargoSii(id));
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

 const blob=await out.generateAsync({type:"blob",compression:"DEFLATE",compressionOptions:{level:4},streamFiles:true},info=>say("Compactando Company… "+Math.round(info.percent)+"%",62+Math.round(info.percent*.28)));
 const check=await JSZip.loadAsync(blob,{createFolders:false});
 for(const p of generated.keys()){
  const obj=check.file(p);
  if(!obj)throw Error("Faltou carga gerada: "+p);
  if(!/cargo\s*:\s*"cargo\./i.test(await obj.async("text")))throw Error("Cargo não registrado corretamente em "+p);
 }
 const generatedLower=new Set([...generated.keys()].map(p=>p.toLowerCase()));
 for(const p of removed)if(check.file(p)&&!generatedLower.has(p.toLowerCase()))throw Error("Cargo original permaneceu no arquivo: "+p);
 for(const x of map.files.values())if(companyMeta(x.p)?.type==="editor"&&!check.file(x.p))throw Error("Arquivo editor perdido: "+x.p);
 return{blob,count:generated.size,removed:removed.length}
}
function audit(map,cargo,sim){
 const companies=[...map.companies.values()],assigned=[...sim.plan.values()].reduce((n,p)=>n+p.in.size+p.out.size,0);
 const warning=[];
 if(sim.grouped.baixa===0)warning.push("Grade baixa sem ofertas verificadas neste mapa. As cargas incompatíveis não foram inventadas.");
 if(sim.grouped.alta===0)warning.push("Grade alta sem ofertas verificadas neste mapa. As cargas incompatíveis não foram inventadas.");
 const unknown=companies.filter(c=>c.role==="desconhecida").length;
 const assignedCompanies=companies.filter(c=>sim.plan.get(c.id)?.out?.size).length;
 const exampleUnknown=companies.filter(c=>c.role==="desconhecida").slice(0,24).map(c=>c.id);
 const inferred=companies.filter(c=>c.evidence==="combinação IN/OUT anterior").length;
 const matched=sim.catalogChecks?.matched??companies.filter(c=>c.catalog).length;
 const inspected=sim.catalogChecks?.consulted??companies.length;
 warning.push("Catálogo conferido somente nas "+inspected+" empresas existentes na DEF; "+matched+" correspondências exatas com empresas padrão SCS.");
 if(unknown)warning.push(unknown+" empresas sem atividade identificada.");
 if(inferred)warning.push(inferred+" empresas classificadas por produtos históricos IN/OUT, além dos nomes e IDs.");
 const manual=companies.filter(c=>c.evidence==="classificação informada pelo usuário").length;
 if(manual)warning.push(manual+" empresas classificadas manualmente.");
 if(!assignedCompanies)warning.push("Nenhum ponto real de expedição foi encontrado. Confira a DEF do mapa.");
 if(!cargo.manifests.length)warning.push("DEF sem arquivo de registro cargo.*.sii identificado.");
 const reasons=new Map();
 for(const item of sim.skipped)for(const reason of item.problems)reasons.set(reason,(reasons.get(reason)||0)+1);
 const ranked=[...reasons].sort((a,b)=>b[1]-a[1]);
 const roles=new Map();
 for(const item of companies)roles.set(item.role,(roles.get(item.role)||0)+1);
 ui.report.innerHTML="<div class='metrics'>"+
 [["Empresas",companies.length],["Cargas do Librelato",cargo.cargos.size],["Sem rota validada",sim.skipped.length],["Observações técnicas",sim.assumptions.length],["Grade baixa",sim.grouped.baixa],["Grade alta",sim.grouped.alta],["Relações IN/OUT",assigned]]
 .map(([t,v])=>"<div class='metric'><span>"+escapeHTML(t)+"</span><strong>"+v+"</strong></div>").join("")+"</div>"+
 (warning.length?"<p class='warning'>"+warning.map(escapeHTML).join("<br>")+"</p>":"")+
 (ranked.length?"<details class='creator-catalog'><summary>Motivos das cargas sem rota ("+sim.skipped.length+")</summary>"+ranked.map(([reason,count])=>"<div class='audit'><b>"+count+"x</b><span>"+escapeHTML(reason)+"</span></div>").join("")+"</details>":"")+
 "<p class='muted'>Empresas reconhecidas por atividade: "+
 [...roles].filter(([k])=>k!=="desconhecida").sort((a,b)=>b[1]-a[1]).map(([role,n])=>escapeHTML(role)+": "+n).join(" · ")+
 ". Empresas ainda sem classificação (amostra): "+escapeHTML(exampleUnknown.join(", "))+ ". Não reconhecer a atividade de uma empresa não significa que ela não tenha cargas no mundo real.</p>";
 const catalogCompanies=companies.filter(c=>c.catalog);
 const catalogSummary="<details class='creator-catalog'><summary>Empresas do mapa identificadas pela base SCS ("+catalogCompanies.length+")</summary>"+
 catalogCompanies.slice(0,120).map(c=>"<div class='creator-catalog-row'><b>"+escapeHTML(c.folder||c.id)+"</b><span>"+escapeHTML(c.catalog.name+" · "+c.catalog.role+" · "+c.catalog.matchBy)+"</span><a href='"+escapeHTML(SCS_REFERENCE_URLS[c.catalog.source]||SCS_REFERENCE_URLS.wiki)+"' target='_blank' rel='noopener noreferrer'>Fonte</a></div>").join("")+
 (catalogCompanies.length>120?"<p class='muted'>Exibindo os primeiros 120. O relatório TXT contém todos os registros.</p>":"")+
 "</details>";
 ui.detail.innerHTML="<details><summary>Conferir relações detalhadas das cargas</summary>"+
 "<p class='muted'>Cargas distribuídas (expedidores → recebedores): "+sim.proof.map(p=>escapeHTML(p.name)+": "+p.origins+" → "+p.destinations).join("; ")+"</p>"+
 "<p class='muted'>Exemplos de relações do mapa (não garante oferta no ETS2):</p>"+
 sim.proof.map(p=>"<div class='audit'><b>"+escapeHTML(p.name)+"</b><span>OUT: "+escapeHTML(p.sourceIds.slice(0,6).join(", "))+" | IN: "+escapeHTML(p.destIds.slice(0,6).join(", "))+"</span></div>").join("")+
 (sim.assumptions.length?"<details class='creator-catalog'><summary>Observações técnicas das cargas ("+sim.assumptions.length+")</summary><p class='muted'>São interpretações ainda não confirmadas, não impedimentos de geração.</p>"+sim.assumptions.map(p=>"<div class='audit'><b>"+escapeHTML(p.id)+"</b><span>"+escapeHTML(p.notes.join("; "))+"</span></div>").join("")+"</details>":"")+
 (sim.skipped.length?"<details class='creator-catalog'><summary>Cargas ainda sem rota verificada ("+sim.skipped.length+")</summary>"+sim.skipped.map(x=>"<div class='audit'><b>"+escapeHTML(x.id+" — "+x.name)+"</b> <span>"+escapeHTML(x.problems.join(", "))+"</span></div>").join("")+"</details>":"")+
 "</details>"+catalogSummary;
}

let latestDiagnostic=null;
function createDiagnosticText(map,cargo,sim){
 const rows=[
  "ETS2 COMPANY LOGISTICS - DIAGNÓSTICO DE ARQUIVOS",
  "Catálogo consultado: "+SCS_COMPANY_CATALOG.length+" referências; somente para classificar empresas existentes.",
  "Empresas existentes na DEF consultadas no catálogo durante a distribuição: "+(sim.catalogChecks?.consulted??map.companies.size),
  "Empresas padrão reconhecidas entre elas: "+(sim.catalogChecks?.matched??0),
  "Referências cargo: lidas dos arquivos IN/OUT: "+(map.parsedRelations||0),
  "Empresas: "+map.companies.size,
  "Cargas personalizadas do Librelato: "+cargo.cargos.size,
  "Empresas com evidência de revenda de materiais (IN/OUT): "+[...map.companies.values()].filter(c=>!!c.supplyProof).map(c=>c.id).join(", "),
  "Definições de carroceria: "+[...cargo.cargos.values()].map(c=>c.id+" = "+(c.body.join("|")||"SEM BODY_TYPES")).join(", "),
  "",
  "EMPRESAS (ID | SETOR IDENTIFICADO | EVIDÊNCIA | CARGAS IN ANTIGAS | CARGAS OUT ANTIGAS)"
 ];
 for(const c of map.companies.values()){
  const ins=c.old.filter(x=>x.dir==="in").map(x=>x.stem);
  const outs=c.old.filter(x=>x.dir==="out").map(x=>x.stem);
  rows.push([c.id,c.role,c.evidence||"nenhuma",ins.join(","),outs.join(","),"categorias IN: "+[...(c.categories?.in||new Map())].map(x=>x.join("=")).join(","),"categorias OUT: "+[...(c.categories?.out||new Map())].map(x=>x.join("=")).join(",")].join(" | "));
 }
 rows.push("","CARGAS REJEITADAS (ID | NOME | MOTIVOS)");
 for(const x of sim.skipped)rows.push([x.id,x.name,x.problems.join("; ")].join(" | "));
 rows.push("","CARGAS LIBERADAS E RAZÕES (ID | NOME | EXPEDIDORES | RECEBEDORES | HIPÓTESES)");
 for(const p of sim.proof)rows.push([p.id,p.name,p.sourceIds.join(","),p.destIds.join(","),p.notes.join("; "),"origens SCS: "+p.scsSourceIds.join(","),"destinos SCS: "+p.scsDestIds.join(",")].join(" | "));
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
let lastCompany=null;
function updateDownloadUI(){
 if(!ui.download)return;
 ui.download.disabled=!lastCompany||busy;
 ui.download.hidden=!lastCompany;
 if(ui.downloadInfo)ui.downloadInfo.textContent=lastCompany?
   "Company pronta: "+lastCompany.filename+" ("+lastCompany.count+" relações IN/OUT). Clique para baixar.":
   "Gere e valide a Company para liberar o download.";
}
function clearCompanyDownload(){
 lastCompany=null;
 updateDownloadUI();
}
function downloadCompany(){
 if(!lastCompany||busy){say("Primeiro gere uma Company válida para habilitar o download.",0);return}
 const {blob,filename}=lastCompany;
 const url=URL.createObjectURL(blob),a=document.createElement("a");
 try{
  a.href=url;
  a.download=filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  say("Download solicitado: "+filename+". Confira a pasta Downloads do navegador.",100);
 }finally{setTimeout(()=>URL.revokeObjectURL(url),60000)}
}
async function generate(){
 if(busy)return;
 const one=ui.map.files?.[0],two=ui.cargo.files?.[0];
 if(!one||!two){say("Anexe a Company do mapa e a DEF das cargas do Librelato.",0);return}
 busy=true;ui.run.disabled=true;clearCompanyDownload();ui.report.innerHTML="";ui.detail.innerHTML="";latestDiagnostic=null;
 try{
  say("Identificando empresas do mapa…",8);
  const map=await loadMap(await zipRead(one));applyCompanyOverrides(map);await yieldUI();
  say("Identificando cargas e carrocerias…",28);
  const cargo=await loadCargo(await zipRead(two));if(!cargo.cargos.size)throw Error("A DEF do Librelato não contém unidades cargo_data reconhecidas.");
  say("Simulando logística…",43);const sim=simulate(map,cargo);audit(map,cargo,sim);
  latestDiagnostic=createDiagnosticText(map,cargo,sim);const diag=el("companyCreateSaveDiagnostic");if(diag)diag.hidden=false;
  if(!sim.plan.size)throw Error("Nenhuma relação IN/OUT válida encontrada. Consulte o diagnóstico de empresas e cargas; o site não gera pacotes vazios.");
  // Não inventar fretes para completar uma grade ausente neste mapa.
  // Exporta somente as ofertas compatíveis e informa a limitação no diagnóstico.
  say("Criando DEF Company completa…",60);
  const out=await build(map,cargo,sim);
  const clean=(one.name.replace(/\.(scs|zip)$/i,"").replace(/[^a-z0-9_-]/gi,"_").slice(0,40)||"Mapa");
  const fingerprint=await mapFingerprint(map);
  // Arquivos chamados def_company.zip em mapas distintos não sobrescrevem o resultado.
  const identifier=clean+"_"+fingerprint;
  lastCompany={
   blob:out.blob,
   filename:"DEF_Company_Librelato_"+identifier+"_Universal.scs",
   count:out.count,
   removed:out.removed
  };
  updateDownloadUI();
  say("Company pronta: "+out.count+" associações IN/OUT, "+map.companies.size+" empresas analisadas, "+map.archivesRead+" arquivo(s) interno(s) processado(s). Grade baixa: "+sim.grouped.baixa+"; grade alta: "+sim.grouped.alta+". Clique em Baixar Company .SCS.",100);
 }catch(e){say("Erro: "+(e?.message||String(e)),0)}
 finally{busy=false;ui.run.disabled=false;updateDownloadUI()}
}
ui.run.addEventListener("click",generate);
if(ui.download)ui.download.addEventListener("click",downloadCompany);
if(el("companyCreateSaveDiagnostic"))el("companyCreateSaveDiagnostic").addEventListener("click",downloadDiagnostic);
for(const id of ["companyCreateMapFile","companyCreateCargoFile"])el(id).addEventListener("change",()=>{clearCompanyDownload();const input=el(id),label=el(id+"Name");label.textContent=input.files?.[0]?.name||"Selecione um arquivo ZIP/SCS";say("Arquivo selecionado.",0)});
if(el("companyCreateOverrides"))el("companyCreateOverrides").addEventListener("input",clearCompanyDownload);
updateDownloadUI();

function renderSCSCatalog(){
 const input=el("companyCreateCatalogSearch"),root=el("companyCreateCatalogResults");
 if(!root)return;
 const query=scsKey(input?.value);
 const rows=SCS_COMPANY_CATALOG.filter(c=>!query||scsKey(c.name+" "+c.role).includes(query));
 root.innerHTML="<p class='muted'>"+rows.length+" de "+SCS_COMPANY_CATALOG.length+" referências. Apenas metadados: nenhum ID é adicionado ao SCS.</p>"+
 rows.slice(0,75).map(c=>"<div class='creator-catalog-row'><b>"+escapeHTML(c.name)+"</b><span>"+escapeHTML(c.role)+"</span><a href='"+escapeHTML(SCS_REFERENCE_URLS[c.source]||SCS_REFERENCE_URLS.wiki)+"' target='_blank' rel='noopener noreferrer'>Fonte</a></div>").join("")+
 (rows.length>75?"<p class='muted'>Mostrando as primeiras 75. Use a busca para filtrar.</p>":"");
}
if(el("companyCreateCatalogSearch"))el("companyCreateCatalogSearch").addEventListener("input",renderSCSCatalog);
renderSCSCatalog();

window.CompanyCreatorTest={kind,known,relatedCargoCandidate,relatedCargoFallback,inferRoleFromHistoricalFreights,createDiagnosticText,companyPath,cargoPath,companyMeta,flows,loadMap,loadCargo,simulate,build,scsCatalogLookup,SCS_COMPANY_CATALOG,oldCargoCategory,catalogForMapCompany,consultCatalogForMapDistribution,resolveEntries,isZipMagic,discoverBareCompanyRoots,mapFingerprint};
})();
