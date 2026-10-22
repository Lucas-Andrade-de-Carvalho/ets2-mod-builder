"""RBR: fontes economicas reais, direcoes corretas e cobertura por empresa."""
import json
import tempfile
import unittest
from pathlib import Path
from test_gerador import g
import politica_economica as p
import cobertura_maxima_rbr as coverage


class RBRRolePolicy(unittest.TestCase):
    def test_important_new_producers_consumers(self):
        cases=[
            ("citrosuco1","processadora_citricos",("laranja","in"),("laranja","out")),
            ("citrosuco2","processadora_citricos",("laranja","in"),("cerveja","out")),
            ("frucamp","processadora_citricos",("laranja","in"),("laranja","out")),
            ("greenplac","fabrica_paineis",("madeira","in"),("madeira","out")),
            ("eternit","fabrica_fibrocimento",("cimento","in"),("cimento","out")),
            ("marcegaglia","metalurgica",("bobina","in"),("bobina","out")),
            ("pr_samsclub","supermercado",("cerveja","in"),("cerveja","out")),
            ("mt_mer_reti","supermercado",("laranja","in"),("cimento","in")),
            ("kaarfor","supermercado",("coco","in"),("coco","out")),
            ("sanbuilders","obras",("tijolo","in"),("tijolo","out")),
            ("konstnr","obras",("cimento","in"),("cimento","out")),
            ("cons_rbr","obras",("granito","in"),("granito","out")),
            ("const_c_g","obras",("madeira","in"),("madeira","out")),
            ("coluna_ma","obras",("tijolo","in"),("cerveja","out")),
            ("made_itaja","revenda_madeiras",("madeira","out"),("palete","out")),
            ("go_madeirani","revenda_madeiras",("madeira","in"),("adubo","out")),
            ("ms_vale_mad","revenda_madeiras",("madeira","out"),("cerveja","out")),
            ("extr_rio_p2","madeireira",("madeira","out"),("bobina","out")),
            ("cana_acucar","plantacao_cana",("adubo","in"),("milho","out")),
            ("cana_acucar2","plantacao_cana",("adubo","in"),("adubo","out")),
            ("cana_ms1","plantacao_cana",("adubo","in"),("soja","out")),
            ("rodoviaria11","infra_passageiros",None,("cerveja","in")),
            ("rodo_mg1","infra_passageiros",None,("cimento","out")),
            ("enel_stb","infra_passageiros",None,("adubo","in")),
        ]
        for id,role,positive,negative in cases:
            with self.subTest(company=id):
                c=g.Company(id)
                self.assertEqual(p.classify(c).role,role)
                if positive:
                    self.assertTrue(p.decide(c,*positive).allowed)
                self.assertFalse(p.decide(c,*negative).allowed)
    def test_passenger_terminals_with_inherited_cargo_are_neutralized(self):
        from auditor_existentes import proven_incompatibility
        for id in ("rodoviaria10","rodo_mg1","enel_stb","prf_nlima"):
            with self.subTest(company=id):
                c=g.Company(id)
                c.role=p.classify(c).role
                self.assertEqual(c.role,"infra_passageiros")
                self.assertIsNotNone(proven_incompatibility(c,"cerveja","in"))
                self.assertIsNotNone(proven_incompatibility(c,"palete","out"))
        self.assertIsNone(proven_incompatibility(
            g.Company("pr_samsclub",role="supermercado"),"cerveja","in"))

    def test_agromec_votuporanga_is_fertilizer_only(self):
        c=g.Company("agromecvo",display_name="Agromec")
        self.assertEqual(p.classify(c).role,"revenda_fertilizante")
        self.assertTrue(p.decide(c,"adubo","in").allowed)
        self.assertTrue(p.decide(c,"adubo","out").allowed)
        self.assertFalse(p.decide(c,"racao","out").allowed)
        self.assertFalse(p.decide(c,"sorgo","in").allowed)
        self.assertFalse(p.decide(c,"bobina","out").allowed)

    def test_eldorado_cargo_receivers_from_real_company_ids(self):
        for id in ("eldconst","eldconst2"):
            with self.subTest(id=id):
                c=g.Company(id)
                self.assertEqual(p.classify(c).role,"obras")
                for cat in ("cimento","tijolo","madeira","granito"):
                    self.assertTrue(p.decide(c,cat,"in").allowed)
                    self.assertFalse(p.decide(c,cat,"out").allowed)
                self.assertFalse(p.decide(c,"cerveja","in").allowed)
        seller=g.Company("itaacos")
        self.assertEqual(p.classify(seller).role,"revenda_aco")
        self.assertFalse(p.decide(seller,"bobina","in").allowed)
        seller.old_in.add("steel_coil")
        self.assertTrue(p.decide(seller,"bobina","in").allowed)
        self.assertFalse(p.decide(seller,"bobina","out").allowed)

    def test_resell_steel_coils_only_with_original_def_proof(self):
        c=g.Company("br_ferro")
        self.assertEqual(p.classify(c).role,"revenda_aco")
        self.assertFalse(p.decide(c,"bobina","in").allowed)
        self.assertFalse(p.decide(c,"bobina","out").allowed)
        c.old_in.add("steel_coils")
        self.assertTrue(p.decide(c,"bobina","in").allowed)
        self.assertFalse(p.decide(c,"bobina","out").allowed)
        c.old_out.add("steel_coils")
        self.assertTrue(p.decide(c,"bobina","out").allowed)
        self.assertFalse(p.decide(c,"tijolo","out").allowed)
    def test_ambiguous_unknowns_remain_unclassified(self):
        for id in ("agro_capim","mt_agrogarca","carga_des3","porto1",
                   "pr_deposito","rubinei","madei_generico_falso"):
            with self.subTest(id=id):
                self.assertEqual(p.classify(g.Company(id)).role,"desconhecida")


