"""Politica economica auditavel para cargas do Librelato (ETS2).

Nao conclui atividade a partir de OUT corrompido. A funcao evaluate
responde do ponto de vista de quem precisa da carga (comprador) e de
quem de fato pode fornecela (produtor/revenda/armazenagem).
Somente biblioteca padrao, offline, deterministica.
"""
from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

VERSION="3.0"
ROLES=(
    # Atividades verificaveis pelo nome da unidade e pelos fluxos originais:
    # Posto de combustivel e mineracao de brita/calcario nao sao silos
    # produtores de milho, algodao ou coco.
    ("posto_combustivel",r"petrobras|posto_?combust|fuel_station|gas_station|^posto_?ipiranga$|^auto_?posto(?:_|$)|^posto_(?!policial|prf|fiscal)"),
    ("mineracao_minerios",r"mineracao|mineradora|^minerita|mine_ore|iron_ore_mine"),
    ("usina_acucar",r"usina_?acucar|sugar_mill|sugar_plant|engenho_?acucar"),
    ("terminal_portuario",r"^porto[0-9]+$|^portosant[0-9]+$|^portosebas[0-9]*$|^pr_porto(?:_pr)?$|^sc_porto(?:_|$)|^porto_?terminal$"),
    ("transportadora",r"transport|transpor|transp|logistic|logistica|logist|freight|carrier|haulage|brasilog|braslog|rasador|avant|cmm_transport|cmm_transp|ttr_?log|^trame2$|^trade2$|^stokes2$|^posped2$|(?:^|_)translov|(?:^|_)multlog$|(?:^|_)jampalog$|(?:^|_)tvslog$|^go_alfa_tr$"),
    ("bananal",r"bananal|banana_farm|banana_plantation|fazenda_banana|^eldorado_bananas$|^bana_farm"),
    ("fazenda_batata",r"(?:fazenda|faz|farm|plantacao|cultivo).*?(?:batata|potato)|(?:batata|potato).*?(?:fazenda|farm|plantacao)"),
    ("fazenda_laranja",r"(?:fazenda|faz|farm|plantacao|cultivo).*?(?:laranja|orange|citrus)|(?:laranja|orange|citrus).*?(?:fazenda|farm|plantacao)"),
    # Cadeias adicionais observadas no relatório real RBR: setores por
    # nome publicamente exibido e marcas documentadas, nao por "agro"
    # generico ou outras palavras ambiguas.
    # RBR: atividades verificadas na DEF e em materiais dos fabricantes.
    # A classificacao nao inclui automaticamente o produto final da
    # industria, que pode nem existir nas 24 cargas disponiveis.
    ("revenda_fertilizante",r"^agromecvo$"),
    ("processadora_citricos",r"^citrosuco[12]?$|^frucamp$"),
    ("fabrica_paineis",r"^greenplac$"),
    ("fabrica_fibrocimento",r"^eternit$"),
    ("revenda_madeiras",r"^go_madeirani$|^go_madesaba$|^made_itaja$|^madei_rdoce$|^madereira(?:[1237]|se|vo)$|^ms_vale_mad$|^mt_cia_madei$|^pr_mademape$"),
    ("revenda_aco",r"^br_ferro$|^mt_ferro_aco$|^udiaco$|^itaacos$"),
    ("plantacao_cana",r"^cana_acucar2?$|^cana_agu$|^cana_ms1$|^usina_cana$"),
    ("infra_passageiros",r"^rodoviaria\d*$|^rodo_(?:bh|go\d+|mg\d+|ms\d+|mt\d+)$|^pr_rodo$|^sc_rodo_(?:gar|ita|join|pic)$|^aero_rverde$|^prf_nlima$|^enel_(?:acreu|india|stb)$"),
    ("entreposto_hortigraos",r"^ceagesp$"),
    ("fabricante_fertilizante",r"^mosaico2?$|^mosaic_fertilizantes$"),
    ("beneficiadora_algodao",r"algodoeira|cotton_gin|^mt_torre_alg$|^ms_alg_ib$"),
    ("fabrica_moveis",r"marcenaria|furniture_factory|furniture_plant|moveis|^bechara$|^brigatto$|^esplane$"),
    ("comercio_graos",r"(?:^|_)graos(?:_|$)|^grupo_cereal$|^g_cereal_(?:rv|stb)$|^pr_anaconda$|^amaggi$"),
    ("concreteira",r"^polimix(?:1|_rib)?$|^concretar$|concreto_usinado|concrete_batch"),
    # CSN Arcos na DEF MG descreve extracao de calcario/brita, nao
    # uma unidade expedidora de bobinas nem de granito ornamentado.
    # Fonte externa: csn.com.br/quem-somos/grupo-csn/unidades-fabris-csn/
    ("mineracao_calcario",r"^csnarcos(?:[234])?$"),
    ("revenda_agricola_documentada",r"^casabatata$"),
    ("distribuidor_cerveja",r"^jmbebidas$"),
    ("siderurgica",r"gerdau|cofer|usiminas|arcelor|^csn(?:_|$)|steel_mill|steelworks|siderurg|sider[ _]"),
    ("automotiva_fabrica",r"^(?:fiat|fca|vw|volkswagen|gm|hyundai|toyota|renault|ford|honda|bmw)(?:_|$)|montadora|automotive_plant|car_factory"),
    ("maquinas",r"^mc_?equip|^mcequip|maquinas|maquinario|machinery|equipment_factory"),
    ("cimenteira",r"votoran|intercement|cimenteira|cement_plant|cement_factory|^globcement2?$"),
    ("premoldados",r"carmoprem|premold|pre_mold|precast|concrete_products"),
    ("cervejaria",r"ambev|heineken|brahma|cervejaria|brewery|brewing|beer_factory|^grupo_petropolis$|^grupo_p2?$|^cercrystal$|^cerveja_crystal$"),
    ("reciclagem",r"recicl|sucata|sucatao|ferro_velho|ferrovelho|scrapyard|recycling_yard"),
    ("ceramica",r"ceramica|^ceramfazpgra$|^cerami_para(?:2|p)$|olaria|brickyard|brick_factory|tijolaria"),
    ("pedreira",r"pedreira|quarry|rock_quarry|extratora"),
    ("marmoraria",r"marmoraria|^marmolider$|marmor|granito|granite_shop|stoneworks"),
    ("madeireira",r"madeireira|^madereira$|^araraserr$|^extrmadserr$|serraria|sawmill|timber_mill|lumberyard|serrac|^madeiras(?:[0-9]+)?$|^extrmadeira$|^betimmadeira$|^samirmadeira$|^extr_rio_p2$|^extracao2$|^extracao_sc$"),
    ("fabrica_racao",r"racao_fabrica|fabrica_racao|feedmill|feed_mill|animal_feed_factory|nutricao_animal|brejeiro|^nutrition$|^trouw_nutrition$"),
    ("revenda_racao",r"^raguife$|^curralracoes$|(?:^|_)racoes(?:_|$)|feed_store|loja_racao"),
    ("agroinsumos",r"agropec|agroinsum|agro_supply|fertiliz|adubo|agrocenter|^agrish|^agroce|^agromais|casa_adubo|^cimoagro$"),
    ("silo",r"silo|armazem|armazens|armz|grain_elevator|grain_storage|cerealista|caramuru"),
    ("cooperativa",r"cooper|coamo|^coop|camda|comigo"),
    ("pecuaria",r"pecuar|gado|cattle|livestock|poultry_farm|suino|criatorio|feedlot|confinamento"),
    ("fazenda",r"fazenda|^faz_|^faze_|(?:^|_)faz_|^faz(?:bale|boa|brejo|cerra|grao|irmas|pedra|pit|sao|serena|serra|sp|sbene|pg)|^farm|_farm|plantacao|farming|agricultural_farm|agric"),
    ("textil",r"textil|tecel|fiacao|cotton_mill|textile|spinning_mill"),
    ("metalurgica",r"metalurg|calha|cortedobra|metalworks|sheetmetal|usinagem|^itcc2?$|^marcegaglia$"),
    ("materiais",r"materiais|(?:^|_)(?:material|materiais)(?:_|$)|^material(?:ber|se1)$|mat_constr|material_constr|loja_material|building_supplies|hardware_store|building_materials|construm|construsol|dep_mat|^material_|^leroy_merlin$|^pinheiralvo$|^depo_(?:bh|cacu)$"),
    ("obras",r"construcao|construction_site|building_site|obra_|^obra|canteiro|batisse|^abcconstru$|^construai2$|^const(?:bd|carmopo|divi|juatub[12]|oliveir|pains|pminas|postoju)$|^constru(?:ca|sc|aco|ai|betim|cana|cb|fer|lavra|sar)$|^sanbuilders2?$|^konstnr(?:_hs)?2?$|^eldconst2?$|^cons_rbr$|^const_c_g$|^coluna_ma$"),
    ("supermercado",r"supermercado|super_mercado|supermarket|grocery|atacadao|assai|bahamas|carrefour|^martmix$|^villefort$|^hipermax$|^walmart$|^spani$|^shibata_ca$|^kaarfor2?$|^sellplan2?$|^pr_samsclub$|^mt_mer_reti$|^extra_|compr_bem|^compre_bem$|^martminas$|^martmina_c$|^super(?:abc|bh|eli|josyldo|oliveir)$|^merc(?:ado(?:kril|_ac)?|_[a-z0-9_]+)$|^pr_mercado$|^sc_mercado$"),
    ("hortifruti",r"ceasa|hortif|sacolao|fruit_warehouse|fresh_produce|produce_market|frutaria"),
    ("alimentos",r"industria_alim|food_processing|cannery|conservas|^arcor"),
    ("distribuidor",r"atacad|wholesale|distribuidor|distrib_fruit|distrib_|^distrbebidas$"),
)
# Nem "banana" generica, nem "carro" generico, nem "agro" sozinho
# identificam automaticamente a empresa; todos podiam causar erros.
CROP_CLASSES={"milho","soja","sorgo","batata","laranja","algodao","coco"}
GRAIN_CLASSES={"milho","soja","sorgo"}
BUILDING_CLASSES={"cimento","tijolo","madeira","granito"}
CATEGORIES={
    "milho","soja","adubo","madeira","algodao","cimento","batata","laranja",
    "bobina","cerveja","tijolo","granito","palete","racao","sorgo","coco"
}
# Alias de ID original da DEF (EN/PT); nao transformar bebidas gerais em cerveja.
ALIASES={
    "milho":r"milho|corn|maize",
    "soja":r"soja|soybean|soybeans|soya",
    "sorgo":r"sorgo|sorghum",
    "adubo":r"adubo|fertilizer|fertilizers|fertiliser|fertilisers|fertilizante|fertilizantes|npk|ureia|urea",
    "batata":r"batata|batatas|potato|potatoes",
    "laranja":r"laranja|laranjas|orange|oranges|citrus",
    "coco":r"coco|cocos|coconut|coconuts",
    "algodao":r"algodao|cotton|cotton_bales|pluma",
    "madeira":r"madeira|madeirase|madeirase_b|troncos|wood|wooden_planks|logs|timber|lumber",
    "cimento":r"cimento|cement|cement_bags|bagged_cement",
    "tijolo":r"tijolo|tijolos|brick|bricks|clay_bricks",
    "granito":r"granito|granite",
    "bobina":r"bobina|bobinas|steel_coil|steel_coils|steel_roll|coil_steel",
    "cerveja":r"cerveja|cervejas|beer|beers|lager|ale|amstel|brahma|budweiser|devassa|heineken|schin|skol|itaipava",
    "palete":r"palete|paletes|paletev|paletesv|pallet|pallets|wooden_pallets|empty_palet|empty_palets|empty_pallet|empty_pallets|supaletes",
    "racao":r"racao|animal_feed|livestock_feed|feedmeal|compound_feed|xerem",
}
# IDs das 24 mercadorias ORIGINAIS, usados somente como evidencia
# quando ja constam em IN/OUT da DEF autentica da empresa.
# A categoria nao e inferida pelo nome ambiguo (ex.: carga17 nao e laranja).
LIBRELATO_ID_CATEGORIES={
    "carga1":"milho", "carga2":"soja", "carga3":"adubo",
    "carga4":"madeira", "carga5":"algodao", "carga6":"cimento",
    "carga7":"batata", "carga8":"laranja", "carga9":"bobina",
    "carga10":"cimento", "carga11":"cimento", "carga12":"cerveja",
    "carga13":"tijolo", "carga14":"granito", "carga15":"granito",
    "carga16":"palete", "carga17":"racao", "carga18":"racao",
    "carga19":"racao", "carga20":"racao", "carga21":"soja",
    "carga22":"milho", "carga23":"sorgo", "carga24":"coco",
}
def norm(v):
    return "".join(ch for ch in unicodedata.normalize("NFKD",str(v).lower())
                   if not unicodedata.combining(ch)).replace("-","_").replace(" ","_")
