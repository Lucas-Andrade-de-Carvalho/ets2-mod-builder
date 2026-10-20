
(function(){
"use strict";
const el=id=>document.getElementById(id),ui={map:el("companyCreateMapFile"),cargo:el("companyCreateCargoFile"),run:el("companyCreateGenerate"),message:el("companyCreateStatus"),bar:el("companyCreateBar"),report:el("companyCreateReport"),detail:el("companyCreateDetail"),download:el("companyCreateDownload"),downloadInfo:el("companyCreateDownloadInfo")};
const ENGINE_BUILD="2026-10-20 · CONTEXTO ECONÔMICO AUDITÁVEL · v6.0";
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
 // O catálogo fornece contexto, mas nunca apaga uma classificação manual
 // ou uma atividade já corrigida por provas mais fortes do IN/OUT.
 if(company.evidence==="classificação informada pelo usuário"||
    company.evidence?.startsWith("categoria agroinsumos inferida de OUT")||
    company.evidence?.startsWith("movimentação IN/OUT"))
   return reference;
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
["premoldados",/(pre.?moldad|precast|fabrica de pre moldad)/],
["calhas",/(fabrica de calhas|fabricante de calhas|calharia|industria de calhas)/],
["reciclagem",/(reciclador|reciclagem|recupera(?:cao|dora) de paletes|reaproveitamento de madeira)/],
["agroinsumos",/(loja agropecuaria|casa agropecuaria|agropecuaria comercial|comercio agropecuario)/],
["algodoeira",/(beneficiadora de algodao|fazenda algodoeira|unidade de beneficiamento de algodao)/],
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
 sorgo:{out:["fazenda","agroinsumos","cooperativa","silo","logistica"],in:["cooperativa","silo","racoes","pecuaria","fazenda","logistica"]},
 adubo:{out:["adubeira","agroinsumos","logistica"],in:["fazenda","cana","pecuaria","agroinsumos","logistica"]},
 madeira:{out:["madeireira","serraria","floresta","materiais","logistica"],in:["obras","madeireira","materiais","logistica"]},
 algodao:{out:["fazenda","algodoeira","logistica"],in:["cooperativa","algodoeira","textil","logistica"]},
 cimento:{out:["materiais","logistica","cimenteira"],in:["obras","materiais","logistica","premoldados"]},
 batata:{out:["fazenda","hortifruti","alimentos","logistica"],in:["supermercado","hortifruti","alimentos","logistica"]},
 laranja:{out:["fazenda","hortifruti","alimentos","logistica"],in:["supermercado","hortifruti","alimentos","logistica"]},
 cerveja:{out:["cervejaria","bebidas","alimentos","logistica"],in:["bebidas","supermercado","alimentos","logistica"]},
 tijolo:{out:["materiais","logistica","ceramica"],in:["obras","materiais","logistica"]},
 granito:{out:["pedreira","mineracao","marmoraria","materiais","logistica"],in:["obras","marmoraria","materiais","logistica"]},
 racao:{out:["racoes","logistica","alimentos"],in:["fazenda","pecuaria","logistica","alimentos"]},
 aco:{out:["siderurgica","metalurgica","materiais","logistica"],in:["metalurgica","obras","materiais","logistica"]},
 bobinas_industriais:{out:["siderurgica","metalurgica","logistica"],in:["metalurgica","calhas","obras","logistica"]},
 // Paletes vazios: fabricantes e operadores logísticos expedem, várias empresas recebem.
 palete_vazio:{out:["madeireira","serraria","paletes","supermercado","alimentos","materiais","logistica","bebidas","cervejaria","hortifruti","cooperativa","racoes","metalurgica"],in:["reciclagem","paletes","madeireira","logistica","cooperativa","silo","materiais","alimentos","supermercado","racoes","cervejaria","hortifruti","textil"]},
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
 ["premoldados",/^(premold|pre.?mold|fabricapremold)/],
 ["calhas",/^(calhas?|fabricacalhas?|fabricantecalhas?)/],
 ["reciclagem",/^(reciclagem|reciclador|recuperadorapalet|recicladoramadeira)/],
 ["agroinsumos",/^(lojaagropec|casaagropec|comercioagropec)/],
 ["algodoeira",/^(algodoeira|beneficiadoraalgodao)/],
 ["metalurgica",/^(cofer|centroaco|distribuidoraco)/],
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
const ALLOWED_ROLES=new Set(["cooperativa","madeireira","cana","marmoraria","agroinsumos","mineracao","logistica","fazenda","silo","pecuaria","racoes","moinho","adubeira","serraria","floresta","textil","algodoeira","ceramica","cimenteira","pedreira","obras","materiais","cervejaria","bebidas","supermercado","hortifruti","alimentos","siderurgica","metalurgica","paletes","posto","concessionaria","correios","premoldados","calhas","reciclagem"]);
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
 if(/\b(?:bobinas?|steel[ _-]?coils?|metal[ _-]?coils?)\b/i.test(x))return "bobinas_industriais";
 // Sementes de algodão não são pluma de algodão beneficiada.
 if(/\b(?:sementes?|seeds?)\b/.test(x)&&/\b(?:algodao|cotton)\b/.test(x))return null;
 // Produto TESTE de paletes sem indicação de vazios/embalagem não é
 // prova de expedição de paletes vazios ou carga paletizada.
 if(/\b(?:teste|test)\b/.test(x)&&/\b(?:paletes?|pallets?)\b/.test(x))return null;
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
// Limites combinados: um ZIP pequeno também pode declarar gigabytes de
// arquivos expandidos. Rejeitar ANTES de descompactar evita travar o navegador.
const ARCHIVE_LIMITS=Object.freeze({
 maxDepth:3,
 maxNestedFiles:32,
 maxEntries:120000,
 maxNestedBytes:320*1024*1024,
 maxExpandedBytes:800*1024*1024,
 maxSingleEntryBytes:150*1024*1024,
 maxCargoDefinitionBytes:1024*1024
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
 let entryCount=0,nestedCount=0,skippedHashFS=0,expandedBytes=0;
 const isRelevant=kind==="map"?companyPath:cargoPath;
 while(stack.length){
  const frame=stack.pop();
  const nested=[];
  const bareRoots=kind==="map"?discoverBareCompanyRoots(frame.zip):null;
  let matchedHere=0;
  for(const [raw,obj] of Object.entries(frame.zip.files)){
   if(obj.dir)continue;
   if(++entryCount>ARCHIVE_LIMITS.maxEntries)throw Error("Pacote muito grande: limite de "+ARCHIVE_LIMITS.maxEntries+" entradas alcançado. Selecione só a DEF do mapa.");
   const declaredSize=obj._data?.uncompressedSize;
   if(Number.isFinite(declaredSize)){
    if(declaredSize>ARCHIVE_LIMITS.maxSingleEntryBytes)
     throw Error("Arquivo expandido grande demais para uma DEF: "+raw);
    expandedBytes+=declaredSize;
    if(expandedBytes>ARCHIVE_LIMITS.maxExpandedBytes)
     throw Error("ZIP expandido supera 800 MB. Separe apenas as definições necessárias, sem modelos ou texturas.");
   }
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
 ["granito",/(?:^|[_ ]|\.)(?:granite|granitto|granito|marble|marmore)(?:$|[_ ]|\.)/],
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
  const values=x.units?.length?x.units:[x.unit].filter(Boolean);
  if(!values.length){
   x.category=null;
   if(x.dir==="in")result.unknownIn++;else result.unknownOut++;
   continue;
  }
  for(const unit of values){
   const role=oldCargoCategory(unit);
   if(!x.category)x.category=role;
   if(role)result[x.dir].set(role,(result[x.dir].get(role)||0)+1);
   else if(x.dir==="in")result.unknownIn++;else result.unknownOut++;
  }
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

// Interpreta campos cargo: respeitando comentários de linha/bloco e strings.
// Devolve offsets para desativar permissões sem destruir outros campos SII.
function maskSiiComments(source){
 // Offsets de regex e slice são posições UTF-16. Spread([...text]) usa
 // pontos de código e perde alinhamento em SII com emoji/caracteres raros.
 const text=String(source),chars=text.split("");let quote="",line=false,block=false;
 for(let i=0;i<text.length;i++){
  const ch=text[i],next=text[i+1];
  if(line){
   if(ch==="\n"){line=false;continue}
   if(ch!=="\r")chars[i]=" ";
   continue;
  }
  if(block){
   if(ch==="*"&&next==="/"){chars[i]=" ";chars[i+1]=" ";i++;block=false;continue}
   if(ch!=="\n"&&ch!=="\r")chars[i]=" ";
   continue;
  }
  if(quote){
   if(ch==="\\"){i++;continue}
   if(ch===quote)quote="";
   continue;
  }
  if(ch==='"'||ch==="'"){quote=ch;continue}
  if(ch==="/"&&next==="/"){chars[i]=" ";chars[i+1]=" ";i++;line=true;continue}
  if(ch==="/"&&next==="*"){chars[i]=" ";chars[i+1]=" ";i++;block=true;continue}
 }
 return chars.join("");
}
function scanCompanyCargoFields(source){
 const clean=maskSiiComments(source),fields=[];
 const re=/(^|[{\n\r])(\s*cargo\s*:\s*)(?:"[^"\r\n]*"|'[^'\r\n]*'|[^\s}\r\n]+)/gmi;
 let match;
 while((match=re.exec(clean))){
  const start=match.index+match[1].length+match[2].length;
  const literal=match[0].slice(match[1].length+match[2].length);
  const value=literal.replace(/^["']|["']$/g,"").trim();
  fields.push({start,end:start+literal.length,value});
 }
 return fields;
}
function parseCompanyCargoUnits(source,path){
 const fields=scanCompanyCargoFields(source),units=[];
 for(const field of fields){
  if(!field.value)continue; // cargo: "" neutraliza a permissão.
  const m=field.value.match(/^cargo\.([a-z0-9_]+)$/i);
  if(!m)throw Error("Referência cargo: inválida em "+path+": "+field.value.slice(0,80));
  units.push(m[1].toLowerCase());
 }
 return [...new Set(units)];
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
  if(m.type==="in"||m.type==="out")c.old.push({p,dir:m.type,stem:m.name.replace(/\.sii$/i,""),unit:null,units:[],category:null});
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
 let parsedRelations=0,scannedRelations=0,withoutCargo=0;
 const relationsByPath=new Map();
 for(const c of companies.values())for(const item of c.old)
  relationsByPath.set(item.p.toLowerCase(),item);
 for(const item of files.values()){
  const m=companyMeta(item.p);
  if(!m||(m.type!=="in"&&m.type!=="out"))continue;
  const size=item.obj._data?.uncompressedSize||0;
  if(size>ARCHIVE_LIMITS.maxCargoDefinitionBytes)
   throw Error("Definição IN/OUT grande demais para interpretar com segurança: "+item.p);
  const raw=await item.obj.async("text");
  if(raw.length>ARCHIVE_LIMITS.maxCargoDefinitionBytes)
   throw Error("Definição IN/OUT excede limite após extração: "+item.p);
  const units=parseCompanyCargoUnits(raw,item.p);
  const relation=relationsByPath.get(item.p.toLowerCase());
  if(relation){
   relation.units=units;
   relation.unit=units[0]||null;
   parsedRelations+=units.length;
   if(!units.length)withoutCargo++;
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

 return{companies,files,parsedRelations,withoutCargo,catalogMatched:[...companies.values()].filter(c=>c.catalog).length,archivesRead:resolution.nestedCount}
}
// Uma DEF pode conter mercadorias adicionais, externas ao reboque.
// Prioridade de escopo: @include do manifesto > modelos físicos
// vehicle/cargo/<id> > todos os cargos quando não há identificação.
// Não depender de nomes "carga1"..."carga23" ou de um mapa específico.
async function selectTrailerCargoScope(files,cargos,manifests){
 const included=new Set(),visual=new Set();
 const includeRe=/^\s*@include\s+["']([^"'\r\n]+)["']/gmi;
 for(const entry of files.values()){
  const folder=entry.p.toLowerCase();
  const m=folder.match(/^def\/vehicle\/cargo\/([a-z0-9_]+)\//i);
  if(m)visual.add(m[1].toLowerCase());
 }
 for(const name of manifests){
  const entry=files.get(name.toLowerCase());if(!entry)continue;
  const content=await entry.obj.async("text");
  let m;
  while((m=includeRe.exec(content))){
   const raw=m[1].replace(/\\/g,"/").replace(/^\/+/,"");
   const path=raw.replace(/^def\//i,"").replace(/^\.\//,"").toLowerCase();
   const unit=path.match(/^cargo\/([a-z0-9_]+)\.(?:sii|sui)$/);
   if(unit)included.add(unit[1]);
  }
  includeRe.lastIndex=0;
 }
 const manifestMatches=[...included].filter(x=>cargos.has(x));
 const visualMatches=[...visual].filter(x=>cargos.has(x));
 const chosen=manifestMatches.length?new Set(manifestMatches):
   visualMatches.length?new Set(visualMatches):null;
 const strategy=manifestMatches.length?"manifesto @include":
   visualMatches.length?"modelos físicos vehicle/cargo":"sem manifesto/modelo (todas as definições)";
 const excluded=[];
 if(chosen)for(const [id,c] of [...cargos]){
  if(chosen.has(id))continue;
  excluded.push({id,name:c.name,reason:"não declarado no "+strategy});
  cargos.delete(id);
 }
 return{strategy,excluded,manifestMatches:manifestMatches.length,
  vehicleMatches:visualMatches.length,declared:included.size};
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
  if((f.obj._data?.uncompressedSize||0)>500000)
   throw Error("Definição cargo_data extensa demais para leitura confiável: "+f.p);
  const txt=await f.obj.async("text"),p=f.p;
  if(txt.length>500000)throw Error("Definição cargo_data extensa demais para leitura confiável: "+p);
  if(/^def\/cargo\.[a-z0-9_-]+\.sii$/i.test(p))manifests.push(p);
  const id=(txt.match(/\bcargo_data\s*:\s*cargo\.([a-z0-9_]+)/i)||[])[1];
  if(id&&/^[a-z][a-z0-9_]*$/i.test(id)){
   let label=(txt.match(/^\s*name\s*:\s*"([^"]+)"/mi)||[])[1]||"";
   let unresolvedName=!label||label.includes("@@");
   // IDs semanticamente explícitos (não cargoN) podem identificar três
   // mercadorias padronizadas da DEF, mesmo quando locale @@ não está presente.
   // Não aplicar esta regra a IDs genéricos do reboque ou produtos ambíguos.
   const semanticLabels={corn_b:"Milho",soybean_b:"Soja",potatoes_b:"Batata"};
   if(unresolvedName&&Object.hasOwn(semanticLabels,id.toLowerCase())){
    label=semanticLabels[id.toLowerCase()];
    unresolvedName=false;
   }
   if(unresolvedName)label="Mercadoria não identificada ("+id+")";
   const bs=[...txt.matchAll(/^\s*body_types\s*(?:\[\s*\d*\s*\])?\s*:\s*["']?([a-z0-9_]+)/gim)].map(x=>x[1].toLowerCase());
   if(cargos.has(id.toLowerCase()))
    throw Error("ID de cargo_data duplicado em arquivos diferentes: "+
      id+" ("+cargos.get(id.toLowerCase()).path+" e "+p+")");
   cargos.set(id.toLowerCase(),{id:id.toLowerCase(),unit:"cargo."+id.toLowerCase(),name:label,unresolvedName,body:[...new Set(bs)],path:p});
  }
  const ca=p.match(/^def\/cargo\/([a-z0-9_]+)\//i);
  if(ca&&/\btrailer_def\s*:/i.test(txt)){
   const bs=[...txt.matchAll(/^\s*body_type\s*:\s*["']?([a-z0-9_]+)/gim)].map(x=>x[1].toLowerCase());
   if(!trailer.has(ca[1]))trailer.set(ca[1],new Set());
   for(const b of bs)trailer.get(ca[1]).add(b)
  }
  if((++i)%100===0)await yieldUI();
 }
 const scope=await selectTrailerCargoScope(files,cargos,manifests);
 for(const c of cargos.values())c.trailer=trailer.get(c.id)||new Set();
 return{files,cargos,manifests,archivesRead:resolution.nestedCount,scope}
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
  if(specific&&specific!==type){
   // Nome como "rocasoja" não é monocultura comprovada: a DEF pode mostrar
   // várias culturas efetivas no OUT e fertilizantes no IN.
   const diversified=type==="algodao"&&
     freightEvidence(c,"out",/^(?:milho|soja|feijao|graos?|corn|soybeans?|rice)$/i)>=2&&
     freightEvidence(c,"in",/^(?:fertilizer|adubo|fertilizante|big_bag_seed)$/i)>=1&&
     freightEvidence(c,"in",/^(?:milho|soja|feijao|graos?|corn|soybeans?|rice)$/i)===0;
   if(!diversified)return false;
  }
 }
 return true;
}

const RELATED_FREIGHT_PATTERNS={
 stone:/^(?:granito|granitto|granite|marmore|marble|marble_blocks?|stones?|pedras?|pedra_?granito|blocos?_?pedra|lajotas?)$/i,
 stoneReceiver:/^(?:pedras?|marmore|granito|granite|tijolos?|areias?|brita|tubosconcret|pisos?|telhas?|revestimentos?)$/i,
 feed:/^(?:racao|racoes|xerem|farelo|bran|animal_?feed|feedmeal|nutricaoanimal|suplementomineral|salmineral)$/i,
 feedInput:/^(?:milho|soja|sorgo|trigo|graos?|farelo|racao|racoes|feno|alfafa|salmineral|leite)$/i,
 grain:/^(?:milho|soja|sorgo|trigo|cevada|arroz|wheat|maize|corn|soybeans?|sorghum|grain|grains|graos?)$/i,
 cotton:/^(?:algodao|pluma|cotton|cotton_?bales?)$/i,
 cottonReceive:/^(?:pluma|algodao|cotton|cotton_?bales?|fibra|fios?|tecidos?|adubo|racao|milho|soja)$/i,
 steel:/^(?:bobinas?|steel_?coils?|metal_?coils?|chapa_?aco|chapas?aco|ferroconst|b_reforco|vergalhao|vergalhoes|sumetal|sualuminio|steel|aco|rolled_steel)$/i
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
// O perfil é montado com mercadorias reais dos IN/OUT; entradas cargo.cargaN
// de DEFs genéricas não são evidência independente de estoque.
function detailedMovement(c){
 const inGoods=new Set(),outGoods=new Set();
 for(const entry of c.old||[]){
  const unit=String(entry.unit||entry.stem||"").toLowerCase();
  if(/^carga[0-9]+$/.test(unit))continue;
  (entry.dir==="in"?inGoods:outGoods).add(unit);
 }
 return{inGoods,outGoods};
}
function isGenericCompanyMap(map){
 let count=0,generic=0,unparsed=0;
 for(const c of map.companies.values())for(const e of c.old||[]){
  count++;
  if(/^carga[0-9]+$/i.test(String(e.unit||e.stem||"")))generic++;
  if(!e.unit)unparsed++;
 }
 return{count,generic,unparsed,share:count?generic/count:0};
}
// Evidência econômica do próprio mapa (208 empresas / 6.739 OUT / 7.088 IN).
// Mercadorias observadas: stones, gravel, iron_pipes, scrap_metals,
// metal_center, hmetal, graos, milho, soja, fertilizer e big_bag_seed.
// Não confundir produtos relacionados com cargo idêntico: marcar hipóteses.
function realMapEconomicCandidate(c,type,dir){
 if(!c||["posto","correios","concessionaria","cana"].includes(c.role))return null;
 const inCount=(re)=>freightEvidence(c,"in",re);
 const outCount=(re)=>freightEvidence(c,"out",re);
 const isOut=dir==="out";
 const size=(c.old||[]).length;
 const grain=/^(?:graos?|milho|soja|feijao|corn|maize|soybeans?|rice|rice_c|wheat|barley)$/i;
 const metal=/^(?:iron_pipes|largetubes|metal_center|hmetal|steel|steel_?coils?|scrap_metals|wallpanels|sandwch_pnls)$/i;
 const stone=/^(?:stones?|granito|granitto|granite|marble|marmore|pedras?)$/i;
 const stoneOut=outCount(stone),stoneIn=inCount(stone);
 const grainOut=outCount(grain),grainIn=inCount(grain);
 const stockOut=outCount(/^(?:big_bag_seed|fertilizer|fertilizante|adubo|young_seed)$/i);
 const fieldIn=inCount(/^(?:fertilizer|fertilizante|adubo|big_bag_seed|young_seed)$/i);
 let score=0,reason="";
 if(type==="granito"){
  if(isOut&&stoneOut&&outCount(/^(?:gravel|sand|areia|ore|coal|calcario)$/i)){
   score=98;reason="OUT stones + material mineral (origem de pedra; granito específico é inferência)";
  }else if(!isOut&&stoneIn){
   score=96;reason="IN stones/pedra registrado na DEF (granito específico é inferência)";
  }else if(!isOut&&size<55&&
   ["obras","materiais","logistica","desconhecida"].includes(c.role)&&
   inCount(/^(?:cement|concrete|bricks|precast_strs|iron_pipes|wallpanels|floorpanels|roof_tiles)$/i)>=2){
   score=74;reason="IN de múltiplos materiais de construção compatíveis com fornecimento de pedra";
  }
 }
 if(type==="racao"){
  const feed=outCount(/^(?:racao|racoes|xerem|animal_?feed|feedmeal|farelo|salmineral|suplementomineral)$/i);
  const feedIn=inCount(/^(?:racao|racoes|xerem|animal_?feed|feedmeal|farelo|salmineral|suplementomineral)$/i);
  if(isOut&&feed){score=120;reason="OUT de ração/alimento animal comprovado";}
  else if(!isOut&&feedIn){score=120;reason="IN de ração/alimento animal comprovado";}
  else if(isOut&&size<50&&grainIn>=2&&grainOut>=1&&stockOut>=1){
   score=81;reason="comércio/cooperativa agrícola recebe grãos e expede grãos/insumos (ração inferida, não documentada)";
  }else if(isOut&&size<50&&grainIn>=2&&stockOut>=2){
   score=77;reason="revenda agropecuária recebe grãos e expede fertilizantes/sementes (ração inferida)";
  }else if(!isOut&&size<50&&
   outCount(/^(?:bois|beef3|beef_meat|milk|leite|goat_cheese)$/i)>=1&&
   (inCount(/^(?:big_bag_seed|young_seed|graos|milho|soja|granel|plant_substr)$/i)>=1||
    c.role==="pecuaria"||c.role==="fazenda")){
   score=86;reason="criação animal/produção pecuária comprovada no OUT e insumos no IN (ração inferida)";
  }
 }
 if(type==="algodao"){
  const cotton=/^(?:cotton|cotton_bales?|pluma|algodao)$/i;
  if(isOut&&outCount(cotton)){score=120;reason="OUT algodão/pluma comprovado";}
  else if(!isOut&&inCount(cotton)){score=120;reason="IN algodão/pluma comprovado";}
  else if(isOut&&size<40&&grainOut>=2&&fieldIn>=1&&grainIn===0&&
   !["silo","cooperativa","logistica"].includes(c.role)){
   score=66;reason="lavoura diversificada: múltiplos grãos no OUT e insumos no IN (algodão não comprovado)";
  }else if(!isOut&&size<45&&grainIn>=2&&grainOut>=2&&fieldIn>=1&&
    ["cooperativa","silo","fazenda","desconhecida"].includes(c.role)){
   score=64;reason="cooperativa agrícola movimenta múltiplas culturas (recebimento de pluma é hipótese)";
  }
 }
 if(type==="bobinas_industriais"){
  const finishedOut=outCount(/^(?:iron_pipes|largetubes|metal_center|hmetal|wallpanels|sandwch_pnls)$/i);
  const finishedIn=inCount(/^(?:iron_pipes|largetubes|metal_center|hmetal|wallpanels|sandwch_pnls)$/i);
  const scrap=outCount(/^(?:scrap_metals)$/i);
  if(isOut&&size<70&&
   (finishedOut>=2||(finishedOut>=1&&scrap>=1))&&
    (finishedIn>=1||["metalurgica","siderurgica"].includes(c.role))){
   score=91;reason="OUT e IN de produtos metálicos industriais (bobinas específicas não confirmadas)";
  }else if(!isOut&&size<80&&finishedIn>=2){
   score=84;reason="recebe múltiplos produtos metálicos industriais (bobinas inferidas)";
  }else if(!isOut&&size<70&&finishedIn>=1&&
    ["metalurgica","siderurgica","obras","materiais"].includes(c.role)){
   score=77;reason="recebe material metálico para beneficiamento/obra (bobinas inferidas)";
  }
 }
 return score?{company:c,score,reason}:null;
}
function relatedCargoCandidate(c,type,dir){
 if(!c||["posto","correios","concessionaria","cana"].includes(c.role))return null;
 const n=(pattern,d=dir)=>freightEvidence(c,d,pattern);
 const exact={
  granito:/^(?:granito|granitto|granite|marmore|marble|marble_blocks?|pedras?|pedra_?granito)$/i,
  racao:/^(?:racao|racoes|xerem|animal_?feed|feedmeal|salmineral|suplementomineral)$/i,
  sorgo:/^(?:sorgo|sorghum)$/i,
  algodao:/^(?:algodao|pluma|cotton|cotton_?bales?)$/i,
  bobinas_industriais:/^(?:bobinas?|steel_?coils?|metal_?coils?)$/i
 };
 const exactCount=n(exact[type]||/$^/);
 if(exactCount)return{company:c,score:110+exactCount*10,reason:"mercadoria correspondente declarada no "+dir.toUpperCase()+" da própria DEF"};
 const economic=realMapEconomicCandidate(c,type,dir);
 if(economic)return economic;
 let score=0,reason="";
 // Evidência de produtos relacionados: exigir coerência da operação IN e OUT,
 // evitando inventar uma fábrica só por um nome semelhante.
 if(type==="granito"){
  const stone=n(RELATED_FREIGHT_PATTERNS.stone);
  if(dir==="out"&&stone){score=90+stone*5;reason="expedição documentada de rochas similares"}
  else if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.stone,"in")&&
   n(/^(?:cimento|cement|tijolos?|bricks?|pisos?|telhas?|tubosconcret|calhas|madeira|ferroconst)$/i,"out")>=2&&
   ["materiais","logistica","desconhecida","obras"].includes(c.role)){
    score=76;reason="revenda: recebe rochas e expede outros materiais de construção";
  }
  if(dir==="in"&&n(RELATED_FREIGHT_PATTERNS.stoneReceiver)>=2){
   score=75+n(RELATED_FREIGHT_PATTERNS.stoneReceiver)*3;reason="recebimento documentado de materiais de construção";
  }
 }
 if(type==="racao"){
  const feed=n(RELATED_FREIGHT_PATTERNS.feed);
  if(feed){score=85+feed*5;reason="movimentação documentada de farelo/insumo para alimentação animal"}
  else if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.feed,"in")&&
   n(/^(?:adubo|fertilizante|fertilizer|sementes?|equipagrico|farelo|salmineral)$/i,"out")>=2&&
   ["agroinsumos","cooperativa","racoes","logistica","desconhecida"].includes(c.role)){
    score=75;reason="revenda agropecuária: recebe ração e expede vários insumos relacionados";
  }
  else if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.feedInput,"in")>=2&&n(RELATED_FREIGHT_PATTERNS.feed,"out")){
   score=75;reason="recebe insumos e expede alimentação animal";
  }
 }
 if(type==="sorgo"){
  if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.grain)>=2){
   score=65;reason="expede múltiplos cereais";
  }
  if(dir==="in"&&n(RELATED_FREIGHT_PATTERNS.grain)){
   score=70;reason="recebe cereais";
  }
 }
 if(type==="algodao"){
  const farmEvidence=c.role==="fazenda"||
   (n(RELATED_FREIGHT_PATTERNS.grain,"out")>=2&&
    n(/^(?:adubo|fertilizante|fertilizer|ureia|seeds?|sementes?)$/i,"in")>=1&&
    n(RELATED_FREIGHT_PATTERNS.grain,"in")===0);
  if(dir==="out"&&n(RELATED_FREIGHT_PATTERNS.grain)>=2&&farmEvidence){
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

function chooseEndpoints(map,type,spec,cargoId=""){
 const {companies,byRole}=getCandidateMap(map);
 const allowed=(c,dir)=>roleSuitableForSpecificCargo(c,type,dir);
 const out=new Set(),inn=new Set(),notes=[],categoryReasons=[];
 const specificOut=[],specificIn=[];
 const hardWrong=new Set(["posto","correios","concessionaria","cana"]);
 // A prova de cargo específico nos IN/OUT da DEF supera rótulos comerciais,
 // salvo os setores explicitamente incompatíveis acima.
 const genericStats=isGenericCompanyMap(map);
 // Não tratar permissões da DEF genérica (cargo.cargaN) como prova econômica
 // quando elas dominam o arquivo de origem.
 const exactCargo=(c,dir)=>Boolean(cargoId)&&genericStats.share<0.50&&c.old?.some(x=>
   x.dir===dir&&String(x.unit||"").toLowerCase()===cargoId.toLowerCase());
 const hasDirect=(c,dir)=>exactCargo(c,dir)||oldSpecificEvidence(c,type,dir);
 const certified=(c,dir)=>Boolean(relatedCargoCandidate(c,type,dir)?.score>=100);

 for(const c of companies){
   if(hardWrong.has(c.role)||!allowed(c,"out"))continue;
   if(hasDirect(c,"out"))specificOut.push(c);
 }
 for(const c of companies){
   if(hardWrong.has(c.role)||!allowed(c,"in"))continue;
   if(hasDirect(c,"in"))specificIn.push(c);
 }
 // Preferência 1: empresas com evidência do MESMO cargo na DEF.
 // Preferência 2: categoria ou atividade de fato compatível, só se faltar evidência.
 for(const c of specificOut)out.add(c);
 for(const c of specificIn)inn.add(c);
 if(!out.size){
   const related=relatedCargoFallback(companies,type,"out");
   for(const c of related.companies)if(allowed(c,"out")&&!hardWrong.has(c.role))out.add(c);
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
       if(c.role==="racoes"&&type!=="racao"&&!hasDirect(c,"out"))continue;
       if(c.role==="agroinsumos"&&["racao","adubo"].includes(type)&&c.old?.length&&!hasDirect(c,"out")&&!certified(c,"out"))continue;
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
   for(const c of related.companies)if(allowed(c,"in")&&!hardWrong.has(c.role))inn.add(c);
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
     // Uma empresa que recebe e expede material pode ter ambos os papéis.
     // Só remova o IN inferido quando não existir outro expedidor distinto;
     // caso contrário a regra apagava TODOS os recebedores de bobinas.
     if([...out].some(source=>source.id!==c.id))continue;
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

// Segundo avaliador independente, voltado a empresas sem nomes descritivos.
// Pontua pares de mercadorias observadas nos dois sentidos e nunca inventa
// qualquer empresa ou cargo. As cargas não declaradas literalmente são hipóteses.
function evidenceFromRealFlows(map,type,dir){
 const grains=/^(?:graos?|milho|soja|feijao|beans|corn|maize|soybeans?|rice|rice_c|wheat|barley)$/i;
 const seeds=/^(?:big_bag_seed|fertilizer|fertilizante|adubo|young_seed)$/i;
 const stones=/^(?:stones?|granito|granitto|granite|marble|marmore|pedras?)$/i;
 const minerals=/^(?:gravel|sand|areia|ore|coal)$/i;
 const building=/^(?:cement|concrete|iron_pipes|largetubes|wallpanels|floorpanels|roof_tiles|precast_strs|gravel|sand|bricks|concr_beams|logs|sawpanels)$/i;
 const metals=/^(?:iron_pipes|largetubes|metal_center|hmetal|wallpanels|sandwch_pnls)$/i;
 const livestock=/^(?:beef3|beef_meat|milk|leite|wool|cattle)$/i;
 const forbidden=new Set(["posto","correios","concessionaria","cana"]);
 const cap={granito:{out:9,in:8},racao:{out:9,in:8},algodao:{out:4,in:5},bobinas_industriais:{out:4,in:8}};
 if(!cap[type])return{companies:[],notes:[]};
 const matches=[];
 for(const c of map.companies.values()){
  if(forbidden.has(c.role))continue;
  const size=c.old?.length||0;
  const n=(direction,re)=>freightEvidence(c,direction,re);
  const out=re=>n("out",re),inn=re=>n("in",re);
  let score=0,reason="";
  if(type==="granito"){
   if(dir==="out"&&size<=58&&out(stones)&&out(minerals)){
    score=95+4*out(stones)+out(minerals);
    reason="OUT documentado de pedras e agregados minerais; granito exato é hipótese";
   }else if(dir==="in"&&size<=100&&(inn(stones)||(!out(stones)&&inn(building)>=3))){
    score=85+3*inn(stones)+inn(building);
    reason="IN documentado de pedras ou múltiplos materiais de construção";
   }
  }else if(type==="racao"){
   if(dir==="out"&&size<=48&&inn(grains)>=2&&out(grains)>=1&&out(seeds)>=1){
    score=90+out(grains)+inn(grains);
    reason="recebe grãos e expede sementes/insumos; comercialização de ração inferida";
   }else if(dir==="in"&&size<=50&&out(livestock)>=1&&(inn(seeds)+inn(grains))>=1){
    score=90+inn(seeds)+inn(grains);
    reason="pecuária documentada no OUT e insumos agrícolas no IN";
   }
  }else if(type==="algodao"){
   if(dir==="out"&&size<=39&&out(grains)>=2&&inn(seeds)>=1&&inn(grains)===0){
    score=87+out(grains);
    reason="lavoura diversificada, com insumos IN e culturas OUT; algodão inferido";
   }else if(dir==="in"&&size<=48&&out(grains)>=2&&inn(grains)>=2&&inn(/^(?:fertilizer|adubo|fertilizante)$/i)>=1){
    score=84+inn(grains);
    reason="cooperativa agrícola com entrada de múltiplas culturas; pluma inferida";
   }
  }else if(type==="bobinas_industriais"){
   if(dir==="out"&&size<=79&&out(metals)>=2&&inn(metals)>=1){
    score=95+out(metals);
    reason="OUT/IN de múltiplos produtos metalúrgicos; bobinas específicas inferidas";
   }else if(dir==="in"&&size<=79&&inn(metals)>=2&&out(stones)===0){
    score=88+inn(metals);
    reason="IN documentado de diversos produtos metálicos industriais";
   }
  }
  if(score)matches.push({company:c,score,reason});
 }
 matches.sort((a,b)=>b.score-a.score||a.company.id.localeCompare(b.company.id));
 // Priorizar pontos com mercadorias realmente específicas, sem transformar
 // operadores genéricos com centenas de permissões em produtores.
 const chosen=matches.slice(0,cap[type][dir]);
 return{
  companies:chosen.map(x=>x.company),
  notes:chosen.length?[dir.toUpperCase()+" por perfil de estoque observado: "+
    chosen.map(x=>x.company.id+" ("+x.reason+")").join("; ")]:[]
 };
}
// O mesmo algoritmo para qualquer mapa: primeiro CADA empresa, depois
// cada carga da DEF do reboque. Nenhuma lista de nomes de mapas ou IDs fixos.
const UNIVERSAL_FREIGHT={
 grain:/^(?:milho|corn|maize|maiz|soja|soybeans?|soya|sorgo|sorghum|graos?|grain|grains|trigo|wheat|rice|arroz|feijao|beans|barley)$/i,
 fertilizer:/^(?:adubo|fertilizantes?|fertilizers?|big_bag_seed|seeds?|sementes?|young_seed|ureia)$/i,
 stone:/^(?:stones?|pedras?|granito|granitto|granite|marble|marmore|gravel|sand|areia|ore|limestone|calcario)$/i,
 building:/^(?:cement|cimento|concrete|bricks?|tijolos?|iron_pipes|largetubes|wallpanels|floorpanels|roof_tiles|precast_strs|concr_beams|gravel|stones?|wood|lumber|sandwch_pnls|metal_center|hmetal)$/i,
 metal:/^(?:steel|steel_coils?|metal_coils?|bobinas?|rolled_steel|hmetal|metal_center|iron_pipes|largetubes|ferroconst|chapaaco|chapa_aco|scrap_metals|wallpanels|sandwch_pnls)$/i,
 livestock:/^(?:beef3|beef_meat|milk|leite|bois|gado|cattle|wool|sheep|lamb|meat|goat_cheese)$/i,
 fruit:/^(?:oranges?|laranjas?|apples?|potatoes?|batatas?|carrots?|tomatoes?|pears?|citrus|naranjas?)$/i,
 wood:/^(?:logs?|timber|lumber|madeira|wood|boards?|planks?|toras?|wood_pallets?|sawpanels)$/i,
 feed:/^(?:racao|racoes|animal_feed|feedmeal|farelo|xerem|salmineral|suplementomineral)$/i,
 pallets:/^(?:empty_palet|empty_pallet|pallets?|paletes?|used_packag|wood_pallets?)$/i
};
function companyCargoProfile(c){
 // Fontes do perfil: SOMENTE cargo: real, não nome de empresa ou .sii.
 const groups={in:new Set(),out:new Set()},declared={in:new Set(),out:new Set()};
 for(const item of c.old||[]){
  if(!groups[item.dir])continue;
  const values=item.units?.length?item.units:[item.unit].filter(Boolean);
  for(const value of values){
   const token=String(value).toLowerCase().replace(/^cargo[.:]/,"").trim();
   if(!token||/^carga\d+$/i.test(token))continue;
   groups[item.dir].add(token);
   declared[item.dir].add(token);
  }
 }
 const count=(dir,re)=>[...groups[dir]].filter(x=>re.test(x)).length;
 return{...groups,declared,count,total:groups.in.size+groups.out.size};
}
// Uma mercadoria isolada em cargo: pode ser erro do mapa. Só contrariar
// um ramo altamente especializado com múltiplos indícios IN/OUT independentes.
const SPECIALIZED_ROLES=new Set([
 "posto","concessionaria","correios","cana",
 "siderurgica","metalurgica","cervejaria","pedreira","mineracao",
 "marmoraria","cimenteira","ceramica","racoes","algodoeira","textil",
 "fazenda","pecuaria","moinho","serraria","floresta","adubeira"
]);
const ECONOMIC_FAMILIES={
 agro:{
  graos:/^(?:corn|maize|milho|soja|soybeans?|sorgo|sorghum|graos?|grain|grains|wheat|trigo|feijao|beans|rice|arroz)$/i,
  adubos:/^(?:adubo|fertilizer|fertilizante|fertilizantes|fertilizers|ureia|urea)$/i,
  sementes:/^(?:big_bag_seed|young_seed|seeds?|sementes?)$/i,
  implementos:/^(?:equipagrico|tractors?|plantadeiras?|agricultural_?machines?)$/i,
  racoes:/^(?:racao|racoes|animal_?feed|feedmeal|farelo|xerem|salmineral)$/i,
  pecuaria:/^(?:milk|leite|beef3|beef_meat|cattle|gado|wool|meat)$/i,
  frutas:/^(?:orange|oranges|laranja|laranjas|potato|potatoes|batata|batatas)$/i,
  algodao:/^(?:cotton|cotton_bales?|algodao|pluma)$/i
 },
 metal:{
  siderurgia:/^(?:steel|aco|steel_?coils?|metal_?coils?|bobinas?|ferroconst|metal_center|hmetal|chapaaco|chapa_aco)$/i,
  metalurgia:/^(?:iron_pipes|largetubes|scrap_metals|sumetal|sualuminio|b_reforco)$/i,
  maquinario:/^(?:machinery|machine_parts|metal_parts|engine_parts)$/i
 },
 mineral:{
  pedras:/^(?:stones?|granito|granite|marmore|marble|pedra|pedras)$/i,
  agregados:/^(?:gravel|sand|areia|brita|limestone|calcario|ore)$/i
 },
 construcao:{
  cimento:/^(?:cimento|cement|concrete|concr_beams)$/i,
  ceramica:/^(?:bricks?|tijolos?|roof_tiles|floorpanels)$/i,
  materiais:/^(?:wallpanels|precast_strs|iron_pipes|largetubes|gravel|stones?|sandwch_pnls)$/i
 },
 madeira:{
  toras:/^(?:logs?|toras?|wood|timber)$/i,
  derivados:/^(?:lumber|madeira|planks?|boards?|sawpanels)$/i,
  paletes:/^(?:pallets?|paletes?|wood_pallets?)$/i
 },
 bebidas:{
  cervejas:/^(?:beer|beer_c|cervejas?|cerveza)$/i,
  bebidas:/^(?:beverages|beverages_c|bottle_water|limonades)$/i
 },
 combustivel:{
  combustiveis:/^(?:diesel|gasoline|petrol|fuel|combustivel)$/i,
  petroquimica:/^(?:oil|crude_oil|fuel_tank|petroleum)$/i
 },
 automotivo:{
  veiculos:/^(?:cars?|new_cars?|vehicles?|car_parts)$/i,
  autopecas:/^(?:tires?|tyres?|spare_parts|auto_parts)$/i
 },
 encomendas:{
  correspondencia:/^(?:mail|letters?|packages?|parcels?|post)$/i
 }
};
const ROLE_FAMILY={
 posto:"combustivel",concessionaria:"automotivo",correios:"encomendas",
 cana:"agro",siderurgica:"metal",metalurgica:"metal",cervejaria:"bebidas",
 pedreira:"mineral",mineracao:"mineral",marmoraria:"mineral",
 cimenteira:"construcao",ceramica:"construcao",racoes:"agro",
 algodoeira:"agro",textil:"agro",fazenda:"agro",pecuaria:"agro",
 moinho:"agro",serraria:"madeira",floresta:"madeira",adubeira:"agro"
};
const CARGO_FAMILY={
 milho:"agro",soja:"agro",sorgo:"agro",adubo:"agro",racao:"agro",
 algodao:"agro",batata:"agro",laranja:"agro",
 cimento:"construcao",tijolo:"construcao",granito:"mineral",
 aco:"metal",bobinas_industriais:"metal",madeira:"madeira",
 cerveja:"bebidas",palete_vazio:"madeira",paletizado:"madeira"
};
function familyEvidence(profile,family){
 const variants=ECONOMIC_FAMILIES[family]||{};
 const groups=new Set(),tokens={in:[],out:[]};
 const declared=profile.declared||profile;
 for(const dir of ["in","out"]){
  for(const unit of declared[dir]||[]){
   for(const [label,re] of Object.entries(variants)){
    if(!re.test(unit))continue;
    groups.add(label);tokens[dir].push(unit);break;
   }
  }
 }
 return{groups,tokens};
}
function economicCoherence(company,profile,type,dir){
 const sector=company.role||"desconhecida";
 const target=CARGO_FAMILY[type],specialist=ROLE_FAMILY[sector];
 const sectors=flows[type]?.[dir]||[];
 // Uma fazenda pode receber fertilizante; uma siderúrgica produz aço.
 // Fora de um conflito especializado, o cargo: continua sendo evidência.
 if(!SPECIALIZED_ROLES.has(sector)||!specialist||!target||
   specialist===target||sectors.includes(sector))
  return{allowed:true,reason:"setor compatível ou não especializado"};
 const support=familyEvidence(profile,target);
 const original=familyEvidence(profile,specialist);
 const coherent=support.groups.size>=3&&
  support.tokens.in.length>0&&support.tokens.out.length>0;
 // Evidência de atividade concorrente mantém o bloqueio. Para catálogo
 // SCS oficialmente identificado, jamais substituir sua atividade automaticamente.
 const contradictory=original.groups.size>0||Boolean(company.catalog);
 const allowed=coherent&&!contradictory;
 return{allowed,reason:allowed?
   "IN/OUT demonstram várias famílias de produtos de uma atividade alternativa":
   "incompatibilidade com ramo especializado ("+sector+"); "+
    support.groups.size+" categorias relacionadas, "+
    (support.tokens.in.length?"IN presente":"IN ausente")+", "+
    (support.tokens.out.length?"OUT presente":"OUT ausente")+
    (contradictory?"; há evidência do ramo original ou catálogo SCS":"")};
}
function companyCargoCompatibility(c,profile,type,dir,info,anomalies){
 const n=profile.count,f=UNIVERSAL_FREIGHT;
 if(!profile[dir].size)return null;
 // SEMPRE examinar a DEF antes de olhar o rótulo da empresa.
 // Nome, ID e catálogo são sugestões, não veto sobre cargo: verdadeiro.
 const declared=profile.declared?.[dir]||new Set();
 const signature=findProductEvidence(profile,type,dir);
 // Compartilhar um identificador numérico entre mods não comprova produto.
 const direct=signature.level==="especifica"; // A categoria antiga não prova equivalência física (cotton ≠ pluma, chapas ≠ bobinas).
 const coherence=economicCoherence(c,profile,type,dir);
 if(!coherence.allowed){
  // Registrar toda contradição literal, não mascarar como rota.
  if(direct&&Array.isArray(anomalies))anomalies.push({
   company:c.id,role:c.role,cargo:info.id,direction:dir,reason:coherence.reason
  });
  return null;
 }
 if(direct){
  const roles=flows[type]?.[dir]||[];
  const mismatch=c.role!=="desconhecida"&&roles.length&&!roles.includes(c.role);
  return{score:120,kind:"direta",roleConflict:!!mismatch,
   reason:"cargo: documentado no "+dir.toUpperCase()+
     (mismatch?" (atividade econômica reavaliada: "+coherence.reason+")":"")};
 }
 // O nome do arquivo nunca cria permissão de frete.
 // Evitar extrapolar um operador genérico com quase todo o catálogo.
 if(profile.total>=95)return null;
 const outs=re=>n("out",re),ins=re=>n("in",re);
 let reason="",score=0; switch(type){
  case "milho":case "soja":case "sorgo":
   if(dir==="out"&&outs(f.grain)>=2&&ins(f.fertilizer)>0&&ins(f.grain)===0){
    score=72;reason="lavoura com diversos grãos expedidos e insumos recebidos";
   }else if(dir==="in"&&ins(f.grain)>=2){
    score=70;reason="recebimento documentado de grãos";
   }break;
  case "adubo":
   if(dir==="out"&&outs(f.fertilizer)>=2&&ins(f.fertilizer)>=1){
    score=74;reason="revenda de insumos agrícolas";
   }else if(dir==="in"&&ins(f.fertilizer)>=1&&outs(f.grain)>=2){
    score=74;reason="propriedade agrícola recebendo insumos";
   }break;
  case "madeira":
   if(dir==="out"&&outs(f.wood)&&outs(f.building)>=2){
    score=74;reason="madeira expedida com materiais de construção";
   }else if(dir==="in"&&ins(f.building)>=3){
    score=67;reason="recebimento documentado de materiais de obra";
   }break;
  case "cimento":case "tijolo":
   if(dir==="out"&&outs(f.building)>=3&&ins(f.building)>=1){
    score=70;reason="revenda de materiais de construção";
   }else if(dir==="in"&&ins(f.building)>=3){
    score=68;reason="obra ou depósito recebe múltiplos materiais";
   }break;
  case "granito":
   if(dir==="out"&&outs(f.stone)>=2){
    score=76;reason="expedição de vários materiais minerais, granito é inferência";
   }else if(dir==="in"&&ins(f.building)>=3){
    score=69;reason="recebe materiais de construção compatíveis com granito";
   }break;
  case "racao":
   if(dir==="out"&&ins(f.grain)>=2&&outs(f.grain)>=1&&outs(f.fertilizer)>=1){
    score=75;reason="distribuidor agrícola recebe grãos e expede insumos; ração inferida";
   }else if(dir==="in"&&outs(f.livestock)>=1&&ins(f.fertilizer)>=1){
    score=77;reason="pecuária documentada recebe insumos; ração inferida";
   }break;
  case "algodao":
   if(dir==="out"&&outs(f.grain)>=2&&ins(f.fertilizer)>=1&&ins(f.grain)===0){
    score=60;reason="lavoura diversificada com insumos, pluma não comprovada";
   }else if(dir==="in"&&ins(f.grain)>=2&&outs(f.grain)>=2&&ins(f.fertilizer)>=1){
    score=61;reason="entreposto/cooperativa agrícola, pluma inferida";
   }break;
  case "bobinas_industriais":case "aco":
   if(dir==="out"&&outs(f.metal)>=2&&ins(f.metal)>=1){
    score=77;reason="movimenta produtos metálicos em ambos os sentidos";
   }else if(dir==="in"&&ins(f.metal)>=2){
    score=75;reason="recebe diversos produtos metalúrgicos";
   }break;
  case "batata":case "laranja":
   if(dir==="out"&&outs(f.fruit)>=3&&ins(f.fruit)===0){
    score=65;reason="produção hortifrutícola diversificada";
   }else if(dir==="in"&&ins(f.fruit)>=2){
    score=65;reason="comércio recebe produtos hortifrutícolas";
   }break;
  case "palete_vazio":case "paletizado":
   if(dir==="out"&&outs(f.wood)>0&&ins(f.wood)>0&&
    ["madeireira","serraria","paletes"].includes(c.role)){
    score=69;reason="expede madeira e recebe matéria-prima para paletes";
   }else if(dir==="in"&&ins(f.pallets)>0){
    score=72;reason="recebe paletes ou embalagens";
   }break;
 }
 return score?{score,kind:"inferida",reason}:null;
}
// Assistente de inteligência logística explicável. Conhecimento referenciado,
// local/offline por padrão. Com conexão consulta automaticamente a base pública
// do próprio projeto, NUNCA envia o mapa nem as empresas para a internet.
const OFFLINE_LOGISTICS_KNOWLEDGE=Object.freeze({"schema":1,"version":"2026-10-20-v6","title":"Base documental de inteligência logística ETS2","reviewed":"2026-10-20","disclaimer":"Regras de cadeia produtiva não comprovam que uma empresa específica existe ou opera determinada mercadoria. Validar com IN/OUT reais.","sources":[{"id":"embrapa_graos","agency":"Embrapa Territorial","title":"Bacias logísticas do escoamento de soja e milho","url":"https://www.embrapa.br/en/web/territorial/macrologistica/sistema/bacias-logisticas","types":["milho","soja","sorgo"],"fact":"Soja e milho possuem origens produtoras, armazenagem e rotas de escoamento; armazenagem não comprova produção na empresa."},{"id":"embrapa_racao","agency":"Embrapa","title":"Nutrição de aves e formas de obtenção de rações","url":"https://www.atermaisdigital.cnptia.embrapa.br/web/frango/nutricao/racao","types":["racao"],"fact":"Milho, farelo de soja e núcleos podem compor rações; uma fábrica precisa de processo de mistura/formulação. Receber milho não prova expedir ração."},{"id":"embrapa_algodao","agency":"Embrapa","title":"Cultura do algodão no Cerrado — beneficiamento","url":"https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1155388/1/Cultura-do-Algodao-no-Cerrado-1.pdf","types":["algodao"],"fact":"Algodão colhido é beneficiado em algodoeiras (separação fibra/semente), então a pluma enfardada segue para mercados consumidores e indústria têxtil. Fazenda de grãos não demonstra expedição de pluma."},{"id":"aco_brasil","agency":"Instituto Aço Brasil","title":"Processo siderúrgico e laminação","url":"https://www.acobrasil.org.br/site/processo-siderurgico/","types":["bobinas_industriais","aco"],"fact":"Produção e laminação transformam semiacabados em produtos siderúrgicos. Movimentação de tubos ou sucata isoladamente não comprova produção de bobinas."},{"id":"abcp_cimento","agency":"ABCP","title":"Cadeia produtiva do cimento e do concreto","url":"https://abcp.org.br/abcp-lab-referencia-tecnica-para-a-cadeia-produtiva-do-cimento/","types":["cimento","tijolo","granito"],"fact":"O cimento integra a construção; produção industrial, revenda e consumo em obras têm papéis econômicos diferentes."},{"id":"embrapa_fertilizante","agency":"Embrapa Hortaliças","title":"Adubos e fertilizantes","url":"https://www.embrapa.br/web/agencia-de-informacao-tecnologica/cultivos/pimenta/pre-producao/insumos/adubos-e-fertilizantes","types":["adubo"],"fact":"Fertilizantes são insumos aplicados na produção agrícola. Uma fazenda pode recebê-los, mas produzi-los requer outra atividade."},{"id":"embrapa_cotton_pluma","agency":"Embrapa Algodão","title":"Algodão em pluma","url":"https://www.infoteca.cnptia.embrapa.br/infoteca/handle/doc/659531","types":["algodao"],"fact":"Fibras de algodão são beneficiadas e enfardadas antes de comercialização para indústria têxtil; algodão em caroço não é automaticamente pluma."},{"id":"florestal_madeira","agency":"Serviço Florestal Brasileiro","title":"Monitoramento e rastreabilidade da madeira: floresta, toras e serraria","url":"https://www.gov.br/florestal/pt-br/assuntos/concessoes-e-monitoramento/monitoramento-das-concessoes-florestais","types":["madeira"],"fact":"Fluxo florestal desde transporte de toras da floresta até beneficiamento na serraria e movimentação de madeira serrada. Mover madeira serrada requer evidência do produto correspondente."},{"id":"ceagesp_hortifruti","agency":"CEAGESP","title":"Entreposto Terminal São Paulo: frutas, hortaliças e abastecimento","url":"https://ceagesp.gov.br/entrepostos/etsp/","types":["laranja","batata"],"fact":"Entrepostos recebem e comercializam frutas, legumes e verduras de múltiplos municípios; fazendas produzem, atacadistas distribuem e supermercados recebem."},{"id":"mapa_cerveja","agency":"Ministério da Agricultura","title":"Cadeia produtiva da cerveja no Brasil","url":"https://www.gov.br/agricultura/pt-br/assuntos/camaras-setoriais-tematicas/camaras-setoriais-1/cerveja-1","types":["cerveja"],"fact":"Cervejarias, distribuidores e varejo ocupam funções diferentes; OUT de bebidas genéricas não comprova cervejas específicas."},{"id":"receita_paletes","agency":"Receita Federal","title":"Unidades de carga, embalagens e paletes","url":"https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/despacho-de-importacao/sistemas/siscomex-importacao-web/declaracao-de-importacao/funcionalidades/ficha-carga/unidades-de-carga-x-embalagens-x-volumes-peso-bruto-x-peso-liquido","types":["paletizado","palete_vazio"],"fact":"Paletes podem ser unidade de carga retornável ou embalagem que acompanha mercadorias. Um estabelecimento com cargas paletizadas não é necessariamente produtor ou expedidor de paletes vazios."},{"id":"aco_produtos_planos","agency":"Instituto Aço Brasil","title":"Produtos planos: chapas e bobinas de aço","url":"https://www.acobrasil.org.br/site/produtos/","types":["bobinas_industriais","aco"],"fact":"Bobinas integram a classe de produtos planos obtidos por laminação; tubos, arames e sucata pertencem a produtos/processos distintos e não comprovam movimentação de bobinas."},{"id":"embrapa_fabrica_racao","agency":"Embrapa","title":"Produção de feno, silagem e ração em sistemas ILPF","url":"https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1128581/1/ProducaoFenoSilagemRacaoSistemaILPF.pdf","types":["racao"],"fact":"A formulação de ração requer processamento e mistura de ingredientes; receber milho, soja ou insumos isoladamente não comprova expedição de ração pronta."},{"id":"embrapa_sorgo_bovinos","agency":"Embrapa Gado de Corte","title":"Sorgo granífero na alimentação de bovinos","url":"https://cloud.cnpgc.embrapa.br/sac/2016/05/24/como-usar-o-sorgo-granifero-e-o-sorgo-forrageiro-na-alimentacao-de-bovinos/","types":["sorgo","racao"],"fact":"O sorgo granífero é ingrediente para alimentação animal; não deve ser identificado como ração industrial pronta nem atribuído como cultura produzida sem evidência."}],"policies":{"noFabricatedBusinesses":true,"noForcedCoverage":true,"readMapCargoFirst":true,"noNameOnly":true,"cottonPlumaRequiresEvidence":true,"steelCoilsRequireEvidence":true,"feedProducerRequiresEvidence":true}});
const RESEARCH_DATA_URL="https://raw.githubusercontent.com/Lucas-Andrade-de-Carvalho/ets2-mod-builder/main/logistics_knowledge.json";
const RESEARCH_HOSTS=new Set(["cloud.cnpgc.embrapa.br","www.embrapa.br","www.atermaisdigital.cnptia.embrapa.br","www.infoteca.cnptia.embrapa.br","www.acobrasil.org.br","abcp.org.br","www.gov.br","ceagesp.gov.br"]);
function validateLogisticsKnowledge(obj){
 if(!obj||obj.schema!==1||!Array.isArray(obj.sources)||obj.sources.length<3||obj.sources.length>30)return false;
 if(!/^\d{4}-\d{2}-\d{2}$/.test(String(obj.reviewed||"")))return false;
 const ids=new Set();
 for(const s of obj.sources){
  if(!s||!/^[-a-z0-9_]{3,45}$/.test(String(s.id||""))||ids.has(s.id))return false;
  if(typeof s.title!=="string"||s.title.length>220||typeof s.fact!=="string"||s.fact.length>700)return false;
  if(!Array.isArray(s.types)||!s.types.length||s.types.length>12)return false;
  const u=/^https:\/\/([a-z0-9.-]+)(?:\/|$)/i.exec(String(s.url||""));
  if(!u||!RESEARCH_HOSTS.has(u[1].toLowerCase()))return false;
  ids.add(s.id);
 }
 return !!obj.policies?.noFabricatedBusinesses&&!!obj.policies?.noForcedCoverage;
}
async function loadLogisticsKnowledge(){
 if(typeof window==="undefined"||!window.location||typeof fetch!=="function")
  return{data:OFFLINE_LOGISTICS_KNOWLEDGE,origin:"integrada/offline"};
 let controller,timeout;
 try{
  if(typeof AbortController!=="undefined")controller=new AbortController();
  if(controller)timeout=setTimeout(()=>controller.abort(),1800);
  const response=await fetch(RESEARCH_DATA_URL,{
    method:"GET",mode:"cors",cache:"no-store",signal:controller?.signal
  });
  if(!response.ok)throw Error("sem rede");
  const raw=await response.text();
  if(raw.length>90000)throw Error("base muito grande");
  const pack=JSON.parse(raw);
  if(!validateLogisticsKnowledge(pack))throw Error("base sem validação");
  return{data:pack,origin:"catálogo documental atualizado pela internet"};
 }catch{
  return{data:OFFLINE_LOGISTICS_KNOWLEDGE,origin:"base integrada/offline (sem atualização web)"};
 }finally{if(timeout)clearTimeout(timeout)}
}
// O modelo não confunde produtos da mesma indústria: milho != sorgo,
// metal/sucata != bobinas, algodão em caroço != pluma beneficiada.
const PRODUCT_EVIDENCE=Object.freeze({
 milho:/^(?:milho|corn|maize|maiz|milho_alto|corn_b)$/i,
 soja:/^(?:soja|soybeans?|soya|soja_alta|soy_b)$/i,
 sorgo:/^(?:sorgo|sorghum|sorgo_alto)$/i,
 adubo:/^(?:adubo|fertilizantes?|fertilizers?|ureia|urea)$/i,
 madeira:/^(?:madeira|madeirame|wood|timber|lumber|logs?|planks?|boards?)$/i,
 algodao:/^(?:pluma|cotton_?bales?|cottonlint|algodao_pluma|baled_?cotton)$/i,
 cimento:/^(?:cimento|cement|cement_b|cement_bags?|cement_pallet)$/i,
 batata:/^(?:batatas?|potatoes?|potato_b)$/i,
 laranja:/^(?:laranjas?|oranges?|citrus_oranges?)$/i,
 // Nomes comerciais da cerveja presentes em DEFs reais do MINAS.
 // Bebidas genéricas não demonstram cerveja, mas estas marcas sim.
 cerveja:/^(?:cervejas?|beer|beer_c|cerveza|amstel|antarctica|brahma|budweiser|devassa|heineken|schin|skol)$/i,
 tijolo:/^(?:tijolos?|bricks?|ceramic_bricks?)$/i,
 granito:/^(?:granito|granitto|granite|granite_blocks?)$/i,
 racao:/^(?:racao|racoes|xerem|feedmeal|feed_meal|animal_?feed|salmineral|suplementomineral)$/i,
 aco:/^(?:aco|steel|steel_plates?|chapa_?aco|ferroconst)$/i,
 bobinas_industriais:/^(?:bobinas?|steel_?coils?|metal_?coils?|rolled_steel|coil_steel)$/i,
 palete_vazio:/^(?:empty_?palet|empty_?pallets?|pallets?_empty|paletes?_vazios?)$/i,
 paletizado:/^(?:pallets?|paletes?|wood_?pallets?|empty_?palet)$/i
});
const RELATED_STONE=/^(?:stones?|pedras?|marmore|marble|marble_blocks?|dimension_?stone)$/i;
const EVIDENCE_REQUIRED=new Set(["milho","soja","sorgo","batata","laranja",
 "cerveja","cimento","tijolo","granito","algodao","racao","adubo","madeira","aco",
 "bobinas_industriais","palete_vazio","paletizado"]);
function findProductEvidence(profile,type,dir){
 const units=profile.declared?.[dir]||new Set();
 const literal=PRODUCT_EVIDENCE[type];
 const explicit=[...units].filter(value=>literal?.test(value));
 if(explicit.length)return{level:"especifica",units:explicit};
 if(type==="granito"){
  const similar=[...units].filter(value=>RELATED_STONE.test(value));
  if(similar.length)return{level:"relacionada",units:similar};
 }
 return{level:"ausente",units:[]};
}
const RESEARCH_CARGO_TOKENS=Object.freeze({
 algodao:/^(?:pluma|cotton_bales?|cottonlint|algodao_pluma|baled_cotton)$/i,
 racao:/^(?:racao|racoes|animal_?feed|feedmeal|feed_meal|xerem|farelo|salmineral|suplementomineral)$/i,
 bobinas_industriais:/^(?:bobinas?|steel_?coils?|metal_?coils?|rolled_steel|coil_steel)$/i
});

// Avaliador econômico contextual. É independente de IDs de mapa/reboque.
// Não transforma nomes de empresas em prova: exige atividade identificada,
// IN/OUT reais e mercadorias tecnicamente relacionadas para cada direção.
// A confiança B/C jamais é documental; é sempre uma inferência explícita.
function economicContextCandidate(c,profile,type,dir){
 if(!c||!profile||!["in","out"].includes(dir)||!profile.total||
    profile.total>=95||c.role==="desconhecida")return null;
 const role=c.role,n=(d,re)=>profile.count(d,re);
 const build=/^(?:bricks?|tijolos?|roof_tiles|tiles?|floorpanels|wallpanels|precast_strs|concr_beams|gravel|sand|areia|brita|stones?|pedras?|iron_pipes|ferroconst|b_reforco|chapaaco|calcario|limestone|concrete)$/i;
 const sheets=/^(?:chapa_?aco|steel_plates?|steel_sheets?|metal_center|hmetal|ferroconst|b_reforco)$/i;
 const steelInput=/^(?:chapa_?aco|steel_plates?|steel_sheets?|metal_center|hmetal|ferroconst|b_reforco|iron_ore|ore|coal|scrap_metals)$/i;
 const livestock=/^(?:beef3|beef_meat|milk|leite|gado|cattle|wool|sheep|livestock|animals?)$/i;
 const feed=/^(?:racao|racoes|feedmeal|animal_?feed|xerem|farelo|milho|corn|soja|soybeans?|sorghum|sorgo|grain|grains)$/i;
 const cotton=/^(?:cotton|cotton_seed|algodao|algodao_?caroco|pluma|cotton_bales?|cottonlint)$/i;
 const packageWood=/^(?:pallets?|paletes?|wood|timber|lumber|boards?|planks?|madeira|used_packag|empty_?pallets?|scrap_wood|sucata_madeira)$/i;
 let why="",level="forte";
 switch(type){
  case "cimento":
   if(dir==="out"&&role==="materiais"&&
      (n("out",build)>=2||(n("out",build)>=1&&n("in",build)>=1)))
    why="revenda: OUT de materiais de construção e estoque compatível com cimento ensacado";
   else if(dir==="out"&&role==="cimenteira"&&
      n("in",/^(?:calcario|limestone|clay|argila|gravel|sand)$/i)>0&&n("out",build)>0)
    why="indústria cimenteira com insumo mineral IN e produtos de construção OUT";
   else if(dir==="in"&&["obras","materiais","premoldados"].includes(role)&&n("in",build)>0)
    why=role==="premoldados"?"fábrica de pré-moldados com materiais de construção IN (consumo, não produção de cimento)":
      "obra ou revenda com recebimento documentado de insumos de construção";
   break;
  case "bobinas_industriais":
   if(dir==="out"&&["siderurgica","metalurgica"].includes(role)&&n("out",sheets)>0&&
      (n("in",steelInput)>0||n("out",sheets)>=2))
    why="siderurgia/distribuição de aço: chapas ou perfis OUT e cadeia de aço IN/OUT; bobina é hipótese";
   else if(dir==="in"&&["metalurgica","calhas"].includes(role)&&n("in",sheets)>0)
    why="processamento metálico que recebe chapa/aço; bobinas são matéria-prima plausível";
   else if(dir==="in"&&role==="obras"&&n("in",sheets)>0&&n("in",build)>=2)
    why="obra com entrada diversificada de aço estrutural; avaliar descarregamento de bobinas";
   break;
  case "sorgo":
   if(dir==="out"&&["agroinsumos","cooperativa","silo","logistica"].includes(role)&&
     n("out",feed)>0&&(n("in",feed)>0||n("out",feed)>=2)){
    why="comércio/armazenagem agropecuária movimenta grãos ou ingredientes de ração; sorgo específico inferido";
    level="inferida";
   }else if(dir==="in"&&["fazenda","pecuaria","racoes"].includes(role)&&
     n("in",feed)>0&&(n("out",livestock)>0||n("in",feed)>=2))
    why="propriedade pecuária ou fábrica de ração recebe ingredientes alimentares; sorgo não é ração pronta";
   else if(dir==="in"&&["cooperativa","silo"].includes(role)&&
     n("in",feed)>0&&n("out",feed)>0){
    why="entreposto recebe e expede grãos; possibilidade de armazenar sorgo";
    level="inferida";
   }
   break;
  case "algodao":
   if(dir==="out"&&role==="algodoeira"&&
     n("out",cotton)>0&&n("in",cotton)>0)
    why="beneficiadora com algodão IN/OUT; pluma pode sair após beneficiamento";
   else if(dir==="in"&&role==="textil"&&n("in",cotton)>0)
    why="indústria têxtil recebe algodão; pluma é matéria-prima de fiação";
   else if(dir==="in"&&role==="cooperativa"&&n("in",cotton)>0&&n("out",cotton)>0){
    why="cooperativa com fluxo de algodão IN/OUT, presumindo armazenagem de fibra";
    level="inferida";
   }
   break;
  case "palete_vazio":
   if(dir==="out"&&["supermercado","materiais","logistica","alimentos","bebidas","cervejaria","hortifruti","cooperativa","racoes","metalurgica"].includes(role)&&
      (profile.in.size>=2||(profile.in.size>=1&&profile.out.size>=1))){
    why="estabelecimento com movimentação física documentada e provável retorno de paletes vazios";
    level="inferida";
   }else if(dir==="in"&&["reciclagem","paletes","madeireira"].includes(role)&&
     (n("in",packageWood)>0||n("out",packageWood)>0)){
    why="recuperação/fabricação/reciclagem de embalagens de madeira documentada";
   }else if(dir==="in"&&role==="logistica"&&n("in",packageWood)>0){
    why="centro logístico com retorno declarado de embalagens";
    level="inferida";
   }
   break;
  case "cerveja":
   if(dir==="out"&&role==="cervejaria"&&
      n("out",/^(?:bebidas?|beverages?|beverages_c)$/i)>0&&
      n("in",/^(?:barley|cevada|malt|malte|hops|lupulo)$/i)>0)
    why="cervejaria com bebidas OUT e insumos cervejeiros IN";
   break;
 }
 if(!why)return null;
 const sectorCheck=economicCoherence(c,profile,type,dir);
 if(!sectorCheck.allowed)return null;
 return{score:level==="forte"?89:71,kind:"contextual",contextLevel:level,
  reason:"Compatibilidade econômica "+(level==="forte"?"forte":"inferida")+
   " ("+role+", "+dir.toUpperCase()+"): "+why+
   ". Evidência contextual, NÃO cargo idêntico na DEF."};
}
function logisticsIntelligenceDecision(company,profile,type,dir,evidence,knowledge=OFFLINE_LOGISTICS_KNOWLEDGE){
 if(!evidence)return null;
 const sourceIds=(knowledge.sources||[]).filter(s=>s.types.includes(type)).map(s=>s.id);
 const proof=findProductEvidence(profile,type,dir);
 if(evidence.kind==="contextual")return{...evidence,sourceIds,
  confidence:evidence.contextLevel==="forte"?"economica_forte":"inferida",documentedUnits:[]};
 if(EVIDENCE_REQUIRED.has(type)&&proof.level==="ausente"){
  return{blocked:true,reason:"Não há produto "+type+" no "+dir.toUpperCase()+
    "; produtos do mesmo setor não comprovam esta mercadoria.",sourceIds,
    confidence:"não comprovada"};
 }
 if(proof.level==="relacionada"){
  return{...evidence,sourceIds,kind:"categoria",confidence:"relacionada",
    documentedUnits:proof.units,
    reason:"Mercadoria mineral relacionada em "+dir.toUpperCase()+" ["+
      proof.units.join(", ")+"]; granito específico não comprovado. "+evidence.reason};
 }
 if(proof.level==="especifica"){
  return{...evidence,sourceIds,kind:"direta",confidence:"documental",
    documentedUnits:proof.units,
    reason:"Mercadoria identificada em "+dir.toUpperCase()+" ["+
      proof.units.join(", ")+"]; "+evidence.reason};
 }
 return{...evidence,sourceIds,confidence:"inferida",documentedUnits:[]};
}

function researchEscape(x){return String(x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function renderLogisticsResearch(research,sim){
 const line=el("companyCreateResearchStatus"),list=el("companyCreateResearchSources");
 if(line)line.textContent="Inteligência logística automática: "+research.data.sources.length+
  " fontes documentais · "+research.origin+" · "+
  (sim.researchRejectedTotal||0)+" associações imprecisas bloqueadas.";
 if(!list)return;
 list.innerHTML=research.data.sources.map(s=>"<p><b>"+researchEscape(s.agency)+
   "</b> — <a href=\""+researchEscape(s.url)+"\" target=\"_blank\" rel=\"noopener noreferrer\">"+
   researchEscape(s.title)+"</a><span class=\"muted small\"> — "+
   researchEscape(s.fact)+"</span></p>").join("");
}
function simulate(map,cargo,knowledge=OFFLINE_LOGISTICS_KNOWLEDGE){
 const catalogChecks=consultCatalogForMapDistribution(map);
 const plan=new Map(),skipped=[],proof=[],assumptions=[],anomalies=[],researchRejected=[],contextualDecisions=[];
 let researchRejectedTotal=0;
 const grouped={alta:0,baixa:0,outros:0},perCompany=[];
 const cargoChecks=new Map();
 for(const info of cargo.cargos.values()){
  const type=info.unresolvedName?null:kind(info.name);
  const body=info.body.filter(b=>!info.trailer.size||info.trailer.has(b));
  cargoChecks.set(info.id,{info,type,body,out:[],inn:[]});
 }
 for(const company of map.companies.values()){
  const profile=companyCargoProfile(company),decisions={id:company.id,in:[],out:[]};
  for(const entry of cargoChecks.values()){
   if(!entry.type||!entry.body.length)continue;
   for(const dir of ["out","in"]){
    const heuristic=companyCargoCompatibility(company,profile,entry.type,dir,entry.info,anomalies);
    const context=economicContextCandidate(company,profile,entry.type,dir);
    const evidence=heuristic?.kind==="direta"?heuristic:(context||heuristic);
    if(!evidence)continue;
    const ai=logisticsIntelligenceDecision(company,profile,entry.type,dir,evidence,knowledge);
    if(ai?.blocked){
      researchRejectedTotal++;
      if(researchRejected.length<600)researchRejected.push({company:company.id,cargo:entry.info.id,
       dir,reason:ai.reason,sourceIds:ai.sourceIds});
      continue;
    }
    if(ai?.kind==="contextual")contextualDecisions.push({company:company.id,
     cargo:entry.info.id,dir,confidence:ai.confidence,reason:ai.reason,sourceIds:ai.sourceIds});
    entry[dir==="out"?"out":"inn"].push({company,evidence:ai});
    decisions[dir].push(entry.info.id);
   }
  }
  perCompany.push(decisions);
 }
 for(const entry of cargoChecks.values()){
  const {info,type,body}=entry,issues=[],outs=entry.out,ins=entry.inn;
  if(!type)issues.push(info.unresolvedName?"cargo_data sem nome legível: informe descrição real, não adivinhar pelo ID":"tipo econômico da mercadoria não identificado");
  if(!info.body.length)issues.push("sem body_types");
  if(!body.length)issues.push("carroceria incompatível");
  if(!outs.length&&type)issues.push("nenhuma empresa com expedição IN/OUT compatível");
  if(!ins.length&&type)issues.push("nenhuma empresa com recebimento IN/OUT compatível");
  if(outs.length&&ins.length&&!outs.some(o=>ins.some(i=>i.company.id!==o.company.id)))
   issues.push("origem e destino seriam a mesma empresa");
  if(issues.length){skipped.push({id:info.id,name:info.name,problems:issues});continue}
  for(const x of outs){
   if(!plan.has(x.company.id))plan.set(x.company.id,{in:new Set(),out:new Set()});
   plan.get(x.company.id).out.add(info.id);
  }
  for(const x of ins){
   if(!plan.has(x.company.id))plan.set(x.company.id,{in:new Set(),out:new Set()});
   plan.get(x.company.id).in.add(info.id);
  }
  const notes=[...outs.map(x=>({...x,dir:"OUT"})),...ins.map(x=>({...x,dir:"IN"}))]
   .filter(x=>x.evidence.kind!=="direta"||x.evidence.roleConflict)
   .map(x=>x.company.id+" "+x.dir+": "+x.evidence.reason);
  if(notes.length)assumptions.push({id:info.id,notes});
  for(const b of body)if(b==="alta"||b==="baixa")grouped[b]++;else grouped.outros++;
  const researchSources=[...new Set([...outs,...ins].flatMap(x=>x.evidence.sourceIds||[]))];
  proof.push({id:info.id,name:info.name,type,researchSources,
   confidence:outs.every(x=>x.evidence.confidence==="documental")&&ins.every(x=>x.evidence.confidence==="documental")?"documental":
    [...outs,...ins].some(x=>x.evidence.confidence==="inferida")?"inferida":
    [...outs,...ins].some(x=>x.evidence.confidence==="economica_forte")?"economica_forte":"relacionada",
   origins:outs.length,destinations:ins.length,
   sourceIds:outs.map(x=>x.company.id),destIds:ins.map(x=>x.company.id),notes,
   categoryReasons:[],directOut:outs.filter(x=>x.evidence.kind==="direta").length,
   directIn:ins.filter(x=>x.evidence.kind==="direta").length,
   scsSourceIds:outs.filter(x=>x.company.catalog).map(x=>x.company.id),
   scsDestIds:ins.filter(x=>x.company.catalog).map(x=>x.company.id)});
 }
 return{plan,skipped,proof,grouped,assumptions,catalogChecks,perCompany,anomalies,researchRejected,researchRejectedTotal,contextualDecisions,knowledge,
  emptyCompanies:[...map.companies.keys()].filter(id=>!plan.has(id)),
  engine:"company-first"};
}

const cargoSii=id=>"SiiNunit\n{\n cargo_def : ."+id+" {\n  cargo: \"cargo."+id+"\"\n }\n}\n";
// Uma remoção dentro do novo ZIP NÃO remove o arquivo da DEF original montada
// pelo jogo. Conforme a documentação oficial SCS, cargo vazio desativa
// aquela permissão. Preservar o MESMO caminho é indispensável.
function disableExistingCargo(raw,p){
 const source=String(raw),fields=scanCompanyCargoFields(source);
 // Preservar arquivos sem cargo: em vez de produzir um SII sem unidade.
 if(!fields.length)return source;
 let result=source;
 for(const item of [...fields].reverse())
  result=result.slice(0,item.start)+'""'+result.slice(item.end);
 if(parseCompanyCargoUnits(result,p).length)
  throw Error("Não foi possível neutralizar todas as permissões: "+p);
 return result;
}
async function build(map,cargo,sim){
 const out=new JSZip(),keys=new Set(),generated=new Map();
 const disabled=[],replacedOriginal=[],coveredOriginal=[];
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
 // Pendente por chave normalizada: tolerar capitalização do mapa.
 const pending=new Map([...generated.entries()].map(([p,text])=>
  [p.toLowerCase(),{p,text}]));
 let count=0;
 for(const x of map.files.values()){
  const m=companyMeta(x.p);
  if(m&&(m.type==="in"||m.type==="out")){
   coveredOriginal.push(x.p);
   const replacement=pending.get(x.p.toLowerCase());
   if(replacement){
    // Já existe definição homônima: o cargo novo vence no mesmo caminho.
    await put(x.p,replacement.text);
    pending.delete(x.p.toLowerCase());
    replacedOriginal.push(x.p);
   }else{
    // SEMPRE cobrir as permissões antigas, mesmo nas empresas que não
    // recebem nenhuma carga Librelato. Assim não herdam fretes do mapa.
    const original=await x.obj.async("text");
    await put(x.p,disableExistingCargo(original,x.p));
    disabled.push(x.p);
   }
  }else{
   if(m?.type==="permanent"&&((x.obj._data?.uncompressedSize||0)<300000)){
    const txt=await x.obj.async("text");
    if(/^\s*(?:in_cargo|out_cargo)(?:\[\s*\d*\s*\])?\s*:/mi.test(txt))
      throw Error("Lista de cargas dentro do arquivo da empresa "+x.p+" exige conversão específica; geração bloqueada.");
   }
   await put(x.p,x.obj);
  }
  if((++count)%150===0){
    say("Substituindo TODAS as permissões IN/OUT do mapa… "+count,54);
    await yieldUI();
  }
 }
 for(const {p,text} of pending.values())await put(p,text);
 const blob=await out.generateAsync({type:"blob",compression:"DEFLATE",
  compressionOptions:{level:4},streamFiles:true},
  info=>say("Compactando Company integral… "+Math.round(info.percent)+"%",
   62+Math.round(info.percent*.28)));
 const check=await JSZip.loadAsync(blob,{createFolders:false});
 const generatedLower=new Set([...generated.keys()].map(p=>p.toLowerCase()));
 for(const p of generated.keys()){
  const obj=check.file(p);
  if(!obj)throw Error("Faltou carga gerada: "+p);
  const expected=p.split("/").pop().replace(/\.sii$/i,"").toLowerCase();
  const units=parseCompanyCargoUnits(await obj.async("text"),p);
  if(units.length!==1||units[0]!==expected)
   throw Error("Cargo gerado diferente da DEF solicitada: "+p);
 }
 let checked=0;
 for(const p of coveredOriginal){
  const obj=check.file(p);
  if(!obj)throw Error("Arquivo IN/OUT original sem sobrescrita: "+p);
  const units=parseCompanyCargoUnits(await obj.async("text"),p);
  if(generatedLower.has(p.toLowerCase())){
   const expected=p.split("/").pop().replace(/\.sii$/i,"").toLowerCase();
   if(units.length!==1||units[0]!==expected)
    throw Error("Nova permissão inválida em "+p);
  }else if(units.length){
   throw Error("Cargo original não neutralizado em "+p+": "+units.join(","));
  }
  if((++checked)%180===0)await yieldUI();
 }
 for(const x of map.files.values())
  if(companyMeta(x.p)?.type==="editor"&&!check.file(x.p))
   throw Error("Arquivo editor perdido: "+x.p);
 const seenCompanies=new Set(coveredOriginal.map(p=>companyMeta(p).id));
 return{blob,count:generated.size,removed:disabled.length+replacedOriginal.length,
  disabled:disabled.length,replacedOriginal:replacedOriginal.length,
  coverage:coveredOriginal.length,originalCompanies:seenCompanies.size};

}
function audit(map,cargo,sim){
 const companies=[...map.companies.values()],assigned=[...sim.plan.values()].reduce((n,p)=>n+p.in.size+p.out.size,0);
 const warning=[];
 if(sim.anomalies?.length)warning.push(sim.anomalies.length+" permissões contraditórias com atividade especializada foram bloqueadas; consulte o diagnóstico TXT.");
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
 if(cargo.scope?.excluded.length)warning.push(
  cargo.scope.excluded.length+" definições extras foram excluídas por não pertencerem ao manifesto/modelos do reboque.");
 const reasons=new Map();
 for(const item of sim.skipped)for(const reason of item.problems)reasons.set(reason,(reasons.get(reason)||0)+1);
 const ranked=[...reasons].sort((a,b)=>b[1]-a[1]);
 const roles=new Map();
 for(const item of companies)roles.set(item.role,(roles.get(item.role)||0)+1);
 ui.report.innerHTML="<div class='metrics'>"+
 [["Empresas",companies.length],["Cargas do reboque",cargo.cargos.size],["Com prova documental",sim.proof.filter(p=>p.confidence==="documental").length],["Compatibilidade econômica forte",sim.proof.filter(p=>p.confidence==="economica_forte").length],["Com categoria relacionada",sim.proof.filter(p=>p.confidence==="relacionada").length],["Rotas inferidas",sim.proof.filter(p=>p.confidence==="inferida").length],["Sem rota válida",sim.skipped.length],["Rejeições econômicas",sim.researchRejectedTotal||0],["Grade baixa",sim.grouped.baixa],["Grade alta",sim.grouped.alta],["Relações IN/OUT",assigned],["Empresas sem cargas compatíveis",sim.emptyCompanies?.length||0]]
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
 ui.detail.innerHTML="<p class='muted small'>Prova documental indica mercadoria declarada nos IN/OUT; não é verificação presencial da empresa. Categoria relacionada e inferência são hipóteses identificadas, não fatos.</p>"+"<details><summary>Conferir relações detalhadas das cargas</summary>"+
 "<p class='muted'>Cargas distribuídas (expedidores → recebedores): "+sim.proof.map(p=>escapeHTML(p.name)+" ("+escapeHTML(p.confidence)+"): "+p.origins+" → "+p.destinations).join("; ")+"</p>"+
 "<p class='muted'>Exemplos de relações do mapa (não garante oferta no ETS2):</p>"+
 sim.proof.map(p=>"<div class='audit'><b>"+escapeHTML(p.name)+" · "+escapeHTML(p.confidence)+"</b><span>OUT: "+escapeHTML(p.sourceIds.slice(0,6).join(", "))+" | IN: "+escapeHTML(p.destIds.slice(0,6).join(", "))+" | Referências: "+escapeHTML(p.researchSources.join(", ")||"nenhuma fonte aplicável")+"</span></div>").join("")+
 (sim.assumptions.length?"<details class='creator-catalog'><summary>Observações técnicas das cargas ("+sim.assumptions.length+")</summary><p class='muted'>São interpretações ainda não confirmadas, não impedimentos de geração.</p>"+sim.assumptions.map(p=>"<div class='audit'><b>"+escapeHTML(p.id)+"</b><span>"+escapeHTML(p.notes.join("; "))+"</span></div>").join("")+"</details>":"")+
 (sim.skipped.length?"<details class='creator-catalog'><summary>Cargas ainda sem rota verificada ("+sim.skipped.length+")</summary>"+sim.skipped.map(x=>"<div class='audit'><b>"+escapeHTML(x.id+" — "+x.name)+"</b> <span>"+escapeHTML(x.problems.join(", "))+"</span></div>").join("")+"</details>":"")+
 "</details>"+catalogSummary;
}

let latestDiagnostic=null;
function createDiagnosticText(map,cargo,sim){
 const rows=[
  "ETS2 COMPANY LOGISTICS - DIAGNÓSTICO DE ARQUIVOS",
  "Motor: "+ENGINE_BUILD,
  "Catálogo consultado: "+SCS_COMPANY_CATALOG.length+" referências; somente para classificar empresas existentes.",
  "Empresas existentes na DEF consultadas no catálogo durante a distribuição: "+(sim.catalogChecks?.consulted??map.companies.size),
  "Empresas padrão reconhecidas entre elas: "+(sim.catalogChecks?.matched??0),
  "Referências cargo: lidas dos arquivos IN/OUT: "+(map.parsedRelations||0),
  "Arquivos IN/OUT sem campo cargo ativo: "+(map.withoutCargo||0),
  "Integridade da DEF: "+JSON.stringify(isGenericCompanyMap(map)),
  "ATENÇÃO: uma Company formada majoritariamente por cargo.cargaN não documenta os produtos originais dos estabelecimentos.",
  "Empresas: "+map.companies.size,
  "Empresas sem cargas compatíveis: "+(sim.emptyCompanies?.length||0),
  "Incompatibilidades isoladas bloqueadas: "+(sim.anomalies?.length||0),
  "Regras de inteligência documental: "+(sim.knowledge?.sources?.length||0)+" fontes",
  "Inconsistências econômicas bloqueadas pelo assistente: "+(sim.researchRejectedTotal||0),
  "Amostra detalhada das rejeições (limite de 600): "+(sim.researchRejected?.length||0),
  "Cargas efetivas do reboque: "+cargo.cargos.size,
  "Escopo das cargas: "+(cargo.scope?.strategy||"sem especificação"),
  "Definições extras excluídas: "+(cargo.scope?.excluded.length||0),
  "Empresas com evidência de revenda de materiais (IN/OUT): "+[...map.companies.values()].filter(c=>!!c.supplyProof).map(c=>c.id).join(", "),
  "Definições de carroceria: "+[...cargo.cargos.values()].map(c=>c.id+" = "+(c.body.join("|")||"SEM BODY_TYPES")).join(", "),
  "",
  "EMPRESAS (ID | SETOR IDENTIFICADO | EVIDÊNCIA | CARGAS IN ANTIGAS | CARGAS OUT ANTIGAS)"
 ];
 for(const c of map.companies.values()){
  const ins=c.old.filter(x=>x.dir==="in").flatMap(x=>x.units?.length?x.units:[x.unit||"(SEM_CARGO)"]);
  const outs=c.old.filter(x=>x.dir==="out").flatMap(x=>x.units?.length?x.units:[x.unit||"(SEM_CARGO)"]);
  rows.push([c.id,c.role,c.evidence||"nenhuma",ins.join(","),outs.join(","),"categorias IN: "+[...(c.categories?.in||new Map())].map(x=>x.join("=")).join(","),"categorias OUT: "+[...(c.categories?.out||new Map())].map(x=>x.join("=")).join(",")].join(" | "));
 }
 rows.push("","CARGAS ENCONTRADAS NO ZIP MAS EXCLUÍDAS DO REBOQUE (ID | NOME | MOTIVO)");
 for(const entry of cargo.scope?.excluded||[])
  rows.push([entry.id,entry.name,entry.reason].join(" | "));
 rows.push("","FONTES PÚBLICAS DA INTELIGÊNCIA LOGÍSTICA (ID | ÓRGÃO | TÍTULO | URL | REGRA)");
 for(const s of sim.knowledge?.sources||[])
  rows.push([s.id,s.agency,s.title,s.url,s.fact].join(" | "));
 rows.push("","DECISÕES BLOQUEADAS PELA PESQUISA DOCUMENTAL (EMPRESA | CARGO | DIREÇÃO | MOTIVO | FONTES)");
 for(const r of sim.researchRejected||[])
  rows.push([r.company,r.cargo,r.dir,r.reason,r.sourceIds.join(",")].join(" | "));
 rows.push("","CARGAS REJEITADAS (ID | NOME | MOTIVOS)");
 for(const x of sim.skipped)rows.push([x.id,x.name,x.problems.join("; ")].join(" | "));
 rows.push("","ASSOCIAÇÕES CONTEXTUAIS EFETIVAS (EMPRESA | CARGA | DIREÇÃO | CONFIANÇA | JUSTIFICATIVA | FONTES)");
 for(const a of sim.contextualDecisions||[])if(sim.plan.get(a.company)?.[a.dir]?.has(a.cargo))
  rows.push([a.company,a.cargo,a.dir.toUpperCase(),a.confidence,a.reason,a.sourceIds.join(",")].join(" | "));
 rows.push("","CARGAS LIBERADAS (ID | NOME | EXPEDIDORES | RECEBEDORES | CONFIANÇA | FONTES | HIPÓTESES)");
 for(const p of sim.proof)rows.push([p.id,p.name,p.sourceIds.join(","),p.destIds.join(","),p.confidence,p.researchSources.join(","),p.notes.join("; "),"origens SCS: "+p.scsSourceIds.join(","),"destinos SCS: "+p.scsDestIds.join(",")].join(" | "));
 rows.push("","CARGAS CONTRADITÓRIAS BLOQUEADAS (EMPRESA | CARGO | SENTIDO | SETOR | MOTIVO)");
 for(const issue of sim.anomalies||[])
  rows.push([issue.company,issue.cargo,issue.direction,issue.role,issue.reason].join(" | "));
 rows.push("","DISTRIBUIÇÃO FINAL DE TODAS AS EMPRESAS (ID | IN | OUT | SITUAÇÃO)");
 for(const co of map.companies.values()){
  const p=sim.plan.get(co.id);
  rows.push([co.id,p?[...p.in].join(","):"",p?[...p.out].join(","):"",
   p?"COMPATÍVEL":"SEM CARGAS (IN/OUT antigos neutralizados)"].join(" | "));
 }
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
  const map=await loadMap(await zipRead(one));
  const integrity=isGenericCompanyMap(map);
  if(integrity.count>=1000&&integrity.share>=0.90)
    throw Error("A DEF do mapa contém "+Math.round(integrity.share*100)+
    "% de permissões genéricas cargo.cargaN, não as mercadorias originais. "+
    "Não é possível deduzir logística real desses arquivos. "+
    "Use a DEF COMPANY ORIGINAL do mapa, sem as DEF Companies genéricas 1 e 2 do Librelato.");
  applyCompanyOverrides(map);await yieldUI();
  say("Identificando cargas e carrocerias…",28);
  const cargo=await loadCargo(await zipRead(two));if(!cargo.cargos.size)throw Error("A DEF do reboque não contém unidades cargo_data reconhecidas.");
  say("Carregando e validando fontes logísticas documentadas…",37);
  const research=await loadLogisticsKnowledge();
  say("Verificando evidências econômicas para cada empresa e carga…",43);
  const sim=simulate(map,cargo,research.data);renderLogisticsResearch(research,sim);audit(map,cargo,sim);
  latestDiagnostic=createDiagnosticText(map,cargo,sim);const diag=el("companyCreateSaveDiagnostic");if(diag)diag.hidden=false;
  // Sem compatibilidade: mantém as empresas e gera SCS neutralizador integral.
  // Isso é um resultado legítimo, não erro de análise.
  if(!sim.plan.size)say("Nenhuma carga nova compatível; todas as empresas serão preservadas com permissões antigas neutralizadas.",51);
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
   removed:out.removed,
   disabled:out.disabled,
   coverage:out.coverage,
   originalCompanies:out.originalCompanies
  };
  updateDownloadUI();
  say("Company integral pronta: "+out.count+" novas associações, "+out.coverage+" arquivos IN/OUT antigos SOBRESCRITOS, "+out.disabled+" neutralizados (cargo vazio), "+map.companies.size+" empresas preservadas. Coloque este mod ACIMA da DEF do mapa. Grade baixa: "+sim.grouped.baixa+"; grade alta: "+sim.grouped.alta+". Baixe a Company .SCS. Motor: "+ENGINE_BUILD,100);
 }catch(e){say("Erro: "+(e?.message||String(e)),0)}
 finally{busy=false;ui.run.disabled=false;updateDownloadUI()}
}
ui.run.addEventListener("click",generate);
if(ui.download)ui.download.addEventListener("click",downloadCompany);
if(el("companyCreateSaveDiagnostic"))el("companyCreateSaveDiagnostic").addEventListener("click",downloadDiagnostic);
for(const id of ["companyCreateMapFile","companyCreateCargoFile"])el(id).addEventListener("change",()=>{clearCompanyDownload();const input=el(id),label=el(id+"Name");label.textContent=input.files?.[0]?.name||"Selecione um arquivo ZIP/SCS";say("Arquivo selecionado.",0)});
if(el("companyCreateOverrides"))el("companyCreateOverrides").addEventListener("input",clearCompanyDownload);
updateDownloadUI();
if(ui.message)ui.message.textContent="Motor carregado: "+ENGINE_BUILD;

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

window.CompanyCreatorTest={kind,known,economicContextCandidate,selectTrailerCargoScope,findProductEvidence,PRODUCT_EVIDENCE,EVIDENCE_REQUIRED,validateLogisticsKnowledge,loadLogisticsKnowledge,OFFLINE_LOGISTICS_KNOWLEDGE,logisticsIntelligenceDecision,maskSiiComments,scanCompanyCargoFields,parseCompanyCargoUnits,companyCargoProfile,companyCargoCompatibility,economicCoherence,disableExistingCargo,evidenceFromRealFlows,ENGINE_BUILD,relatedCargoCandidate,realMapEconomicCandidate,relatedCargoFallback,chooseEndpoints,detailedMovement,isGenericCompanyMap,inferRoleFromHistoricalFreights,createDiagnosticText,companyPath,cargoPath,companyMeta,flows,loadMap,loadCargo,simulate,build,scsCatalogLookup,SCS_COMPANY_CATALOG,oldCargoCategory,catalogForMapCompany,consultCatalogForMapDistribution,resolveEntries,isZipMagic,discoverBareCompanyRoots,mapFingerprint};
})();
