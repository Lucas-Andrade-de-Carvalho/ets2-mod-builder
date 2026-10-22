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


def model_loading_evidence(g, sources, records, manifest):
    """Evidencia 1.54+: modelo, metodo de carga e carroceria real.

    A falta de dados nao e tratada como incompatibilidade comprovada:
    arquivos base do jogo e mods externos podem suprir dependencias.
    """
    body_methods=defaultdict(set)
    model_units=defaultdict(list)
    known_files=set()
    for label,archive in sources:
        known_files.update(archive)
        for path,raw in archive.items():
            if path.startswith("def/vehicle/trailer_owned/") and "/body/" in path:
                text=g.read_sii(raw)
                bodies=set(g.RE_TRAILER_BODY.findall(text))
                methods=set(re.findall(
                    r"(?im)^\s*cargo_loading_methods(?:\[\s*\d*\s*\])?\s*:\s*([a-z0-9_]+)",
                    text))
                for body in bodies:
                    body_methods[body].update(methods)
            if not re.fullmatch(r"def/vehicle/cargo/[a-z0-9_]+/[^/]+\.(?:sii|sui)",
                                path):
                continue
            text=g.read_sii(raw)
            if not re.search(r"\bcargo_model_match\s*:",text,re.I):
                continue
            cid=path.split("/")[3]
            methods=set(re.findall(
                r"(?im)^\s*loading_method\s*:\s*([a-z0-9_]+)",text))
            refs=re.findall(
                r"""(?im)^\s*data_path(?:\[\s*\d*\s*\])?\s*:\s*['"]?(/def/vehicle/cargo/[a-z0-9_./-]+)""",
                text)
            model_units[cid].append({
                "arquivo":path,
                "fonte":label,
                "loading_methods":sorted(methods),
                "accessories_referenciados":sorted(set(x.lstrip("/") for x in refs))
            })
    result={}
    for key in manifest:
        cid=g.catalogo_cargas.cargo_id(key)
        required_bodies=set(records[cid]["body"])
        allowed_methods=set().union(
            *(body_methods[b] for b in required_bodies)) if required_bodies else set()
        units=model_units.get(cid,[])
        actual_methods={x for unit in units for x in unit["loading_methods"]}
        refs={x for unit in units for x in unit["accessories_referenciados"]}
        missing=sorted(refs-known_files)
        explicit_mismatch=(bool(actual_methods and allowed_methods) and
                           not bool(actual_methods & allowed_methods))
        result[cid]={
            "cargo_model_match_nas_fontes":units,
            "metodos_do_modelo":sorted(actual_methods),
            "metodos_das_carrocerias":sorted(allowed_methods),
            "modelos_referenciados_ausentes_nas_fontes":missing,
            "incompatibilidade_explicita_de_metodos":explicit_mismatch,
            "status":("CONFLITO_DE_METODO" if explicit_mismatch else
                      "MODELO_ENCONTRADO" if units else
                      "SEM_MODELO_NAS_TRES_FONTES"),
            "alerta":"Nao prova disponibilidade no ETS2. Dados podem depender do jogo base/terceiros."
        }
    return result


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
    modern_models=model_loading_evidence(g,sources,records,manifest) if manifest else {}
    for cid,data in modern_models.items():
        if data["incompatibilidade_explicita_de_metodos"]:
            warnings.append(cid+": metodo de carga do modelo nao coincide com "
                            "cargo_loading_methods das carrocerias declaradas; "
                            "revisar arquivos 1.54+.")
        if data["modelos_referenciados_ausentes_nas_fontes"]:
            warnings.append(cid+": accessory_cargo_data nao encontrado nos "
                            "tres arquivos; verificar dependencias externas.")
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
        "carga_modelo_154":modern_models,
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
