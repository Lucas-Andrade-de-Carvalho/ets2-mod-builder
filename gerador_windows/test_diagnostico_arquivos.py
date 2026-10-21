"""Regressoes para verificacao tecnica do MOD/DEF1/DEF2 e TXT."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from test_gerador import Regression, zip_write, g
import diagnostico_arquivos as diag


class DiagnosticTrailerTests(unittest.TestCase):
    def setUp(self):
        self.fixture=Regression()
        self.fixture.setUp()
        self.root=self.fixture.root
        self.txt=self.root/"legendas.txt"
        self.txt.write_text("\n".join(
            "carga"+str(n)+" = "+title for n,(_cat,title) in g.MANIFEST.items()),
            encoding="utf-8")
        self.input={**self.fixture.inp,"txt":self.txt}
    def tearDown(self):
        self.fixture.tearDown()
    def test_all_sources_and_sha_are_auditable(self):
        dest,report=diag.inspect(g,self.input,self.txt,self.root/"report")
        self.assertEqual(report["total_cargas_catalogo"],23)
        self.assertEqual(len(report["fontes"]),3)
        self.assertEqual(len(report["cargas"]),23)
        self.assertFalse(report["erros"])
        self.assertEqual(json.loads(dest.read_text(encoding="utf-8"))["fontes"],
                         report["fontes"])
        for cargo in report["cargas"]:
            self.assertEqual(len(cargo["sha256"]),64)
            self.assertFalse(cargo["validado_no_ets2"])
    def test_missing_txt_reports_error_not_homologation(self):
        self.txt.write_text("carga1: Soja\n",encoding="utf-8")
        dest,report=diag.inspect(g,self.input,self.txt,self.root/"bad")
        self.assertEqual(report["resultado"],"BLOQUEADO")
        self.assertIn("TXT",str(report["erros"]))
        self.assertTrue(dest.exists())
    def test_divergent_cargo_definitions_are_visible(self):
        path=self.fixture.inp["def1"]
        with zipfile.ZipFile(path) as archive:
            mapping={p:archive.read(p) for p in archive.namelist()}
        mapping["def/cargo/carga1.sii"]=(
            b'SiiNunit\n{\n cargo_data : cargo.carga1 {\n'
            b' body_types[]: tanque\n }\n}\n')
        zip_write(path,mapping)
        dest,report=diag.inspect(g,self.input,self.txt,self.root/"conflict")
        self.assertEqual(report["resultado"],"BLOQUEADO")
        self.assertTrue(any("carga1" in x for x in report["erros"]))
        self.assertTrue(dest.exists())


if __name__=="__main__":
    unittest.main()
