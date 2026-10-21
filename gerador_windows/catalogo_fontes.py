"""Catalogo SOMENTE LEITURA, extraido do MOD/DEF1/DEF2 e TXT fornecidos.

Nao permite cadastrar, editar, remover ou importar carga pela interface.
As novas mercadorias precisam existir nos arquivos reais do reboque.
Sua politica economica nao pode ser adivinhada a partir de um nome.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

CARGO_NUMBER = re.compile(r"^carga([1-9][0-9]*)$")
TXT_LINE = re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:carga)\s*([1-9][0-9]*)\s*[:=\-\u2013]\s*(.+?)\s*$")

def cargo_id(key):
    return "carga" + str(key) if isinstance(key, int) else str(key)

def sort_key(key):
    cid = cargo_id(key)
    m = CARGO_NUMBER.fullmatch(cid)
    return (0, int(m.group(1))) if m else (1, cid)

def txt_inventory(path=None):
    """Ler descricao declarada no TXT. Sem interpretar texto como permissoes."""
    if not path:
        return {}
    raw = Path(path).read_text(encoding="utf-8-sig")
    result = {}
    for number, title in TXT_LINE.findall(raw):
        cid = "carga" + str(int(number))
        title = title.strip().strip(" -:;")
        if not title:
            continue
        if cid in result and result[cid] != title:
            raise ValueError("TXT possui nomes conflitantes para " + cid)
        result[cid] = title
    return result

def known_economic_category(title):
    """Correspondencias EXATAS para novas mercadorias sem cadastro manual.

    Outros nomes permanecem pendentes; nunca deduzir que oleo de coco,
    leite de coco ou derivados sejam o fruto in natura.
    """
    label = re.sub(r"\s+", " ", str(title).strip().lower())
    if re.fullmatch(r"coco(?: (?:verde|seco|fresco|in natura))?", label):
        return "coco"
    return "nao_classificada"


def from_originals(base_manifest, cargo_records, txt_path=None, *, require_txt_for_new=True):
    """Retorna manifesto + novas mercadorias fisicamente comprovadas em cargo_data.

    IDs de outros reboques (corn_b etc.) nao sao adicionados ao Librelato.
    A politica de novas cargas fica pendente ate analise economica fundamentada.
    """
    text_labels = txt_inventory(txt_path)
    base_ids = {cargo_id(k) for k in base_manifest}
    source_ids = {cid for cid in cargo_records if CARGO_NUMBER.fullmatch(cid)}
    for cid in sorted(base_ids, key=sort_key):
        if cid not in source_ids:
            raise ValueError(cid + ": cargo_data original nao encontrado no reboque")
    new_ids = sorted(source_ids - base_ids, key=sort_key)
    if new_ids and require_txt_for_new:
        missing=[cid for cid in new_ids if cid not in text_labels]
        if missing:
            raise ValueError("Nova(s) mercadoria(s) presente(s) nos SCS sem descricao no TXT: "+
                             ", ".join(missing)+". Atualize e informe o TXT original.")
    phantom = set(text_labels)-source_ids
    if phantom:
        raise ValueError("TXT descreve carga(s) sem cargo_data comprovado nos 3 SCS: "+
                         ", ".join(sorted(phantom,key=sort_key)))
    manifest = dict(base_manifest)
    extras = {}
    for cid in new_ids:
        record = cargo_records[cid]
        spec={
            "id":cid,
            "nome":text_labels.get(cid, cid+" (descricao pendente)"),
            "categoria":known_economic_category(text_labels.get(cid, "")),
            "body_types":sorted(record["body"]),
            "sha256":hashlib.sha256(record["raw"]).hexdigest(),
            "source":record["source"],
            "source_path":record["path"],
        }
        extras[cid]=spec
        manifest[cid]=(spec["categoria"],spec["nome"])
    return manifest, extras

def evaluate(company, spec, direction, identity):
    """Usar politica economica verificada; nenhuma rota para tipo sem regra."""
    from politica_economica import Decision, CATEGORIES, decide
    if spec["categoria"] in CATEGORIES:
        return decide(company, spec["categoria"], direction, identity)
    return Decision(
        False,
        "Carga "+spec["id"]+" identificada no mod, mas sem regra economica "
        "validada para associar a empresas",
        "TXT: "+spec["nome"]+"; body_types: "+", ".join(spec["body_types"]),
        "indeterminada")
