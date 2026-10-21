#!/usr/bin/env python3
# ETS2 Company Logistics - gerador offline para Windows
# Apenas biblioteca padrao Python; conversao para EXE via GitHub Actions.
from __future__ import annotations
import argparse
import csv
import io
import os
import shutil
import tempfile
import collections
import hashlib
import threading
import queue
import json
import re
import sys
import traceback
import unicodedata
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

VERSION = '2.5.0'

MANIFEST = {
 1:("milho","Milho"),2:("soja","Soja"),3:("adubo","Adubo"),
 4:("madeira","Madeira"),5:("algodao","Pluma de algodao"),
 6:("cimento","Cimento"),7:("batata","Sacos de batata"),
 8:("laranja","Sacos de laranja"),9:("bobina","Bobinas"),
 10:("cimento","Cimento paletizado"),11:("cimento","Cimento em cinta"),
 12:("cerveja","Cerveja"),13:("tijolo","Tijolos"),
 14:("granito","Granito 1"),15:("granito","Granito 2"),
 16:("palete","Palete Alto"),17:("racao","Racao mineral"),
 18:("racao","Xerem / racao"),19:("racao","Sacaria de racao"),
 20:("racao","Sacaria de racao 2"),21:("soja","Soja alta"),
 22:("milho","Milho alto"),23:("sorgo","Sorgo / alimentacao animal")
}
PATTERNS = {
 "milho":r"(?:^|_)(?:rbr_|ros_|cs_)?(?:milho|corn|maize)(?:_[ab])?$",
 "soja":r"(?:^|_)(?:rbr_|ros_|cs_)?(?:soja|soybean)(?:_[ab])?$",
 "adubo":r"adubo|fertiliz|npk|nitrato|ureia|urea",
 "madeira":r"madeir|tronco|toras?|logs?|timber|lumber|mdf|serrag",
 "algodao":r"algodao|pluma|cotton",
 "cimento":r"cimento|cement",
 "batata":r"batata|potato",
 "laranja":r"laranja|orange|citrus",
 "bobina":r"bobinas?|bobin[a-z_]*|steel_coils?|steelcoil|steel_roll|coil_steel|aco_bobina|chapa_aco_bobina",
 "cerveja":r"cerveja|bebidas?|beer|ambev|brahma|skol|heineken|antartica|itaipava|refrigerant",
 "tijolo":r"tijolo|brick|telha|ceramica",
 "granito":r"granito|granitto|marmore|marble|pedra|brita|calcario|minerio",
 "racao":r"racao|xerem|animal_feed|feedmeal|farelo|sorgo",
 "sorgo":r"sorgo|sorghum",
 "palete":r"palete|pallet|madeirase|sucata|recicla"
}
ROLE_KEYWORDS = [
 ("reciclagem",r"recicl|sucata|sucatao|ferrovelho|sucateir|reaproveit"),
 # Fabricantes de automoveis e equipamentos jamais viram siderurgicas
 # por acidente so porque a DEF original contem bobinas no OUT.
 ("automotiva_fabrica",r"^(fiat|fca|gm|volkswagen|vw|renault|hyundai|toyota|ford|bmw|honda)(?:_|$)|montadora|fabrica_auto|fabricarros|autofabrica"),
 ("maquinas",r"^mc_?equip|^mcequip|equipamentos|maquin[a-z]*_|maquinaria"),
 ("premoldados",r"carmoprem|premold|pre_mold|concret"),
 ("cervejaria",r"ambev|cervej|brewery|cercrystal|heineken|brahma"),
 ("supermercado",r"super|mercado|atacadao|assai|bahamas|carrefour|compr_bem|compre_bem|extra_"),
 ("silo",r"silo|armazem|armz|cereal|comigo|caramuru|ac(s|z)_armazem"),
 ("cooperativa",r"cooper|coamo|coop|camda|cooperc"),
 ("agroinsumos",r"agro|adubo|fertil|agrish|agroce|agromais|casa_adubo"),
 ("fazenda",r"fazend|^faz|^farm|plant|rural|batata_f|^roca|agric"),
 ("fabrica_racao",r"racao|nutricao|animal_feed|brejeiro"),
 ("pecuaria",r"pecuar|gado|confin|boi|suino|frango|aves|criatorio"),
 ("madeireira",r"madeire|serraria|serra_|serrac|florest|^lenha"),
 ("textil",r"textil|tecel|fiac|algodoe|fiação"),
 ("cimenteira",r"cimento|cimenteir|votoran|intercement"),
 ("ceramica",r"ceram|olaria|tijol|telha"),
 ("pedreira",r"pedreira|quarry|basalto|extratora"),
 ("marmoraria",r"marmoraria|marmor|granito|granitos"),
 ("siderurgica",r"gerdau|cofer|arcel|sider|usiminas|steel|csn_"),
 ("metalurgica",r"metalurg|calha|cortedobra|(?:^|_)aco(?:_|$)|ferragem|usinagem|estrut_metal"),
  ("materiais",r"construsol|construm|material|casa_center|casaverde|dep_mat|construja|casa_mat"),
 ("obras",r"construcao|^constr|^cons_|obra|canteiro|batisse"),
 ("hortifruti",r"ceasa|hortif|sacolao|frut|banana|verdura"),
 ("alimentos",r"aliment|arcor|industria_alim|conservas"),
 ("atacadista",r"atacad|distrib|centro_dist|cd_|logistica|transpor"),
 ("automotiva",r"concession|veiculos|carros|revend_auto|autopecas|mercedes|scania"),
 ("posto",r"posto|combustivel|gasolina|petro|refinar")
]
DIRECTIONS = {
 "milho":({"fazenda","silo","cooperativa"},{"silo","cooperativa","fabrica_racao","agroinsumos"}),
 "soja":({"fazenda","silo","cooperativa"},{"silo","cooperativa","fabrica_racao","agroinsumos"}),
 "adubo":({"agroinsumos","atacadista"},{"fazenda","agroinsumos","cooperativa"}),
 "madeira":({"madeireira","materiais"},{"materiais","obras","premoldados","atacadista"}),
 "algodao":({"fazenda","cooperativa"},{"textil","cooperativa","atacadista"}),
 "cimento":({"cimenteira","materiais"},{"materiais","obras","premoldados"}),
 "batata":({"fazenda","hortifruti","cooperativa"},{"hortifruti","supermercado","alimentos","atacadista","cooperativa"}),
 "laranja":({"fazenda","hortifruti","cooperativa"},{"hortifruti","supermercado","alimentos","atacadista","cooperativa"}),
 "bobina":({"siderurgica"},{"metalurgica","automotiva_fabrica","maquinas"}),
 "cerveja":({"cervejaria","atacadista"},{"supermercado","atacadista","alimentos"}),
 "tijolo":({"ceramica","materiais"},{"materiais","obras"}),
 "granito":({"pedreira","marmoraria"},{"marmoraria","materiais","obras"}),
 "racao":({"fabrica_racao","agroinsumos","cooperativa"},{"pecuaria","fazenda","agroinsumos","cooperativa"}),
 "sorgo":({"fazenda","silo","cooperativa"},{"fabrica_racao","pecuaria","cooperativa","silo"}),
 "palete":({"madeireira"},{"reciclagem"})
}
RE_CARGO_FIELD = re.compile(r'(?m)^(\s*cargo\s*:\s*)(?:"[^"\r\n]*"|[a-zA-Z0-9_.-]+)')
RE_CARGO_UNIT = re.compile(r'\bcargo_data\s*:\s*cargo\.([a-z][\w]*)\b',re.I)
RE_COMPANY_PATH = re.compile(r'(?:^|/)def/company/([a-z0-9_]+)/(?:(in|out|editor)/)?([^/]+)$',re.I)
RE_CARGO_PATH = re.compile(r'(?:^|/)def/cargo/([a-z0-9_]+)(?:\.(?:sii|sui)|/([^/]+))$',re.I)
RE_TRAILER_BODY = re.compile(r'(?m)^\s*body_type\s*:\s*["'+"']?([a-z0-9_]+)",re.I)
RE_CARGO_BODY = re.compile(r'(?m)^\s*body_types(?:\[\d*\])?\s*:\s*["'+"']?([a-z0-9_]+)",re.I)

def normal(text):
    return "".join(c for c in unicodedata.normalize("NFKD",str(text).lower()) if not unicodedata.combining(c))

def clean_path(raw):
    path=str(raw).replace("\\","/").lstrip("/")
    if ".." in path.split("/") or path.startswith("./"): return None
    return path

def canonical_path(raw):
    path=clean_path(raw)
    if not path:return None
    # ZIPs de mapas podem comecar em def/company, company ou uma pasta raiz/...
    m=re.search(r'(?:^|/)(def/(?:company|cargo|vehicle)/.+)$',path,re.I)
    if m:return m.group(1).lower()
    m=re.search(r'(?:^|/)(def/cargo(?:\.[a-z0-9_-]+)?\.(?:sii|sui))$',path,re.I)
    if m:return m.group(1).lower()
    m=re.search(r'(?:^|/)(company/[a-z0-9_]+/(?:in|out|editor)/[^/]+)$',path,re.I)
    if m:return ("def/"+m.group(1)).lower()
    # Eldorado: Company ZIP nao contem "def/company"; cada empresa
    # esta diretamente na raiz, por exemplo:
    # ambev/out/bebidas.sii, alc_cle/in/tanquevazio.sii,
    # ale/editor/cerroazul.sii. Converter para o caminho CANONICO
    # esperado no jogo, sem modificar ou reempacotar a entrada.
    m=re.fullmatch(r'([a-z0-9_]+)/(in|out|editor)/([a-z0-9_.-]+\.(?:sii|sui))',
                   path,re.I)
    if m:
        name,direction,filename=m.groups()
        return f"def/company/{name}/{direction}/{filename}".lower()
    # Company permanente avulsa (empresa.sii) nos ZIPs de mapa.
    m=re.search(r'(?:^|/)(company/[a-z0-9_]+\.(?:sii|sui))$',path,re.I)
    if m:return ("def/"+m.group(1)).lower()
    m=re.search(r'(?:^|/)(cargo/[a-z0-9_]+(?:\.(?:sii|sui)|/[^/]+))$',path,re.I)
    if m:return ("def/"+m.group(1)).lower()
    m=re.search(r'(?:^|/)(vehicle/trailer_owned/.+)$',path,re.I)
    if m:return ("def/"+m.group(1)).lower()
    return None

