"use strict";
/**
 * Testes estruturais do HTML independente. Node >= 20, sem dependências externas.
 * Execute: node tests/company-creator.smoke.cjs
 *
 * Estes testes não substituem a verificação de fretes dentro do ETS2.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
assert.equal(scripts.length,3,"O HTML precisa conter biblioteca, motor antigo e motor Company");
const engineSource=fs.readFileSync(path.join(root,"creator_tab.js"),"utf8");
const catalogSource=fs.readFileSync(path.join(root,"scs_company_catalog.js"),"utf8");
assert.equal(scripts[2].trim(),engineSource.trim(),"O motor incorporado no HTML está desatualizado");
assert.ok(engineSource.includes(catalogSource.trim()),"O catálogo incorporado no motor está desatualizado");


const moduleShim={exports:{}};
new Function("module","exports","setImmediate",scripts[0])(
 moduleShim,moduleShim.exports,setImmediate
);
const JSZip=moduleShim.exports;
let generatedBytes=null;
const originalGenerate=JSZip.prototype.generateAsync;
JSZip.prototype.generateAsync=function(options,callback){
 return originalGenerate.call(this,
  options.type==="blob"?{...options,type:"uint8array"}:options,callback
 ).then(bytes=>{
  if(options.type==="blob")generatedBytes=bytes;
  return bytes;
 });
};

const elements=new Map();
function element(id){
 if(!elements.has(id))elements.set(id,{
  value:"",files:[],textContent:"",innerHTML:"",disabled:false,
  hidden:id==="companyCreateDownload",style:{},listeners:{},
  addEventListener(name,callback){this.listeners[name]=callback},
  classList:{add(){},remove(){},toggle(){}},insertAdjacentHTML(){}
 });
 return elements.get(id);
}
let downloadClicks=0,filename="";
const documentShim={
 getElementById:element,querySelectorAll:()=>[],
 createElement:()=>({
  click(){downloadClicks++},remove(){},
  set download(value){filename=value}
 }),
 body:{appendChild(){}}
};
const windowShim={addEventListener(){}};
const URLShim={createObjectURL:()=>"blob:smoke-test",revokeObjectURL(){}};
new Function("document","window","JSZip","URL",scripts[1])(
 documentShim,windowShim,JSZip,URLShim
);
new Function("document","window","JSZip","URL","setTimeout",scripts[2])(
 documentShim,windowShim,JSZip,URLShim,
 (fn,delay)=>delay>=5000?0:setTimeout(fn,delay)
);
const creator=windowShim.CompanyCreatorTest;

function fakeFile(bytes,name){
 bytes.name=name;
 bytes.size=bytes.length;
 bytes.slice=function(start,end){
  const chunk=Uint8Array.prototype.slice.call(this,start,end);
  chunk.arrayBuffer=async()=>chunk.buffer.slice(chunk.byteOffset,chunk.byteOffset+chunk.byteLength);
  return chunk;
 };
 return bytes;
}
function companyFile(zip,co,dir,id,cargo){
 zip.file("def/company/"+co+"/"+dir+"/"+id+".sii",
  'SiiNunit\n{\n cargo_def : .unit {\n cargo: "cargo.'+cargo+'"\n }\n}\n');
}
async function makesFixtures(){
 const map=new JSZip();
 for(const id of ["fazenda01","silo01","lojamaterial01","obra01"]){
  map.file("def/company/"+id+"/editor/city.sii","SiiNunit\n{}\n");
 }
 companyFile(map,"fazenda01","out","milho_original","corn");
 companyFile(map,"silo01","in","milho_original","corn");
 companyFile(map,"lojamaterial01","out","tijolo_original","bricks");
 companyFile(map,"obra01","in","tijolo_original","bricks");
 const lib=new JSZip();
 lib.file("cargo/carga1.sui",
  'cargo_data : cargo.carga1 {\n name: "Milho"\n body_types[]: baixa\n}\n');
 lib.file("cargo/carga13.sui",
  'cargo_data : cargo.carga13 {\n name: "Tijolos"\n body_types[]: alta\n}\n');
 lib.file("cargo.librelato.sii",'@include "cargo/carga1.sui"\n@include "cargo/carga13.sui"');

 const one=new JSZip();
 one.file("Brasil/MAPA.scs",await map.generateAsync({type:"uint8array"}));
 const two=new JSZip();
 two.file("Pacote DEF/Librelato.scs",await lib.generateAsync({type:"uint8array"}));
 const wrapper=new JSZip();
 wrapper.file("Baixe aqui/Def do mapa.zip",await one.generateAsync({type:"uint8array"}));
 return{
  map,lib,
  wrapper,
  originalMap:await map.generateAsync({type:"uint8array"}),
  mapFile:fakeFile(await wrapper.generateAsync({type:"uint8array"}),"qualquer_mapa.zip"),
  cargoFile:fakeFile(await two.generateAsync({type:"uint8array"}),"def_librelato.zip")
 };
}

async function main(){
 const f=await makesFixtures();

 // Teste das mercadorias recuperadas de def_company(2).zip (208 empresas)
 // sem presumir IDs ou nomes. Regras exigem prova IN/OUT e rejeitam
 // distribuidores genéricos que carregam de tudo.
 const profile=(id,out,inGoods)=>({id,role:"desconhecida",
  old:[...out.map(unit=>({dir:"out",unit,stem:unit})),
       ...inGoods.map(unit=>({dir:"in",unit,stem:unit}))]});
 const fixtures=[
  ["ped",["coal","gravel","ore","sand","stones"],["cement","concrete","diesel"]],
  ["konstnr2",["digger500","forklifts","mobile_crane"],["bricks","chimney_syst","concrete","floorpanels","gravel","iron_pipes","roof_tiles","wallpanels"]],
  ["arc",["big_bag_seed","feijao","graos","milho","soja"],["feijao","fertilizer","graos","milho","soja"]],
  ["aria_bd2",["beef3","milk"],["big_bag_seed","tractors"]],
  ["rocasoja",["feijao","milho","soja"],["big_bag_seed","fertilizer","tractors"]],
  ["cooper",["big_bag_seed","feijao","graos","milho","soja"],["feijao","fertilizer","graos","milho","soja"]],
  ["itaacos",["iron_pipes","largetubes","roof_tiles","sandwch_pnls","scrap_metals","wallpanels"],["iron_pipes","largetubes","sandwch_pnls","wallpanels"]],
  ["itcc2",["cement","concr_beams","floorpanels","iron_pipes","largetubes","wallpanels"],["cement","gravel","largetubes","metal_center"]]
 ];
 const mapFacts={companies:new Map(fixtures.map(([id,o,i])=>[id,profile(id,o,i)]))};
 const needed=[["granito","out"],["granito","in"],["racao","out"],["racao","in"],
  ["algodao","out"],["algodao","in"],["bobinas_industriais","out"],["bobinas_industriais","in"]];
 for(const [type,dir] of needed){
  const got=creator.evidenceFromRealFlows(mapFacts,type,dir);
  assert.ok(got.companies.length,"Falha ao recuperar "+type+"/"+dir+" da DEF real");
 }
 const junk=profile("generic_port",Array.from({length:120},(_,i)=>"cargo"+i),
   Array.from({length:120},(_,i)=>"cargo"+i));
 const withJunk={companies:new Map([...mapFacts.companies,[junk.id,junk]])};
 for(const [type,dir] of needed)
  assert.equal(creator.evidenceFromRealFlows(withJunk,type,dir).companies.some(x=>x.id===junk.id),false);


 // Regressão derivada da DEF real def_company(1).zip, com 208 empresas e
 // 6.739 arquivos OUT. Os IDs e mercadorias abaixo existem nessa DEF.
 const sample=(id,role,from,to)=>({id,role,
  old:[...from.map(unit=>({dir:"out",unit,stem:unit})),
       ...to.map(unit=>({dir:"in",unit,stem:unit}))]});
 const genuineSamples=[
  ["granito","out",sample("ped","pedreira",["stones","gravel","ore","sand"],["cement"])],
  ["granito","in",sample("car","desconhecida",["stones","gravel","ore"],["cement","iron_pipes","concrete"])],
  ["racao","out",sample("arc","cooperativa",["big_bag_seed","graos","milho","soja"],["milho","soja","fertilizer"])],
  ["racao","in",sample("aria_bd2","pecuaria",["beef3","milk"],["big_bag_seed","tractors"])],
  ["algodao","out",sample("rocasoja","desconhecida",["feijao","milho","soja"],["big_bag_seed","fertilizer"])],
  ["algodao","in",sample("cooper","cooperativa",["feijao","graos","milho","soja"],["feijao","graos","milho","soja","fertilizer"])],
  ["bobinas_industriais","out",sample("itaacos","metalurgica",["iron_pipes","scrap_metals","largetubes"],["iron_pipes","largetubes"])],
  ["bobinas_industriais","in",sample("itaacos","metalurgica",["iron_pipes","scrap_metals","largetubes"],["iron_pipes","largetubes"])]
 ];
 for(const [type,dir,company] of genuineSamples){
  assert.ok(creator.realMapEconomicCandidate(company,type,dir),
   "Regras novas não encontram evidência da DEF real: "+type+" "+dir+" "+company.id);
 }
 const misleading=sample("posto","posto",["stones","gravel","iron_pipes"],["cement"]);
 assert.equal(creator.realMapEconomicCandidate(misleading,"granito","out"),null,
  "Posto deve continuar excluído mesmo com dados absurdos");


 // Caso real reproduzido: DEF de mapa original tem IDs das mercadorias.
 // Já a DEF Company genérica 1/2 Librelato pode repetir cargo.cargaN
 // indiscriminadamente para praticamente todas as empresas.
 const genuine={companies:new Map([["dep",{
  id:"dep",role:"materiais",old:[{dir:"in",unit:"pedra"},{dir:"out",unit:"tijolos"},{dir:"out",unit:"madeira"}]
 }]])};
 assert.equal(creator.isGenericCompanyMap(genuine).generic,0);
 assert.ok(creator.relatedCargoCandidate(genuine.companies.get("dep"),"granito","out"),
   "Depósito com entrada de pedra e saída de materiais deve ser reconhecido como revenda");
 const agro={id:"loja_opaca",role:"desconhecida",old:[
  {dir:"in",unit:"racao"},{dir:"out",unit:"adubo"},{dir:"out",unit:"fertilizante"}]};
 assert.ok(creator.relatedCargoCandidate(agro,"racao","out"),
  "Distribuidora com entrada de ração e expedição de insumos deve poder revender");
 const diverse={id:"sem_nome",role:"desconhecida",old:[
  {dir:"out",unit:"milho"},{dir:"out",unit:"soja"},{dir:"in",unit:"adubo"}]};
 assert.ok(creator.relatedCargoCandidate(diverse,"algodao","out"),
   "Fazenda inferida por combinação IN/OUT, não pelo nome");
 const generic={companies:new Map(Array.from({length:30},(_,i)=>[
  "sem_ramo_"+i,{id:"sem_ramo_"+i,role:"desconhecida",
   old:Array.from({length:24},(_,j)=>({dir:"out",unit:"carga"+(j+1)}))}
 ]))};
 assert.equal(creator.isGenericCompanyMap(generic).share,1);
 assert.equal(creator.relatedCargoCandidate(generic.companies.values().next().value,"granito","out"),null,
  "Cargo.cargaN genérico não é prova de granito");


 // As empresas devem ser selecionadas pelos produtos em IN/OUT, não por
 // supostos ramos derivados do nome e do ID.
 const cargoFlows=[
  {id:"carga14",name:"Pedra Granito 1",type:"granito",from:"granitto",to:"marble"},
  {id:"carga15",name:"Pedra Granito 2",type:"granito",from:"granitto",to:"marble"},
  {id:"carga17",name:"Ração Mineral Laranja",type:"racao",from:"racao",to:"animal_feed"},
  {id:"carga18",name:"Xerém",type:"racao",from:"xerem",to:"animal_feed"},
  {id:"carga19",name:"Sacaria Ração",type:"racao",from:"racao",to:"animal_feed"},
  {id:"carga20",name:"Sacaria Ração 2",type:"racao",from:"racao",to:"animal_feed"},
  {id:"carga23",name:"Sorgoalto",type:"sorgo",from:"corn",to:"soybeans"},
  {id:"carga5",name:"Carga Pluma de Algodão",type:"algodao",from:"cotton",to:"cotton"},
  {id:"carga9",name:"Bobinas 2",type:"bobinas_industriais",from:"chapaaco",to:"ferroconst"}
 ];
 for(const [i,item] of cargoFlows.entries()){
  const made=(id,dir,units)=>({id,folder:id,role:"desconhecida",old:units.map((unit,k)=>({
   p:"def/company/"+id+"/"+dir+"/old"+k+".sii",dir,stem:"old"+k,unit
  }))});
  const src=made("empresa_origem"+i,"out",item.id==="carga23"?["corn","soybeans"]:item.id==="carga9"?["chapaaco","ferroconst"]:[item.from]);
  const dest=made("empresa_destino"+i,"in",item.id==="carga9"?["chapaaco","ferroconst"]:[item.to]);
  const map={companies:new Map([[src.id,src],[dest.id,dest]])};
  const endpoints=creator.chooseEndpoints(map,item.type,creator.flows[item.type],item.id);
  assert.ok(endpoints.out.some(x=>x.id===src.id),"Sem origem provada "+item.id);
  assert.ok(endpoints.inn.some(x=>x.id===dest.id),"Sem destino provado "+item.id);
 }


 // Evidência IN/OUT deve superar ID/nome que aparenta outro setor.
 for(const [dir,type,unit] of [["out","racao","racao"],["out","granito","granito"],
  ["in","granito","marmore"],["out","bobinas_industriais","bobinas"],
  ["out","algodao","algodao"]]){
  const co={id:"identificador_opaco",name:"",role:"desconhecida",
   old:[{dir,unit,stem:"arquivo_sem_significado"}]};
  assert.ok(creator.relatedCargoCandidate(co,type,dir),
   "IN/OUT real ignorado para "+type);
 }
 const unrelated={id:"metal_comercial",name:"Metal",role:"metalurgica",
  old:[{dir:"out",unit:"adubo",stem:"adubo"}]};
 assert.equal(creator.relatedCargoCandidate(unrelated,"bobinas_industriais","out"),null,
  "Nome ou ramo não pode justificar carga sem evidência");


 // Regressões: IDs opacos com provas nos cargos IN/OUT não devem ser
 // descartados só porque a empresa não tem nome de fábrica conhecido.
 function opaque(id,dir,goods){
  return {id,name:"",role:"desconhecida",old:goods.map((unit,i)=>({dir,unit,stem:"arquivo_"+i}))};
 }
 for(const [type,dir,goods] of [
  ["granito","out",["granito"]],["granito","in",["marmore"]],
  ["racao","out",["racao"]],["racao","out",["farelo"]],
  ["algodao","out",["pluma"]],["bobinas_industriais","out",["bobinas"]]
 ]){
  const candidate=opaque("empresa_sem_nome",dir,goods);
  assert.ok(creator.relatedCargoCandidate(candidate,type,dir),
   "Evidência explícita não reconhecida: "+type+" "+dir);
 }
 const incompatible={...opaque("posto01","out",["granito"]),role:"posto"};
 assert.equal(creator.relatedCargoCandidate(incompatible,"granito","out"),null,"Posto não pode expedir granito");


 // Integração completa: nove cargos, 18 empresas com nomes opacos, DEFs ZIP
 // reais em memória, geração de .SCS e auditoria dos caminhos gerados.
 const criticalMap=new JSZip(),criticalLib=new JSZip(),criticalAllowed=new Set();
 for(const [i,item]of cargoFlows.entries()){
  const origin="anon_origem_"+i,dest="anon_destino_"+i;
  criticalAllowed.add(origin);criticalAllowed.add(dest);
  for(const co of [origin,dest]){
   criticalMap.file("def/company/"+co+"/editor/cidade.sii","SiiNunit\n{}\n");
  }
  const outs=item.id==="carga23"?["corn","soybeans"]:item.id==="carga9"?["chapaaco","ferroconst"]:[item.from];
  const ins=item.id==="carga9"?["chapaaco","ferroconst"]:[item.to];
  for(const [dir,co,goods]of [["out",origin,outs],["in",dest,ins]])
   for(const [k,unit]of goods.entries())
    companyFile(criticalMap,co,dir,"evidencia_"+k,unit);
  criticalLib.file("cargo/"+item.id+".sui",
   'cargo_data : cargo.'+item.id+' {\n name: "'+item.name+'"\n body_types[]: alta\n}\n');
 }
 const parsedMap=await creator.loadMap(criticalMap);
 const parsedLib=await creator.loadCargo(criticalLib);
 assert.equal(parsedMap.companies.size,18,"Não deve importar empresas externas ao mapa");
 assert.equal(parsedLib.cargos.size,9,"Não deve inventar cargas de reboque");
 const criticalSim=creator.simulate(parsedMap,parsedLib);
 assert.deepEqual(criticalSim.skipped.map(x=>x.id),[],
  "Cargas com provas IN/OUT válidas não podem ficar sem rota: "+JSON.stringify(criticalSim.skipped));
 assert.equal(criticalSim.proof.length,9);
 for(const p of criticalSim.proof){
  assert.ok(p.origins>0&&p.destinations>0,p.id+" sem ambos os sentidos");
  assert.ok(p.sourceIds.every(id=>criticalAllowed.has(id))&&p.destIds.every(id=>criticalAllowed.has(id)),
   p.id+" tem empresa inventada");
 }
 const built=await creator.build(parsedMap,parsedLib,criticalSim);
 const reread=await JSZip.loadAsync(built.blob);
 for(const item of cargoFlows){
  const i=cargoFlows.indexOf(item);
  assert.ok(reread.file("def/company/anon_origem_"+i+"/out/"+item.id+".sii"),item.id+" sem OUT");
  assert.ok(reread.file("def/company/anon_destino_"+i+"/in/"+item.id+".sii"),item.id+" sem IN");
 }
 for(const p of Object.keys(reread.files)){
  const ref=/^def[/]company[/]([^/]+)[/](?:in|out)[/](carga[0-9]+)[.]sii$/i.exec(p);
  if(ref){
   assert.ok(criticalAllowed.has(ref[1]),"Empresa não autorizada no .SCS: "+ref[1]);
   assert.ok(cargoFlows.some(x=>x.id===ref[2]),"Cargo inexistente no .SCS: "+ref[2]);
  }
 }


 // Integração da correção com perfis extraídos da DEF REAL anexada pelo usuário.
 // Empresa IDs, mercadorias IN/OUT e combinações foram verificadas no ZIP
 // def_company(1).zip (208 empresas, 6739 OUT, 7088 IN).
 const actualProfiles=[
  {id:"ped",out:["stones","gravel","ore","sand"],in:["cement"]},
  {id:"car",out:["stones","gravel","ore"],in:["cement","iron_pipes","concrete"]},
  {id:"arc",out:["big_bag_seed","graos","milho","soja"],in:["milho","soja","fertilizer"]},
  {id:"aria_bd2",out:["beef3","milk"],in:["big_bag_seed","tractors"]},
  {id:"rocasoja",out:["feijao","milho","soja"],in:["big_bag_seed","fertilizer"]},
  {id:"cooper",out:["feijao","graos","milho","soja"],in:["feijao","graos","milho","soja","fertilizer"]},
  {id:"itaacos",out:["iron_pipes","scrap_metals","largetubes"],in:["iron_pipes","largetubes"]},
  {id:"gnt2",out:["metal_center","hmetal"],in:["metal_center","hmetal"]}
 ];
 const mapRealSubset=new JSZip(),libRealSubset=new JSZip();
 for(const co of actualProfiles){
  mapRealSubset.file("def/company/"+co.id+"/editor/test.sii","SiiNunit\n{}\n");
  for(const dir of ["out","in"])for(const [i,unit]of co[dir].entries())
   companyFile(mapRealSubset,co.id,dir,"real_"+i+"_"+dir,unit);
 }
 const missingEight=[
  ["carga14","Pedra Granito 1","baixa"],["carga15","Pedra Granito 2","baixa"],
  ["carga17","Ração Mineral Laranja","alta"],["carga18","Xerém","alta"],
  ["carga19","Sacaria Ração","alta"],["carga20","Sacaria Ração 2","alta"],
  ["carga5","Carga Pluma de Algodão","alta"],["carga9","Bobinas 2","baixa"]
 ];
 for(const [id,name,body]of missingEight)
  libRealSubset.file("cargo/"+id+".sui",
    'cargo_data : cargo.'+id+' {\n name: "'+name+'"\n body_types[]: '+body+'\n}\n');
 const mapSubset=await creator.loadMap(mapRealSubset);
 const libSubset=await creator.loadCargo(libRealSubset);
 assert.equal(mapSubset.companies.size,actualProfiles.length);
 const realSim=creator.simulate(mapSubset,libSubset);
 assert.deepEqual(realSim.skipped.map(x=>x.id),[],
  "DEF baseada em mercadorias reais deve permitir 8 cargas: "+JSON.stringify(realSim.skipped));
 const realScs=await creator.build(mapSubset,libSubset,realSim);
 const realArchive=await JSZip.loadAsync(realScs.blob);
 const ids=new Set(actualProfiles.map(x=>x.id));
 for(const [id]of missingEight){
  const src=realSim.proof.find(x=>x.id===id);
  assert.ok(src&&src.origins>0&&src.destinations>0,"Origem/destino inválido "+id);
  for(const co of src.sourceIds)
   assert.ok(realArchive.file("def/company/"+co+"/out/"+id+".sii"),"OUT ausente "+id+" "+co);
  for(const co of src.destIds)
   assert.ok(realArchive.file("def/company/"+co+"/in/"+id+".sii"),"IN ausente "+id+" "+co);
 }
 for(const path of Object.keys(realArchive.files)){
  const match=path.match(/^def[/]company[/]([^/]+)[/](?:in|out)[/](carga[0-9]+)[.]sii$/i);
  if(match){
   assert.ok(ids.has(match[1]),"Empresa inventada "+match[1]);
   assert.ok(missingEight.some(x=>x[0]===match[2]),"Cargo inventado "+match[2]);
  }
 }

 for(const [label,archive,expectedDepth] of [
  ["raiz",f.map,0],
  ["ZIP/SCS aninhado",f.wrapper,2]
 ]){
  const result=await creator.loadMap(archive);
  assert.equal(result.companies.size,4,label);
  assert.equal(result.archivesRead,expectedDepth,label);
 }
 const packageWithHashFS=new JSZip();
 packageWithHashFS.file("mod.scs",new Uint8Array([83,67,83,35,0,1,2]));
 await assert.rejects(creator.loadMap(packageWithHashFS),/HashFS não legíveis/);

 // Empresa sem "company/" na raiz: exatamente como os ZIPs com alc_cle/editor.
 const bare=new JSZip();
 bare.file("alc_cle/editor/clementina.sii","SiiNunit\n{}\n");
 bare.file("alc_cle/in/tanquevazio.sii",'SiiNunit\n{\n cargo_def: .c { cargo: "cargo.tanquevazio" }\n}\n');
 bare.file("alc_cle/out/alcoil.sii",'SiiNunit\n{\n cargo_def: .c { cargo: "cargo.alcoil" }\n}\n');
 bare.file("alc_cle.sii",'SiiNunit\n{\ncompany_permanent: .test {}\n}\n');
 const bareMap=await creator.loadMap(bare);
 assert.equal(bareMap.companies.size,1);
 assert.ok(bareMap.files.has("def/company/alc_cle/editor/clementina.sii"));
 assert.ok(bareMap.files.has("def/company/alc_cle/in/tanquevazio.sii"));
 assert.ok(bareMap.files.has("def/company/alc_cle/out/alcoil.sii"));
 assert.ok(bareMap.files.has("def/company/alc_cle.sii"));

 // Prioriza a Company já encontrada na raiz e não mistura outros mods aninhados.
 const mixed=new JSZip();
 mixed.file("def/company/fazenda01/editor/city.sii","SiiNunit\n{}\n");
 mixed.file("pacote.scs",f.originalMap);
 const mixedResult=await creator.loadMap(mixed);
 assert.equal(mixedResult.companies.size,1);
 assert.equal(mixedResult.archivesRead,0);

 // Dois caminhos diferentes que geram o mesmo destino não podem sobrescrever.
 const conflict=new JSZip();
 conflict.file("def/company/fazenda01/editor/city.sii","SiiNunit\n{}\n");
 conflict.file("company/fazenda01/editor/city.sii","SiiNunit\n{}\n");
 await assert.rejects(creator.loadMap(conflict),/duplicada/);

 const noCompany=new JSZip();
 noCompany.file("vehicle/truck/editor/part.sii","SiiNunit\n{}\n");
 await assert.rejects(creator.loadMap(noCompany),/Nenhuma DEF Company reconhecida/);

 const changed=new JSZip();
 changed.file("alc_cle/editor/clementina.sii","SiiNunit\n{}\n");
 changed.file("alc_cle/out/alcoil.sii",'SiiNunit\n{\n cargo_def: .c { cargo: "cargo.combustivel" }\n}\n');
 changed.file("alc_cle/in/tanquevazio.sii",'SiiNunit\n{\n cargo_def: .c { cargo: "cargo.tanquevazio" }\n}\n');
 const fingerprintOriginal=await creator.mapFingerprint(bareMap);
 const fingerprintChanged=await creator.mapFingerprint(await creator.loadMap(changed));
 assert.notEqual(fingerprintOriginal,fingerprintChanged,"Identificador deve refletir conteúdo");

 const cargoOuter=await JSZip.loadAsync(f.cargoFile);
 assert.equal((await creator.loadCargo(cargoOuter)).cargos.size,2);
 element("companyCreateMapFile").files=[f.mapFile];
 element("companyCreateCargoFile").files=[f.cargoFile];

 assert.equal(element("companyCreateDownload").hidden,true);
 await element("companyCreateGenerate").listeners.click();
 assert.match(element("companyCreateStatus").textContent,/Company integral pronta:/);
 assert.equal(element("companyCreateDownload").hidden,false);
 assert.equal(element("companyCreateDownload").disabled,false);
 const output=await JSZip.loadAsync(generatedBytes);
 const wanted=[
  "def/company/fazenda01/out/carga1.sii",
  "def/company/silo01/in/carga1.sii",
  "def/company/lojamaterial01/out/carga13.sii",
  "def/company/obra01/in/carga13.sii",
  "def/company/fazenda01/editor/city.sii"
 ];
 for(const name of wanted)assert.ok(output.file(name),"Faltou "+name);
 // Deve COBRIR o caminho original, pois o mapa permanece ativo no jogo.
 const obsolete=output.file("def/company/fazenda01/out/milho_original.sii");
 assert.ok(obsolete,"Arquivo antigo sem substituição (o mapa reinjeta a carga)");
 assert.match(await obsolete.async("text"),/\\bcargo\\s*:\\s*""/,
  "Arquivo original deve ter cargo vazio");
 assert.doesNotMatch(await obsolete.async("text"),/cargo\\.corn|cargo\\.milho_original/i);
 assert.match(creator.disableExistingCargo('SiiNunit\\n{\\n cargo_def: .a { cargo: "cargo.old" }\\n}'),
  /cargo:\\s*""/);
 const allowed=new Set(["fazenda01","silo01","lojamaterial01","obra01"]);
 const cargos=new Set(["carga1","carga13"]);
 for(const pathname of Object.keys(output.files)){
  const c=pathname.match(/^def\/company\/([^/]+)\//);
  if(c)assert.ok(allowed.has(c[1]),"Empresa inventada: "+c[1]);
  const cargo=pathname.match(/^def\/company\/[^/]+\/(?:in|out)\/([^/]+)\.sii$/);
  if(cargo)assert.ok(cargos.has(cargo[1]),"Cargo inventado: "+cargo[1]);
  assert.equal(/^def\/cargo\//.test(pathname),false,"O mod não pode recriar cargo_data");
 }
 element("companyCreateDownload").listeners.click();
 // Nenhuma empresa pode herdar permissão antiga apenas por ficar sem rota.
 const noReplacement=new JSZip();
 noReplacement.file("def/company/deposito_sem_rota/editor/cidade.sii","SiiNunit\\n{}");
 companyFile(noReplacement,"deposito_sem_rota","out","antiga_carga","old_steel");
 companyFile(noReplacement,"deposito_sem_rota","in","antiga_recebida","old_wood");
 const oldMap=await creator.loadMap(noReplacement);
 const blank=await creator.build(oldMap,{cargos:new Map()}, {plan:new Map()});
 const emptyZip=await JSZip.loadAsync(blank.blob);
 for(const item of ["def/company/deposito_sem_rota/out/antiga_carga.sii",
                    "def/company/deposito_sem_rota/in/antiga_recebida.sii"]){
  assert.ok(emptyZip.file(item),"Empresa sem rota reteve permissão: "+item);
  const txt=await emptyZip.file(item).async("text");
  assert.match(txt,/cargo:\\s*""/);
  assert.doesNotMatch(txt,/cargo\\.old_/);
 }
 assert.equal(blank.disabled,2);
 assert.equal(blank.coverage,2);
 assert.ok(emptyZip.file("def/company/deposito_sem_rota/editor/cidade.sii"));
 
 element("companyCreateDownload").listeners.click();
 assert.equal(downloadClicks,2,"Botão de download deve permitir repetição");
 assert.match(filename,/\.scs$/i);
 element("companyCreateMapFile").listeners.change();
 assert.equal(element("companyCreateDownload").hidden,true,"Troca de arquivo invalida download");
 console.log("OK: DEF alc_cle sem prefixo; ZIP raiz/aninhado; HashFS; colisão; fingerprint; carrocerias; integridade SCS; download.");
}
main().catch(error=>{console.error(error);process.exitCode=1});
