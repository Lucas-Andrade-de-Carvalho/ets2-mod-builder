#!/usr/bin/env python3
# ETS2 Company Logistics - gerador offline para Windows
# Apenas biblioteca padrao Python; conversao para EXE via GitHub Actions.
from __future__ import annotations
import argparse
import csv
import io
import json
import re
import sys
import traceback
import unicodedata
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST = {
 1:("milho","Milho"),2:("soja","Soja"),3:("adubo","Adubo"),
 4:("madeira","Madeira"),5:("algodao","Pluma de algodao"),
 6:("cimento","Cimento"),7:("batata","Sacos de batata"),
 8:("laranja","Sacos de laranja"),9:("bobina","Bobinas"),
 10:("cimento","Cimento paletizado"),11:("cimento","Cimento em cinta"),
 12:("cerveja","Cerveja"),13:("tijolo","Tijolos"),
 14:("granito","Granito 1"),15:("granito","Granito 2"),
 16:("palete","Palete Alto"),17:("racao","Racao mineral"),
 18:("racao","Xerem / racao"),19:("racao","Sacaria de racao"),
 20:("racao","Sacaria de racao 2"),21:("soja","Soja alta"),
 22:("milho","Milho alto"),23:("sorgo","Sorgo / alimentacao animal")
}
PATTERNS = {
 "milho":r"(?:^|_)(?:rbr_|ros_|cs_)?(?:milho|corn|maize)(?:_[ab])?$",
 "soja":r"(?:^|_)(?:rbr_|ros_|cs_)?(?:soja|soybean)(?:_[ab])?$",
 "adubo":r"adubo|fertiliz|npk|nitrato|ureia|urea",
 "madeira":r"madeir|tronco|toras?|logs?|timber|lumber|mdf|serrag",
 "algodao":r"algodao|pluma|cotton",
 "cimento":r"cimento|cement|argamassa|rejunte|concr|premold",
 "batata":r"batata|potato",
 "laranja":r"laranja|orange|citrus",
 "bobina":r"bobina|steel_coil|barraferro|barrasferro|ferro|sider|vergalhao|chapa_aco",
 "cerveja":r"cerveja|bebidas?|beer|ambev|brahma|skol|heineken|antartica|itaipava|refrigerant",
 "tijolo":r"tijolo|brick|telha|ceramica",
 "granito":r"granito|granitto|marmore|marble|pedra|brita|calcario|minerio",
 "racao":r"racao|xerem|animal_feed|feedmeal|farelo|sorgo",
 "sorgo":r"sorgo|sorghum",
 "palete":r"palete|pallet|madeirase|sucata|recicla"
}
ROLE_KEYWORDS = [
 ("reciclagem",r"recicl|sucata|sucatao|ferrovelho|sucateir|reaproveit"),
 ("cervejaria",r"ambev|cervej|brewery|cercrystal|heineken|brahma"),
 ("supermercado",r"super|mercado|atacadao|assai|bahamas|carrefour|compr_bem|compre_bem|extra_"),
 ("silo",r"silo|armazem|armz|cereal|comigo|caramuru|ac(s|z)_armazem"),
 ("cooperativa",r"cooper|coamo|coop|camda|cooperc"),
 ("agroinsumos",r"agro|adubo|fertil|agrish|agroce|agromais|casa_adubo"),
 ("fazenda",r"fazend|^faz|^farm|plant|rural|batata_f|^roca|agric"),
 ("fabrica_racao",r"racao|nutricao|animal_feed|brejeiro"),
 ("pecuaria",r"pecuar|gado|confin|boi|suino|frango|aves|criatorio"),
 ("madeireira",r"madeire|serraria|serra_|serrac|florest|^lenha"),
 ("textil",r"textil|tecel|fiac|algodoe|fiação"),
 ("cimenteira",r"cimento|cimenteir|votoran|intercement"),
 ("ceramica",r"ceram|olaria|tijol|telha"),
 ("pedreira",r"pedreira|quarry|basalto|extratora"),
 ("marmoraria",r"marmoraria|marmor|granito|granitos"),
 ("siderurgica",r"gerdau|cofer|arcel|sider|usiminas|steel|csn_"),
 ("metalurgica",r"metalurg|calha|cortedobra|aco|ferragem"),
 ("premoldados",r"premold|pre_mold|concret"),
 ("materiais",r"construsol|construm|material|casa_center|casaverde|dep_mat|construja|casa_mat"),
 ("obras",r"construcao|^constr|^cons_|obra|canteiro|batisse"),
 ("hortifruti",r"ceasa|hortif|sacolao|frut|banana|verdura"),
 ("alimentos",r"aliment|arcor|industria_alim|conservas"),
 ("atacadista",r"atacad|distrib|centro_dist|cd_|logistica|transpor"),
 ("automotiva",r"concession|veiculos|carros|auto|bmw|mercedes|scania"),
 ("posto",r"posto|combustivel|gasolina|petro|refinar")
]
DIRECTIONS = {
 "milho":({"fazenda","silo","cooperativa"},{"silo","cooperativa","fabrica_racao","agroinsumos"}),
 "soja":({"fazenda","silo","cooperativa"},{"silo","cooperativa","fabrica_racao","agroinsumos"}),
 "adubo":({"agroinsumos","atacadista"},{"fazenda","agroinsumos","cooperativa"}),
 "madeira":({"madeireira","materiais"},{"materiais","obras","premoldados","atacadista"}),
 "algodao":({"fazenda","cooperativa"},{"textil","cooperativa","atacadista"}),
 "cimento":({"cimenteira","materiais","premoldados"},{"materiais","obras","premoldados"}),
 "batata":({"fazenda","hortifruti","cooperativa"},{"hortifruti","supermercado","alimentos","atacadista","cooperativa"}),
 "laranja":({"fazenda","hortifruti","cooperativa"},{"hortifruti","supermercado","alimentos","atacadista","cooperativa"}),
 "bobina":({"siderurgica","metalurgica"},{"metalurgica","premoldados","obras","atacadista","automotiva"}),
 "cerveja":({"cervejaria","atacadista"},{"supermercado","atacadista","alimentos"}),
 "tijolo":({"ceramica","materiais"},{"materiais","obras"}),
 "granito":({"pedreira","marmoraria"},{"marmoraria","materiais","obras"}),
 "racao":({"fabrica_racao","agroinsumos","cooperativa"},{"pecuaria","fazenda","agroinsumos","cooperativa"}),
 "sorgo":({"fazenda","silo","cooperativa"},{"fabrica_racao","pecuaria","cooperativa","silo"}),
 "palete":({"madeireira"},{"reciclagem"})
}
RE_CARGO_FIELD = re.compile(r'(?m)^(\s*cargo\s*:\s*)(?:"[^"\r\n]*"|[a-zA-Z0-9_.-]+)')
RE_CARGO_UNIT = re.compile(r'\bcargo_data\s*:\s*cargo\.([a-z][\w]*)\b',re.I)
RE_COMPANY_PATH = re.compile(r'(?:^|/)def/company/([a-z0-9_]+)/(?:(in|out|editor)/)?([^/]+)$',re.I)
RE_CARGO_PATH = re.compile(r'(?:^|/)def/cargo/([a-z0-9_]+)(?:\.(?:sii|sui)|/([^/]+))$',re.I)
RE_TRAILER_BODY = re.compile(r'(?m)^\s*body_type\s*:\s*["'+"']?([a-z0-9_]+)",re.I)
RE_CARGO_BODY = re.compile(r'(?m)^\s*body_types(?:\[\d*\])?\s*:\s*["'+"']?([a-z0-9_]+)",re.I)