def read_sii(blob):
    if b"\x00" in blob or blob.count(b"\xef\xbf\xbd")>3:
        raise ValueError("Encontrado SII/SUI binario ou malformado; nao e seguro editar sem converter para texto")
    return blob.decode("utf-8-sig","replace")

def cargo_tokens(text):
    return [x.lower() for x in re.findall(r'\bcargo\s*:\s*"?cargo\.([a-z0-9_]+)"?',text,re.I)]

def product_types(tokens):
    out=set()
    for token in tokens:
        n=normal(token)
        for label,pattern in PATTERNS.items():
            if re.search(pattern,n):out.add(label)
    return out

def zip_members(path, wanted=None):
    """Le ZIPs e .scs ZIP; nunca altera os originais."""
    path=Path(path)
    if path.is_dir():
        entries=((str(p.relative_to(path)).replace("\\","/"),p.read_bytes()) for p in path.rglob("*") if p.is_file())
    else:
        if not zipfile.is_zipfile(path):
            raise ValueError(f"'{path.name}' nao e arquivo ZIP/SCS ZIP legivel. Extraia previamente com o SCS Extractor oficial e selecione a pasta extraida.")
        zf=zipfile.ZipFile(path)
        infos=[x for x in zf.infolist() if not x.is_dir()]
        if len(infos)>80000 or sum(x.file_size for x in infos)>1_400_000_000:
            zf.close();raise ValueError(f"Arquivo excessivo ou suspeito: {path.name}")
        entries=((x.filename,zf.read(x)) for x in infos if x.file_size<8_000_000)
    out={}
    try:
        for name,data in entries:
            c=canonical_path(name)
            if c and (wanted is None or wanted(c)):
                if c in out and out[c]!=data:
                    raise ValueError(f"Colisao de caminhos no mesmo arquivo: {c} em {path.name}")
                out[c]=data
    finally:
        if not path.is_dir():zf.close()
    return out


def describe_archive(path, limit=50):
    """Diagnostico independente do extrator; funciona ate para ZIPs desconhecidos."""
    p=Path(path)
    if p.is_dir():
        names=[str(x.relative_to(p)).replace("\\","/") for x in p.rglob("*") if x.is_file()]
        sizes={}
    elif zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            inf=[x for x in z.infolist() if not x.is_dir()]
            names=[x.filename.replace("\\","/") for x in inf]
            sizes={x.filename:x.file_size for x in inf}
    else:
        return {"arquivo":p.name,"erro":"Nao e ZIP valido nem pasta extraida"}
    normalized=[clean_path(n) or n for n in names]
    company_like=[n for n in normalized if re.search(r'(^|/)(company|companies|def_company)(/|\.)',n,re.I)]
    inout=[n for n in normalized if re.search(r'/(in|out)/[^/]+\.(?:sii|sui)$',n,re.I)]
    legacy=[n for n in normalized if re.search(r'/(company|companies)/[a-z0-9_]+\.(?:sii|sui)$',n,re.I)]
    canonical=[n for n in normalized if canonical_path(n)]
    top=collections.Counter(n.split("/")[0] for n in normalized)
    extensions=collections.Counter(Path(n).suffix.lower() for n in normalized)
    root_company=[n for n in normalized
        if re.fullmatch(r'[a-z0-9_]+/(?:in|out|editor)/[a-z0-9_.-]+\.(?:sii|sui)',
                        n,re.I)]
    prefixed_company=[n for n in normalized if re.search(
        r'(?:^|/)def/company/[a-z0-9_]+/(?:in|out|editor)/[^/]+\.(?:sii|sui)$',
        n,re.I)]
    company_names=sorted({n.split("/")[0].lower() for n in root_company})
    return {
        "arquivo":p.name,"total_arquivos":len(names),
        "tamanho_total_declarado":sum(sizes.values()),
        "pastas_raiz":top.most_common(20),"extensoes":extensions.most_common(16),
        "caminhos_reconhecidos":len(canonical),
        "arquivos_parecidos_com_company":len(company_like),
        "caminhos_in_out":len(inout),"arquivos_permanentes_possiveis":len(legacy),
        "company_na_raiz":len(root_company),
        "company_com_prefixo_def":len(prefixed_company),
        "empresas_raiz_identificadas":len(company_names),
        "amostra_empresas_raiz":company_names[:limit],
        "layout_detectado":("company_direto_na_raiz" if root_company and
                           len(root_company)>=len(prefixed_company) else
                           "def_company" if prefixed_company else "desconhecido"),
        "amostra_company":company_like[:limit],
        "amostra_in_out":inout[:limit],
        "amostra_geral":normalized[:limit],
        "avisos":[]
    }

def export_diagnostic(path, dest, issue=""):
    report=describe_archive(path)
    if issue:report["erro_de_leitura"]=str(issue)
    folder=Path(dest);folder.mkdir(parents=True,exist_ok=True)
    name=re.sub(r'[^a-zA-Z0-9_-]','_',Path(path).stem)[:55]
    target=folder/("DIAGNOSTICO_ARQUIVO_"+name+".json")
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return target

@dataclass
class Company:
    name:str
    files:dict=field(default_factory=dict)
    editor_files:dict=field(default_factory=dict)
    old_in:set=field(default_factory=set)
    old_out:set=field(default_factory=set)
    role:str="desconhecida"
    explicit_role:bool=False

def classify_company(c):
    n=normal(c.name)
    incoming=product_types(c.old_in);outgoing=product_types(c.old_out)
    # Distinguir produtor rural de comercio agro: o historico IN/OUT supera
    # um prefixo de nome ambiguo (por exemplo empresas que comecam com "agro").
    if "adubo" in incoming and outgoing & {"milho","soja","batata","laranja","algodao"}:
        c.role="fazenda";c.explicit_role=True;return
    # Identificadores precisos sao preferiveis a deducoes por uma palavra isolada.
    for role,pat in ROLE_KEYWORDS:
        if re.search(pat,n):
            c.role=role;c.explicit_role=True;return
    incoming=product_types(c.old_in);outgoing=product_types(c.old_out)
    if "cerveja" in outgoing and "cerveja" not in incoming:c.role="cervejaria"
    elif "adubo" in outgoing and incoming & {"milho","soja","adubo"}:c.role="agroinsumos"
    elif incoming & {"milho","soja"} and "racao" in outgoing:c.role="fabrica_racao"
    elif incoming & {"milho","soja"} and outgoing & {"milho","soja"}:c.role="silo"
    elif "adubo" in incoming and outgoing & {"milho","soja","batata","laranja"}:c.role="fazenda"
    elif "madeira" in outgoing and not incoming & {"cimento","tijolo"}:c.role="madeireira"
    elif "cimento" in incoming and "cimento" in outgoing:c.role="materiais"
    elif "cerveja" in incoming and "cerveja" not in outgoing:c.role="supermercado"

def extract_map(path):
    archive=zip_members(path)
    companies={}
    old_file_count=0
    legacy=[]
    for p,raw in archive.items():
        # Definicoes legadas no arquivo permanente sao ACRESCENTADAS pelo
        # ETS2. Apenas limpar in/out nao as neutraliza (SCS Wiki).
        if re.fullmatch(r'def/company/[a-z0-9_]+\.(?:sii|sui)',p,re.I):
            txt=read_sii(raw)
            if re.search(r'(?m)^\s*(?:in_cargo|out_cargo)(?:\[\s*\d*\s*\])?\s*:',txt,re.I):
                legacy.append(p)
            continue
        m=RE_COMPANY_PATH.search(p)
        if not m:continue
        id,dir,filename=m.groups()
        c=companies.setdefault(id,Company(id))
        if dir in {"in","out"} and filename.lower().endswith((".sii",".sui")):
            old_file_count+=1;c.files[p]=raw
            ct=cargo_tokens(read_sii(raw))
            (c.old_in if dir=="in" else c.old_out).update(ct)
        elif dir=="editor" and filename.lower().endswith((".sii",".sui")):
            # Arquivo de instancia/cidade preservado byte a byte.
            c.editor_files[p]=raw
        elif dir is None and filename.endswith(".sii"):
            if re.search(r'(?m)^\s*(in_cargo|out_cargo)(?:\[\d*\])?\s*:',read_sii(raw)):
                legacy.append(p)
    if not companies or old_file_count==0:
        raise ValueError(f"{Path(path).name}: formato IN/OUT nao identificado. "+
                         "Veja o DIAGNOSTICO_ARQUIVO_*.json; o leitor NAO inventara "+
                         "empresas nem criara .scs a partir de dados desconhecidos.")
    if legacy:raise ValueError(
        "Foi encontrado in_cargo/out_cargo legado em company_permanent; "
        "o ETS2 ACRESCENTA estas cargas mesmo se as pastas in/out forem neutralizadas. "
        "Geracao bloqueada para nao produzir Company incompleta: "+
        ", ".join(legacy[:5]))
    for c in companies.values():classify_company(c)
    return companies,old_file_count


