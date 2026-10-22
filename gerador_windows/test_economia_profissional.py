import unittest
import zipfile
import json
from pathlib import Path

from test_gerador import g, Regression, old, zip_write
import politica_economica as policy
import auditor_existentes as existing

class ProfessionalEconomyTests(unittest.TestCase):
    def test_real_map_sector_identifiers_with_false_positive_guards(self):
        cases={
            "superbh":"supermercado",
            "superabc":"supermercado",
            "mercado":"supermercado",
            "merc_guapo":"supermercado",
            "supergasbras":"desconhecida",
            "fazbalegraos":"fazenda",
            "fazcerragrao":"fazenda",
            "ms_faz_fern":"fazenda",
            "faze_paraiso":"fazenda",
            "go_alfa_tr":"transportadora",
            "pr_translov":"transportadora",
            "jampalog":"transportadora",
            "materialber":"materiais",
            "construaco":"obras",
            "madeiras3":"madeireira",
            "agrotec":"desconhecida",
            "sequoia":"desconhecida",
            "midwest":"desconhecida",
        }
        for company,expected in cases.items():
            with self.subTest(company=company):
                self.assertEqual(policy.classify(g.Company(company)).role,expected)

    def test_pallet_return_requires_original_out_and_recycling_buyer(self):
        market=g.Company("supermercado_centro",old_out={"pallets"})
        without=g.Company("supermercado_centro")
        receiver=g.Company("sucatao_ouro")
        self.assertTrue(policy.decide(market,"palete","out").allowed)
        self.assertFalse(policy.decide(without,"palete","out").allowed)
        self.assertTrue(policy.decide(receiver,"palete","in").allowed)
        self.assertFalse(policy.decide(receiver,"palete","out").allowed)

    def test_company_permanent_name_is_used_only_when_unambiguous(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            archive=Path(td)/"reais.zip"
            zip_write(archive,{
                "def/company/qxj.sii": (
                    b'SiiNunit\n{\n company_permanent : company.permanent.qxj {\n'
                    b' name: "Supermercado Bairro"\n }\n}\n'),
                "def/company/qxj/in/beer.sii":old("beer"),
                "def/company/abz.sii":b'name: "@@city.company_name@@"\n',
                "def/company/abz/out/grains.sii":old("corn"),
                "def/company/mx1.sii":b'name: "Transportadora e Supermercado"\n',
                "def/company/mx1/in/beer.sii":old("beer"),
            })
            companies,_=g.extract_map(archive)
            self.assertEqual(companies["qxj"].display_name,"Supermercado Bairro")
            self.assertEqual(policy.classify(companies["qxj"]).role,"supermercado")
            self.assertEqual(policy.classify(companies["abz"]).role,"desconhecida")
            self.assertEqual(policy.classify(companies["mx1"]).role,"desconhecida")

    def test_real_rbr_company_names_resolve_hierarchical_roles(self):
        # Casos presentes em AUDITORIA_RBR(2).json. O classificador
        # antigo classificava estes nomes como desconhecidos porque
        # reconhecia duas expressoes sobrepostas.
        cases=[
            ("batata_f","Batata Fazenda","fazenda_batata","batata"),
            ("batata_ms1","Fazenda de Batatas","fazenda_batata","batata"),
            ("depos_ribas","Depósito Materiais de Construção","materiais","cimento"),
        ]
        for identifier,label,role,category in cases:
            with self.subTest(company=identifier):
                company=g.Company(identifier,display_name=label)
                self.assertEqual(policy.classify(company).role,role)
                self.assertTrue(policy.decide(company,category,"out").allowed)
        # Sem compatibilidade presumida de empresa sem nome/sufixo.
        self.assertEqual(policy.classify(g.Company("depos_ribas")).role,
                         "desconhecida")
        self.assertEqual(policy.classify(g.Company(
            "mx1",display_name="Transportadora e Supermercado")).role,
            "desconhecida")

    def test_cimoagro_is_documented_agricultural_inputs_wholesaler(self):
        # Identificador do RBR + ramo confirmado em fontes publicas:
        # cimoagro.com.br e CNPJ com CNAE de fertilizantes/adubos.
        c=g.Company("cimoagro",display_name="Cimoagro")
        self.assertEqual(policy.classify(c).role,"agroinsumos")
        self.assertTrue(policy.decide(c,"adubo","out").allowed)
        self.assertTrue(policy.decide(c,"adubo","in").allowed)
        self.assertFalse(policy.decide(c,"bobina","out").allowed)

    def test_purchase_perspective_and_english_terms(self):
        cases=[
            ("fiat","bobina","out",False),
            ("fiat","bobina","in",True),
            ("gerdau","bobina","out",True),
            ("brasilog","batata","out",False),
            ("rasador","cerveja","out",False),
            ("eldorado_bananas","batata","in",False),
            ("eldorado_bananas","adubo","in",True),
            ("obra_construcao","cimento","in",True),
            ("obra_construcao","tijolo","in",True),
            ("obra_construcao","cimento","out",False),
            ("loja_material","cimento","out",True),
            ("loja_material","tijolo","out",True),
            ("agrish","adubo","out",True),
            ("ambev","cerveja","out",True),
            ("supermercado_centro","cerveja","in",True),
            ("serraria_ouro","madeira","out",True),
            ("serraria_ouro","palete","out",True),
            ("sucatao_ouro","palete","in",True),
            ("carmoprem","cimento","in",True),
            ("carmoprem","cimento","out",False),
            ("marmoraria_botrel","granito","out",True),
            ("carmoprem","bobina","out",False),
        ]
        for name,category,side,expected in cases:
            with self.subTest(name=name,category=category,side=side):
                c=g.Company(name)
                self.assertEqual(policy.decide(c,category,side).allowed,expected)
        self.assertEqual(policy.cargo_categories(["beverages"]),set())
        self.assertEqual(policy.cargo_categories(["potatoes"]),{"batata"})
        self.assertEqual(policy.cargo_categories(["bananas"]),set())
        self.assertEqual(policy.cargo_categories(["cott_seed"]),set())
        self.assertEqual(policy.cargo_categories(["marble"]),set())
        self.assertEqual(policy.cargo_categories(["steel_coils"]),{"bobina"})
        self.assertEqual(policy.classify(g.Company("mystery")).certainty,"indeterminada")
        mystery=g.Company("mystery",old_out={"steel_coils"})
        self.assertFalse(policy.decide(mystery,"bobina","out").allowed)

    def test_farms_need_crop_evidence_not_just_generic_label(self):
        farm=g.Company("fazenda_santa_rita",old_in={"fertilizer"},
                       old_out={"corn","soybeans"})
        self.assertTrue(policy.decide(farm,"milho","out").allowed)
        self.assertTrue(policy.decide(farm,"soja","out").allowed)
        self.assertFalse(policy.decide(farm,"batata","out").allowed)
        self.assertTrue(policy.decide(farm,"adubo","in").allowed)
        self.assertFalse(policy.decide(farm,"racao","in").allowed)
        farm.old_in.add("animal_feed")
        self.assertTrue(policy.decide(farm,"racao","in").allowed)


    def test_reported_rbr_industries_receive_only_economic_goods(self):
        examples=[
            ("ms_alg_ib","Algodoeira Irmãos Bürgel","beneficiadora_algodao",
             "algodao","out"),
            ("bechara","Moveis Bechara","fabrica_moveis","madeira","in"),
            ("moveis1","Modelo Móveis","fabrica_moveis","madeira","in"),
            ("marcenaria1","Marcenaria Água Clara","fabrica_moveis","madeira","in"),
            ("polimix1","Polimix","concreteira","cimento","in"),
            ("cercrystal","Cerveja Crystal","cervejaria","cerveja","out"),
            ("grupo_p","Grupo Petrópolis","cervejaria","cerveja","out"),
            ("leroy_merlin","Leroy Merlin","materiais","tijolo","out"),
            ("guarezi_m","Guarezi Material de Construção","materiais",
             "cimento","out"),
            ("compre_bem","Compre Bem","supermercado","cerveja","in"),
            ("mer_bh_itabi","Super Mercado BH","supermercado","cerveja","in"),
            ("martinmina","MartMinas","supermercado","cerveja","in"),
        ]
        for identifier,label,role,cargo,direction in examples:
            with self.subTest(identifier=identifier):
                c=g.Company(identifier,display_name=label)
                self.assertEqual(policy.classify(c).role,role)
                self.assertTrue(policy.decide(c,cargo,direction).allowed)
        self.assertFalse(policy.decide(g.Company(
            "bechara",display_name="Moveis Bechara"),"madeira","out").allowed)
        self.assertFalse(policy.decide(g.Company(
            "polimix1",display_name="Polimix"),"cimento","out").allowed)
        self.assertFalse(policy.decide(g.Company(
            "ms_alg_ib",display_name="Algodoeira Irmãos Bürgel"),"algodao","in").allowed)

    def test_grain_traders_require_original_cargo_evidence(self):
        for company,label in [
                ("g_cereal_rv","Grupo Cereal"),
                ("go_graos","Rio Verde Grãos"),
                ("ms_graos","Ms Grãos"),
                ("pr_anaconda","Anaconda Grãos"),
                ("amaggi","AMAGGI")]:
            with self.subTest(name=company):
                c=g.Company(company,display_name=label,old_in={"corn"})
                self.assertEqual(policy.classify(c).role,"comercio_graos")
                self.assertTrue(policy.decide(c,"milho","in").allowed)
                self.assertTrue(policy.decide(c,"milho","out").allowed)
                self.assertFalse(policy.decide(c,"soja","out").allowed)
                self.assertFalse(policy.decide(c,"sorgo","in").allowed)
                self.assertFalse(policy.decide(c,"adubo","out").allowed)

    def test_sorgo_animal_feed_chain_is_supported_without_fake_crops(self):
        agropecuaria=g.Company("agropecuaria_centro")
        pecuaria=g.Company("pecuaria_gado")
        fazenda=g.Company("fazenda_santa_luzia")
        self.assertTrue(policy.decide(agropecuaria,"sorgo","out").allowed)
        self.assertTrue(policy.decide(agropecuaria,"sorgo","in").allowed)
        self.assertTrue(policy.decide(pecuaria,"sorgo","in").allowed)
        self.assertFalse(policy.decide(pecuaria,"sorgo","out").allowed)
        # Fazenda sem criacao documentada nao deve receber sorgo
        # automaticamente nem alegar que o cultivou.
        self.assertFalse(policy.decide(fazenda,"sorgo","in").allowed)
        self.assertFalse(policy.decide(fazenda,"sorgo","out").allowed)
        fazenda.old_in.add("animal_feed")
        self.assertTrue(policy.decide(fazenda,"sorgo","in").allowed)
        fazenda.old_out.add("sorghum")
        self.assertTrue(policy.decide(fazenda,"sorgo","out").allowed)
        # Transportadora nao vira distribuidor apenas por nome generico.
        self.assertFalse(policy.decide(g.Company("transportadora_centro"),
                                       "sorgo","out").allowed)

    def test_complete_23_chains_and_company_city_instances(self):
        mapping={
            "fazenda_ouro":{"in":["fertilizer"],"out":["corn","soybeans","cotton","sorghum"]},
            "silo_armazen":{"in":["corn","soybeans"],"out":["corn","soybeans","sorghum"]},
            "agrish":{"out":["fertilizer","animal_feed"]},
            "serraria_ouro":{"out":["timber","pallets"]},
            "textil_ouro":{"in":["cotton"]},
            "votoran":{"out":["cement"]},
            "loja_material":{"in":["cement","bricks","timber"],"out":["cement"]},
            "obra_construcao":{"in":["cement","bricks","granite","timber"]},
            "fazenda_potato":{"out":["potatoes"]},
            "fazenda_orange":{"out":["oranges"]},
            "supermercado_centro":{"in":["potatoes","oranges","beer"]},
            "gerdau":{"out":["steel_coils"]},
            "fiat":{"in":["steel_coils"],"out":["steel_coils"]},
            "ambev":{"out":["beer"]},
            "ceramica_ouro":{"out":["bricks"]},
            "pedreira_ouro":{"out":["granite"]},
            "marmoraria_ouro":{"in":["granite"]},
            "sucatao_ouro":{"in":["pallets"]},
            "feedmill_ouro":{"out":["animal_feed"],"in":["sorghum","corn","soybeans"]},
            "pecuaria_gado":{"in":["animal_feed"]},
            "brasilog":{"out":["potatoes"]},
            "eldorado_bananas":{"in":["potatoes","fertilizer"]}
        }
        self.fixture=Regression("test_neutralization")
        self.fixture.setUp()
        try:
            files={}
            for company,dirs in mapping.items():
                for side,tokens in dirs.items():
                    for token in tokens:
                        files[f"{company}/{side}/{token}.sii"]=old(token)
                for city in ("betim","lavras"):
                    files[f"{company}/editor/{city}.sii"]="SiiNunit\n{}\n"
            map_path=self.fixture.root/"realistic_v3_eldorado.zip"
            zip_write(map_path,files)
            companies,_=g.extract_map(map_path)
            cov=policy.coverage(companies,g.MANIFEST)
            self.assertEqual(cov["cargas_com_pares"],23)
            self.assertEqual(cov["total_instancias_editor"],len(mapping)*2)
            self.assertEqual(cov["empresas_sem_editor"],0)
            routes=cov["rotas"]
            self.assertNotIn("fiat",routes["carga9"]["origens_lista"])
            self.assertIn("fiat",routes["carga9"]["destinos_lista"])
            self.assertNotIn("brasilog",routes["carga7"]["origens_lista"])
            self.assertNotIn("eldorado_bananas",routes["carga7"]["destinos_lista"])
            self.assertIn("ambev",routes["carga12"]["origens_lista"])
            inp={**self.fixture.inp,"maps":{"Eldorado":map_path}}
            gen_dir=self.fixture.root/"generated_v3"
            result=g.generate(inp,gen_dir,professional=True)
            self.assertEqual(len(result),1)
            self.assertEqual(result[0][2]["cobertura_23_cargas"]["cargas_com_rota"],23)
            self.assertTrue((gen_dir/"Eldorado_EMPRESAS_E_CIDADES.csv").exists())
            with zipfile.ZipFile(result[0][1]) as z:
                self.assertNotIn("def/company/fiat/out/carga9.sii",z.namelist())
                self.assertIn("def/company/fiat/in/carga9.sii",z.namelist())
                self.assertIn("def/company/agrish/out/carga3.sii",z.namelist())
                self.assertIn("def/company/obra_construcao/in/carga13.sii",z.namelist())
            # Auditoria da Company existente: preserva todas as unidades.
            audit_dir=self.fixture.root/"revised_v3"
            result2=existing.run(g,{"Eldorado":{"existing":result[0][1],
                                                "map_def":map_path}},audit_dir,
                                 professional=True,
                                 source_files={"mod":self.fixture.inp["mod"],
                                               "def1":self.fixture.inp["def1"],
                                               "def2":self.fixture.inp["def2"]})
            self.assertEqual(result2[0]["rotas_completas_depois"],23)
            self.assertEqual(result2[0]["matriz_empresa_cidade"]["total_instancias_editor"],
                             len(mapping)*2)
            self.assertTrue((audit_dir/"COBERTURA_EMPRESA_CIDADE_ELDORADO.csv").exists())
        finally:
            self.fixture.tearDown()

    def test_professional_gate_blocks_missing_23_no_fake_routes(self):
        fixture=Regression("test_neutralization")
        fixture.setUp()
        try:
            source={**fixture.inp,"maps":{"Minas_Gerais":fixture.inp["maps"]["Minas_Gerais"]}}
            with self.assertRaisesRegex(ValueError,"23 cargas"):
                g.generate(source,fixture.root/"incomplete",professional=True)
            self.assertFalse(list((fixture.root/"incomplete").glob("*.scs")))
            self.assertTrue(list((fixture.root/"incomplete").glob("*COBERTURA_23_CARGAS.json")))
        finally:
            fixture.tearDown()
if __name__=="__main__":
    unittest.main()