def normal(text):
    return "".join(c for c in unicodedata.normalize("NFKD",str(text).lower()) if not unicodedata.combining(c))

def clean_path(raw):
    path=str(raw).replace("\\","/").lstrip("/")
    if ".." in path.split("/") or path.startswith("./"): return None
    return path

def canonical_path(raw):
    path=clean_path(raw)
    if not path: return None
    m=re.search(r'(?:^|/)(def/(?:company|cargo|vehicle)/.+)$',path,re.I)
    return m.group(1).lower() if m else None

def read_sii(blob):
    return blob.decode("utf-8-sig","replace")

def cargo_tokens(text):
    return [x.lower() for x in re.findall(r'\bcargo\s*:\s*"?cargo\.([a-z0-9_]+)"?',text,re.I)]

def product_types(tokens):
    out=set()
    for token in tokens:
        n=normal(token)
        for label,pattern in PATTERNS.items():
            if re.search(pattern,n):out.add(label)
    return out

def zip_members(path, wanted=None):
    """Le ZIPs e .scs ZIP; nunca altera os originais."""
    path=Path(path)
    if path.is_dir():
        entries=((str(p.relative_to(path)).replace("\\","/"),p.read_bytes()) for p in path.rglob("*") if p.is_file())
    else:
        if not zipfile.is_zipfile(path):
            raise ValueError(f"'{path.name}' nao e arquivo ZIP/SCS ZIP legivel. Extraia previamente com o SCS Extractor oficial e selecione a pasta extraida.")
        zf=zipfile.ZipFile(path)
        infos=[x for x in zf.infolist() if not x.is_dir()]
        if len(infos)>80000 or sum(x.file_size for x in infos)>1_400_000_000:
            zf.close();raise ValueError(f"Arquivo excessivo ou suspeito: {path.name}")
        entries=((x.filename,zf.read(x)) for x in infos if x.file_size<8_000_000)
    out={}
    try:
        for name,data in entries:
            c=canonical_path(name)
            if c and (wanted is None or wanted(c)):
                if c in out and out[c]!=data:
                    raise ValueError(f"Colisao de caminhos no mesmo arquivo: {c} em {path.name}")
                out[c]=data
    finally:
        if not path.is_dir():zf.close()
    return out