# Politica especifica Eldorado: mercadorias inglesas da DEF. Nunca
# traduzir fruits -> batatas ou bananas -> laranjas.
ELDORADO_ENGLISH = (
    ("batata",r"^(?:potato|potatoes|potatos)(?:_[a-z0-9]+)?$"),
    ("laranja",r"^(?:orange|oranges|citrus|citrus_fruit)(?:_[a-z0-9]+)?$"),
    ("banana",r"^(?:banana|bananas|plantain|plantains)(?:_[a-z0-9]+)?$"),
    ("frutas_gerais",r"^(?:fruit|fruits|fresh_fruit|mixed_fruits|vegetables|veggies)(?:_[a-z0-9]+)?$"),
    ("cerveja",r"^(?:beer|beers|ale|lager|cerveja|cervejas)(?:_[a-z0-9]+)?$"),
    ("bebidas_gerais",r"^(?:beverage|beverages|drinks|limonades|soda|soft_drinks|"
                      r"bottle_water|bottled_water|water)(?:_[a-z0-9]+)?$"),
    ("adubo",r"^(?:fertiliz(?:er|ers)|fertilis(?:er|ers)|fertilizante|"
             r"compost|urea|npk|ammonium_nitrate)(?:_[a-z0-9]+)?$"),
    ("milho",r"^(?:corn|maize|milho)(?:_[a-z0-9]+)?$"),
    ("soja",r"^(?:soybean|soybeans|soya|soy_beans|soja)(?:_[a-z0-9]+)?$"),
    ("arroz",r"^(?:rice|arroz)(?:_[a-z0-9]+)?$"),
    ("trigo",r"^(?:wheat|trigo)(?:_[a-z0-9]+)?$"),
    ("racao",r"^(?:animal_feed|livestock_feed|feed|feedmeal|compound_feed|"
             r"fodder|forage|racao)(?:_[a-z0-9]+)?$"),
    ("algodao",r"^(?:cotton|cotton_bales|cott_seed|algodao)(?:_[a-z0-9]+)?$"),
    ("palete",r"^(?:pallet|pallets|wooden_pallets|palete|paletes)(?:_[a-z0-9]+)?$"),
    ("madeira",r"^(?:logs|log|timber|lumber|wood|wooden_planks|sawn_wood|madeira)(?:_[a-z0-9]+)?$"),
    ("cimento",r"^(?:cement|cement_bags|bagged_cement|cimento)(?:_[a-z0-9]+)?$"),
    ("tijolo",r"^(?:brick|bricks|clay_bricks|tijolos)(?:_[a-z0-9]+)?$"),
    ("granito",r"^(?:granite|marble|marble_blocks|stone_blocks|granito)(?:_[a-z0-9]+)?$"),
    ("bobina",r"^(?:steel_coil|steel_coils|steel_roll|coil_steel|bobina|bobinas)(?:_[a-z0-9]+)?$"),
    ("sorgo",r"^(?:sorghum|sorgo)(?:_[a-z0-9]+)?$")
)

def eldorado_translate(tokens):
    """Traduz IDs de carga em ingles preservando a especie de mercadoria."""
    found=set()
    for token in tokens:
        n=normal(token)
        for cat,pattern in ELDORADO_ENGLISH:
            if re.fullmatch(pattern,n,re.I):found.add(cat)
    found |= product_types(tokens)
    return found

ELDORADO_LOGISTICS = re.compile(
    r"transport|transpor|transp|logistic|logistica|logist|freight|"
    r"carrier|haulage|brasilog|braslog|rasador|avant|cmm|ttr[_-]?log|"
    r"^trame2$|^trade2$|^stokes2$|^posped2$|^ancapi$",re.I)
ELDORADO_BANANA = re.compile(
    r"banana|bananal|banana_farm|banana_plant|^eldbanana|^bana_",re.I)
ELDORADO_WHOLESALE = re.compile(
    r"atacad|wholesale|ceasa|hortif|frutaria|sacolao|"
    r"distrib_fruit|fresh_produce|mercado_horti",re.I)
ELDORADO_POTATO_FARM = re.compile(r"batat|potato",re.I)
ELDORADO_ORANGE_FARM = re.compile(r"laranj|citrus|orange",re.I)
ELDORADO_AGRO_SUPPLIER = re.compile(
    r"agropec|agroinsum|fertil|adubo|insumos|agrocenter|agrish|agroce|agromais",re.I)

def eldorado_classify(c):
    """Reclassificar por atividade, nunca fabricar por um OUT antigo."""
    name=normal(c.name)
    out_types=eldorado_translate(c.old_out)
    in_types=eldorado_translate(c.old_in)
    if ELDORADO_LOGISTICS.search(name):
        c.role="transportadora";c.explicit_role=True;return
    # Hubs com catalogo enorme e carga de setores desconexos nao sao fabrica.
    if not c.explicit_role and len(c.old_out)>=45 and len(out_types)>=6:
        c.role="hub_generico";c.explicit_role=False;return
    if (ELDORADO_BANANA.search(name) and
        not ELDORADO_WHOLESALE.search(name) and
        c.role in {"hortifruti","fazenda","desconhecida"}):
        c.role="bananal";c.explicit_role=True;return
    if ("banana" in out_types and "banana" not in in_types and
        not ({"batata","laranja"} & out_types) and
        not ELDORADO_WHOLESALE.search(name) and
        c.role in {"hortifruti","fazenda","desconhecida"}):
        c.role="bananal";c.explicit_role=False;return
    if ELDORADO_POTATO_FARM.search(name) and c.role in {"hortifruti","fazenda","desconhecida"}:
        c.role="fazenda_batata";c.explicit_role=True;return
    if ELDORADO_ORANGE_FARM.search(name) and c.role in {"hortifruti","fazenda","desconhecida"}:
        c.role="fazenda_laranja";c.explicit_role=True;return
    # Interpretacao bilingue dos proprios identificadores de empresa.
    # Sem nome significativo ou evidencias, NAO chutar fornecedor.
    role_english=(
        ("pecuaria",r"cattle_farm|cattle_ranch|livestock|poultry_farm|pig_farm|feedlot"),
        ("fazenda",r"(?:^|_)(?:farm|farms|farming|farmstead)(?:_|$)|agricultural_farm"),
        ("cervejaria",r"brewery|brewing|beer_factory"),
        ("supermercado",r"supermarket|grocery_store|hypermarket|grocery"),
        ("silo",r"grain_elevator|grain_storage|grain_silo"),
        ("cooperativa",r"cooperative|farmers_coop"),
        ("hortifruti",r"produce_market|fresh_produce|fruit_warehouse"),
        ("cimenteira",r"cement_plant|cement_factory"),
        ("obras",r"construction_site|building_site|construction_work"),
        ("materiais",r"building_supplies|hardware_store|building_materials"),
        ("madeireira",r"sawmill|timber_mill|lumberyard"),
        ("pedreira",r"quarry|stone_mine|rock_quarry"),
        ("marmoraria",r"stonecutting|granite_shop|stoneworks"),
        ("siderurgica",r"steel_mill|steel_factory|steelworks"),
        ("metalurgica",r"metalworks|sheetmetal|steel_fabrication"),
        ("textil",r"textile_mill|cotton_mill|spinning_mill"),
        ("agroinsumos",r"agro_supply|fertilizer_store|fertilizer_plant"),
        ("fabrica_racao",r"feedmill|feed_factory|animal_feed_factory"),
        ("reciclagem",r"recycling_yard|scrapyard"),
        ("alimentos",r"food_processing|cannery")
    )
    if c.role in {"desconhecida","hortifruti","atacadista"}:
        for role,pattern in role_english:
            if re.search(pattern,name):
                c.role=role;c.explicit_role=True;return
    if ELDORADO_AGRO_SUPPLIER.search(name) and c.role in {"agroinsumos","desconhecida"}:
        c.role="agroinsumos";c.explicit_role=True;return
    if ELDORADO_WHOLESALE.search(name) and c.role in {"hortifruti","atacadista","desconhecida"}:
        c.role="hortifruti";c.explicit_role=True;return
    if c.role=="atacadista" and not ELDORADO_WHOLESALE.search(name):
        c.role="hub_generico";c.explicit_role=False;return
    if not c.explicit_role and c.role in {"cervejaria","madeireira","silo","supermercado"}:
        c.role="desconhecida"

