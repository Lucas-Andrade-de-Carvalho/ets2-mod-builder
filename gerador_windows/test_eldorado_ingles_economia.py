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
    def test_all_225_original_eldorado_cargo_identifiers_translate(self):
        raw = (
            "acetylene acid alcool almond ammonia ammunition apples apples_c areia arsenic asph_miller bagacof banana beans bebidas beef3 beef_meat betoneira beverages beverages_c bguerra big_bag_seed bois boric_acid bottle_water brake_pads bricks cable_reel cacamvazio calcario cana canavazio canned_beans carb_water carbn_pwdr_c carrots carrots_c cauliflower cement cheese chem_sorb_c chem_sorbent chemicals chewing_gums chimney_syst chlorine chlorine_t chocolate clinquer clothes clothes3 clothes_c coal concr_beams concrete cont_trees container containersud contamin contrato_tnl_bau contrato_tnl_bau2 copp_rf_gutt cyanide diesel diesel2 digger1000 digger500 diggers dozer dryers drymilk dynamite electronics empty_barr empty_palet emptytank encomendas eucalipto excavator excavator2 explosives feijao fertilizer fireworks floorpanels flour fluorine forklifts fosforo fuel_oil fueltanker furniture gas gasolina glass glass_packed goat_cheese granel graos grapes graph_grease grass_rolls gravel hchemicals hipresstank hmetal honey hwaste hydrochlor hydrogen ibc_cont icecream iron_pipes kerosene ketchup largetubes lead leite limonades lixo lixo1 lixo2 lixo3 lixo4 lixo5 locomotive logs lpg lumber magnesium maple_syrup mason_jars med_equip mercuric metal_center milho milk mobile_crane mondeos motor_oil motor_oil_c neon nitrocel nitrogen nonalco_beer nuts oil oil_filt_c oil_filters oranges ore outdr_flr_tl overweight packag_food paper passageiros passageiros2 passageiros3 passageiros4 passageiros5 passageiros6 passageiros7 passageiros8 passageiros9 peas pesticide petrol phosphor plant_substr plastic_gra plums pnut_butter potahydro potassium potatoes precast_strs princess querosene radiators rice rice_c roof_tiles roofing_felt rooflights sand sandwch_pnls sawpanels scrap_metals sedex sodchlor sodhydro sodium soja sq_tub stones straw_bales sucata sugar sugar2 sulfuric sulfuric_t tableware tanquevazio tomatoes toys tractors tractors2 transformat truck_rims truck_rims_c truck_tyres tyres used_battery used_packag used_plast used_plast_c vent_tube vinegar vinegar_c wallpanels watermelons wrk_cloth wshavings yogurt young_seed"
        )
        items = raw.split()
        self.assertEqual(len(items),225)
        missing = [name for name in items
                   if english.translate(name).startswith("NAO_TRADUZIDO")]
        self.assertEqual(missing,[])
        self.assertEqual(english.translate(
            "concr_beams.dlc_heavy_cargo"),
            "vigas de concreto")

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
