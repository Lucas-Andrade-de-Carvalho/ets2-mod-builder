"""Auditoria objetiva de COBERTURA MAXIMA por empresa/cidade em qualquer mapa.

O indicador 24/24 mercadorias COM rotas NAO mede cobertura das empresas.
Este modulo cruza toda a matriz de empresas conhecidas e evidencia onde
ha possivel compatibilidade ainda nao classificada sem inventar permissao.
"""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path

# Sinais de atividade relevante nas 24 cargas, usados SOMENTE para abrir
# investigacao, nunca como autorizacao automatica de OUT/IN.
HINT=re.compile(
    r"madeir|madereir|extracao.*madei|lumber|citr|frut|agr[oí]|cereai|"
    r"armaz[eé]|fazend|serrar|algod|cotton|a[cç]o|ferro|sider|constru|"
    r"dep[oó]sito|mercado|sams|suco|f[aá]brica|fabrica|cimento|"
    r"tijolo|metal|pallet|palete|silo|m[oó]ve|sucata|sorgo|racao|"
    r"laranja|soja|milho|cerveja|coco|celulos|pain[eé]is|pre.?mold",
    re.I
)

def assess(companies,territory,final_active,manifest,quality):
    """Um registro para cada empresa (sem excluir nenhuma do denominador)."""
    docs={x["empresa"]:x for x in territory["empresas"]}
    cities={}
    unit_counts={}
    for x in territory["instancias_cidade"]:
        cities.setdefault(x["empresa"],set()).add(x["cidade"])
        unit_counts[x["empresa"]]=unit_counts.get(x["empresa"],0)+1
    rows=[]
    known_with_cargo=known_complete=known_incomplete=outside=unclassified=0
    potential_unknown=0
    for id,c in sorted(companies.items()):
        row=docs[id]
        # Usar a MESMA identidade documental empregada pela matriz
        # empresa/cidade. c.role e um cache mutavel que pode divergir
        # da atividade do relatorio; misturar os dois produz contadores
        # inconsistentes entre o total geral e os tres mapas.
        role=row["atividade"]
        planned_in=set(row["in_esperados"])
        planned_out=set(row["out_esperados"])
        actual_in=set(final_active[id]["in"])
        actual_out=set(final_active[id]["out"])
        missing_in=sorted(planned_in-actual_in)
        missing_out=sorted(planned_out-actual_out)
        candidate=role=="desconhecida"
        # Nenhuma permissao e deduzida a partir deste sinal.
        historical=bool(actual_in|actual_out)
        old_name=getattr(c,"display_name","") or ""
        maybe=candidate and (
            bool(HINT.search(id+" "+old_name)) or
            historical or bool(getattr(c,"old_in",set())|
                               getattr(c,"old_out",set())))
        if candidate:
            unclassified+=1
            potential_unknown+=bool(maybe)
            status=("REVISAR_POSSIVEL_COMPATIBILIDADE" if maybe
                    else "ATIVIDADE_SEM_PROVA")
        elif role=="infra_passageiros":
            outside+=1
            status="FORA_DAS_24_MERCADORIAS"
        elif planned_in or planned_out:
            known_with_cargo+=1
            if missing_in or missing_out:
                known_incomplete+=1
                status="COMPATIVEL_COM_LACUNAS"
            else:
                known_complete+=1
                status="COMPATIVEL_CONTEMPLADA"
        else:
            outside+=1
            status="CLASSIFICADA_SEM_CARGA_COMPATIVEL"
        rows.append({
            "empresa":id,
            "nome_exibido":old_name,
            "setor":role,
            "status":status,
            "cidades":sorted(cities.get(id,[])),
            "total_instancias_editor":unit_counts.get(id,0),
            "in_esperados":sorted(planned_in),
            "out_esperados":sorted(planned_out),
            "in_efetivos":sorted(actual_in),
            "out_efetivos":sorted(actual_out),
            "in_faltantes":missing_in,
            "out_faltantes":missing_out,
            "herdadas_nao_comprovadas":bool(
                candidate and (actual_in or actual_out)),
            "sinal_compatibilidade_a_investigar":bool(maybe)
        })
    # Matriz territorial: cidade e unidade SEM estimar geografia quando
    # a DEF nao fornece company_def/editor. Um par de empresas iguais
    # em varias cidades nao comprova o prefab navegavel dentro do jogo.
    by_city={}
    for unit in territory["instancias_cidade"]:
        city=unit["cidade"]
        company_id=unit["empresa"]
        # A auditoria territorial deve usar a mesma identidade documental
        # da matriz por empresa; company.role e apenas um cache mutavel.
        role=docs[company_id]["atividade"]
        bucket=by_city.setdefault(city,{
            "cidade":city,"instancias":0,"empresas":set(),
            "compativeis":set(),"compativeis_cobertas":set(),
            "compativeis_incompletas":set(),"desconhecidas":set(),
            "sem_cargas_24":set()})
        bucket["instancias"]+=1
        bucket["empresas"].add(company_id)
        if role=="desconhecida":
            bucket["desconhecidas"].add(company_id)
        elif unit.get("in_esperados",[]) or unit.get("out_esperados",[]):
            bucket["compativeis"].add(company_id)
            actual=final_active[company_id]
            if (set(unit.get("in_esperados",[]))-set(actual["in"]) or
                    set(unit.get("out_esperados",[]))-set(actual["out"])):
                bucket["compativeis_incompletas"].add(company_id)
            else:
                bucket["compativeis_cobertas"].add(company_id)
        else:
            bucket["sem_cargas_24"].add(company_id)
    cities_report=[]
    for city,record in sorted(by_city.items()):
        missing=record["compativeis_incompletas"]
        unknown=record["desconhecidas"]
        cities_report.append({
            "cidade":city,
            "instancias_editor":record["instancias"],
            "empresas_distintas":len(record["empresas"]),
            "empresas_compativeis":len(record["compativeis"]),
            "empresas_compativeis_cobertas":len(record["compativeis_cobertas"]-
                                                missing),
            "empresas_compativeis_incompletas":sorted(missing),
            "empresas_sem_atividade_identificada":sorted(unknown),
            "empresas_fora_das_24":len(record["sem_cargas_24"]),
            "situacao":(
                "REVISAO_COMPATIBILIDADE" if unknown else
                "INCOMPLETA" if missing else
                "COMPATIVEIS_COBERTAS" if record["compativeis"] else
                "SEM_EMPRESA_COMPATIVEL_CONFIRMADA"
            )
        })
    total_cargos=len(manifest)
    economic=int(quality.get("cargas_com_par_economico_comprovavel",0))
    with_editor=int(quality.get("cargas_candidatas_teste_ets2",0))
    complete=(
        known_incomplete==0 and potential_unknown==0 and
        unclassified==0 and economic==total_cargos and
        with_editor==total_cargos
    )
    return {
        "total_empresas_def":len(rows),
        "empresas_reconhecidas_com_ao_menos_uma_carga":known_with_cargo,
        "empresas_reconhecidas_totalmente_contempladas":known_complete,
        "empresas_reconhecidas_com_lacunas":known_incomplete,
        "empresas_classificadas_sem_carga_nas_24":outside,
        "empresas_sem_classificacao":unclassified,
        "desconhecidas_com_sinais_de_carga_a_investigar":potential_unknown,
        "cobertura_empresas_reconhecidas_pct":round(
            100*known_complete/known_with_cargo,2)
            if known_with_cargo else None,
        "cadeias_economicas":economic,
        "cargas_candidatas_teste":with_editor,
        "instancias_editor_detectadas":sum(unit_counts.values()),
        "cidades_identificadas":len(cities_report),
        "cidades_com_empresas_compativeis_incompletas":sum(
            bool(row["empresas_compativeis_incompletas"]) for row in cities_report),
        "cidades_com_empresas_sem_classificacao":sum(
            bool(row["empresas_sem_atividade_identificada"]) for row in cities_report),
        "cidades_com_compativeis_reconhecidas_cobertas":sum(
            row["situacao"]=="COMPATIVEIS_COBERTAS" for row in cities_report),
        "empresas_sem_editor":sum(not unit_counts.get(id,0) for id in companies),
        "total_cargas":total_cargos,
        "cobertura_100_por_cento_comprovada":bool(complete),
        "aviso":"Percentual se limita a empresas JA classificadas. "
                "Nao representa 100% das empresas compativeis enquanto "
                "restarem empresas nao classificadas, e NAO homologa jogo.",
        "empresas":rows,
        "cidades":cities_report
    }