class EvidenceFromRealDEF(unittest.TestCase):
    def test_permanent_only_company_must_enter_coverage(self):
        import zipfile
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"def_map.scs"
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("def/company/ambev/out/beer.sii",
                           'SiiNunit\n{\ncargo_data : .beer {\n cargo: cargo.beer\n}\n}\n')
                z.writestr("def/company/unit42.sii",
                           'SiiNunit\n{\ncompany_permanent : company.unit42 {\n name: "Construcao Brasil"\n}\n}\n')
            companies,_=g.extract_map(path)
            self.assertIn("unit42",companies)
            site=companies["unit42"]
            self.assertFalse(site.old_in or site.old_out)
            self.assertEqual(site.display_name,"Construcao Brasil")
            self.assertEqual(p.classify(site).role,"obras")
            self.assertTrue(p.decide(site,"cimento","in").allowed)
            self.assertFalse(p.decide(site,"cimento","out").allowed)

    def test_original_24_ids_are_exact_evidence_without_wrong_categories(self):
        self.assertEqual(len(p.LIBRELATO_ID_CATEGORIES), 24)
        self.assertEqual(p.cargo_categories({"carga1","carga21","carga24"}),
                         {"milho","soja","coco"})
        self.assertEqual(p.cargo_categories({"carga17","carga10"}),
                         {"racao","cimento"})
        self.assertNotIn("laranja",p.cargo_categories({"carga17"}))
        self.assertEqual(p.cargo_categories({"carga25","carga999"}),set())

    def test_farm_can_export_only_documented_crops(self):
        farm=g.Company("fazenda_confiavel",old_out={"carga1","carga21"})
        self.assertEqual(p.classify(farm).role,"fazenda")
        self.assertTrue(p.decide(farm,"milho","out").allowed)
        self.assertTrue(p.decide(farm,"soja","out").allowed)
        self.assertFalse(p.decide(farm,"coco","out").allowed)
        self.assertFalse(p.decide(farm,"algodao","out").allowed)

    def test_grain_silo_can_receive_documented_original_id(self):
        silo=g.Company("silo_documentado",old_in={"carga1"})
        self.assertTrue(p.decide(silo,"milho","in").allowed)
        self.assertFalse(p.decide(silo,"soja","in").allowed)
        # Silos podem reexpedir o grao que receberam e armazenaram.
        self.assertTrue(p.decide(silo,"milho","out").allowed)

    def test_city_requires_documented_city_and_prefab_not_filename(self):
        comp=g.Company("constdivi")
        comp.editor_files={
            "def/company/constdivi/editor/cidade_inventada.sii":
                b"SiiNunit\n{}\n",
            "def/company/constdivi/editor/divinopolis.sii":
                b"SiiNunit\n{\ncompany_def : .divinopolis {\n"
                b" city: divinopolis\n prefab: mg_prefab_01\n}\n}\n",
        }
        refs=p.city_references(comp)
        self.assertEqual(len(refs),1)
        self.assertEqual(refs[0]["cidade"],"divinopolis")
        self.assertEqual(refs[0]["prefab_declarado"],"mg_prefab_01")
        self.assertFalse(refs[0]["prefab_confirmado"])
        coverage=p.coverage({comp.name:comp},{6:("cimento","Cimento")})
        self.assertEqual(coverage["total_instancias_editor"],1)
        self.assertEqual(coverage["instancias_cidade"][0]["cidade"],"divinopolis")

    def test_real_map_economic_roles_without_overgeneralizing(self):
        roles={"abcconstru":"obras","constdivi":"obras",
               "constjuatub2":"obras","construai2":"obras",
               "ceramfazpgra":"ceramica","cerami_parap":"ceramica",
               "marmolider":"marmoraria","curralracoes":"revenda_racao",
               "araraserr":"madeireira","extrmadserr":"madeireira"}
        for identifier,role in roles.items():
            with self.subTest(identifier=identifier):
                self.assertEqual(p.classify(g.Company(identifier)).role,role)
        self.assertTrue(p.decide(g.Company("constdivi"),"cimento","in").allowed)
        self.assertFalse(p.decide(g.Company("constdivi"),"cimento","out").allowed)
        self.assertTrue(p.decide(g.Company("curralracoes"),"racao","out").allowed)
        self.assertFalse(p.decide(g.Company("curralracoes"),"sorgo","out").allowed)
        self.assertEqual(p.classify(g.Company("carga_des3")).role,"desconhecida")


