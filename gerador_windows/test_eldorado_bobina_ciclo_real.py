import unittest
from test_gerador import g
import politica_economica as policy


class RealEldoradoSteelFlow(unittest.TestCase):
    def test_csn_steel_coils_to_itaacos_processing(self):
        csn = g.Company("csn")
        ita = g.Company(
            "itaacos",
            old_in={"iron_pipes", "largetubes", "sandwch_pnls"},
            old_out={"sandwch_pnls", "scrap_metals", "iron_pipes",
                     "roof_tiles", "largetubes"},
        )
        self.assertEqual(policy.classify(ita).role, "revenda_aco")
        self.assertTrue(policy.decide(csn, "bobina", "out").allowed)
        decision = policy.decide(ita, "bobina", "in")
        self.assertTrue(decision.allowed)
        self.assertIn("inferida", decision.evidence)
        self.assertFalse(policy.decide(ita, "bobina", "out").allowed)

    def test_generic_steel_reseller_is_not_automatically_buyer(self):
        shop = g.Company(
            "itaacos",
            old_in={"iron_pipes", "largetubes"},
            old_out={"iron_pipes", "largetubes"},
        )
        self.assertFalse(policy.decide(shop, "bobina", "in").allowed)

    def test_missing_metal_processing_evidence_blocks_coils(self):
        shop = g.Company(
            "itaacos",
            old_in={"iron_pipes", "largetubes"},
            old_out={"sandwch_pnls"},
        )
        self.assertFalse(policy.decide(shop, "bobina", "in").allowed)

    def test_prefabricated_concrete_does_not_become_steel_buyer(self):
        concrete = g.Company(
            "itcc2",
            old_in={"cement", "largetubes", "ore"},
            old_out={"concr_beams", "floorpanels", "precast_strs",
                     "wallpanels", "cement"},
        )
        self.assertEqual(policy.classify(concrete).role, "premoldados")
        self.assertFalse(policy.decide(concrete, "bobina", "in").allowed)
        self.assertTrue(policy.decide(concrete, "cimento", "in").allowed)


if __name__ == "__main__":
    unittest.main()
