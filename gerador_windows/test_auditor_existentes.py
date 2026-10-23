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

    def test_rbr_audit5_logging_and_fuel_cleanup_preserves_original(self):
        """AUDITORIA_RBR(5): extracao_ju move troncos, postos movem combustivel.
        Corrige SOMENTE fretes antigos incompatíveis no SCS novo.
        """
        map_zip=self.root/"rbr_audit5_company_originais.zip"
        zip_write(map_zip,{
            "extracao_ju/in/ponsse.sii":old("ponsse"),
            "extracao_ju/out/troncos.sii":old("troncos"),
            "extracao_sc/in/ponsse2.sii":old("ponsse2"),
            "extracao_sc/out/troncos_di.sii":old("troncos_di"),
            "go_p_riobra/in/gasolina.sii":old("gasolina"),
            "go_p_riobra/out/tanqvazio.sii":old("tanqvazio"),
            "faz_milho/in/fertilizante.sii":old("fertilizante"),
            "faz_milho/out/milho_a.sii":old("milho_a"),
            "silo_1/in/milho_a.sii":old("milho_a"),
        })
        existing=self.root/"rbr_audit5_existing.scs"
        zip_write(existing,{
            "def/company/extracao_ju/in/carga1.sii":g.cargo_sii("carga1"),
            "def/company/extracao_ju/in/carga2.sii":g.cargo_sii("carga2"),
            "def/company/extracao_ju/out/carga17.sii":g.cargo_sii("carga17"),
            "def/company/extracao_sc/out/carga20.sii":g.cargo_sii("carga20"),
            "def/company/go_p_riobra/in/carga6.sii":g.cargo_sii("carga6"),
            "def/company/go_p_riobra/in/carga13.sii":g.cargo_sii("carga13"),
            "def/company/faz_milho/out/carga1.sii":g.cargo_sii("carga1"),
            "def/company/silo_1/in/carga1.sii":g.cargo_sii("carga1"),
            "Original.txt":b"RBR_ANTES_INTACTO"
        })
        pristine=existing.read_bytes()
        out=self.root/"rbr_audit5_repaired"
        input_files={name:self.fixture.inp[name] for name in ("mod","def1","def2")}
        result=audit.run(
            g,{"RBR":{"existing":existing,"map_def":map_zip}},
            out,professional=True,source_files=input_files)[0]
        self.assertEqual(existing.read_bytes(),pristine)
        self.assertGreaterEqual(result["permissoes_removidas"],6)
        with zipfile.ZipFile(out/result["arquivo_corrigido"]) as patched:
            self.assertIsNone(patched.testzip())
            self.assertEqual(patched.read("Original.txt"),b"RBR_ANTES_INTACTO")
            for relative in (
                "extracao_ju/in/carga1.sii","extracao_ju/in/carga2.sii",
                "extracao_ju/out/carga17.sii","extracao_sc/out/carga20.sii",
                "go_p_riobra/in/carga6.sii","go_p_riobra/in/carga13.sii"):
                self.assertEqual(audit.file_active_ids(
                    g,patched.read("def/company/"+relative)),[])
            for relative in ("faz_milho/out/carga1.sii","silo_1/in/carga1.sii"):
                self.assertEqual(audit.file_active_ids(
                    g,patched.read("def/company/"+relative)),["carga1"])
        by_id={x["empresa"]:x for x in
               result["matriz_empresa_cidade"]["empresas"]}
        self.assertEqual(by_id["extracao_ju"]["atividade"],"madeireira")
        self.assertEqual(by_id["go_p_riobra"]["atividade"],"posto_combustivel")
        self.assertIn("carga1",result["rotas_depois"])

    def test_three_map_pending_queue_priority_and_original_inout(self):
        maps=[]
        for name in ("Minas_Gerais","Eldorado","RBR"):
            maps.append({
                "mapa":name,"total_cargas_catalogo":24,
                "pendencias_revisao":1,
                "permissoes_sem_evidencia_preservadas":1,
                "permissoes_plausiveis_sem_evidencia_def":1,
                "matriz_empresa_cidade":{"empresas":[
                    {"empresa":"unidade_confusa","atividade":"desconhecida",
                     "nome_exibido":"Empresa sem nome",
                     "in_originais_def":["fertilizer"],
                     "out_originais_def":["corn"],"instancias_editor":1},
                    {"empresa":"empresa_sem_cargas","atividade":"desconhecida",
                     "nome_exibido":"Unidade sem frete",
                     "in_originais_def":[],"out_originais_def":[],
                     "instancias_editor":0}
                ]},
                "decisoes":[
                    {"acao":"REVISAR","empresa":"unidade_confusa",
                     "carga":"carga1","direcao":"out",
                     "arquivo":"def/company/unidade_confusa/out/carga1.sii",
                     "setor":"desconhecida","motivo":"precisa confirmar"},
                    {"acao":"PRESERVAR_SEM_EVIDENCIA",
                     "empresa":"unidade_confusa","carga":"carga2",
                     "direcao":"out","motivo":"falta evidencia"},
                    {"acao":"MANTER_PLAUSIVEL","empresa":"unidade_confusa",
                     "carga":"carga23","direcao":"in",
                     "motivo":"possivel rotacao"},
                    {"acao":"ADICIONAR","empresa":"unidade_confusa",
                     "carga":"carga3","direcao":"in"}
                ],
                "qualidade_logistica":{
                    "cargas_com_par_cadastrado":24,
                    "cargas_com_par_economico_comprovavel":22,
                    "cargas_candidatas_teste_ets2":20},
                "cargas_sem_rota_validada":[]})
        target=self.root/"triagem_global"
        target.mkdir()
        report=audit._three_map_pending_queue(target,maps)
        self.assertEqual(report["prioridade_1_revisao"],3)
        self.assertEqual(report["prioridade_2_legada_sem_prova"],3)
        self.assertEqual(report["prioridade_3_hipotese"],3)
        self.assertEqual(report["prioridade_4_sem_frete"],3)
        self.assertFalse(report["homologado_no_ets2"])
        import csv
        with (target/"TRIAGEM_PENDENCIAS_3_MAPAS.csv").open(
                newline="",encoding="utf-8-sig") as fp:
            records=list(csv.DictReader(fp,delimiter=";"))
        self.assertEqual(len(records),12)
        self.assertEqual(records[0]["prioridade"],"1")
        self.assertIn("fertilizer",records[0]["in_originais_def"])
        self.assertIn("corn",records[0]["out_originais_def"])
        self.assertEqual(records[0]["homologado_ets2"],"NAO")
        self.assertEqual(records[-1]["acao"],
                         "SEM_FRETE_PENDENTE_IDENTIFICADO")
        self.assertIsNone(
            audit._three_map_pending_queue(target,maps[:2]))

    def test_scs_with_all_previous_chains_cannot_publish_broken_catalog(self):
        """Se entrada tinha todos os pares, nao silenciosamente perder
        carga após limpar posto sem alternativa economica verdadeira."""
        real_def=self.root/"mapa_sem_produtor_adequado.zip"
        zip_write(real_def,{
            "go_petrobras/in/gasolina.sii":old("gasolina"),
            "go_petrobras/out/tanqvazio.sii":old("tanqvazio"),
            "supermercado_centro/in/potatoes.sii":old("potatoes")
        })
        previous=self.root/"company_todas_rotas_herdadas.scs"
        archive={}
        for n in range(1,len(g.MANIFEST)+1):
            for company,direction in (
                    ("go_petrobras","out"),("supermercado_centro","in")):
                archive[
                    f"def/company/{company}/{direction}/carga{n}.sii"
                ]=g.cargo_sii(f"carga{n}")
        zip_write(previous,archive)
        original=previous.read_bytes()
        target=self.root/"blocked_catalog_regression"
        with self.assertRaisesRegex(ValueError,"PROTECAO DE CADEIAS"):
            audit.run(g,{"RBR":{"existing":previous,"map_def":real_def}},
                      target,professional=True,source_files={
                        k:self.fixture.inp[k] for k in ("mod","def1","def2")})
        self.assertEqual(previous.read_bytes(),original)
        self.assertEqual(list(target.glob("*.scs")),[])
        self.assertTrue((target/"AUDITORIA_INCOMPLETA.txt").exists())

    def test_rbr_real_sector_corrections_preserve_crop_rotation_as_hypothesis(self):
        """Auditoria binaria: remove fretes minerais/combustivel falsos e
        mantem sorghum em fazenda/silo SOMENTE quando herdado e plausivel."""
        map_def=self.root/"rbr_correcao_final_evidencias.zip"
        zip_write(map_def,{
            "faz_milho/in/fertilizante.sii":old("fertilizante"),
            "faz_milho/out/milho_a.sii":old("milho_a"),
            "acs_armazem/in/milho_a.sii":old("milho_a"),
            "acs_armazem/out/milho_a.sii":old("milho_a"),
            "mineracao1/out/brita.sii":old("brita"),
            "mineracao1/out/minerio.sii":old("minerio"),
            "go_petrobras/in/gasolina.sii":old("gasolina"),
            "go_petrobras/out/tanqvazio.sii":old("tanqvazio"),
            "extracao1/in/troncos.sii":old("troncos"),
            "extracao1/out/moveis.sii":old("moveis")
        })
        original=self.root/"rbr_company_herdada.scs"
        keep={
            "def/company/faz_milho/out/carga23.sii":g.cargo_sii("carga23"),
            "def/company/acs_armazem/in/carga23.sii":g.cargo_sii("carga23"),
            "def/company/mineracao1/out/carga2.sii":g.cargo_sii("carga2"),
            "def/company/go_petrobras/in/carga1.sii":g.cargo_sii("carga1"),
            "def/company/extracao1/out/carga8.sii":g.cargo_sii("carga8"),
            "note.txt":b"PRESERVAR"
        }
        zip_write(original,keep)
        backup=original.read_bytes()
        path=self.root/"rbr_qualidade_final"
        src=self.fixture.inp
        reports=audit.run(g,{"RBR":{"existing":original,"map_def":map_def}},
                          path,professional=True,source_files={
                              n:src[n] for n in ("mod","def1","def2")})
        self.assertEqual(original.read_bytes(),backup)
        result=reports[0]
        self.assertGreaterEqual(result["permissoes_plausiveis_sem_evidencia_def"],2)
        with (path/"MATRIZ_ENSAIOS_ETS2_RBR.csv").open(
                newline="",encoding="utf-8-sig") as fp:
            import csv
            rows=list(csv.DictReader(fp,delimiter=";"))
        self.assertEqual(len(rows),len(g.MANIFEST))
        self.assertIn("origem_real_testada",rows[0])
        self.assertIn("entrega_concluida",rows[0])
        self.assertTrue(all(row["entrega_concluida"]=="" for row in rows))
        self.assertTrue(all(row["frete_visivel_no_ets2"]=="" for row in rows))
        hyp=[d for d in result["decisoes"] if d["acao"]=="MANTER_PLAUSIVEL"]
        self.assertIn(("faz_milho","carga23"),
                      [(x["empresa"],x["carga"]) for x in hyp])
        self.assertIn(("acs_armazem","carga23"),
                      [(x["empresa"],x["carga"]) for x in hyp])
        with zipfile.ZipFile(path/result["arquivo_corrigido"]) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(z.read("note.txt"),b"PRESERVAR")
            for file in (
                "def/company/faz_milho/out/carga23.sii",
                "def/company/acs_armazem/in/carga23.sii"):
                self.assertIn("carga23",g.read_sii(z.read(file)))
            for file in (
                "def/company/mineracao1/out/carga2.sii",
                "def/company/go_petrobras/in/carga1.sii",
                "def/company/extracao1/out/carga8.sii"):
                self.assertEqual(audit.file_active_ids(g,z.read(file)),[])
        self.assertFalse(result["status"]=="AUDITORIA_ESTRUTURAL_CONCLUÍDA")


    def test_minas_eldorado_cotton_coconut_regional_scs_without_changing_rbr(self):
        """Excecao de pluma/coco gera cargas novas nos dois mapas mas
        RBR permanece byte a byte idêntico e nao é aberto."""
        from gerador import MANIFEST
        # O mod sintetico de base tem 23 cargas; adicionar a vigesima quarta
        # no mesmo formato do cargo_data, preservando as 23 primeiras.
        mod=self.fixture.inp["mod"]
        with zipfile.ZipFile(mod) as z:
            items={name:z.read(name) for name in z.namelist()}
        items["def/cargo/carga24.sui"]=(
            b"cargo_data : cargo.carga24 {\n body_types[]: alta\n}\n")
        zip_write(mod,items)
        txt=self.root/"cargas_regionais_24.txt"
        txt.write_text(
            "\n".join("carga"+str(n)+" = "+title
                      for n,(_cat,title) in MANIFEST.items())+
            "\ncarga24 = Coco\n",encoding="utf-8")
        map_base={
            "fazenda_milho/in/fertilizer.sii":old("fertilizer"),
            "fazenda_milho/out/corn.sii":old("corn"),
            "fazenda_batata/out/potatoes.sii":old("potatoes"),
            "silo_central/in/corn.sii":old("corn"),
            "cooperativa_vale/in/soybeans.sii":old("soybeans"),
            "martminas/in/potatoes.sii":old("potatoes"),
            "mercearia_jardim/in/beer.sii":old("beer"),
            "ceasa_centro/in/oranges.sii":old("oranges"),
            "construcao_01/in/bricks.sii":old("bricks"),
            "posto_combustivel/in/diesel.sii":old("diesel"),
        }
        defs={}
        companies={}
        for region in ("Minas_Gerais","Eldorado"):
            map_file=self.root/(region+"_regional_def.zip")
            zip_write(map_file,map_base)
            comp_file=self.root/(region+"_regional_company.scs")
            zip_write(comp_file,{
                "ReadMe.txt":b"ORIGINAL PRESERVADO",
                "def/company/construcao_01/in/carga5.sii":
                    g.cargo_sii("carga5"),
                "def/company/posto_combustivel/in/carga24.sii":
                    g.cargo_sii("carga24"),
            })
            defs[region]={"existing":comp_file,"map_def":map_file}
            companies[region]=comp_file.read_bytes()
        out=self.root/"saida_pluma_coco_so_minas_eldorado"
        out.mkdir()
        untouched_rbr=out/"ETS2_RBR_AUDITADA_ANTERIOR.scs"
        untouched_rbr.write_bytes(b"RBR_NAO_ALTERAR_NUNCA")
        inputs={k:self.fixture.inp[k] for k in ("mod","def1","def2")}
        inputs["txt"]=txt
        reports=audit.run(g,defs,out,professional=True,source_files=inputs)
        self.assertEqual({x["mapa"] for x in reports},{"Minas_Gerais","Eldorado"})
        self.assertEqual(untouched_rbr.read_bytes(),b"RBR_NAO_ALTERAR_NUNCA")
        self.assertFalse((out/"AUDITORIA_RBR.json").exists())
        for report in reports:
            with self.subTest(map=report["mapa"]):
                region=report["mapa"]
                self.assertEqual(defs[region]["existing"].read_bytes(),
                                 companies[region])
                self.assertGreater(report["permissoes_adaptacao_regional_adicionadas"],0)
                cotton=report["rotas_depois"]["carga5"]
                coconut=report["rotas_depois"]["carga24"]
                self.assertGreater(cotton["pares_distintos"],0)
                self.assertGreater(coconut["pares_distintos"],0)
                with zipfile.ZipFile(out/report["arquivo_corrigido"]) as z:
                    members=set(z.namelist())
                    self.assertIsNone(z.testzip())
                    for farm in ("fazenda_milho","fazenda_batata"):
                        for cargo in ("carga5","carga24"):
                            self.assertIn(
                                f"def/company/{farm}/out/audit_{cargo}.sii",members)
                    for dst in ("silo_central","cooperativa_vale"):
                        self.assertIn(
                            f"def/company/{dst}/in/audit_carga5.sii",members)
                        self.assertNotIn(
                            f"def/company/{dst}/in/audit_carga24.sii",members)
                    for dst in ("martminas","mercearia_jardim","ceasa_centro"):
                        self.assertIn(
                            f"def/company/{dst}/in/audit_carga24.sii",members)
                        self.assertNotIn(
                            f"def/company/{dst}/in/audit_carga5.sii",members)
                    for bad in ("construcao_01","posto_combustivel"):
                        for cargo in ("carga5","carga24"):
                            self.assertNotIn(
                                f"def/company/{bad}/in/audit_{cargo}.sii",members)
                            self.assertNotIn(
                                f"def/company/{bad}/out/audit_{cargo}.sii",members)
                    self.assertEqual(z.read("ReadMe.txt"),
                                     b"ORIGINAL PRESERVADO")
                    for bad_file in (
                            "def/company/construcao_01/in/carga5.sii",
                            "def/company/posto_combustivel/in/carga24.sii"):
                        self.assertIn(bad_file,members)
                        self.assertEqual(
                            audit.file_active_ids(g,z.read(bad_file)),[])
                self.assertGreaterEqual(report["permissoes_removidas"],2)
                quality=report["qualidade_logistica"]
                self.assertGreater(
                    quality["cargas"]["carga5"]["pares_simulacao_regional"],0)
                self.assertGreater(
                    quality["cargas"]["carga24"]["pares_simulacao_regional"],0)
                # Algumas CEASAs ja possuem comercio hortifruti como
                # ramo forte; nao exigir zero pares setoriais. O essencial
                # e que a nova producao na fazenda NAO seja tratada como
                # cultivo documentado no OUT da DEF original.
                self.assertEqual(
                    quality["cargas"]["carga24"]["pares_com_evidencia_inout_distintos"],0)
                self.assertFalse(
                    quality["cargas"]["carga24"]["homologado_no_ets2"])
                decisions=[d for d in report["decisoes"]
                           if d["acao"]=="ADICIONAR_ADAPTACAO_REGIONAL"]
                self.assertTrue(decisions)
                self.assertEqual(
                    {d["carga"] for d in decisions},{"carga5","carga24"})
                self.assertTrue(all(
                    d["fonte"]=="SIMULACAO_ECONOMICA_REGIONAL_AUTORIZADA"
                    for d in decisions))

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
