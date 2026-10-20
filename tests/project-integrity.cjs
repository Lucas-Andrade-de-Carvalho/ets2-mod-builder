"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=name=>fs.readFileSync(path.join(root,name),"utf8");
const html=read("index.html"),engine=read("creator_tab.js");
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,3,"O HTML deve manter exatamente os scripts esperados das seis abas");
assert.equal(scripts[2][1].trim(),engine.trim(),
 "ERRO: script de Criação de Companys no HTML não corresponde a creator_tab.js");
for(let i=0;i<scripts.length;i++)
 new vm.Script(scripts[i][1],{filename:"index-inline-"+i+".js"});
for(const file of ["creator_tab.js","engine_universal.js","scs_company_catalog.js"])
 new vm.Script(read(file),{filename:file});
const pages=["files","creator","companies","logistics","chains","export"];
for(const id of pages){
 assert.match(html,new RegExp('data-page="'+id+'"'),"Aba ausente: "+id);
 assert.match(html,new RegExp('<section id="'+id+'"'),"Conteúdo da aba ausente: "+id);
}
for(const id of ["companyCreateMapFile","companyCreateCargoFile","companyCreateGenerate",
                 "companyCreateDownload","companyCreateStatus","companyCreateReport"])
 assert.ok(html.includes('id="'+id+'"'),"Controle de Company ausente: "+id);
assert.ok(!html.includes('<script src="engine_universal.js"'),
 "O motor legado engine_universal.js não pode ser carregado por engano");
assert.match(engine,/function parseCompanyCargoUnits\(/);
assert.match(engine,/function maskSiiComments\(/);
assert.match(engine,/function companyCargoProfile\(/);
assert.match(engine,/function economicCoherence\(/);
assert.match(engine,/function disableExistingCargo\(/);
assert.match(engine,/const ENGINE_BUILD=/);
console.log("OK: 6 abas, motor embutido sincronizado, scripts íntegros, parser e segurança presentes.");