class ProvenEconomicExpansion(unittest.TestCase):
    def test_real_csn_arcos_mining_not_steel_or_granite(self):
        for cid in ("csnarcos","csnarcos2","csnarcos3","csnarcos4"):
            with self.subTest(cid=cid):
                c=g.Company(cid,old_out={"calcario","brita"})
                self.assertEqual(p.classify(c).role,"mineracao_calcario")
                for product in ("bobina","granito","cimento"):
                    self.assertFalse(p.decide(c,product,"out").allowed)

    def test_abbreviated_mg_crop_and_grain_ids_require_original_evidence(self):
        farm=g.Company("batatfazpgra",old_out={"batata"})
        self.assertEqual(p.classify(farm).role,"fazenda_batata")
        self.assertTrue(p.decide(farm,"batata","out").allowed)
        self.assertFalse(p.decide(farm,"soja","out").allowed)
        self.assertEqual(p.classify(g.Company("batatfazpgra")).role,"desconhecida")
        broker=g.Company("araragrao",old_in={"corn"},old_out={"corn"})
        self.assertEqual(p.classify(broker).role,"comercio_graos")
        self.assertTrue(p.decide(broker,"milho","in").allowed)
        self.assertTrue(p.decide(broker,"milho","out").allowed)
        self.assertFalse(p.decide(broker,"soja","out").allowed)
        self.assertEqual(p.classify(g.Company("araragrao")).role,"desconhecida")

    def test_real_mg_batata_store_in_out_cargo_ids_need_evidence(self):
        c=g.Company("casabatata",old_in={"batata","milho","racao"},
                    old_out={"batata","milho","racao"})
        self.assertEqual(p.classify(c).role,"revenda_agricola_documentada")
        for cat in ("batata","milho","racao"):
            self.assertTrue(p.decide(c,cat,"in").allowed)
            self.assertTrue(p.decide(c,cat,"out").allowed)
        self.assertFalse(p.decide(c,"coco","out").allowed)
        self.assertFalse(p.decide(c,"soja","in").allowed)
        unproven=g.Company("casabatata")
        self.assertFalse(p.decide(unproven,"batata","out").allowed)

    def test_real_mg_beer_distributor_uses_brand_not_generic_bebidas(self):
        c=g.Company("jmbebidas",old_in={"amstel","brahma","bebidas"},
                    old_out={"budweiser","skol","refri"})
        self.assertEqual(p.classify(c).role,"distribuidor_cerveja")
        self.assertTrue(p.decide(c,"cerveja","in").allowed)
        self.assertTrue(p.decide(c,"cerveja","out").allowed)
        unknown=g.Company("jmbebidas",old_out={"bebidas","agua600","refri"})
        self.assertFalse(p.decide(unknown,"cerveja","out").allowed)
        self.assertNotIn("cerveja",p.cargo_categories({"bebidas","refri"}))

    def test_recognize_documented_grocery_brands_without_inventing_factory(self):
        for cid in ("martmix","villefort","hipermax","walmart","spani"):
            with self.subTest(cid=cid):
                c=g.Company(cid)
                self.assertEqual(p.classify(c).role,"supermercado")
                self.assertTrue(p.decide(c,"cerveja","in").allowed)
                self.assertFalse(p.decide(c,"cerveja","out").allowed)
                self.assertFalse(p.decide(c,"bobina","in").allowed)


