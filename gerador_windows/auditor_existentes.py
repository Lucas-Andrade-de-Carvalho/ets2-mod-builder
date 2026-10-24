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
import homologacao_logistica
import recuperacao_editor
import cobertura_maxima_rbr

SII_EXT=(".sii",".sui")
CARGO_FIELD = re.compile(r'(?im)^([ \t]*cargo[ \t]*:[ \t]*)"?cargo\.([a-z][a-z0-9_]*)"?(?=[ \t]*(?:}[ \t]*)*(?:(?:#|//)[^\r\n]*)?\r?$)')
OTHER_FIELD = re.compile(r'(?im)^\s*cargo\s*:\s*"?cargo\.([a-z0-9_]+)"?')
# Tokens SII sao ASCII; operar sobre bytes evita destruir comentarios ou
# nomes cp1252/latin1 quando neutralizando uma carga especifica.
CARGO_FIELD_BYTES = re.compile(CARGO_FIELD.pattern.encode("ascii"))
OTHER_FIELD_BYTES = re.compile(OTHER_FIELD.pattern.encode("ascii"))
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
    # Ainda validar o SII antes de procurar tokens: um arquivo binario
    # nao pode ser confundido com DEF textual.
    g.read_sii(raw)
    found=[m.group(2).decode("ascii").lower()
           for m in CARGO_FIELD_BYTES.finditer(raw)]
    documented=OTHER_FIELD_BYTES.findall(raw)
    if len(found)!=len(documented):
        # Sem essa verificacao, sintaxe nao reconhecida podia sumir
        # do inventario e reaparecer como cargo duplicado no novo SCS.
        raise ValueError(
            "Company contem linha cargo: em sintaxe nao reconhecida; "
            "revisar aspas, comentarios e final da linha antes de "
            "neutralizar ou adicionar qualquer permissao")
    return found

def disable_id(g, raw, cargo_id):
    file_active_ids(g,raw)
    token=cargo_id.encode("ascii")
    removed=[0]
    def transform(m):
        if m.group(2).lower()!=token:
            return m.group(0)
        removed[0]+=1
        return m.group(1)+b'""'
    out=CARGO_FIELD_BYTES.sub(transform,raw)
    if removed[0]<1:
        raise ValueError("Cargo nao localizado ao neutralizar: "+cargo_id)
    # Reescrever apenas bytes do campo cargo. A empresa pode ter CRLF,
    # BOM, comentarios ou nomes Latin-1, preservados integralmente.
    return out

def safe_reason(g, c,cat,direction,map_name,professional=False,spec=None):
    if professional:
        regional=professional_policy.regional_approved_decision(
            c,cat,direction,map_name)
        if regional is not None and regional.allowed:
            return regional.reason
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
    if professional:
        regional=professional_policy.regional_approved_decision(
            c,cat,direction,map_name)
        if regional is not None and regional.allowed:
            # Escopo MG/Eldorado, somente carga5/pluma e carga24/coco.
            # Permitir inclusive company role desconhecido se o
            # nome for explicitamente fazenda/mercearia/CEASA/armazem.
            return regional.reason
    why=safe_reason(g,c,cat,direction,map_name,professional=professional,spec=spec)
    explicit_custom=(spec is not None and
                     professional_policy.norm(c.name) in spec.get(direction+"_companies", ()))
    if not why:return None
    if professional and c.role=="desconhecida" and spec is None:
        # Uma empresa ficticia nao precisa ter ramo conhecido para usar
        # uma das variantes Librelato da MESMA mercadoria do IN/OUT original.
        # Nao permite nova categoria nem troca de direcao sem evidencia.
        original=(c.old_in if direction=="in" else c.old_out)
        if cat in professional_policy.cargo_categories(original):
            return "equivalencia comprovada pelo IN/OUT da DEF: "+why
        return None
    if not (explicit_confidence(c) or explicit_custom):return None
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