def cargo_categories(tokens):
    found=set()
    for tok in tokens:
        tok=norm(tok)
        if tok in LIBRELATO_ID_CATEGORIES:
            found.add(LIBRELATO_ID_CATEGORIES[tok])
            continue
        for category,pattern in ALIASES.items():
            if re.fullmatch(r"(?:rbr_|ros_|cs_)?(?:"+pattern+r")(?:_[ab])?",tok):
                found.add(category)
    return found

@dataclass(frozen=True)
class Identity:
    role:str
    certainty:str
    evidence:str

# Inferencia conservadora de ATIVIDADE por fluxo documental (DEF original).
# "Graos" genericos ajudam a reconhecer agricultura, mas nao comprovam
# que a cultura seja milho, soja ou sorgo: OUT dessas cargas exige especie.
GENERIC_GRAIN=re.compile(
    r"^(?:grao|graos|cereal|cereais|grain|grains|bulk_grain|bulk_grains)$"
)
AGRICULTURE_INCOMPATIBLE={
    "cimento","bobina","cerveja","tijolo","granito","madeira","palete"
}
RETAIL_FOOD={"cerveja","batata","laranja","coco"}

def _any_evidence(tokens, pattern):
    """Reconhece itens fora das 24 cargas, mas apenas como indício do setor."""
    return any(re.fullmatch(pattern, norm(value)) for value in tokens)


