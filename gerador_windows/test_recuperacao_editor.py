"""Testes estritos: cidades e prefabs recuperados SOMENTE de company_def."""
import tempfile
import unittest
from pathlib import Path

import recuperacao_editor as recovery
import politica_economica as policy
from test_gerador import g, zip_write


def editor(city="divinopolis", prefab="company_yard"):
    return ('SiiNunit\n{\ncompany_def : company.def.depot {\n'
            f' city: {city}\n prefab: {prefab}\n'
            '}\n}\n').encode()


class RecoverEditorTests(unittest.TestCase):
    def test_real_editor_in_existing_company_rescues_missing_map_def(self):
        comps={"material":g.Company("material")}
        raw=editor()
        report=recovery.recover(
            g,comps,{"def/company/material/editor/divinopolis.sii":raw})
        self.assertEqual(report["editor_ja_presente_na_def"],0)
        self.assertEqual(report["editor_recuperado_company_existente"],1)
        self.assertEqual(report["total_editor_depois"],1)
        self.assertEqual(policy.city_references(comps["material"])[0]["cidade"],
                         "divinopolis")
        self.assertIs(comps["material"].editor_files[
            "def/company/material/editor/divinopolis.sii"],raw)
        self.assertFalse(policy.city_references(comps["material"])[0]["prefab_confirmado"])

    def test_rejects_missing_city_prefab_and_unknown_company(self):
        comps={"materiais":g.Company("materiais")}
        source={
            "def/company/materiais/editor/fake.sii":b'city: falsa\n',
            "def/company/nunca_existiu/editor/abc.sii":editor("abc"),
            "def/company/materiais/editor/invalid.sii":
                b'company_def : a {\ncity: real\nprefab: ""\n}'
        }
        report=recovery.recover(g,comps,source)
        self.assertEqual(report["editor_rejeitado_empresa_ausente"],1)
        self.assertEqual(report["editor_rejeitado_sem_city_prefab"],2)
        self.assertTrue(report["sem_editor"])

    def test_optional_archive_requires_true_company_def(self):
        with tempfile.TemporaryDirectory() as t:
            extra=Path(t)/"editor_minas.zip"
            zip_write(extra,{
                "def/company/material/editor/setelagoas.sii":
                    editor("setelagoas","galpao_a"),
                "def/company/material/editor/divinopolis.sii":
                    editor("divinopolis","galpao_b")
            })
            comps={"material":g.Company("material")}
            result=recovery.recover(g,comps,{},extra)
            self.assertEqual(result["editor_recuperado_fonte_adicional"],2)
            self.assertEqual(result["total_editor_depois"],2)
            self.assertEqual(len(policy.city_references(comps["material"])),2)

    def test_conflict_keeps_def_primary_without_mixing_prefab(self):
        main=editor("divinopolis","original")
        secondary=editor("divinopolis","other")
        path="def/company/material/editor/divinopolis.sii"
        comps={"material":g.Company("material",editor_files={path:main})}
        result=recovery.recover(g,comps,{path:secondary})
        self.assertEqual(result["editor_conflito_entre_fontes"],1)
        self.assertEqual(comps["material"].editor_files[path],main)
        self.assertEqual(result["total_editor_depois"],1)

    def test_duplicate_signature_does_not_inflate_city_coverage(self):
        raw=editor("divinopolis","original")
        comps={"material":g.Company("material",
                   editor_files={"def/company/material/editor/one.sii":raw})}
        result=recovery.recover(g,comps,
                   {"def/company/material/editor/two.sii":raw})
        self.assertEqual(result["total_editor_depois"],1)
        self.assertEqual(result["editor_recuperado_company_existente"],0)


class RealAuditorRecoveryRegression(unittest.TestCase):
    def test_professional_audit_uses_existing_and_optional_editor_without_new_prefabs(self):
        import zipfile
        import auditor_existentes as audit
        from test_auditor_existentes import AuditorSCSRegression
        fixture=AuditorSCSRegression()
        fixture.setUp()
        try:
            with zipfile.ZipFile(fixture.existing) as z:
                payload={name:z.read(name) for name in z.namelist()}
            payload["def/company/ambev/editor/itumbiara.sii"]=editor(
                "itumbiara","cerveja_yard")
            zip_write(fixture.existing,payload)
            additional=fixture.root/"editor_suplementar_mg.zip"
            zip_write(additional,{
                "def/company/gerdau/editor/setelagoas.sii":
                    editor("setelagoas","sidyard")
            })
            result=audit.run(g,{
                "Minas_Gerais":{"existing":fixture.existing,
                                "map_def":fixture.baseline,
                                "editor_source":additional}
            },fixture.root/"audit_editor",mode="auditar",professional=True,
                 source_files={k:fixture.fixture.inp[k]
                               for k in ("mod","def1","def2")})[0]
            evidence=result["recuperacao_editor"]
            self.assertEqual(evidence["editor_recuperado_company_existente"],1)
            self.assertEqual(evidence["editor_recuperado_fonte_adicional"],1)
            self.assertEqual(evidence["total_editor_depois"],2)
            self.assertEqual(result["matriz_empresa_cidade"]["total_instancias_editor"],2)
            self.assertEqual(len(result["unidades_cidade_compativeis_esquecidas"]),0)
            self.assertTrue(result["nenhum_scs_gerado"])
        finally:
            fixture.tearDown()


class EldoradoEconomicIdentifiers(unittest.TestCase):
    def test_mosaic_and_cement_industry_are_specific_producers(self):
        for id in ("mosaico","mosaico2"):
            c=g.Company(id)
            self.assertEqual(policy.classify(c).role,"fabricante_fertilizante")
            self.assertTrue(policy.decide(c,"adubo","out").allowed)
            for cat,d in [("racao","out"),("sorgo","out"),
                          ("adubo","in"),("cimento","out")]:
                self.assertFalse(policy.decide(c,cat,d).allowed)
        for id in ("globcement","globcement2"):
            c=g.Company(id)
            self.assertEqual(policy.classify(c).role,"cimenteira")
            self.assertTrue(policy.decide(c,"cimento","out").allowed)
            self.assertFalse(policy.decide(c,"cerveja","out").allowed)

    def test_ceagesp_grains_require_def_and_fruit_hub_is_real(self):
        c=g.Company("ceagesp")
        self.assertEqual(policy.classify(c).role,"entreposto_hortigraos")
        self.assertTrue(policy.decide(c,"batata","out").allowed)
        self.assertTrue(policy.decide(c,"coco","in").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)
        c.old_in.add("corn")
        self.assertTrue(policy.decide(c,"milho","out").allowed)
        self.assertTrue(policy.decide(c,"milho","in").allowed)
        self.assertFalse(policy.decide(c,"soja","in").allowed)

    def test_soy_farm_requires_original_crop_evidence(self):
        c=g.Company("rocasoja")
        self.assertEqual(policy.classify(c).role,"desconhecida")
        c.old_out.add("soybeans")
        self.assertEqual(policy.classify(c).role,"fazenda_soja")
        self.assertTrue(policy.decide(c,"soja","out").allowed)
        self.assertTrue(policy.decide(c,"adubo","in").allowed)
        self.assertFalse(policy.decide(c,"milho","out").allowed)
        self.assertFalse(policy.decide(c,"soja","in").allowed)

    def test_other_brands_are_not_guessed(self):
        for id in ("bayer","ataca","agronord2","midwest"):
            self.assertEqual(policy.classify(g.Company(id)).role,
                             "desconhecida")


if __name__=="__main__":
    unittest.main()
