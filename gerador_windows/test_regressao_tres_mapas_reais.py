"""Tests over MG and Eldorado economic flows from uploaded 2026-10-23 audits.

All input freight tokens below are from original DEF IN/OUT evidence, not
from potentially corrupted historical Company SCS. No external firm registry
or fictitious city/prefab is needed for these decisions.
"""
import unittest

from test_gerador import g
import politica_economica as policy
from auditor_existentes import proven_incompatibility


def examined(company, in_tokens=(), out_tokens=(), name=""):
    c=g.Company(company,display_name=name,old_in=set(in_tokens),
                old_out=set(out_tokens))
    c.role=policy.classify(c).role
    c.explicit_role=policy.classify(c).certainty=="alta"
    return c


class MGAndEldoradoEconomicFlows(unittest.TestCase):
    def test_minas_receiving_three_crops_does_not_become_producer(self):
        c=examined("copacafeanim",
                   ["batata","feijao","milho","soja"])
        self.assertEqual(c.role,"recebedor_agricola_inferido")
        for cat in ("milho","soja","batata"):
            self.assertTrue(policy.decide(c,cat,"in").allowed)
            self.assertFalse(policy.decide(c,cat,"out").allowed)
            self.assertIsNotNone(proven_incompatibility(
                c,cat,"out",map_name="Minas_Gerais"))
        self.assertFalse(policy.decide(c,"adubo","out").allowed)

    def test_minas_recycling_only_outbound_is_not_unknown_factory(self):
        for company,goods in (
            ("copobras2",["papelao","plasticom","supaletes"]),
            ("acero2",["papelao","plasticom","supaletes"]),
            ("belgo2",["papelao","plasticom","supaletes","sumetal"])
        ):
            with self.subTest(company=company):
                c=examined(company,out_tokens=goods)
                self.assertEqual(c.role,"expedidor_residuos_inferido")
                self.assertTrue(policy.decide(c,"palete","out").allowed)
                self.assertFalse(policy.decide(c,"palete","in").allowed)
                self.assertIsNotNone(proven_incompatibility(
                    c,"cimento","in",map_name="Minas_Gerais"))

    def test_minas_packaging_waste_without_palete_does_not_invent_one(self):
        c=examined("quim_07",out_tokens=["papelao","plasticom"])
        self.assertEqual(c.role,"expedidor_residuos_inferido")
        self.assertFalse(policy.decide(c,"palete","out").allowed)

    def test_minas_agrotec_outbound_agro_inputs_is_not_crop_farm(self):
        c=examined("agrotec",out_tokens=[
            "adubo","aramefar","equipagrico","fertilizante",
            "papelao","plasticom","racao","supaletes"])
        self.assertEqual(c.role,"agroinsumos")
        self.assertTrue(policy.decide(c,"adubo","out").allowed)
        self.assertTrue(policy.decide(c,"racao","out").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)
        self.assertFalse(policy.decide(c,"soja","out").allowed)

    def test_minas_copobras_disposables_not_cement_or_bricks(self):
        c=examined("copobras",out_tokens=[
            "coposdesc","pratosdesc","talheresdesc"])
        self.assertEqual(c.role,"fabricante_descartaveis_inferido")
        self.assertFalse(policy.decide(c,"cimento","out").allowed)
        self.assertFalse(policy.decide(c,"tijolo","out").allowed)

    def test_eldorado_warehouse_wood_bidirectional(self):
        c=examined("eld",in_tokens=[
            "empty_palet","eucalipto","logs","lumber","sawpanels"],
            out_tokens=[
            "empty_palet","eucalipto","logs","lumber","sawpanels"])
        self.assertEqual(c.role,"entreposto_madeira_inferido")
        for cat in ("madeira","palete"):
            self.assertTrue(policy.decide(c,cat,"in").allowed)
            self.assertTrue(policy.decide(c,cat,"out").allowed)
        self.assertFalse(policy.decide(c,"cimento","in").allowed)
        self.assertIsNotNone(proven_incompatibility(
            c,"racao","out",map_name="Eldorado"))

    def test_eldorado_bidirectional_wood_without_in_is_not_warehouse(self):
        c=examined("eld",out_tokens=["logs","lumber"])
        self.assertNotEqual(c.role,"entreposto_madeira_inferido")

    def test_eldorado_cmddiesel_diversified_logistics_not_fertilizer_only(self):
        goods=[
            "beverages","bguerra","big_bag_seed","canned_beans",
            "carrots","cauliflower","clothes","clothes3",
            "drymilk","fertilizer","granel","sugar",
            "sugar2","tableware","toys","tyres"]
        c=examined("cmddiesel",in_tokens=goods,out_tokens=goods)
        self.assertEqual(c.role,"centro_logistico_inferido")
        self.assertTrue(policy.decide(c,"adubo","in").allowed)
        self.assertTrue(policy.decide(c,"adubo","out").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)

    def test_eldorado_chemical_depot_overrides_false_supermarket_and_works(self):
        chemicals=[
            "arsenic","chlorine","cyanide","mercuric",
            "sulfuric","nitrocel","acid","potahydro"]
        for name in ("sellplan2","sanbuilders2","midwest"):
            with self.subTest(name=name):
                c=examined(name,in_tokens=chemicals,out_tokens=chemicals)
                self.assertEqual(c.role,"terminal_quimico_inferido")
                self.assertFalse(policy.decide(c,"cerveja","in").allowed)
                self.assertFalse(policy.decide(c,"cimento","in").allowed)

    def test_no_garbage_graos_alias_or_sorghum_without_documentation(self):
        c=examined("agh",in_tokens=[
            "big_bag_seed","digger500","feijao","milho",
            "rice","rice_c","soja","tractors"],
            out_tokens=["big_bag_seed","digger500","fertilizer","graos"])
        self.assertTrue(policy.decide(c,"milho","in").allowed)
        self.assertTrue(policy.decide(c,"soja","in").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)
        self.assertFalse(policy.decide(c,"sorgo","out").allowed)

    def test_region_coconut_and_cotton_only_mg_eldorado(self):
        farm=examined("fazenda_teste",in_tokens=["adubo"])
        for map_name in ("Minas_Gerais","Eldorado"):
            for category in ("algodao","coco"):
                with self.subTest(map_name=map_name,category=category):
                    self.assertTrue(policy.regional_approved_decision(
                        farm,category,"out",map_name).allowed)
        for category in ("algodao","coco"):
            self.assertIsNone(policy.regional_approved_decision(
                farm,category,"out","RBR"))

    def test_coconut_market_not_cotton_receiver(self):
        market=examined("ceagesp",name="CEAGESP Hortifruti")
        self.assertTrue(policy.regional_approved_decision(
            market,"coco","in","Eldorado").allowed)
        self.assertIsNone(policy.regional_approved_decision(
            market,"algodao","in","Eldorado"))
        self.assertIsNone(policy.regional_approved_decision(
            market,"coco","in","RBR"))


if __name__=="__main__":
    unittest.main()