def eldorado_permit(c,category,direction):
    """Politica de economia real: produtor, revenda com prova, consumidor.

    Evidencia de transporte nao e evidencia de producao. Uma plantacao
    especializada NAO recebe qualquer produto hortifruti.
    """
    role=c.role
    outgoing=eldorado_translate(c.old_out)
    incoming=eldorado_translate(c.old_in)
    observed=outgoing if direction=="out" else incoming
    both=incoming|outgoing
    if role in {"transportadora","hub_generico","desconhecida"}:return None
    if role=="bananal":
        if category=="adubo" and direction=="in":
            return "bananal compra fertilizante para cultivo de bananas"
        return None
    if category in {"batata","laranja"}:
        correct=("fazenda_batata" if category=="batata" else "fazenda_laranja")
        other=("fazenda_laranja" if category=="batata" else "fazenda_batata")
        if role==other:return None
        if direction=="out":
            if role==correct:return "plantacao especializada identificada de "+category
            if role=="fazenda" and category in outgoing:
                return "fazenda produz "+category+" documentado no OUT original"
            if role in {"hortifruti","cooperativa"} and category in both:
                return "revenda de "+category+" documentada na DEF"
            return None
        if role in {"supermercado","hortifruti"}:
            return "comercio recebe "+category+" para revenda"
        if role=="cooperativa" and category in both:
            return "cooperativa recebe a cultura documentada"
        if role=="alimentos" and category in incoming:
            return "industria alimenticia recebe esta materia-prima na DEF"
        return None
    if category=="cerveja":
        if direction=="out":
            if role=="cervejaria" and c.explicit_role:
                return "cervejaria identificada produz/expede cerveja"
            if role in {"supermercado","atacadista"} and "cerveja" in outgoing:
                return "comercio revende cerveja documentada"
            return None
        if role=="supermercado":return "supermercado recebe cerveja para revenda"
        if role=="atacadista" and ({"cerveja","bebidas_gerais"} & both):
            return "distribuidor documentado de bebidas recebe cerveja"
        return None
    if category=="adubo":
        if direction=="out":
            if role=="agroinsumos" and (
                    ELDORADO_AGRO_SUPPLIER.search(normal(c.name)) or "adubo" in outgoing):
                return "agropecuaria documentada fornece adubo"
            if role=="cooperativa" and "adubo" in outgoing:
                return "cooperativa distribui fertilizante documentado"
            return None
        if role in {"fazenda","fazenda_batata","fazenda_laranja"}:
            return "produtor rural compra adubo para plantio"
        if role in {"agroinsumos","cooperativa"} and "adubo" in incoming:
            return "distribuidor recebe adubo para comercializacao"
        return None
    if category in {"milho","soja","sorgo"}:
        if direction=="out":
            if role=="fazenda" and category in outgoing:
                return "fazenda produz "+category+" documentado"
            if role in {"silo","cooperativa"} and category in both:
                return "cooperativa/armazem movimenta "+category+" documentado"
            return None
        if role in {"silo","cooperativa","fabrica_racao"} and (
             category in both or role=="fabrica_racao"):
            return "recebe "+category+" para armazenamento/industria"
        if role=="pecuaria" and category=="sorgo" and "racao" in incoming:
            return "pecuaria recebe sorgo para alimentacao de animais"
        return None
    if category=="racao":
        if direction=="out":
            if role=="fabrica_racao" and c.explicit_role:
                return "fabricante de racao identificado"
            if role=="agroinsumos" and "racao" in both:
                return "agropecuaria revende racao documentada"
            return None
        if role=="pecuaria":return "criacao animal compra racao"
        if role=="fazenda" and "racao" in incoming:
            return "fazenda compra racao documentada no IN"
        if role=="agroinsumos" and "racao" in incoming:
            return "agropecuaria recebe racao para revenda"
        return None
    if category=="algodao":
        if direction=="out" and role=="fazenda" and "algodao" in outgoing:
            return "fazenda documenta producao de algodao"
        if direction=="out" and role=="cooperativa" and "algodao" in both:
            return "cooperativa vende algodao documentado"
        if direction=="in" and role=="textil":
            return "industria textil recebe algodao"
        if direction=="in" and role=="cooperativa" and "algodao" in both:
            return "cooperativa recebe algodao documentado"
        return None
    if category=="madeira":
        if direction=="out":
            if role=="madeireira" and c.explicit_role:
                return "serraria/madeireira fornece madeira"
            if role=="materiais" and "madeira" in both:
                return "loja de materiais revende madeira documentada"
            return None
        if role in {"materiais","obras"}:
            return "construcao compra madeira"
        return None
    if category=="palete":
        if direction=="out" and role=="madeireira" and c.explicit_role:
            return "madeireira fornece paletes"
        if direction=="in" and role=="reciclagem" and c.explicit_role:
            return "reciclagem recebe paletes usados"
        return None
    if category=="bobina":return permits(c,category,direction)
    if category=="cimento":
        if direction=="out":
            if role=="cimenteira" and c.explicit_role:
                return "fabrica de cimento identificada"
            if role=="materiais" and "cimento" in both:
                return "loja de material revende cimento documentado"
            return None
        if role in {"materiais","obras","premoldados"}:
            return "revenda/obra/pre-moldado compra cimento"
        return None
    if category=="tijolo":
        if direction=="out" and role=="ceramica" and c.explicit_role:
            return "ceramica/olaria fabrica tijolos"
        if direction=="out" and role=="materiais" and "tijolo" in both:
            return "loja de material revende tijolos documentados"
        if direction=="in" and role in {"materiais","obras"}:
            return "obra/revenda compra tijolos"
        return None
    if category=="granito":
        if direction=="out" and role in {"pedreira","marmoraria"} and c.explicit_role:
            return "extracao/beneficiamento de pedras"
        if direction=="in" and role in {"marmoraria","materiais"}:
            return "beneficiamento/revenda recebe pedras"
        if direction=="in" and role=="obras" and "granito" in incoming:
            return "obra recebe granito documentado"
        return None
    return None

def cargo_inventory(mods):
    """Cargo_data + 2 sistemas distintos de trailer_def do ETS2.

    Legado: def/cargo/<cargo>/<reboque>.sii
    Reboque proprio: def/vehicle/trailer_defs/ e trailer_owned/<id>/body/
    NUNCA exigir def/cargo/<cargo>/ para cargas de reboque proprio.
    """
    records={}
    legacy_trailers=defaultdict(set)
    ownable_trailer_defs=set()
    owned_bodies=set()
    totals={"owned_body_files":0,"owned_trailer_def_files":0,"legacy_trailer_def_files":0}
    for source,archive in mods:
        for path,raw in archive.items():
            if not path.endswith((".sii",".sui")):continue
            # Carrocerias das configuracoes compraveis pelo jogador.
            if path.startswith("def/vehicle/trailer_owned/") and "/body/" in path:
                text=read_sii(raw)
                types=set(RE_TRAILER_BODY.findall(text))
                if types:
                    owned_bodies.update(types)
                    totals["owned_body_files"]+=1
            # A partir do ETS2 1.32 trailer_def de reboque proprio
            # pertence a def/vehicle/trailer_defs, nao a def/cargo/cargaN/.
            if path.startswith("def/vehicle/trailer_defs/"):
                text=read_sii(raw)
                if re.search(r'\btrailer_def\s*:',text,re.I):
                    ownable_trailer_defs.update(RE_TRAILER_BODY.findall(text))
                    totals["owned_trailer_def_files"]+=1
            m=RE_CARGO_PATH.search(path)
            if not m:continue
            cid,sub=m.groups()
            txt=read_sii(raw)
            if sub is None:
                ids=RE_CARGO_UNIT.findall(txt)
                for id in ids:
                    if id.lower()!=cid.lower():continue
                    body=set(RE_CARGO_BODY.findall(txt))
                    if cid in records and records[cid]["body"]!=body:
                        raise ValueError(f"Definicoes conflitantes do cargo {cid} entre arquivos do reboque")
                    records[cid]={"source":source,"path":path,"raw":raw,"body":body,
                                  "valuable":bool(re.search(r'\bvaluable\s*:\s*true\b',txt,re.I)),
                                  "adr":bool(re.search(r'\badr_class\s*:\s*[1-9]',txt,re.I))}
            elif re.search(r'\btrailer_def\s*:',txt,re.I):
                legacy_trailers[cid].update(RE_TRAILER_BODY.findall(txt))
                totals["legacy_trailer_def_files"]+=1
    return records,legacy_trailers,owned_bodies,ownable_trailer_defs,totals

def permits(c,category,dir):
    role=c.role
    observed=product_types(c.old_out if dir=="out" else c.old_in)
    reverse=product_types(c.old_in if dir=="out" else c.old_out)
    allow=DIRECTIONS[category][0 if dir=="out" else 1]
    if role not in allow: return None
    # Grade Baixa: as mercadorias NAO definem a industria de uma empresa.
    # Fabrica automotiva, fabricante de maquinario, construcao e premoldados
    # podem CONSUMIR insumos metalicos, mas nao fabricam bobinas de aco.
    if category=="bobina":
        if dir=="out":
            if role!="siderurgica" or not c.explicit_role:
                return None
            return ("siderurgica identificada: expedicao de aco em bobinas"
                    if "bobina" in observed else
                    "siderurgica identificada: producao de produtos siderurgicos")
        if role=="automotiva_fabrica":
            return "montadora identificada: bobinas de aco como insumo de fabricacao"
        if role=="metalurgica" and c.explicit_role:
            return "metalurgica identificada: bobinas de aco como insumo"
        if role=="maquinas" and "bobina" in observed:
            return "maquinario: recebimento de bobinas documentado no IN original"
        return None
    if category=="cimento":
        if dir=="out":
            if role=="cimenteira" and c.explicit_role:
                return "fabricante de cimento identificado"
            if role=="materiais" and "cimento" in observed:
                return "revenda de cimento documentada no OUT original"
            return None
        if role=="premoldados":
            return "fabricacao de pre-moldados: cimento recebido como materia-prima"
    if category=="granito" and dir=="out":
        if role=="pedreira" and c.explicit_role:
            return "pedreira identificada: extracao e expedicao de pedras"
        if role=="marmoraria" and (c.explicit_role or "granito" in observed):
            return "marmoraria identificada: venda de pedras beneficiadas"
        return None
    # Proibir falsa classificacao de recicladora / madeireira, e protecao contra dispersao universal.
    if category=="palete":
        if dir=="out" and role=="madeireira":return "madeireira: origem de paletes"
        if dir=="in" and role=="reciclagem":return "reciclagem/sucatao: destino de paletes"
        return None
    if role=="desconhecida":return None
    if category in observed:
        return "documental: mercadoria/familia no "+dir.upper()+" original"
    if category=="sorgo" and "milho" in observed:
        return "inferida: movimentacao comprovada de cereais"
    if category=="racao":
        if dir=="in" and role=="fazenda" and ("racao" in reverse or "racao" in observed):
            return "inferida: fazenda com evidencias de alimentacao animal"
        if dir=="in" and role=="pecuaria":return "economica: criacao animal compra racao"
        if dir=="out" and role=="fabrica_racao":return "economica: fabricacao de racao"
        if dir=="out" and role=="agroinsumos" and ("adubo" in observed or "racao" in reverse):
            return "inferida: revenda agropecuaria"
        return None
    if category=="algodao":
        if "algodao" in observed or "algodao" in reverse:return "documental: algodao presente na DEF"
        return None
    if category=="granito" and role=="marmoraria" and dir=="out" and "granito" not in observed:
        return None
    if category=="bobina" and role=="obras" and "bobina" not in observed and "bobina" not in reverse:
        return None
    if category=="cerveja" and dir=="out" and role=="atacadista" and "cerveja" not in observed:
        return None
    if category=="madeira" and dir=="out" and role=="materiais" and "madeira" not in observed:
        return None
    if category=="adubo" and dir=="out" and role=="atacadista" and "adubo" not in observed:
        return None
    if category=="cimento" and dir=="out" and role=="premoldados" and "cimento" not in observed:
        return None
    if category=="milho" or category=="soja":
        if dir=="out" and role=="fazenda" and not (observed & {"milho","soja"} or reverse & {"milho","soja"}):
            return None
    if role=="fazenda" and dir=="out" and category in {"batata","laranja","sorgo"}:
        if not (observed & {category,"milho","soja"} or reverse & {category}):
            return None
    if role in {"supermercado","materiais","hortifruti","agroinsumos","silo","cooperativa"}:
        return "inferida: compra/venda compativel com a atividade e capacidade"
    return "inferida: utilizacao/producao compativel com a atividade"

