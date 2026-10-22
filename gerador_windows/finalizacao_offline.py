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


def run(g, sources, entries, output, *, game_log=None, log=lambda s:None):
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

        missing_economic=any(
            (r.get("qualidade_logistica") or {}).get(
                "cargas_com_par_economico_comprovavel",0)!=24
            for r in verified)
        missing_editor=any(
            (r.get("qualidade_logistica") or {}).get(
                "cargas_candidatas_teste_ets2",0)!=24
            for r in verified)
        residual_review=any(
            r["pendencias_revisao"] or r["empresas_classificacao_pendente"]
            or r["cargas_sem_rota_validada"] for r in verified)
        is_complete=(preflight_status=="PRONTO_PARA_TESTES_NO_JOGO" and
                     not missing_economic and not missing_editor and
                     not residual_review)
        final_status=("PRONTO_PARA_TESTE_NO_ETS2" if is_complete else
                      "CANDIDATAS_COM_LACUNAS_DOCUMENTADAS")
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
