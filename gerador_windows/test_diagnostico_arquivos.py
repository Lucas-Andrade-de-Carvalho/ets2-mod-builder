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
    def test_large_archive_reads_only_definitions(self):
        """Texturas e arquivos binarios nao devem ser descompactados."""
        from unittest.mock import patch
        arc=self.root/"grande_simulado.scs"
        zip_write(arc,{
            "vehicle/textures/unused.dds":b"DDS"+b"X"*50000,
            "sound/unused.bank":b"nao ler",
            "def/cargo/carga24.sui":b"cargo_data : cargo.carga24 { body_types[]: alta }",
        })
        originals=zipfile.ZipFile.read
        read_names=[]
        def observed(zf,member,*args,**kwargs):
            read_names.append(member.filename if hasattr(member,"filename") else member)
            return originals(zf,member,*args,**kwargs)
        with patch.object(zipfile.ZipFile,"read",observed):
            result=g.zip_members(arc)
        self.assertEqual(list(result),["def/cargo/carga24.sui"])
        self.assertEqual(read_names,["def/cargo/carga24.sui"])

    def test_cli_diagnostic_runs_without_any_map_defs(self):
        import subprocess,sys
        output=self.root/"cli_only_reboque"
        args=[sys.executable,str(Path(g.__file__).resolve()),"--cli",
              "--diagnose-librelato",
              "--mod",str(self.input["mod"]),
              "--def1",str(self.input["def1"]),
              "--def2",str(self.input["def2"]),
              "--txt",str(self.txt),"--output",str(output)]
        returned=subprocess.run(args,capture_output=True,text=True,timeout=30)
        self.assertEqual(returned.returncode,0,returned.stderr)
        result=json.loads((output/"DIAGNOSTICO_LIBRELATO_CARGAS_ORIGINAIS.json")
                          .read_text(encoding="utf-8"))
        self.assertEqual(result["total_cargas_catalogo"],23)
        self.assertFalse(result["erros"])

    def test_cargo_model_154_and_loading_method_crosscheck(self):
        p=self.input["mod"]
        with zipfile.ZipFile(p) as archive:
            content={name:archive.read(name) for name in archive.namelist()}
        content["def/vehicle/trailer_owned/test/body/grade.sii"]=(
            b"body_type: alta\ncargo_loading_methods[]: area\n")
        content["def/vehicle/cargo/carga1/model_area.sii"]=(
            b"cargo_model_match : .area {\n"
            b" loading_method: area\n"
            b' data_path[]: "/def/vehicle/cargo/carga1/accessory.sii"\n}')
        content["def/vehicle/cargo/carga1/accessory.sii"]=(
            b"accessory_cargo_data: .carga { }")
        zip_write(p,content)
        _dest,report=diag.inspect(g,self.input,self.txt,self.root/"models_ok")
        evidence=report["carga_modelo_154"]["carga1"]
        self.assertEqual(evidence["status"],"MODELO_ENCONTRADO")
        self.assertEqual(evidence["metodos_do_modelo"],["area"])
        self.assertEqual(evidence["metodos_das_carrocerias"],["area"])
        self.assertEqual(evidence["modelos_referenciados_ausentes_nas_fontes"],[])
        self.assertFalse(evidence["incompatibilidade_explicita_de_metodos"])

        content["def/vehicle/trailer_owned/test/body/grade.sii"]=(
            b"body_type: alta\ncargo_loading_methods[]: bulk\n")
        zip_write(p,content)
        _dest,broken=diag.inspect(g,self.input,self.txt,self.root/"models_mismatch")
        self.assertTrue(broken["carga_modelo_154"]["carga1"][
            "incompatibilidade_explicita_de_metodos"])
        self.assertIn("carga1",str(broken["erros"]))
        self.assertEqual(broken["resultado"],"BLOQUEADO")

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
    def test_binary_invalid_cargo_yields_blocking_json_not_crash(self):
        p=self.input["mod"]
        with zipfile.ZipFile(p) as arc:
            content={path:arc.read(path) for path in arc.namelist()}
        content["def/cargo/carga1.sui"]=b"cargo_data : cargo.carga1 {\x00 }"
        zip_write(p,content)
        filename,report=diag.inspect(g,self.input,self.txt,self.root/"binary_invalid")
        self.assertTrue(filename.exists())
        self.assertEqual(report["resultado"],"BLOQUEADO")
        self.assertIn("carga1",str(report["erros"]))

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