def infer_by_flow(company):
    """Analisa cada empresa ficticia pela RELACAO DIRECIONAL IN/OUT da DEF.

    Nunca consulta empresas reais. Preferir o fluxo de materiais (insumo ->
    atividade -> produto), sem inventar especie de grao, fruta ou mineral.
    Sinais contraditorios impedem uma classificacao automatica.
    """
    incoming=cargo_categories(company.old_in)
    outgoing=cargo_categories(company.old_out)
    in_names={norm(x) for x in company.old_in}
    out_names={norm(x) for x in company.old_out}
    grains_out=outgoing & GRAIN_CLASSES
    grains_in=incoming & GRAIN_CLASSES
    crops_out=outgoing & CROP_CLASSES
    crops_in=incoming & CROP_CLASSES
    grain_generic_out=any(GENERIC_GRAIN.fullmatch(t) for t in out_names)
    grain_generic_in=any(GENERIC_GRAIN.fullmatch(t) for t in in_names)
    other_out=outgoing - CROP_CLASSES

    # RBR: extração de madeira usa colheitadeiras florestais Ponsse no
    # recebimento e expede troncos. Não é fábrica de ração nem fazenda de
    # grãos. Vários IDs fictícios (extracao_ju/sb) usam exatamente o fluxo.
    if (_any_evidence(in_names,r"(?:ponsse(?:[0-9]+)?|harvester_?forest|forest_?machine)")
            and _any_evidence(out_names,r"(?:troncos(?:_di)?|logs|timber|madeirase(?:_b)?)")
            and not (outgoing - {"madeira"})):
        return Identity("madeireira","alta",
                        "fluxo florestal: colheitadeira Ponsse no IN e "
                        "troncos/madeira no OUT original da DEF")

    # Empresas de logística podem movimentar muitos setores sem
    # fabricar todos os produtos. Exigir diversidade inequívoca e
    # mercadorias documentadas nos dois sentidos.
    all_cats=incoming|outgoing
    if (len(all_cats)>=5 and len(incoming)>=4 and len(outgoing)>=4
            and (all_cats & GRAIN_CLASSES)
            and (all_cats & (BUILDING_CLASSES|{"bobina"}))
            and (all_cats & (RETAIL_FOOD|{"racao","adubo"}))):
        return Identity("centro_logistico_inferido","alta",
                        "fluxo multi-setorial de armazenagem/transbordo: "
                        "diversas mercadorias de setores diferentes IN e OUT; "
                        "nao confirma fabricacao de nenhuma delas")

    # Industria madeireira/extração de madeira: receber troncos, expedir
    # moveis. Um nome ficticio "extracao1" NAO indica cultivo de graos.
    if (("madeira" in incoming or
         _any_evidence(in_names,r"(?:troncos|madeirase(?:_b)?|logs|timber)"))
         and _any_evidence(out_names,r"(?:moveis?|furniture|furniture_items)")
         and not outgoing):
        return Identity("fabrica_moveis","alta",
                        "troncos/madeira no IN e moveis no OUT documentados")

    # Extracao mineral: carregadeiras, escavadeiras, brita, areia, minério.
    # Minerio nao equivale a bobina e brita nao equivale a granito.
    if (_any_evidence(out_names,
                      r"(?:rbr_)?(?:brita|calcario|cascalho|areia|minerio|ore|gravel|limestone)")
        and not (outgoing & CATEGORIES)):
        return Identity("mineracao_minerios","alta",
                        "minerais brutos documentados no OUT, sem carga "
                        "granito ou bobina comprovada")

    # Reposição agrícola e comércio: IN/OUT adubo e expedição de ração,
    # sem colheita. Não classificar como lavoura só por "agrícola".
    if ({"adubo"} <= incoming and {"adubo","racao"} <= outgoing
            and not (outgoing & CROP_CLASSES)):
        return Identity("agroinsumos","alta",
                        "adubo em IN/OUT, racao no OUT e nenhuma colheita "
                        "documentada: atividade de comercializacao")

    # Cadeias industriais: materia-prima recebida E produto expedido.
    # Identificador ficticio (empresa_x7) nao impede inferencia.
    if ("racao" in outgoing and grains_in and
            "racao" not in incoming and not (other_out - {"racao"})):
        return Identity("fabrica_racao_inferida","alta",
                        "fluxo industrial: cereais no IN e racao no OUT da DEF")
    if ("cimento" in outgoing and
            _any_evidence(in_names,r"(?:calcario|limestone|clinker|argila_calcaria)")
            and not (other_out - {"cimento"})):
        return Identity("cimenteira_inferida","alta",
                        "fluxo industrial: calcario/clinker no IN e cimento no OUT")
    if ("tijolo" in outgoing and
            _any_evidence(in_names,r"(?:argila|clay|barro|ceramic_clay)")
            and not (other_out - {"tijolo"})):
        return Identity("ceramica_inferida","alta",
                        "fluxo industrial: argila no IN e tijolo no OUT")
    if ("laranja" in incoming and
            _any_evidence(out_names,r"(?:suco_?laranja|orange_juice|juice_orange)")
            and not (outgoing - {"laranja"})):
        return Identity("processadora_citricos","alta",
                        "fluxo industrial: laranja no IN e suco no OUT")
    if ("madeira" in incoming and
            _any_evidence(out_names,r"(?:moveis?|furniture|furniture_items)")
            and not (outgoing - {"madeira"})):
        return Identity("fabrica_moveis","alta",
                        "fluxo industrial: madeira no IN e moveis no OUT")
    if ("algodao" in incoming and
            _any_evidence(out_names,r"(?:tecido|tecidos|fabric|fabrics|fio|fios|yarn)")
            and not (outgoing - {"algodao"})):
        return Identity("textil","alta",
                        "fluxo industrial: algodao no IN e tecido/fio no OUT")
    if ("racao" in incoming and
            _any_evidence(out_names,r"(?:gado|boi|bois|cattle|suino|suinos|pig|pigs|porco|porcos|livestock)")
            and not (outgoing - {"racao"})):
        return Identity("pecuaria","alta",
                        "fluxo agropecuario: racao no IN e animais no OUT")

    # Compra e revenda de material de construcao documentados.
    # Loja inferida NAO gera cargas fora das especies que constam na DEF.
    materials_in=incoming & BUILDING_CLASSES
    materials_out=outgoing & BUILDING_CLASSES
    if (len(materials_in & materials_out)>=2 and
            not (incoming - BUILDING_CLASSES) and
            not (outgoing - BUILDING_CLASSES)):
        return Identity("comercio_materiais_inferido","alta",
                        "comercio: dois ou mais materiais da construcao "
                        "documentados nos dois sentidos da DEF")
    # Local que recebe diversos materiais sem revender: pode ser obra,
    # reforma ou industria; reconhecer somente a funcao de recebedor.
    if (len(materials_in)>=2 and not outgoing and
            not (incoming - BUILDING_CLASSES)):
        return Identity("consumidor_materiais_inferido","alta",
                        "unidade recebedora de materiais da construcao no IN, "
                        "sem evidencia de revenda ou fabricacao")

    # Fazenda ficticia de QUALQUER uma das culturas: milho, soja, sorgo,
    # batata, laranja, algodao ou coco. Producao exige OUT da especie
    # + fertilizante no IN e nenhuma entrada da propria colheita.
    # "graos" nao especifica especie: nao inventa milho/soja.
    if ("adubo" in incoming and (crops_out or grain_generic_out)
            and not (crops_in or grain_generic_in)
            and not (other_out or
                     (incoming & AGRICULTURE_INCOMPATIBLE))):
        detail=", ".join(sorted(crops_out)) or "graos sem especie"
        return Identity(
            "fazenda","alta",
            "inferencia economica: adubo no IN + "+detail+
            " no OUT original, sem entrada da colheita nem fluxo industrial; "
            "somente culturas nomeadas no OUT autorizam expedir carga"
        )
    # IN+OUT de cereais identificados indica comercio/armazenagem;
    # nao permite afirmar que a empresa produz a colheita.
    if (grains_out and grains_in and grains_out & grains_in
            and "adubo" not in incoming and
            not (outgoing - GRAIN_CLASSES)):
        return Identity(
            "comercio_graos","alta",
            "inferencia de comercio/armazenagem: mesmas especies de graos "
            "documentadas no IN e OUT; nao comprova producao agricola"
        )
    # Frutas, batata, algodao ou coco IN e OUT da mesma unidade:
    # revenda/entreposto, NAO prova de cultivo da mercadoria.
    # Restrito aos produtos documentados e a direcao original.
    if (crops_out & crops_in and
            not (outgoing - CROP_CLASSES) and
            not (incoming - CROP_CLASSES)):
        return Identity(
            "entreposto_agricola_inferido","alta",
            "fluxo de comercializacao: cultura identificada em IN e OUT; "
            "nenhuma evidencia de que a empresa cultive a colheita"
        )
    if ("adubo" in incoming and "adubo" in outgoing
            and not (outgoing - {"adubo"})):
        return Identity(
            "revenda_fertilizante","alta",
            "fertilizante registrado em IN e OUT; transacao comercial "
            "demonstrada, sem atribuir fabricacao"
        )
    # Empresa alimenticia ficticia: sem afirmar que e supermercado.
    if (len(incoming & RETAIL_FOOD)>=3 and
            not (outgoing - RETAIL_FOOD) and
            not (incoming & (AGRICULTURE_INCOMPATIBLE-RETAIL_FOOD))):
        return Identity(
            "comercio_alimentos_inferido","alta",
            "fluxo alimentar diversificado documentado na DEF, sem prova "
            "de que seja supermercado ou produtor"
        )
    return None

