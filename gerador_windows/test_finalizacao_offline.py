"""Regressoes da entrega offline em 3 mapas: sem falsificar testes ETS2."""
import json
import unittest
import zipfile
from pathlib import Path
from test_auditor_existentes import AuditorSCSRegression
from test_gerador import g, zip_write
import finalizacao_offline as finish


class ThreeMapOfflineFinalizationTests(unittest.TestCase):
    def setUp(self):
        self.case=AuditorSCSRegression()
        self.case.setUp()
        self.root=self.case.root
        fixture=self.case.fixture.inp
        self.src={k:fixture[k] for k in ("mod","def1","def2")}
        self.txt=self.root/"descricao_24.txt"
        self.txt.write_text(
            "\n".join("carga"+str(n)+" = "+title
                      for n,(_category,title) in g.MANIFEST.items())+
            "\ncarga24 = Coco\n",encoding="utf-8")
        self.src["txt"]=self.txt
        self.maps={
            name:{"existing":self.case.existing,"map_def":self.case.baseline}
            for name in finish.MAPS}
    def tearDown(self):
        self.case.tearDown()

    def add_coco_to_real_sources(self):
        with zipfile.ZipFile(self.src["mod"]) as z:
            files={p:z.read(p) for p in z.namelist()}
        files["def/cargo/carga24.sui"]=(
            b"cargo_data : cargo.carga24 {\n body_types[]: alta\n}\n")
        zip_write(self.src["mod"],files)

    def test_missing_coco_blocks_without_three_published_scs(self):
        root=self.root/"missing_coco"
        report=finish.run(g,self.src,self.maps,root)
        self.assertEqual(report["status"],"BLOQUEADO_SEM_ENTREGA")
        self.assertTrue(report["nenhum_scs_publicado"])
        self.assertEqual(list(root.rglob("*.scs")),[])
        self.assertTrue((root/"RESULTADO_FINALIZACAO_OFFLINE.json").is_file())

    def test_three_realistic_archives_are_reaudited_and_unchanged(self):
        self.add_coco_to_real_sources()
        root=self.root/"full"
        before={k:g.hash_source(v) for k,v in self.src.items()}
        before.update({"scs":g.hash_source(self.case.existing),
                       "map":g.hash_source(self.case.baseline)})
        report=finish.run(g,self.src,self.maps,root)
        self.assertEqual(len(report["arquivos_corrigidos"]),3)
        self.assertEqual(set(report["mapas_reauditados"]),set(finish.MAPS))
        self.assertEqual(report["reescritas_residuais"],0)
        self.assertTrue(report["originais_preservados"])
        self.assertFalse(report["homologado_no_ets2"])
        self.assertEqual(report["status"],"CANDIDATAS_COM_LACUNAS_DOCUMENTADAS")
        delivered=root/"02_CANDIDATAS_PARA_JOGO"
        for row in report["arquivos_corrigidos"]:
            file=delivered/row["arquivo"]
            self.assertTrue(file.is_file())
            self.assertEqual(g.hash_source(file),row["sha256"])
            with zipfile.ZipFile(file) as z:
                self.assertIsNone(z.testzip())
        self.assertEqual(
            {k:g.hash_source(v) for k,v in self.src.items()},
            {k:before[k] for k in self.src})
        self.assertEqual(before["scs"],g.hash_source(self.case.existing))
        self.assertEqual(before["map"],g.hash_source(self.case.baseline))
        self.assertEqual(json.loads(
            (root/"RESULTADO_FINALIZACAO_OFFLINE.json").read_text())["status"],
            "CANDIDATAS_COM_LACUNAS_DOCUMENTADAS")
        self.assertTrue((delivered/"02_REAUDITORIA"/
                         "AUDITORIA_RBR.json").exists())

    def test_refuses_second_delivery_into_same_directory(self):
        self.add_coco_to_real_sources()
        root=self.root/"never_overwrite"
        finish.run(g,self.src,self.maps,root)
        with self.assertRaises(FileExistsError):
            finish.run(g,self.src,self.maps,root)

    def test_missing_map_never_produces_any_new_scs(self):
        self.add_coco_to_real_sources()
        maps={key:value for key,value in self.maps.items() if key!="RBR"}
        out=self.root/"incomplete"
        with self.assertRaises(ValueError):
            finish.run(g,self.src,maps,out)
        self.assertFalse(list(out.rglob("*.scs")))


if __name__=="__main__":
    unittest.main()
