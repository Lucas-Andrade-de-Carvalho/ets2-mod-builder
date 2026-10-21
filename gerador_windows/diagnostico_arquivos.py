"""Diagnostico reprodutivel dos tres arquivos originais do reboque e TXT.

Este relatorio NUNCA modifica os SCS e NAO equivale a testar no ETS2.
"""
from __future__ import annotations
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import catalogo_fontes as catalogo


def inspect(g, source_files, txt_path, output):
    sources=[]
    fingerprints=[]
    definitions=defaultdict(list)
    warnings=[]
    errors=[]
    for label,key in (("MOD PRINCIPAL","mod"),("DEF COMPANY 1","def1"),
                      ("DEF COMPANY 2","def2")):
        path=Path(source_files[key])
        archive=g.zip_members(path)
        if not archive:
            raise ValueError(label+": nenhum arquivo def/ identificado")
        sources.append((label,archive))
        fingerprints.append({"arquivo":path.name,"papel":label,
                             "sha256":g.hash_source(path),
                             "definicoes_lidas":len(archive)})
        for internal,raw in archive.items():
            m=g.RE_CARGO_PATH.search(internal)
            if not m or m.group(2) is not None or not internal.endswith((".sii",".sui")):
                continue
            cid=m.group(1)
            if not catalogo.CARGO_NUMBER.fullmatch(cid):
                continue
            txt=g.read_sii(raw)
            if cid not in (unit.lower() for unit in g.RE_CARGO_UNIT.findall(txt)):
                continue
            bodies=sorted(set(g.RE_CARGO_BODY.findall(txt)))
            definitions[cid].append({
                "fonte":label,"caminho":internal,
                "sha256":hashlib.sha256(raw).hexdigest(),
                "body_types":bodies,
            })
    # A existencia de multiplas copias nem sempre e defeito: conteudos iguais
    # sao deduplicados, divergencias tecnicas exigem investigacao.
    conflicts=[]
    for cid,entries in sorted(definitions.items(),key=lambda kv:catalogo.sort_key(kv[0])):
        payloads={x["sha256"] for x in entries}
        types={tuple(x["body_types"]) for x in entries}
        if len(types)>1:
            errors.append(cid+": body_types divergentes entre MOD/DEF1/DEF2")
            conflicts.append({"carga":cid,"tipo":"body_types_divergentes",
                              "fontes":entries})
        elif len(payloads)>1:
            warnings.append(cid+": definicoes diferentes em arquivos distintos, "
                            "mesmo body_type; revisar nome/massa/outros campos")
            conflicts.append({"carga":cid,"tipo":"conteudo_diferente",
                              "fontes":entries})
    manifest={}
    extras={}
    records={}
    owned=set()
    ownable_defs=set()
    totals={}
    try:
        records,_legacy,owned,ownable_defs,totals=g.cargo_inventory(sources)
        manifest,extras=catalogo.from_originals(g.MANIFEST,records,txt_path)
        if not owned:
            errors.append("Nenhuma carroceria de trailer_owned identificada")
        for key,(category,title) in manifest.items():
            cid=catalogo.cargo_id(key)
            record=records[cid]
            if not record["body"]:
                errors.append(cid+": body_types da carga nao encontrado")
            elif owned and not (set(record["body"])&owned):
                errors.append(cid+": nenhuma carroceria propria compativel")
    except (ValueError,KeyError,OSError) as exc:
        errors.append(str(exc))
    cargos=[]
    for key,(category,title) in sorted(manifest.items(),
                                       key=lambda kv:catalogo.sort_key(kv[0])):
        cid=catalogo.cargo_id(key)
        original=records[cid]
        cargos.append({
            "id":cid,"nome_txt":title,"categoria_economica":category,
            "body_types":sorted(original["body"]),
            "carrocerias_instaladas_compativeis":sorted(set(original["body"])&owned),
            "definicao_origem":original["source"],
            "caminho":original["path"],
            "sha256":hashlib.sha256(original["raw"]).hexdigest(),
            "ocorrencias_originais":definitions.get(cid,[]),
            "validado_no_ets2":False,
        })
    report={
        "resultado":"BLOQUEADO" if errors else
                    ("REVISAO_NECESSARIA" if warnings else "TECNICAMENTE_COHERENTE"),
        "alerta_homologacao":"Integridade de arquivo nao comprova empresa/cidade/prefab ou rotas no ETS2",
        "fontes":fingerprints,
        "arquivo_txt":Path(txt_path).name if txt_path else None,
        "total_cargas_catalogo":len(manifest),
        "cargas_adicionais":sorted(extras,key=catalogo.sort_key),
        "carrocerias_encontradas":sorted(owned),
        "trailer_defs_encontrados":sorted(ownable_defs),
        "totais_tecnicos":totals,
        "cargas":cargos,
        "definicoes_duplicadas_ou_divergentes":conflicts,
        "erros":errors,
        "avisos":warnings,
    }
    path=Path(output);path.mkdir(parents=True,exist_ok=True)
    dest=path/"DIAGNOSTICO_LIBRELATO_CARGAS_ORIGINAIS.json"
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return dest,report
