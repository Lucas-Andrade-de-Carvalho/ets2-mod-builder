"""Pre-homologacao reprodutivel dos arquivos REAIS do ETS2.

Nao finge dirigir um frete. Valida os 3 SCS do Librelato/TXT, audita DEF +
Company de cada mapa SEM alterar os arquivos e gera a matriz de ensaios
necessarios no jogo. O status final nunca afirma homologacao sem ETS2.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
from pathlib import Path

import auditor_existentes as audit
import diagnostico_arquivos as diag
import catalogo_fontes as catalogo

EXPECTED_MAPS=("Minas_Gerais","Eldorado","RBR")
BLOCKED={"BLOQUEADO_TECNICO","BLOQUEADO_ECONOMICO"}


def assess_logs(path):
    """Extrair diagnostico de game.log.txt; log nao prova frete entregue."""
    if not path:
        return {"situacao":"NAO_FORNECIDO","erros":[],"avisos":[],
                "teste_real_ets2_comprovado":False}
    f=Path(path)
    if not f.is_file():
        raise FileNotFoundError("game.log.txt nao encontrado: "+str(f))
    if f.stat().st_size>80_000_000:
        raise ValueError("game.log.txt excede limite de seguranca (80 MB)")
    errors=[];warnings=[]
    for n,line in enumerate(f.read_text(encoding="utf-8-sig",errors="replace").splitlines(),1):
        if re.search(r"<ERROR>|\berror\s*:",line,re.I):
            if len(errors)<250:errors.append({"linha":n,"texto":line[:500]})
        elif re.search(r"<WARNING>|\bwarning\s*:",line,re.I):
            if len(warnings)<150:warnings.append({"linha":n,"texto":line[:500]})
    return {"situacao":("ERROS_DE_JOGO_ENCONTRADOS" if errors else
                         "SEM_ERROS_TEXTUAIS_DETECTADOS"),
            "arquivo":f.name,"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
            "erros":errors,"avisos":warnings,
            "erros_truncados":len(errors)==250,
            "teste_real_ets2_comprovado":False,
            "observacao":"Log limpo nao prova carga visivel, frete iniciado ou entrega concluida."}


def run(g, sources, entries, out_path, game_log=None,
        log=lambda message:None, expected_maps=EXPECTED_MAPS):
    """Auditar insumos sem sobrescrever arquivos de entrada.

    O preflight por mapa (RBR isolado) NAO substitui homologacao dos 3
    mapas nem prova frete entregue dentro do ETS2.
    """
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    required={"mod","def1","def2","txt"}
    if required-set(sources):
        raise ValueError("Faltam fontes: "+", ".join(sorted(required-set(sources))))
    requested=set(expected_maps)
    if (not requested or not requested.issubset(set(EXPECTED_MAPS))
            or set(entries)!=requested):
        label=("Minas_Gerais, Eldorado e RBR"
               if tuple(expected_maps)==EXPECTED_MAPS else
               ", ".join(expected_maps))
        raise ValueError("Pre-homologacao exige exatamente os mapas escolhidos: "+
                         label)
    source_paths={name:Path(sources[name]) for name in required}
    for name,path in source_paths.items():
        if not path.exists():raise FileNotFoundError(name+": "+str(path))
    for name,entry in entries.items():
        for key in ("existing","map_def"):
            if not entry.get(key) or not Path(entry[key]).exists():
                raise FileNotFoundError(name+" / "+key+" ausente")
    out_diag=out/"01_LIBRELATO"
    diag_path, diag_result=diag.inspect(g,sources,sources["txt"],out_diag)
    log("Diagnostico tecnico: "+diag_result["resultado"])
    logs=assess_logs(game_log)
    rows=[]
    summaries=[]
    blocked=[]
    audit_error=None
    if diag_result["erros"]:
        blocked.extend(diag_result["erros"])
    if diag_result["total_cargas_catalogo"]!=24:
        blocked.append("Esperadas 24 cargas neste projeto; encontradas "+
                       str(diag_result["total_cargas_catalogo"]))
    if not blocked:
        log("Iniciando auditoria dos tres mapas em modo somente leitura...")
        try:
            summaries=audit.run(g,entries,out/"02_MAPAS",mode="auditar",
                               log=log,professional=True,source_files=sources)
        except (ValueError, OSError, KeyError, RuntimeError) as exc:
            audit_error=type(exc).__name__+": "+str(exc)
            blocked.append("Auditoria dos mapas falhou: "+audit_error)
        for summary in summaries:
            map_name=summary["mapa"]
            quality=summary.get("qualidade_logistica") or {}
            matrix=quality.get("cargas",{})
            for cid,entry in sorted(matrix.items(),key=lambda kv:catalogo.sort_key(kv[0])):
                confirmed=entry.get("candidatos_para_teste",[])
                documented=entry.get("candidatos_documentados_para_teste",[])
                regional=entry.get("candidatos_simulacao_regional",[])
                suggested=confirmed or documented or regional
                first=suggested[0] if suggested else {}
                evidence_level=("SETOR_E_ECONOMIA" if confirmed else
                                "MESMA_MERCADORIA_IN_OUT_SETOR_PENDENTE"
                                if documented else
                                "ADAPTACAO_REGIONAL_AUTORIZADA_SEM_PROVA_INOUT"
                                if regional else "SEM_PAR_DOCUMENTAL_EDITOR")
                rows.append({
                    "mapa":map_name,"carga":cid,"mercadoria":entry["nome"],
                    "situacao_auditoria":entry["status"],
                    "nivel_evidencia":evidence_level,
                    "origem_sugerida":first.get("origem",""),
                    "destino_sugerido":first.get("destino",""),
                    "frete_visivel_no_ets2":"",
                    "coleta_realizada":"",
                    "entrega_realizada":"",
                    "carga_modelo_visivel":"",
                    "evidencia_de_teste":"",
                    "observacoes_de_jogo":""
                })
            if summary.get("pendencias_revisao"):
                blocked.append(map_name+": "+
                               str(summary["pendencias_revisao"])+" revisoes pontuais")
            if summary.get("permissoes_plausiveis_sem_evidencia_def"):
                blocked.append(map_name+": "+
                               str(summary["permissoes_plausiveis_sem_evidencia_def"])+
                               " fretes antigos economicamente plausiveis, "
                               "mas ainda sem comprovacao de mercadoria na DEF")
            if summary.get("empresas_classificacao_pendente"):
                blocked.append(map_name+": "+
                               str(summary["empresas_classificacao_pendente"])+
                               " empresas sem classificacao")
            if quality.get("cargas_com_par_economico_comprovavel",0)<24:
                blocked.append(map_name+": apenas "+
                               str(quality.get("cargas_com_par_economico_comprovavel",0))+
                               "/24 cargas com pares economicos")
            if quality.get("cargas_candidatas_teste_ets2",0)<24:
                blocked.append(map_name+": apenas "+
                               str(quality.get("cargas_candidatas_teste_ets2",0))+
                               "/24 cargas com ambas empresas no editor")
    if logs["situacao"]=="ERROS_DE_JOGO_ENCONTRADOS":
        blocked.append("game.log.txt possui erros; investigar antes da entrega")
    result=("BLOQUEADO_TECNICO" if diag_result["erros"] or
            diag_result["total_cargas_catalogo"]!=24 else
            "BLOQUEADO_AUDITORIA" if audit_error else
            "BLOQUEADO_ECONOMICO" if blocked and
                 logs["situacao"]!="ERROS_DE_JOGO_ENCONTRADOS" else
            "BLOQUEADO_GAME_LOG" if blocked else
            "PRONTO_PARA_TESTES_NO_JOGO")
    # NENHUM status de preflight certifica um frete no ETS2.
    cert={
        "versao_protocolo":"1.0",
        "status_pre_homologacao":result,
        "homologado_no_ets2":False,
        "arquivos_librelato":str(diag_path.name),
        "relatorio_librelato":str(diag_path.relative_to(out)),
        "arquivos_fonte":[{"id":item["papel"],"nome":item["arquivo"],
                           "sha256":item["sha256"]}
                          for item in diag_result["fontes"]],
        "txt":Path(sources["txt"]).name,
        "mapas_esperados":list(expected_maps),
        "preflight_isolado":requested!=set(EXPECTED_MAPS),
        "mapas": [{
            "nome":m["mapa"],"status":m["status"],
            "rotas_registradas":m["rotas_completas_depois"],
            "cargas_economicamente_justificadas":
                (m.get("qualidade_logistica") or {}).get(
                    "cargas_com_par_economico_comprovavel",0),
            "cargas_candidatas_de_teste":
                (m.get("qualidade_logistica") or {}).get(
                    "cargas_candidatas_teste_ets2",0),
            "revisoes_pontuais":m.get("pendencias_revisao"),
            "fretes_herdados_plausiveis_sem_def":
                m.get("permissoes_plausiveis_sem_evidencia_def",0),
            "empresas_sem_classificacao":m.get("empresas_classificacao_pendente"),
            "hash_company_original":m["sha256_entrada"],
            "hash_def_original":m["sha256_def"],
        } for m in summaries],
        "game_log":logs,
        "avisos_tecnicos":diag_result["avisos"],
        "erro_auditoria":audit_error,
        "bloqueios":blocked,
        "cargas_esperadas_por_mapa":24,
        "ensaios_de_jogo_planejados":len(rows),
        "teste_de_entrega_no_jogo_automatico":False,
        "criterio":"O preflight nao acessa o jogo; a presenca de editor ou "
                  "log limpo nao confirma mercado, coleta ou entrega."
    }
    (out/"RESULTADO_PRE_HOMOLOGACAO.json").write_text(
        json.dumps(cert,indent=2,ensure_ascii=False),encoding="utf-8")
    with (out/"MATRIZ_ENSAIOS_ETS2.csv").open("w",newline="",encoding="utf-8-sig") as fp:
        columns=("mapa","carga","mercadoria","situacao_auditoria",
                 "nivel_evidencia","origem_sugerida","destino_sugerido",
                 "frete_visivel_no_ets2",
                 "coleta_realizada","entrega_realizada","carga_modelo_visivel",
                 "evidencia_de_teste","observacoes_de_jogo")
        writer=csv.DictWriter(fp,fieldnames=columns,delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    (out/"COMO_HOMOLOGAR_NO_JOGO.txt").write_text(
        "1. Habilite o MOD, DEF1/DEF2 e a Company corrigida do mapa em perfil de teste.\n"
        "2. Confirme compatibilidade de versao, ordem dos mods e ausencia de erro relevante no game.log.txt.\n"
        "3. Para CADA carga do mapa, veja um frete compativel no mercado, pegue o "
        "reboque, inicie o servico e conclua a entrega em empresa distinta.\n"
        "4. Anote empresa de origem/destino, visibilidade da carga e evidencias "
        "individuais na MATRIZ_ENSAIOS_ETS2.csv.\n"
        "5. Execute nos mapas selecionados; repita nos demais para homologacao global. Se a DEF nao tiver "
        "produtor/comprador verdadeiro, registre a lacuna: NAO crie um fornecedor ficticio.\n"
        "6. Reanalise game.log.txt ao final. Versao do jogo e mods dependentes "
        "devem estar identificados.\n"
        "ATENCAO: resultado de preflight e checklist nao sao homologacao real.\n",
        encoding="utf-8")
    return cert