def cargo_sii(cid):
    return f'SiiNunit\n{{\n cargo_def : .{cid} {{\n  cargo: "cargo.{cid}"\n }}\n}}\n'.encode("utf-8")

def neutralize(raw,path):
    txt=read_sii(raw)
    if not RE_CARGO_FIELD.search(txt):
        if re.search(r'\bcargo_def\s*:',txt,re.I):
            raise ValueError("Nao foi possivel neutralizar cargo_def sem campo cargo: "+path)
        return raw
    result=RE_CARGO_FIELD.sub(lambda m:m.group(1)+'""',txt)
    if cargo_tokens(result):
        raise ValueError("Cargo antigo ainda ativo apos neutralizacao: "+path)
    return result.encode("utf-8")

def cargo_override(record,drop_skill=True):
    txt=read_sii(record["raw"])
    if drop_skill and record["valuable"]:
        txt=re.sub(r'(?im)^(\s*valuable\s*:\s*)true\b',r'\1false',txt)
    # Reducao seletiva; nao altera corpo/modelos, que devem continuar no mod original.
    if re.search(r'(?im)^\s*prob_coef\s*:',txt):
        txt=re.sub(r'(?im)^(\s*prob_coef\s*:\s*)[\d.]+',r'\g<1>0.08',txt)
    else:
        # Campo deve estar dentro de cargo_data; inserido imediatamente depois da abertura.
        txt=re.sub(r'(\bcargo_data\s*:\s*cargo\.carga16\s*\{)',r'\1\n prob_coef: 0.08',txt,count=1,flags=re.I)
    return txt.encode("utf-8")


def cargo_manifest_warnings(sources,records):
    masters=[]
    for source,archive in sources:
        for path,blob in archive.items():
            if re.fullmatch(r'def/cargo(?:\.[a-z0-9_-]+)?\.(?:sii|sui)',path):
                masters.append((source,path,read_sii(blob)))
    if not masters:
        return ["Master def/cargo*.sii nao encontrado nos SCS anexados; "
                "o registro das mercadorias precisa ser confirmado no jogo."]
    joined="\n".join(t for src,p,t in masters).lower()
    missing=[f"carga{n}" for n in MANIFEST if f"carga{n}" in records and
             not re.search(r'(?<![a-z0-9_])carga'+str(n)+r'(?![a-z0-9_])',joined)]
    notices=["Manifests identificados: "+
             ", ".join(src+"/"+p for src,p,t in masters[:10])]
    if missing:
        notices.append("Cargas nao citadas literalmente nos manifestos: "+
                       ", ".join(missing)+". Includes indiretos podem existir.")
    return notices

def hash_source(path):
    h=hashlib.sha256();p=Path(path)
    if p.is_dir():
        files=sorted(x for x in p.rglob("*") if x.is_file())
        for f in files:
            h.update(str(f.relative_to(p)).replace("\\","/").encode("utf-8"))
            with f.open("rb") as stream:
                for part in iter(lambda:stream.read(1024*1024),b""):h.update(part)
    else:
        with p.open("rb") as stream:
            for part in iter(lambda:stream.read(1024*1024),b""):h.update(part)
    return h.hexdigest()

def grade_label(body_types):
    names={str(x).lower() for x in body_types}
    # Ler os body_types REAIS no cargo_data, nao presumir as grades pelo numero ID.
    if "alta" in names:return "Grade Alta"
    if "baixa" in names:return "Grade Baixa"
    if "hopper" in names:return "Hopper / graneleiro"
    return "Outras carrocerias: "+", ".join(sorted(names))

def coverage_audit(companies,cargo_routes,cargo_records,name):
    """Cobertura de cada cargo: ao menos um produtor e comprador DIFERENTES.

    Nao cria nem inventa permissao; somente documenta o mercado existente.
    """
    cargo_rows=[]
    for n,(category,title) in MANIFEST.items():
        cargo=f"carga{n}"
        route=cargo_routes[cargo]
        outs=set(route["origens_lista"])
        ins=set(route["destinos_lista"])
        valid_pairs=len(outs)*len(ins)-len(outs&ins)
        has_route=bool(outs and ins and valid_pairs)
        candidates=[]
        if not has_route:
            for company in sorted(companies.values(),key=lambda c:c.name):
                original=eldorado_translate(company.old_in|company.old_out) if name.lower()=="eldorado" else product_types(company.old_in|company.old_out)
                if category in original:
                    candidates.append({
                        "empresa":company.name,"setor":company.role,
                        "evidencia_def":category,
                        "in_original":category in (eldorado_translate(company.old_in) if name.lower()=="eldorado" else product_types(company.old_in)),
                        "out_original":category in (eldorado_translate(company.old_out) if name.lower()=="eldorado" else product_types(company.old_out)),
                        "nota":"Candidato documental, NAO autorizacao automatica"
                    })
        body=cargo_records.get(cargo,{}).get("body",set())
        cargo_rows.append({
            "id":cargo,"mercadoria":title,"categoria":category,
            "carroceria":grade_label(body),"body_types":sorted(body),
            "origens":len(outs),"destinos":len(ins),
            "pares_distintos_possiveis":valid_pairs,
            "rota_completa":has_route,
            "origens_lista":sorted(outs),"destinos_lista":sorted(ins),
            "lacuna":("nenhuma" if has_route else
                      "sem origem e destino" if not outs and not ins else
                      "sem origem" if not outs else
                      "sem destino" if not ins else
                      "origem e destino sao a mesma empresa"),
            "candidatos_com_evidencia_para_revisao":candidates[:100],
            "total_candidatos_documentais":len(candidates)
        })
    complete=sum(1 for r in cargo_rows if r["rota_completa"])
    grades={}
    for row in cargo_rows:
        group=grades.setdefault(row["carroceria"],{"total":0,"rotas_completas":0,
                                                  "cargas_faltantes":[]})
        group["total"]+=1
        if row["rota_completa"]:group["rotas_completas"]+=1
        else:group["cargas_faltantes"].append(row["id"])
    return {"mapa":name,"total":len(MANIFEST),
            "cobertura_por_carroceria":grades,
            "cargas_com_rota":complete,
            "cargas_sem_rota":len(MANIFEST)-complete,
            "pronto_para_gerar":complete==len(MANIFEST),
            "metodologia":"carga valida precisa ter IN e OUT economicamente justificados e empresa origem diferente da empresa destino",
            "cargas":cargo_rows}

