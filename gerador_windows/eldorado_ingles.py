"""Perfil economico especializado para a DEF do Eldorado.

Traduz os identificadores INGLES sem confundir produto com ramo.
Fluxos IN/OUT sao evidencias; rotas adicionadas por simulacao sao rotuladas
e limitadas a empresas reais da DEF (nunca cidades/prefabs inventados).
Este modulo so e ativado pela auditoria profissional do Eldorado.
"""
from __future__ import annotations
import csv
from collections import Counter

# Traducoes conservadoras. Produto ausente permanece com o ID original,
# em vez de receber uma traducao inventada. As variantes DLC usam base.
PT = {
"almond":"amendoas","apples":"macas","apples_c":"macas refrigeradas",
"banana":"bananas","beans":"feijao (nao soja)","feijao":"feijao",
"beef_meat":"carne bovina","beef3":"carne bovina",
"beverages":"bebidas genericas","beverages_c":"bebidas em embalagens",
"bebidas":"bebidas genericas","big_bag_seed":"sementes em big bags",
"bois":"gado bovino vivo","bottle_water":"agua engarrafada",
"canned_beans":"feijao em conserva","carrots":"cenouras",
"carrots_c":"cenouras refrigeradas","cauliflower":"couve-flor",
"cheese":"queijo","chocolate":"chocolate","clothes":"roupas",
"clothes3":"roupas","clothes_c":"roupas em caixas","corn":"milho",
"cement":"cimento","concrete":"concreto","concr_beams":"vigas de concreto",
"cont_trees":"mudas de arvores","drymilk":"leite em po",
"fertilizer":"fertilizante (adubo)","flour":"farinha",
"fruit":"frutas genericas","granel":"carga a granel generica",
"graos":"graos genericos (nao confirma soja ou milho)",
"grapes":"uvas","honey":"mel","icecream":"sorvete",
"leite":"leite","limonades":"refrigerantes/limonadas",
"milk":"leite","milho":"milho","nonalco_beer":"cerveja SEM alcool",
"oranges":"laranjas","peas":"ervilhas","plums":"ameixas",
"potatoes":"batatas","pnut_butter":"pasta de amendoim",
"rice":"arroz","rice_c":"arroz em embalagem",
"soja":"soja","soybeans":"soja","straw_bales":"fardos de palha",
"sugar":"acucar","sugar2":"acucar","tomatoes":"tomates",
"watermelons":"melancias","young_seed":"mudas e sementes",
"yogurt":"iogurte","vinegar":"vinagre","vinegar_c":"vinagre",
"ammonia":"amonia","acetylene":"acetileno","acid":"acidos",
"arsenic":"arsenico","boric_acid":"acido borico",
"chlorine":"cloro","chlorine_t":"cloro em tanque",
"chemicals":"produtos quimicos","chem_sorbent":"absorvente quimico",
"chem_sorb_c":"absorvente quimico embalado","cyanide":"cianeto",
"fluorine":"fluor","hydrochlor":"acido cloridrico",
"mercuric":"mercurio","nitrocel":"nitrocelulose","nitrogen":"nitrogenio",
"phosphor":"fosforo","potahydro":"hidroxido de potassio",
"pesticide":"pesticidas","sodhydro":"hidroxido de sodio",
"sulfuric":"acido sulfurico","sulfuric_t":"acido sulfurico em tanque",
"magnesium":"magnesio","lead":"chumbo","coal":"carvao mineral",
"ore":"minerio","gravel":"brita","sand":"areia",
"areia":"areia","calcario":"calcario","stones":"pedras genericas",
"bricks":"tijolos","clinquer":"clinquer de cimento",
"eucalipto":"eucalipto","logs":"toras de madeira",
"lumber":"madeira serrada","sawpanels":"paineis de madeira",
"wood":"madeira","wshavings":"serragem/lascas",
"furniture":"moveis","iron_pipes":"tubos de ferro/aco",
"largetubes":"tubos grandes de aco",
"metal_center":"pecas de centro metalico",
"hmetal":"metal pesado","scrap_metals":"sucata metalica",
"sandwch_pnls":"paineis sanduiche (construcao)",
"wallpanels":"paineis de parede","floorpanels":"paineis de piso",
"roof_tiles":"telhas","rooflights":"claraboias",
"roofing_felt":"manta para telhado",
"precast_strs":"estruturas pre-moldadas",
"outdr_flr_tl":"piso externo","glass":"vidro",
"glass_packed":"vidro embalado","copp_rf_gutt":"calhas de cobre",
"vent_tube":"tubos de ventilacao","chimney_syst":"sistema de chamine",
"digger500":"escavadeira compacta","digger1000":"escavadeira pesada",
"diggers":"escavadeiras","excavator":"escavadeira",
"excavator2":"escavadeira","tractors":"tratores",
"tractors2":"tratores","forklifts":"empilhadeiras",
"betoneira":"betoneira","mondeos":"veiculos de passeio",
"brake_pads":"pastilhas de freio","radiators":"radiadores",
"tyres":"pneus","truck_tyres":"pneus de caminhao",
"truck_rims":"rodas de caminhao",
"truck_rims_c":"rodas de caminhao embaladas",
"cable_reel":"carretel de cabos","electronics":"eletronicos",
"med_equip":"equipamentos medicos","tableware":"utensilios de mesa",
"toys":"brinquedos","dryers":"secadoras","paper":"papel",
"mason_jars":"potes de vidro","plastic_gra":"granulos de plastico",
"used_plast":"plastico usado","used_plast_c":"plastico usado prensado",
"empty_palet":"paletes vazios","used_packag":"embalagens usadas",
"empty_barr":"barris vazios","emptytank":"tanque vazio",
"tanquevazio":"tanque vazio","used_battery":"baterias usadas",
"lixo":"residuos","lixo1":"residuos diversos","lixo2":"residuos diversos",
"lixo3":"residuos diversos","lixo4":"residuos diversos",
"lixo5":"residuos diversos","sucata":"sucata",
"container":"container","containersud":"container",
"ibc_cont":"contentor industrial IBC",
"diesel":"oleo diesel","diesel2":"oleo diesel",
"petrol":"gasolina","gasolina":"gasolina","gas":"gas",
"fuel_oil":"oleo combustivel","fueltanker":"caminhao-tanque",
"hipresstank":"tanque de alta pressao","kerosene":"querosene",
"querosene":"querosene","lpg":"gas liquefeito de petroleo",
"motor_oil":"oleo de motor","motor_oil_c":"oleo de motor em caixa",
"oil":"oleo","oil_filters":"filtros de oleo",
"oil_filt_c":"filtros de oleo embalados",
"graph_grease":"graxa grafitada",
"grass_rolls":"rolos de grama","plant_substr":"substrato para plantas",
"maple_syrup":"xarope de bordo","carb_water":"agua com gas",
"bottle_water":"agua engarrafada","packag_food":"alimentos embalados",
"chewing_gums":"gomas de mascar",
"nut":"castanhas","nuts":"castanhas",
"ammunition":"municao","dynamite":"dinamite","explosives":"explosivos",
"fireworks":"fogos de artificio",
"passageiros":"passageiros","encomendas":"encomendas",
"sedex":"encomendas expressas","alcool":"alcool",
"cana":"cana-de-acucar","canavazio":"veiculo de cana vazio",
"bagacof":"bagaco fibroso",
"overweight":"carga especial de excesso de peso",
"bguerra":"equipamento/carga identificada por nome proprio",
"contrato_tnl_bau":"contrato de transporte",
"contrato_tnl_bau2":"contrato de transporte",
"princess":"carga especial (nome de modelo)",
"fosforo":"fosforo","potassium":"potassio","sodium":"sodio",
"neon":"neon","hydrogen":"hidrogenio",
"contamin":"material contaminado","hwaste":"residuos perigosos",
"hchemicals":"quimicos perigosos","carbn_pwdr_c":"po de carbono",
"sodchlor":"cloreto de sodio","water":"agua"
}
# Complemento validado contra os 225 IDs existentes na DEF entregue.
PT.update({
    "asph_miller":"fresadora de asfalto (maquina pesada)",
    "cacamvazio":"cacamba vazia",
    "dozer":"trator de esteiras",
    "goat_cheese":"queijo de cabra",
    "ketchup":"molho ketchup",
    "locomotive":"locomotiva",
    "mobile_crane":"guindaste movel",
    "sq_tub":"tubos metalicos de secao quadrada",
    "transformat":"transformador eletrico",
    "wrk_cloth":"roupas de trabalho",
    "tnl_bau":"carga de contrato em bau",
    "tnl_bau2":"carga de contrato em bau (variante)"
})
for i in range(2,10):
    PT["passageiros"+str(i)]="passageiros"

