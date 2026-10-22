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
    ("usina_acucar",r"usina_?acucar|sugar_mill|sugar_plant|engenho_?acucar"),
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
    ("processadora_citricos",r"^citrosuco[12]?$|^frucamp$"),
    ("fabrica_paineis",r"^greenplac$"),
    ("fabrica_fibrocimento",r"^eternit$"),
    ("revenda_madeiras",r"^go_madeirani$|^go_madesaba$|^made_itaja$|^madei_rdoce$|^madereira(?:[1237]|se|vo)$|^ms_vale_mad$|^mt_cia_madei$|^pr_mademape$"),
    ("revenda_aco",r"^br_ferro$|^mt_ferro_aco$|^udiaco$"),
    ("plantacao_cana",r"^cana_acucar2?$|^cana_agu$|^cana_ms1$|^usina_cana$"),
    ("infra_passageiros",r"^rodoviaria\d*$|^rodo_(?:bh|go\d+|mg\d+|ms\d+|mt\d+)$|^pr_rodo$|^sc_rodo_(?:gar|ita|join|pic)$|^aero_rverde$|^prf_nlima$|^enel_(?:acreu|india|stb)$"),
    ("entreposto_hortigraos",r"^ceagesp$"),
    ("fabricante_fertilizante",r"^mosaico2?$|^mosaic_fertilizantes$"),
    ("beneficiadora_algodao",r"algodoeira|cotton_gin|^mt_torre_alg$|^ms_alg_ib$"),
    ("fabrica_moveis",r"marcenaria|furniture_factory|furniture_plant|moveis|^bechara$|^brigatto$|^esplane$"),
    ("comercio_graos",r"(?:^|_)graos(?:_|$)|^grupo_cereal$|^g_cereal_(?:rv|stb)$|^pr_anaconda$|^amaggi$"),
    ("concreteira",r"^polimix(?:1|_rib)?$|^concretar$|concreto_usinado|concrete_batch"),
    ("siderurgica",r"gerdau|cofer|usiminas|arcelor|^csn(?:_|$)|steel_mill|steelworks|siderurg|sider[ _]"),
    ("automotiva_fabrica",r"^(?:fiat|fca|vw|volkswagen|gm|hyundai|toyota|renault|ford|honda|bmw)(?:_|$)|montadora|automotive_plant|car_factory"),
    ("maquinas",r"^mc_?equip|^mcequip|maquinas|maquinario|machinery|equipment_factory"),
    ("cimenteira",r"votoran|intercement|cimenteira|cement_plant|cement_factory|^globcement2?$"),
    ("premoldados",r"carmoprem|premold|pre_mold|precast|concrete_products"),
    ("cervejaria",r"ambev|heineken|brahma|cervejaria|brewery|brewing|beer_factory|^grupo_petropolis$|^grupo_p2?$|^cercrystal$|^cerveja_crystal$"),
    ("reciclagem",r"recicl|sucata|sucatao|ferro_velho|ferrovelho|scrapyard|recycling_yard"),
    ("ceramica",r"ceramica|olaria|brickyard|brick_factory|tijolaria"),
    ("pedreira",r"pedreira|quarry|rock_quarry|extratora"),
    ("marmoraria",r"marmoraria|marmor|granito|granite_shop|stoneworks"),
    ("madeireira",r"madeireira|^madereira$|serraria|sawmill|timber_mill|lumberyard|serrac|^madeiras(?:[0-9]+)?$|^extrmadeira$|^betimmadeira$|^samirmadeira$|^extr_rio_p2$|^extracao2$|^extracao_sc$"),
    ("fabrica_racao",r"racao_fabrica|fabrica_racao|feedmill|feed_mill|animal_feed_factory|nutricao_animal|brejeiro|^nutrition$|^trouw_nutrition$"),
    ("revenda_racao",r"^raguife$|(?:^|_)racoes(?:_|$)|feed_store|loja_racao"),
    ("agroinsumos",r"agropec|agroinsum|agro_supply|fertiliz|adubo|agrocenter|^agrish|^agroce|^agromais|casa_adubo|^cimoagro$"),
    ("silo",r"silo|armazem|armazens|armz|grain_elevator|grain_storage|cerealista|caramuru"),
    ("cooperativa",r"cooper|coamo|^coop|camda|comigo"),
    ("pecuaria",r"pecuar|gado|cattle|livestock|poultry_farm|suino|criatorio|feedlot|confinamento"),
    ("fazenda",r"fazenda|^faz_|^faze_|(?:^|_)faz_|^faz(?:bale|boa|brejo|cerra|grao|irmas|pedra|pit|sao|serena|serra|sp|sbene|pg)|^farm|_farm|plantacao|farming|agricultural_farm|agric"),
    ("textil",r"textil|tecel|fiacao|cotton_mill|textile|spinning_mill"),
    ("metalurgica",r"metalurg|calha|cortedobra|metalworks|sheetmetal|usinagem|^itcc2?$|^marcegaglia$"),
    ("materiais",r"materiais|(?:^|_)(?:material|materiais)(?:_|$)|^material(?:ber|se1)$|mat_constr|material_constr|loja_material|building_supplies|hardware_store|building_materials|construm|construsol|dep_mat|^material_|^leroy_merlin$|^pinheiralvo$|^depo_(?:bh|cacu)$"),
    ("obras",r"construcao|construction_site|building_site|obra_|^obra|canteiro|batisse|^constru(?:ca|sc|aco|ai|betim|cana|cb|fer|lavra|sar)$|^sanbuilders2?$|^konstnr(?:_hs)?2?$|^cons_rbr$|^const_c_g$|^coluna_ma$"),
    ("supermercado",r"supermercado|super_mercado|supermarket|grocery|atacadao|assai|bahamas|carrefour|^kaarfor2?$|^sellplan2?$|^pr_samsclub$|^mt_mer_reti$|^extra_|compr_bem|^compre_bem$|^martminas$|^martmina_c$|^super(?:abc|bh|eli|josyldo|oliveir)$|^merc(?:ado(?:kril|_ac)?|_[a-z0-9_]+)$|^pr_mercado$|^sc_mercado$"),
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
    "madeira":r"madeira|wood|wooden_planks|logs|timber|lumber",
    "cimento":r"cimento|cement|cement_bags|bagged_cement",
    "tijolo":r"tijolo|tijolos|brick|bricks|clay_bricks",
    "granito":r"granito|granite",
    "bobina":r"bobina|bobinas|steel_coil|steel_coils|steel_roll|coil_steel",
    "cerveja":r"cerveja|cervejas|beer|beers|lager|ale",
    "palete":r"palete|paletes|pallet|pallets|wooden_pallets",
    "racao":r"racao|animal_feed|livestock_feed|feedmeal|compound_feed|xerem",
}
def norm(v):
    return "".join(ch for ch in unicodedata.normalize("NFKD",str(v).lower())
                   if not unicodedata.combining(ch)).replace("-","_").replace(" ","_")
