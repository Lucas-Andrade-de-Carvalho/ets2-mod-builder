"""Qualificacao conservadora de cada cadeia IN/OUT para entrega comercial.

Os arquivos da DEF informam POSSIBILIDADES. Nenhuma contagem de pares
substitui a verificacao no mercado de fretes e nos prefabs do ETS2.
"""
from __future__ import annotations
from collections import defaultdict


def assess(baseline, active, manifest, extras, policy, catalog):
    """Separar pares meramente cadastrados de cadeias com evidencia economica.

    A prova automatica de compatibilidade e fundamentada na atividade
    reconhecida explicitamente e em regra de produto/direcao. A existencia
    de editor dos dois lados gera apenas candidato para teste, nunca
    comprovacao de cidade/rota jogavel.
    """
    evaluated={}
    for company,c in baseline.items():
        identity=policy.classify(c)
        evaluated[company]={
            "company":c,"identity":identity,
            "explicit":identity.certainty=="alta" and
                       identity.role not in {"desconhecida","hub_generico","atacadista"},
            # Apenas company_def com cidade + prefab documentalmente existente
            # e candidato territorial. Arquivos editor vazios nao contam.
            "editor":bool(policy.city_references(c))
        }
    result={}
    for key,(category,title) in manifest.items():
        cid=catalog.cargo_id(key)
        all_in={name for name,perm in active.items() if cid in perm["in"]}
        all_out={name for name,perm in active.items() if cid in perm["out"]}
        accepted={"in":set(),"out":set()}
        documented={"in":set(),"out":set()}
        reasons={}
        documentary_reasons={}
        for direction,names in (("in",all_in),("out",all_out)):
            for name in names:
                entry=evaluated.get(name)
                if not entry:
                    continue
                comp=entry["company"]
                if cid in extras:
                    verdict=catalog.evaluate(comp,extras[cid],direction,entry["identity"])
                else:
                    verdict=policy.decide(comp,category,direction,entry["identity"])
                if not verdict.allowed:
                    continue
                key=direction+":"+name
                in_original=policy.cargo_categories(
                    comp.old_in if direction=="in" else comp.old_out)
                if entry["explicit"]:
                    # Evidencia SETORIAL autoriza a cadeia economica mesmo
                    # quando a DEF nao tinha aquela mercadoria original.
                    accepted[direction].add(name)
                    reasons[key]=verdict.reason
                if category in in_original:
                    # Camada DOCUMENTAL e estritamente IN/OUT de mesma
                    # categoria e direcao. Nome/atividade sozinho NAO basta.
                    documented[direction].add(name)
                    documentary_reasons[key]=(
                        "categoria registrada no IN/OUT original da DEF; "
                        "papel: "+entry["identity"].role)

        potential_in=accepted["in"]
        potential_out=accepted["out"]
        # Contar sem construir todas as combinacoes na memoria.
        # Um mapa com milhares de empresas pode gerar milhoes de pares.
        pairs=len(potential_out)*len(potential_in)-len(potential_out & potential_in)
        doc_in=documented["in"]
        doc_out=documented["out"]
        doc_pairs=len(doc_out)*len(doc_in)-len(doc_out & doc_in)
        editor_doc_out={src for src in doc_out if evaluated[src]["editor"]}
        editor_doc_in={dst for dst in doc_in if evaluated[dst]["editor"]}
        doc_editor_pairs=(len(editor_doc_out)*len(editor_doc_in)-
                          len(editor_doc_out & editor_doc_in))
        editor_out={src for src in potential_out if evaluated[src]["editor"]}
        editor_in={dst for dst in potential_in if evaluated[dst]["editor"]}
        editor_pairs=len(editor_out)*len(editor_in)-len(editor_out & editor_in)
        all_pairs=len(all_out)*len(all_in)-len(all_out & all_in)
        candidates=[]
        for src in sorted(editor_out):
            for dst in sorted(editor_in):
                if src==dst:continue
                candidates.append({"origem":src,"destino":dst,
                                   "motivo_origem":reasons["out:"+src],
                                   "motivo_destino":reasons["in:"+dst]})
                if len(candidates)>=30:break
            if len(candidates)>=30:break
        documented_candidates=[]
        for src in sorted(editor_doc_out):
            for dst in sorted(editor_doc_in):
                if src==dst:continue
                documented_candidates.append({
                    "origem":src,"destino":dst,
                    "evidencia_origem":documentary_reasons["out:"+src],
                    "evidencia_destino":documentary_reasons["in:"+dst],
                    "setores_ambos_confirmados":(
                        src in potential_out and dst in potential_in)})
                if len(documented_candidates)>=30:break
            if len(documented_candidates)>=30:break
        blockers=[]
        if not all_pairs:
            blockers.append("Sem par IN/OUT cadastrado entre empresas distintas")
        if not pairs:
            blockers.append("Nao existe cadeia com setores e produto comprovados na DEF")
        if not editor_pairs:
            blockers.append("Nenhum par economico com company_def (cidade + prefab) valido nas duas empresas")
        if cid in extras and extras[cid].get("categoria") not in policy.CATEGORIES:
            blockers.append("Mercadoria nova sem regra economica homologada")
        if any(name not in baseline for name in all_in|all_out):
            blockers.append("Company possui empresa inexistente na DEF do mapa")
        status=("CANDIDATA_TESTE_ETS2" if editor_pairs else
                "ECONOMIA_SEM_EDITOR_VALIDADO" if pairs else
                "CANDIDATA_TESTE_COM_DOCUMENTO_INOUT" if doc_editor_pairs else
                "INOUT_DOCUMENTADO_SEM_EDITOR" if doc_pairs else
                "SEM_EVIDENCIA_ECONOMICA" if all_pairs else
                "SEM_PAR_CADASTRADO")
        result[cid]={
            "nome":title,"categoria":category,
            "status":status,"total_pares_no_scs":all_pairs,
            "origens_ativas":len(all_out),"destinos_ativos":len(all_in),
            "origens_com_evidencia":sorted(potential_out),
            "destinos_com_evidencia":sorted(potential_in),
            "pares_economicos_distintos":pairs,
            "pares_com_evidencia_inout_distintos":doc_pairs,
            "pares_com_editor_evidencia_inout":doc_editor_pairs,
            "origens_documentadas":sorted(doc_out),
            "destinos_documentados":sorted(doc_in),
            "candidatos_documentados_para_teste":documented_candidates,
            "pares_com_editor_em_ambas_empresas":editor_pairs,
            "candidatos_para_teste":candidates,
            "candidatos_truncados":max(0,editor_pairs-30),
            "bloqueios":blockers,
            "homologado_no_ets2":False,
        }
    return {
        "cargas":result,
        "cargas_com_par_cadastrado":sum(x["total_pares_no_scs"]>0 for x in result.values()),
        "cargas_com_par_economico_comprovavel":sum(x["pares_economicos_distintos"]>0 for x in result.values()),
        "cargas_com_par_evidencia_inout":sum(x["pares_com_evidencia_inout_distintos"]>0 for x in result.values()),
        "cargas_candidatas_documentais_teste":sum(x["pares_com_editor_evidencia_inout"]>0 for x in result.values()),
        "cargas_candidatas_teste_ets2":sum(x["pares_com_editor_em_ambas_empresas"]>0 for x in result.values()),
        "cargas_homologadas_no_ets2":0,
        "aviso":"Candidato no editor nao prova cidade/prefab acessivel, peso, mercado ou frete jogavel."
    }