def norm(value):
    return str(value).lower().strip().split(".",1)[0].replace("-","_")

def translate(token):
    key=norm(token)
    return PT.get(key,"NAO_TRADUZIDO: "+str(token))

def token_groups(company,policy):
    names_in={norm(x) for x in company.old_in}
    names_out={norm(x) for x in company.old_out}
    return names_in,names_out,policy.cargo_categories(names_in),policy.cargo_categories(names_out)

def infer_identity(company,policy):
    """Retorna Identity somente para um ciclo realmente distinguivel na DEF.

    Regras do Eldorado nao passam a se aplicar ao Minas/RBR: a auditoria
    so chama esta funcao no escopo Eldorado.
    """
    ii,oo,ci,co=token_groups(company,policy)
    standard=policy.classify(company)
    farm=standard.role in {"fazenda","fazenda_soja","fazenda_batata",
                           "fazenda_laranja","desconhecida"}
    livestock=bool("bois" in oo or
        ("bois" in ii and "leite" in oo))
    crop_output=bool(co & {"milho","soja","batata","laranja"})
    generic_multisector=(len(oo)>45 and len(oo & ii)>10)
    if (farm and livestock and not crop_output and
            len(oo)<=14 and not generic_multisector):
        return policy.Identity("eldorado_pecuaria","alta",
            "criacao documentada: bois no OUT ou gado no IN + leite no OUT")
    # Se as MESMAS culturas entram E saem, ha comercializacao/armazenagem:
    # sementes/adubo no IN nao tornam o entreposto plantacao produtora.
    # Preservar a cooperativa identificada por marca como cooperativa.
    if (standard.role in {"fazenda","desconhecida","comercio_graos"}
            and {"milho","soja"} <= ci
            and {"milho","soja"} <= co and len(oo)<=15):
        return policy.Identity("eldorado_armazem_graos","alta",
            "milho e soja identificados no IN e no OUT; "
            "armazenagem/comercio de grãos, nao cultivo demonstrado")
    if (farm and crop_output and
            ({"fertilizer","big_bag_seed","young_seed"} & ii)
            and len(oo)<=16):
        return policy.Identity("eldorado_lavoura","alta",
            "semeadura/adubo no IN e especie agricola no OUT; "
            "nenhuma outra cultura e presumida")
    if (farm and not crop_output and "cana" in oo and
            "canavazio" in ii and len(oo)<=3):
        return policy.Identity("eldorado_canavial","alta",
            "cana no OUT e carro canavieiro vazio no IN; "
            "nao e plantacao de milho/soja")
    # Distribuidor agricola: insumos ao mercado, sementes/maquinas no IN;
    # nao transmutar graos genericos no OUT em cultivo de soja ou milho.
    if (standard.role=="desconhecida" and
            {"milho","soja"} <= ci and "fertilizer" in oo and
            "big_bag_seed" in (ii | oo) and
            "tractors" in ii and not ("bois" in oo)):
        return policy.Identity("eldorado_comercio_rural","alta",
            "milho/soja recebidos e fertilizante expedido; "
            "graos genericos no OUT nao indicam especie")
    if (standard.role=="desconhecida" and
            {"milho","soja"} <= ci
            and "graos" in oo and not (co & {"milho","soja"})):
        return policy.Identity("eldorado_recebedor_graos","alta",
            "milho e soja no IN; OUT apenas graos genericos: "
            "nao simular expedicao dessas especies")
    if (standard.role=="desconhecida" and
            {"milho","soja"} <= ci and {"milho","soja"} <= co and
            len(oo)<=15):
        return policy.Identity("eldorado_armazem_graos","alta",
            "milho/soja em IN e OUT: entreposto, nao fazenda")
    # Centrais com fluxo extenso em ambos os sentidos fazem transbordo,
    # nao plantam todas as culturas presentes no catalogo.
    if (standard.role=="desconhecida" and len(ii)>=25 and
            len(oo)>=25 and len(ii & oo)>=20):
        return policy.Identity("eldorado_hub_bidirecional","alta",
            "dezenas de mercadorias iguais em IN/OUT: centro de "
            "distribuicao, sem fabricacao/cultivo comprovados")
    # Material de construcao: areias e betoneiras recebidas e
    # cimento no OUT, nao confundir com pedreira ou silo agricola.
    if (standard.role=="desconhecida" and "cement" in oo
            and {"areia","betoneira"} <= ii and len(oo)<15):
        return policy.Identity("eldorado_distribuidor_cimento","alta",
            "cimento expedido e operacao de betoneiras/areia; "
            "distribuicao documentada, nao prova fabrica de cimento")

    # Distribuidores sintéticos sem qualquer IN nao produzem centenas
    # de produtos. Preservar apenas cargas originais no OUT.
    if (standard.role=="desconhecida" and len(oo)>=65 and not ii):
        return policy.Identity("eldorado_hub_saida","alta",
            "catalogo multissetorial de saida sem IN; centro distribuidor "
            "nao equivale a produtor de todas as mercadorias")
    return None

