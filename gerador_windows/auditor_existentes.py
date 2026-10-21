#!/usr/bin/env python3
"""Auditoria conservadora de Company SCS existentes, offline e com trilha de decisao.

Nunca modifica o SCS de entrada; usa a DEF original do mapa como evidencia.
Funciona com gerador.py no EXE PyInstaller sem bibliotecas adicionais.
"""
from __future__ import annotations
import csv
import hashlib
import json
import os
import re
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path

SII_EXT=(".sii",".sui")
CARGO_FIELD = re.compile(r'(?im)^(\s*cargo\s*:\s*)"?cargo\.(carga(?:[1-9]|1[0-9]|2[0-3]))"?(?=\s*(?:#.*)?$)')
OTHER_FIELD = re.compile(r'(?im)^\s*cargo\s*:\s*"?cargo\.([a-z0-9_]+)"?')
ROLE_SAFE_PRODUCERS={
    "siderurgica","cervejaria","cimenteira","ceramica","pedreira",
    "madeireira","fabrica_racao","fazenda_batata","fazenda_laranja"
}
ROLE_SAFE_CONSUMERS={
    "supermercado","obras","premoldados","automotiva_fabrica",
    "pecuaria","textil","metalurgica","reciclagem","marmoraria",
    "bananal","fabrica_racao"
}
def inventory_archive(g, path):
    p=Path(path)
    if p.is_dir():
        members=((str(f.relative_to(p)).replace("\\","/"),f.read_bytes())
                 for f in sorted(p.rglob("*")) if f.is_file())
    else:
        if not zipfile.is_zipfile(p):
            raise ValueError("A Company existente nao e ZIP/SCS legivel: "+p.name)
        z=zipfile.ZipFile(p)
        files=[a for a in z.infolist() if not a.is_dir()]
        if len(files)>100000 or sum(a.file_size for a in files)>1_600_000_000:
            z.close();raise ValueError("Company excede os limites seguros de processamento")
        members=((a.filename,z.read(a)) for a in files if a.file_size<9_000_000)
    result={}
    try:
        for original,raw in members:
            clean=g.clean_path(original)
            if not clean:raise ValueError("Caminho irregular: "+original)
            canonical=g.canonical_path(clean)
            path=(canonical or clean).lower()
            if path in result and result[path]!=raw:
                raise ValueError("Colisao de arquivo SCS: "+path)
            result[path]=raw
    finally:
        if not p.is_dir():z.close()
    return result

def file_active_ids(g, raw):
    text=g.read_sii(raw)
    return [v.lower() for v in CARGO_FIELD.findall(text)]

def disable_id(g, raw, cargo_id):
    text=g.read_sii(raw)
    removed=[0]
    def transform(m):
        if m.group(2).lower()!=cargo_id:
            return m.group(0)
        removed[0]+=1
        return m.group(1)+'""'
    out=CARGO_FIELD.sub(transform,text)
    if removed[0]<1:raise ValueError("Cargo nao localizado ao neutralizar: "+cargo_id)
    return out.encode("utf-8")

def safe_reason(g, c,cat,direction,map_name):
    why=(g.eldorado_permit(c,cat,direction)
         if map_name.lower()=="eldorado"
         else g.permits(c,cat,direction))
    return why

def explicit_confidence(c):
    return c.explicit_role and c.role not in {"desconhecida","hub_generico","atacadista","hortifruti"}

def can_add(g,c,cat,direction,map_name):
    why=safe_reason(g,c,cat,direction,map_name)
    if not why or not explicit_confidence(c):return None
    if c.role in {"transportadora","bananal"} and direction=="out":return None
    original=(g.eldorado_translate if map_name.lower()=="eldorado"
              else g.product_types)
    evidence=cat in original(c.old_out if direction=="out" else c.old_in)
    bidirectional=cat in original(c.old_out|c.old_in)
    role_specific=(c.role in (ROLE_SAFE_PRODUCERS if direction=="out" else ROLE_SAFE_CONSUMERS))
    if not (evidence or (role_specific and c.explicit_role) or (
            bidirectional and c.role in {"materiais","cooperativa","agroinsumos"})):
        return None
    return why

