"""Recuperar evidencias de cidade/prefab REAIS sem criar editor ficticio.

Fontes, por prioridade: DEF do mapa ja carregada > Company de entrada >
pacote adicional de editor do proprio mapa. Nao transfere cidades de outro
mapa, nao cria company_def e nao diz que prefab existe/funciona no ETS2.
"""
from __future__ import annotations

import re
from collections import Counter

EDITOR_PATH=re.compile(
    r"^def/company/([a-z0-9_]+)/editor/([a-z0-9_.-]+)\.(?:sii|sui)$",
    re.I,
)
TOKEN=r'["\']?(?:[a-z_]+\.)?([a-z0-9_]+)["\']?'
CITY=re.compile(r'(?im)^\s*city\s*:\s*'+TOKEN+r'\s*(?:#.*)?$')
PREFAB=re.compile(r'(?im)^\s*prefab\s*:\s*'+TOKEN+r'\s*(?:#.*)?$')
COMPANY_DEF=re.compile(r'\bcompany_def\s*:',re.I)


def recover(g, companies, existing_files, optional_archive=None):
    """Acrescenta apenas instancias editor documentalmente existentes.

    * Nunca usa nome de cidade extraido do nome de empresa.
    * Exige arquivo company_def contendo city e prefab (nao apenas filename).
    * Rejeita empresa desconhecida e caminhos duplicados discordantes.
    * Quando o arquivo def/company/*/editor ja existe, preserva-o.
    * Nao acrescenta nada aos SCS de saida: apenas evidencia aos relatorios.
    """
    status={
        "editor_ja_presente_na_def":sum(len(c.editor_files) for c in companies.values()),
        "editor_recuperado_company_existente":0,
        "editor_recuperado_fonte_adicional":0,
        "editor_rejeitado_sem_city_prefab":0,
        "editor_rejeitado_empresa_ausente":0,
        "editor_conflito_entre_fontes":0,
        "fontes":["DEF original do mapa"],
        "aviso":"Cidade e prefab provem de company_def original; nenhum "
                "prefab foi testado no jogo nem inventado."
    }
    def collect(source,label):
        if not source:return
        status["fontes"].append(label)
        for path,raw in sorted(source.items()):
            m=EDITOR_PATH.fullmatch(path.lower().replace("\\","/"))
            if not m:continue
            company_id=m.group(1).lower()
            company=companies.get(company_id)
            if company is None:
                status["editor_rejeitado_empresa_ausente"]+=1
                continue
            data=g.read_sii(raw)
            c=CITY.search(data)
            p=PREFAB.search(data)
            if not c or not p or not COMPANY_DEF.search(data):
                status["editor_rejeitado_sem_city_prefab"]+=1
                continue
            existing=company.editor_files.get(path)
            if existing is not None:
                if existing!=raw:
                    status["editor_conflito_entre_fontes"]+=1
                continue
            # A mesma empresa, cidade e prefab podem existir em mais de
            # um ZIP com nomes de arquivo diferentes. Nao duplicar.
            def pair(txt):
                cm=CITY.search(txt);pm=PREFAB.search(txt)
                return (cm.group(1),pm.group(1)) if cm and pm else None
            signature=(c.group(1),p.group(1))
            if any(pair(g.read_sii(other))==signature
                   for other in company.editor_files.values()):
                continue
            company.editor_files[path]=raw
            key=("editor_recuperado_company_existente" if
                 label=="Company existente" else
                 "editor_recuperado_fonte_adicional")
            status[key]+=1
    collect(existing_files,"Company existente")
    if optional_archive:
        files=g.zip_members(optional_archive,wanted=lambda path:
                            bool(EDITOR_PATH.fullmatch(path)))
        collect(files,"Pacote editor do mapa fornecido: "+str(optional_archive))
    status["total_editor_depois"]=sum(len(c.editor_files) for c in companies.values())
    status["empresas_com_editor"]=sum(bool(c.editor_files) for c in companies.values())
    status["sem_editor"]=not bool(status["total_editor_depois"])
    if status["sem_editor"]:
        status["motivo"]="Nem a DEF, nem a Company, nem o pacote adicional " \
                        "possuem pares reais company_def: city + prefab"
    return status
