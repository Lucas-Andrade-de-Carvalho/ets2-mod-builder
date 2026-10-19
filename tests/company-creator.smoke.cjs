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

 const conflict=new JSZip();
 conflict.file("def/company/fazenda01/editor/city.sii","SiiNunit\n{}\n");
 conflict.file("pacote.scs",f.originalMap);
 await assert.rejects(creator.loadMap(conflict),/duplicada/);

 const cargoOuter=await JSZip.loadAsync(f.cargoFile);
 assert.equal((await creator.loadCargo(cargoOuter)).cargos.size,2);
 element("companyCreateMapFile").files=[f.mapFile];
 element("companyCreateCargoFile").files=[f.cargoFile];

 assert.equal(element("companyCreateDownload").hidden,true);
 await element("companyCreateGenerate").listeners.click();
 assert.match(element("companyCreateStatus").textContent,/Company pronta:/);
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
 assert.equal(output.file("def/company/fazenda01/out/milho_original.sii"),null);
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
 element("companyCreateDownload").listeners.click();
 assert.equal(downloadClicks,2,"Botão de download deve permitir repetição");
 assert.match(filename,/\.scs$/i);
 element("companyCreateMapFile").listeners.change();
 assert.equal(element("companyCreateDownload").hidden,true,"Troca de arquivo invalida download");
 console.log("OK: ZIP raiz e duplamente aninhado; HashFS; colisão; carrocerias; integridade SCS; download.");
}
main().catch(error=>{console.error(error);process.exitCode=1});