def digest(value):
    return hashlib.sha256(value).hexdigest()

def run(g, map_entries, out_path, mode="corrigir", log=lambda s: None):
    """map_entries: {Eldorado:{existing:...,map_def:...}, Minas_Gerais:{...}}.

    Usa o arquivo do mapa COMO EVIDENCIA, e a Company EXISTENTE como base.
    """
    if mode not in {"corrigir","auditar"}:
        raise ValueError("Modo deve ser corrigir ou auditar")
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    if not map_entries:raise ValueError("Selecione ao menos uma Company existente")
    loaded={}
    for name,entry in map_entries.items():
        if not entry.get("existing") or not entry.get("map_def"):
            raise ValueError(name+": escolha Company existente e DEF do mapa")
        origin=Path(entry["existing"]).resolve()
        if not origin.exists():raise FileNotFoundError(str(origin))
        if origin==out.resolve():raise ValueError("Pasta de saida nao pode ser o arquivo de entrada")
        log("Lendo Company EXISTENTE: "+name+" — "+origin.name)
        source=inventory_archive(g,origin)
        baseline,_=g.extract_map(entry["map_def"])
        if name.lower()=="eldorado":
            for c in baseline.values():g.eldorado_classify(c)
        if not source:raise ValueError(name+": Company existente vazia ou ilegivel")
        loaded[name]=(source,baseline,entry)
    outputs=[]
    for name,(contents,baseline,entry) in loaded.items():
        log("Auditoria "+name+": "+str(len(baseline))+" empresas na DEF; "+
            str(len(contents))+" arquivos no SCS enviado")
        changed=dict(contents)
        decisions=[]
        states=defaultdict(lambda:{"in":set(),"out":set()})
        orig_states=defaultdict(lambda:{"in":set(),"out":set()})
        seen=defaultdict(list)
        company_files=set()
        untouched_other=0
        neutral=0
        count=0
        for path,raw in sorted(contents.items()):
            m=g.RE_COMPANY_PATH.search(path)
            if not m or m.group(2) not in {"in","out"} or not path.endswith(SII_EXT):
                continue
            company,direction=m.group(1).lower(),m.group(2).lower()
            company_files.add(company)
            ids=file_active_ids(g,raw)
            if not ids:
                text=g.read_sii(raw)
                neutral+=int('cargo: ""' in text or "cargo:\"\"" in text)
                untouched_other+=len(OTHER_FIELD.findall(text))
                continue
            if company not in baseline:
                for cargo in ids:
                    decisions.append({"acao":"REVISAR","empresa":company,"direcao":direction,
                        "carga":cargo,"arquivo":path,"setor":"EMPRESA_NAO_ENCONTRADA",
                        "confianca":"indeterminada",
                        "motivo":"ID nao aparece na DEF original do mapa; mantido para revisao"})
                    states[(company,direction)][direction].add(cargo)
                continue
            comp=baseline[company]
            for cargo in ids:
                cid=int(cargo[5:])
                cat=g.MANIFEST[cid][0]
                orig_states[company][direction].add(cargo)
                seen[(company,direction,cargo)].append(path)
                reason=safe_reason(g,comp,cat,direction,name)
                if reason:
                    decisions.append({"acao":"MANTER","empresa":company,"direcao":direction,
                        "carga":cargo,"arquivo":path,"setor":comp.role,
                        "confianca":"alta" if explicit_confidence(comp) else "media",
                        "motivo":reason})
                    states[company][direction].add(cargo)
                elif explicit_confidence(comp):
                    changed[path]=disable_id(g,changed[path],cargo)
                    decisions.append({"acao":"REMOVER","empresa":company,"direcao":direction,
                        "carga":cargo,"arquivo":path,"setor":comp.role,"confianca":"alta",
                        "motivo":"Empresa identificada como "+comp.role+
                                 "; carga/direcao incompatível com politica economica"})
                else:
                    decisions.append({"acao":"REVISAR","empresa":company,"direcao":direction,
                        "carga":cargo,"arquivo":path,"setor":comp.role,
                        "confianca":"baixa",
                        "motivo":"Empresa sem classificacao conclusiva; nao remover automaticamente"})
                    states[company][direction].add(cargo)
                count+=1
        # Nao repetir a mesma carga 2x no mesmo IN/OUT.
        for (company,direction,cargo),paths in seen.items():
            active=[path for path in paths if cargo in file_active_ids(g,changed[path])]
            if len(active)<=1:continue
            keep=sorted(active,key=lambda p:(not p.endswith("/"+cargo+".sii"),p))[0]
            for path in active:
                if path==keep:continue
                changed[path]=disable_id(g,changed[path],cargo)
                decisions.append({"acao":"REMOVER_DUPLICADO","empresa":company,
                    "direcao":direction,"carga":cargo,"arquivo":path,"setor":baseline[company].role,
                    "confianca":"alta","motivo":"Cargo ja existe no mesmo IN/OUT em "+keep})
        # Completar lacunas confiaveis de empresas EXISTENTES do mapa.
        for company,comp in sorted(baseline.items()):
            for n,(cat,title) in g.MANIFEST.items():
                cargo="carga"+str(n)
                for direction in ("in","out"):
                    present=(cargo in states[company][direction] and any(
                        cargo in file_active_ids(g,raw)
                        for p,raw in changed.items()
                        if p.startswith("def/company/"+company+"/"+direction+"/")))
                    if present:continue
                    why=can_add(g,comp,cat,direction,name)
                    if why:
                        new_path=f"def/company/{company}/{direction}/audit_{cargo}.sii"
                        if new_path in changed:
                            if cargo in file_active_ids(g,changed[new_path]):continue
                            decisions.append({"acao":"REVISAR","empresa":company,"direcao":direction,
                                "carga":cargo,"arquivo":new_path,"setor":comp.role,
                                "confianca":"baixa",
                                "motivo":"Caminho de complemento ocupado; evita sobrescrever"})
                            continue
                        changed[new_path]=g.cargo_sii(cargo)
                        decisions.append({"acao":"ADICIONAR","empresa":company,"direcao":direction,
                            "carga":cargo,"arquivo":new_path,"setor":comp.role,
                            "confianca":"alta","motivo":"Empresa compativel validada pela DEF: "+why})
                        states[company][direction].add(cargo)
        # Reconstruir estado pelo SCS FINAL, nao confiar nas decisoes.
        final_active=defaultdict(lambda:{"in":set(),"out":set()})
        original_active=defaultdict(lambda:{"in":set(),"out":set()})
        for files,dest in ((contents,original_active),(changed,final_active)):
            for p,raw in files.items():
                m=g.RE_COMPANY_PATH.search(p)
                if not m or m.group(2) not in {"in","out"} or not p.endswith(SII_EXT):continue
                for cargo in file_active_ids(g,raw):
                    dest[m.group(1)][m.group(2)].add(cargo)
        before={}
        after={}
        for n,(cat,title) in g.MANIFEST.items():
            cargo="carga"+str(n)
            for state,values in ((original_active,before),(final_active,after)):
                src=sorted(cid for cid,dirs in state.items() if cargo in dirs["out"])
                dst=sorted(cid for cid,dirs in state.items() if cargo in dirs["in"])
                values[cargo]={"nome":title,"categoria":cat,
                    "origens":len(src),"destinos":len(dst),
                    "origens_lista":src,"destinos_lista":dst,
                    "pares_distintos":len(src)*len(dst)-len(set(src)&set(dst))}
        updated=sum(contents.get(p)!=raw for p,raw in changed.items())
        added=sum(p not in contents for p in changed)
        manual=[d for d in decisions if d["acao"]=="REVISAR"]
        removals=[d for d in decisions if d["acao"] in ("REMOVER","REMOVER_DUPLICADO")]
        summary={"versao":"2.5.0","mapa":name,"modo":mode,"company_entrada":Path(entry["existing"]).name,
            "sha256_entrada":g.hash_source(entry["existing"]),
            "def_original":Path(entry["map_def"]).name,
            "sha256_def":g.hash_source(entry["map_def"]),
            "empresas_na_def":len(baseline),"empresas_no_scs":len(company_files),
            "permissoes_examindas":count,"arquivos_original":len(contents),
            "arquivos_adicionados":added,"arquivos_modificados":updated,
            "permissoes_removidas":len(removals),"pendencias_revisao":len(manual),
            "rotas_antes":before,"rotas_depois":after,
            "rotas_completas_depois":sum(x["pares_distintos"]>0 for x in after.values()),
            "decisoes":decisions,
            "status":"REVISÃO_MANUAL_NECESSÁRIA" if manual or any(
                x["pares_distintos"]==0 for x in after.values()) else
                "AUDITORIA_ESTRUTURAL_CONCLUÍDA",
            "aviso":"Nao homologado em ETS2; classificacao sem nome/evidencia conclusivos requer revisao humana."}
        outbase=out/("AUDITORIA_"+name.upper())
        outbase.with_suffix(".json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),
                                                 encoding="utf-8")
        with outbase.with_suffix(".csv").open("w",newline="",encoding="utf-8-sig") as fp:
            writer=csv.writer(fp,delimiter=";")
            writer.writerow(["acao","empresa","setor","direcao","carga","confianca","arquivo","motivo"])
            for d in decisions:
                writer.writerow([d.get(c,"") for c in
                    ("acao","empresa","setor","direcao","carga","confianca","arquivo","motivo")])
        with (out/("COBERTURA_"+name.upper()+"_23.csv")).open("w",newline="",
                                                          encoding="utf-8-sig") as fp:
            writer=csv.writer(fp,delimiter=";")
            writer.writerow(["carga","origens_antes","destinos_antes","origens_depois",
                             "destinos_depois","pares_distintos_depois"])
            for cargo in sorted(after,key=lambda c:int(c[5:])):
                a,b=before[cargo],after[cargo]
                writer.writerow([cargo,a["origens"],a["destinos"],b["origens"],
                                 b["destinos"],b["pares_distintos"]])
        if mode=="corrigir":
            output=out/("ETS2_"+name.upper()+"_AUDITADA_V25_"+
                        g.hash_source(entry["existing"])[:8]+".scs")
            if Path(entry["existing"]).resolve()==output.resolve():
                raise ValueError("Nunca sobrescrever a Company original")
            with tempfile.NamedTemporaryFile(prefix="company_audit_",suffix=".scs",
                                             dir=out,delete=False) as tmp:
                temporary=Path(tmp.name)
            try:
                with zipfile.ZipFile(temporary,"w",compression=zipfile.ZIP_DEFLATED) as z:
                    for p,raw in sorted(changed.items()):
                        inf=zipfile.ZipInfo(p,date_time=(2020,1,1,0,0,0))
                        inf.external_attr=0o644<<16
                        z.writestr(inf,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
                with zipfile.ZipFile(temporary) as z:
                    if z.testzip() is not None:raise ValueError("SCS de saida corrompido")
                    if set(z.namelist())!=set(changed):raise ValueError("Arquivos perdidos na saida")
                    for p,raw in contents.items():
                        if p not in changed or (
                            changed[p]==raw and z.read(p)!=raw):
                            raise ValueError("Arquivo original alterado indevidamente: "+p)
                os.replace(temporary,output)
            finally:
                if temporary.exists():temporary.unlink()
            summary["arquivo_corrigido"]=output.name
            outbase.with_suffix(".json").write_text(
                json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
            log(name+": Company auditada salva: "+output.name+
                " | "+str(len(removals))+" exclusoes, "+str(added)+
                " adicoes, "+str(len(manual))+" pendencias")
        else:
            log(name+": auditoria sem editar SCS | "+str(len(manual))+" pendencias")
        outputs.append(summary)
    return outputs
