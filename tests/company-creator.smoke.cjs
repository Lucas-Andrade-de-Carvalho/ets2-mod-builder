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

 // Integração diretamente derivada dos arquivos de origem MINAS:
 // marcas comerciais de cerveja são produtos identificáveis, e as
 // definições auxiliares do jogo não pertencem automaticamente ao reboque.
 const beerMap=new JSZip(),beerDef=new JSZip();
 for(const id of ["ambev","jjdistibuido","abcatacado","superabc","bebida_generica"]){
  beerMap.file("def/company/"+id+"/editor/filial.sii","SiiNunit\n{}\n");
 }
 for(const brand of ["brahma","skol","heineken","amstel","antarctica","budweiser"]){
  companyFile(beerMap,"ambev","out",brand,brand);
  companyFile(beerMap,"jjdistibuido","out",brand,brand);
  companyFile(beerMap,"abcatacado","in",brand,brand);
  companyFile(beerMap,"superabc","in",brand,brand);
 }
 companyFile(beerMap,"bebida_generica","out","bebidas","bebidas");
 beerDef.file("cargo/carga12.sui",
  'cargo_data : cargo.carga12 {\n name: "Cervejas"\n body_types[]: alta\n}');
 beerDef.file("cargo/carga6.sui",
  'cargo_data : cargo.carga6 {\n name: "Carga de Cimento"\n body_types[]: baixa\n}');
 beerDef.file("cargo/cott_seed.sui",
  'cargo_data : cargo.cott_seed {\n name: "Sementes de Algodão"\n body_types[]: hopper\n}');
 beerDef.file("cargo/sugar_beet_b.sui",
  'cargo_data : cargo.sugar_beet_b {\n name: "@@cn_sugar_beet@@"\n body_types[]: granel\n}');
 beerDef.file("cargo/corn_b.sui",
  'cargo_data : cargo.corn_b {\n name: "@@cn_maize@@"\n body_types[]: granel\n}');
 beerDef.file("cargo.librelato.sii",
  'SiiNunit\n{\n@include "cargo/carga12.sui"\n@include "cargo/carga6.sui"\n}\n');
 const beerCargo=await creator.loadCargo(beerDef);
 assert.deepEqual([...beerCargo.cargos.keys()].sort(),["carga12","carga6"],
  "Manifesto determina cargas reais, não todas as defs extras no ZIP");
 assert.equal(beerCargo.scope.strategy,"manifesto @include");
 assert.equal(beerCargo.scope.excluded.length,3);
 const beerMapRead=await creator.loadMap(beerMap);
 const beerSim=creator.simulate(beerMapRead,beerCargo);
 const beerProof=beerSim.proof.find(p=>p.id==="carga12");
 assert.ok(beerProof,"Cerveja de marca real deve ter rota no MINAS");
 assert.deepEqual(beerProof.sourceIds.sort(),["ambev","bebida_generica","jjdistibuido"]);
 // V6.1: bebidas genéricas documentam a CATEGORIA, não cerveja literal.
 assert.deepEqual(beerProof.destIds.sort(),["abcatacado","superabc"]);
 assert.notEqual(beerProof.confidence,"documental","Categoria não é identidade literal");
 assert.equal(beerSim.proof.some(p=>p.id==="carga6"),false,
  "Sem cimento real, não inventar origem/destino apenas por haver outras cargas de construção");
 assert.equal(beerSim.plan.get("bebida_generica")?.out.has("carga12"),true,
  "Distribuição por categoria deve admitir saída de bebidas genéricas sem alegar cerveja literal");
 const beerBuilt=await creator.build(beerMapRead,beerCargo,beerSim);
 const beerPack=await JSZip.loadAsync(beerBuilt.blob);
 for(const company of ["ambev","jjdistibuido"])
  assert.ok(beerPack.file("def/company/"+company+"/out/carga12.sii"));
 for(const company of ["abcatacado","superabc"])
  assert.ok(beerPack.file("def/company/"+company+"/in/carga12.sii"));
 assert.deepEqual(creator.parseCompanyCargoUnits(
  await beerPack.file("def/company/bebida_generica/out/bebidas.sii").async("text"),
  "def/company/bebida_generica/out/bebidas.sii"),[],
  "Mercadoria antiga é neutralizada mesmo quando habilitada sua categoria");
 assert.ok(beerPack.file("def/company/bebida_generica/out/carga12.sii"),
  "A categoria de bebidas pode participar como OUT, mantendo distinção documental");

 // Sem manifesto, models vehicle/cargo fornecem o escopo de forma genérica.
 const modelScope=new JSZip();
 modelScope.file("cargo/soja_custom.sui",
  'cargo_data : cargo.soja_custom {\n name: "Soja"\n body_types[]: alta\n}');
 modelScope.file("cargo/nem_do_reboque.sui",
  'cargo_data : cargo.nem_do_reboque {\n name: "Sementes de Algodão"\n body_types[]: hopper\n}');
 modelScope.file("vehicle/cargo/soja_custom/model_area.sii",
  'SiiNunit\n{ cargo_model_match : .area { loading_method: custom } }\n');
 const modelLoad=await creator.loadCargo(modelScope);
 assert.deepEqual([...modelLoad.cargos.keys()],["soja_custom"]);
 assert.equal(modelLoad.scope.strategy,"modelos físicos vehicle/cargo");


 // Regressão baseada nos tokens IN/OUT observados nas DEFs MINAS e
 // em outra DEF brasileira: sem copiar arquivos privados para o repositório.
 assert.equal(creator.kind("Sementes de Algodão"),null,
  "Semente não pode se converter em pluma");
 assert.equal(creator.kind("Pallets Alto TESTE"),"paletizado",
  "Mercadoria teste deve ser somente categoria genérica de paletes");
 const sampleMap=new JSZip(),sampleCargo=new JSZip();
 const sampleCompanies={
  agromais:{out:["racao","adubo","fertilizante"],in:["milho","soja"]},
  abcatacado:{in:["racao","batata","laranja","milho"],out:[]},
  belgo:{out:["chapaaco","ferroconst"],in:["chapaaco"]},
  cofepe:{in:["chapaaco","ferroconst"],out:["ferroconst"]},
  ped:{out:["stones","gravel"],in:["cement"]},
  empresa_sem_evidencia:{out:["sucata"],in:["diesel"]}
 };
 for(const [co,flow] of Object.entries(sampleCompanies)){
  sampleMap.file("def/company/"+co+"/editor/filial.sii","SiiNunit\n{}\n");
  for(const dir of ["in","out"])for(const [index,unit] of (flow[dir]||[]).entries())
   companyFile(sampleMap,co,dir,unit+"_"+index,unit);
 }
 sampleCargo.file("cargo/carga17.sui",
  'cargo_data : cargo.carga17 {\n name: "Ração Mineral Laranja"\n body_types[]: alta\n}\n');
 sampleCargo.file("cargo/carga9.sui",
  'cargo_data : cargo.carga9 {\n name: "Bobinas 2"\n body_types[]: baixa\n}\n');
 sampleCargo.file("cargo/carga5.sui",
  'cargo_data : cargo.carga5 {\n name: "Carga Pluma de Algodão"\n body_types[]: alta\n}\n');
 sampleCargo.file("cargo/carga23.sui",
  'cargo_data : cargo.carga23 {\n name: "Sorgoalto"\n body_types[]: alta\n}\n');
 const minasParsedMap=await creator.loadMap(sampleMap);
 const parsedCargo=await creator.loadCargo(sampleCargo);
 const reality=creator.simulate(minasParsedMap,parsedCargo);
 // No modo categoria, chapas e ferragens documentam siderurgia,
 // mas não comprovam bobinas literais; a confiança precisa refletir isso.
 const feedProof=reality.proof.find(p=>p.id==="carga17");
 const steelProof=reality.proof.find(p=>p.id==="carga9");
 assert.ok(feedProof,"Ração literal deve preservar rota");
 assert.ok(feedProof.directOut>0&&feedProof.directIn>0,
  "Manter prova literal de ração em pelo menos um OUT e IN, mesmo quando a rota também envolve empresas por categoria");
 assert.notEqual(feedProof.confidence,"documental",
  "A confiança geral não pode ser documental quando há inclusão de categorias não literais");
 assert.ok(feedProof.sourceIds.includes("agromais"));
 assert.ok(feedProof.destIds.includes("abcatacado"));
 assert.ok(steelProof,"Bobinas devem circular na categoria siderúrgica");
 assert.notEqual(steelProof.confidence,"documental","Chapas não comprovam bobinas físicas");
 for(const id of ["carga5","carga23"])
  assert.ok(reality.skipped.some(item=>item.id===id),
   "Sem pares econômicos distintos da categoria, a carga não pode inventar empresas");
 assert.ok(!reality.plan.has("empresa_sem_evidencia"));
 const realityBuilt=await creator.build(minasParsedMap,parsedCargo,reality);
 const realitySCS=await JSZip.loadAsync(realityBuilt.blob);
 assert.ok(realitySCS.file("def/company/agromais/out/carga17.sii"));
 assert.ok(realitySCS.file("def/company/abcatacado/in/carga17.sii"));
 for(const [co,dir,unit] of [["belgo","out","chapaaco_0"],
  ["empresa_sem_evidencia","out","sucata_0"]]){
  const generated=realitySCS.file("def/company/"+co+"/"+dir+"/"+unit+".sii");
  assert.ok(generated,"Preservar arquivo original como neutralizador");
  assert.deepEqual(creator.parseCompanyCargoUnits(await generated.async("text"),unit+".sii"),[],
   "Neutralizar fretes incompatíveis");
 }


 // V6: inferências contextualizadas por papel econômico + fluxos reais da DEF.
 // Nenhuma rota abaixo depende de ID cargaN nem presume produto documental.
 const economyMap=new JSZip(),economyCargo=new JSZip();
 const enterprises={
  loja_material_construcao01:{in:["sand","gravel"],out:["bricks","roof_tiles"]},
  obra_mg01:{in:["bricks","gravel"],out:[]},
  fabrica_premoldados01:{in:["bricks","gravel"],out:["precast_strs"]},
  cofer:{in:["chapaaco"],out:["chapaaco","ferroconst"]},
  fabrica_calhas01:{in:["chapaaco"],out:["ferroconst"]},
  loja_agropecuaria01:{in:["corn","soybeans"],out:["corn","feedmeal"]},
  fazenda_boi01:{in:["feedmeal"],out:["beef3"]},
  algodoeira01:{in:["cotton"],out:["cotton"]},
  industria_textil01:{in:["cotton"],out:["fabric"]},
  supermercado_a01:{in:["potatoes","brahma","soybeans"],out:[]},
  reciclagem_madeira01:{in:["wood"],out:["lumber"]},
  sem_setor_provado:{in:["diesel"],out:["scrap_metals"]}
 };
 for(const [name,trade] of Object.entries(enterprises)){
  economyMap.file("def/company/"+name+"/editor/city.sii","SiiNunit\n{}\n");
  for(const d of ["in","out"])for(const [i,item] of trade[d].entries())
   companyFile(economyMap,name,d,item+"_"+i,item);
 }
 for(const [id,name] of [["cement_bags","Cimento em sacos"],
  ["steel_bundle","Bobinas de aço"],["sorghum_feed","Sorgo para ração"],
  ["cotton_lint","Pluma de algodão"],["empty_wood_pallets","Paletes vazios"]])
  economyCargo.file("cargo/"+id+".sui",
   'cargo_data : cargo.'+id+' {\n name: "'+name+'"\n body_types[]: baixa\n}');
 const econCompanies=await creator.loadMap(economyMap);
 const econLoads=await creator.loadCargo(economyCargo);
 const econSim=creator.simulate(econCompanies,econLoads);
 const route=id=>econSim.proof.find(p=>p.id===id);
 for(const [id,origin,dest] of [
  ["cement_bags","loja_material_construcao01","fabrica_premoldados01"],
  ["steel_bundle","cofer","fabrica_calhas01"],
  ["sorghum_feed","loja_agropecuaria01","fazenda_boi01"],
  ["cotton_lint","algodoeira01","industria_textil01"],
  ["empty_wood_pallets","supermercado_a01","reciclagem_madeira01"]
 ]){
  const p=route(id);
  assert.ok(p,"V6 deve identificar cadeia realista para "+id+
   ": "+JSON.stringify(econSim.skipped.find(x=>x.id===id)));
  assert.ok(p.sourceIds.includes(origin),id+" sem origem econômica plausível");
  assert.ok(p.destIds.includes(dest),id+" sem destino econômico plausível");
  assert.notEqual(p.confidence,"documental","Inferência não pode virar prova literal: "+id);
 }
 assert.equal(econSim.plan.has("sem_setor_provado"),false,
  "Metal sucata + diesel de uma empresa opaca não autoriza nenhum frete");
 assert.equal(econSim.proof.length,5);
 assert.ok(econSim.contextualDecisions.length>=10);
 assert.equal(creator.kind("Pallets Alto TESTE"),"paletizado","Palete genérico não é palete vazio comprovado");
 assert.equal(creator.economicContextCandidate({id:"f",role:"fazenda"},
  creator.companyCargoProfile({old:[{dir:"out",unit:"corn"},{dir:"out",unit:"soybeans"}]}),
  "sorgo","out"),null,"Produzir milho/soja não comprova sorgo");
 const ecoPack=await creator.build(econCompanies,econLoads,econSim);
 const ecoOutput=await JSZip.loadAsync(ecoPack.blob);
 assert.ok(ecoOutput.file("def/company/cofer/out/steel_bundle.sii"));
 assert.ok(ecoOutput.file("def/company/fabrica_calhas01/in/steel_bundle.sii"));
 assert.ok(ecoOutput.file("def/company/reciclagem_madeira01/in/empty_wood_pallets.sii"));
 assert.ok(ecoOutput.file("def/company/loja_material_construcao01/out/cement_bags.sii"));
 assert.deepEqual(creator.parseCompanyCargoUnits(
  await ecoOutput.file("def/company/sem_setor_provado/out/scrap_metals_0.sii").async("text"),
  "scrap_metals_0.sii"),[]);

 // Strings com caracteres UTF-16 de dois code units não podem deslocar
 // offsets de neutralização nem alterar comentários.
 const unicodeSii='SiiNunit\n{\n // 🚚 carga de teste\\n'+
  ' cargo_def : .a { cargo: "cargo.milho" } \n'+
  ' cargo_def : .b { cargo: "cargo.soja" }\n}';
 const corrected=creator.disableExistingCargo(unicodeSii,"unicode.sii");
 assert.deepEqual(creator.parseCompanyCargoUnits(corrected,"unicode.sii"),[]);
 assert.ok(corrected.includes("🚚"),"Texto Unicode original deve permanecer intacto");

 // IDs semânticos localizados podem ser resolvidos; IDs genéricos não.
 const labels=new JSZip();
 for(const [id,locale] of [["corn_b","@@cn_maize@@"],["soybean_b","@@cn_soybean@@"],
   ["potatoes_b","@@cn_potatoes@@"],["sugar_beet_b","@@cn_sugar_beet@@"]]){
  labels.file("cargo/"+id+".sui",
   'cargo_data : cargo.'+id+' {\n name: "'+locale+'"\n body_types[]: alta\n}\n');
 }
 const labelsData=await creator.loadCargo(labels);
 for(const id of ["corn_b","soybean_b","potatoes_b"]){
  assert.equal(labelsData.cargos.get(id).unresolvedName,false,"Nome semântico resolvido "+id);
 }
 assert.equal(labelsData.cargos.get("sugar_beet_b").unresolvedName,true,
  "Mercadorias fora do dicionário semântico devem permanecer sem classificação");

 // Não ignorar arquivos enormes ou IDs de cargo_data duplicados.
 const repeated=new JSZip();
 for(const path of ["cargo/carga1.sui","cargo/carga2.sui"])
  repeated.file(path,'cargo_data : cargo.milho_repetido {\n name: "Milho"\n body_types[]: alta\n}');
 await assert.rejects(creator.loadCargo(repeated),/duplicado/);
 const cargoOversize=new JSZip();
 cargoOversize.file("cargo/carga1.sui",
  'cargo_data : cargo.carga1 {\n name: "Milho"\n body_types[]: alta\n}\n'+" ".repeat(520000));
 await assert.rejects(creator.loadCargo(cargoOversize),/extensa demais/);


 // V5: a forma física e a mercadoria individual têm prioridade sobre
 // a semelhança entre produtos da mesma indústria.
 assert.equal(creator.kind("Bobina de aço"),"bobinas_industriais");
 assert.equal(creator.kind("Bobinas 2"),"bobinas_industriais");
 const documented=(id,entries)=>({id,role:"desconhecida",old:entries.map(([dir,unit])=>({dir,unit,stem:"arquivo_irrelevante"}))});
 const cropFarm=documented("sem_nome",[
  ["out","corn"],["out","soybeans"],["in","fertilizer"]]);
 const cropProfile=creator.companyCargoProfile(cropFarm);
 for(const [type,dir] of [["sorgo","out"],["batata","out"],["laranja","out"],
  ["algodao","out"],["racao","out"],["cerveja","out"]]){
  assert.equal(creator.findProductEvidence(cropProfile,type,dir).level,"ausente");
  assert.equal(creator.logisticsIntelligenceDecision(cropFarm,cropProfile,type,dir,
   {score:80,kind:"inferida",reason:"mesmo setor"}).blocked,true,
   "Não deduzir "+type+" a partir de milho/soja");
 }
 const mill=documented("expedidor_siderurgico",[
  ["out","iron_pipes"],["out","scrap_metals"],["in","metal_center"]]);
 const millProfile=creator.companyCargoProfile(mill);
 assert.equal(creator.findProductEvidence(millProfile,"bobinas_industriais","out").level,"ausente");
 assert.equal(creator.logisticsIntelligenceDecision(mill,millProfile,
  "bobinas_industriais","out",{score:88,kind:"inferida",reason:"metal"}).blocked,true);
 const coil=documented("id_opaco",[
  ["out","steel_coils"],["in","scrap_metals"]]);
 const coilProfile=creator.companyCargoProfile(coil);
 assert.equal(creator.findProductEvidence(coilProfile,"bobinas_industriais","out").level,"especifica");
 assert.equal(creator.logisticsIntelligenceDecision(coil,coilProfile,
  "bobinas_industriais","out",{score:120,kind:"direta",reason:"coil"}).confidence,"documental");
 const quarry=documented("id_mineral",[
  ["out","stones"],["out","gravel"],["in","cement"]]);
 const quarryProof=creator.logisticsIntelligenceDecision(quarry,creator.companyCargoProfile(quarry),
  "granito","out",{score:75,kind:"inferida",reason:"rochas"});
 assert.equal(quarryProof.confidence,"relacionada");
 const rawCotton=documented("produtor",[
  ["out","cotton"],["in","fertilizer"]]);
 assert.equal(creator.findProductEvidence(creator.companyCargoProfile(rawCotton),"algodao","out").level,
  "ausente","Algodão em caroço não é automaticamente pluma beneficiada");
 const unnamedCargo=new JSZip();
 unnamedCargo.file("cargo/carga9.sui",
  'cargo_data : cargo.carga9 {\n name: "@@cargo_localizado@@"\n body_types[]: alta\n}\n');
 const unknownCargo=await creator.loadCargo(unnamedCargo);
 assert.equal(unknownCargo.cargos.get("carga9").unresolvedName,true);
 const unsupported=creator.simulate({companies:new Map([[coil.id,coil]])},unknownCargo);
 assert.ok(unsupported.skipped.some(x=>x.id==="carga9"),
  "ID carga9 não deve inferir bobinas sem uma descrição legível");


 // Inteligência documental interna: sem API paga, sem fabricador de fretes.
 const kb=creator.OFFLINE_LOGISTICS_KNOWLEDGE;
 assert.equal(creator.validateLogisticsKnowledge(kb),true);
 assert.ok(kb.sources.length>=5,"Fontes documentadas integradas");
 const suspect={id:"agricola_generica",role:"desconhecida",old:[
  {dir:"out",unit:"corn"},{dir:"out",unit:"soybeans"},
  {dir:"in",unit:"fertilizer"}]};
 const ps=creator.companyCargoProfile(suspect);
 const evidence={score:70,kind:"inferida",reason:"culturas diversificadas"};
 for(const type of ["algodao","racao","bobinas_industriais"]){
  const decision=creator.logisticsIntelligenceDecision(suspect,ps,type,"out",evidence,kb);
  assert.equal(decision.blocked,true,"Não inventar "+type+" por semelhança econômica");
  assert.ok(decision.sourceIds.length>0,"Rejeição deve citar fonte: "+type);
 }
 const algodoeira={id:"n1",role:"desconhecida",old:[
  {dir:"out",unit:"pluma"},{dir:"in",unit:"cotton"}]};
 const pAlg=creator.companyCargoProfile(algodoeira);
 assert.equal(creator.logisticsIntelligenceDecision(algodoeira,pAlg,
   "algodao","out",{score:120,kind:"direta",reason:"pluma OUT"},kb).blocked,undefined);
 const rações={id:"r1",role:"desconhecida",old:[{dir:"out",unit:"racao"},{dir:"in",unit:"corn"}]};
 assert.equal(creator.logisticsIntelligenceDecision(rações,creator.companyCargoProfile(rações),
  "racao","out",{score:120,kind:"direta",reason:"ração real"},kb).blocked,undefined);
 const sider={id:"s1",role:"desconhecida",old:[{dir:"out",unit:"steel_coils"},{dir:"in",unit:"scrap_metals"}]};
 assert.equal(creator.logisticsIntelligenceDecision(sider,creator.companyCargoProfile(sider),
  "bobinas_industriais","out",{score:120,kind:"direta",reason:"coils OUT"},kb).blocked,undefined);
 const absent={id:"empty",role:"desconhecida",old:[]};
 assert.equal(creator.logisticsIntelligenceDecision(absent,creator.companyCargoProfile(absent),
  "algodao","out",null,kb),null);
 assert.equal(creator.validateLogisticsKnowledge({...kb,sources:kb.sources.map((x,i)=>i?x:{...x,url:"http://example.com"})}),false);
 const automated=await creator.loadLogisticsKnowledge();
 assert.equal(automated.data.sources.length,kb.sources.length);


 // A aba Arquivos/Gerar SCS (outra ferramenta do mesmo HTML) também deve
 // rejeitar ZIPs inseguros, sem confundi-la com o gerador universal.
 assert.equal(typeof windowShim.Ets2MainTest.validateMainArchive,"function");
 const mainZip=new JSZip();mainZip.file("def/company/a/editor/city.sii","SiiNunit\n{}");
 assert.equal(windowShim.Ets2MainTest.validateMainArchive(mainZip).entries,1);
 assert.throws(()=>windowShim.Ets2MainTest.validateMainArchive({
  files:{"def/../invalido.sii":{dir:false,_data:{uncompressedSize:30}}}
 }),/inseguro/);
 assert.throws(()=>windowShim.Ets2MainTest.validateMainArchive({
  files:{"def/company/a/out/huge.sii":{dir:false,_data:{uncompressedSize:180*1024*1024}}}
 }),/150 MB/);


 // Profissionalização da leitura: múltiplos cargo: no mesmo SII,
 // comentários ignorados, preservação das unidades e classificação manual.
 const multiCargo=new JSZip();
 multiCargo.file("def/company/loja_ab/editor/city.sii","SiiNunit\n{}\n");
 multiCargo.file("def/company/loja_ab/out/multiplo.sii",
  'SiiNunit\n{\n // cargo: "cargo.fake_comment"\n'+
  ' cargo_def: .one { cargo: "cargo.corn" }\n'+
  ' /* cargo: "cargo.another_fake" */\n'+
  ' cargo_def: .two { cargo: cargo.soybeans }\n}\n');
 const multiMap=await creator.loadMap(multiCargo);
 const multiCompany=multiMap.companies.get("loja_ab");
 assert.deepEqual(multiCompany.old[0].units,["corn","soybeans"]);
 assert.equal(multiMap.parsedRelations,2);
 const multiProfile=creator.companyCargoProfile(multiCompany);
 assert.ok(multiProfile.declared.out.has("corn"));
 assert.ok(multiProfile.declared.out.has("soybeans"));
 assert.ok(!multiProfile.declared.out.has("fake_comment"));
 assert.deepEqual(creator.parseCompanyCargoUnits(
  'cargo_def: .one { cargo: "cargo.bricks" }\n// cargo: "cargo.fake"\n', "example.sii"),["bricks"]);
 assert.throws(()=>creator.parseCompanyCargoUnits(
  'cargo_def: .one { cargo: "invalid_reference" }', "broken.sii"),/inválida/);
 const neutralized=creator.disableExistingCargo(
  'SiiNunit\n{\n // cargo: "cargo.comment"\n'+
  ' cargo_def: .x { cargo: "cargo.corn" }\n'+
  ' cargo_def: .y { cargo: cargo.soybeans }\n}',"multi.sii");
 assert.deepEqual(creator.parseCompanyCargoUnits(neutralized,"multi.sii"),[]);
 assert.ok(neutralized.includes('// cargo: "cargo.comment"'),
  "Não modificar comentários legítimos");
 assert.equal((neutralized.match(/cargo:\s*""/g)||[]).length,2);
 const noCargoDefinition='SiiNunit\n{\n some_unit : .test { value: 1 }\n}\n';
 assert.equal(creator.disableExistingCargo(noCargoDefinition,"none.sii"),noCargoDefinition);
 const funnyName={id:"fazenda_batata",role:"fazenda",
  old:[{dir:"out",stem:"milho.sii",unit:null}]};
 assert.equal(creator.companyCargoProfile(funnyName).out.size,0,
  "Nomes de arquivos não geram mercadorias");

 // Catálogo nunca deve cancelar ajuste feito pelo usuário.
 const manual={id:"euroacres",role:"agroinsumos",
  evidence:"classificação informada pelo usuário",old:[]};
 const mapManual={companies:new Map([[manual.id,manual]])};
 creator.consultCatalogForMapDistribution(mapManual);
 assert.equal(manual.role,"agroinsumos");
 assert.equal(manual.evidence,"classificação informada pelo usuário");
 assert.ok(manual.catalog);

 // Carga de outro reboque: não limitar arbitrariamente aos IDs cargaN.
 const independentCargo=new JSZip();
 independentCargo.file("cargo/milho_real.sui",
  'cargo_data : cargo.milho_real {\n name: "Milho"\n body_types[]: alta\n}\n');
 const independentParsed=await creator.loadCargo(independentCargo);
 assert.ok(independentParsed.cargos.has("milho_real"));

 // Definição IN/OUT anormalmente grande deve falhar explicitamente,
 // em vez de ser ignorada e gerar cargas por adivinhação.
 const tooBig=new JSZip();
 tooBig.file("def/company/empresa/editor/city.sii","SiiNunit\n{}\n");
 tooBig.file("def/company/empresa/out/huge.sii",
  'SiiNunit\n{\n cargo_def: .x { cargo: "cargo.corn" }\n}\n'+
  " ".repeat(1100000));
 await assert.rejects(creator.loadMap(tooBig),/grande demais|excede limite/);


 // O nome é auxiliar: se ele contradiz os arquivos IN/OUT, a mercadoria
 // efetivamente declarada deve prevalecer. O nome SOZINHO não libera frete.
 function counterExample(id,role,old){
  return{id,role,old:old.map(([dir,unit])=>({dir,unit,stem:"irrelevante"}))};
 }
 const nameMismatch=counterExample("posto_de_combustivel","posto",[["out","corn"],["in","fertilizer"]]);
 const nameProfile=creator.companyCargoProfile(nameMismatch);
 const nameResult=creator.companyCargoCompatibility(nameMismatch,nameProfile,"milho","out",{id:"carga1"});
 assert.equal(nameResult,null,
  "Posto não deve expedir milho só porque uma permissão isolada menciona corn");
 assert.equal(creator.economicCoherence(nameMismatch,nameProfile,"milho","out").allowed,false,
  "Receber fertilizante e expedir milho não prova uma fazenda em um posto");
 assert.equal(creator.companyCargoCompatibility(nameMismatch,nameProfile,"cerveja","out",{id:"carga12"}),null);
 const namedSteel=counterExample("gerdau","siderurgica",[["out","adubo"],["in","corn"]]);
 const refused=[];
 assert.equal(creator.companyCargoCompatibility(namedSteel,creator.companyCargoProfile(namedSteel),
  "adubo","out",{id:"carga3"},refused),null,
  "Siderúrgica não deve expedir adubo com única evidência OUT desconectada");
 assert.equal(refused.length,1);
 // Caso oposto: só uma empresa originalmente rotulada de outro setor mas
 // reconfigurada para operar claramente um entreposto agro pode ser aceita.
 const farmMarket=counterExample("metal_nome_antigo","metalurgica",[
  ["out","adubo"],["out","fertilizante"],["out","equipagrico"],
  ["out","racao"],["in","milho"],["in","big_bag_seed"]]);
 const farmProfile=creator.companyCargoProfile(farmMarket);
 assert.equal(creator.economicCoherence(farmMarket,farmProfile,"adubo","out").allowed,true);
 assert.equal(creator.companyCargoCompatibility(farmMarket,farmProfile,
  "adubo","out",{id:"carga3"})?.kind,"direta");
 const steelActual=counterExample("siderurgica_verdadeira","siderurgica",[
  ["out","steel"],["out","adubo"],["in","iron_pipes"],["in","big_bag_seed"]]);
 assert.equal(creator.companyCargoCompatibility(steelActual,creator.companyCargoProfile(steelActual),
  "adubo","out",{id:"carga3"}),null,
  "Indústria com evidência real de aço não pode virar agroinsumos");

 const byNameOnly=counterExample("fazenda_milho","fazenda",[["out","diesel"],["in","petrol"]]);
 assert.equal(creator.companyCargoCompatibility(byNameOnly,creator.companyCargoProfile(byNameOnly),
  "milho","out",{id:"carga1"}),null,"O nome fazenda não inventa milho");
 const idOpaque=counterExample("xy987","desconhecida",[["out","bricks"],["in","wood"]]);
 assert.equal(creator.companyCargoCompatibility(idOpaque,creator.companyCargoProfile(idOpaque),
  "tijolo","out",{id:"carga13"})?.kind,"direta");
 const noCargo={id:"empresaA",role:"materiais",old:[{dir:"out",stem:"bricks",unit:null}]};
 assert.equal(creator.companyCargoCompatibility(noCargo,creator.companyCargoProfile(noCargo),
  "tijolo","out",{id:"carga13"}),null,
  "Nome do arquivo nunca pode substituir evidência cargo: real");


 // Um mapa só com postos e cargas incompatíveis ainda deve gerar o SCS
 // neutralizador integral, preservando suas empresas sem novas ofertas.
 const emptyWorld=new JSZip(),emptyCargo=new JSZip();
 emptyWorld.file("def/company/p0/editor/city.sii","SiiNunit\n{}\n");
 companyFile(emptyWorld,"p0","out","petroleum","diesel");
 companyFile(emptyWorld,"p0","in","refinery","petrol");
 emptyCargo.file("cargo/carga13.sui",
  'cargo_data : cargo.carga13 {\n name: "Tijolos"\n body_types[]: baixa\n}\n');
 const emptyWorldMap=await creator.loadMap(emptyWorld);
 const emptyWorldLoads=await creator.loadCargo(emptyCargo);
 const emptyWorldSim=creator.simulate(emptyWorldMap,emptyWorldLoads);
 assert.equal(emptyWorldSim.plan.size,0);
 assert.equal(emptyWorldSim.emptyCompanies.length,1);
 const emptyWorldArchive=await creator.build(emptyWorldMap,emptyWorldLoads,emptyWorldSim);
 const checkedEmpty=await JSZip.loadAsync(emptyWorldArchive.blob);
 for(const item of ["def/company/p0/out/petroleum.sii","def/company/p0/in/refinery.sii"]){
  assert.match(await checkedEmpty.file(item).async("text"),/cargo:\s*""/);
 }


 // Diferentes mapas com IDs opacos: nenhuma associação deve depender
 // do nome da empresa ou de listas fixas de empresas.
 const universalMap=new JSZip(),universalCargo=new JSZip();
 for(const id of ["origin_opaque","receiver_xyz","construction_shop","construction_work","fuel_station","unrelated"]){
  universalMap.file("def/company/"+id+"/editor/city.sii","SiiNunit\n{}\n");
 }
 companyFile(universalMap,"origin_opaque","out","crop","corn");
 companyFile(universalMap,"origin_opaque","in","input","fertilizer");
 companyFile(universalMap,"receiver_xyz","in","cereal","corn");
 companyFile(universalMap,"construction_shop","out","bricks","bricks");
 companyFile(universalMap,"construction_work","in","bricks","bricks");
 companyFile(universalMap,"fuel_station","out","diesel","diesel");
 companyFile(universalMap,"unrelated","out","steel_pipe","iron_pipes");
 universalCargo.file("cargo/carga1.sui",
   'cargo_data : cargo.carga1 {\n name: "Milho"\n body_types[]: alta\n}\n');
 universalCargo.file("cargo/carga13.sui",
   'cargo_data : cargo.carga13 {\n name: "Tijolos"\n body_types[]: baixa\n}\n');
 const universalMapRead=await creator.loadMap(universalMap);
 const universalCargoRead=await creator.loadCargo(universalCargo);
 const universal=creator.simulate(universalMapRead,universalCargoRead);
 assert.equal(universal.engine,"company-first");
 assert.equal(universal.skipped.length,0);
 assert.ok(universal.proof.find(x=>x.id==="carga1").sourceIds.includes("origin_opaque"));
 assert.ok(universal.proof.find(x=>x.id==="carga1").destIds.includes("receiver_xyz"));
 assert.ok(universal.proof.find(x=>x.id==="carga13").sourceIds.includes("construction_shop"));
 assert.ok(universal.proof.find(x=>x.id==="carga13").destIds.includes("construction_work"));
 assert.equal(universal.plan.has("fuel_station"),false);
 assert.equal(universal.plan.has("unrelated"),false);
 assert.ok(universal.emptyCompanies.includes("fuel_station"));
 const outputUniversal=await creator.build(universalMapRead,universalCargoRead,universal);
 const verifyUniversal=await JSZip.loadAsync(outputUniversal.blob);
 const oldFuel=verifyUniversal.file("def/company/fuel_station/out/diesel.sii");
 assert.ok(oldFuel,"Permissão antiga precisa continuar coberta");
 assert.match(await oldFuel.async("text"),/cargo:\s*""/);


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
  {id:"carga5",name:"Carga Pluma de Algodão",type:"algodao",from:"pluma",to:"pluma"},
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
  // Teste de integração: cargas só são obrigatórias quando a própria DEF
  // comprova a mercadoria, e não quando há apenas itens vagamente relacionados.
  const outs=item.id==="carga23"?["sorghum","corn"]:item.id==="carga9"?["steel_coils","chapaaco"]:[item.from];
  const ins=item.id==="carga23"?["sorghum"]:item.id==="carga9"?["metal_coils","ferroconst"]:[item.to];
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
 // Estes dados reais não contêm OUT explícito de ração, pluma ou bobinas.
 // A ausência de rota é o resultado correto: conhecimento geral não é prova
 // de atividade econômica de uma empresa específica.
 const mustSkip=["carga14","carga15","carga17","carga18","carga19","carga20","carga5","carga9"];
 for(const id of mustSkip)assert.ok(realSim.skipped.some(x=>x.id===id),
   "Não atribuir "+id+" sem mercadoria comprovada no OUT");
 assert.equal(realSim.plan.size,0,
  "Sem comprovante de destino de granito/rações/pluma/bobinas, não inventar rotas");
 const realScs=await creator.build(mapSubset,libSubset,realSim);
 const realArchive=await JSZip.loadAsync(realScs.blob);
 const ids=new Set(actualProfiles.map(x=>x.id));
 for(const [id]of missingEight){
  const src=realSim.proof.find(x=>x.id===id);
  if(mustSkip.includes(id)){
   assert.equal(src,undefined,"Carga indevidamente distribuída: "+id);
   continue;
  }
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
 assert.match(await obsolete.async("text"),/\bcargo\s*:\s*""/,
  "Arquivo original deve ter cargo vazio");
 assert.doesNotMatch(await obsolete.async("text"),/cargo\.corn|cargo\.milho_original/i);
 assert.match(creator.disableExistingCargo('SiiNunit\\n{\\n cargo_def: .a { cargo: "cargo.old" }\\n}'),
  /cargo:\s*""/);
 const allowed=new Set(["fazenda01","silo01","lojamaterial01","obra01"]);
 const cargos=new Set(["carga1","carga13"]);
 for(const pathname of Object.keys(output.files)){
  const c=pathname.match(/^def\/company\/([^/]+)\//);
  if(c)assert.ok(allowed.has(c[1]),"Empresa inventada: "+c[1]);
  const cargo=pathname.match(/^def\/company\/[^/]+\/(?:in|out)\/([^/]+)\.sii$/);
  if(cargo&&!cargos.has(cargo[1])){
   const contents=await output.file(pathname).async("text");
   assert.match(contents,/\bcargo\s*:\s*""/,
    "Arquivo IN/OUT antigo não está neutralizado: "+pathname);
  }
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
  assert.match(txt,/cargo:\s*""/);
  assert.doesNotMatch(txt,/cargo\.old_/);
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
