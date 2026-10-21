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
import politica_economica as professional_policy
import catalogo_fontes as catalogo_cargas

SII_EXT=(".sii",".sui")
CARGO_FIELD = re.compile(r'(?im)^(\s*cargo\s*:\s*)"?cargo\.([a-z][a-z0-9_]*)"?(?=\s*(?:#.*)?$)')
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
        if any(a.file_size>=9_000_000 for a in files):
            z.close();raise ValueError("Arquivo interno acima de 9 MB; processamento exige revisao")
        members=((a.filename,z.read(a)) for a in files)
    result={}
    try:
        for original,raw in members:
            clean=g.clean_path(original)
            if not clean:raise ValueError("Caminho irregular: "+original)
            canonical=g.canonical_path(clean)
            path=canonical or clean
            if path in result and result[path]!=raw:
                raise ValueError("Colisao de arquivo SCS: "+path)
            result[path]=raw
    finally:
        if not p.is_dir():z.close()
    return result

def file_active_ids(g, raw):
    text=g.read_sii(raw)
    return [m.group(2).lower() for m in CARGO_FIELD.finditer(text)]

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

def safe_reason(g, c,cat,direction,map_name,professional=False,spec=None):
    if spec is not None:
        verdict=catalogo_cargas.evaluate(c,spec,direction,professional_policy.classify(c))
        return verdict.reason if verdict.allowed else None
    if professional:
        verdict=professional_policy.decide(c,cat,direction)
        return verdict.reason if verdict.allowed else None
    # Regras de seguranca valem nos tres mapas: transportadora nao e fabrica
    # e plantacao de banana nao e mercado geral de hortifruti.
    if c.role in {"transportadora","bananal"} or map_name.lower()=="eldorado":
        return g.eldorado_permit(c,cat,direction)
    return g.permits(c,cat,direction)

def explicit_confidence(c):
    if not c.explicit_role:return False
    if c.role in {"desconhecida","hub_generico","atacadista"}:return False
    # CEASA e hortifrutis explicitamente identificados possuem funcao real
    # de compra e revenda; nao confundir com empresa generica de transporte.
    if c.role=="hortifruti":
        return bool(re.search(r"ceasa|hortif|sacolao|fruit_warehouse|produce_market",
                              c.name,re.I))
    return True

def can_add(g,c,cat,direction,map_name,professional=False,spec=None):
    why=safe_reason(g,c,cat,direction,map_name,professional=professional,spec=spec)
    explicit_custom=(spec is not None and
                     professional_policy.norm(c.name) in spec.get(direction+"_companies", ()))
    if not why or not (explicit_confidence(c) or explicit_custom):return None
    if professional:
        # A politica moderna JA valida as restricoes por ramo, produto
        # e evidencia dos IN/OUT originais.
        return why
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

def proven_incompatibility(company, category, direction, spec=None):
    """So exclui automaticamente contradicoes claras, nao mera falta de prova.

    Um setor reconhecido nao demonstra que todas as suas outras cargas
    sejam invalidas. Fazendas podem ter culturas secundarias; pecuaristas
    podem plantar; cooperativas armazenam e revendem varias mercadorias.
    """
    role=company.role
    if spec is not None:
        if role in spec.get("forbidden_roles",()):
            return "Setor explicitamente proibido no cadastro desta mercadoria"
        return None
    if role=="transportadora":
        return "Transportadora nao e unidade de producao, compra ou revenda comprovada"
    if role=="bananal" and (direction!="in" or category!="adubo"):
        return "Bananal nao fornece outras culturas nem recebe genericamente estes produtos"
    if direction=="out" and (
        (role in {"automotiva_fabrica","maquinas"} and category=="bobina") or
        (role=="premoldados" and category=="cimento")
    ):
        return "Fabricante identificado nao produz a materia-prima correspondente"
    return None


def digest(value):
    return hashlib.sha256(value).hexdigest()

