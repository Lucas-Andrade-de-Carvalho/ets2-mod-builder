"""Testes do novo contrato: mercadoria somente MOD/DEF+TXT; sem formulario."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from test_gerador import Regression, zip_write, old, g
import catalogo_fontes as fontes
import auditor_existentes as audit


class SourceCargoTests(unittest.TestCase):
    def setUp(self):
        self.fix=Regression()
        self.fix.setUp()
        self.root=self.fix.root
        self.raw=b'cargo_data : cargo.carga24 {\n name: "Coco"\n body_types[]: alta\n valuable: false\n}\n'
        p=self.fix.inp["mod"]
        with zipfile.ZipFile(p) as z:
            data={k:z.read(k) for k in z.namelist()}
        data["def/cargo/carga24.sui"]=self.raw
        zip_write(p,data)
        self.txt=self.root/"cargas24.txt"
        self.txt.write_text(
            "\n".join("carga"+str(n)+" = "+title for n,(_,title) in g.MANIFEST.items())+
            "\ncarga24 = Coco\n",encoding="utf-8")
        self.sources=[(k,g.zip_members(self.fix.inp[k])) for k in ("mod","def1","def2")]
        self.records=g.cargo_inventory(self.sources)[0]
    def tearDown(self):
        self.fix.tearDown()
    def test_new_cargo_comes_from_real_definition_not_catalog(self):
        manifest,extras=fontes.from_originals(g.MANIFEST,self.records,self.txt)
        self.assertEqual(len(manifest),24)
        self.assertEqual(manifest["carga24"],("coco","Coco"))
        self.assertEqual(extras["carga24"]["body_types"],["alta"])
        self.assertEqual(self.records["carga24"]["raw"],self.raw)
    def test_user_24_cargo_txt_labels_and_categories(self):
        # A descricao tem prioridade para exibir o nome, sem recategorizar
        # racao mineral laranja como fruta ou cimento e pallet como palete.
        text=self.root/"cargas_usuario.txt"
        names={
            1:"Carga de Milho",2:"Carga de Soja",3:"Carga adubo",
            4:"Carga Madeira",5:"Carga Pluma de algodão",6:"Carga de Cimento",
            7:"Sacos de Batata",8:"Sacos de Laranja",9:"Bobinas 2",
            10:"Cimento e Pallet",11:"Cimento e Cinta",12:"cerveja",
            13:"Tijolos",14:"Pedra Granitto 1",15:"Pedra Granitto 2",
            16:"palete alto",17:"Ração Mineral Laranja",18:"Xerém (Ração)",
            19:"sacaria ração",20:"sacaria de ração 2",21:"Soja alto",
            22:"milho alto",23:"Sorgo alto (alimento para gado)",24:"Coco"}
        text.write_text("\n".join(
            f"carga{i} = {label}" for i,label in names.items())+"\n",encoding="utf-8")
        manifest,extra=fontes.from_originals(g.MANIFEST,self.records,text)
        self.assertEqual(len(manifest),24)
        self.assertEqual(len(extra),1)
        self.assertEqual(manifest[17],("racao","Ração Mineral Laranja"))
        self.assertEqual(manifest[10],("cimento","Cimento e Pallet"))
        self.assertEqual(manifest[16],("palete","palete alto"))
        self.assertEqual(manifest[24] if 24 in manifest else manifest["carga24"],
                         ("coco","Coco"))
        self.assertEqual(manifest[5][1],"Carga Pluma de algodão")

    def test_txt_missing_original_blocks_audit_silently_wrong_catalog(self):
        text=self.root/"incomplete.txt"
        text.write_text("carga24 = Coco\n",encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"TXT nao identifica carga original"):
            fontes.from_originals(g.MANIFEST,self.records,text)

    def test_cargo24_without_txt_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"TXT"):
            fontes.from_originals(g.MANIFEST,self.records,None)
    def test_txt_without_cargo_data_fails_closed(self):
        rec=dict(self.records);rec.pop("carga24")
        with self.assertRaisesRegex(ValueError,"cargo_data"):
            fontes.from_originals(g.MANIFEST,rec,self.txt)
    def test_coco_is_not_invented_from_oil_or_processed_derivative(self):
        self.assertEqual(fontes.known_economic_category("Coco"),"coco")
        self.assertEqual(fontes.known_economic_category("Coco verde"),"coco")
        self.assertEqual(fontes.known_economic_category("Oleo de coco"),"nao_classificada")
        self.assertEqual(fontes.known_economic_category("Leite de coco"),"nao_classificada")

    def test_coco_policy_requires_documentary_production(self):
        import politica_economica as policy
        spec={"id":"carga24","nome":"Coco","categoria":"coco",
              "body_types":["alta"]}
        farm=g.Company("fazenda_coco",old_out={"coconuts"})
        farm_without_proof=g.Company("fazenda_coco")
        store=g.Company("supermercado_centro")
        self.assertTrue(fontes.evaluate(farm,spec,"out",policy.classify(farm)).allowed)
        self.assertFalse(fontes.evaluate(farm_without_proof,spec,"out",
                                         policy.classify(farm_without_proof)).allowed)
        self.assertTrue(fontes.evaluate(store,spec,"in",policy.classify(store)).allowed)
        self.assertFalse(fontes.evaluate(store,spec,"out",policy.classify(store)).allowed)

    def test_24_25_and_others_scanned_without_code_changes(self):
        r=dict(self.records)
        raw=b'cargo_data : cargo.carga25 {\n body_types[]: baixa\n}\n'
        r["carga25"]={"raw":raw,"body":{"baixa"},"source":"DEF1",
                      "path":"def/cargo/carga25.sui"}
        path=self.root/"cargas25.txt"
        path.write_text(self.txt.read_text()+"carga25: Produto novo\n",encoding="utf-8")
        manifest,extras=fontes.from_originals(g.MANIFEST,r,path)
        self.assertEqual(len(manifest),25)
        self.assertEqual(set(extras),{"carga24","carga25"})
    def test_cargo_ids_of_other_trailers_not_autoregistered(self):
        r=dict(self.records)
        r["corn_b"]={"body":{"hopper"},"raw":b"x","source":"MOD","path":"x"}
        manifest,extras=fontes.from_originals(g.MANIFEST,r,self.txt)
        self.assertEqual(len(manifest),24)
        self.assertNotIn("corn_b",extras)
    def test_generator_detects_24_without_external_json_and_fails_unjustified(self):
        inp={**self.fix.inp,"txt":self.txt}
        out=self.root/"new_output"
        with self.assertRaisesRegex(ValueError,"cobertura insuficiente"):
            g.generate(inp,out,professional=True)
        self.assertFalse(list(out.glob("*.scs")))
        assert list(out.glob("*_COBERTURA_CARGAS.json"))
    def test_audit_preserves_24_and_flags_no_economic_policy(self):
        company=self.root/"Company24.scs"
        baseline=self.fix.inp["maps"]["Minas_Gerais"]
        zip_write(company,{
            "def/company/supermercado1/in/carga24.sii":g.cargo_sii("carga24"),
            "def/company/fazenda_a/out/carga24.sii":g.cargo_sii("carga24")})
        old_hash=g.hash_source(company)
        out=self.root/"audit_new"
        data=audit.run(g,{"Minas_Gerais":{"existing":company,"map_def":baseline}},
                       out,mode="corrigir",professional=True,
                       source_files={"mod":self.fix.inp["mod"],
                                     "def1":self.fix.inp["def1"],
                                     "def2":self.fix.inp["def2"],
                                     "txt":self.txt})[0]
        self.assertEqual(g.hash_source(company),old_hash)
        self.assertEqual(data["total_cargas_catalogo"],24)
        actions=[d for d in data["decisoes"] if d.get("carga")=="carga24"]
        self.assertTrue(actions)
        self.assertFalse(any(d["acao"]=="REMOVER" for d in actions))
        # Nova excecao REGIONAL foi explicitamente autorizada para Minas:
        # fazenda pode expedir coco e supermercado pode receber. Essa
        # associacao NAO vira documentacao de cultivo no IN/OUT original.
        self.assertTrue(any(
            d["acao"]=="MANTER_ADAPTACAO_REGIONAL" for d in actions))
        self.assertGreaterEqual(data["permissoes_adaptacao_regional_herdadas"],2)
        self.assertTrue(all(
            d.get("fonte")=="SIMULACAO_ECONOMICA_REGIONAL_AUTORIZADA"
            for d in actions if d["acao"]=="MANTER_ADAPTACAO_REGIONAL"))
        with zipfile.ZipFile(out/data["arquivo_corrigido"]) as z:
            self.assertEqual(z.read("def/company/supermercado1/in/carga24.sii"),
                             g.cargo_sii("carga24"))
    def test_no_manual_editor_or_mutable_catalog_imported(self):
        import inspect
        source=inspect.getsource(g.run_gui)
        self.assertNotIn("GERENCIAMENTO DE CARGAS",source)
        self.assertNotIn("gerenciamento_gui",source)


if __name__=="__main__":
    unittest.main()