@dataclass
class Company:
    name:str
    files:dict=field(default_factory=dict)
    old_in:set=field(default_factory=set)
    old_out:set=field(default_factory=set)
    role:str="desconhecida"
    explicit_role:bool=False

def classify_company(c):
    n=normal(c.name)
    # Identificadores precisos sao preferiveis a deducoes por uma palavra isolada.
    for role,pat in ROLE_KEYWORDS:
        if re.search(pat,n):
            c.role=role;c.explicit_role=True;return
    incoming=product_types(c.old_in);outgoing=product_types(c.old_out)
    if "cerveja" in outgoing and "cerveja" not in incoming:c.role="cervejaria"
    elif "adubo" in outgoing and incoming & {"milho","soja","adubo"}:c.role="agroinsumos"
    elif incoming & {"milho","soja"} and "racao" in outgoing:c.role="fabrica_racao"
    elif incoming & {"milho","soja"} and outgoing & {"milho","soja"}:c.role="silo"
    elif "adubo" in incoming and outgoing & {"milho","soja","batata","laranja"}:c.role="fazenda"
    elif "madeira" in outgoing and not incoming & {"cimento","tijolo"}:c.role="madeireira"
    elif "granito" in outgoing and not incoming & {"granito","cimento"}:c.role="pedreira"
    elif "bobina" in outgoing and "bobina" not in incoming:c.role="siderurgica"
    elif "cimento" in incoming and "cimento" in outgoing:c.role="materiais"
    elif "cerveja" in incoming and "cerveja" not in outgoing:c.role="supermercado"

def extract_map(path):
    archive=zip_members(path)
    companies={}
    old_file_count=0
    legacy=[]
    for p,raw in archive.items():
        m=RE_COMPANY_PATH.search(p)
        if not m:continue
        id,dir,filename=m.groups()
        c=companies.setdefault(id,Company(id))
        if dir in {"in","out"} and filename.lower().endswith((".sii",".sui")):
            old_file_count+=1;c.files[p]=raw
            ct=cargo_tokens(read_sii(raw))
            (c.old_in if dir=="in" else c.old_out).update(ct)
        elif dir is None and filename.endswith(".sii"):
            if re.search(r'(?m)^\s*(in_cargo|out_cargo)(?:\[\d*\])?\s*:',read_sii(raw)):
                legacy.append(p)
    if not companies or old_file_count==0:
        raise ValueError(f"{Path(path).name}: nenhuma pasta def/company/<empresa>/in|out com cargas foi encontrada")
    if legacy:raise ValueError("Company legada com in_cargo/out_cargo requer tratamento especifico: "+", ".join(legacy[:5]))
    for c in companies.values():classify_company(c)
    return companies,old_file_count