def classify(company):
    identifier=norm(company.name)
    # Empresas MG com identificadores abreviados: confirmar a especie
    # pela carga original antes de classificar. Nunca inventar colheita.
    if identifier=="batatfazpgra" and "batata" in cargo_categories(company.old_out):
        return Identity("fazenda_batata","alta",
                        "fazenda produtora + OUT batata documentado na DEF")
    if identifier=="araragrao" and (
            GRAIN_CLASSES & cargo_categories(company.old_in|company.old_out)):
        return Identity("comercio_graos","alta",
                        "comercio de graos + especie documentada na DEF")
    # Eldorado: rocasoja aparece expedindo soja na DEF original.
    # Sem OUT documental, nao presumir propriedade/colheita pelo ID.
    if identifier=="rocasoja" and "soja" in cargo_categories(company.old_out):
        return Identity("fazenda_soja","alta",
                        "identificador rocasoja + OUT soja no arquivo original")
    for role,pattern in ROLES:
        if re.search(pattern,identifier,re.I):
            return Identity(role,"alta","atividade pelo identificador de empresa "+company.name)
    # Nome publicamente exibido vem de company_permanent.name, NAO do
    # campo de uma carga nem de OUT potencialmente adulterado. Usar apenas
    # quando houver correspondencia inequívoca com UM setor.
    public_name=getattr(company,"display_name","")
    # RBR "fazenda_ac": o nome do editor declara ARMAZENAGEM DE GRAOS,
    # e ha as mesmas especies de graos IN/OUT. Nao inferir lavoura.
    public_name=getattr(company,"display_name","")
    in_grains=cargo_categories(company.old_in)&GRAIN_CLASSES
    out_grains=cargo_categories(company.old_out)&GRAIN_CLASSES
    if (in_grains & out_grains and re.search(
            r"armazena(?:gem)?_?(?:de_?)?graos|(?:silo|armazem)_?de_?graos",
            norm(public_name))):
        return Identity("silo","alta",
                        "nome exibido diz armazenagem de graos e especies "
                        "compartilhadas constam de IN e OUT originais")
    # RBR "Galo Prod. Agricolas": nao confundir vendedor de ração/adubo
    # com fazenda so porque o nome publico tem 'agricola'.
    # O proprio IN/OUT da DEF documenta adubo IN/OUT e racao OUT.
    evidence_role=infer_by_flow(company)
    if (evidence_role is not None and
            evidence_role.role=="agroinsumos" and
            re.search(r"prod[._-]*agric|produtos[._-]*agr|insumos[._-]*agr",
                      norm(public_name))):
        return evidence_role
    if public_name and "@@" not in public_name:
        normalized=norm(public_name)
        candidates={role for role,pattern in ROLES if re.search(pattern,normalized,re.I)}
        # "Fazenda de Batatas" satisfaz tanto o papel especifico quanto
        # "fazenda" generico. O mesmo ocorre com loja de materiais e
        # "construcao": sao sobreposicoes hierarquicas, nao dois negocios
        # contraditorios. Manter o bloqueio para misturas verdadeiras.
        if candidates=={"fazenda_batata","fazenda"}:
            candidates={"fazenda_batata"}
        elif candidates=={"fazenda_laranja","fazenda"}:
            candidates={"fazenda_laranja"}
        elif candidates=={"materiais","obras"} and re.search(
                r"(?:materiais?|material|loja)_?(?:de_?)?(?:construcao|constr|building)|"
                r"deposito_?materiais?",normalized):
            candidates={"materiais"}
        if len(candidates)==1:
            found=next(iter(candidates))
            return Identity(found,"alta",
                            "atividade pelo name da company_permanent: "+public_name)
    # Usar o fluxo quando identificador e nome publico nao revelam o ramo.
    # Regras economicas respeitam a direcao da carga na DEF ORIGINAL.
    inferred=infer_by_flow(company)
    if inferred is not None:
        return inferred
    return Identity("desconhecida","indeterminada",
                    "nome/IN/OUT insuficientes para inferencia economica segura")