def evaluate(company,category,direction,identity,policy):
    role=identity.role
    if not role.startswith("eldorado_"):
        return None
    ii,oo,ci,co=token_groups(company,policy)
    documented=category in (ci if direction=="in" else co)
    def yes(reason,source="SIMULACAO_ECONOMICA_ELDORADO"):
        return policy.Decision(True,reason,source,"media")
    def no(reason):
        return policy.Decision(False,reason,identity.evidence,"alta")
    if role=="eldorado_pecuaria":
        if direction=="in" and category in {"racao","sorgo"}:
            return yes("criacao bovina precisa receber alimentacao animal")
        if direction=="in" and category=="adubo" and category in ci:
            return yes("adubo documentado em propriedade com atividade mista",
                       "IN original de adubo")
        return no("criacao bovina nao demonstra plantio de milho, soja, "
                  "coco ou algodao; nenhuma expedicao Librelato comprovada")
    if role=="eldorado_lavoura":
        if direction=="out" and category in {"milho","soja","batata","laranja"}:
            return (yes("colheita especifica expedida pela lavoura",
                        "OUT original da especie agricola")
                    if category in co else no("especie nao declarada no OUT"))
        if direction=="in" and category=="adubo":
            return yes("lavoura consome fertilizante para plantio")
        return no("lavoura nao recebe racao sem animais comprovados nem "
                  "expede outra especie nao documentada")
    if role=="eldorado_canavial":
        if direction=="in" and category=="adubo":
            return yes("canavial recebe fertilizante para o cultivo")
        return no("cana-de-acucar nao equivale a soja, milho, sorgo "
                  "ou outras cargas do Librelato")
    if role in {"eldorado_recebedor_graos",
                "eldorado_hub_bidirecional",
                "eldorado_distribuidor_cimento"}:
        if documented:
            return yes("produto original na direcao correta da unidade",
                       "IN/OUT original da DEF; sem supor producao")
        return no("centro/fornecedor nao registra mercadoria nessa direcao")
    if role=="eldorado_comercio_rural":
        if documented and category in {"milho","soja","adubo"}:
            return yes("revenda rural: carga original na direcao IN/OUT",
                       "IN/OUT original da DEF")
        return no("revenda nao produz graos ausentes do OUT especifico")
    if role=="eldorado_armazem_graos":
        if documented and category in {"milho","soja","adubo"}:
            return yes("armazem movimenta especie original nessa direcao",
                       "IN/OUT original da DEF")
        return no("armazem nao comprova esta mercadoria nesta direcao")
    if role=="eldorado_hub_saida":
        if direction=="out" and category in co:
            return yes("centro de distribuicao com mercadoria documentada",
                       "OUT original da DEF; NAO significa producao")
        return no("hub sem entrada documentada ou produto no OUT")
    return None