class DirectionalINOUTInference(unittest.TestCase):
    def test_anonymous_farm_detected_from_fertilizer_in_and_crop_out(self):
        farm=g.Company("unidade_xyz",old_in={"fertilizer"},
                       old_out={"corn","soybeans"})
        role=p.classify(farm)
        self.assertEqual(role.role,"fazenda")
        self.assertEqual(role.certainty,"alta")
        self.assertIn("inferencia",role.evidence)
        report=p.coverage({farm.name:farm},g.MANIFEST)
        item=report["empresas"][0]
        self.assertEqual(item["atividade"],"fazenda")
        self.assertEqual(set(item["out_esperados"]),
                         {"carga1","carga2","carga21","carga22"})
        self.assertEqual(set(item["in_esperados"]),{"carga3"})
        self.assertNotIn("carga24",item["out_esperados"])
        self.assertNotIn("carga23",item["out_esperados"])
        from auditor_existentes import can_add
        farm.role=role.role
        farm.explicit_role=True
        self.assertTrue(can_add(g,farm,"milho","out","Minas_Gerais",
                                professional=True))
        self.assertTrue(can_add(g,farm,"adubo","in","RBR",
                                professional=True))
        self.assertFalse(can_add(g,farm,"soja","in","RBR",
                                 professional=True))

    def test_anonymous_farm_with_generic_grains_never_invents_species(self):
        farm=g.Company("prod_42",old_in={"fertilizer"},old_out={"graos"})
        self.assertEqual(p.classify(farm).role,"fazenda")
        report=p.coverage({farm.name:farm},g.MANIFEST)["empresas"][0]
        self.assertEqual(report["in_esperados"],["carga3"])
        self.assertEqual(report["out_esperados"],[])

    def test_bidirectional_grain_trade_is_not_a_farm(self):
        depot=g.Company("unidade_876",old_in={"corn","soybeans"},
                        old_out={"corn","soybeans"})
        role=p.classify(depot)
        self.assertEqual(role.role,"comercio_graos")
        self.assertIn("armazenagem",role.evidence)
        report=p.coverage({depot.name:depot},g.MANIFEST)["empresas"][0]
        cargo={"carga1","carga2","carga21","carga22"}
        self.assertEqual(set(report["in_esperados"]),cargo)
        self.assertEqual(set(report["out_esperados"]),cargo)
        self.assertNotIn("carga3",report["in_esperados"])
        self.assertNotIn("carga23",report["out_esperados"])

    def test_transport_or_conflicting_flows_are_not_misclassified(self):
        transport=g.Company("transportadora_exemplo",
                            old_in={"fertilizer"},old_out={"corn"})
        self.assertEqual(p.classify(transport).role,"transportadora")
        self.assertFalse(p.decide(transport,"milho","out").allowed)
        contradictory=g.Company("company_nebulosa",
                                old_in={"fertilizer","corn"},
                                old_out={"corn","steel_coils"})
        self.assertEqual(p.classify(contradictory).role,"desconhecida")
        self.assertFalse(p.decide(contradictory,"soja","out").allowed)

    def test_martminas_store_gets_all_proven_grocery_categories(self):
        market=g.Company("MartMinas")
        self.assertEqual(p.classify(market).role,"supermercado")
        manifest={**g.MANIFEST,24:("coco","Coco")}
        row=p.coverage({market.name:market},manifest)["empresas"][0]
        self.assertEqual(set(row["in_esperados"]),
                         {"carga7","carga8","carga12","carga24"})
        self.assertEqual(row["out_esperados"],[])

    def test_anonymous_food_trader_preserves_documentary_product_limit(self):
        c=g.Company("company_anonymous",old_in={"beer","potatoes","oranges"})
        self.assertEqual(p.classify(c).role,"comercio_alimentos_inferido")
        row=p.coverage({c.name:c},g.MANIFEST)["empresas"][0]
        self.assertEqual(set(row["in_esperados"]),
                         {"carga7","carga8","carga12"})
        self.assertEqual(row["out_esperados"],[])
        self.assertNotIn("carga24",row["in_esperados"])

    def test_original_librelato_cargo_ids_support_directional_inference(self):
        c=g.Company("agro_anonymous",old_in={"carga3"},
                    old_out={"carga1","carga2"})
        self.assertEqual(p.classify(c).role,"fazenda")
        self.assertTrue(p.decide(c,"milho","out").allowed)
        self.assertTrue(p.decide(c,"adubo","in").allowed)
        self.assertFalse(p.decide(c,"cerveja","in").allowed)