@dataclass(frozen=True)
class Decision:
    allowed:bool
    reason:str
    evidence:str
    certainty:str

def decide(company,category,direction,identity=None):
    if category not in CATEGORIES or direction not in {"in","out"}:
        return Decision(False,"categoria ou direcao invalida","nenhuma","alta")
    identity=identity or classify(company)
    role=identity.role
    old_in=cargo_categories(company.old_in)
    old_out=cargo_categories(company.old_out)
    old=old_in|old_out
    documentary=category in (old_out if direction=="out" else old_in)
    def permit(reason,requirements="setor"):
        return Decision(True,reason,requirements,
                        "alta" if identity.certainty=="alta" else "media")
    def forbid(reason):
        return Decision(False,reason,identity.evidence,identity.certainty)
    if role in {"centro_logistico_inferido","terminal_portuario"}:
        # Um terminal/armazem comercializa servicos de transbordo, nao
        # fabrica cada especie. Aceitar APENAS a mercadoria/ciclo no
        # IN/OUT autenticado na mesma direcao.
        if documentary:
            return permit("movimentacao/armazenagem documentada da "
                          "mercadoria na direcao original do terminal",
                          "somente IN/OUT original da DEF; nao e produtor")
        return forbid("sem IN/OUT original nesta mercadoria/direcao; "
                      "terminal nao fabrica cargas")
    if role=="desconhecida":
        # Mesmo sem identificar o ramo ficticio, a DEF ORIGINAL documenta
        # exatamente esta mercadoria nessa direcao. Converter p.ex. corn
        # em carga1/carga22 nao significa afirmar que seja uma fazenda.
        if documentary:
            return permit("equivalencia de mercadoria IN/OUT declarada na DEF "
                          "original, sem inferir atividade da empresa",
                          "categoria E direcao comprovadas na DEF do mapa")
        return forbid("ramo nao confirmado e nenhum IN/OUT original para "
                      "esta mercadoria/direcao; nao criar rota")

    if role=="transportadora":
        return forbid("transportadora executa fretes, nao produz nem consome automaticamente a mercadoria")
    if role in {"posto_combustivel","mineracao_minerios"}:
        return forbid("posto de combustivel/mineracao de materia-prima nao "
                      "e produtor ou consumidor demonstrado desta carga "
                      "do Librelato; exigir empresa realmente compatível")
    # Mapa Eldorado: empty_palet em IN/OUT de spani e madereira,
    # e empty_palet em OUT de kaarfor2. Mapa MG: supaletes em OUT
    # de abcatacado. Mercadoria concreta, apenas MESMA direcao.
    # Entradas representam compra/retorno de paletes para armazenagem;
    # saidas representam reposicao, retorno ou reciclagem.
    if category=="palete" and documentary and role in {
        "supermercado","distribuidor","revenda_madeiras","madeireira",
        "materiais","comercio_materiais_inferido","hortifruti",
        "silo","cooperativa","entreposto_hortigraos","revenda_racao",
        "revenda_fertilizante","agroinsumos","fabrica_racao",
        "cervejaria","alimentos","fabrica_moveis","cimenteira",
        "ceramica","metalurgica","automotiva_fabrica"}:
        return permit("paletes vazios/reutilizaveis documentados em "+
                      direction.upper()+" na DEF original da empresa",
                      "somente empty_palet/supaletes/palete na direcao registrada")

    if role=="mineracao_calcario":
        return forbid("Unidade CSN Arcos expede calcario/brita na DEF; nao e comprovada fonte de bobina nem de granito nas 24 cargas")
    if role=="revenda_agricola_documentada":
        if category in {"batata","milho","racao"} and documentary:
            return permit("comercializacao da carga comprovada pelo IN/OUT da DEF original",
                          "setor e mercadoria documentados na DEF do mapa")
        return forbid("mercadoria ou direcao nao comprovada na DEF da revenda agricola")
    if role=="distribuidor_cerveja":
        if category=="cerveja" and documentary:
            return permit("distribuidora de bebidas com marca de cerveja documentada",
                          "IN/OUT com identificador de cerveja na DEF original")
        return forbid("bebidas genericas nao comprovam a mercadoria do Librelato")
    if role=="infra_passageiros":
        return forbid("rodoviaria/infraestrutura de passageiros nao e fabrica, mercado ou recebedora comprovada das 24 cargas")
    if role=="revenda_fertilizante":
        if category=="adubo":
            return permit("atacadista identificado comercializa adubo/fertilizante")
        return forbid("comercio de fertilizante nao comprova racao, sorgo nem outras cargas")
    if role=="entreposto_agricola_inferido":
        declared=old_in if direction=="in" else old_out
        if category in CROP_CLASSES and category in declared:
            return permit("produto agropecuario comprovado na direcao original "
                          "da DEF; sem supor producao propria",
                          "IN/OUT documental do entreposto")
        return forbid("entreposto ficticio nao documentou esta cultura/direcao")
    if role=="comercio_alimentos_inferido":
        available=old_in if direction=="in" else old_out
        if category in RETAIL_FOOD and category in available:
            return permit("mercadoria alimentar explicitamente registrada "
                          "nesta direcao da DEF", "IN/OUT original")
        return forbid("fluxo alimentar nao comprova este produto/direcao")
    if role in {"fabrica_racao_inferida","cimenteira_inferida",
                "ceramica_inferida","comercio_materiais_inferido",
                "consumidor_materiais_inferido"}:
        if role=="fabrica_racao_inferida":
            allowed=(category=="racao" and direction=="out" and category in old_out or
                     category in GRAIN_CLASSES and direction=="in" and category in old_in)
        elif role=="cimenteira_inferida":
            allowed=category=="cimento" and direction=="out" and category in old_out
        elif role=="ceramica_inferida":
            allowed=category=="tijolo" and direction=="out" and category in old_out
        elif role=="comercio_materiais_inferido":
            allowed=(category in BUILDING_CLASSES and
                     category in (old_in if direction=="in" else old_out))
        else:
            allowed=(direction=="in" and category in BUILDING_CLASSES and
                     category in old_in)
        if allowed:
            return permit("produto/direcao compatível com fluxo economico da DEF",
                          "IN/OUT e atividade inferida da empresa ficticia")
        return forbid("nao existe evidencia desse produto/direcao na DEF original")
    if role=="processadora_citricos":
        if category=="laranja" and direction=="in":
            return permit("industria de suco recebe fruta para processamento")
        return forbid("industria de suco NAO expede fruta bruta nem mercadoria nao demonstrada")
    if role=="fabrica_paineis":
        if category=="madeira" and direction=="in":
            return permit("industria MDF recebe madeira como materia-prima")
        return forbid("paineis MDF nao equivalem automaticamente a carga madeira/toras do reboque")
    if role=="fabrica_fibrocimento":
        if category=="cimento" and direction=="in":
            return permit("fabrica de fibrocimento compra cimento como materia-prima")
        return forbid("fabrica de telhas nao produz carga de cimento")
    if role=="revenda_madeiras":
        if category=="madeira":
            return permit("comercio especializado de madeira expede produtos ou repoe estoque")
        if category=="palete" and category in (old_out if direction=="out" else old_in):
            return permit("empresa madeireira movimenta paletes documentados", "DEF original da mercadoria")
        return forbid("revenda de madeiras nao fabrica nem consome automaticamente outras cargas")
    if role=="revenda_aco":
        if category=="bobina" and category in (old_out if direction=="out" else old_in):
            return permit("distribuidora de aco movimenta bobina documentada na DEF","DEF original da bobina")
        return forbid("comercio de ferro/aco nao comprova bobinas sem evidencias na DEF")
    if role=="plantacao_cana":
        if category=="adubo" and direction=="in":
            return permit("lavoura de cana recebe adubo")
        return forbid("cana nao equivale a milho, soja, sorgo ou outras 24 cargas")
    if role=="fabricante_fertilizante":
        if category=="adubo" and direction=="out":
            return permit("Mosaic fabrica e comercializa adubo",
                          "empresa e mercadoria explicitamente associadas")
        return forbid("fabrica de fertilizantes nao e fornecedora/compradora generica")
    if role=="entreposto_hortigraos":
        if category in {"batata","laranja","coco"}:
            return permit("entreposto comercializa hortifrutigranjeiros")
        if category in GRAIN_CLASSES and category in (old_in|old_out):
            return permit("entreposto recebe/expede graos documentados na DEF",
                          "setor de armazenagem mais cargo original")
        return forbid("CEAGESP nao demonstra comercio desta carga na unidade")
    if role=="fazenda_soja":
        if category=="soja" and direction=="out" and category in old_out:
            return permit("fazenda expede soja documentada no OUT original")
        if category=="adubo" and direction=="in":
            return permit("fazenda de soja recebe adubo para lavoura")
        return forbid("fazenda de soja nao produz nem consome esta carga sem evidencia")
    if role=="bananal":
        return (permit("bananal compra adubo para suas plantas","atividade agricola da unidade")
                if category=="adubo" and direction=="in" else
                forbid("plantacao de banana nao e produtor/consumidor generico desta carga"))
    if direction=="out":
        # De quem o comprador deve contratar a coleta?
        if role=="fazenda":
            if category in CROP_CLASSES and category in old_out:
                return permit("fazenda colheu "+category+" e solicita transporte para comprador",
                              "atividade rural + OUT original da cultura")
            return forbid("sem evidencias de producao desta cultura na DEF original da fazenda")
        if role in {"fazenda_batata","fazenda_laranja"}:
            if category==("batata" if role=="fazenda_batata" else "laranja"):
                return permit("fazenda especializada fornece sua propria colheita")
            return forbid("fazenda de cultura especifica nao produz outros produtos")
        if role in {"silo","cooperativa"}:
            if category in GRAIN_CLASSES and category in old:
                return permit("armazem/cooperativa expede cereal ou grao armazenado",
                              "setor + evidencia do cereal na DEF")
            if role=="cooperativa" and category in {"adubo","racao","algodao","coco"} and category in old_out:
                return permit("cooperativa revende mercadoria documentada","OUT da mercadoria")
            return forbid("cooperativa/silo sem expedicao documentada dessa mercadoria")
        # Logistica reversa de paletes usados: industrias, mercados e
        # armazenagem so expedem quando o produto ESTA na DEF do mapa.
        # A madeira produzida pela serraria nao prova palete usado;
        # o caso madeireira fabricante continua separado abaixo.
        if (category=="palete" and role in {
                "supermercado","hortifruti","materiais","agroinsumos",
                "alimentos","silo","cooperativa","fabrica_racao",
                "cervejaria","cimenteira","automotiva_fabrica","metalurgica"}
                and category in old_out):
            return permit("estabelecimento expede paletes usados para retorno "
                          "ou reciclagem", "OUT de paletes documentado na DEF")
        factory={
            "cervejaria":"cerveja","cimenteira":"cimento","siderurgica":"bobina",
            "ceramica":"tijolo","fabrica_racao":"racao","madeireira":"madeira",
            "pedreira":"granito","marmoraria":"granito"
        }
        if role in factory and factory[role]==category:
            return permit("produtor identificado de "+category)
        if role=="madeireira" and category=="palete":
            return permit("madeireira fornece paletes")
        if role=="agroinsumos" and category in {"adubo","racao","sorgo"}:
            return permit("agropecuaria fornece insumo ou alimento animal solicitado pelo comprador")
        if role=="revenda_racao" and category=="racao":
            return permit("comercio especializado revende racao animal")
        if role=="beneficiadora_algodao" and category=="algodao":
            return permit("algodoeira expede pluma beneficiada")
        if role=="comercio_graos" and category in GRAIN_CLASSES and category in old:
            return permit("comercial de graos expede mercadoria documentada na DEF",
                          "setor de graos + mercadoria original documentada")
        if role=="materiais" and category in BUILDING_CLASSES:
            # Lojas fornecem cimento/tijolos/madeira; para rochas ornamentais
            # exigir prova de comercializacao no arquivo de origem.
            if category=="granito" and category not in old:
                return forbid("loja sem prova de comercializar granito")
            return permit("loja de materiais atende pedido de "+category+" da obra")
        if role=="hortifruti" and category in {"batata","laranja","coco"}:
            return permit("CEASA/hortifruti comercializa "+category+" ao comprador")
        if role=="supermercado" and category in {"batata","laranja","cerveja","coco"} and category in old_out:
            return permit("varejista revende mercadoria documentada","OUT original")
        if role=="distribuidor" and category in old_out:
            return permit("distribuidor especializado movimenta produto documentado","OUT original")
        return forbid("empresa nao e produtora/revendedora comprovada de "+category)
    # Quem contrata o motorista para repor estoque ou receber materia-prima?
    if role in {"fazenda","fazenda_batata","fazenda_laranja"}:
        if category=="adubo":
            return permit("fazenda precisa repor fertilizante para a lavoura")
        if category in {"racao","sorgo"} and (
                category in old_in or "racao" in old_in):
            return permit("criacao de animais documentou compra de alimento animal",
                          "IN de racao/sorgo na DEF")
        return forbid("fazenda nao possui necessidade comprovada desta mercadoria")
    if role=="pecuaria" and category in {"racao","sorgo"}:
        return permit("criacao animal compra alimento para o rebanho")
    if role=="supermercado" and category in {"cerveja","batata","laranja","coco"}:
        return permit("supermercado repoe estoque para seus clientes")
    if role=="hortifruti" and category in {"batata","laranja","coco"}:
        return permit("CEASA/hortifruti recebe produto para revenda/distribuicao")
    if role=="alimentos" and category in {"batata","laranja","milho","soja","coco"} and category in old_in:
        return permit("industria alimenticia usa materia-prima documentada","IN original")
    if role=="agroinsumos" and category in {"adubo","racao","sorgo"}:
        return permit("agropecuaria reabastece mercadoria para revenda")
    if role=="revenda_racao" and category=="racao":
        return permit("comercio de racoes recebe mercadoria para revenda")
    if role=="fabrica_racao" and category in GRAIN_CLASSES:
        return permit("fabrica de racao compra materia-prima para fabricar alimento animal")
    if role in {"silo","cooperativa"} and category in GRAIN_CLASSES and category in old:
        return permit("armazem/cooperativa recebe graos da fazenda","grao documentado na DEF")
    if role=="cooperativa" and category in {"adubo","algodao","racao","coco"} and category in old:
        return permit("cooperativa recebe insumo/produto associado documentado","DEF original")
    if role=="textil" and category=="algodao":
        return permit("industria textil necessita de fibra de algodao")
    if role in {"obras","materiais"} and category in BUILDING_CLASSES:
        return permit("obra/loja compra "+category+" para construção ou estoque")
    if role=="premoldados" and category=="cimento":
        return permit("fabrica de pre-moldados consome cimento")
    if role=="concreteira" and category=="cimento":
        return permit("central de concreto usa cimento como materia-prima")
    if role=="fabrica_moveis" and category=="madeira":
        return permit("industria moveleira consome madeira ou paineis de madeira")
    if role=="comercio_graos" and category in GRAIN_CLASSES and category in old:
        return permit("comercial de graos recebe mercadoria documentada na DEF",
                      "setor de graos + mercadoria original documentada")
    if role in {"automotiva_fabrica","metalurgica"} and category=="bobina":
        return permit("industria usa bobinas de aco na producao")
    if role=="metalurgica" and category=="cimento" and category in old_in:
        return permit("fabrica industrial recebe cimento declarado na DEF",
                      "industria + consumo de cimento documentado na DEF")
    if role=="maquinas" and category=="bobina" and category in old_in:
        return permit("fabricante de equipamentos documentou consumo de bobinas","IN original")
    if role=="marmoraria" and category=="granito":
        return permit("marmoraria recebe pedra para beneficiamento")
    if role=="reciclagem" and category=="palete":
        return permit("recicladora recebe paletes usados")
    if role in {"distribuidor","silo","cooperativa"} and category=="palete" and category in old_in:
        return permit("unidade recebe paletes para retorno documentado",
                      "IN especifico de paletes na DEF do mapa")
    return forbid("empresa nao demonstrou necessidade de receber "+category)