def cargo_inventory(mods):
    records={}
    trailers=defaultdict(set)
    owned_bodies=set()
    for source,archive in mods:
        for path,raw in archive.items():
            if path.startswith("def/vehicle/trailer_owned/") and path.endswith((".sii",".sui")):
                owned_bodies.update(RE_TRAILER_BODY.findall(read_sii(raw)))
            m=RE_CARGO_PATH.search(path)
            if not m or not path.endswith((".sii",".sui")):continue
            cid,sub=m.groups();txt=read_sii(raw)
            if sub is None:
                ids=RE_CARGO_UNIT.findall(txt)
                for id in ids:
                    if id.lower()!=cid.lower():continue
                    body=set(RE_CARGO_BODY.findall(txt))
                    if cid in records and records[cid]["body"]!=body:
                        raise ValueError(f"Definicoes conflitantes do cargo {cid} entre arquivos do reboque")
                    records[cid]={"source":source,"path":path,"raw":raw,"body":body,
                                  "valuable":bool(re.search(r'\bvaluable\s*:\s*true\b',txt,re.I)),
                                  "adr":bool(re.search(r'\badr_class\s*:\s*[1-9]',txt,re.I))}
            elif re.search(r'\btrailer_def\s*:',txt,re.I):
                trailers[cid].update(RE_TRAILER_BODY.findall(txt))
    return records,trailers,owned_bodies

def permits(c,category,dir):
    role=c.role
    observed=product_types(c.old_out if dir=="out" else c.old_in)
    reverse=product_types(c.old_in if dir=="out" else c.old_out)
    allow=DIRECTIONS[category][0 if dir=="out" else 1]
    if role not in allow: return None
    # Proibir falsa classificacao de recicladora / madeireira, e protecao contra dispersao universal.
    if category=="palete":
        if dir=="out" and role=="madeireira":return "madeireira: origem de paletes"
        if dir=="in" and role=="reciclagem":return "reciclagem/sucatao: destino de paletes"
        return None
    if role=="desconhecida":return None
    if category in observed:
        return "documental: mercadoria/familia no "+dir.upper()+" original"
    if category=="sorgo" and "milho" in observed:
        return "inferida: movimentacao comprovada de cereais"
    if category=="racao":
        if dir=="in" and role=="fazenda" and ("racao" in reverse or "racao" in observed):
            return "inferida: fazenda com evidencias de alimentacao animal"
        if dir=="in" and role=="pecuaria":return "economica: criacao animal compra racao"
        if dir=="out" and role=="fabrica_racao":return "economica: fabricacao de racao"
        if dir=="out" and role=="agroinsumos" and ("adubo" in observed or "racao" in reverse):
            return "inferida: revenda agropecuaria"
        return None
    if category=="algodao":
        if "algodao" in observed or "algodao" in reverse:return "documental: algodao presente na DEF"
        return None
    if category=="granito" and role=="marmoraria" and dir=="out" and "granito" not in observed:
        return None
    if category=="bobina" and role=="obras" and "bobina" not in observed and "bobina" not in reverse:
        return None
    if category=="cerveja" and dir=="out" and role=="atacadista" and "cerveja" not in observed:
        return None
    if category=="madeira" and dir=="out" and role=="materiais" and "madeira" not in observed:
        return None
    if category=="adubo" and dir=="out" and role=="atacadista" and "adubo" not in observed:
        return None
    if category=="cimento" and dir=="out" and role=="premoldados" and "cimento" not in observed:
        return None
    if category=="milho" or category=="soja":
        if dir=="out" and role=="fazenda" and not (observed & {"milho","soja"} or reverse & {"milho","soja"}):
            return None
    if role=="fazenda" and dir=="out" and category in {"batata","laranja","sorgo"}:
        if not (observed & {category,"milho","soja"} or reverse & {category}):
            return None
    if role in {"supermercado","materiais","hortifruti","agroinsumos","silo","cooperativa"}:
        return "inferida: compra/venda compativel com a atividade e capacidade"
    return "inferida: utilizacao/producao compativel com a atividade"

def cargo_sii(cid):
    return f'SiiNunit\n{{\n cargo_def : .{cid} {{\n  cargo: "cargo.{cid}"\n }}\n}}\n'.encode("utf-8")

def neutralize(raw,path):
    txt=read_sii(raw)
    if not RE_CARGO_FIELD.search(txt):
        if re.search(r'\bcargo_def\s*:',txt,re.I):
            raise ValueError("Nao foi possivel neutralizar cargo_def sem campo cargo: "+path)
        return raw
    result=RE_CARGO_FIELD.sub(lambda m:m.group(1)+'""',txt)
    if cargo_tokens(result):
        raise ValueError("Cargo antigo ainda ativo apos neutralizacao: "+path)
    return result.encode("utf-8")

