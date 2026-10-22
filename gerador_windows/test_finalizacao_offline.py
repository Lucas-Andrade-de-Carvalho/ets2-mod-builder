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


    def test_missing_economic_evidence_blocks_all_three_real_scs(self):
        """Sem 24 fornecedores e compradores validos, ZERO SCS publicados."""
        self.add_coco_to_real_sources()
        root=self.root/"no_fiction"
        before={k:g.hash_source(v) for k,v in self.src.items()}
        before.update({"scs":g.hash_source(self.case.existing),
                       "map":g.hash_source(self.case.baseline)})
        report=finish.run(g,self.src,self.maps,root)
        self.assertEqual(report["status"],"BLOQUEADO_ECONOMIA_REAL")
        self.assertEqual(len(report["arquivos_corrigidos"]),0)
        self.assertEqual(set(report["mapas_reauditados"]),set(finish.MAPS))
        self.assertEqual(report["reescritas_residuais"],0)
        self.assertTrue(report["originais_preservados"])
        self.assertFalse(report["homologado_no_ets2"])
        self.assertTrue(report["nenhum_scs_publicado"])
        self.assertTrue(report["motivos"])
        self.assertFalse((root/"02_CANDIDATAS_PARA_JOGO").exists())
        self.assertFalse(list(root.rglob("*.scs")))
        self.assertEqual({k:g.hash_source(v) for k,v in self.src.items()},
                         {k:before[k] for k in self.src})
        self.assertEqual(before["scs"],g.hash_source(self.case.existing))
        self.assertEqual(before["map"],g.hash_source(self.case.baseline))
        self.assertEqual(json.loads((root/"RESULTADO_FINALIZACAO_OFFLINE.json")
                        .read_text(encoding="utf-8"))["status"],
                        "BLOQUEADO_ECONOMIA_REAL")

    def test_complete_24x3_fixture_publishes_and_never_overwrites(self):
        """Teste do portao positivo SEM fingir que os tres mapas sao reais."""
        from unittest.mock import patch
        self.add_coco_to_real_sources()
        root=self.root/"valid_mock"
        synthetic24={
            "cargas":{"carga"+str(n):{"status":"CANDIDATA_TESTE_ETS2"}
                      for n in range(1,25)},
            "cargas_com_par_economico_comprovavel":24,
            "cargas_candidatas_teste_ets2":24
        }
        pre_result={"status_pre_homologacao":"PRONTO_PARA_TESTES_NO_JOGO",
                    "ensaios_de_jogo_planejados":72,"bloqueios":[]}
        calls=[]
        def audited(gmod,map_entries,out_path,mode,log,professional,source_files):
            names=tuple(sorted(map_entries))
            self.assertEqual(names,tuple(sorted(finish.MAPS)))
            self.assertTrue(professional)
            calls.append(mode)
            out_path=Path(out_path)
            out_path.mkdir(parents=True,exist_ok=True)
            results=[]
            for name in names:
                item={
                    "mapa":name,
                    "rotas_depois":{"carga1":{"pares_distintos":1}},
                    "arquivos_adicionados":0,
                    "arquivos_modificados":0,
                    "permissoes_removidas":0,
                    "pendencias_revisao":0,
                    "empresas_classificacao_pendente":0,
                    "cargas_sem_rota_validada":[],
                    "status":"AUDITORIA_ESTRUTURAL_CONCLUÍDA",
                    "qualidade_logistica":synthetic24,
                }
                if mode=="corrigir":
                    item["arquivo_corrigido"]=name+".scs"
                    with zipfile.ZipFile(out_path/(name+".scs"),"w") as z:
                        z.writestr("def/company/test/in/carga1.sii",
                                   b'cargo: "cargo.carga1"')
                results.append(item)
            return results
        with patch.object(finish.preflight,"run",return_value=pre_result),\
             patch.object(finish.audit,"run",side_effect=audited):
            report=finish.run(g,self.src,self.maps,root)
            self.assertEqual(report["status"],"PRONTO_PARA_TESTE_NO_ETS2")
            self.assertEqual(len(report["arquivos_corrigidos"]),3)
            self.assertFalse(report["homologado_no_ets2"])
            self.assertFalse(report["nenhum_scs_publicado"])
            for file in report["arquivos_corrigidos"]:
                archive=root/"02_CANDIDATAS_PARA_JOGO"/file["arquivo"]
                self.assertTrue(archive.is_file())
                self.assertEqual(g.hash_source(archive),file["sha256"])
            with self.assertRaises(FileExistsError):
                finish.run(g,self.src,self.maps,root)
        self.assertEqual(calls,["corrigir","auditar"])

    def test_missing_map_never_produces_any_new_scs(self):
        self.add_coco_to_real_sources()
        maps={key:value for key,value in self.maps.items() if key!="RBR"}
        out=self.root/"incomplete"
        with self.assertRaises(ValueError):
            finish.run(g,self.src,maps,out)
        self.assertFalse(list(out.rglob("*.scs")))
        failure=out/"FALHA_FINALIZACAO_OFFLINE.json"
        self.assertTrue(failure.is_file())
        self.assertEqual(json.loads(failure.read_text(encoding="utf-8"))[
            "status"],"INTERROMPIDO")


if __name__=="__main__":
    unittest.main()
