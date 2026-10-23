"""Regressoes RBR 2026-10-23 baseadas em AUDITORIA_RBR(6).json.

Os testes usam IN/OUT ORIGINAIS do relatorio, nao confianca na Company
herdada. Preserva cadeia valida e remove apenas contradicoes fortes.
"""
import unittest

from test_gerador import g
import politica_economica as policy
from auditor_existentes import proven_incompatibility


class RBRRealEconomicRefinement(unittest.TestCase):
    def test_coca_cola_soda_is_not_beer(self):
        company=g.Company(
            "coca_itabi", display_name="Coca-Cola Itabirito",
            old_in={"banana","laranja","lata"},
            old_out={"bebidas","bebidas_b","refrigerant","paletev"}
        )
        self.assertEqual(policy.classify(company).role,"fabricante_refrigerantes")
        self.assertFalse(policy.decide(company,"cerveja","out").allowed)
        self.assertTrue(policy.decide(company,"palete","out").allowed)
        company.role=policy.classify(company).role
        self.assertIsNotNone(proven_incompatibility(
            company,"cerveja","out",map_name="RBR"))
        self.assertIsNone(proven_incompatibility(
            company,"palete","out",map_name="RBR"))

    def test_pepsico_generic_beverage_cannot_ship_cerveja(self):
        company=g.Company(
            "pepsico",display_name="Pepsico",
            old_in={"celulose","lata","matprima","paletev"},
            old_out={"bebidas","bebidas_b","cavaco_alu","plast_usado"}
        )
        self.assertEqual(policy.classify(company).role,"fabricante_refrigerantes")
        company.role=policy.classify(company).role
        self.assertIsNotNone(proven_incompatibility(
            company,"cerveja","out",map_name="RBR"))
        self.assertFalse(policy.decide(company,"cerveja","out").allowed)
        self.assertTrue(policy.decide(company,"palete","in").allowed)

    def test_explicit_beer_is_preserved_not_overruled_by_brand(self):
        company=g.Company(
            "pepsico",old_out={"bebidas","beer"},old_in={"paletev"}
        )
        company.role=policy.classify(company).role
        self.assertEqual(company.role,"fabricante_refrigerantes")
        self.assertTrue(policy.decide(company,"cerveja","out").allowed)
        self.assertIsNone(proven_incompatibility(
            company,"cerveja","out",map_name="RBR"))

    def test_generic_beverage_without_brand_is_not_automatically_beer(self):
        company=g.Company("fornecedor_q7",old_out={"bebidas"})
        self.assertNotEqual(policy.classify(company).role,"fabricante_refrigerantes")
        self.assertFalse(policy.decide(company,"cerveja","out").allowed)

    def test_soda_brand_without_soda_evidence_is_not_classified(self):
        company=g.Company("pepsico",old_out={"plast_usado"})
        self.assertNotEqual(policy.classify(company).role,"fabricante_refrigerantes")

    def test_machinery_company_does_not_sell_grains_or_fertilizer(self):
        company=g.Company(
            "mt_agrogarca",display_name="AgroGarcas",
            old_in={"case9230","case9230_3e","newlholl","newlholl_3e","filtro_oleo"},
            old_out={"case9230","case9230_3e","newlholl","newlholl_3e","filtro_usad"}
        )
        self.assertEqual(policy.classify(company).role,
                         "revenda_maquinas_agricolas_inferida")
        company.role=policy.classify(company).role
        for cat,side in [
            ("milho","in"),("soja","in"),("adubo","in"),
            ("adubo","out"),("sorgo","out"),("racao","out")
        ]:
            with self.subTest(category=cat,direction=side):
                self.assertFalse(policy.decide(company,cat,side).allowed)
                self.assertIsNotNone(proven_incompatibility(
                    company,cat,side,map_name="RBR"))

    def test_machine_sale_with_crops_is_not_overclassified(self):
        company=g.Company(
            "q7",old_in={"case9230","newlholl"},
            old_out={"case9230","newlholl","milho"}
        )
        self.assertNotEqual(policy.classify(company).role,
                            "revenda_maquinas_agricolas_inferida")

    def test_single_machine_model_is_not_enough(self):
        company=g.Company("q8",old_in={"case9230","case9230_3e"},
                          old_out={"case9230","case9230_3e"})
        self.assertNotEqual(policy.classify(company).role,
                            "revenda_maquinas_agricolas_inferida")

    def test_boisserie_is_woodworking_not_feed_buyer(self):
        company=g.Company("boisserie",old_in={"paletev"})
        self.assertEqual(policy.classify(company).role,"fabrica_moveis")
        company.role=policy.classify(company).role
        self.assertTrue(policy.decide(company,"palete","in").allowed)
        for cat in ("racao","sorgo"):
            with self.subTest(category=cat):
                self.assertFalse(policy.decide(company,cat,"in").allowed)
                self.assertIsNotNone(proven_incompatibility(
                    company,cat,"in",map_name="RBR"))

    def test_no_regression_ambev_supermarket_and_regional_scope(self):
        brewery=g.Company("ambev",old_out={"beer"})
        market=g.Company("supermercado_centro",old_in={"beer"})
        self.assertTrue(policy.decide(brewery,"cerveja","out").allowed)
        self.assertTrue(policy.decide(market,"cerveja","in").allowed)
        farm=g.Company("fazenda_teste",old_in={"adubo"})
        self.assertIsNone(policy.regional_approved_decision(
            farm,"coco","out","RBR"))
        self.assertTrue(policy.regional_approved_decision(
            farm,"coco","out","Minas_Gerais").allowed)


if __name__=="__main__":
    unittest.main()
