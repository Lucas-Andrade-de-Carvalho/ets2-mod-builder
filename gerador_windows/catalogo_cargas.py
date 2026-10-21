#!/usr/bin/env python3
"""Catalogo adicional de cargas ETS2. Offline, sem modificar os 23 registros originais.

Um registro so e utilizavel se possuir uma definicao cargo_data original legivel,
body_types reais e uma politica economica explicita. Campos nao comprovados
permanecem pendentes. O conteudo de .sii/.sui e preservado byte a byte.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

SCHEMA = 1
ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
UNIT_RE = re.compile(r"\bcargo_data\s*:\s*cargo\.([a-z][a-z0-9_]*)\s*\{", re.I)
BODY_RE = re.compile(r'(?im)^\s*body_types(?:\[\d*\])?\s*:\s*["' + "'" + r']?([a-z0-9_]+)')
VALID_EVIDENCE = {"setor", "documental"}
MAX_BYTES = 512_000


def default_path():
    base = Path(os.environ.get("APPDATA", str(Path.home())))
    return base / "ETS2_Company_Logistics" / "catalogo_cargas_v3.json"


def cargo_id(key):
    return "carga" + str(key) if isinstance(key, int) else str(key)


def sort_key(key):
    cid = cargo_id(key)
    match = re.fullmatch(r"carga(\d+)", cid)
    return (0, int(match.group(1))) if match else (1, cid)


def parse_sii(source: bytes, cargo: str):
    if len(source) > MAX_BYTES:
        raise ValueError("Definicao excede 512 KB; revisar dependencias manualmente")
    try:
        txt = source.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Definicao SII/SUI nao e UTF-8; importar arquivo texto original") from exc
    if not re.search(r"(?im)^\s*SiiNunit\s*$", txt):
        raise ValueError("Arquivo deve ser definicao SiiNunit completa (fragmento .sui isolado nao basta)")
    units = [x.lower() for x in UNIT_RE.findall(txt)]
    if len(units) != 1 or units[0] != cargo:
        raise ValueError("cargo_data deve declarar exatamente cargo." + cargo)
    if re.search(r"(?im)^\s*@include\b", txt):
        raise ValueError("Definicao depende de @include; importe versao independente antes de gerar")
    if txt.count("{") != txt.count("}"):
        raise ValueError("Delimitadores de unidades SII inconsistentes")
    body = sorted(set(x.lower() for x in BODY_RE.findall(txt)))
    if not body:
        raise ValueError("body_types nao encontrado na definicao original; sem carroceria comprovada")
    return body


def _tokens(value):
    if isinstance(value, str):
        value = re.split(r"[,;\n]", value)
    if not isinstance(value, list):
        raise ValueError("Campos de setores/aliases devem ser listas")
    return sorted(set(str(x).strip().lower() for x in value if str(x).strip()))


def validate(item, reserved=()):
    if not isinstance(item, dict):
        raise ValueError("Registro de carga invalido")
    spec = dict(item)
    cid = str(spec.get("id", "")).lower().strip()
    if not ID_RE.fullmatch(cid):
        raise ValueError("ID deve ter 2-64 caracteres [a-z0-9_]")
    if cid in reserved:
        raise ValueError("ID colide com cargo original: " + cid)
    spec["id"] = cid
    spec["nome"] = str(spec.get("nome", "")).strip()
    spec["descricao"] = str(spec.get("descricao", "")).strip()
    spec["categoria"] = str(spec.get("categoria", "")).lower().strip()
    spec["subcategoria"] = str(spec.get("subcategoria", "")).strip()
    if not spec["nome"] or not ID_RE.fullmatch(spec["categoria"]):
        raise ValueError("Nome e categoria economica sao obrigatorios")
    for key in ("aliases", "out_roles", "in_roles", "forbidden_roles",
                "out_companies", "in_companies"):
        spec[key] = _tokens(spec.get(key, []))
    for key in ("out_evidence", "in_evidence"):
        spec[key] = str(spec.get(key, "setor")).lower()
        if spec[key] not in VALID_EVIDENCE:
            raise ValueError(key + ": use setor ou documental")
    # Nenhuma rota e presumida sem declarar fornecedor E consumidor.
    if not spec["out_roles"] and not spec["out_companies"]:
        raise ValueError("Configure pelo menos um setor ou empresa fornecedora (OUT)")
    if not spec["in_roles"] and not spec["in_companies"]:
        raise ValueError("Configure pelo menos um setor ou empresa compradora (IN)")
    source = spec.get("sii_base64")
    if not isinstance(source, str) or not source:
        raise ValueError("Importe a definicao SII original antes de ativar a carga")
    try:
        blob = base64.b64decode(source, validate=True)
    except (ValueError, Exception) as exc:
        raise ValueError("Arquivo SII embutido nao e base64 valido") from exc
    sha = hashlib.sha256(blob).hexdigest()
    if spec.get("sha256") and spec["sha256"] != sha:
        raise ValueError("SHA-256 da definicao SII nao confere: " + cid)
    spec["sha256"] = sha
    spec["body_types"] = parse_sii(blob, cid)
    spec["cargo_path"] = "def/cargo/" + cid + ".sii"
    return spec


def import_definition(path, cargo):
    p = Path(path)
    if p.suffix.lower() not in (".sii", ".sui"):
        raise ValueError("Selecione arquivo .sii ou .sui")
    original = p.read_bytes()
    raw = original
    # Arquivos SUI de cargo_data frequentemente sao fragmentos incluidos por
    # master SII. Envolver a unidade completa permite gerar arquivo autonomo.
    # Nao transformar imports/dependencias ocultas.
    if p.suffix.lower() == ".sui" and not re.search(
            rb"(?im)^s*SiiNunits*$", original):
        raw = b"SiiNunit\n{\n" + original + b"\n}\n"
    bodies = parse_sii(raw, cargo)
    return {"sii_base64": base64.b64encode(raw).decode("ascii"),
            "sha256": hashlib.sha256(raw).hexdigest(), "body_types": bodies,
            "sha256_origem": hashlib.sha256(original).hexdigest(),
            "arquivo_origem": p.name,
            "convertido_de_sui": original != raw}


def load(path=None, reserved=()):
    path = Path(path) if path is not None else default_path()
    if not path.exists():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA or not isinstance(doc.get("cargas"), list):
        raise ValueError("Catalogo JSON sem schema suportado; nao gerar SCS")
    result = {}
    for raw in doc["cargas"]:
        spec = validate(raw, reserved)
        if spec["id"] in result:
            raise ValueError("IDs de cargas duplicados no catalogo: " + spec["id"])
        result[spec["id"]] = spec
    return result


def save(catalog, path=None, reserved=()):
    path = Path(path) if path is not None else default_path()
    checked = {}
    for key, raw in catalog.items():
        spec = validate(raw, reserved)
        if key != spec["id"] or key in checked:
            raise ValueError("Colisao de IDs durante gravacao: " + str(key))
        checked[key] = spec
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps({"schema": SCHEMA, "cargas": list(checked.values())},
                      ensure_ascii=False, indent=2)
    handle = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=".catalogo_",
                                         suffix=".tmp", encoding="utf-8",
                                         delete=False) as fp:
            handle = Path(fp.name)
            fp.write(data)
        os.replace(handle, path)
    finally:
        if handle is not None and handle.exists():
            handle.unlink()


def decode_definition(spec):
    blob = base64.b64decode(spec["sii_base64"], validate=True)
    if hashlib.sha256(blob).hexdigest() != spec["sha256"]:
        raise ValueError("Definicao original alterada no catalogo")
    return blob


def manifest(base_manifest, extras):
    result = dict(base_manifest)
    for cid, spec in extras.items():
        if cid in (cargo_id(k) for k in result):
            raise ValueError("Colisao com carga do manifesto: " + cid)
        result[cid] = (spec["categoria"], spec["nome"])
    return result


def evaluate(company, spec, direction, identity):
    """Politica dinamica separada; nenhuma autorizacao por similaridade vaga."""
    from politica_economica import Decision, norm
    if direction not in ("in", "out"):
        return Decision(False, "direcao desconhecida", "nenhuma", "alta")
    role = identity.role
    if role == "transportadora" or role in spec["forbidden_roles"]:
        return Decision(False, "ramo proibido para esta mercadoria", identity.evidence, "alta")
    explicit = norm(company.name) in spec[direction + "_companies"]
    by_role = role in spec[direction + "_roles"] and identity.certainty == "alta"
    if not (explicit or by_role):
        return Decision(False, "atividade/empresa nao autorizada no cadastro desta carga",
                        identity.evidence, identity.certainty)
    required = spec[direction + "_evidence"]
    tokens = {norm(t) for t in (company.old_out if direction == "out" else company.old_in)}
    known = {norm(spec["id"])} | {norm(t) for t in spec["aliases"]}
    # Um atacadista generico precisa demonstrar movimentacao especifica;
    # "distribuidor" por nome nunca vira fornecedor universal.
    if direction == "out" and role in {"distribuidor", "atacadista"} and not explicit:
        required = "documental"
    if required == "documental" and not (tokens & known):
        return Decision(False, "falta IN/OUT documental especifico da mercadoria",
                        "cadastro exige evidencia na DEF do mapa", "alta")
    if explicit and not spec["descricao"]:
        return Decision(False, "empresa cadastrada sem justificativa descritiva",
                        "configuracao incompleta", "alta")
    return Decision(True,
                    ("fornecedor" if direction == "out" else "comprador") +
                    " economicamente autorizado para " + spec["nome"],
                    ("empresa explicitamente cadastrada" if explicit else
                     "classificacao do setor do mapa") + "; regra " + required, "alta")