def proven_incompatibility(company, category, direction, spec=None, map_name=None):
    """So exclui automaticamente contradicoes claras, nao mera falta de prova.

    Um setor reconhecido nao demonstra que todas as suas outras cargas
    sejam invalidas. Fazendas podem ter culturas secundarias; pecuaristas
    podem plantar; cooperativas armazenam e revendem varias mercadorias.
    """
    role=company.role
    if professional_policy.norm(map_name or "")=="eldorado":
        original=professional_policy.cargo_categories(
            company.old_in if direction=="in" else company.old_out)
        if category=="algodao" and category not in original:
            return ("Eldorado: pluma/algodao NAO e excecao; "
                    "sem esta mercadoria no IN/OUT original da DEF")
        if (category=="racao" and direction=="out"
                and role in {"fazenda","fazenda_soja","fazenda_batata",
                             "fazenda_laranja","eldorado_lavoura"}
                and (professional_policy.cargo_categories(
                    company.old_out)&{"milho","soja"})):
            return ("Lavoura de milho/soja nao fabrica racao; "
                    "a saida de graos nao justifica carga17-20")
        import eldorado_ingles
        scoped=eldorado_ingles.inherited_conflict(
            company,category,direction,professional_policy)
        if scoped is not None:
            return scoped
    if (professional_policy.norm(map_name or "") in
            professional_policy.REGIONAL_APPROVED_MAPS and
            category in {"algodao","coco"}):
        # A excecao solicitada exige que NEM as permissoes ANTIGAS
        # continuem mandando pluma/coco para postos, construcoes ou
        # industrias sem nexo. Restricao exclusiva MG/Eldorado.
        bad_roles={
            "obras","posto_combustivel","infra_passageiros",
            "transportadora","mineracao_minerios","mineracao_calcario",
            "siderurgica","metalurgica","premoldados","cimenteira",
            "automotiva_fabrica","terminal_quimico_inferido",
            "fabricante_descartaveis_inferido",
            "revenda_maquinas_agricolas_inferida","reciclagem_inferida"
        }
        identifying_name=professional_policy.norm(
            company.name+" "+getattr(company,"display_name",""))
        if (role in bad_roles or re.search(
                r"(?:^|_)(?:obra|posto_combustivel|posto_gasolina|"
                r"construcao|construction_site|gas_station)",identifying_name)):
            return ("ADAPTACAO REGIONAL: pluma/coco nao devem ser "
                    "carregados ou descarregados em obra, posto ou "
                    "industria incompatível; permissao legada neutralizada")
    # Minas: etapa anterior adicionava pluma a distribuidores
    # alimenticios genericos (ex.: abcatacado), embora o usuario tenha
    # autorizado destinos agricolas/texteis e nao atacados de cerveja.
    # Reverter APENAS a permissao de pluma herdada para unidade que
    # comprovadamente recebe alimentos, mas nao fibra/armazenagem textil.
    if (professional_policy.norm(map_name or "") in
            professional_policy.REGIONAL_APPROVED_MAPS and
            category=="algodao" and direction=="in" and
            role=="distribuidor" and
            professional_policy.regional_approved_decision(
                company,"algodao","in",map_name) is None):
        groceries=professional_policy.cargo_categories(company.old_in)
        if (groceries & {"cerveja","batata","laranja","coco"} and
                "algodao" not in groceries):
            return ("Distribuidor de alimentos/cerveja sem operacao "
                    "agricola/textil de algodao: pluma herdada de "
                    "regra regional antiga excessivamente ampla")
    if spec is not None:
        if role in spec.get("forbidden_roles",()):
            return "Setor explicitamente proibido no cadastro desta mercadoria"
        return None
    # Atividades fisicamente incompatíveis prevalecem mesmo se a DEF tiver
    # um cargo muito genérico: transportadora não vira produtora agrícola.
    if role=="transportadora":
        return "Transportadora nao e unidade de producao, compra ou revenda comprovada"
    if role=="infra_passageiros":
        return ("Rodoviaria, posto policial ou subestacao nao opera carga "
                "comercial comprovada das 24 mercadorias")
    if role=="bananal" and (direction!="in" or category!="adubo"):
        return "Bananal nao fornece outras culturas nem recebe genericamente estes produtos"
    if direction=="out" and (
        (role in {"automotiva_fabrica","maquinas"} and category=="bobina") or
        (role=="premoldados" and category=="cimento") or
        (role=="metalurgica" and category=="tijolo")
    ):
        return "Fabricante identificado nao produz a materia-prima correspondente"
    original=professional_policy.cargo_categories(
        company.old_in if direction=="in" else company.old_out)
    if category in original:
        # Outros setores: nao apagar mercadoria realmente declarada no
        # IN/OUT autentico sem uma contradicao material acima.
        return None
    # Empresas ficticias reclassificadas por forte evidencia DIRECIONAL.
    # Nao confundir quimicos com supermarket/obra nem descartaveis com
    # fabricacao de cimento/tijolos. As mercadorias documentadas na
    # propria direcao foram preservadas no teste acima.
    if role=="terminal_quimico_inferido":
        return ("Fluxo predominante de quimicos perigosos no IN e OUT "
                "da DEF, sem esta mercadoria do Librelato; remover "
                "permissao antiga de setor errado")
    if role=="fabricante_descartaveis_inferido":
        return ("Fabrica de copos, pratos e talheres descartaveis; "
                "nao produz nem recebe automaticamente esta "
                "mercadoria Librelato sem IN/OUT original")
    if role=="reciclagem_inferida":
        return ("Reciclagem documentada de residuos/paletes; "
                "nao assumir outras 23 cargas sem produto no IN/OUT")
    if role=="revenda_maquinas_agricolas_inferida":
        return ("Venda documentada de maquinas agricolas e fertilizante "
                "mas nao desta colheita/carga na direcao original")
    # RBR: extracao de troncos exige maquinaria florestal Ponsse e
    # expedicao de madeira bruta. Fretes legados de milho, soja ou
    # racao para esses pontos vieram de mapeamentos genericos de IN/OUT
    # e nao fazem sentido com o fluxo de madeira documentado.
    if role=="madeireira":
        ins={professional_policy.norm(x) for x in company.old_in}
        outs={professional_policy.norm(x) for x in company.old_out}
        extraction=(
            any(re.fullmatch(r"ponsse[0-9]*",v) for v in ins) and
            bool(outs & {"troncos","troncos_di","logs","timber"})
        )
        if extraction and category in {
                "milho","soja","sorgo","racao","batata","laranja",
                "coco","algodao","cerveja","cimento","bobina",
                "tijolo","granito"}:
            return ("Empresa comprovadamente dedicada a extracao florestal "
                    "(colheitadeiras Ponsse IN, toras OUT): esta carga "
                    "herdada nao combina com a operacao original")
    if role in {"posto_combustivel","mineracao_minerios"}:
        return ("A DEF original comprova combustiveis/minerios brutos, "
                "nao esta carga do Librelato; permissao legada contraditoria")
    # RBR: refrigerante nao e cerveja. O nome da marca e o OUT da
    # DEF demonstram bebida NAO alcoolica; so preservar cerveja se o
    # proprio IN/OUT original trouxer identificador especifico de beer.
    # Nao bloquear paletes documentados (retorno de embalagens).
    if role=="fabricante_refrigerantes" and category not in original:
        return ("Industria de refrigerantes nao possui IN/OUT original "
                "para esta mercadoria Librelato; nao extrapolar bebida "
                "generica para cerveja, graos ou outros produtos")
    if role=="agroinsumos" and direction=="in" and category in {
            "milho","soja"}:
        return ("Revenda de insumos rurais nao recebeu estes graos no "
                "IN original; evitar converter loja de adubo em silo "
                "de colheita sem prova documental")
    # Negocios especializados nao sao exportadores de todo tipo de
    # produto apenas porque a Company antiga lhes atribuiu fretes.
    # Documentacao ORIGINAL da mesma categoria e direcao foi avaliada
    # acima e sempre prevalece.
    if role in {"recebedor_agricola_inferido",
                 "expedidor_residuos_inferido",
                 "entreposto_madeira_inferido"}:
        return ("Atividade comprovada por IN/OUT direcional, mas esta "
                "permissao herdada nao tem o mesmo produto e direcao "
                "na DEF; nao extrapolar ramo inferido")
    if role=="revenda_fertilizante" and category!="adubo":
        return ("Revenda especializada de fertilizante sem IN/OUT "
                "original desta mercadoria; nao fabricar colheita/racao")
    if role=="revenda_racao" and category not in {"racao"}:
        return ("Loja de racao nao produz nem recebe grãos sem IN/OUT "
                "especifico da DEF na direcao existente")
    if role=="obras" and direction=="out" and category in {
            "cimento","tijolo","granito","madeira","bobina"}:
        return ("Canteiro de obras consome material; expedicao de "
                "material novo sem OUT original nao e fornecedor")
    if role in {"fabrica_moveis","fabrica_paineis"} and direction=="out" and (
            category in {"madeira","palete"}):
        return ("Produto final industrial nao equivale a madeira bruta "
                "ou palete da carga Librelato sem OUT original")
    if role=="fabrica_moveis" and category in {
            "milho","soja","sorgo","adubo","racao","cerveja",
            "batata","laranja","coco","algodao"}:
        return ("Industria de moveis nao demonstrou operar esta carga "
                "rural ou alimenticia na DEF original")
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
    cargo_model_evidence={}
    if professional:
        if not source_files or any(k not in source_files for k in ("mod","def1","def2")):
            raise ValueError("Auditoria V3 precisa dos arquivos originais do reboque: MOD, DEF1 e DEF2.")
        originals=[]
        for label in ("mod","def1","def2"):
            originals.append((label,g.zip_members(source_files[label])))
        cargo_records,_legacy,owned,_defs,_totals=g.cargo_inventory(originals)
        manifest,extras=catalogo_cargas.from_originals(
            g.MANIFEST,cargo_records,(source_files or {}).get("txt"))
        archive_paths={p.lower() for _name,archive in originals for p in archive}
        for cid in extras:
            files=sorted(p for p in archive_paths
                         if p.startswith("def/vehicle/cargo/"+cid+"/"))
            cargo_model_evidence[cid]={
                "arquivos_em_def_vehicle_cargo":files[:30],
                "evidencia_modelo_embarcado":bool(files),
                "validacao_no_ets2":"PENDENTE",
                "observacao":("ETS2 1.54+ pode exigir cargo_model_match e "
                              "accessory_cargo_data. Presenca de arquivos nao "
                              "garante funcionalidade; ausencia pode indicar "
                              "dependencia de outro mod ou do jogo.")
            }
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
        editor_recovery=recuperacao_editor.recover(
            g,baseline,source,entry.get("editor_source"))
        for c in baseline.values():
            if professional:
                if name.lower()=="eldorado":
                    c._eldorado_map=True
                    import eldorado_ingles
                    scoped=eldorado_ingles.infer_identity(c,professional_policy)
                    if scoped is not None:
                        c._eldorado_identity=scoped
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
        if professional and name.lower()=="eldorado":
            import eldorado_ingles
            eldorado_ingles.export_translation_reports(baseline,out)
            identified=sum(getattr(c,"_eldorado_identity",None) is not None
                           for c in baseline.values())
            log("ELDORADO: dicionario de cargas inglesas e perfis: "+
                str(identified)+" empresas com classificacao dedicada; "+
                "TRADUCAO_DEF_ELDORADO.csv / PERFIS_ECONOMICOS_ELDORADO.csv")
        if not source:raise ValueError(name+": Company existente vazia ou ilegivel")
        loaded[name]=(source,baseline,entry,editor_recovery)
    outputs=[]
    for name,(contents,baseline,entry,editor_recovery) in loaded.items():
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
                count+=1  # incluir registros reconhecidos, desconhecidos e invalidos
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
                    regional=(professional_policy.regional_approved_decision(
                        comp,cat,direction,name) if professional else None)
                    adapted=bool(regional and regional.allowed)
                    decisions.append({
                        "acao":"MANTER_ADAPTACAO_REGIONAL" if adapted else "MANTER",
                        "empresa":company,"direcao":direction,
                        "carga":cargo,"arquivo":path,"setor":comp.role,
                        "fonte":"SIMULACAO_ECONOMICA_REGIONAL_AUTORIZADA"
                                if adapted else "POLITICA_ECONOMICA",
                        "confianca":"media" if adapted else
                                     "alta" if explicit_confidence(comp) else "media",
                        "motivo":reason})
                    states[company][direction].add(cargo)
                else:
                    prohibition=(proven_incompatibility(
                        comp,cat,direction,extras.get(cargo),map_name=name)
                        if (explicit_confidence(comp) or
                            (professional and
                             name in {"Minas_Gerais","Eldorado"} and
                             cat in {"algodao","coco"})) else None)
                    if prohibition:
                        changed[path]=disable_id(g,changed[path],cargo)
                        decisions.append({"acao":"REMOVER","empresa":company,
                            "direcao":direction,"carga":cargo,"arquivo":path,
                            "setor":comp.role,"confianca":"alta","motivo":prohibition})
                    else:
                        hypothesis=(professional_policy.legacy_plausible(
                            comp,cat,direction) if professional and
                            explicit_confidence(comp) and cargo not in extras
                            else None)
                        decisions.append({
                            "acao":("MANTER_PLAUSIVEL" if hypothesis else
                                    "REVISAR" if explicit_confidence(comp)
                                    else "PRESERVAR_SEM_EVIDENCIA"),
                            "empresa":company,"direcao":direction,"carga":cargo,
                            "arquivo":path,"setor":comp.role,
                            "confianca":"media" if explicit_confidence(comp) else "indeterminada",
                            "motivo":(hypothesis if hypothesis else
                                     "Atividade conhecida mas a mercadoria exige "
                                     "confirmacao documental antes de ser aprovada"
                                     if explicit_confidence(comp) else
                                     "Permissao herdada preservada sem alterar; "
                                     "empresa ainda nao classificada")})
                        states[company][direction].add(cargo)
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
                        regional=(professional_policy.regional_approved_decision(
                            comp,cat,direction,name) if professional else None)
                        adapted=bool(regional and regional.allowed)
                        decisions.append({
                            "acao":"ADICIONAR_ADAPTACAO_REGIONAL" if adapted
                                   else "ADICIONAR",
                            "empresa":company,"direcao":direction,"carga":cargo,
                            "arquivo":new_path,"setor":comp.role,
                            "confianca":"media" if adapted else "alta",
                            "fonte":"SIMULACAO_ECONOMICA_REGIONAL_AUTORIZADA"
                                    if adapted else "POLITICA_ECONOMICA",
                            "motivo":(why if adapted else
                                      "Empresa compativel validada pela DEF: "+why)})
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
        homologation=(homologacao_logistica.assess(
            baseline,final_active,manifest,extras,professional_policy,
            catalogo_cargas,map_name=name)
            if professional else None)
        def territory_decision(c,cat,direction,cargo):
            regional=professional_policy.regional_approved_decision(
                c,cat,direction,name)
            if regional is not None and regional.allowed:
                return regional
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
        # Arquivos NOVOS nao sao arquivos MODIFICADOS: separar indicadores.
        updated=sum(p in contents and contents[p]!=raw for p,raw in changed.items())
        added=sum(p not in contents for p in changed)
        # Nao transformar a ausencia de classificacao em centenas de alertas.
        # Preservar cada permissao herdada, com rastro individual, e produzir
        # uma fila de classificacao agrupada por empresa.
        manual=[d for d in decisions if d["acao"]=="REVISAR"]
        preserved=[d for d in decisions if d["acao"]=="PRESERVAR_SEM_EVIDENCIA"]
        plausible=[d for d in decisions if d["acao"]=="MANTER_PLAUSIVEL"]
        regional_additions=[
            d for d in decisions if d["acao"]=="ADICIONAR_ADAPTACAO_REGIONAL"
        ]
        regional_preserved=[
            d for d in decisions if d["acao"]=="MANTER_ADAPTACAO_REGIONAL"
        ]
        pending_by_company=defaultdict(list)
        for item in manual+preserved+plausible:
            pending_by_company[item["empresa"]].append(item)
        classification_pending={d["empresa"] for d in preserved}
        routes_without_pair=[
            cargo for cargo,row in after.items() if row["pares_distintos"]==0]
        # Impedir regressao silenciosa ao consolidar 3 mapas: nao entregar
        # arquivo novo que PERDEU uma cadeia originalmente completa.
        # O alerta e bloqueante: se a rota antiga era economicamente
        # falsa, o usuario deve buscar origem/destino comprovaveis,
        # e nao preservar o frete falso so para exibir 24/24.
        regressed_routes=sorted(
            cargo for cargo in before
            if before[cargo]["pares_distintos"]>0
            and after[cargo]["pares_distintos"]==0)
        originally_complete=bool(before) and all(
            row["pares_distintos"]>0 for row in before.values())
        if mode=="corrigir" and professional and originally_complete and regressed_routes:
            raise ValueError(
                name+": PROTECAO DE CADEIAS: a correcao eliminaria "
                "todos os pares de origem/destino das cargas "+
                ", ".join(regressed_routes)+". Nenhum SCS sera publicado. "
                "Confirme na DEF fornecedor e comprador validos; "
                "nao restaure automaticamente rotas incorretas.")
        additional_without_policy=sorted(
            (cid for cid,spec in extras.items()
             if spec.get("categoria") not in professional_policy.CATEGORIES),
            key=catalogo_cargas.sort_key)
        removals=[d for d in decisions if d["acao"] in ("REMOVER","REMOVER_DUPLICADO")]
        summary={"versao":"3.0.0" if professional else "2.5.0",
            "recuperacao_editor":editor_recovery,
            "economia_profissional":professional,
            "alteracoes_sao_simulacao":mode=="auditar",
            "nenhum_scs_gerado":mode=="auditar",
            "diagnostico_pendencias":{
                "total_decisoes_revisar":len(manual),
                "permissoes_herdadas_plausiveis_sem_prova_original":len(plausible),
                "novas_permissoes_adaptacao_regional":len(regional_additions),
                "permissoes_anteriores_adaptacao_regional":len(regional_preserved),
                "empresas_contempladas_por_adaptacao_regional":len({
                    d["empresa"] for d in regional_additions}),
                "criterio_adaptacao_regional":"Excecao autorizada pelo usuario "
                    "para pluma/coco apenas em Minas_Gerais e Eldorado; nao "
                    "afirma que IN/OUT original traz pluma/coco.",
                "empresas_com_hipoteses_plausiveis":len(
                    {d["empresa"] for d in plausible}),
                "permissoes_herdadas_preservadas_sem_evidencia":len(preserved),
                "empresas_com_classificacao_pendente":len(classification_pending),
                "empresas_com_revisoes_acionaveis":len({d["empresa"] for d in manual}),
                "empresas_com_revisoes":len(pending_by_company),
                "criterio":"MANTER_PLAUSIVEL sugere compatibilidade economica, "
                           "NAO prova original nem homologacao. "
                           "PRESERVAR_SEM_EVIDENCIA segue pendente.",
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
                     "situacao":("regra_definida_pendente_teste_ETS2"
                                if spec["categoria"] in professional_policy.CATEGORIES
                                else "regra_economica_pendente")}
                for cid,spec in extras.items()},
            "total_cargas_catalogo":len(manifest),
            "cargas_adicionais":{cid:{"sha256":spec["sha256"],"body_types":spec["body_types"]} for cid,spec in extras.items()},
            "validacao_carga_carroceria":trailer_record,
            "verificacao_modelos_carga_ets2_154":cargo_model_evidence,
            "qualidade_logistica":homologation,
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
            "permissoes_plausiveis_sem_evidencia_def":len(plausible),
            "permissoes_adaptacao_regional_adicionadas":len(regional_additions),
            "permissoes_adaptacao_regional_herdadas":len(regional_preserved),
            "mapa_autorizado_adaptacao_regional":name in {"Minas_Gerais","Eldorado"},
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
                      if manual or plausible or preserved or forgotten_companies or
                         routes_without_pair or additional_without_policy or
                         (territory and territory["empresas_sem_identificacao"])
                      else "AUDITORIA_ESTRUTURAL_CONCLUÍDA"),
            "aviso":("Arquivo tecnicamente auditado, NAO homologado para cliente "
                     "ou ETS2 enquanto restarem empresas sem classificacao, "
                     "permissoes sem evidencia e cargas sem rotas.")}
        # Auditoria dupla: par registrado nao e rota comprovada.
        if homologation:
            with (out/("CADEIAS_COMPROVADAS_"+name.upper()+".csv")).open(
                    "w",newline="",encoding="utf-8-sig") as fp:
                writer=csv.writer(fp,delimiter=";")
                writer.writerow(["carga","nome","status","pares_scs",
                    "pares_economicos","pares_com_editor","origens_confirmadas",
                    "destinos_confirmados","bloqueios","homologado_ets2"])
                for cid,row in sorted(homologation["cargas"].items(),
                       key=lambda kv:catalogo_cargas.sort_key(kv[0])):
                    writer.writerow([cid,row["nome"],row["status"],
                        row["total_pares_no_scs"],
                        row["pares_economicos_distintos"],
                        row["pares_com_editor_em_ambas_empresas"],
                        ",".join(row["origens_com_evidencia"]),
                        ",".join(row["destinos_com_evidencia"]),
                        " | ".join(row["bloqueios"]),"NAO"])
            with (out/("QUALIDADE_LOGISTICA_"+name.upper()+".json")).open(
                    "w",encoding="utf-8") as fp:
                json.dump(homologation,fp,ensure_ascii=False,indent=2)
        if professional and homologation:
            # Um mapa de cada vez: checklist independente do preflight de 3
            # mapas. Nao provar frete de jogo apenas por presença no SCS.
            checklist=out/("MATRIZ_ENSAIOS_ETS2_"+name.upper()+".csv")
            with checklist.open("w",newline="",encoding="utf-8-sig") as fp:
                fields=("mapa","carga","mercadoria","nivel_evidencia",
                        "status_documental","origem_sugerida","destino_sugerido",
                        "origem_real_testada","destino_real_testado",
                        "frete_visivel_no_ets2","modelo_da_carga_visivel",
                        "coleta_realizada","entrega_concluida",
                        "game_log_sem_erro_relevante","evidencia_arquivo",
                        "observacoes")
                writer=csv.DictWriter(fp,fieldnames=fields,delimiter=";")
                writer.writeheader()
                for cargo,record in sorted(
                        homologation["cargas"].items(),
                        key=lambda p:catalogo_cargas.sort_key(p[0])):
                    strong=record.get("candidatos_para_teste",[])
                    original=record.get("candidatos_documentados_para_teste",[])
                    regional=record.get("candidatos_simulacao_regional",[])
                    first=(strong or original or regional or [{}])[0]
                    writer.writerow({
                        "mapa":name,"carga":cargo,
                        "mercadoria":record["nome"],
                        "nivel_evidencia":(
                            "ATIVIDADE_ECONOMICA" if strong else
                            "SOMENTE_IN_OUT_ORIGINAL" if original else
                            "ADAPTACAO_REGIONAL_AUTORIZADA" if regional else
                            "ORIGEM_DESTINO_NAO_COMPROVADOS"),
                        "status_documental":record["status"],
                        "origem_sugerida":first.get("origem",""),
                        "destino_sugerido":first.get("destino","")
                    })
        # Dois niveis de diagnostico: aviso acionavel vs situacao herdada
        # somente informativa. O conjunto completo continua em AUDITORIA*.csv.
        with (out/("RESUMO_VALIDACAO_"+name.upper()+".txt")).open(
                "w",encoding="utf-8") as fp:
            fp.write("Mapa: "+name+"\n")
            fp.write("Revisoes pontuais: "+str(len(manual))+"\n")
            fp.write("Permissoes herdadas preservadas sem evidencia: "+
                     str(len(preserved))+"\n")
            fp.write("Adaptacoes regionais ADICIONADAS de pluma/coco: "+
                     str(len(regional_additions))+" (simulacao, sem comprovacao no IN/OUT)\n")
            fp.write("Adaptacoes regionais HERDADAS de pluma/coco: "+
                     str(len(regional_preserved))+"\n")
            fp.write("Empresas necessitando identificacao de atividade: "+
                     str(len(classification_pending))+"\n")
            if homologation:
                fp.write("Cargas com cadeia economicamente fundamentada: "+
                         str(homologation["cargas_com_par_economico_comprovavel"])+
                         "/"+str(len(manifest))+"\n")
                fp.write("Cargas candidatas a teste no ETS2 (ambos editor): "+
                         str(homologation["cargas_candidatas_teste_ets2"])+
                         "/"+str(len(manifest))+"\n")
                fp.write("Cargas comprovadamente homologadas no jogo: ZERO\n")
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
        if professional and territory is not None:
            map_coverage=cobertura_maxima_rbr.assess(
                baseline,territory,final_active,manifest,homologation)
            summary["cobertura_maxima_empresas"]={
                k:v for k,v in map_coverage.items() if k!="empresas"}
            cobertura_maxima_rbr.write(out,map_coverage,name)
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
            input_digest=g.hash_source(entry["existing"])[:8]
            # O nome final inclui tambem a identidade da SAIDA. Gerar a
            # partir da mesma Company com outra politica nao pode
            # sobrescrever uma versao anterior do usuario.
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
                    # Auditoria POS-EXPORTACAO: ler o ZIP de verdade,
                    # reconstruir permissao por empresa/direcao e conferir
                    # 100% com o estado que gerou os relatórios. Nunca
                    # divulgar 24/24 com arquivo diferente do inventario.
                    validated=defaultdict(lambda:{"in":set(),"out":set()})
                    occurrences=defaultdict(int)
                    for path in sorted(z.namelist()):
                        match=g.RE_COMPANY_PATH.search(path)
                        if (not match or match.group(2) not in {"in","out"}
                                or not path.endswith(SII_EXT)):
                            continue
                        company,direction=match.group(1).lower(),match.group(2).lower()
                        for cargo in file_active_ids(g,z.read(path)):
                            validated[company][direction].add(cargo)
                            occurrences[(company,direction,cargo)]+=1
                    for company in set(validated)|set(final_active):
                        for direction in ("in","out"):
                            if (validated[company][direction]!=
                                    final_active[company][direction]):
                                raise ValueError(
                                    "SCS e relatorio discordam em "+company+
                                    "/"+direction+"; publicacao bloqueada")
                    duplicates=[(company,direction,cargo)
                                for (company,direction,cargo),n in occurrences.items()
                                if n>1 and company in baseline]
                    if duplicates:
                        example=duplicates[0]
                        raise ValueError(
                            "SCS ainda contem cargo duplicado para empresa "
                            "da DEF: "+"/".join(example)+
                            " (total "+str(len(duplicates))+"); "
                            "nao sera publicado")
                    summary["validacao_pos_exportacao"]={
                        "arquivo_zip_integro":True,
                        "mesmas_permissoes_do_relatorio":True,
                        "duplicatas_em_empresas_do_mapa":0,
                        "permissoes_ativas":sum(occurrences.values()),
                        "homologado_no_ets2":False
                    }
                output_sha=digest(temporary.read_bytes())
                output=out/("ETS2_"+name.upper()+"_AUDITADA_V25_"+
                            input_digest+"_"+output_sha[:12]+".scs")
                if Path(entry["existing"]).resolve()==output.resolve():
                    raise ValueError("Nunca sobrescrever a Company original")
                if output.exists():
                    if digest(output.read_bytes())!=output_sha:
                        raise ValueError("Nome de SCS ja utilizado por outra "
                                         "versao; preservando arquivo existente: "+
                                         output.name)
                    # Idempotencia: output ja e EXATAMENTE o mesmo.
                    # Nao atualizar data de modificacao nem apagar backup.
                else:
                    os.replace(temporary,output)
            finally:
                if temporary.exists():temporary.unlink()
            summary["arquivo_corrigido"]=output.name
            summary["sha256_scs_corrigido"]=output_sha
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