class FictionalCompanySectorInference(unittest.TestCase):
    """As 24 cargas devem ser avaliadas SEM tabela de empresas reais."""

    def test_fictional_feed_factory_inputs_and_outputs(self):
        comp=g.Company("empresa_zx_001",old_in={"corn","soybeans"},
                       old_out={"animal_feed"})
        ident=p.classify(comp)
        self.assertEqual(ident.role,"fabrica_racao_inferida")
        row=p.coverage({comp.name:comp},g.MANIFEST)["empresas"][0]
        self.assertEqual(set(row["in_esperados"]),
                         {"carga1","carga2","carga21","carga22"})
        self.assertEqual(set(row["out_esperados"]),
                         {"carga17","carga18","carga19","carga20"})
        self.assertNotIn("carga23",row["in_esperados"])

    def test_fictional_industries_from_input_material_to_output_product(self):
        candidates=[
            ("alfa_x7",{"limestone"},{"cement"},"cimenteira_inferida","cimento"),
            ("lote_42",{"argila"},{"bricks"},"ceramica_inferida","tijolo"),
            ("logica_x",{"oranges"},{"orange_juice"},"processadora_citricos","laranja"),
            ("santa_x",{"wood"},{"furniture"},"fabrica_moveis","madeira"),
            ("fabrica_a8",{"cotton"},{"fabrics"},"textil","algodao"),
            ("zaf_991",{"animal_feed"},{"cattle"},"pecuaria","racao"),
        ]
        for company,orig_in,orig_out,role,category in candidates:
            with self.subTest(company=company):
                obj=g.Company(company,old_in=orig_in,old_out=orig_out)
                self.assertEqual(p.classify(obj).role,role)
                if role in {"cimenteira_inferida","ceramica_inferida"}:
                    self.assertTrue(p.decide(obj,category,"out").allowed)
                    self.assertFalse(p.decide(obj,category,"in").allowed)
                else:
                    self.assertTrue(p.decide(obj,category,"in").allowed)
                    self.assertFalse(p.decide(obj,category,"out").allowed)

    def test_fictional_building_store_vs_building_receiver(self):
        store=g.Company("company_4e2",old_in={"cement","bricks"},
                        old_out={"cement","bricks"})
        consumer=g.Company("company_9y2",old_in={"cement","bricks","wood"})
        self.assertEqual(p.classify(store).role,"comercio_materiais_inferido")
        self.assertEqual(p.classify(consumer).role,"consumidor_materiais_inferido")
        for n,(cat,title) in g.MANIFEST.items():
            cargo="carga"+str(n)
            if cat in {"cimento","tijolo"}:
                self.assertTrue(p.decide(store,cat,"in").allowed)
                self.assertTrue(p.decide(store,cat,"out").allowed)
            elif cat=="madeira":
                self.assertFalse(p.decide(store,cat,"out").allowed)
            if cat in {"cimento","tijolo","madeira"}:
                self.assertTrue(p.decide(consumer,cat,"in").allowed)
                self.assertFalse(p.decide(consumer,cat,"out").allowed)
        self.assertFalse(p.decide(consumer,"granito","in").allowed)

    def test_random_ids_and_ambiguous_industries_do_not_fabricate_cargo(self):
        cases=[
            g.Company("zzz999"),
            g.Company("x_nohit",old_in={"limestone"}),
            g.Company("x_mixed",old_in={"fertilizer","corn"},
                      old_out={"corn","beer"}),
            g.Company("x_builder",old_in={"cement","beer"},
                      old_out={"bricks"}),
            g.Company("x_feeds",old_in={"corn"},old_out={"beer"}),
        ]
        for c in cases:
            with self.subTest(company=c.name):
                self.assertEqual(p.classify(c).role,"desconhecida")
                self.assertFalse(p.decide(c,"milho","out").allowed)
                self.assertFalse(p.decide(c,"cimento","in").allowed)

    def test_audit_matrix_contains_every_fictional_company(self):
        examples={
            "ficticia_001":g.Company("ficticia_001",old_in={"fertilizer"},
                                     old_out={"corn"}),
            "ficticia_002":g.Company("ficticia_002",old_in={"cement","bricks"}),
            "ficticia_003":g.Company("ficticia_003"),
        }
        territory=p.coverage(examples,{1:("milho","Milho"),
                                       6:("cimento","Cimento"),
                                       13:("tijolo","Tijolos")})
        self.assertEqual(territory["total_empresas"],3)
        by_id={item["empresa"]:item for item in territory["empresas"]}
        self.assertEqual(by_id["ficticia_001"]["atividade"],"fazenda")
        self.assertEqual(by_id["ficticia_002"]["atividade"],
                         "consumidor_materiais_inferido")
        self.assertEqual(by_id["ficticia_003"]["atividade"],"desconhecida")
        self.assertEqual(by_id["ficticia_001"]["in_esperados"],[])
        self.assertEqual(by_id["ficticia_002"]["out_esperados"],[])