def cargo_override(record):
    txt=read_sii(record["raw"])
    if record["valuable"]:
        txt=re.sub(r'(?im)^(\s*valuable\s*:\s*)true\b',r'\1false',txt)
    # Reducao seletiva; nao altera corpo/modelos, que devem continuar no mod original.
    if re.search(r'(?im)^\s*prob_coef\s*:',txt):
        txt=re.sub(r'(?im)^(\s*prob_coef\s*:\s*)[\d.]+',r'\g<1>0.08',txt)
    else:
        # Campo deve estar dentro de cargo_data; inserido imediatamente depois da abertura.
        txt=re.sub(r'(\bcargo_data\s*:\s*cargo\.carga16\s*\{)',r'\1\n prob_coef: 0.08',txt,count=1,flags=re.I)
    return txt.encode("utf-8")

def write_report(outdir,name,result):
    with open(outdir/(name+"_auditoria.json"),"w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    with open(outdir/(name+"_empresas.csv"),"w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f,delimiter=";")
        writer.writerow(["empresa","setor","in_novos","out_novos","in_originais","out_originais"])
        for row in result["empresas"]:
            writer.writerow([row[k] for k in ("empresa","setor","in_novos","out_novos","in_originais","out_originais")])

def generate(inputs,output,log=lambda s:None, fix_skills=True):
    outdir=Path(output);outdir.mkdir(parents=True,exist_ok=True)
    log("Lendo arquivos originais do Librelato...")
    sources=[]
    for label,path in [("MOD PRINCIPAL",inputs["mod"]),("DEF 1",inputs["def1"]),("DEF 2",inputs["def2"])]:
        arc=zip_members(path)
        if not arc:raise ValueError(f"{label}: nenhuma definicao def/ legivel encontrada")
        sources.append((label,arc))
        log(f"{label}: {len(arc)} definicoes")
    records,trailers,owned=cargo_inventory(sources)
    errors=[];warnings=[]
    for n,(category,description) in MANIFEST.items():
        id=f"carga{n}"
        r=records.get(id)
        if not r:errors.append(f"{id} ({description}): cargo_data ausente no reboque");continue
        if not r["body"]:errors.append(f"{id}: body_types ausente no cargo_data");continue
        suitable=trailers.get(id,set())&r["body"]
        if not suitable:errors.append(f"{id}: sem trailer_def e body_type correspondentes ({sorted(r['body'])} x {sorted(trailers.get(id,set()))})")
        if r["adr"]:warnings.append(f"{id}: exige habilidade ADR; verificar se intencional")
        if r["valuable"]:warnings.append(f"{id}: valuable=true"+(" (correcao somente no mod gerado)" if fix_skills else " (habilidade de alto valor exigida)"))
    if not owned:
        warnings.append("Nao foram encontrados body_types de trailer_owned; verificar configuracao especifica no jogo.")
    else:
        used=set().union(*(r["body"] for id,r in records.items() if id in {f"carga{n}" for n in MANIFEST}))
        if not used & owned:errors.append("Nenhum body_type das 23 cargas coincide com os body_types do mod de reboque proprio")
    if errors:
        outdir.joinpath("FALHA_DIAGNOSTICO.txt").write_text(
            "GERACAO BLOQUEADA: corrigir problemas tecnicos antes de entregar Companies.\n\n"+
            "\n".join(errors)+"\n\nAVISOS\n"+"\n".join(warnings),encoding="utf-8")
        raise ValueError("Diagnostico tecnico bloqueou geracao:\n- "+"\n- ".join(errors[:12]))
    log("Cargo_data, body_types e trailer_def: verificacoes essenciais aprovadas.")
    results=[]
    for name,path in inputs["maps"].items():
        log("Analisando mapa "+name+"...")
        companies,count=extract_map(path)
        work={};evidence=[];bycargo={}
        for n,(category,title) in MANIFEST.items():
            id=f"carga{n}"
            outs=[];ins=[]
            for c in companies.values():
                for direction,results_list in (("out",outs),("in",ins)):
                    why=permits(c,category,direction)
                    if why:results_list.append(c.name)
                    if why:evidence.append({"empresa":c.name,"direcao":direction,"carga":id,"categoria":category,"justificativa":why})
            bycargo[id]={"nome":title,"origens":len(outs),"destinos":len(ins),
                         "origens_lista":outs,"destinos_lista":ins}
            # Nao inventar rotas para completar 23/23.
            if not outs or not ins: warnings.append(f"{name} / {id}: sem cadeia economica completa (OUT={len(outs)}, IN={len(ins)})")
            for c_id in outs:work.setdefault(c_id,{"in":set(),"out":set()})["out"].add(id)
            for c_id in ins:work.setdefault(c_id,{"in":set(),"out":set()})["in"].add(id)
        output_files={}
        for c in companies.values():
            for p,raw in c.files.items():
                output_files[p]=neutralize(raw,p)
        for cid,dirs in work.items():
            for direction in ("in","out"):
                for id in dirs[direction]:
                    output_files[f"def/company/{cid}/{direction}/{id}.sii"]=cargo_sii(id)
        # As cargas precisam permanecer disponiveis: retirar exigencia injustificada
        # de skill somente no mod complementar; originais NUNCA sao editados.
        if fix_skills:
            for n in MANIFEST:
                id=f"carga{n}"
                record=records[id]
                if record["valuable"] or id=="carga16":
                    output_files[record["path"]]=(cargo_override(record) if id=="carga16" else
                      re.sub(r'(?im)^(\s*valuable\s*:\s*)true\b',r'\1false',read_sii(record["raw"])).encode("utf-8"))
        dest=outdir/("ETS2_"+name.upper().replace(" ","_")+"_COMPANY.scs")
        with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p,raw in sorted(output_files.items()):z.writestr(p,raw)
        with zipfile.ZipFile(dest) as z:
            if z.testzip() is not None:raise ValueError("Falha na integridade do ZIP: "+str(dest))
            paths=set(z.namelist())
            if not all(p in paths for c in companies.values() for p in c.files):
                raise ValueError("Arquivo original IN/OUT ficou sem cobertura: "+str(dest))
            for id,info in bycargo.items():
                for company in info["origens_lista"]:
                    if f"def/company/{company}/out/{id}.sii" not in paths:raise ValueError("Permissao OUT ausente")
                for company in info["destinos_lista"]:
                    if f"def/company/{company}/in/{id}.sii" not in paths:raise ValueError("Permissao IN ausente")
        rows=[]
        for cid,c in sorted(companies.items()):
            selected=work.get(cid,{"in":set(),"out":set()})
            rows.append({"empresa":cid,"setor":c.role,"in_novos":",".join(sorted(selected["in"])),
                         "out_novos":",".join(sorted(selected["out"])),"in_originais":",".join(sorted(c.old_in)),
                         "out_originais":",".join(sorted(c.old_out))})
        data={"mapa":name,"empresas":rows,"total_empresas":len(companies),
              "empresas_atendidas":len(work),"arquivos_inout_originais":count,
              "arquivos_inout_gerados":sum(len(x["in"])+len(x["out"]) for x in work.values()),
              "cadeias":bycargo,"evidencias":evidence,"avisos":list(warnings),
              "validacao":"SCS ZIP, paths IN/OUT, manifesto, cargo_data, trailer_def; nao e teste dentro do ETS2"}
        write_report(outdir,name,data)
        log(name+": "+str(len(companies))+" empresas, "+str(len(work))+" com cargas e "+
            str(data["arquivos_inout_gerados"])+" permissões.")
        results.append((name,str(dest),data))
    outdir.joinpath("LEIA_PRIMEIRO.txt").write_text(
        "ETS2 COMPANY LOGISTICS - GERADOR OFFLINE\n\n"+
        "1. Utilize somente a Company do mapa ativo.\n"+
        "2. Mantenha o mod principal do Librelato ativo.\n"+
        "3. Desative DEF Company 1 e DEF Company 2 antigas, quando forem complementos conflitantes.\n"+
        "4. Deixe o novo SCS acima das DEFs do mapa e do reboque.\n"+
        "5. Teste carrocerias Grade Alta e Grade Baixa e atualize economia.\n"+
        "6. O Mercado de Cargas de reboque PROPRIO exige carroceria e configuracao correspondente.\n"+
        "7. Se o mercado ficar vazio, anexe game.log.txt e dados da configuracao instalada.\n"+
        "ATENCAO: analise estatica nao prova ofertas no jogo.\n\n"+
        "\n".join(warnings),encoding="utf-8")
    return results

