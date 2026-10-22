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

    def test_professional_anonymous_farm_flow_generates_real_scs_permissions(self):
        """A interpretacao IN/OUT tem de alterar o SCS, nao so o JSON."""
        mapa=self.root/"fluxo_mapa_rbr.zip"
        zip_write(mapa,{
            "unidade_anonima/in/fertilizer.sii":old("fertilizer"),
            "unidade_anonima/out/corn.sii":old("corn"),
            "unidade_anonima/out/soybeans.sii":old("soybeans"),
            "martminas/in/beer.sii":old("beer"),
            "martminas/in/potatoes.sii":old("potatoes"),
            "ambev/out/beer.sii":old("beer"),
        })
        entrada=self.root/"Company_rbr_sem_permissoes.scs"
        zip_write(entrada,{"ReadMe.txt":b"ORIGINAL INTACTO"})
        origem=entrada.read_bytes()
        out=self.root/"fluxo_saida"
        files=self.fixture.inp
        reports=audit.run(g,{"RBR":{"existing":entrada,"map_def":mapa}},out,
                          professional=True,source_files={
                              key:files[key] for key in ("mod","def1","def2")})
        self.assertEqual(len(reports),1)
        self.assertEqual(entrada.read_bytes(),origem)
        with zipfile.ZipFile(out/reports[0]["arquivo_corrigido"]) as scs:
            self.assertIsNone(scs.testzip())
            for n in (1,2,21,22):
                self.assertIn(
                    f"def/company/unidade_anonima/out/audit_carga{n}.sii",
                    scs.namelist())
            self.assertIn("def/company/unidade_anonima/in/audit_carga3.sii",
                          scs.namelist())
            for n in (7,8,12):
                self.assertIn(f"def/company/martminas/in/audit_carga{n}.sii",
                              scs.namelist())
            self.assertNotIn("def/company/unidade_anonima/out/audit_carga23.sii",
                             scs.namelist())
            self.assertNotIn("def/company/martminas/out/audit_carga12.sii",
                             scs.namelist())
            self.assertEqual(scs.read("ReadMe.txt"),b"ORIGINAL INTACTO")
        self.assertEqual(reports[0]["cobertura_maxima_empresas"][
            "empresas_reconhecidas_com_lacunas"],0)

    def test_unnamed_fictional_industries_generate_real_in_out_in_scs(self):
        """Sem marcas reais: empresas ficticias sao analisadas por fluxo."""
        original=self.root/"mapa_ficticio_original.scs"
        zip_write(original,{
            "company_z_feed/in/corn.sii":old("corn"),
            "company_z_feed/out/animal_feed.sii":old("animal_feed"),
            "company_z_store/in/cement.sii":old("cement"),
            "company_z_store/in/bricks.sii":old("bricks"),
            "company_z_store/out/cement.sii":old("cement"),
            "company_z_store/out/bricks.sii":old("bricks"),
            "company_z_build/in/cement.sii":old("cement"),
            "company_z_build/in/bricks.sii":old("bricks"),
        })
        existing=self.root/"company_ficticia_existente.scs"
        zip_write(existing,{"Info.txt":b"EMPRESAS FICTICIAS INTACTAS"})
        src=self.fixture.inp
        dest=self.root/"saida_empresas_ficticias"
        output=audit.run(
            g,{"RBR":{"existing":existing,"map_def":original}},dest,
            professional=True,source_files={key:src[key] for key in ("mod","def1","def2")})
        self.assertEqual(output[0]["arquivos_modificados"],0)
        with zipfile.ZipFile(dest/output[0]["arquivo_corrigido"]) as final:
            names=set(final.namelist())
            self.assertIsNone(final.testzip())
            for id in (1,22):
                self.assertIn(f"def/company/company_z_feed/in/audit_carga{id}.sii",names)
            for id in (17,18,19,20):
                self.assertIn(f"def/company/company_z_feed/out/audit_carga{id}.sii",names)
            for id in (6,10,11,13):
                self.assertIn(f"def/company/company_z_store/in/audit_carga{id}.sii",names)
                self.assertIn(f"def/company/company_z_store/out/audit_carga{id}.sii",names)
                self.assertIn(f"def/company/company_z_build/in/audit_carga{id}.sii",names)
                self.assertNotIn(f"def/company/company_z_build/out/audit_carga{id}.sii",names)
            self.assertNotIn("def/company/company_z_feed/in/audit_carga23.sii",names)
            self.assertNotIn("def/company/company_z_store/out/audit_carga4.sii",names)
            self.assertEqual(final.read("Info.txt"),b"EMPRESAS FICTICIAS INTACTAS")
        import json
        audit_data=json.loads(
            (dest/"AUDITORIA_RBR.json").read_text(encoding="utf-8"))
        matrix={x["empresa"]:x for x in audit_data["matriz_empresa_cidade"]["empresas"]}
        self.assertEqual(set(matrix),{"company_z_feed","company_z_store","company_z_build"})
        self.assertEqual(matrix["company_z_feed"]["atividade"],"fabrica_racao_inferida")
        self.assertEqual(matrix["company_z_store"]["atividade"],"comercio_materiais_inferido")
        self.assertEqual(matrix["company_z_build"]["atividade"],"consumidor_materiais_inferido")
        self.assertIn("corn",matrix["company_z_feed"]["in_originais_def"])
        self.assertIn("bricks",matrix["company_z_build"]["in_originais_def"])


    def test_fictional_unnamed_company_preserves_exact_original_cargo_directions(self):
        """Prova em SCS: IN de milho e OUT de cimento, sem descobrir o ramo."""
        def_map=self.root/"def_ficcional_misto.zip"
        zip_write(def_map,{
            "z_company_917/in/corn.sii":old("corn"),
            "z_company_917/out/cement.sii":old("cement"),
        })
        existing=self.root/"company_neutra.zip"
        zip_write(existing,{"original.txt":b"permanecer intacto"})
        dest=self.root/"audit_z_company"
        source={key:self.fixture.inp[key] for key in ("mod","def1","def2")}
        reports=audit.run(
            g,{"Minas_Gerais":{"existing":existing,"map_def":def_map}},dest,
            professional=True,source_files=source)
        self.assertEqual(len(reports),1)
        with zipfile.ZipFile(dest/reports[0]["arquivo_corrigido"]) as z:
            filenames=set(z.namelist())
            self.assertIsNone(z.testzip())
            for n in (1,22):
                self.assertIn(f"def/company/z_company_917/in/audit_carga{n}.sii",
                              filenames)
                self.assertNotIn(f"def/company/z_company_917/out/audit_carga{n}.sii",
                                 filenames)
            for n in (6,10,11):
                self.assertIn(f"def/company/z_company_917/out/audit_carga{n}.sii",
                              filenames)
                self.assertNotIn(f"def/company/z_company_917/in/audit_carga{n}.sii",
                                 filenames)
            self.assertNotIn("def/company/z_company_917/out/audit_carga2.sii",
                             filenames)
            self.assertEqual(z.read("original.txt"),b"permanecer intacto")
        row=reports[0]["matriz_empresa_cidade"]["empresas"][0]
        self.assertEqual(row["atividade"],"desconhecida")
        self.assertEqual(row["in_originais_def"],["corn"])
        self.assertEqual(row["out_originais_def"],["cement"])
        self.assertNotEqual(reports[0]["status"],"AUDITORIA_ESTRUTURAL_CONCLUÍDA")


    def test_three_map_dashboard_never_uses_documentary_100_as_game_100(self):
        items=[]
        for map_name in ("Minas_Gerais","Eldorado","RBR"):
            items.append({
                "mapa":map_name,"empresas_na_def":7,
                "total_cargas_catalogo":24,"pendencias_revisao":0,
                "cobertura_maxima_empresas":{
                    "empresas_sem_classificacao":1,
                    "empresas_sem_editor":1,
                    "empresas_compativeis_sem_editor_valido":1,
                    "cidades_identificadas":0,
                    "permissoes_justificadas":24,
                    "permissoes_justificadas_atendidas":24,
                    "cobertura_permissoes_justificadas_pct":100.0},
                "qualidade_logistica":{
                    "cargas_com_par_cadastrado":24,
                    "cargas_com_par_evidencia_inout":24,
                    "cargas_com_par_economico_comprovavel":23,
                    "cargas_candidatas_documentais_teste":0,
                    "cargas_candidatas_teste_ets2":0,
                    "cargas":{"carga"+str(i):{
                        "pares_economicos_distintos":1 if i<24 else 0,
                        "pares_com_evidencia_inout_distintos":1,
                        "pares_com_editor_em_ambas_empresas":0
                        } for i in range(1,25)}}})
        path=self.root/"dashboard_only"
        summary=audit._write_three_map_dashboard(path,items,simulated=True)
        self.assertEqual(summary["mapas_analisados"],3)
        self.assertTrue(summary["simulacao_sem_escrita_scs"])
        self.assertFalse(summary["homologado_no_ets2"])
        self.assertEqual(len(summary["mapas"]),3)
        for report in summary["mapas"]:
            self.assertEqual(report["pct_permissoes_justificadas"],100.0)
            self.assertEqual(report["cargas_com_par_documental"],24)
            self.assertEqual(report["cargas_com_par_economico"],23)
            self.assertIn("carga24",report["cargas_sem_par_economico"])
            self.assertEqual(report["status"],"ANALISE_PENDENTE")
            self.assertFalse(report["homologado_no_ets2"])
        self.assertTrue((path/"PAINEL_GERAL_LOGISTICA_V3.json").exists())
        txt=(path/"PAINEL_GERAL_LOGISTICA_V3.txt").read_text(
            encoding="utf-8")
        self.assertIn("24/24 cargas",txt)
        self.assertIn("23/24 cargas",txt)
        self.assertIn("SIMULACAO",txt)

    def test_real_eldorado_pallet_in_out_closes_missing_receiver(self):
        """Reproduz palete: madereira OUT, spani IN, kaarfor2 OUT.

        A DEF original contem 'empty_palet'; nao pode ser descartada
        por diferenca de grafia com palete do Librelato.
        """
        map_file=self.root/"def_eldorado_palete_real.zip"
        zip_write(map_file,{
            "madereira/out/empty_palet.sii":old("empty_palet"),
            "madereira/in/empty_palet.sii":old("empty_palet"),
            "spani/in/empty_palet.sii":old("empty_palet"),
            "spani/out/empty_palet.sii":old("empty_palet"),
            "kaarfor2/out/empty_palet.sii":old("empty_palet"),
            "kaarfor2/in/potatoes.sii":old("potatoes"),
            "brasilog/out/empty_palet.sii":old("empty_palet"),
        })
        original=self.root/"company_palete_original.scs"
        zip_write(original,{"Info.txt":b"KEEP ORIGINAL"})
        dest=self.root/"eldorado_palete_corrigido"
        fixture=self.fixture.inp
        reports=audit.run(
            g,{"Eldorado":{"existing":original,"map_def":map_file}},
            dest,professional=True,
            source_files={key:fixture[key] for key in ("mod","def1","def2")})
        self.assertEqual(len(reports),1)
        after=reports[0]["rotas_depois"]["carga16"]
        self.assertGreaterEqual(after["origens"],2)
        self.assertGreaterEqual(after["destinos"],1)
        self.assertGreaterEqual(after["pares_distintos"],1)
        with zipfile.ZipFile(dest/reports[0]["arquivo_corrigido"]) as z:
            names=set(z.namelist())
            self.assertIn("def/company/spani/in/audit_carga16.sii",names)
            self.assertIn("def/company/madereira/out/audit_carga16.sii",names)
            self.assertIn("def/company/kaarfor2/out/audit_carga16.sii",names)
            self.assertNotIn("def/company/kaarfor2/in/audit_carga16.sii",
                             names)
            self.assertNotIn("def/company/brasilog/out/audit_carga16.sii",
                             names)
            self.assertEqual(z.read("Info.txt"),b"KEEP ORIGINAL")
        self.assertGreater(original.stat().st_size,0)

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

    def test_three_maps_write_independent_comprehensive_company_coverage(self):
        out=self.root/"tres_coberturas"
        files=self.fixture.inp
        cases={
            map_name:{"existing":self.existing,"map_def":self.baseline}
            for map_name in ("Minas_Gerais","Eldorado","RBR")
        }
        original=self.existing.read_bytes()
        report=audit.run(g,cases,out,mode="auditar",professional=True,
                         source_files={k:files[k] for k in ("mod","def1","def2")})
        self.assertEqual(len(report),3)
        self.assertEqual(self.existing.read_bytes(),original)
        self.assertFalse(list(out.glob("*.scs")))
        for r in report:
            map_name=r["mapa"]
            prefix=map_name.upper()
            summary=r["cobertura_maxima_empresas"]
            self.assertEqual(summary["total_empresas_def"],11)
            self.assertEqual(summary["empresas_reconhecidas_com_lacunas"],
                             len(r["empresas_compativeis_esquecidas"]))
            self.assertFalse(summary["cobertura_100_por_cento_comprovada"])
            path=out/("COBERTURA_MAXIMA_"+prefix+".json")
            self.assertTrue(path.exists(),str(path))
            full=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(full["total_empresas_def"],11)
            self.assertEqual(len(full["empresas"]),11)
            self.assertTrue((out/("COBERTURA_MAXIMA_"+prefix+".csv")).exists())
            self.assertTrue((out/(prefix+"_REVISAO_ECONOMICA_PRIORIZADA.csv")).exists())
            self.assertTrue((out/("COBERTURA_CIDADES_"+prefix+".csv")).exists())
            self.assertTrue((out/("COBERTURA_CIDADES_"+prefix+".json")).exists())
            self.assertEqual(full["cargas_candidatas_teste"],
                             r["qualidade_logistica"]["cargas_candidatas_teste_ets2"])

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