class RBRCoverageReport(unittest.TestCase):
    def fake(self):
        objs={
            "citrosuco1":g.Company("citrosuco1"),
            "frucamp":g.Company("frucamp"),
            "rodoviaria11":g.Company("rodoviaria11"),
            "agro_duvidoso":g.Company("agro_duvidoso"),
        }
        for c in objs.values():
            c.role=p.classify(c).role
        labels=[{
                "empresa":id,
                "atividade":c.role,
                "in_esperados":(["carga8"] if c.role=="processadora_citricos" else []),
                "out_esperados":[],
            } for id,c in objs.items()]
        from collections import defaultdict
        active=defaultdict(lambda:{"in":set(),"out":set()})
        active["citrosuco1"]["in"].add("carga8")
        active["frucamp"]["in"].add("carga8")
        return objs,{"empresas":labels,"instancias_cidade":[]},active

    def test_unknown_counts_use_same_documentary_role_as_territorial_matrix(self):
        companies,territory,active=self.fake()
        # Regressao: a classificacao guardada em c.role pode estar
        # desatualizada, mas os dois relatorios devem concordar.
        companies["frucamp"].role="desconhecida"
        companies["agro_duvidoso"].role="supermercado"
        report=coverage.assess(
            companies,territory,active,
            {i:("laranja","Sacos de Laranja") for i in range(24)},
            {"cargas_com_par_economico_comprovavel":24,
             "cargas_candidatas_teste_ets2":24})
        self.assertEqual(
            report["empresas_sem_classificacao"],
            sum(r["atividade"]=="desconhecida" for r in territory["empresas"]))
        self.assertEqual(report["empresas_sem_classificacao"],1)
        rows={r["empresa"]:r for r in report["empresas"]}
        self.assertEqual(rows["agro_duvidoso"]["status"],
                         "REVISAR_POSSIVEL_COMPATIBILIDADE")
        self.assertEqual(rows["frucamp"]["status"],"COMPATIVEL_CONTEMPLADA")

    def test_city_unknown_counts_follow_documentary_matrix_not_mutable_cache(self):
        companies,territory,active=self.fake()
        territory["instancias_cidade"]=[
            {"empresa":"frucamp","cidade":"divinopolis",
             "in_esperados":["carga8"],"out_esperados":[]},
            {"empresa":"agro_duvidoso","cidade":"divinopolis",
             "in_esperados":[],"out_esperados":[]},
        ]
        companies["frucamp"].role="desconhecida"
        companies["agro_duvidoso"].role="supermercado"
        result=coverage.assess(
            companies,territory,active,
            {8:("laranja","Sacos de Laranja")},
            {"cargas_com_par_economico_comprovavel":0,
             "cargas_candidatas_teste_ets2":0})
        city=result["cidades"][0]
        self.assertEqual(city["empresas_compativeis"],1)
        self.assertEqual(city["empresas_compativeis_cobertas"],1)
        self.assertEqual(city["empresas_sem_atividade_identificada"],
                         ["agro_duvidoso"])
        self.assertEqual(city["situacao"],"REVISAO_COMPATIBILIDADE")

    def test_every_company_is_accounted_for_without_fake_completion(self):
        companies,territory,active=self.fake()
        quality={
            "cargas_com_par_economico_comprovavel":24,
            "cargas_candidatas_teste_ets2":24}
        data=coverage.assess(companies,territory,active,
                              {i:("laranja","Sacos de Laranja") for i in range(24)},
                              quality)
        self.assertEqual(data["total_empresas_def"],4)
        self.assertEqual(data["empresas_reconhecidas_com_ao_menos_uma_carga"],2)
        self.assertEqual(data["empresas_reconhecidas_totalmente_contempladas"],2)
        self.assertEqual(data["empresas_classificadas_sem_carga_nas_24"],1)
        self.assertEqual(data["empresas_sem_classificacao"],1)
        self.assertEqual(data["desconhecidas_com_sinais_de_carga_a_investigar"],1)
        self.assertEqual(data["cobertura_empresas_reconhecidas_pct"],100.0)
        self.assertFalse(data["cobertura_100_por_cento_comprovada"])
        with tempfile.TemporaryDirectory() as t:
            coverage.write(t,data)
            result=json.loads((Path(t)/"COBERTURA_MAXIMA_RBR.json").read_text())
            self.assertEqual(len(result["empresas"]),4)
            self.assertTrue((Path(t)/"COBERTURA_MAXIMA_RBR.csv").is_file())
            review=Path(t)/"RBR_REVISAO_ECONOMICA_PRIORIZADA.csv"
            self.assertTrue(review.is_file())
            import csv
            with review.open(encoding="utf-8-sig",newline="") as source:
                review_rows=list(csv.DictReader(source,delimiter=";"))
            self.assertEqual(len(review_rows),1)
            self.assertEqual(review_rows[0]["empresa"],"agro_duvidoso")

    def test_perfect_cargo_pairs_never_homologate_compatible_companies_without_city(self):
        companies,territory,active=self.fake()
        for missing in ("rodoviaria11","agro_duvidoso"):
            del companies[missing]
        territory["empresas"]=[
            row for row in territory["empresas"] if row["empresa"] in companies]
        proof=coverage.assess(
            companies,territory,active,{8:("laranja","Sacos de Laranja")},
            {"cargas_com_par_economico_comprovavel":1,
             "cargas_candidatas_teste_ets2":1})
        self.assertEqual(proof["empresas_sem_classificacao"],0)
        self.assertEqual(proof["empresas_reconhecidas_com_lacunas"],0)
        self.assertEqual(proof["empresas_compativeis_sem_editor_valido"],2)
        self.assertFalse(proof["cobertura_100_por_cento_comprovada"])

    def test_invalid_editor_files_do_not_inflate_territorial_coverage(self):
        companies,territory,active=self.fake()
        companies["citrosuco1"].editor_files={
            "def/company/citrosuco1/editor/fiction.sii":b"SiiNunit {}"}
        territory["instancias_cidade"]=[
            {"empresa":"frucamp","cidade":"documented_city",
             "in_esperados":["carga8"],"out_esperados":[]}]
        report=coverage.assess(companies,territory,active,
                {8:("laranja","Sacos de Laranja")},
                {"cargas_com_par_economico_comprovavel":0,
                 "cargas_candidatas_teste_ets2":0})
        rows={r["empresa"]:r for r in report["empresas"]}
        self.assertEqual(rows["citrosuco1"]["total_instancias_editor"],0)
        self.assertEqual(rows["frucamp"]["total_instancias_editor"],1)
        self.assertEqual(report["instancias_editor_detectadas"],1)
        self.assertEqual(report["empresas_sem_editor"],3)

    def test_same_company_coverage_contract_for_all_three_maps(self):
        companies,territory,active=self.fake()
        quality={"cargas_com_par_economico_comprovavel":24,
                 "cargas_candidatas_teste_ets2":24}
        cargo_manifest={i:("laranja","Sacos de Laranja") for i in range(24)}
        result=coverage.assess(companies,territory,active,cargo_manifest,quality)
        self.assertEqual(result["empresas_sem_editor"],4)
        self.assertEqual(result["cidades_identificadas"],0)
        self.assertFalse(result["cobertura_100_por_cento_comprovada"])
        with tempfile.TemporaryDirectory() as temp:
            for name in ("RBR","ELDORADO","MINAS_GERAIS"):
                coverage.write(temp,result,name)
                self.assertTrue((Path(temp)/("COBERTURA_MAXIMA_"+name+".json")).exists())
                self.assertTrue((Path(temp)/("COBERTURA_MAXIMA_"+name+".csv")).exists())
                self.assertTrue((Path(temp)/(name+"_REVISAO_ECONOMICA_PRIORIZADA.csv")).exists())
                loaded=json.loads((Path(temp)/("COBERTURA_MAXIMA_"+name+".json")).read_text())
                self.assertEqual(loaded["total_empresas_def"],4)
                self.assertEqual(loaded["empresas_sem_classificacao"],1)
            self.assertEqual(
                len(list(Path(temp).glob("COBERTURA_MAXIMA_*.json"))),3)
            with self.assertRaises(ValueError):
                coverage.write(temp,result,"MAPA_INEXISTENTE")

    def test_three_map_city_coverage_uses_only_editor_units(self):
        companies,territory,active=self.fake()
        territory["instancias_cidade"]=[
            {"empresa":"citrosuco1","cidade":"divinopolis",
             "in_esperados":["carga8"],"out_esperados":[]},
            {"empresa":"frucamp","cidade":"divinopolis",
             "in_esperados":["carga8"],"out_esperados":[]},
            {"empresa":"agro_duvidoso","cidade":"divinopolis",
             "in_esperados":[],"out_esperados":[]},
            {"empresa":"rodoviaria11","cidade":"itauna",
             "in_esperados":[],"out_esperados":[]},
        ]
        data=coverage.assess(companies,territory,active,
                             {i:("laranja","Sacos de Laranja") for i in range(24)},
                             {"cargas_com_par_economico_comprovavel":24,
                              "cargas_candidatas_teste_ets2":24})
        self.assertEqual(data["cidades_identificadas"],2)
        self.assertEqual(data["cidades_com_empresas_sem_classificacao"],1)
        by_city={row["cidade"]:row for row in data["cidades"]}
        self.assertEqual(by_city["divinopolis"]["empresas_compativeis"],2)
        self.assertEqual(by_city["divinopolis"]["empresas_compativeis_cobertas"],2)
        self.assertEqual(by_city["itauna"]["situacao"],
                         "SEM_EMPRESA_COMPATIVEL_CONFIRMADA")
        self.assertFalse(data["cobertura_100_por_cento_comprovada"])
        with tempfile.TemporaryDirectory() as temp:
            for name in ("RBR","ELDORADO","MINAS_GERAIS"):
                coverage.write(temp,data,name)
                path=Path(temp)/("COBERTURA_CIDADES_"+name+".csv")
                self.assertTrue(path.exists())
                with path.open(encoding="utf-8-sig",newline="") as f:
                    import csv
                    rows=list(csv.DictReader(f,delimiter=";"))
                self.assertEqual(len(rows),2)
                self.assertTrue((Path(temp)/("COBERTURA_CIDADES_"+name+".json")).exists())

    def test_no_editor_never_implies_city_homologation(self):
        companies,territory,active=self.fake()
        for key in companies:
            territory["instancias_cidade"].append({
                "empresa":key,"cidade":"divinopolis"})
        data=coverage.assess(companies,territory,active,
                            {i:("laranja","Sacos de Laranja") for i in range(24)},
                            {"cargas_com_par_economico_comprovavel":24,
                             "cargas_candidatas_teste_ets2":0})
        self.assertEqual(data["cargas_candidatas_teste"],0)
        self.assertFalse(data["cobertura_100_por_cento_comprovada"])

    def test_missing_known_company_is_reported_separately_from_24_cargos(self):
        companies,territory,active=self.fake()
        active["frucamp"]["in"].clear()
        report=coverage.assess(companies,territory,active,
                         {i:("laranja","Sacos de Laranja") for i in range(24)},
                         {"cargas_com_par_economico_comprovavel":24,
                          "cargas_candidatas_teste_ets2":24})
        self.assertEqual(report["empresas_reconhecidas_com_lacunas"],1)
        missing=next(x for x in report["empresas"] if x["empresa"]=="frucamp")
        self.assertEqual(missing["in_faltantes"],["carga8"])


if __name__=="__main__":
    unittest.main()
