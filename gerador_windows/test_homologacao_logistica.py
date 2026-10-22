"""Nao confundir presença de IN/OUT com rota comprovada."""
import unittest
from test_gerador import g
import politica_economica as policy
import catalogo_fontes as catalog
import homologacao_logistica as homol


def company(name, in_cargos=(), out_cargos=(), editor=False):
    c=g.Company(name)
    c.old_in=set(in_cargos)
    c.old_out=set(out_cargos)
    if editor:
        c.editor_files={"def/company/"+name+"/editor/test.sii":b"SiiNunit {}"}
    return c


def state(*, origins=(), destinations=(), cargo="carga12"):
    from collections import defaultdict
    result=defaultdict(lambda:{"in":set(),"out":set()})
    for name in origins:result[name]["out"].add(cargo)
    for name in destinations:result[name]["in"].add(cargo)
    return result


class LogisticsCertificateTests(unittest.TestCase):
    manifest={12:("cerveja","Cerveja")}
    def assessment(self, comps, active, manifest=None, extras=None):
        return homol.assess(comps,active,manifest or self.manifest,
                            extras or {},policy,catalog)

    def test_economic_confirmed_is_not_equivalent_to_ets2_homologation(self):
        companies={
            "ambev":company("ambev",out_cargos={"beer"},editor=True),
            "supermercado_centro":company("supermercado_centro",
                                         in_cargos={"beer"},editor=True)}
        active=state(origins=["ambev"],destinations=["supermercado_centro"])
        cert=self.assessment(companies,active)
        cargo=cert["cargas"]["carga12"]
        self.assertEqual(cargo["total_pares_no_scs"],1)
        self.assertEqual(cargo["pares_economicos_distintos"],1)
        self.assertEqual(cargo["pares_com_editor_em_ambas_empresas"],1)
        self.assertEqual(cargo["status"],"CANDIDATA_TESTE_ETS2")
        self.assertFalse(cargo["homologado_no_ets2"])
        self.assertEqual(cert["cargas_homologadas_no_ets2"],0)

    def test_unknown_economy_in_scs_does_not_get_certified(self):
        companies={"desconhecida007":company("desconhecida007",editor=True),
                   "supermercado_centro":company("supermercado_centro",editor=True)}
        active=state(origins=["desconhecida007"],
                     destinations=["supermercado_centro"])
        cert=self.assessment(companies,active)["cargas"]["carga12"]
        self.assertEqual(cert["total_pares_no_scs"],1)
        self.assertEqual(cert["pares_economicos_distintos"],0)
        self.assertEqual(cert["status"],"SEM_EVIDENCIA_ECONOMICA")
        self.assertIn("Nao existe cadeia",cert["bloqueios"][0])

    def test_real_roles_without_editor_still_need_geography(self):
        comps={"ambev":company("ambev",editor=True),
               "supermercado_centro":company("supermercado_centro")}
        cargo=self.assessment(comps,state(origins=["ambev"],
                           destinations=["supermercado_centro"]))["cargas"]["carga12"]
        self.assertEqual(cargo["pares_economicos_distintos"],1)
        self.assertEqual(cargo["pares_com_editor_em_ambas_empresas"],0)
        self.assertEqual(cargo["status"],"ECONOMIA_SEM_EDITOR_VALIDADO")

    def test_coco_without_confirmed_origin_is_not_invented(self):
        comps={"fazenda_coco":company("fazenda_coco"),
               "supermercado_centro":company("supermercado_centro",editor=True)}
        active=state(origins=["fazenda_coco"],
                     destinations=["supermercado_centro"],cargo="carga24")
        extras={"carga24":{"categoria":"coco","nome":"Coco",
                           "body_types":["alta"],"id":"carga24"}}
        cert=self.assessment(comps,active,manifest={"carga24":("coco","Coco")},
                             extras=extras)["cargas"]["carga24"]
        self.assertEqual(cert["total_pares_no_scs"],1)
        self.assertEqual(cert["pares_economicos_distintos"],0)
        self.assertEqual(cert["status"],"SEM_EVIDENCIA_ECONOMICA")

    def test_nonexistent_company_in_map_cannot_be_validated(self):
        comps={"supermercado_centro":company("supermercado_centro",editor=True)}
        cert=self.assessment(comps,state(origins=["empresa_fantasma"],
                  destinations=["supermercado_centro"]))["cargas"]["carga12"]
        self.assertIn("inexistente",str(cert["bloqueios"]))
        self.assertEqual(cert["pares_economicos_distintos"],0)


if __name__=="__main__":
    unittest.main()
