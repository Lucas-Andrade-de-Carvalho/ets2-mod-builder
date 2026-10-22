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
