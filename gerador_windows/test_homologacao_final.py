"""Regressoes do protocolo de pre-homologacao REAL (sem simular o ETS2)."""
from __future__ import annotations
import csv
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from test_gerador import g, zip_write
from test_auditor_existentes import AuditorSCSRegression
import homologacao_final as final


class EndToEndPreflightTests(unittest.TestCase):
    def setUp(self):
        self.fixture=AuditorSCSRegression()
        self.fixture.setUp()
        self.root=self.fixture.root
        original=self.fixture.fixture.inp
        self.source={k:original[k] for k in ("mod","def1","def2")}
        self.txt=self.root/"cargas_24.txt"
        self.txt.write_text(
            "\n".join("carga"+str(n)+" = "+title
                      for n,(_category,title) in g.MANIFEST.items())+
            "\ncarga24 = Coco\n",encoding="utf-8")
        self.source["txt"]=self.txt
        self.maps={
            name:{"existing":self.fixture.existing,"map_def":self.fixture.baseline}
            for name in final.EXPECTED_MAPS}
    def tearDown(self):
        self.fixture.tearDown()

    def test_missing_24th_cargo_is_blocked_with_json_and_no_maps_published(self):
        target=self.root/"no_coco"
        summary=final.run(g,self.source,self.maps,target)
        self.assertEqual(summary["status_pre_homologacao"],"BLOQUEADO_TECNICO")
        self.assertFalse(summary["homologado_no_ets2"])
        self.assertTrue((target/"RESULTADO_PRE_HOMOLOGACAO.json").exists())
        self.assertTrue((target/"01_LIBRELATO"/
                         "DIAGNOSTICO_LIBRELATO_CARGAS_ORIGINAIS.json").exists())
        self.assertEqual(list(target.rglob("*.scs")),[])

    def test_three_maps_24_cargos_are_classified_not_falsely_homologated(self):
        with zipfile.ZipFile(self.source["mod"]) as z:
            content={p:z.read(p) for p in z.namelist()}
        content["def/cargo/carga24.sui"]=(
            b'cargo_data : cargo.carga24 {\n body_types[]: alta\n}\n')
        zip_write(self.source["mod"],content)
        target=self.root/"full_24"
        summary=final.run(g,self.source,self.maps,target)
        self.assertEqual(len(summary["mapas"]),3)
        self.assertEqual(summary["ensaios_de_jogo_planejados"],72)
        self.assertEqual(summary["status_pre_homologacao"],"BLOQUEADO_ECONOMICO")
        self.assertFalse(summary["homologado_no_ets2"])
        with (target/"MATRIZ_ENSAIOS_ETS2.csv").open(
                encoding="utf-8-sig",newline="") as fp:
            rows=list(csv.DictReader(fp,delimiter=";"))
        self.assertEqual(len(rows),72)
        self.assertEqual({x["carga"] for x in rows},
                         {"carga"+str(n) for n in range(1,25)})
        self.assertEqual({x["mapa"] for x in rows},set(final.EXPECTED_MAPS))
        for name in final.EXPECTED_MAPS:
            self.assertTrue((target/"02_MAPAS"/
                             ("QUALIDADE_LOGISTICA_"+name.upper()+".json")).exists())
        self.assertEqual(list(target.rglob("*.scs")),[])

    def test_rbr_only_24_cargo_preflight_no_unrelated_map_required(self):
        with zipfile.ZipFile(self.source["mod"]) as z:
            contents={p:z.read(p) for p in z.namelist()}
        contents["def/cargo/carga24.sui"]=(
            b'cargo_data : cargo.carga24 {\n body_types[]: alta\n}\n')
        zip_write(self.source["mod"],contents)
        root=self.root/"preflight_rbr_isolado"
        report=final.run(g,self.source,{"RBR":self.maps["RBR"]},root,
                         expected_maps=("RBR",))
        self.assertTrue(report["preflight_isolado"])
        self.assertEqual(report["mapas_esperados"],["RBR"])
        self.assertEqual(report["ensaios_de_jogo_planejados"],24)
        self.assertEqual([m["nome"] for m in report["mapas"]],["RBR"])
        self.assertFalse(report["homologado_no_ets2"])
        with (root/"MATRIZ_ENSAIOS_ETS2.csv").open(
                newline="",encoding="utf-8-sig") as fp:
            entries=list(csv.DictReader(fp,delimiter=";"))
        self.assertEqual(len(entries),24)
        self.assertEqual({e["mapa"] for e in entries},{"RBR"})
        self.assertTrue(all(e["entrega_realizada"]=="" for e in entries))
        self.assertFalse((root/"02_MAPAS"/"AUDITORIA_ELDORADO.json").exists())
        self.assertFalse((root/"02_MAPAS"/"AUDITORIA_MINAS_GERAIS.json").exists())
        self.assertEqual(list(root.rglob("*.scs")),[])

    def test_log_errors_are_recorded_not_confused_with_gameplay(self):
        log=self.root/"game.log.txt"
        log.write_text("00:00:00 <WARNING> benign\n"
                       "00:00:01 <ERROR> Missing cargo model\n",encoding="utf-8")
        result=final.assess_logs(log)
        self.assertEqual(result["situacao"],"ERROS_DE_JOGO_ENCONTRADOS")
        self.assertEqual(len(result["erros"]),1)
        self.assertFalse(result["teste_real_ets2_comprovado"])

    def test_missing_map_is_not_silently_ignored(self):
        with self.assertRaisesRegex(ValueError,"Minas_Gerais, Eldorado e RBR"):
            final.run(g,self.source,
                      {"Eldorado":self.maps["Eldorado"]},
                      self.root/"incomplete")


if __name__=="__main__":
    unittest.main()