def _write_three_map_dashboard(folder, reports, *, simulated=False):
    """Resumo auditavel para cada mapa sem misturar cobertura e homologacao."""
    if not reports:
        return
    items=[]
    for report in sorted(reports,key=lambda x:x["mapa"]):
        evidence=report.get("cobertura_maxima_empresas") or {}
        quality=report.get("qualidade_logistica") or {}
        cargo_info=quality.get("cargas") or {}
        total_cargas=int(report.get("total_cargas_catalogo",len(cargo_info)))
        missing_economic=sorted(
            cargo for cargo,v in cargo_info.items()
            if v.get("pares_economicos_distintos",0)==0)
        missing_documented=sorted(
            cargo for cargo,v in cargo_info.items()
            if v.get("pares_com_evidencia_inout_distintos",0)==0)
        missing_editors=sorted(
            cargo for cargo,v in cargo_info.items()
            if v.get("pares_com_editor_em_ambas_empresas",0)==0)
        blockers=[]
        if evidence.get("empresas_sem_classificacao",0):
            blockers.append("Empresas com atividade ainda desconhecida")
        if evidence.get("empresas_compativeis_sem_editor_valido",0):
            blockers.append("Empresas compativeis sem company_def cidade+prefab")
        if report.get("pendencias_revisao",0):
            blockers.append("Decisoes economicas exigem revisao")
        if report.get("permissoes_plausiveis_sem_evidencia_def",0):
            blockers.append("Cargas herdadas plausiveis sem prova do produto na DEF")
        if missing_economic:
            blockers.append("Cargas sem par economicamente justificado")
        if missing_editors:
            blockers.append("Cargas sem par com editor documentado")
        items.append({
            "mapa":report["mapa"],
            "total_cargas_catalogo":total_cargas,
            "empresas_na_def":report.get("empresas_na_def"),
            "empresas_nao_classificadas":evidence.get("empresas_sem_classificacao"),
            "empresas_com_editor_ausente":evidence.get("empresas_sem_editor"),
            "cidades_documentadas":evidence.get("cidades_identificadas"),
            "permissoes_justificadas":evidence.get("permissoes_justificadas"),
            "permissoes_justificadas_atendidas":
                evidence.get("permissoes_justificadas_atendidas"),
            "pct_permissoes_justificadas":
                evidence.get("cobertura_permissoes_justificadas_pct"),
            "cargas_com_par_cadastrado":quality.get("cargas_com_par_cadastrado",0),
            "cargas_com_par_documental":
                quality.get("cargas_com_par_evidencia_inout",0),
            "cargas_com_par_economico":
                quality.get("cargas_com_par_economico_comprovavel",0),
            "cargas_com_par_adaptacao_regional":
                quality.get("cargas_com_par_simulacao_regional",0),
            "cargas_candidatas_adaptacao_regional":
                quality.get("cargas_candidatas_simulacao_regional_teste",0),
            "adaptacoes_regionais_novas":
                report.get("permissoes_adaptacao_regional_adicionadas",0),
            "adaptacoes_regionais_preservadas":
                report.get("permissoes_adaptacao_regional_herdadas",0),
            "cargas_com_par_editor_documental":
                quality.get("cargas_candidatas_documentais_teste",0),
            "cargas_candidatas_no_editor":
                quality.get("cargas_candidatas_teste_ets2",0),
            "cargas_sem_par_documental":missing_documented,
            "cargas_sem_par_economico":missing_economic,
            "cargas_sem_par_editor":missing_editors,
            "pendencias_revisao":report.get("pendencias_revisao",0),
            "permissoes_legadas_plausiveis":
                report.get("permissoes_plausiveis_sem_evidencia_def",0),
            "bloqueios":blockers,
            "hash_company_original":report.get("sha256_entrada",""),
            "hash_def_original":report.get("sha256_def",""),
            "status":"ANALISE_PENDENTE" if blockers else
                     "DOCUMENTOS_CONSISTENTES_TESTE_NO_JOGO_PENDENTE",
            "homologado_no_ets2":False
        })
    dashboard={
        "versao":"3.0-painel",
        "mapas_analisados":len(items),
        "simulacao_sem_escrita_scs":simulated,
        "status":"HOMOLOGACAO_ETS2_PENDENTE",
        "homologado_no_ets2":False,
        "criterio":"Percentual de permissoes justificadas mede apenas o que "
                   "os IN/OUT e regras de setor demonstram. Sem exigir "
                   "cidades/prefabs jogaveis, fretes visiveis e entregas "
                   "no ETS2, jamais e homologacao de 100%.",
        "mapas":items
    }
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"PAINEL_GERAL_LOGISTICA_V3.json").write_text(
        json.dumps(dashboard,indent=2,ensure_ascii=False),encoding="utf-8")
    lines=["PAINEL GERAL DE LOGISTICA V3 - NAO E HOMOLOGACAO ETS2",
           "Analise: SIMULACAO" if simulated else "Analise: COMPANY CORRIGIDA"]
    for item in items:
        lines+=["", "MAPA "+item["mapa"],
                "Empresas da DEF: "+str(item["empresas_na_def"]),
                "Cobertura de permissoes justificadas: "+
                str(item["pct_permissoes_justificadas"])+"% ("+
                str(item["permissoes_justificadas_atendidas"])+"/"+
                str(item["permissoes_justificadas"])+")",
                "Pares IN/OUT documentados: "+
                str(item["cargas_com_par_documental"])+"/"+
                str(item["total_cargas_catalogo"])+" cargas",
                "Pares com setor conhecido: "+
                str(item["cargas_com_par_economico"])+"/"+
                str(item["total_cargas_catalogo"])+" cargas",
                "Pares por ADAPTACAO REGIONAL (nao comprovados no IN/OUT): "+
                str(item["cargas_com_par_adaptacao_regional"])+"/"+
                str(item["total_cargas_catalogo"])+" cargas",
                "Novas permissoes regionais: "+
                str(item["adaptacoes_regionais_novas"]),
                "Pares com editor: "+
                str(item["cargas_candidatas_no_editor"])+"/"+
                str(item["total_cargas_catalogo"])+" cargas",
                "Empresas nao classificadas: "+
                str(item["empresas_nao_classificadas"]),
                "Legadas economicamente plausiveis, nao documentadas: "+
                str(item["permissoes_legadas_plausiveis"]),
                "Bloqueios: "+"; ".join(item["bloqueios"] or
                                        ["Testes reais no jogo pendentes"])]
    (folder/"PAINEL_GERAL_LOGISTICA_V3.txt").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")
    return dashboard