def cargo_categories(tokens):
    found=set()
    for tok in tokens:
        tok=norm(tok)
        for category,pattern in ALIASES.items():
            if re.fullmatch(r"(?:rbr_|ros_|cs_)?(?:"+pattern+r")(?:_[ab])?",tok):
                found.add(category)
    return found

@dataclass(frozen=True)
class Identity:
    role:str
    certainty:str
    evidence:str

def classify(company):
    identifier=norm(company.name)
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
    # A DEF pode conter registros confiaveis de movimento de mercadorias;
    # porem OUT nao e demonstracao da INDUSTRIA. Os nao reconhecidos ficam
    # em revisao em vez de criar fornecedor ficticio.
    return Identity("desconhecida","indeterminada",
                    "identificador nao permite afirmar atividade; IN/OUT exige revisao")

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
    if role=="desconhecida":
        return forbid("ramo nao confirmado; carga deve ser revisada, sem preencher automaticamente")
    if role=="transportadora":
        return forbid("transportadora executa fretes, nao produz nem consome automaticamente a mercadoria")
    if role=="infra_passageiros":
        return forbid("rodoviaria/infraestrutura de passageiros nao e fabrica, mercado ou recebedora comprovada das 24 cargas")
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

def city_references(company):
    """Cada editor/*.sii identifica uma unidade/cidade candidata no mapa.

    A confirmacao final de prefab depende de arquivos completos do mapa/ETS2.
    """
    refs=[]
    for path,raw in sorted(company.editor_files.items()):
        city=Path(path).stem
        text=raw.decode("utf-8-sig","replace")
        m=re.search(r'(?im)^\s*(?:city|city_name)\s*:\s*["'+"']?([a-z0-9_]+)",text)
        if m:city=m.group(1)
        refs.append({"cidade":city,"arquivo_editor":path,
                     "fonte":"campo city" if m else "nome do arquivo editor",
                     "prefab_confirmado":False})
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
