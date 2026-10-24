"""Refinamento final Eldorado: casos derivados do IN/OUT da DEF real.

Essas classes nao criam frete para um setor sem evidencia. Os exemplos
abaixo conferem a direcao e deixam os tres outros mapas sem interferencia.
"""
import unittest
import gerador as g
import politica_economica as policy
import eldorado_ingles as eld
from auditor_existentes import proven_incompatibility,can_add


def real_company(company_id, incoming, outgoing):
    company=g.Company(company_id,old_in=set(incoming),old_out=set(outgoing))
    identity=eld.infer_identity(company,policy)
    if identity is not None:
        company._eldorado_identity=identity
    standard=policy.classify(company)
    company.role=standard.role
    company.explicit_role=(standard.certainty=="alta")
    return company


class EldoradoFinalDefIndustry(unittest.TestCase):
    def test_ipiranga_fuel_depot_is_not_freight_industry(self):
        tokens={"alcool","diesel","diesel2","emptytank","fueltanker",
                "gasolina","oil","petrol","querosene"}
        c=real_company("ipiranga",tokens,tokens | {"tanquevazio"})
        self.assertEqual(c.role,"eldorado_combustiveis")
        self.assertFalse(policy.decide(c,"cerveja","out").allowed)
        self.assertFalse(policy.decide(c,"adubo","in").allowed)
        self.assertIsNotNone(proven_incompatibility(
            c,"soja","out",map_name="Eldorado"))

    def test_graal_passenger_terminals_not_cargo_factories(self):
        passenger={"passageiros","passageiros2","passageiros3",
                   "passageiros4","passageiros5","passageiros6",
                   "passageiros7","passageiros8","passageiros9"}
        c=real_company("graal",passenger,passenger)
        self.assertEqual(c.role,"eldorado_transporte_passageiros")
        self.assertFalse(policy.decide(c,"racao","in").allowed)
        self.assertFalse(policy.decide(c,"palete","out").allowed)

    def test_med_dairy_processes_milk_not_crops(self):
        c=real_company("med",
            {"apples","milk","grapes","leite","emptytank"},
            {"cheese","yogurt"})
        self.assertEqual(c.role,"eldorado_laticinios")
        self.assertFalse(policy.decide(c,"soja","out").allowed)
        self.assertFalse(policy.decide(c,"racao","in").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)

    def test_aria_dairy_meat_processing_not_cattle_farm(self):
        c=real_company("aria_bd2",
            {"big_bag_seed","diesel","tractors","plant_substr"},
            {"beef3","beef_meat","cheese","drymilk","goat_cheese",
             "milk","tractors"})
        self.assertEqual(c.role,"eldorado_produtos_animais")
        self.assertFalse(policy.decide(c,"soja","out").allowed)
        self.assertFalse(policy.decide(c,"racao","in").allowed)

    def test_polar_fish_inbound_potatoes_for_processing(self):
        c=real_company("polar_fish2",
            {"container","containersud","flour","peas","potatoes",
             "tomatoes","vinegar","vinegar_c"},
            {"container","containersud"})
        self.assertEqual(c.role,"eldorado_processador_alimentos")
        self.assertTrue(policy.decide(c,"batata","in").allowed)
        self.assertFalse(policy.decide(c,"batata","out").allowed)
        self.assertIsNone(proven_incompatibility(
            c,"batata","in",map_name="Eldorado"))

    def test_facchini_auto_parts_recycles_empty_pallets(self):
        c=real_company("facchini",
            {"brake_pads","truck_rims","truck_rims_c",
             "truck_tyres","tyres"},
            {"empty_barr","empty_palet"})
        self.assertEqual(c.role,"eldorado_autopecas")
        self.assertTrue(policy.decide(c,"palete","out").allowed)
        self.assertFalse(policy.decide(c,"palete","in").allowed)
        self.assertFalse(policy.decide(c,"madeira","out").allowed)

    def test_lov_potato_field_outbound_and_fertilizer_in(self):
        c=real_company("lov",
            {"diesel","digger1000","digger500","diggers",
             "empty_palet","forklifts"},
            {"potatoes"})
        self.assertEqual(c.role,"eldorado_lavoura")
        self.assertTrue(policy.decide(c,"batata","out").allowed)
        self.assertTrue(policy.decide(c,"adubo","in").allowed)
        self.assertFalse(policy.decide(c,"soja","out").allowed)
        self.assertFalse(policy.decide(c,"racao","in").allowed)

    def test_no_farm_with_only_stock_receipt_or_no_harvest(self):
        c=real_company("testfarmshop",
            {"digger500","diggers","potatoes"},
            {"empty_palet"})
        self.assertNotEqual(c.role,"eldorado_lavoura")
        c2=real_company("testwarehouse",
            {"digger500","potatoes"},
            {"potatoes"})
        self.assertNotEqual(c2.role,"eldorado_lavoura")

    def test_evidence_matrix_separates_source_and_simulation(self):
        import csv
        import tempfile
        from pathlib import Path
        farm=real_company("fazenda",{"bois","leite"},{"bois"})
        food=real_company("polar_fish2",
                          {"peas","potatoes","tomatoes"},
                          {"container","containersud"})
        with tempfile.TemporaryDirectory() as temp:
            eld.export_translation_reports(
                {"fazenda":farm,"polar_fish2":food},temp)
            p=Path(temp)/"MATRIZ_ECONOMICA_ELDORADO.csv"
            self.assertTrue(p.is_file())
            with p.open(encoding="utf-8-sig",newline="") as stream:
                records=list(csv.DictReader(stream,delimiter=";"))
            for key in ("empresa","categoria_librelato","direcao",
                        "tipo_de_evidencia","base_da_decisao"):
                self.assertIn(key,records[0])
            self.assertTrue(any(
                row["empresa"]=="fazenda" and
                row["categoria_librelato"]=="racao" and
                row["direcao"]=="in" and
                row["tipo_de_evidencia"]=="SIMULACAO_ECONOMICA"
                for row in records))
            self.assertTrue(any(
                row["empresa"]=="polar_fish2" and
                row["categoria_librelato"]=="batata" and
                row["direcao"]=="in" and
                row["tipo_de_evidencia"]=="DEF_ORIGINAL"
                for row in records))
            self.assertFalse(any(
                row["empresa"]=="fazenda" and
                row["categoria_librelato"]=="soja" and
                row["direcao"]=="out" for row in records))

    def test_other_maps_do_not_get_eldorado_rules(self):
        original=g.Company("lov",old_in={"digger500","diggers"},
                           old_out={"potatoes"})
        self.assertNotEqual(policy.classify(original).role,
                            "eldorado_lavoura")
        self.assertFalse(policy.decide(original,"adubo","in").allowed)
        self.assertIsNone(policy.regional_approved_decision(
            original,"coco","out","RBR"))

    def test_explicit_def_product_preserved_no_arbitrary_freight(self):
        c=real_company("polar_fish2",
            {"potatoes","peas","tomatoes"},
            {"container","containersud"})
        self.assertTrue(can_add(
            g,c,"batata","in","Eldorado",professional=True))
        self.assertIsNone(can_add(
            g,c,"milho","out","Eldorado",professional=True))


if __name__=="__main__":
    unittest.main()