def inherited_conflict(company,category,direction,policy):
    """Remover apenas fretes herdados contraditorios e sem IN/OUT real."""
    identity=getattr(company,"_eldorado_identity",None)
    if identity is None:return None
    ii,oo,ci,co=token_groups(company,policy)
    if category in (ci if direction=="in" else co):return None
    role=identity.role
    # Frete antigo herdado nao supera evidencia contraria da DEF.
    # So limitar atividades com perfil forte, exclusivamente no Eldorado.
    if role in {"eldorado_comercio_rural","eldorado_recebedor_graos",
                "eldorado_armazem_graos","eldorado_hub_saida",
                "eldorado_hub_bidirecional","eldorado_distribuidor_cimento"}:
        return ("Frete legado sem IN/OUT da mesma carga nessa direcao "
                "para atividade inferida por fluxo original")
    if role=="eldorado_lavoura" and direction=="out" and category not in {
            "algodao","coco"}:
        return "Lavoura nao produziu esta mercadoria no OUT original"
    if role=="eldorado_lavoura" and direction=="in" and category!="adubo":
        return "Lavoura nao comprovou compra desta mercadoria no IN"
    if role=="eldorado_pecuaria" and (
        direction=="out" or
        category in {"adubo","milho","soja","algodao","coco"}):
        return "Pecuaria documentada nao comprova este produto/direcao"
    if role=="eldorado_canavial" and (
        direction=="out" or category in {"milho","soja","algodao","coco"}):
        return "Canavial documentado nao equivale a lavoura de graos"
    if role=="eldorado_lavoura" and direction=="out" and category in {
            "milho","soja","batata","laranja"}:
        return "Especie agricola herdada sem prova no OUT original"
    return None