# Excecao solicitada pelo autor do mapa/Company. Por construcao,
# nao se aplica ao RBR nem a cargas alem da pluma e do coco.
# A regra oferece origens/destinos ficticios EXISTENTES da DEF; nao
# afirma que a empresa tenha aqueles produtos em IN/OUT originais.
REGIONAL_APPROVED_MAPS=frozenset({"minas_gerais","eldorado"})
REGIONAL_APPROVED_CATEGORIES=frozenset({"algodao","coco"})
REGIONAL_FARM_ROLES=frozenset({
    "fazenda","fazenda_soja","fazenda_batata","fazenda_laranja"
})
REGIONAL_COTTON_RECEIVERS=frozenset({
    "silo","cooperativa","beneficiadora_algodao","textil",
    "entreposto_hortigraos","comercio_graos","distribuidor"
})
REGIONAL_COCONUT_RECEIVERS=frozenset({
    "supermercado","hortifruti","entreposto_hortigraos",
    "comercio_alimentos_inferido"
})
REGIONAL_FORBIDDEN_ROLES=frozenset({
    "obras","posto_combustivel","infra_passageiros",
    "transportadora","mineracao_minerios","mineracao_calcario",
    "siderurgica","metalurgica","premoldados","cimenteira",
    "automotiva_fabrica","bananal","cervejaria","ceramica"
})


