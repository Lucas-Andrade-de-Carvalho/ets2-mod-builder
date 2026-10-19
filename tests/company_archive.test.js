/*
 * ETS2 Company Logistics — regression tests for Company ZIP layouts.
 * In a browser, open index.html, then run this script in DevTools.
 * Usage: await runCompanyArchiveTests()
 * This script reads no local files and does not change map data.
 */
window.runCompanyArchiveTests=async function runCompanyArchiveTests(){
 "use strict";
 const api=window.CompanyCreatorTest, Zip=window.JSZip;
 if(!api||!Zip)throw Error("Abra index.html antes de executar os testes.");
 const results=[];
 function check(condition,message){
  if(!condition)throw Error("TESTE FALHOU: "+message);
 }
 function addCompany(zip,company="alc_cle",prefix=""){
  zip.file(prefix+company+"/editor/clementina.sii","SiiNunit\n{}\n");
  zip.file(prefix+company+"/out/alcoil.sii",'SiiNunit\n{\n cargo_def: .x { cargo: "cargo.alcoil" }\n}\n');
  zip.file(prefix+company+"/in/tanquevazio.sii",'SiiNunit\n{\n cargo_def: .x { cargo: "cargo.tanquevazio" }\n}\n');
  zip.file(prefix+company+".sii","SiiNunit\n{}\n");
 }
 async function runLayout(label,prepare){
  const zip=new Zip();
  await prepare(zip);
  const map=await api.loadMap(zip);
  const paths=new Set([...map.files.values()].map(x=>x.p));
  check(map.companies.size===1,label+" — total de empresas");
  check(map.companies.has("alc_cle"),label+" — ID original");
  for(const required of [
   "def/company/alc_cle/editor/clementina.sii",
   "def/company/alc_cle/in/tanquevazio.sii",
   "def/company/alc_cle/out/alcoil.sii",
   "def/company/alc_cle.sii"
  ])check(paths.has(required),label+" — "+required);
  results.push(label);
 }
 await runLayout("pasta alc_cle/ sem company/",z=>addCompany(z));
 await runLayout("company/alc_cle/",z=>addCompany(z,"alc_cle","company/"));
 await runLayout("def/company/alc_cle/",z=>addCompany(z,"alc_cle","def/company/"));
 await runLayout("def/alc_cle/",z=>addCompany(z,"alc_cle","def/"));
 await runLayout("exportacao/alc_cle/",z=>addCompany(z,"alc_cle","MeuMapa/exportacao/"));
 await runLayout("ZIP interno",async z=>{
  const nested=new Zip();addCompany(nested);
  z.file("modificacoes/company.scs",await nested.generateAsync({type:"uint8array"}));
 });
 await runLayout("manifesto externo + ZIP interno",async z=>{
  z.file("company.sii","SiiNunit\n{}\n");
  const nested=new Zip();addCompany(nested);
  z.file("company-files.zip",await nested.generateAsync({type:"uint8array"}));
 });
 const falsePositive=new Zip();
 falsePositive.file("vehicle/truck/editor/test.sii","SiiNunit\n{}\n");
 let invalidRejected=false;
 try{await api.loadMap(falsePositive)}catch(e){invalidRejected=/Nenhuma DEF Company reconhecida/.test(e.message)}
 check(invalidRejected,"não confundir modelos com empresas");
 results.push("arquivos que não são Company rejeitados");
 const a=new Zip(),b=new Zip();addCompany(a);addCompany(b);
 b.file("alc_cle/out/alcoil.sii",'SiiNunit\n{\ncargo_def : .t {cargo: "cargo.combustivel"}\n}\n');
 const aHash=await api.mapFingerprint(await api.loadMap(a));
 const bHash=await api.mapFingerprint(await api.loadMap(b));
 check(aHash!==bHash,"ZIPs diferentes devem ter identificadores diferentes");
 results.push("identificador distingue conteúdo");
 const duplicated=new Zip();addCompany(duplicated);addCompany(duplicated,"alc_cle","company/");
 let duplicateBlocked=false;
 try{await api.loadMap(duplicated)}catch(e){duplicateBlocked=/Definição duplicada/.test(e.message)}
 check(duplicateBlocked,"não sobrescrever definições duplicadas");
 results.push("colisões bloqueadas");
 return{ok:true,total:results.length,results};
};