def write_coverage_report(directory,audit):
    """Grava diagnostico mesmo quando a geracao SCS e bloqueada."""
    target=Path(directory);target.mkdir(parents=True,exist_ok=True)
    name=audit["mapa"]
    (target/(name+"_COBERTURA_23_CARGAS.json")).write_text(
        json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
    with (target/(name+"_COBERTURA_23_CARGAS.csv")).open(
            "w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f,delimiter=";")
        w.writerow(["id","mercadoria","carroceria","body_types","origens",
                    "destinos","pares_distintos","rota_completa","lacuna",
                    "empresas_de_origem","empresas_de_destino","candidatos_para_revisao"])
        for c in audit["cargas"]:
            w.writerow([c["id"],c["mercadoria"],c["carroceria"],
                ",".join(c["body_types"]),c["origens"],c["destinos"],
                c["pares_distintos_possiveis"],"SIM" if c["rota_completa"] else "NAO",
                c["lacuna"],",".join(c["origens_lista"]),",".join(c["destinos_lista"]),
                ",".join(x["empresa"] for x in c["candidatos_com_evidencia_para_revisao"])])
    return target/(name+"_COBERTURA_23_CARGAS.json")

def write_report(outdir,name,result):
    with open(outdir/(name+"_auditoria.json"),"w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    with open(outdir/(name+"_empresas.csv"),"w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f,delimiter=";")
        writer.writerow(["empresa","setor","in_novos","out_novos","in_originais","out_originais"])
        for row in result["empresas"]:
            writer.writerow([row[k] for k in ("empresa","setor","in_novos","out_novos","in_originais","out_originais")])
    if name.lower()=="eldorado":
        with open(outdir/(name+"_traducoes_cargas_ingles.csv"),"w",
                  encoding="utf-8-sig",newline="") as f:
            writer=csv.writer(f,delimiter=";")
            writer.writerow(["id_original_ingles","familias_traduzidas_pt"])
            for token,categories in sorted(result["traducoes_ingles_portugues"].items()):
                writer.writerow([token,", ".join(categories) if categories else "NAO_IDENTIFICADO"])
        with open(outdir/(name+"_permissoes_rejeitadas.csv"),"w",
                  encoding="utf-8-sig",newline="") as f:
            writer=csv.writer(f,delimiter=";")
            writer.writerow(["empresa","setor","direcao","mercadoria","motivo"])
            for item in result["rejeicoes_eldorado"]:
                writer.writerow([item["empresa"],item["setor"],item["direcao"],
                                 item["familia"],item["motivo"]])
    with open(outdir/(name+"_rotas_justificadas.csv"),"w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f,delimiter=";")
        w.writerow(["empresa","setor","tipo_de_classificacao","direcao","carga",
                    "categoria","justificativa_economica"])
        for row in result["evidencias"]:
            w.writerow([row["empresa"],row["setor"],
                        "nome_ou_marca" if row["classificacao_explicita"] else "inferida_por_historico",
                        row["direcao"],row["carga"],row["categoria"],row["justificativa"]])

def generate(inputs,output,log=lambda s:None, fix_skills=True, require_complete=None):
    outdir=Path(output);outdir.mkdir(parents=True,exist_ok=True)
    log("Lendo arquivos originais do Librelato...")
    sources=[]
    for label,path in [("MOD PRINCIPAL",inputs["mod"]),("DEF 1",inputs["def1"]),("DEF 2",inputs["def2"])]:
        arc=zip_members(path)
        if not arc:raise ValueError(f"{label}: nenhuma definicao def/ legivel encontrada")
        sources.append((label,arc))
        log(f"{label}: {len(arc)} definicoes")
    records,legacy,owned,ownable_defs,totals=cargo_inventory(sources)
    errors=[];warnings=cargo_manifest_warnings(sources,records)
    provenance=[{"arquivo":Path(p).name,"papel":label,"sha256":hash_source(p),
                 "definicoes":len(arc)}
                for (label,p),(_,arc) in zip(
                    [("MOD PRINCIPAL",inputs["mod"]),("DEF 1",inputs["def1"]),
                     ("DEF 2",inputs["def2"])],sources)]
    log("Trailer: "+str(totals["owned_body_files"])+" arquivos de carroceria propria; "+
        str(totals["owned_trailer_def_files"])+" trailer_defs novos; "+
        str(totals["legacy_trailer_def_files"])+" trailer_defs antigos.")
    log("Body types das carrocerias: "+str(sorted(owned))+
        " | trailer_defs globais: "+str(sorted(ownable_defs)))
    if not owned:
        warnings.append("SEM CARROCERIAS trailer_owned/*/body nos SCS originais. "+
                        "Impossivel garantir compatibilidade com o reboque proprio; "+
                        "verifique se existem no jogo base ou em outro mod.")
    if not ownable_defs and not any(legacy.values()):
        warnings.append("Nenhuma trailer_def foi encontrada nos originais fornecidos. "+
                        "O arquivo pode depender das defs base do ETS2 ou de outra fonte; "+
                        "nao significa automaticamente falha para reboque proprio.")
    for n,(category,description) in MANIFEST.items():
        id=f"carga{n}"
        r=records.get(id)
        if not r:
            errors.append(f"{id} ({description}): cargo_data ausente no reboque")
            continue
        if not r["body"]:
            errors.append(f"{id}: body_types ausente no cargo_data")
            continue
        # Validacao primaria para Mercado de Cargas com reboque proprio.
        # Nao usar um trailer_def LEGADO como requisito obrigatorio.
        if owned and not (r["body"]&owned):
            errors.append(f"{id}: nenhum body_type compativel com as carrocerias "+
                          f"do reboque proprio: carga={sorted(r['body'])}, "+
                          f"trailer_owned={sorted(owned)}")
        # O trailer_def global eh uma camada adicional; sua ausencia nao
        # significa que def/cargo/<cargo>/ tenha de existir.
        if ownable_defs and not (r["body"]&ownable_defs):
            warnings.append(f"{id}: nao ha trailer_def global com body_type "+
                            f"{sorted(r['body'])}; confirme trailer_body_set do reboque.")
        if legacy.get(id) and not (r["body"]&legacy[id]):
            warnings.append(f"{id}: trailer_def legado nao tem body_type equivalente; "+
                            "pode ser irrelevante para a configuracao propria.")
        if r["adr"]:
            warnings.append(f"{id}: exige habilidade ADR; verificar se intencional")
        if r["valuable"]:
            warnings.append(f"{id}: valuable=true"+
                            (" (correcao somente no mod gerado)" if fix_skills else
                             " (habilidade de alto valor exigida)"))
    if errors:
        outdir.joinpath("FALHA_DIAGNOSTICO.txt").write_text(
            "GERACAO BLOQUEADA: corrigir problemas tecnicos antes de entregar Companies.\n\n"+
            "\n".join(errors)+"\n\nAVISOS\n"+"\n".join(warnings),encoding="utf-8")
        raise ValueError("Diagnostico tecnico bloqueou geracao:\n- "+"\n- ".join(errors[:12]))
    log("Validacao de cargo_data e carroceria de reboque proprio concluida; avisos no relatorio.")
    # FASE 1: preflight dos mapas SELECIONADOS. Nada publica se algum falhar.
    checked_maps={}
    map_failures={}
    for name,path in inputs["maps"].items():
        log("Verificando estrutura de "+name+" ...")
        try:
            checked_maps[name]=extract_map(path)
            if name.lower()=="eldorado":
                for c in checked_maps[name][0].values():
                    eldorado_classify(c)
            log(name+": "+str(len(checked_maps[name][0]))+" empresas reconhecidas.")
        except Exception as exc:
            map_failures[name]=str(exc)
            diag=export_diagnostic(path,outdir,str(exc))
            log("ERRO em "+name+": "+str(exc))
            log("Diagnostico salvo: "+str(diag))
    if map_failures:
        report=outdir/"FALHA_MAPAS_NAO_GERAR.txt"
        report.write_text("Nenhum SCS novo foi publicado por esta execucao. "+
                          "Nao use resultados parciais ou de execucoes anteriores.\n\n"+
                          "\n".join(k+": "+v for k,v in map_failures.items())+
                          "\n\nArquivos DIAGNOSTICO_ARQUIVO_*.json foram criados na pasta de saida.\n",
                          encoding="utf-8")
        raise ValueError("Analise interrompida sem publicar Companies. "+
                         "Confira FALHA_MAPAS_NAO_GERAR.txt e envie o "+
                         "DIAGNOSTICO_ARQUIVO_*.json do mapa com erro.")
    results=[]
    # Exigencia comercial: Eldorado SOMENTE nao pode ser aprovado sem 23/23.
    # Demais mapas mantem o comportamento das versoes aprovadas.
    if require_complete is None:
        require_complete=(list(inputs["maps"])==["Eldorado"])
    # FASE 2: construir apenas mapas selecionados em staging.
    publish_dir=outdir
    staging=tempfile.TemporaryDirectory(prefix="company_staging_",dir=publish_dir)
    outdir=Path(staging.name)
    try:
        for name,path in inputs["maps"].items():
            log("Gerando Company de "+name+"...")
            companies,count=checked_maps[name]
            local_warnings=list(warnings)
            work={};evidence=[];bycargo={}
            for n,(category,title) in MANIFEST.items():
                id=f"carga{n}"
                outs=[];ins=[]
                for c in companies.values():
                    for direction,results_list in (("out",outs),("in",ins)):
                        why=(eldorado_permit(c,category,direction)
                             if name.lower()=="eldorado"
                             else permits(c,category,direction))
                        if why:results_list.append(c.name)
                        if why:evidence.append({"empresa":c.name,"setor":c.role,
                            "classificacao_explicita":c.explicit_role,"direcao":direction,
                            "carga":id,"categoria":category,"justificativa":why})
                bycargo[id]={"nome":title,"origens":len(outs),"destinos":len(ins),
                             "origens_lista":outs,"destinos_lista":ins}
                # Nao inventar rotas para completar 23/23.
                if not outs or not ins: local_warnings.append(f"{name} / {id}: sem cadeia economica completa (OUT={len(outs)}, IN={len(ins)})")
                for c_id in outs:work.setdefault(c_id,{"in":set(),"out":set()})["out"].add(id)
                for c_id in ins:work.setdefault(c_id,{"in":set(),"out":set()})["in"].add(id)
            coverage=coverage_audit(companies,bycargo,records,name)
            write_coverage_report(outdir,coverage)
            log(name+": COBERTURA "+str(coverage["cargas_com_rota"])+"/23 cargas.")
            for grade,stats in sorted(coverage["cobertura_por_carroceria"].items()):
                log("   "+grade+": "+str(stats["rotas_completas"])+"/"+
                    str(stats["total"])+" cargas com rota verificada")
            if require_complete and not coverage["pronto_para_gerar"]:
                report=write_coverage_report(publish_dir,coverage)
                gaps=[c["id"]+" ("+c["lacuna"]+")" for c in coverage["cargas"] if not c["rota_completa"]]
                (publish_dir/(name+"_COBERTURA_INCOMPLETA.txt")).write_text(
                    "GERACAO BLOQUEADA: "+str(coverage["cargas_com_rota"])+"/23 rotas verificadas.\n"+
                    "Nao gerar nem instalar uma Company incompleta em cliente.\n"+
                    "\n".join(gaps)+"\nConsulte "+report.name+" e respectivo CSV.\n"+
                    "Nao inventar empresas nem cargas sem evidencia na DEF.\n",
                    encoding="utf-8")
                raise ValueError(name+": somente "+str(coverage["cargas_com_rota"])+
                    "/23 cargas com origem e destino distintos. Nao foi gerado SCS. "+
                    "Abra "+report.name+" e "+name+"_COBERTURA_INCOMPLETA.txt "+
                    "para identificar empresas/setores que precisam revisao.")
            output_files={}
            for c in companies.values():
                for p,raw in c.editor_files.items():
                    output_files[p]=raw
                for p,raw in c.files.items():
                    output_files[p]=neutralize(raw,p)
            for cid,dirs in work.items():
                for direction in ("in","out"):
                    for id in dirs[direction]:
                        output_files[f"def/company/{cid}/{direction}/{id}.sii"]=cargo_sii(id)
            # As cargas precisam permanecer disponiveis: retirar exigencia injustificada
            # de skill somente no mod complementar; originais NUNCA sao editados.
            for n in MANIFEST:
                id=f"carga{n}"
                record=records[id]
                if id=="carga16":
                    # Baixa frequencia, independentemente da opcao de habilidade.
                    output_files[record["path"]]=cargo_override(record,drop_skill=fix_skills)
                elif fix_skills and record["valuable"]:
                    output_files[record["path"]]=re.sub(
                        r'(?im)^(\s*valuable\s*:\s*)true\b',r'\1false',
                        read_sii(record["raw"])).encode("utf-8")
            dest=outdir/("ETS2_"+name.upper().replace(" ","_")+"_COMPANY.scs")
            with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                for p,raw in sorted(output_files.items()):
                    entry=zipfile.ZipInfo(p,date_time=(2020,1,1,0,0,0))
                    entry.external_attr=0o644<<16
                    z.writestr(entry,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
            with zipfile.ZipFile(dest) as z:
                if z.testzip() is not None:raise ValueError("Falha na integridade do ZIP: "+str(dest))
                paths=set(z.namelist())
                if not all(p in paths for c in companies.values() for p in c.files):
                    raise ValueError("Arquivo original IN/OUT ficou sem cobertura: "+str(dest))
                for c in companies.values():
                    for p,raw in c.editor_files.items():
                        if p not in paths or z.read(p)!=raw:
                            raise ValueError("Arquivo editor original nao foi preservado: "+p)
                for id,info in bycargo.items():
                    for company in info["origens_lista"]:
                        if f"def/company/{company}/out/{id}.sii" not in paths:raise ValueError("Permissao OUT ausente")
                    for company in info["destinos_lista"]:
                        if f"def/company/{company}/in/{id}.sii" not in paths:raise ValueError("Permissao IN ausente")
            rows=[]
            for cid,c in sorted(companies.items()):
                selected=work.get(cid,{"in":set(),"out":set()})
                rows.append({"empresa":cid,"setor":c.role,"in_novos":",".join(sorted(selected["in"])),
                             "out_novos":",".join(sorted(selected["out"])),"in_originais":",".join(sorted(c.old_in)),
                             "out_originais":",".join(sorted(c.old_out))})
            # Sinalizar comportamentos anormais existentes na DEF original.
            # Um OUT original invalido NAO pode justificar nova expedicao.
            grade_baixa_rejeitados=[]
            for company in companies.values():
                observed=product_types(company.old_out)
                for cat in ("bobina","cimento","granito","tijolo"):
                    if cat not in observed:continue
                    if (eldorado_permit(company,cat,"out") if name.lower()=="eldorado"
                        else permits(company,cat,"out")) is None:
                        grade_baixa_rejeitados.append({
                            "empresa":company.name,"categoria":cat,
                            "papel_detectado":company.role,
                            "motivo":"OUT antigo incompativel com o setor; nao replicado"
                        })
            # Relatorio explica tambem rejeicoes de transportadoras, cultivos
            # especificos e nomes ingleses; sem reabrir a compatibilidade.
            eldorado_rejeicoes=[]
            eldorado_traducoes={}
            if name.lower()=="eldorado":
                for company in companies.values():
                    for direction,old_tokens in (("in",company.old_in),("out",company.old_out)):
                        for token in sorted(old_tokens):
                            identified=eldorado_translate({token})
                            eldorado_traducoes[token]=sorted(identified)
                        for category in sorted(eldorado_translate(old_tokens)):
                            if category not in {c for c,t in MANIFEST.values()}:
                                continue
                            if not eldorado_permit(company,category,direction):
                                eldorado_rejeicoes.append({
                                    "empresa":company.name,"setor":company.role,
                                    "direcao":direction,"familia":category,
                                    "motivo":("transportadora/centro generico nao e produtor nem comprador do produto"
                                      if company.role in {"transportadora","hub_generico"} else
                                      "incompatibilidade economica ou cultura nao demonstrada")
                                })
            data={"versao_gerador":VERSION,"mapa":name,"empresas":rows,
                  "cobertura_23_cargas":coverage,
                  "rejeicoes_eldorado":eldorado_rejeicoes,
                  "traducoes_ingles_portugues":eldorado_traducoes,
                  "rejeicoes_grade_baixa":grade_baixa_rejeitados,
                  "total_empresas":len(companies),"empresas_atendidas":len(work),
                  "arquivos_inout_originais":count,
                  "arquivos_editor_preservados":sum(len(c.editor_files) for c in companies.values()),
                  "arquivos_inout_gerados":sum(len(x["in"])+len(x["out"]) for x in work.values()),
                  "cadeias":bycargo,"evidencias":evidence,
                  "fontes_sha256":provenance+[{"arquivo":Path(path).name,"papel":"MAPA "+name,
                                              "sha256":hash_source(path)}],
                  "avisos":local_warnings,
                  "validacao":"SCS ZIP, caminhos IN/OUT, body_types; disponibilidade no ETS2 nao testada"}
            write_report(outdir,name,data)
            log(name+": "+str(len(companies))+" empresas, "+str(len(work))+" com cargas e "+
                str(data["arquivos_inout_gerados"])+" permissões.")
            results.append((name,str(publish_dir/dest.name),data))
        outdir.joinpath("LEIA_PRIMEIRO.txt").write_text(
            "ETS2 COMPANY LOGISTICS - GERADOR OFFLINE\n\n"+
            "1. Utilize somente a Company do mapa ativo.\n"+
            "2. Mantenha o mod principal do Librelato ativo.\n"+
            "3. Desative DEF Company 1 e DEF Company 2 antigas, quando forem complementos conflitantes.\n"+
            "4. Deixe o novo SCS acima das DEFs do mapa e do reboque.\n"+
            "5. Teste carrocerias Grade Alta e Grade Baixa e atualize economia.\n"+
            "6. O Mercado de Cargas de reboque PROPRIO exige carroceria e configuracao correspondente.\n"+
            "7. Se o mercado ficar vazio, anexe game.log.txt e dados da configuracao instalada.\n"+
            "ATENCAO: analise estatica nao prova ofertas no jogo.\n\n"+
            "\n".join(warnings),encoding="utf-8")
            # Apenas publicar apos TODOS os SCS serem gerados e validados.
        for generated in sorted(outdir.iterdir()):
            if generated.is_file():
                os.replace(generated,publish_dir/generated.name)
        log("PUBLICACAO CONCLUIDA: "+str(len(results))+
            " mapa(s) selecionado(s), relatorios e SCS verificados.")
    finally:
        staging.cleanup()
    return results

def run_gui():
    import tkinter as tk
    from tkinter import filedialog,messagebox,ttk
    root=tk.Tk()
    root.title("ETS2 Company Logistics Ultimate — Auditor e Gerador Offline v2.5")
    root.geometry("1080x880")
    root.minsize(950,730)
    style=ttk.Style(root)
    if "clam" in style.theme_names():style.theme_use("clam")
    style.configure("Main.TButton",font=("Segoe UI",10,"bold"),padding=(14,10))
    frame=ttk.Frame(root,padding=16)
    frame.pack(fill="both",expand=True)
    ttk.Label(frame,text="ETS2 | Company Logistics — Librelato",font=("Segoe UI",17,"bold")).pack(anchor="w")
    ttk.Label(frame,text="v2.5  ·  NOVO: auditar e corrigir suas Companies SCS existentes",
              font=("Segoe UI",10)).pack(anchor="w",pady=(2,6))
    ttk.Label(frame,text="Leia primeiro: sem validacao dentro do jogo, nao trate um SCS como entrega homologada.",
              font=("Segoe UI",9)).pack(anchor="w",pady=(0,12))
    widgets={}
    fields=[
       ("mod","Mod principal Librelato (.scs)"),
       ("def1","DEF Company 1 original (.scs)"),
       ("def2","DEF Company 2 original (.scs)"),
       ("txt","TXT com as 23 cargas"),
       ("minas","Mapa Minas Gerais (.zip)"),
       ("eldorado","Mapa Eldorado (.zip)"),
       ("rbr","Mapa RBR (.zip)"),
       ("existing_eldorado","Company EXISTENTE do Eldorado (.scs)"),
       ("existing_minas","Company EXISTENTE Minas Gerais (.scs)"),
       ("existing_rbr","Company EXISTENTE RBR (.scs)"),
       ("output","Pasta de saida")
    ]
    controls=[]
    for key,label in fields:
        row=ttk.Frame(frame);row.pack(fill="x",pady=3)
        ttk.Label(row,text=label,width=32).pack(side="left")
        value=tk.StringVar();widgets[key]=value
        ttk.Entry(row,textvariable=value).pack(side="left",fill="x",expand=True,padx=7)
        def choose(k=key,v=value):
            p=filedialog.askdirectory(title="Selecione a pasta de resultados") if k=="output" else (
                filedialog.askopenfilename(title="Selecione "+k))
            if p:v.set(p)
        bt=ttk.Button(row,text="Selecionar",command=choose)
        bt.pack(side="right")
        controls.append(bt)
    config_dir=Path(os.environ.get("APPDATA",str(Path.home())))/"ETS2_Company_Logistics"
    config_file=config_dir/"preferencias_v2.json"
    try:
        saved=json.loads(config_file.read_text(encoding="utf-8"))
        for k in widgets:
            value=saved.get(k,"")
            if value and Path(value).exists():widgets[k].set(value)
    except (OSError,ValueError,TypeError):pass
    scope_var=tk.StringVar(value="eldorado")
    scope_row=ttk.LabelFrame(frame,text="Quais Companies deseja atualizar?",padding=8)
    scope_row.pack(fill="x",pady=(8,4))
    ttk.Radiobutton(scope_row,text="Somente ELDORADO — manter Minas Gerais e RBR intactos",
                    variable=scope_var,value="eldorado").pack(anchor="w")
    ttk.Radiobutton(scope_row,text="Todos os 3 mapas — executar gerador para MG, Eldorado e RBR",
                    variable=scope_var,value="todos").pack(anchor="w")
    audit_mode=tk.StringVar(value="corrigir")
    audit_row=ttk.Frame(frame);audit_row.pack(fill="x",pady=(3,1))
    ttk.Radiobutton(audit_row,text="Auditar e corrigir SCS EXISTENTE (preserva o original)",
                    variable=audit_mode,value="corrigir").pack(side="left",padx=(0,14))
    ttk.Radiobutton(audit_row,text="Apenas auditar, sem gerar SCS",
                    variable=audit_mode,value="auditar").pack(side="left")
    options_row=ttk.Frame(frame);options_row.pack(fill="x",pady=(4,4))
    fix_var=tk.BooleanVar(value=False)
    ttk.Checkbutton(options_row,text="Opcional: remover restricao de Carga de Alto Valor dos cargos comuns (apenas no SCS gerado)",
                    variable=fix_var).pack(anchor="w")
    ttk.Label(options_row,text="As rotas sao inferidas a partir das DEFs; nenhuma cadeia sem origem/destino e inventada.",
              font=("Segoe UI",9)).pack(anchor="w")
    progress=ttk.Progressbar(frame,mode="indeterminate")
    progress.pack(fill="x",pady=(6,4))
    status=tk.StringVar(value="Pronto. Selecione os arquivos ou gere um diagnostico primeiro.")
    ttk.Label(frame,textvariable=status,wraplength=900).pack(anchor="w")
    console=tk.Text(frame,height=12,wrap="word",state="disabled",font=("Consolas",9))
    console.pack(fill="both",expand=True,pady=7)
    actions=ttk.Frame(frame);actions.pack(fill="x",pady=6)
    work_queue=queue.Queue()
    busy=[False]
    def append_log(message):
        console.configure(state="normal")
        console.insert("end",str(message)+"\n")
        console.see("end");console.configure(state="disabled")
    def persist():
        try:
            config_dir.mkdir(parents=True,exist_ok=True)
            config_file.write_text(json.dumps({k:v.get() for k,v in widgets.items()},indent=2),
                                   encoding="utf-8")
        except OSError as exc:
            append_log("Aviso: nao consegui salvar os caminhos: "+str(exc))
    def check_paths(include_librelato):
        required=(
            ["mod","def1","def2","txt","eldorado"] if scope_var.get()=="eldorado"
            else ["mod","def1","def2","txt","minas","eldorado","rbr"])
        if include_librelato=="audit":
            required=(["eldorado","existing_eldorado"] if scope_var.get()=="eldorado" else
                      ["minas","eldorado","rbr","existing_minas",
                       "existing_eldorado","existing_rbr"])
        elif not include_librelato:required=["minas","eldorado","rbr"]
        needed=required+["output"]
        missing=[k for k in needed if not widgets[k].get().strip()]
        if missing:raise ValueError("Selecione os campos: "+", ".join(missing))
        invalid=[k for k in required if not Path(widgets[k].get()).exists()]
        if invalid:raise ValueError("Arquivo ou pasta inexistente: "+", ".join(invalid))
    def change_busy(value):
        busy[0]=value
        for c in controls+[btn_diag,btn_generate,btn_audit]:
            c.configure(state="disabled" if value else "normal")
        if value:progress.start(12)
        else:progress.stop()
    def worker_generate(snapshot,fix,scope):
        try:
            txt=Path(snapshot["txt"]).read_text(encoding="utf-8-sig")
            for n in MANIFEST:
                if not re.search(r"(?m)^\s*carga"+str(n)+r"\s*[:=\-]",txt,re.I):
                    raise ValueError("TXT incompleto: falta carga"+str(n))
            if scope=="eldorado":
                # MG e RBR nao sao lidos, regenerados nem sobrescritos.
                maps={"Eldorado":snapshot["eldorado"]}
            else:
                maps={"Minas_Gerais":snapshot["minas"],
                      "Eldorado":snapshot["eldorado"],"RBR":snapshot["rbr"]}
            inp={"mod":snapshot["mod"],"def1":snapshot["def1"],
                 "def2":snapshot["def2"],"maps":maps}
            work_queue.put(("log","Escopo escolhido: "+", ".join(maps)))
            items=generate(inp,snapshot["output"],
                           log=lambda msg:work_queue.put(("log",msg)),fix_skills=fix)
            work_queue.put(("success","Gerados "+str(len(items))+
                " arquivos SCS. Audite os JSON/CSV e valide no ETS2 antes de entregar."))
        except Exception as exc:
            work_queue.put(("error",str(exc)))
    def worker_audit(snapshot,scope,mode):
        try:
            import auditor_existentes
            entries=({"Eldorado":{"existing":snapshot["existing_eldorado"],
                                   "map_def":snapshot["eldorado"]}} if scope=="eldorado" else
                     {"Minas_Gerais":{"existing":snapshot["existing_minas"],
                                     "map_def":snapshot["minas"]},
                      "Eldorado":{"existing":snapshot["existing_eldorado"],
                                  "map_def":snapshot["eldorado"]},
                      "RBR":{"existing":snapshot["existing_rbr"],
                             "map_def":snapshot["rbr"]}})
            work_queue.put(("log","AUDITORIA de Companies existentes: "+
                            ", ".join(entries)+" | modo="+mode))
            results=auditor_existentes.run(sys.modules[__name__],entries,snapshot["output"],
                          mode=mode,log=lambda msg:work_queue.put(("log",msg)))
            total_pending=sum(x["pendencias_revisao"] for x in results)
            work_queue.put(("success",
                str(len(results))+" Company(s) examinada(s). "+
                str(total_pending)+" ocorrencias requerem revisao. "+
                ("Corrigida(s) em arquivos NOVOS; originais preservados. " if mode=="corrigir" else
                 "Nenhum SCS gerado. ")+
                "Confira AUDITORIA_*.json e .csv ANTES de entregar ao cliente."))
        except Exception as exc:
            work_queue.put(("error",str(exc)))

    def worker_diagnostic(snapshot):
        try:
            out=Path(snapshot["output"])
            for key in ("minas","eldorado","rbr"):
                p=export_diagnostic(snapshot[key],out)
                work_queue.put(("log",key+": diagnostico salvo em "+str(p)))
            work_queue.put(("success","Diagnosticos dos 3 mapas exportados. "+
                            "Envie o JSON do Eldorado para investigar a estrutura real."))
        except Exception as exc:
            work_queue.put(("error","Falha no diagnostico: "+str(exc)))
    def run(action):
        if busy[0]:return
        try:
            check_paths(include_librelato=("audit" if action=="audit" else action=="generate"))
            persist()
            snapshot={k:v.get() for k,v in widgets.items()}
            change_busy(True)
            status.set("Analisando arquivos; aguarde...")
            if action=="generate":
                fun=worker_generate
                args=(snapshot,fix_var.get(),scope_var.get())
            elif action=="audit":
                fun=worker_audit
                args=(snapshot,scope_var.get(),audit_mode.get())
            else:
                fun=worker_diagnostic
                args=(snapshot,)
            threading.Thread(target=fun,args=args,daemon=True).start()
        except Exception as exc:
            messagebox.showerror("Campos incompletos",str(exc))
    def pump():
        try:
            while True:
                event,value=work_queue.get_nowait()
                if event=="log":
                    append_log(value)
                    status.set(str(value)[:160])
                elif event in ("error","success"):
                    change_busy(False)
                    status.set("Concluido" if event=="success" else "Interrompido sem validar os 3 mapas.")
                    append_log(("CONCLUIDO: " if event=="success" else "ERRO: ")+value)
                    (messagebox.showinfo if event=="success" else messagebox.showerror)(
                        "Processamento concluido" if event=="success" else "Processamento interrompido",
                        value)
        except queue.Empty:
            pass
        root.after(125,pump)
    btn_diag=ttk.Button(actions,text="1. DIAGNOSTICAR OS 3 MAPAS",
                        command=lambda:run("diagnostic"),style="Main.TButton")
    btn_diag.pack(side="left",padx=(0,8))
    btn_generate=ttk.Button(actions,text="2. GERAR COMPANY(S) SELECIONADA(S)",
                            command=lambda:run("generate"),style="Main.TButton")
    btn_generate.pack(side="left",padx=6)
    btn_audit=ttk.Button(actions,text="3. AUDITAR / CORRIGIR SCS EXISTENTE",
                         command=lambda:run("audit"),style="Main.TButton")
    btn_audit.pack(side="left",padx=6)
    def open_folder():
        p=widgets["output"].get()
        if not p or not Path(p).is_dir():
            messagebox.showwarning("Pasta indisponivel","Selecione primeiro uma pasta de saida.")
            return
        if sys.platform=="win32":os.startfile(p)
    ttk.Button(actions,text="Abrir pasta de saida",command=open_folder).pack(side="right")
    root.after(125,pump)
    root.mainloop()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--cli",action="store_true")
    parser.add_argument("--only-eldorado",action="store_true",
                        help="Gerar apenas Eldorado; nao abrir nem alterar os mapas MG/RBR")
    parser.add_argument("--audit-existing",action="store_true",
                        help="Auditar/corrigir Company SCS existente sem regenerar do zero")
    parser.add_argument("--audit-only",action="store_true",
                        help="Gerar somente relatorio de auditoria, sem .scs corrigido")
    for x in ("mod","def1","def2","txt","minas","eldorado","rbr",
              "existing-eldorado","existing-minas","existing-rbr","output"):
        parser.add_argument("--"+x,required=False)
    args=parser.parse_args()
    if not args.cli:run_gui();return
    if args.audit_existing:
        import auditor_existentes
        needed=(("eldorado","existing_eldorado","output") if args.only_eldorado
                else ("minas","eldorado","rbr","existing_minas",
                      "existing_eldorado","existing_rbr","output"))
        missing=[k for k in needed if not getattr(args,k)]
        if missing:parser.error("Auditoria exige: "+", ".join(missing))
        jobs=({"Eldorado":{"existing":args.existing_eldorado,"map_def":args.eldorado}}
              if args.only_eldorado else
              {"Minas_Gerais":{"existing":args.existing_minas,"map_def":args.minas},
               "Eldorado":{"existing":args.existing_eldorado,"map_def":args.eldorado},
               "RBR":{"existing":args.existing_rbr,"map_def":args.rbr}})
        auditor_existentes.run(sys.modules[__name__],jobs,args.output,
                              mode="auditar" if args.audit_only else "corrigir",log=print)
        return
    required=("mod","def1","def2","txt","eldorado","output") if args.only_eldorado else (
        "mod","def1","def2","txt","minas","eldorado","rbr","output")
    if any(getattr(args,x) is None for x in required):
        parser.error("Em modo --cli, informe: "+", ".join(required))
    original=Path(args.txt).read_text(encoding="utf-8-sig")
    for n in MANIFEST:
        if not re.search(r"(?m)^\s*carga"+str(n)+r"\s*[:=\-]",original,re.I):
            parser.error(f"TXT incompleto: falta carga{n}")
    maps=({"Eldorado":args.eldorado} if args.only_eldorado else
          {"Minas_Gerais":args.minas,"Eldorado":args.eldorado,"RBR":args.rbr})
    inp={"mod":args.mod,"def1":args.def1,"def2":args.def2,"maps":maps}
    generate(inp,args.output,print)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("ERRO:",exc,file=sys.stderr);sys.exit(1)
