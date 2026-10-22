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


def run(g, sources, entries, out_path, game_log=None, log=lambda message:None):
    """Auditar integralmente os insumos sem sobrescrever arquivos do usuario.

    A ausencia de mapas, empresas ou itens do trailer bloqueia a etapa.
    Exige explicitamente os tres mapas, nao apenas um subconjunto.
    """
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    required={"mod","def1","def2","txt"}
    if required-set(sources):
        raise ValueError("Faltam fontes: "+", ".join(sorted(required-set(sources))))
    if set(entries)!=set(EXPECTED_MAPS):
        raise ValueError("Pre-homologacao exige Minas_Gerais, Eldorado e RBR")
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
    if diag_result["erros"]:
        blocked.extend(diag_result["erros"])
    if diag_result["total_cargas_catalogo"]!=24:
        blocked.append("Esperadas 24 cargas neste projeto; encontradas "+
                       str(diag_result["total_cargas_catalogo"]))
    if not blocked:
        log("Iniciando auditoria dos tres mapas em modo somente leitura...")
        summaries=audit.run(g,entries,out/"02_MAPAS",mode="auditar",
                           log=log,professional=True,source_files=sources)
        for summary in summaries:
            map_name=summary["mapa"]
            quality=summary.get("qualidade_logistica") or {}
            matrix=quality.get("cargas",{})
            for cid,entry in sorted(matrix.items(),key=lambda kv:catalogo.sort_key(kv[0])):
                suggested=entry.get("candidatos_para_teste",[])
                first=suggested[0] if suggested else {}
                rows.append({
                    "mapa":map_name,"carga":cid,"mercadoria":entry["nome"],
                    "situacao_auditoria":entry["status"],
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
    result=("BLOQUEADO_TECNICO" if diag_result["erros"] or
            diag_result["total_cargas_catalogo"]!=24 else
            "BLOQUEADO_ECONOMICO" if blocked else
            "PRONTO_PARA_TESTES_NO_JOGO")
    if logs["situacao"]=="ERROS_DE_JOGO_ENCONTRADOS":
        blocked.append("game.log.txt possui erros; investigar antes da entrega")
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
            "empresas_sem_classificacao":m.get("empresas_classificacao_pendente"),
            "hash_company_original":m["sha256_entrada"],
            "hash_def_original":m["sha256_def"],
        } for m in summaries],
        "game_log":logs,
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
                 "origem_sugerida","destino_sugerido","frete_visivel_no_ets2",
                 "coleta_realizada","entrega_realizada","carga_modelo_visivel",
                 "evidencia_de_teste","observacoes_de_jogo")
        writer=csv.DictWriter(fp,fieldnames=columns,delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    (out/"COMO_HOMOLOGAR_NO_JOGO.txt").write_text(
        "1. Habilite os 3 SCS originais e a Company corrigida do mapa em um perfil de testes.\n"
        "2. Confirme compatibilidade de versao, ordem dos mods e ausencia de erro relevante no game.log.txt.\n"
        "3. Para CADA carga do mapa, veja um frete compativel no mercado, pegue o "
        "reboque, inicie o servico e conclua a entrega em empresa distinta.\n"
        "4. Anote empresa de origem/destino, visibilidade da carga e evidencias "
        "individuais na MATRIZ_ENSAIOS_ETS2.csv.\n"
        "5. Execute em Minas Gerais, Eldorado e RBR. Se a DEF nao tiver "
        "produtor/comprador verdadeiro, registre a lacuna: NAO crie um fornecedor ficticio.\n"
        "6. Reanalise game.log.txt ao final. Versao do jogo e mods dependentes "
        "devem estar identificados.\n"
        "ATENCAO: resultado de preflight e checklist nao sao homologacao real.\n",
        encoding="utf-8")
    return cert