def export_translation_reports(companies,folder):
    """CSV verificavel das cargas originais inglesas e dos perfis inferidos."""
    root=__import__("pathlib").Path(folder)
    occurrences=Counter()
    for c in companies.values():
        for token in c.old_in:occurrences[(str(token),"IN")]+=1
        for token in c.old_out:occurrences[(str(token),"OUT")]+=1
    with (root/"TRADUCAO_DEF_ELDORADO.csv").open("w",newline="",encoding="utf-8-sig") as fp:
        wr=csv.writer(fp,delimiter=";")
        wr.writerow(["identificador_def","descricao_portugues","direcao","empresas"])
        for (tok,side),count in sorted(occurrences.items()):
            wr.writerow([tok,translate(tok),side,count])
    with (root/"PERFIS_ECONOMICOS_ELDORADO.csv").open("w",newline="",encoding="utf-8-sig") as fp:
        wr=csv.writer(fp,delimiter=";")
        wr.writerow(["empresa","setor_inferido","evidencia","entrada_def","saida_def"])
        for name,c in sorted(companies.items()):
            identity=getattr(c,"_eldorado_identity",None)
            if identity is None:continue
            wr.writerow([name,identity.role,identity.evidence,
                         ",".join(sorted(str(x) for x in c.old_in)),
                         ",".join(sorted(str(x) for x in c.old_out))])