def regional_approved_decision(company,category,direction,map_name,identity=None):
    """EXCECAO EXPLICITA do usuario para MG/Eldorado, nunca RBR.

    Devolve Decision aprovado somente para:
      OUT de pluma/coco de fazendas existentes;
      IN pluma de armazens/silos, cooperativas, beneficiadoras ou texteis;
      IN coco de mercados, mercearias e centrais de hortifruti.
    Nao fabrica empresa/cidade/arquivo editor nem atribui commodity
    desconhecida à DEF original. Sua confianca é nivel SIMULADO.
    """
    scope=norm(map_name or "")
    if (scope not in REGIONAL_APPROVED_MAPS or
            category not in REGIONAL_APPROVED_CATEGORIES or
            direction not in {"in","out"}):
        return None
    identity=identity or classify(company)
    role=identity.role
    if role in REGIONAL_FORBIDDEN_ROLES:
        return None
    candidate=norm(company.name)+" "+norm(getattr(company,"display_name",""))
    farm_name=bool(re.search(r"(?:^|_)(?:fazenda|faz_|farm|plantacao|sitio|chacara)",candidate))
    farm=(role in REGIONAL_FARM_ROLES or
          (role=="desconhecida" and farm_name))
    if direction=="out":
        if not farm:
            return None
        return Decision(
            True,
            "ADAPTACAO REGIONAL AUTORIZADA: fazenda existente pode "
            "expedir "+("pluma de algodao" if category=="algodao" else "coco")+
            " como producao/compra agregada simulada, mesmo sem OUT "
            "original da mercadoria",
            "SIMULACAO_ECONOMICA_APROVADA_USUARIO_MG_ELDORADO","media"
        )
    # Pluma: armazéns também recebem/armazenam fardos e cooperativas
    # podem agrupar a safra; não enviar para obras, postos ou siderúrgicas.
    if category=="algodao":
        warehouse_name=bool(re.search(
            r"(?:armazem|armazens|warehouse|galpao|deposito_agric|"
            r"beneficiadora_?algodao|cotton_?gin|algodoeira)",
            candidate))
        cotton=(role in REGIONAL_COTTON_RECEIVERS or
                (role=="desconhecida" and warehouse_name))
        if not cotton:return None
        return Decision(
            True,
            "ADAPTACAO REGIONAL AUTORIZADA: pluma expedida por fazendas "
            "para armazenagem/beneficiamento/distribuicao; nao confirma "
            "pluma no IN original",
            "SIMULACAO_ECONOMICA_APROVADA_USUARIO_MG_ELDORADO","media"
        )
    grocery_name=bool(re.search(
        r"mercearia|mercadinho|quitanda|mercado(?:_|$)|supermercado|"
        r"ceasa|hortifrut|sacolao|frutaria|grocery",candidate))
    food_retail=(role in REGIONAL_COCONUT_RECEIVERS or
                 (role=="desconhecida" and grocery_name))
    if not food_retail:return None
    return Decision(
        True,
        "ADAPTACAO REGIONAL AUTORIZADA: coco de fazendas para reposicao "
        "de estoque em supermercado, mercearia, CEASA ou hortifruti",
        "SIMULACAO_ECONOMICA_APROVADA_USUARIO_MG_ELDORADO","media"
    )


