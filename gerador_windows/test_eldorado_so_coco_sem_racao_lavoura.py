"""Regressoes de regras definitivas autorizadas para o Eldorado.

IN de racao em pecuarias = coerente; OUT de racao em lavoura de
milho/soja = proibido, inclusive permissao herdada na Company antiga.
A unica adaptacao regional no Eldorado e coco, sem mudar Minas/RBR.
"""
import unittest
import gerador as g
import politica_economica as policy
import eldorado_ingles
from auditor_existentes import proven_incompatibility, can_add


def specialized(name, incoming=(), outgoing=()):
    c=g.Company(name,old_in=set(incoming),old_out=set(outgoing))
    c._eldorado_map=True
    scoped=eldorado_ingles.infer_identity(c,policy)
    if scoped is not None:
        c._eldorado_identity=scoped
    ident=policy.classify(c)
    c.role=ident.role
    c.explicit_role=ident.certainty=="alta"
    return c


class OnlyCoconutAndNoFarmFeedOutput(unittest.TestCase):
    def test_soy_and_maize_plantation_cannot_ship_feed_even_if_old_def_says_feed(self):
        farm=specialized(
            "rocasoja",
            incoming={"fertilizer","big_bag_seed","tractors"},
            outgoing={"milho","soja","animal_feed"})
        self.assertEqual(farm.role,"eldorado_lavoura")
        for i in (17,18,19,20):
            with self.subTest(cargo="carga"+str(i)):
                self.assertFalse(policy.decide(farm,"racao","out").allowed)
        self.assertTrue(policy.decide(farm,"milho","out").allowed)
        self.assertTrue(policy.decide(farm,"soja","out").allowed)
        self.assertTrue(policy.decide(farm,"adubo","in").allowed)
        self.assertFalse(can_add(g,farm,"racao","out","Eldorado",
                                 professional=True))
        self.assertIsNotNone(proven_incompatibility(
            farm,"racao","out",map_name="Eldorado"))

    def test_named_soy_farm_still_does_not_export_feed(self):
        farm=specialized("rocasoja",outgoing={"soja","racao"})
        self.assertEqual(farm.role,"fazenda_soja")
        self.assertFalse(policy.decide(farm,"racao","out").allowed)
        self.assertIsNotNone(proven_incompatibility(
            farm,"racao","out",map_name="Eldorado"))

    def test_feed_factory_and_animal_farm_keep_correct_directions(self):
        factory=specialized("fabrica_racao",incoming={"milho","soja"},
                            outgoing={"racao"})
        self.assertEqual(factory.role,"fabrica_racao")
        self.assertTrue(policy.decide(factory,"racao","out").allowed)
        self.assertTrue(policy.decide(factory,"milho","in").allowed)
        livestock=specialized("fazenda",incoming={"bois"},outgoing={"bois"})
        self.assertEqual(livestock.role,"eldorado_pecuaria")
        self.assertTrue(policy.decide(livestock,"racao","in").allowed)
        self.assertFalse(policy.decide(livestock,"racao","out").allowed)

    def test_coconut_only_regional_override(self):
        crop=specialized("rocasoja",
            incoming={"fertilizer","big_bag_seed"},
            outgoing={"milho","soja"})
        coco=policy.regional_approved_decision(
            crop,"coco","out","Eldorado")
        self.assertTrue(coco.allowed)
        self.assertIsNone(policy.regional_approved_decision(
            crop,"algodao","out","Eldorado"))
        self.assertFalse(policy.decide(crop,"algodao","out").allowed)
        self.assertIsNotNone(proven_incompatibility(
            crop,"algodao","out",map_name="Eldorado"))
        self.assertTrue(can_add(g,crop,"coco","out","Eldorado",
                                professional=True))
        market=specialized("supermercado_centro")
        self.assertTrue(policy.regional_approved_decision(
            market,"coco","in","Eldorado").allowed)
        self.assertIsNone(policy.regional_approved_decision(
            market,"algodao","in","Eldorado"))

    def test_minas_and_rbr_untouched(self):
        c=g.Company("fazenda_soja",old_in={"adubo"},old_out={"soja"})
        self.assertTrue(policy.regional_approved_decision(
            c,"algodao","out","Minas_Gerais").allowed)
        self.assertIsNone(policy.regional_approved_decision(
            c,"coco","out","RBR"))
        self.assertFalse(hasattr(c,"_eldorado_map"))


if __name__=="__main__":
    unittest.main()