def write(directory, report, map_name="RBR"):
    """Relatorios isolados por mapa, com nomes estaveis e CSV priorizado."""
    allowed={"RBR","ELDORADO","MINAS_GERAIS"}
    key=map_name.upper()
    if key not in allowed:
        raise ValueError("Mapa nao suportado para cobertura: "+str(map_name))
    out=Path(directory)
    out.mkdir(parents=True,exist_ok=True)
    (out/("COBERTURA_MAXIMA_"+key+".json")).write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/("COBERTURA_CIDADES_"+key+".json")).write_text(
        json.dumps(report["cidades"],ensure_ascii=False,indent=2),
        encoding="utf-8")
    with (out/("COBERTURA_CIDADES_"+key+".csv")).open(
            "w",newline="",encoding="utf-8-sig") as f:
        columns=["cidade","instancias_editor","empresas_distintas",
                 "empresas_compativeis","empresas_compativeis_cobertas",
                 "empresas_compativeis_incompletas",
                 "empresas_sem_atividade_identificada",
                 "empresas_fora_das_24","situacao"]
        w=csv.DictWriter(f,fieldnames=columns,delimiter=";")
        w.writeheader()
        for item in report["cidades"]:
            w.writerow({k:",".join(v) if isinstance(v,list) else v
                        for k,v in item.items()})
    with (out/("COBERTURA_MAXIMA_"+key+".csv")).open(
            "w",newline="",encoding="utf-8-sig") as f:
        fieldnames=[
            "empresa","nome_exibido","setor","status","cidades",
            "total_instancias_editor","in_esperados","out_esperados",
            "in_efetivos","out_efetivos","in_faltantes","out_faltantes",
            "herdadas_nao_comprovadas","sinal_compatibilidade_a_investigar"
        ]
        w=csv.DictWriter(f,fieldnames=fieldnames,delimiter=";")
        w.writeheader()
        for row in report["empresas"]:
            w.writerow({k:",".join(v) if isinstance(v,list) else v
                        for k,v in row.items()})
    priority={"COMPATIVEL_COM_LACUNAS":0,
              "REVISAR_POSSIVEL_COMPATIBILIDADE":1}
    pending=sorted(
        (r for r in report["empresas"] if r["status"] in priority),
        key=lambda r:(priority[r["status"]],
                      -r["total_instancias_editor"],r["empresa"]))
    with (out/(key+"_REVISAO_ECONOMICA_PRIORIZADA.csv")).open(
            "w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fieldnames,delimiter=";")
        w.writeheader()
        for row in pending:
            w.writerow({k:",".join(v) if isinstance(v,list) else v
                        for k,v in row.items()})