def legacy_plausible(company,category,direction):
    """Só avaliar permissões JÁ existentes; nunca gerar novas por hipótese.

    Retorna uma justificativa ECONOMICAMENTE PLAUSÍVEL com confianca MEDIA.
    Nao equivale à categoria original documentada no IN/OUT e nao cria
    'comprovacao' territorial ou ensaio dentro do ETS2.
    """
    if direction not in {"in","out"} or category not in CATEGORIES:
        return None
    identity=classify(company)
    role=identity.role
    in_cats=cargo_categories(company.old_in)
    out_cats=cargo_categories(company.old_out)
    orig=in_cats if direction=="in" else out_cats
    if category in orig:
        return None  # A permissao literal fica para a politica forte.
    # Armazens/cooperativas com pelo menos uma especie de cereal movimentada
    # no MESMO sentido podem plausivelmente receber/expedir sorgo a granel.
    if (role in {"silo","cooperativa","comercio_graos"} and
            category=="sorgo" and (orig & GRAIN_CLASSES)):
        return ("POSSIVEL movimentacao sazonal de sorgo em unidade que "
                "ja movimenta outros graos no mesmo sentido; permissao "
                "herdada nao comprova variedade")
    # Fazenda com colheita de graos no OUT pode plantar sorgo em rotacao.
    # Nao inventar soja, algodao, coco ou batata para qualquer fazenda.
    if (role=="fazenda" and direction=="out" and category=="sorgo"
            and (out_cats & GRAIN_CLASSES)
            and not (in_cats & GRAIN_CLASSES)):
        return ("POSSIVEL cultivo alternado de sorgo em fazenda de graos; "
                "permissao antiga sujeita a confirmacao no jogo/mapa")
    # Paletes de apoio para empresas que realmente trabalham com produtos
    # embalados ou madeira. Sem a carga no IN/OUT ela fica apenas plausivel.
    if category=="palete" and role in {
        "materiais","revenda_madeiras","madeireira","fabrica_moveis",
        "comercio_materiais_inferido","distribuidor","supermercado",
        "cervejaria","cimenteira","revenda_racao","agroinsumos"
    }:
        if direction=="in" and (in_cats & (BUILDING_CLASSES | RETAIL_FOOD |
                                           {"madeira","racao","adubo"})):
            return ("POSSIVEL recebimento de paletes para reposicao e "
                    "retorno de embalagens; nao consta palete na DEF original")
        if direction=="out" and (out_cats & (BUILDING_CLASSES | RETAIL_FOOD |
                                             {"madeira","racao","adubo"})):
            return ("POSSIVEL expedicao de paletes vazios ou embalagens "
                    "retornaveis; permissao herdada sem prova original")
    return None


def city_references(company):
    """Somente company_def com CITY e PREFAB reais entra na matriz territorial.

    Nunca confundir nome do arquivo com cidade. Um identificador de prefab
    declarado continua sem homologacao dentro do ETS2 ate teste em jogo.
    """
    from recuperacao_editor import CITY, PREFAB, COMPANY_DEF
    refs=[]
    for path,raw in sorted(company.editor_files.items()):
        text=raw.decode("utf-8-sig","replace")
        city=CITY.search(text)
        prefab=PREFAB.search(text)
        if not (COMPANY_DEF.search(text) and city and prefab):
            continue
        refs.append({
            "cidade":city.group(1),
            "arquivo_editor":path,
            "fonte":"company_def: city + prefab",
            "prefab_declarado":prefab.group(1),
            "prefab_confirmado":False
        })
    return refs

def coverage(companies,manifest,decision_fn=None):
    """Matriz empresa/cidade/carga IN-OUT + todas as cargas e todas as unidades."""
    company_rows=[];unit_rows=[];routes={}
    expected={}
    for c in sorted(companies.values(),key=lambda x:x.name):
        ident=classify(c)
        ins=set();outs=set();reasons={}
        for n,(cat,title) in manifest.items():
            cargo=("carga"+str(n) if isinstance(n,int) else str(n))
            for direction,container in (("in",ins),("out",outs)):
                d=(decision_fn(c,cat,direction,cargo) if decision_fn else
                   decide(c,cat,direction,ident))
                reasons[direction+":"+cargo]={"permitido":d.allowed,"motivo":d.reason,
                                              "evidencia":d.evidence,"confianca":d.certainty}
                if d.allowed:container.add(cargo)
        locations=city_references(c)
        company_rows.append({"empresa":c.name,
            "nome_exibido_def":getattr(c,"display_name",""),
            "atividade":ident.role,
            "confianca_classificacao":ident.certainty,"justificativa":ident.evidence,
            # Rastreabilidade para CADA empresa (inclusive ficticia):
            # o auditor pode comparar cargas ORIGINAIS e decisoes por produto.
            "in_originais_def":sorted(c.old_in),
            "out_originais_def":sorted(c.old_out),
            "categorias_in_originais":sorted(cargo_categories(c.old_in)),
            "categorias_out_originais":sorted(cargo_categories(c.old_out)),
            "metodo_classificacao":(
                "pendente_evidencia" if ident.role=="desconhecida" else
                "inferencia_fluxo_in_out" if (
                    ident.role.endswith("_inferida") or
                    "inferencia economica" in ident.evidence or
                    "inferencia de comercio" in ident.evidence or
                    "fluxo " in ident.evidence or
                    "fertilizante registrado em IN e OUT" in ident.evidence
                ) else "identificador_ou_nome_def"),
            "instancias_editor":len(locations),"in_esperados":sorted(ins),
            "out_esperados":sorted(outs),"decisoes":reasons})
        for loc in locations:
            unit_rows.append({"empresa":c.name,"cidade":loc["cidade"],"atividade":ident.role,
                "arquivo_editor":loc["arquivo_editor"],"fonte_cidade":loc["fonte"],
                "in_esperados":sorted(ins),"out_esperados":sorted(outs),
                "prefab_confirmado":False})
        expected[c.name]={"in":ins,"out":outs}
    for n,(cat,title) in manifest.items():
        cargo=("carga"+str(n) if isinstance(n,int) else str(n))
        src=[c for c,dirs in expected.items() if cargo in dirs["out"]]
        dst=[c for c,dirs in expected.items() if cargo in dirs["in"]]
        routes[cargo]={"mercadoria":title,"categoria":cat,
            "origens":len(src),"destinos":len(dst),
            "pares_distintos":len(src)*len(dst)-len(set(src)&set(dst)),
            "origens_lista":src,"destinos_lista":dst}
    return {
        "empresas":company_rows,"instancias_cidade":unit_rows,
        "rotas":routes,"total_empresas":len(company_rows),
        "total_instancias_editor":len(unit_rows),
        "empresas_sem_identificacao":sum(x["atividade"]=="desconhecida" for x in company_rows),
        "empresas_sem_cargas_compatíveis":sum(not x["in_esperados"] and not x["out_esperados"]
                                             for x in company_rows),
        "empresas_sem_editor":sum(not x["instancias_editor"] for x in company_rows),
        "cargas_com_pares":sum(x["pares_distintos"]>0 for x in routes.values()),
        "cargas_total":len(routes),
        "garantia_territorial":"nao certificada sem validar prefabs/cidades e o mercado dentro do ETS2",
    }
