"""Teste seguro: Company existente com erros propositais e DEF original como evidencia."""
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from test_gerador import Regression as Fixture, zip_write, old, g
import auditor_existentes as audit

class AuditorSCSRegression(unittest.TestCase):
    def setUp(self):
        self.fixture=Fixture(methodName="test_neutralization")
        self.fixture.setUp()
        self.root=self.fixture.root
        self.baseline=self.root/"mapa_original_eldorado.zip"
        source={
            "brasilog/out/potatoes.sii":old("potatoes"),
            "brasilog/in/oranges.sii":old("oranges"),
            "eldorado_bananas/in/fertilizer.sii":old("fertilizer"),
            "eldorado_bananas/out/bananas.sii":old("bananas"),
            "fiat/in/steel_coils.sii":old("steel_coils"),
            "gerdau/out/steel_coils.sii":old("steel_coils"),
            "ambev/out/beer.sii":old("beer"),
            "supermercado_centro/in/beer.sii":old("beer"),
            "fazenda_potato/out/potatoes.sii":old("potatoes"),
            "ceasa/in/potatoes.sii":old("potatoes"),
            "serraria_ouro/out/timber.sii":old("timber"),
            "sucatao_ouro/in/pallets.sii":old("pallets"),
            "desconhecida007/in/oranges.sii":old("oranges"),
        }
        zip_write(self.baseline,source)
        self.existing=self.root/"Company_Eldorado_Atual.scs"
        payload={
            "def/company/brasilog/out/carga7.sii":g.cargo_sii("carga7"),
            "def/company/eldorado_bananas/in/carga7.sii":g.cargo_sii("carga7"),
            "def/company/fiat/out/carga9.sii":g.cargo_sii("carga9"),
            "def/company/fiat/in/carga9.sii":g.cargo_sii("carga9"),
            "def/company/gerdau/out/carga9.sii":g.cargo_sii("carga9"),
            "def/company/ambev/out/carga12.sii":g.cargo_sii("carga12"),
            "def/company/ambev/out/carga12_duplicate.sii":g.cargo_sii("carga12"),
            "def/company/segredo123/in/carga12.sii":g.cargo_sii("carga12"),
            "def/company/desconhecida007/in/carga8.sii":g.cargo_sii("carga8"),
            "def/company/brasilog/out/beer.sii":old("beer"),
            "def/company/eldorado_bananas/editor/village.sii":b"ABC ORIGINAL EDITOR",
            "ReadMe.txt":b"NAME: ORIGINAL PERSISTS",
            "def/cargo/carga16.sui":b"cargo_data : cargo.carga16 { prob_coef: 0.14 }\n",
        }
        zip_write(self.existing,payload)
        self.payload=payload
    def tearDown(self):
        self.fixture.tearDown()
    def invoke(self,mode="corrigir",out=None):
        return audit.run(g,{"Eldorado":{"existing":self.existing,
                                         "map_def":self.baseline}},
                         out or self.root/"audit_output",mode=mode)

    def test_correct_false_routes_and_preserve_valid_originals(self):
        old_bytes=self.existing.read_bytes()
        result=self.invoke()
        r=result[0]
        self.assertTrue(r["permissoes_removidas"]>=4)
        self.assertTrue(r["arquivos_adicionados"]>=2)
        self.assertTrue(r["pendencias_revisao"]>=1)
        self.assertGreaterEqual(r["permissoes_sem_evidencia_preservadas"],1)
        self.assertGreaterEqual(r["empresas_classificacao_pendente"],1)
        self.assertEqual(self.existing.read_bytes(),old_bytes)
        output=self.root/"audit_output"/r["arquivo_corrigido"]
        self.assertTrue(output.exists())
        self.assertNotEqual(output,self.existing)
        with zipfile.ZipFile(output) as z:
            self.assertIsNone(z.testzip())
            for filename in ("def/company/brasilog/out/carga7.sii",
                             "def/company/eldorado_bananas/in/carga7.sii",
                             "def/company/fiat/out/carga9.sii"):
                self.assertIn('cargo: ""',z.read(filename).decode("utf-8"))
            self.assertIn("cargo.carga9",z.read(
                "def/company/fiat/in/carga9.sii").decode("utf-8"))
            self.assertIn("cargo.carga12",z.read(
                "def/company/ambev/out/carga12.sii").decode("utf-8"))
            self.assertIn('cargo: ""',z.read(
                "def/company/ambev/out/carga12_duplicate.sii").decode("utf-8"))
            self.assertIn('cargo: "cargo.beer"',z.read(
                "def/company/brasilog/out/beer.sii").decode("utf-8"))
            self.assertIn("def/company/fazenda_potato/out/audit_carga7.sii",z.namelist())
            self.assertIn("def/company/ceasa/in/audit_carga7.sii",z.namelist())
            self.assertEqual(z.read("ReadMe.txt"),b"NAME: ORIGINAL PERSISTS")
            self.assertEqual(z.read(
                "def/company/eldorado_bananas/editor/village.sii"),b"ABC ORIGINAL EDITOR")
            self.assertEqual(z.read("def/cargo/carga16.sui"),
                             self.payload["def/cargo/carga16.sui"])
        report=json.loads((self.root/"audit_output"/"AUDITORIA_ELDORADO.json")
                         .read_text(encoding="utf-8"))
        removed={(x["empresa"],x["direcao"],x["carga"]) for x in
                 report["decisoes"] if x["acao"]=="REMOVER"}
        self.assertIn(("brasilog","out","carga7"),removed)
        self.assertIn(("eldorado_bananas","in","carga7"),removed)
        self.assertIn(("fiat","out","carga9"),removed)
        self.assertIn("carga7",report["rotas_depois"])
        self.assertLess(report["rotas_completas_depois"],23)
        self.assertEqual(report["status"],"PENDENTE_VALIDACAO_ECONOMICA")

    def test_analogous_transport_safety_applies_to_minas_and_rbr(self):
        for map_name in ("Minas_Gerais","RBR"):
            with self.subTest(map=map_name):
                out=self.root/("audit_"+map_name)
                result=audit.run(g,{map_name:{"existing":self.existing,
                                             "map_def":self.baseline}},out)[0]
                with zipfile.ZipFile(out/result["arquivo_corrigido"]) as z:
                    self.assertIn(b'cargo: ""',
                                  z.read("def/company/brasilog/out/carga7.sii"))
                    self.assertIn(b'cargo: ""',
                                  z.read("def/company/eldorado_bananas/in/carga7.sii"))
                    self.assertIn(b'cargo: ""',
                                  z.read("def/company/fiat/out/carga9.sii"))
                self.assertEqual(result["mapa"],map_name)

    def test_exhaustive_reports_include_empty_and_editor_company_files(self):
        self.invoke(out=self.root/"complete_inventory")
        folder=self.root/"complete_inventory"
        import csv
        with (folder/"INVENTARIO_COMPLETO_ELDORADO.csv").open(
             encoding="utf-8-sig",newline="") as fp:
            rows=list(csv.DictReader(fp,delimiter=";"))
        self.assertEqual(len(rows),10)  # todos os IN/OUT ja existentes no SCS
        with (folder/"EMPRESAS_COMPLETAS_ELDORADO.csv").open(
             encoding="utf-8-sig",newline="") as fp:
            all_rows=list(csv.DictReader(fp,delimiter=";"))
        self.assertEqual(len(all_rows),11)
        # A empresa de banana aparece na DEF mesmo sem receber batatas validas.
        self.assertIn("eldorado_bananas",{row["empresa"] for row in all_rows})

    def test_multi_map_audit_never_publishes_partial_scs(self):
        dest=self.root/"atomic_result"
        missing_def=self.root/"missing_map.zip"
        original=self.existing.read_bytes()
        with self.assertRaises(Exception):
            audit.run(g, {
               "Minas_Gerais":{"existing":self.existing,"map_def":self.baseline},
               "Eldorado":{"existing":self.existing,"map_def":missing_def}
            },dest)
        self.assertEqual(self.existing.read_bytes(),original)
        self.assertEqual(list(dest.glob("*.scs")),[])
        self.assertTrue((dest/"AUDITORIA_INCOMPLETA.txt").is_file())

    def test_professional_audit_exports_economic_certification_ledger(self):
        out=self.root/"certificacao_pro"
        mod=self.fixture.inp
        result=audit.run(g,{"Eldorado":{"existing":self.existing,
                            "map_def":self.baseline}},out,mode="auditar",
                            professional=True,source_files={
                                "mod":mod["mod"],"def1":mod["def1"],
                                "def2":mod["def2"]})[0]
        quality=result["qualidade_logistica"]
        self.assertIsNotNone(quality)
        self.assertEqual(quality["cargas_homologadas_no_ets2"],0)
        self.assertEqual(len(quality["cargas"]),23)
        self.assertTrue((out/"QUALIDADE_LOGISTICA_ELDORADO.json").exists())
        self.assertTrue((out/"CADEIAS_COMPROVADAS_ELDORADO.csv").exists())
        self.assertFalse(list(out.glob("*.scs")))
        for row in quality["cargas"].values():
            self.assertFalse(row["homologado_no_ets2"])
            self.assertGreaterEqual(row["total_pares_no_scs"],
                                    row["pares_economicos_distintos"])
            self.assertGreaterEqual(row["pares_economicos_distintos"],
                                    row["pares_com_editor_em_ambas_empresas"])

    def test_reauditing_corrected_scs_is_idempotent(self):
        """Executar a mesma correção de novo não deve inventar mudanças."""
        first=self.invoke(out=self.root/"primeira")[0]
        before=self.root/"primeira"/first["arquivo_corrigido"]
        before_bytes=before.read_bytes()
        dest=self.root/"segunda"
        again=audit.run(g,{"Eldorado":{"existing":before,
                                      "map_def":self.baseline}},dest)[0]
        self.assertEqual(again["arquivos_adicionados"],0)
        self.assertEqual(again["arquivos_modificados"],0)
        self.assertEqual(again["permissoes_removidas"],0)
        self.assertEqual(before.read_bytes(),before_bytes)
        with zipfile.ZipFile(dest/again["arquivo_corrigido"]) as z:
            self.assertIsNone(z.testzip())
        self.assertEqual(first["rotas_depois"],again["rotas_depois"])

    def test_audit_only_creates_ledger_not_scs(self):
        out=self.root/"dry_run"
        self.invoke(mode="auditar",out=out)
        self.assertEqual(list(out.glob("*.scs")),[])
        self.assertTrue((out/"AUDITORIA_ELDORADO.json").exists())
        self.assertTrue((out/"AUDITORIA_ELDORADO.csv").exists())
        self.assertTrue((out/"COBERTURA_ELDORADO_23.csv").exists())

    def test_only_selected_eldorado_never_changes_minas_or_rbr(self):
        out=self.root/"originals_preserved"
        out.mkdir()
        mina=out/"ETS2_MINAS_GERAIS_COMPANY.scs"
        rbr=out/"ETS2_RBR_COMPANY.scs"
        mina.write_bytes(b"MG_KEEP")
        rbr.write_bytes(b"RBR_KEEP")
        self.invoke(out=out)
        self.assertEqual(mina.read_bytes(),b"MG_KEEP")
        self.assertEqual(rbr.read_bytes(),b"RBR_KEEP")
        self.assertEqual(len(list(out.glob("*AUDITADA_V25_*.scs"))),1)

    def test_unclassified_company_is_preserved_without_duplicated_error_alerts(self):
        """Regressao dos 2.207 avisos: herdados desconhecidos nao sao erros."""
        out=self.root/"sem_alarme_falso"
        result=self.invoke(mode="corrigir",out=out)[0]
        unknown=[x for x in result["decisoes"]
                 if x["empresa"]=="desconhecida007" and x["carga"]=="carga8"]
        self.assertEqual(len(unknown),1)
        self.assertEqual(unknown[0]["acao"],"PRESERVAR_SEM_EVIDENCIA")
        self.assertNotIn(unknown[0],[
            x for x in result["decisoes"] if x["acao"]=="REVISAR"])
        self.assertGreaterEqual(result["permissoes_sem_evidencia_preservadas"],1)
        self.assertEqual(result["diagnostico_pendencias"][
            "permissoes_herdadas_preservadas_sem_evidencia"],
            result["permissoes_sem_evidencia_preservadas"])
        self.assertTrue((out/"RESUMO_VALIDACAO_ELDORADO.txt").exists())
        self.assertTrue((out/"PENDENCIAS_CLASSIFICACAO_ELDORADO.csv").exists())
        with zipfile.ZipFile(out/result["arquivo_corrigido"]) as zipf:
            self.assertEqual(
                zipf.read("def/company/desconhecida007/in/carga8.sii"),
                self.payload["def/company/desconhecida007/in/carga8.sii"])
        second=self.invoke(mode="corrigir",out=self.root/"sem_alarme_falso_2")[0]
        self.assertEqual(second["permissoes_sem_evidencia_preservadas"],
                         result["permissoes_sem_evidencia_preservadas"])

    def test_targeted_neutralization_never_clears_unrelated_cargo(self):
        blob=(b'SiiNunit\n{\n cargo: "cargo.carga7"\n'
              b' cargo: "cargo.carga9"\n cargo: "cargo.beer"\n}\n')
        new=audit.disable_id(g,blob,"carga7")
        self.assertIn(b'cargo: ""',new)
        self.assertIn(b'cargo: "cargo.carga9"',new)
        self.assertIn(b'cargo: "cargo.beer"',new)
        self.assertNotIn(b'cargo.carga7',new)

if __name__=="__main__":unittest.main()