def _three_map_pending_queue(folder, reports):
    """Fila de DECISOES dos 3 mapas, contextualizada pelos IN/OUT verdadeiros.

    Nao transforma nomes desconhecidos em produtor, nao inventa cargas e
    nao mistura permissao 'possivel' com comprovacao da DEF original.
    Publicada so depois de analisar os tres mapas na mesma execucao.
    """
    expected={"Minas_Gerais","Eldorado","RBR"}
    if {r.get("mapa") for r in reports}!=expected:
        return None
    categories={
        "REVISAR":(1,"Exigir documento original que confirme carga/direcao"),
        "PRESERVAR_SEM_EVIDENCIA":(
            2,"Identificar atividade pelos fluxos, nao aprovar ainda"),
        "MANTER_PLAUSIVEL":(
            3,"Conferir produto e direcao na DEF; plausibilidade nao e prova")
    }
    headers=[
        "prioridade","mapa","empresa","nome_exibido","setor_inferido",
        "acao","carga","direcao","arquivo_scs",
        "in_originais_def","out_originais_def","instancias_editor",
        "motivo","acao_recomendada","homologado_ets2"
    ]
    queue=[]
    overview={}
    for report in sorted(reports,key=lambda x:x["mapa"]):
        map_name=report["mapa"]
        territory=(report.get("matriz_empresa_cidade") or {})
        company_evidence={
            x.get("empresa"):x for x in territory.get("empresas",[])
        }
        unresolved=set()
        for d in report.get("decisoes",[]):
            action=d.get("acao")
            if action not in categories:
                continue
            urgency,advice=categories[action]
            comp=d.get("empresa","")
            ev=company_evidence.get(comp,{})
            def as_text(value):
                if isinstance(value,(list,tuple,set)):
                    return ",".join(sorted(str(x) for x in value))
                return str(value or "")
            queue.append({
                "prioridade":urgency,"mapa":map_name,"empresa":comp,
                "nome_exibido":ev.get("nome_exibido",""),
                "setor_inferido":d.get("setor") or ev.get("atividade",""),
                "acao":action,"carga":d.get("carga",""),
                "direcao":d.get("direcao",""),
                "arquivo_scs":d.get("arquivo",""),
                "in_originais_def":as_text(ev.get("in_originais_def")),
                "out_originais_def":as_text(ev.get("out_originais_def")),
                "instancias_editor":ev.get("instancias_editor",0),
                "motivo":d.get("motivo",""),"acao_recomendada":advice,
                "homologado_ets2":"NAO"
            })
            unresolved.add(comp)
        # Empresa desconhecida SEM permissao pendente nao equivale a
        # carga errada. Manter listada como baixa prioridade, nunca erro.
        unknown=0
        for company,ev in company_evidence.items():
            if not company or ev.get("atividade")!="desconhecida":
                continue
            unknown+=1
            if company in unresolved:
                continue
            queue.append({
                "prioridade":4,"mapa":map_name,"empresa":company,
                "nome_exibido":ev.get("nome_exibido",""),
                "setor_inferido":"desconhecida",
                "acao":"SEM_FRETE_PENDENTE_IDENTIFICADO",
                "carga":"","direcao":"","arquivo_scs":"",
                "in_originais_def":as_text(ev.get("in_originais_def")),
                "out_originais_def":as_text(ev.get("out_originais_def")),
                "instancias_editor":ev.get("instancias_editor",0),
                "motivo":"Empresa sem classe segura mas sem cargo antigo "
                         "pendente nesta auditoria",
                "acao_recomendada":"Revisar setor apenas se houver demanda "
                                   "de frete compatível com as 24 mercadorias",
                "homologado_ets2":"NAO"
            })
        quality=report.get("qualidade_logistica") or {}
        overview[map_name]={
            "total_cargas":report.get("total_cargas_catalogo"),
            "cargas_com_par_cadastrado":quality.get("cargas_com_par_cadastrado",0),
            "pares_economicos":quality.get("cargas_com_par_economico_comprovavel",0),
            "candidatas_teste_ets2":quality.get("cargas_candidatas_teste_ets2",0),
            "revisoes_pontuais":report.get("pendencias_revisao",0),
            "herdadas_sem_prova":report.get(
                "permissoes_sem_evidencia_preservadas",0),
            "herdadas_plausiveis_sem_prova":report.get(
                "permissoes_plausiveis_sem_evidencia_def",0),
            "empresas_sem_classe":unknown,
            "empresas_com_revisao_relevante":len(unresolved),
            "cargas_sem_par":report.get("cargas_sem_rota_validada",[]),
            "adaptacoes_regionais_novas":report.get(
                "permissoes_adaptacao_regional_adicionadas",0)
        }
    queue.sort(key=lambda d:(d["prioridade"],d["mapa"],d["empresa"],
                             d["carga"],d["direcao"]))
    with (folder/"TRIAGEM_PENDENCIAS_3_MAPAS.csv").open(
            "w",newline="",encoding="utf-8-sig") as stream:
        writer=csv.DictWriter(stream,fieldnames=headers,delimiter=";")
        writer.writeheader()
        writer.writerows(queue)
    summary={
        "mapas":overview,"decisoes_na_fila":len(queue),
        "prioridade_1_revisao":sum(r["prioridade"]==1 for r in queue),
        "prioridade_2_legada_sem_prova":sum(r["prioridade"]==2 for r in queue),
        "prioridade_3_hipotese":sum(r["prioridade"]==3 for r in queue),
        "prioridade_4_sem_frete":sum(r["prioridade"]==4 for r in queue),
        "status":"PENDENTE_ENSAIOS_NO_ETS2",
        "homologado_no_ets2":False,
        "criterio":"Fila de evidencias; nenhuma mercadoria nova e "
                   "aprovada apenas por nome de empresa, origem/destino "
                   "ou quantidade de instancias editor."
    }
    (folder/"TRIAGEM_PENDENCIAS_3_MAPAS.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2),
        encoding="utf-8")
    return summary


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
        if professional:
            _write_three_map_dashboard(stage,result,simulated=mode=="auditar")
            _three_map_pending_queue(stage,result)
        # Publicacao em lote com rollback: se um relatorio/Company falhar
        # na etapa final, restaurar exatamente os arquivos que existiam
        # antes da execucao. O staging no proprio volume garante replace
        # local sem copiar modelos de centenas de MB desnecessariamente.
        undo=stage/"_ROLLBACK_PREEXISTENTES"
        undo.mkdir()
        shipped=[]
        replaced=[]
        try:
            # NUNCA substituir .scs anterior: os nomes incluem hash do
            # proprio conteudo. Se alguem alterou um arquivo com o mesmo
            # nome, o conflito e fatal, nao um overwrite silencioso.
            # Prevalidar antes de mover um unico relatorio da execucao.
            for item in sorted(stage.iterdir()):
                if not item.is_file() or item.suffix.lower()!=".scs":
                    continue
                dest=published/item.name
                if dest.exists():
                    if not dest.is_file():
                        raise ValueError(
                            "Saida SCS ocupada por pasta: "+dest.name)
                    if digest(item.read_bytes())!=digest(dest.read_bytes()):
                        raise ValueError(
                            "Arquivo SCS existente com mesmo nome e bytes "
                            "diferentes; recusa sobrescrever versao anterior: "+
                            dest.name)
            for item in sorted(stage.iterdir()):
                if not item.is_file():
                    continue
                dest=published/item.name
                if dest.exists():
                    if not dest.is_file():
                        raise ValueError("Destino ocupado por pasta: "+dest.name)
                    if item.suffix.lower()==".scs":
                        # Mesmo SHA -> ja publicado: preservar o arquivo e
                        # o mtime para evitar confusao com o mod em uso.
                        continue
                    previous=undo/item.name
                    os.replace(dest,previous)
                    replaced.append((dest,previous))
                os.replace(item,dest)
                shipped.append(dest)
        except Exception as exc:
            problems=[]
            for dest in reversed(shipped):
                try:
                    if dest.exists():
                        dest.unlink()
                except OSError as failure:
                    problems.append("Nao removeu "+dest.name+": "+str(failure))
            for dest,previous in reversed(replaced):
                try:
                    if previous.exists():
                        os.replace(previous,dest)
                except OSError as failure:
                    problems.append("Nao restaurou "+dest.name+": "+str(failure))
            (published/"AUDITORIA_INCOMPLETA.txt").write_text(
                "Publicacao de tres mapas interrompida. Foi tentada a "
                "restauracao integral dos arquivos que existiam antes.\n"+
                type(exc).__name__+": "+str(exc)+"\n"+
                ("Falhas no rollback: "+"; ".join(problems)+"\n"
                 if problems else "Rollback efetuado sem erro registrado.\n"),
                encoding="utf-8")
            raise
        # Remover marcador obsoleto so depois da publicacao completa.
        marker=published/"AUDITORIA_INCOMPLETA.txt"
        if marker.is_file():
            marker.unlink()
        log("Auditoria de "+str(len(result))+
            " mapa(s) finalizada e publicada em conjunto.")
        return result