def run_gui():
    import tkinter as tk
    from tkinter import filedialog,messagebox,ttk
    root=tk.Tk();root.title("ETS2 Company Logistics - Gerador Offline");root.geometry("930x650")
    frame=ttk.Frame(root,padding=16);frame.pack(fill="both",expand=True)
    ttk.Label(frame,text="ETS2 | Company Logistics — Librelato",font=("Segoe UI",16,"bold")).pack(anchor="w")
    ttk.Label(frame,text="Escolha os 7 arquivos originais. Nenhum arquivo enviado ou alterado.",wraplength=850).pack(anchor="w",pady=(2,16))
    widgets={}
    fields=[
       ("mod","Mod principal Librelato (.scs)"),
       ("def1","DEF Company 1 original (.scs)"),
       ("def2","DEF Company 2 original (.scs)"),
       ("txt","TXT com a lista das 23 cargas"),
       ("minas","Mapa Minas Gerais (.zip)"),
       ("eldorado","Mapa Eldorado (.zip)"),
       ("rbr","Mapa RBR (.zip)"),
       ("output","Pasta de saida")
    ]
    for key,label in fields:
        row=ttk.Frame(frame);row.pack(fill="x",pady=4)
        ttk.Label(row,text=label,width=35).pack(side="left")
        value=tk.StringVar();widgets[key]=value
        ttk.Entry(row,textvariable=value).pack(side="left",fill="x",expand=True,padx=6)
        def choose(k=key,v=value):
            if k=="output":p=filedialog.askdirectory()
            else:p=filedialog.askopenfilename(title="Selecione "+k)
            if p:v.set(p)
        ttk.Button(row,text="Selecionar",command=choose).pack(side="right")
    fix_var=tk.BooleanVar(value=True)
    ttk.Checkbutton(frame,text="Remover exigencia de Carga de Alto Valor das 23 cargas comuns (na Company gerada, nao no original)",variable=fix_var).pack(anchor="w",pady=(9,4))
    console=tk.Text(frame,height=12,wrap="word",state="disabled")
    console.pack(fill="both",expand=True,pady=8)
    def log(msg):
        console.configure(state="normal");console.insert("end",msg+"\n")
        console.see("end");console.configure(state="disabled");root.update_idletasks()
    def start():
        try:
            needed=[key for key,_ in fields]
            if not all(widgets[k].get().strip() for k in needed):
                messagebox.showerror("Arquivos incompletos","Selecione os sete arquivos e a pasta de saida.");return
            with open(widgets["txt"].get(),encoding="utf-8-sig") as f:
                manifest=f.read()
            for n in MANIFEST:
                if not re.search(r"(?m)^\s*carga"+str(n)+r"\s*[:=\-]",manifest,re.I):
                    raise ValueError(f"TXT nao identifica carga{n}; confira se e a lista correta")
            inp={"mod":widgets["mod"].get(),"def1":widgets["def1"].get(),
                 "def2":widgets["def2"].get(),
                 "maps":{"Minas_Gerais":widgets["minas"].get(),
                         "Eldorado":widgets["eldorado"].get(),
                         "RBR":widgets["rbr"].get()}}
            data=generate(inp,widgets["output"].get(),log=log,fix_skills=fix_var.get())
            messagebox.showinfo("Concluido",f"Gerados {len(data)} arquivos SCS. Confira as auditorias e teste no ETS2.")
        except Exception as ex:
            log("ERRO: "+str(ex))
            messagebox.showerror("Geracao interrompida",str(ex))
    ttk.Button(frame,text="ANALISAR E GERAR 3 COMPANIES",command=start).pack(pady=8)
    root.mainloop()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--cli",action="store_true")
    for x in ("mod","def1","def2","txt","minas","eldorado","rbr","output"):
        parser.add_argument("--"+x,required=False)
    args=parser.parse_args()
    if not args.cli:run_gui();return
    if any(getattr(args,x) is None for x in ("mod","def1","def2","txt","minas","eldorado","rbr","output")):
        parser.error("Em modo --cli, informe os 8 caminhos.")
    original=Path(args.txt).read_text(encoding="utf-8-sig")
    for n in MANIFEST:
        if not re.search(r"(?m)^\s*carga"+str(n)+r"\s*[:=\-]",original,re.I):
            parser.error(f"TXT incompleto: falta carga{n}")
    inp={"mod":args.mod,"def1":args.def1,"def2":args.def2,"maps":
         {"Minas_Gerais":args.minas,"Eldorado":args.eldorado,"RBR":args.rbr}}
    generate(inp,args.output,print)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("ERRO:",exc,file=sys.stderr);sys.exit(1)