def _run_unpublished(g, map_entries, out_path, mode="corrigir",
                     log=lambda s: None,professional=False,source_files=None):
    """map_entries: {Eldorado:{existing:...,map_def:...}, Minas_Gerais:{...}}.

    Usa o arquivo do mapa COMO EVIDENCIA, e a Company EXISTENTE como base.
    """
    if mode not in {"corrigir","auditar"}:
        raise ValueError("Modo deve ser corrigir ou auditar")
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    if not map_entries:raise ValueError("Selecione ao menos uma Company existente")
    extras={}
    manifest=dict(g.MANIFEST)
    trailer_record={}
    if professional:
        if not source_files or any(k not in source_files for k in ("mod","def1","def2")):
            raise ValueError("Auditoria V3 precisa dos arquivos originais do reboque: MOD, DEF1 e DEF2.")
        originals=[]
        for label in ("mod","def1","def2"):
            originals.append((label,g.zip_members(source_files[label])))
        cargo_records,_legacy,owned,_defs,_totals=g.cargo_inventory(originals)
        manifest,extras=catalogo_cargas.from_originals(
            g.MANIFEST,cargo_records,(source_files or {}).get("txt"))
        failures=[]
        for n in manifest:
            cargo=catalogo_cargas.cargo_id(n)
            record=cargo_records.get(cargo)
            if not record or not record.get("body"):
                failures.append(cargo+" sem cargo_data/body_types")
            elif cargo in extras and not owned:
                failures.append(cargo+" sem carroceria do reboque identificada")
            elif owned and not set(record["body"]).intersection(owned):
                failures.append(cargo+" sem carroceria compativel")
        if failures:
            raise ValueError("Auditoria bloqueada: compatibilidade do Librelato nao comprovada: "+
                             "; ".join(failures))
        trailer_record={cargo:{"body_types":sorted(info["body"]),
                                "carrocerias_instaladas":sorted(owned),
                                "carroceria_compativel":bool(set(info["body"])&owned)}
                        for cargo,info in cargo_records.items()}
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
        for c in baseline.values():
            if professional:
                identity=professional_policy.classify(c)
                c.role=identity.role
                c.explicit_role=(identity.certainty=="alta")
                continue
            if name.lower()=="eldorado":
                g.eldorado_classify(c)
            else:
                # Em MG/RBR nomes podem representar transportadoras e
                # fazendas de banana do mesmo modo; priorizar a atividade
                # real sobre OUT herdado da Company.
                if g.ELDORADO_LOGISTICS.search(g.normal(c.name)):
                    c.role="transportadora";c.explicit_role=True
                elif (g.ELDORADO_BANANA.search(g.normal(c.name)) and
                      c.role in {"hortifruti","fazenda","desconhecida"}):
                    c.role="bananal";c.explicit_role=True
        if not source:raise ValueError(name+": Company existente vazia ou ilegivel")
        loaded[name]=(source,baseline,entry)
    outputs=[]
    for name,(contents,baseline,entry) in loaded.items():
        log("Auditoria "+name+": "+str(len(baseline))+" empresas na DEF; "+
            str(len(contents))+" arquivos no SCS enviado")
        changed=dict(contents)
        decisions=[]
        states=defaultdict(lambda:{"in":set(),"out":set()})
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
                    states[company][direction].add(cargo)
                continue
            comp=baseline[company]
            for cargo in ids:
                index=(next((k for k in manifest if catalogo_cargas.cargo_id(k)==cargo),None))
                if index is None:
                    decisions.append({"acao":"REVISAR","empresa":company,
                        "direcao":direction,"carga":cargo,"arquivo":path,
                        "setor":comp.role,"confianca":"indeterminada",
                        "motivo":"Carga sem definicao no catalogo; mantida inalterada"})
                    states[company][direction].add(cargo)
                    continue
                cat=manifest[index][0]
                seen[(company,direction,cargo)].append(path)
                reason=safe_reason(g,comp,cat,direction,name,professional=professional,
                                   spec=extras.get(cargo))
                if reason:
                    decisions.append({"acao":"MANTER","empresa":company,"direcao":direction,
                        "carga":cargo,"arquivo":path,"setor":comp.role,
                        "confianca":"alta" if explicit_confidence(comp) else "media",
                        "motivo":reason})
                    states[company][direction].add(cargo)
                else:
                    prohibition=(proven_incompatibility(
                        comp,cat,direction,extras.get(cargo))
                        if explicit_confidence(comp) else None)
                    if prohibition:
                        changed[path]=disable_id(g,changed[path],cargo)
                        decisions.append({"acao":"REMOVER","empresa":company,
                            "direcao":direction,"carga":cargo,"arquivo":path,
                            "setor":comp.role,"confianca":"alta","motivo":prohibition})
                    else:
                        decisions.append({
                            "acao":("REVISAR" if explicit_confidence(comp)
                                    else "PRESERVAR_SEM_EVIDENCIA"),
                            "empresa":company,"direcao":direction,"carga":cargo,
                            "arquivo":path,"setor":comp.role,
                            "confianca":"media" if explicit_confidence(comp) else "indeterminada",
                            "motivo":("Atividade conhecida mas a mercadoria exige "
                                     "confirmacao documental antes de ser aprovada"
                                     if explicit_confidence(comp) else
                                     "Permissao herdada preservada sem alterar; "
                                     "empresa ainda nao classificada")})
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
        # Indexar uma vez os cargos ainda ativos apos remocoes/duplicados.
        current=defaultdict(lambda:{"in":set(),"out":set()})
        for p,raw in changed.items():
            m=g.RE_COMPANY_PATH.search(p)
            if not m or m.group(2) not in {"in","out"} or not p.endswith(SII_EXT):continue
            current[m.group(1)][m.group(2)].update(file_active_ids(g,raw))
        # Completar lacunas confiaveis de empresas EXISTENTES do mapa.
        for company,comp in sorted(baseline.items()):
            for n,(cat,title) in manifest.items():
                cargo=catalogo_cargas.cargo_id(n)
                for direction in ("in","out"):
                    present=(cargo in current[company][direction])
                    if present:continue
                    why=can_add(g,comp,cat,direction,name,professional=professional,
                                spec=extras.get(cargo))
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
                        current[company][direction].add(cargo)
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
        for n,(cat,title) in manifest.items():
            cargo=catalogo_cargas.cargo_id(n)
            for state,values in ((original_active,before),(final_active,after)):
                src=sorted(cid for cid,dirs in state.items() if cargo in dirs["out"])
                dst=sorted(cid for cid,dirs in state.items() if cargo in dirs["in"])
                values[cargo]={"nome":title,"categoria":cat,
                    "origens":len(src),"destinos":len(dst),
                    "origens_lista":src,"destinos_lista":dst,
                    "pares_distintos":len(src)*len(dst)-len(set(src)&set(dst))}
        def territory_decision(c,cat,direction,cargo):
            if cargo in extras:
                return catalogo_cargas.evaluate(
                    c,extras[cargo],direction,professional_policy.classify(c))
            return professional_policy.decide(c,cat,direction)
        territory=(professional_policy.coverage(
            baseline,manifest,decision_fn=territory_decision)
            if professional else None)
        forgotten_companies=[]
        forgotten_units=[]
        if territory is not None:
            for row in territory["empresas"]:
                actual=final_active[row["empresa"]]
                missing_in=sorted(set(row["in_esperados"])-actual["in"])
                missing_out=sorted(set(row["out_esperados"])-actual["out"])
                if missing_in or missing_out:
                    forgotten_companies.append({"empresa":row["empresa"],
                        "setor":row["atividade"],"faltando_in":missing_in,
                        "faltando_out":missing_out,"unidades_cidade":row["instancias_editor"]})
            for row in territory["instancias_cidade"]:
                actual=final_active[row["empresa"]]
                missing_in=sorted(set(row["in_esperados"])-actual["in"])
                missing_out=sorted(set(row["out_esperados"])-actual["out"])
                if missing_in or missing_out:
                    forgotten_units.append({**row,"faltando_in":missing_in,
                                             "faltando_out":missing_out})
        updated=sum(contents.get(p)!=raw for p,raw in changed.items())
        added=sum(p not in contents for p in changed)
        # Nao transformar a ausencia de classificacao em centenas de alertas.
        # Preservar cada permissao herdada, com rastro individual, e produzir
        # uma fila de classificacao agrupada por empresa.
        manual=[d for d in decisions if d["acao"]=="REVISAR"]
        preserved=[d for d in decisions if d["acao"]=="PRESERVAR_SEM_EVIDENCIA"]
        pending_by_company=defaultdict(list)
        for item in manual+preserved:
            pending_by_company[item["empresa"]].append(item)
        classification_pending={d["empresa"] for d in preserved}
        routes_without_pair=[
            cargo for cargo,row in after.items() if row["pares_distintos"]==0]
        additional_without_policy=sorted(extras,key=catalogo_cargas.sort_key)
        removals=[d for d in decisions if d["acao"] in ("REMOVER","REMOVER_DUPLICADO")]
        summary={"versao":"3.0.0" if professional else "2.5.0",
            "economia_profissional":professional,
            "alteracoes_sao_simulacao":mode=="auditar",
            "nenhum_scs_gerado":mode=="auditar",
            "diagnostico_pendencias":{
                "total_decisoes_revisar":len(manual),
                "permissoes_herdadas_preservadas_sem_evidencia":len(preserved),
                "empresas_com_classificacao_pendente":len(classification_pending),
                "empresas_com_revisoes_acionaveis":len({d["empresa"] for d in manual}),
                "empresas_com_revisoes":len(pending_by_company),
                "criterio":"PRESERVAR_SEM_EVIDENCIA nao e erro; "
                           "permissoes ficam intactas ate comprovacao documental.",
                "cargas_sem_rota":routes_without_pair,
                "cargas_novas_sem_politica_economica":additional_without_policy,
                "por_motivo":dict(sorted(
                    (m,sum(x["motivo"]==m for x in manual))
                    for m in {x["motivo"] for x in manual})),
                "por_atividade":dict(sorted(
                    (role,sum(x["setor"]==role for x in manual))
                    for role in {x["setor"] for x in manual})),
                "empresas_nao_classificadas_com_revisao":len(classification_pending),
            },
            "politica_cargas_adicionais":{
                cid:{"categoria":spec["categoria"],"nome":spec["nome"],
                     "body_types":spec["body_types"],
                     "situacao":"pendente de validacao economica com DEF/TXT originais"}
                for cid,spec in extras.items()},
            "total_cargas_catalogo":len(manifest),
            "cargas_adicionais":{cid:{"sha256":spec["sha256"],"body_types":spec["body_types"]} for cid,spec in extras.items()},
            "validacao_carga_carroceria":trailer_record,
            "matriz_empresa_cidade":territory,
            "empresas_compativeis_esquecidas":forgotten_companies,
            "unidades_cidade_compativeis_esquecidas":forgotten_units,
            "mapa":name,"modo":mode,"company_entrada":Path(entry["existing"]).name,
            "sha256_entrada":g.hash_source(entry["existing"]),
            "def_original":Path(entry["map_def"]).name,
            "sha256_def":g.hash_source(entry["map_def"]),
            "empresas_na_def":len(baseline),"empresas_no_scs":len(company_files),
            "permissoes_examinadas":count,"arquivos_original":len(contents),
            "arquivos_adicionados":added,"arquivos_modificados":updated,
            "permissoes_removidas":len(removals),"pendencias_revisao":len(manual),
            "permissoes_sem_evidencia_preservadas":len(preserved),
            "empresas_classificacao_pendente":len(classification_pending),
            "cargas_sem_rota_validada":routes_without_pair,
            "rotas_antes":before,"rotas_depois":after,
            "nota_rotas_depois":("PROJECAO de como ficaria se corrigisse; "
                                "nenhuma permissao alterada no arquivo original"
                                if mode=="auditar" else
                                "Resultado exportado para novo SCS auditado"),
            "rotas_completas_depois":sum(x["pares_distintos"]>0 for x in after.values()),
            "decisoes":decisions,
            "status":("PENDENTE_VALIDACAO_ECONOMICA"
                      if manual or preserved or forgotten_companies or
                         routes_without_pair or additional_without_policy or
                         (territory and territory["empresas_sem_identificacao"])
                      else "AUDITORIA_ESTRUTURAL_CONCLUÍDA"),
            "aviso":("Arquivo tecnicamente auditado, NAO homologado para cliente "
                     "ou ETS2 enquanto restarem empresas sem classificacao, "
                     "permissoes sem evidencia e cargas sem rotas.")}
        # Dois niveis de diagnostico: aviso acionavel vs situacao herdada
        # somente informativa. O conjunto completo continua em AUDITORIA*.csv.
        with (out/("RESUMO_VALIDACAO_"+name.upper()+".txt")).open(
                "w",encoding="utf-8") as fp:
            fp.write("Mapa: "+name+"\n")
            fp.write("Revisoes pontuais: "+str(len(manual))+"\n")
            fp.write("Permissoes herdadas preservadas sem evidencia: "+
                     str(len(preserved))+"\n")
            fp.write("Empresas necessitando identificacao de atividade: "+
                     str(len(classification_pending))+"\n")
            fp.write("Cargas sem rota com empresas distintas: "+
                     ", ".join(routes_without_pair)+"\n")
            fp.write("Cargas novas aguardando politica economica: "+
                     ", ".join(additional_without_policy)+"\n")
            fp.write("Aviso: sem verificacao em mapa/ETS2, nao e entrega homologada.\n")
        # Indica quais empresas realmente precisam ser classificadas primeiro.
        with (out/("PENDENCIAS_CLASSIFICACAO_"+name.upper()+".csv")).open(
                "w",newline="",encoding="utf-8-sig") as fp:
            writer=csv.writer(fp,delimiter=";")
            writer.writerow(["empresa","setor_atual","permissoes_a_conferir","cargas_ativas_in",
                             "cargas_ativas_out","instancias_editor",
                             "prefab_confirmado","acao_recomendada"])
            for cid,pending in sorted(pending_by_company.items(),
                                      key=lambda kv:(-len(kv[1]),kv[0])):
                comp=baseline.get(cid)
                ins=sorted({x["carga"] for x in pending
                            if x["direcao"]=="in"},key=catalogo_cargas.sort_key)
                outs=sorted({x["carga"] for x in pending
                             if x["direcao"]=="out"},key=catalogo_cargas.sort_key)
                writer.writerow([cid,comp.role if comp else "NAO_PRESENTE_NA_DEF",
                    len(pending),",".join(ins),",".join(outs),
                    len(comp.editor_files) if comp else 0,"NAO",
                    "Confirmar atividade e cargas na DEF original antes de aprovar"])
        outbase=out/("AUDITORIA_"+name.upper())
        outbase.with_suffix(".json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),
                                                 encoding="utf-8")
        with outbase.with_suffix(".csv").open("w",newline="",encoding="utf-8-sig") as fp:
            writer=csv.writer(fp,delimiter=";")
            writer.writerow(["acao","empresa","setor","direcao","carga","confianca","arquivo","motivo"])
            for d in decisions:
                writer.writerow([d.get(c,"") for c in
                    ("acao","empresa","setor","direcao","carga","confianca","arquivo","motivo")])
        # Inventario EXAUSTIVO: cada arquivo original IN e OUT, inclusive
        # neutralizados/vazios. Nao se limita as 23 permissoes ativas.
        with (out/("INVENTARIO_COMPLETO_"+name.upper()+".csv")).open(
                "w",newline="",encoding="utf-8-sig") as fp:
            writer=csv.writer(fp,delimiter=";")
            writer.writerow(["empresa","setor","direcao","arquivo_sii","cargas_antes",
                             "cargas_depois","neutralizado","foi_alterado"])
            for path,raw in sorted(contents.items()):
                m=g.RE_COMPANY_PATH.search(path)
                if not m or m.group(2) not in {"in","out"} or not path.endswith(SII_EXT):
                    continue
                comp=m.group(1)
                before_fields=file_active_ids(g,raw)
                after_fields=file_active_ids(g,changed[path])
                role=(baseline[comp].role if comp in baseline else "SEM_DEF")
                writer.writerow([comp,role,m.group(2),path,
                                 ",".join(before_fields),",".join(after_fields),
                                 "SIM" if not before_fields else "NAO",
                                 "SIM" if raw!=changed[path] else "NAO"])
        # Uma linha por CADA empresa conhecida no mapa, inclusive sem carga:
        # mostra as instancias editor que foram encontradas na DEF (nao
        # equivale a validar o prefab da cidade dentro do jogo).
        with (out/("EMPRESAS_COMPLETAS_"+name.upper()+".csv")).open(
                "w",newline="",encoding="utf-8-sig") as fp:
            writer=csv.writer(fp,delimiter=";")
            writer.writerow(["empresa","setor","classificacao_por_nome_ou_evidencia",
                             "instancias_editor_na_def","arquivos_editor_na_def",
                             "in_atuais","out_atuais","total_permissoes"])
            for company,c in sorted(baseline.items()):
                ins=sorted(final_active[company]["in"],key=catalogo_cargas.sort_key)
                outs=sorted(final_active[company]["out"],key=catalogo_cargas.sort_key)
                editor_names=sorted(c.editor_files)
                writer.writerow([
                    company,c.role,
                    "EXPLICITA" if c.explicit_role else "INFERIDA_OU_DESCONHECIDA",
                    len(editor_names),",".join(x.rsplit("/",1)[-1] for x in editor_names),
                    ",".join(ins),",".join(outs),len(ins)+len(outs)])
        if territory is not None:
            with (out/("COBERTURA_EMPRESA_CIDADE_"+name.upper()+".csv")).open(
                    "w",encoding="utf-8-sig",newline="") as fp:
                writer=csv.writer(fp,delimiter=";")
                writer.writerow(["empresa","cidade_editor","setor","in_esperados",
                    "out_esperados","in_efetivos","out_efetivos",
                    "in_faltantes","out_faltantes","prefab_confirmado"])
                for city in territory["instancias_cidade"]:
                    actual=final_active[city["empresa"]]
                    needed_in=set(city["in_esperados"]);needed_out=set(city["out_esperados"])
                    writer.writerow([city["empresa"],city["cidade"],city["atividade"],
                        ",".join(sorted(needed_in)),",".join(sorted(needed_out)),
                        ",".join(sorted(actual["in"])),",".join(sorted(actual["out"])),
                        ",".join(sorted(needed_in-actual["in"])),
                        ",".join(sorted(needed_out-actual["out"])),"NAO"])
                # Empresas sem editor nao podem ser apresentadas como cidade confirmada.
                for company in territory["empresas"]:
                    if company["instancias_editor"]==0:
                        actual=final_active[company["empresa"]]
                        writer.writerow([company["empresa"],"CIDADE_NAO_IDENTIFICADA",
                            company["atividade"],",".join(company["in_esperados"]),
                            ",".join(company["out_esperados"]),
                            ",".join(sorted(actual["in"])),",".join(sorted(actual["out"])),
                            ",".join(sorted(set(company["in_esperados"])-actual["in"])),
                            ",".join(sorted(set(company["out_esperados"])-actual["out"])),"NAO"])
        with (out/("COBERTURA_"+name.upper()+("_23" if len(manifest)==23 else "_CARGAS")+".csv")).open("w",newline="",
                                                          encoding="utf-8-sig") as fp:
            writer=csv.writer(fp,delimiter=";")
            writer.writerow(["carga","origens_antes","destinos_antes","origens_depois",
                             "destinos_depois","pares_distintos_depois"])
            for cargo in sorted(after,key=catalogo_cargas.sort_key):
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
                " adicoes; "+str(len(manual))+" revisoes pontuais, "+
                str(len(classification_pending))+" empresas sem classificacao")
        else:
            log(name+": auditoria sem editar SCS | "+str(len(manual))+
                " revisoes pontuais; "+str(len(classification_pending))+
                " empresas com atividade pendente")
        outputs.append(summary)
    return outputs


def run(g, map_entries, out_path, mode="corrigir", log=lambda s: None,
        professional=False, source_files=None):
    """Publica resultados SOMENTE depois que todos os mapas terminarem.

    Preserva arquivos existentes caso a auditoria do segundo ou terceiro
    mapa falhe; nunca deixa resultado parcial parecendo entrega concluida.
    """
    published=Path(out_path)
    published.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="auditor_staging_",dir=published) as tmp:
        stage=Path(tmp)
        try:
            result=_run_unpublished(
                g,map_entries,stage,mode=mode,log=log,
                professional=professional,source_files=source_files)
        except Exception as exc:
            (published/"AUDITORIA_INCOMPLETA.txt").write_text(
                "Processamento dos mapas interrompido antes da publicacao. "
                "Nenhum SCS novo desta execucao foi entregue.\n"+
                type(exc).__name__+": "+str(exc)+"\n",
                encoding="utf-8")
            raise
        for item in sorted(stage.iterdir()):
            if item.is_file():
                os.replace(item,published/item.name)
        log("Auditoria de "+str(len(result))+
            " mapa(s) finalizada e publicada em conjunto.")
        return result
