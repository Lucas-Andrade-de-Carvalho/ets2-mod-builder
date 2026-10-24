"""Provas de realismo: os casos replicam IN/OUT da DEF Eldorado entregue.
Nao usar company IDs ficticios para fabricar culturas nao documentadas.
"""
import unittest
from test_gerador import g
import politica_economica as policy
import eldorado_ingles as english
from auditor_existentes import can_add, proven_incompatibility


def company(name, incoming=(), outgoing=()):
    c=g.Company(name,old_in=set(incoming),old_out=set(outgoing))
    scoped=english.infer_identity(c,policy)
    if scoped is not None:
        c._eldorado_identity=scoped
    inferred=policy.classify(c)
    c.role=inferred.role
    c.explicit_role=inferred.certainty=="alta"
    return c


class EldoradoEnglishEconomicSimulation(unittest.TestCase):
    def test_semantics_translate_without_false_commodity_equivalence(self):
        self.assertEqual(english.translate("fertilizer"),"fertilizante (adubo)")
        self.assertEqual(english.translate("big_bag_seed"),"sementes em big bags")
        self.assertIn("NAO_TRADUZIDO",english.translate("unknown_dlc_777"))
        self.assertNotIn("cerveja",policy.cargo_categories({"beverages","nonalco_beer"}))
        self.assertNotIn("soja",policy.cargo_categories({"beans","rice","graos"}))
        self.assertEqual(english.translate("tractors"),"tratores")

    def test_fazenda_is_cattle_ranch_not_cotton_or_coconut_farm(self):
        c=company("fazenda",
            incoming=("bois","leite","digger500","tractors"),
            outgoing=("bois",))
        self.assertEqual(c.role,"eldorado_pecuaria")
        self.assertTrue(policy.decide(c,"racao","in").allowed)
        self.assertTrue(policy.decide(c,"sorgo","in").allowed)
        self.assertFalse(policy.decide(c,"adubo","in").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)
        self.assertFalse(policy.decide(c,"soja","out").allowed)
        self.assertIsNone(policy.regional_approved_decision(
            c,"coco","out","Eldorado"))
        self.assertIsNotNone(proven_incompatibility(
            c,"algodao","out",map_name="Eldorado"))
        self.assertIsNone(proven_incompatibility(
            c,"racao","in",map_name="Eldorado"))

    def test_milk_farm_needs_feed_and_not_fertilizer(self):
        c=company("fazenda2",
            incoming=("bois","leite","digger500","bagacof"),
            outgoing=("leite","lumber","wshavings"))
        self.assertEqual(c.role,"eldorado_pecuaria")
        self.assertTrue(can_add(g,c,"racao","in","Eldorado",professional=True))
        self.assertFalse(can_add(g,c,"adubo","in","Eldorado",professional=True))
        self.assertFalse(can_add(g,c,"soja","out","Eldorado",professional=True))

    def test_ale_as_cattle_operation(self):
        c=company("ale",incoming=("bois","leite","tractors"),
                  outgoing=("bois","leite"))
        self.assertEqual(c.role,"eldorado_pecuaria")

    def test_soy_and_maize_leave_documented_plantation(self):
        c=company("rocasoja",
            incoming=("big_bag_seed","fertilizer","tractors"),
            outgoing=("feijao","milho","soja"))
        self.assertEqual(c.role,"eldorado_lavoura")
        self.assertTrue(policy.decide(c,"soja","out").allowed)
        self.assertTrue(policy.decide(c,"milho","out").allowed)
        self.assertTrue(policy.decide(c,"adubo","in").allowed)
        self.assertFalse(policy.decide(c,"batata","out").allowed)
        self.assertFalse(policy.decide(c,"racao","in").allowed)
        self.assertTrue(policy.regional_approved_decision(
            c,"algodao","out","Eldorado").allowed)
        self.assertIsNone(policy.regional_approved_decision(
            c,"algodao","out","RBR"))

    def test_potatoes_documented_from_real_crop_farm(self):
        c=company("agronord2",
            incoming=("fertilizer","young_seed","digger500"),
            outgoing=("apples","beans","potatoes","tomatoes"))
        self.assertEqual(c.role,"eldorado_lavoura")
        self.assertTrue(policy.decide(c,"batata","out").allowed)
        self.assertFalse(policy.decide(c,"soja","out").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)

    def test_sugarcane_is_not_soybean_farm(self):
        c=company("roca_bon",incoming=("canavazio",),outgoing=("cana",))
        self.assertEqual(c.role,"eldorado_canavial")
        self.assertTrue(policy.decide(c,"adubo","in").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)
        self.assertIsNone(policy.regional_approved_decision(
            c,"coco","out","Eldorado"))

    def test_agh_receives_grain_but_sends_only_documented_fertilizer(self):
        c=company("agh",
            incoming=("big_bag_seed","digger500","feijao",
                      "milho","rice","rice_c","soja","tractors"),
            outgoing=("big_bag_seed","digger500","fertilizer","graos"))
        self.assertEqual(c.role,"eldorado_comercio_rural")
        self.assertTrue(policy.decide(c,"milho","in").allowed)
        self.assertTrue(policy.decide(c,"soja","in").allowed)
        self.assertTrue(policy.decide(c,"adubo","out").allowed)
        self.assertFalse(policy.decide(c,"soja","out").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)

    def test_warehouse_not_producer(self):
        c=company("arc",
            incoming=("digger500","feijao","fertilizer","graos",
                      "milho","soja","tractors"),
            outgoing=("big_bag_seed","digger500","feijao","graos",
                      "milho","soja"))
        self.assertEqual(c.role,"eldorado_armazem_graos")
        self.assertTrue(policy.decide(c,"soja","in").allowed)
        self.assertTrue(policy.decide(c,"soja","out").allowed)
        self.assertFalse(policy.decide(c,"sorgo","out").allowed)

    def test_bulk_hub_not_real_farm(self):
        c=company("ancapi",outgoing=("potatoes","oranges","cement",
               "beverages","rice","lumber","fertilizer","empty_palet")
               +tuple("product"+str(n) for n in range(67)))
        self.assertEqual(c.role,"eldorado_hub_saida")
        self.assertTrue(policy.decide(c,"batata","out").allowed)
        self.assertFalse(policy.decide(c,"batata","in").allowed)
        self.assertFalse(policy.decide(c,"cerveja","out").allowed)

    def test_same_company_outside_eldorado_keeps_old_policy(self):
        c=g.Company("fazenda",old_in={"bois"},old_out={"bois"})
        self.assertEqual(policy.classify(c).role,"fazenda")
        self.assertTrue(policy.decide(c,"adubo","in").allowed)


if __name__=="__main__":
    unittest.main()
