"""Regressao do cadastro dinamico e das permissoes originais (sem arquivos privados)."""
from __future__ import annotations
import base64
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import catalogo_cargas as catalog
import politica_economica as policy
import auditor_existentes as existing
from test_gerador import Regression, zip_write, old, g


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.file=self.root/"catalog.json"
        self.raw=(b'SiiNunit\n{\n cargo_data : cargo.acucar_ensacado {\n'
                  b' name: "Acucar ensacado"\n body_types[]: alta\n'
                  b' mass: 15000\n }\n}\n')
        self.origin=self.root/"acucar.sii"
        self.origin.write_bytes(self.raw)
        self.spec={
            "id":"acucar_ensacado","nome":"Acucar ensacado",
            "descricao":"Usinas de acucar fornecem; supermercados compram para revenda",
            "categoria":"acucar","subcategoria":"ensacado",
            "aliases":["bagged_sugar","acucar"],
            "out_roles":["usina_acucar","distribuidor"],"in_roles":["supermercado","alimentos"],
            "forbidden_roles":["transportadora"],"out_evidence":"setor",
            "in_evidence":"setor",
            "out_companies":[],"in_companies":[],
            **catalog.import_definition(self.origin,"acucar_ensacado")
        }
    def tearDown(self):
        self.tmp.cleanup()
    def save_one(self):
        catalog.save({self.spec["id"]:self.spec},self.file,
                     reserved={catalog.cargo_id(x) for x in g.MANIFEST})
    def test_24_then_25_dynamic_and_remove(self):
        self.save_one()
        extras=catalog.load(self.file)
        self.assertEqual(len(catalog.manifest(g.MANIFEST,extras)),24)
        two=dict(self.spec);two["id"]="xilose_ensacada";two["nome"]="Xilose"
        raw=self.raw.replace(b"acucar_ensacado",b"xilose_ensacada")
        two["sii_base64"]=base64.b64encode(raw).decode("ascii")
        two["sha256"]=""  # revalida checksum
        catalog.save({**extras,"xilose_ensacada":two},self.file)
        self.assertEqual(len(catalog.manifest(g.MANIFEST,catalog.load(self.file))),25)
        catalog.save({"xilose_ensacada":catalog.load(self.file)["xilose_ensacada"]},
                     self.file)
        self.assertEqual(len(catalog.manifest(g.MANIFEST,catalog.load(self.file))),24)
        self.assertEqual(len(g.MANIFEST),23)  # sem tocar nos originais
    def test_reject_wrong_id_and_tampering(self):
        bad=dict(self.spec);bad["id"]="carga24"
        with self.assertRaisesRegex(ValueError,"ID"):catalog.validate(bad)
        bad=dict(self.spec);bad["id"]="acucar_errado"
        with self.assertRaisesRegex(ValueError,"cargo_data"):catalog.validate(bad)
        bad=dict(self.spec);bad["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SHA-256"):catalog.validate(bad)
        bad=dict(self.spec);bad["out_roles"]=[];bad["out_companies"]=[]
        with self.assertRaisesRegex(ValueError,"OUT"):catalog.validate(bad)
    def test_missing_body_and_corrupted_json(self):
        bad=self.raw.replace(b"body_types[]: alta",b"name: sem_corpo")
        self.origin.write_bytes(bad)
        with self.assertRaisesRegex(ValueError,"body_types"):
            catalog.import_definition(self.origin,"acucar_ensacado")
        self.file.write_text('{"schema":1,"cargas":[{}]}')
        with self.assertRaises(ValueError):catalog.load(self.file)
    def test_sugar_buyer_and_supplier_not_generic_carrier(self):
        self.save_one()
        spec=catalog.load(self.file)["acucar_ensacado"]
        company=lambda name: g.Company(name)
        yes_out=catalog.evaluate(company("usina_acucar_ouro"),spec,"out",
                                 policy.classify(company("usina_acucar_ouro")))
        yes_in=catalog.evaluate(company("supermercado_centro"),spec,"in",
                                policy.classify(company("supermercado_centro")))
        no_out=catalog.evaluate(company("brasilog"),spec,"out",
                                policy.classify(company("brasilog")))
        wholesale=catalog.evaluate(company("distribuidor_geral"),spec,"out",
                                   policy.classify(company("distribuidor_geral")))
        self.assertTrue(yes_out.allowed)
        self.assertTrue(yes_in.allowed)
        self.assertFalse(no_out.allowed)
        self.assertFalse(wholesale.allowed)
    def test_24th_cargo_in_generator_and_body_gate(self):
        self.save_one()
        fixture=Regression()
        fixture.setUp()
        try:
            # Acrescenta duas empresas com necessidade demonstravel a DEF sintetica.
            from test_gerador import zip_write
            p=fixture.inp["maps"]["Minas_Gerais"]
            with zipfile.ZipFile(p) as z:
                files={name:z.read(name) for name in z.namelist()}
            files["def/company/usina_acucar_ouro/out/acucar.sii"]=old("bagged_sugar")
            files["def/company/supermercado_centro/in/acucar.sii"]=old("bagged_sugar")
            zip_write(p,files)
            inputs={**fixture.inp,"maps":{"Minas_Gerais":p},"catalogo":self.file}
            result=g.generate(inputs,self.root/"gerado",professional=True,
                              require_complete=False)
            self.assertEqual(len(result),1)
            name,scs,data=result[0]
            self.assertIn("acucar_ensacado",data["cadeias"])
            self.assertEqual(data["cobertura_catalogo"]["total"],24)
            with zipfile.ZipFile(scs) as z:
                self.assertEqual(z.read("def/cargo/acucar_ensacado.sii"),self.raw)
                self.assertIn(b"cargo.acucar_ensacado",z.read(
                    "def/company/usina_acucar_ouro/out/acucar_ensacado.sii"))
                self.assertIn(b"cargo.acucar_ensacado",z.read(
                    "def/company/supermercado_centro/in/acucar_ensacado.sii"))
            badspec=dict(self.spec)
            raw=self.raw.replace(b"body_types[]: alta",b"body_types[]: tanque_inexistente")
            badspec["sii_base64"]=base64.b64encode(raw).decode()
            badspec["sha256"]=""
            catalog.save({"acucar_ensacado":badspec},self.file)
            with self.assertRaisesRegex(ValueError,"acucar_ensacado"):
                g.generate(inputs,self.root/"invalido",professional=True,require_complete=False)
            self.assertFalse(list((self.root/"invalido").glob("*.scs")))
        finally:
            fixture.tearDown()
    def test_existing_company_keeps_originals_and_adds_new_cargo(self):
        self.save_one()
        fixture=Regression()
        fixture.setUp()
        try:
            source={"def/company/usina_acucar_ouro/out/bagged_sugar.sii":old("bagged_sugar"),
                    "def/company/supermercado_centro/in/bagged_sugar.sii":old("bagged_sugar"),
                    "def/company/brasilog/out/beer.sii":old("beer")}
            map_def=self.root/"map.zip"
            zip_write(map_def,source)
            existing_scs=self.root/"existing.scs"
            old_content={"def/company/ambev/out/carga12.sii":g.cargo_sii("carga12"),
                         "def/company/brasilog/out/beer.sii":old("beer"),
                         "README.txt":b"ORIGINAL"}
            zip_write(existing_scs,old_content)
            original_bytes=existing_scs.read_bytes()
            output=self.root/"corrected"
            result=existing.run(g,{"Minas_Gerais":{"existing":existing_scs,
                        "map_def":map_def}},output,mode="corrigir",professional=True,
                        source_files={"mod":fixture.inp["mod"],"def1":fixture.inp["def1"],
                                      "def2":fixture.inp["def2"],"catalogo":self.file})[0]
            self.assertEqual(original_bytes,existing_scs.read_bytes())
            self.assertEqual(result["total_cargas_catalogo"],24)
            with zipfile.ZipFile(output/result["arquivo_corrigido"]) as z:
                self.assertEqual(z.read("def/cargo/acucar_ensacado.sii"),self.raw)
                self.assertIn("def/company/usina_acucar_ouro/out/audit_acucar_ensacado.sii",z.namelist())
                self.assertIn("def/company/supermercado_centro/in/audit_acucar_ensacado.sii",z.namelist())
                self.assertEqual(z.read("README.txt"),b"ORIGINAL")
                self.assertEqual(z.read("def/company/ambev/out/carga12.sii"),
                                 old_content["def/company/ambev/out/carga12.sii"])
        finally:
            fixture.tearDown()


if __name__=="__main__":
    unittest.main()
