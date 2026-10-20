#!/usr/bin/env node
"use strict";
// Atualiza somente o motor da aba Criação de Companys dentro do HTML.
// Requer Node.js apenas para desenvolvimento; o HTML final funciona offline.
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const sourcePath=path.join(root,"creator_tab.js");
const htmlPath=path.join(root,"index.html");
const engine=fs.readFileSync(sourcePath,"utf8").trim();
const html=fs.readFileSync(htmlPath,"utf8");
const blocks=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if(blocks.length!==3)throw Error("O HTML não tem os 3 blocos esperados; sincronização cancelada.");
const old=blocks[2][0],replacement="<script>"+engine+"</script>";
const result=html.replace(old,()=>replacement);
if(result===html){
 process.stdout.write("Já sincronizado.\n");
 process.exit(0);
}
if(process.argv.includes("--check")){
 process.stderr.write("Motor embutido no index.html está desatualizado. Rode node scripts/sync-company-engine.cjs\n");
 process.exit(1);
}
fs.writeFileSync(htmlPath,result);
process.stdout.write("Motor incorporado ao index.html sem alterar as outras abas.\n");
