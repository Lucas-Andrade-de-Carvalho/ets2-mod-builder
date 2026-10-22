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
    def test_agromec_votuporanga_is_fertilizer_only(self):
        c=g.Company("agromecvo",display_name="Agromec")
        self.assertEqual(p.classify(c).role,"revenda_fertilizante")
        self.assertTrue(p.decide(c,"adubo","in").allowed)
        self.assertTrue(p.decide(c,"adubo","out").allowed)
        self.assertFalse(p.decide(c,"racao","out").allowed)
        self.assertFalse(p.decide(c,"sorgo","in").allowed)
        self.assertFalse(p.decide(c,"bobina","out").allowed)

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
                "in_esperados":(["carga8"] if c.role=="processadora_citricos" else []),
                "out_esperados":[],
            } for id,c in objs.items()]
        from collections import defaultdict
        active=defaultdict(lambda:{"in":set(),"out":set()})
        active["citrosuco1"]["in"].add("carga8")
        active["frucamp"]["in"].add("carga8")
        return objs,{"empresas":labels,"instancias_cidade":[]},active

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
