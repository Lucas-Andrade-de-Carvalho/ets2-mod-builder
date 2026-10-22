"""Finalizacao OFFLINE dos tres mapas, com reauditoria dos SCS reais.

Os 3 arquivos corrigidos sao publicados atomicamente SOMENTE apos
inspecao do Librelato, auditoria da DEF de cada mapa e segunda auditoria.
A validacao dentro do ETS2 nao e simulada.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path

import auditor_existentes as audit
import homologacao_final as preflight

MAPS=preflight.EXPECTED_MAPS


def _fingerprint(g, paths):
    return {key:g.hash_source(path) for key,path in sorted(paths.items())}


def _run(g, sources, entries, output, *, game_log=None, log=lambda s:None):
    """Devolve arquivo completo candidato para jogo ou relatorio de bloqueio.

    Retorna status, arquivos corrigidos, motivacao e checksums. Nunca diz
    que o ETS2 foi homologado. Os SCS originais permanecem intocados.
    """
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    if set(entries)!=set(MAPS):
        raise ValueError("Finalizacao exige os mapas: "+", ".join(MAPS))
    needed=("mod","def1","def2","txt")
    if not all(sources.get(k) for k in needed):
        raise ValueError("Finalizacao exige MOD, DEF1, DEF2 e TXT")
    source_files={key:sources[key] for key in needed}
    inputs={**source_files}
    for map_name,entry in entries.items():
        for key in ("existing","map_def"):
            if not entry.get(key):
                raise ValueError(map_name+": falta "+key)
            inputs[map_name+":"+key]=entry[key]
    for key,path in inputs.items():
        if not Path(path).exists():
            raise FileNotFoundError(key+": "+str(path))
    hashes_before=_fingerprint(g,inputs)
    preflight_report=preflight.run(g,source_files,entries,out/"01_PRE_HOMOLOGACAO",
                                  game_log=game_log,log=log)
    preflight_status=preflight_report["status_pre_homologacao"]
    blocked=("BLOQUEADO_TECNICO","BLOQUEADO_AUDITORIA","BLOQUEADO_GAME_LOG")
    if preflight_status in blocked or preflight_report["ensaios_de_jogo_planejados"]!=72:
        result={
            "status":"BLOQUEADO_SEM_ENTREGA","preflight_status":preflight_status,
            "homologado_no_ets2":False,
            "nenhum_scs_publicado":True,
            "motivos":preflight_report["bloqueios"],
            "arquivos_corrigidos":[],
            "originais_preservados":hashes_before==_fingerprint(g,inputs)
        }
        (out/"RESULTADO_FINALIZACAO_OFFLINE.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        return result

    delivery=out/"02_CANDIDATAS_PARA_JOGO"
    if delivery.exists():
        raise FileExistsError("Pasta de saida ja existe; escolha uma nova pasta: "+
                              str(delivery))
    with tempfile.TemporaryDirectory(prefix="ets2_candidatos_",dir=out) as temporary:
        staging=Path(temporary)
        first=staging/"01_SCS_AUDITADOS"
        second=staging/"02_REAUDITORIA"
        log("Auditoria e criacao das tres Companies em area temporaria...")
        summaries=audit.run(g,entries,first,mode="corrigir",log=log,
                            professional=True,source_files=source_files)
        if {r["mapa"] for r in summaries}!=set(MAPS):
            raise ValueError("Faltam Companies: esperado exatamente MG/Eldorado/RBR")
        corrected={}
        output_hashes={}
        for report in summaries:
            name=report["mapa"]
            if not report.get("arquivo_corrigido"):
                raise ValueError(name+": nao foi exportado SCS corrigido")
            path=first/report["arquivo_corrigido"]
            if not path.is_file() or not zipfile.is_zipfile(path):
                raise ValueError(name+": SCS nao foi exportado corretamente")
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None:
                    raise ValueError(name+": entrada ZIP corrompida")
                if not any(p.startswith("def/company/") for p in archive.namelist()):
                    raise ValueError(name+": Company nao contem def/company")
            corrected[name]={"existing":path,"map_def":entries[name]["map_def"]}
            output_hashes[name]=g.hash_source(path)

        log("Reauditando as Companies geradas, sem modificar os originais...")
        verified=audit.run(g,corrected,second,mode="auditar",
                          log=log,professional=True,source_files=source_files)
        second_by_name={r["mapa"]:r for r in verified}
        issues=[]
        for first_report in summaries:
            name=first_report["mapa"]
            second_report=second_by_name.get(name)
            if second_report is None:
                issues.append(name+": falta reauditoria")
                continue
            if second_report["rotas_depois"]!=first_report["rotas_depois"]:
                issues.append(name+": reauditoria alterou matriz IN/OUT")
            if (second_report["arquivos_adicionados"] or
                second_report["arquivos_modificados"] or
                second_report["permissoes_removidas"]):
                issues.append(name+": segunda auditoria encontrou correcao residual")
            if output_hashes[name]!=g.hash_source(corrected[name]["existing"]):
                issues.append(name+": conteudo corrigido mudou na reauditoria")
        hashes_after=_fingerprint(g,inputs)
        if hashes_after!=hashes_before:
            issues.append("Os arquivos originais foram alterados indevidamente")
        if issues:
            result={
                "status":"BLOQUEADO_REAUDITORIA","homologado_no_ets2":False,
                "nenhum_scs_publicado":True,"motivos":issues,
                "preflight_status":preflight_status,
                "arquivos_corrigidos":[],
                "originais_preservados":hashes_after==hashes_before
            }
            (out/"RESULTADO_FINALIZACAO_OFFLINE.json").write_text(
                json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
            return result

        # ENTREGA DEFINITIVA exige 24 cadeias comprovaveis nos tres mapas.
        # Uma empresa preservada com atividade desconhecida NAO aprova
        # automaticamente o mercado de fretes. Isso deve BLOQUEAR os SCS,
        # nunca resultar em arquivo candidato apresentado como pronto.
        economic_problems=[]
        quality_by_map={}
        for report in verified:
            name=report["mapa"]
            quality=report.get("qualidade_logistica") or {}
            quality_by_map[name]=quality
            if len(quality.get("cargas",{}))!=24:
                economic_problems.append(name+": catalogo economico incompleto")
            economic_count=quality.get("cargas_com_par_economico_comprovavel",0)
            if economic_count!=24:
                economic_problems.append(
                    name+": apenas "+str(economic_count)+"/24 cargas com pares economicos")
            editor_count=quality.get("cargas_candidatas_teste_ets2",0)
            if editor_count!=24:
                economic_problems.append(
                    name+": apenas "+str(editor_count)+"/24 cargas com origem/destino editor")
            if report["pendencias_revisao"]:
                economic_problems.append(name+": "+
                    str(report["pendencias_revisao"])+" revisoes pontuais")
            if report["empresas_classificacao_pendente"]:
                economic_problems.append(name+": "+
                    str(report["empresas_classificacao_pendente"])+
                    " empresas com papel economico pendente")
            if report["cargas_sem_rota_validada"]:
                economic_problems.append(name+": cadeias sem par registrado: "+
                    ", ".join(report["cargas_sem_rota_validada"]))
            if report.get("status")!="AUDITORIA_ESTRUTURAL_CONCLUÍDA":
                economic_problems.append(name+": auditoria estrutural/economica pendente")
        if economic_problems:
            result={
                "status":"BLOQUEADO_ECONOMIA_REAL",
                "homologado_no_ets2":False,
                "nenhum_scs_publicado":True,
                "preflight_status":preflight_status,
                "originais_preservados":hashes_after==hashes_before,
                "arquivos_corrigidos":[],
                "cargas_esperadas":24,
                "mapas_reauditados":sorted(second_by_name),
                "reescritas_residuais":0,
                "motivos":economic_problems,
                "qualidade_por_mapa":{
                    name:{
                        "cargas_com_par_economico_comprovavel":
                            q.get("cargas_com_par_economico_comprovavel",0),
                        "cargas_candidatas_teste_ets2":
                            q.get("cargas_candidatas_teste_ets2",0)
                    }
                    for name,q in quality_by_map.items()},
                "aviso":"Nenhuma Company comercial sera publicada com "
                        "cadeias incompletas ou nao classificadas. "
                        "O teste no ETS2 nao foi executado."
            }
            (out/"RESULTADO_FINALIZACAO_OFFLINE.json").write_text(
                json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
            return result
        final_status="PRONTO_PARA_TESTE_NO_ETS2"
        result={
            "status":final_status,
            "homologado_no_ets2":False,
            "nenhum_scs_publicado":False,
            "preflight_status":preflight_status,
            "originais_preservados":True,
            "arquivos_corrigidos":[
                {"mapa":name,"arquivo":"01_SCS_AUDITADOS/"+corrected[name]["existing"].name,
                 "sha256":output_hashes[name]}
                for name in MAPS],
            "cargas_esperadas":24,
            "mapas_reauditados":sorted(second_by_name),
            "reescritas_residuais":0,
            "bloqueios_restantes":preflight_report["bloqueios"],
            "limites":"Sem jogabilidade, entrega, peso, prefab/cidade e game.log "
                      "testados de forma real, nao ha homologacao ETS2."
        }
        (staging/"RESULTADO_FINALIZACAO_OFFLINE.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        # Somente apos validar a trilha de auditoria completa.
        os.replace(staging,delivery)

    (out/"RESULTADO_FINALIZACAO_OFFLINE.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    log("Tres SCS tecnicamente revalidados e publicados em "+str(delivery)+
        ". Homologacao no ETS2 permanece pendente.")
    return result


def run(g, sources, entries, output, *, game_log=None, log=lambda s:None):
    """Falhas inesperadas tambem deixam motivo legivel sem SCS parcial."""
    try:
        return _run(g, sources, entries, output, game_log=game_log, log=log)
    except Exception as exc:
        try:
            root=Path(output)
            root.mkdir(parents=True,exist_ok=True)
            (root/"FALHA_FINALIZACAO_OFFLINE.json").write_text(
                json.dumps({
                    "status":"INTERROMPIDO",
                    "homologado_no_ets2":False,
                    "motivo":type(exc).__name__+": "+str(exc),
                    "acao":"Verifique os arquivos fonte. Nada desta tentativa "
                           "pode ser tratado como Company homologada."
                },indent=2,ensure_ascii=False),encoding="utf-8")
        except OSError:
            pass
        raise
