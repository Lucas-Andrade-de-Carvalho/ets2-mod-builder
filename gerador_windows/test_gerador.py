import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ets2_generator",ROOT/"gerador.py")
g=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=g
spec.loader.exec_module(g)

def zip_write(path,files):
    with zipfile.ZipFile(path,"w") as z:
        for k,v in files.items():z.writestr(k,v)

def old(id):
    return f'SiiNunit\n{{\n cargo_def : .old {{\n  cargo: "cargo.{id}"\n }}\n}}\n'

class Regression(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        mods={}
        for n in g.MANIFEST:
            body="baixa" if n in (9,10,11,14,15,13) else "alta"
            mods[f"def/cargo/carga{n}.sui"]=(
                f'cargo_data : cargo.carga{n} {{\n name: "Cargo {n}"\n'
                f' body_types[]: {body}\n valuable: true\n}}\n')
            mods[f"def/cargo/carga{n}/rodotrem.sii"]=(
                f'SiiNunit\n{{\n trailer_def : .a {{\n body_type: {body}\n'
                ' chain_type: hct\n length: 22\n }}\n}\n')
        mods["def/vehicle/trailer_owned/test/body/grade.sii"]="body_type: alta\n"
        mods["def/vehicle/trailer_owned/test/body/baix.sii"]="body_type: baixa\n"
        zip_write(self.root/"rodotrem.scs",mods)
        zip_write(self.root/"def1.scs",{"def/company/fazenda_a/in/milho_b.sii":old("milho_b")})
        zip_write(self.root/"def2.scs",{"def/company/ambev/out/bebidas.sii":old("bebidas")})
        self.company_raw={
           "fazenda_a":{"in":["adubo","racao"],"out":["milho_a","soja_a"]},
           "agrish":{"in":["milho_b"],"out":["adubo","fertilizante"]},
           "silo_armazen":{"in":["milho_a","soja_a"],"out":["milho_a","soja_a"]},
           "ambev":{"in":["vasilhame"],"out":["bebidas","brahma"]},
           "supermercado1":{"in":["bebidas","batata_a","laranja_a"],"out":["paletev"]},
           "serraria_a":{"in":["troncos"],"out":["madeirase"]},
           "sucatao_a":{"in":["paletev"],"out":["sucata"]},
           "construcao_1":{"in":["cimento","tijolo_b","bobina"],"out":["sucata"]},
           "loja_material":{"in":["cimento","tijolo_b"],"out":["cimento","tijolo_b"]},
           "quarry_pedreira":{"in":["oleo"],"out":["brita","granito"]},
           "fabrica_racao":{"in":["milho_a","soja_a"],"out":["racao"]},
           "pecuaria_gado":{"in":["racao","milho_b"],"out":["gado"]},
        }
        files={}
        for co,dirs in self.company_raw.items():
            for direction,ids in dirs.items():
                for token in ids:
                    files[f"def/company/{co}/{direction}/{token}.sii"]=old(token)
        files["def/company/agrish/editor/test.sii"]="SiiNunit\n{}\n"
        for name in ("minas","eldorado","rbr"):
            zip_write(self.root/f"{name}.zip",files)
        self.inp={"mod":self.root/"rodotrem.scs","def1":self.root/"def1.scs",
                  "def2":self.root/"def2.scs",
                  "maps":{"Minas_Gerais":self.root/"minas.zip",
                          "Eldorado":self.root/"eldorado.zip","RBR":self.root/"rbr.zip"}}
    def tearDown(self):
        self.tmp.cleanup()
    def test_generate_3_maps_and_roles(self):
        result=g.generate(self.inp,self.root/"out")
        self.assertEqual(len(result),3)
        for name,scs,data in result:
            with zipfile.ZipFile(scs) as z:
                self.assertIsNone(z.testzip())
                self.assertIn("cargo.carga3",z.read("def/company/agrish/out/carga3.sii").decode())
                self.assertIn("cargo.carga3",z.read("def/company/fazenda_a/in/carga3.sii").decode())
                self.assertIn("cargo.carga12",z.read("def/company/ambev/out/carga12.sii").decode())
                self.assertIn("cargo.carga12",z.read("def/company/supermercado1/in/carga12.sii").decode())
                self.assertIn("cargo.carga16",z.read("def/company/serraria_a/out/carga16.sii").decode())
                self.assertIn("cargo.carga16",z.read("def/company/sucatao_a/in/carga16.sii").decode())
                self.assertNotIn("def/company/sucatao_a/out/carga16.sii",z.namelist())
                self.assertNotIn("def/company/serraria_a/in/carga16.sii",z.namelist())
                self.assertIn('cargo: ""',z.read("def/company/ambev/out/bebidas.sii").decode())
                self.assertIn("valuable: false",z.read("def/cargo/carga12.sui").decode())
                self.assertIn("prob_coef: 0.08",z.read("def/cargo/carga16.sui").decode())
            self.assertEqual(data["total_empresas"],len(self.company_raw))
            self.assertGreater(data["arquivos_inout_gerados"],0)
            self.assertTrue((self.root/"out"/(name+"_empresas.csv")).exists())
            self.assertFalse(data["cadeias"]["carga16"]["origens_lista"]==[])
    def test_fails_safely_if_trailer_body_mismatch(self):
        src=self.root/"rodotrem.scs"
        with zipfile.ZipFile(src) as z:
            contents={x.filename:z.read(x) for x in z.infolist()}
        # Incompatibilidade verdadeira: carroceria de carga1 deixou de existir
        # em todos os trailer_owned/body e trailer_defs compatíveis.
        contents["def/cargo/carga1.sui"]=(
            'cargo_data : cargo.carga1 {\n name: "Milho"\n'
            ' body_types[]: tanque_inexistente\n valuable: true\n}\n')
        zip_write(src,contents)
        with self.assertRaisesRegex(ValueError,"carga1"):
            g.generate(self.inp,self.root/"invalid")
        self.assertFalse((self.root/"invalid"/"ETS2_MINAS_GERAIS_COMPANY.scs").exists())

    def test_global_trailer_defs_without_legacy_folders(self):
        """Reboque proprio (ETS2 1.32+) usa def/vehicle/trailer_defs."""
        src=self.root/"rodotrem.scs"
        with zipfile.ZipFile(src) as z:
            content={x.filename:z.read(x) for x in z.infolist()
                     if not x.filename.startswith("def/cargo/") or "/" not in x.filename[len("def/cargo/"):]}
        content["def/vehicle/trailer_defs/limeira_alta.sii"]=(
            "SiiNunit\n{\n trailer_def : .alta {\n body_type: alta\n"
            " chain_type: hct\n }\n}\n")
        content["def/vehicle/trailer_defs/limeira_baixa.sii"]=(
            "SiiNunit\n{\n trailer_def : .baixa {\n body_type: baixa\n"
            " chain_type: hct\n }\n}\n")
        zip_write(src,content)
        records,legacy,owned,global_defs,counts=g.cargo_inventory([
            ("MOD",g.zip_members(src))])
        self.assertEqual(len(records),23)
        self.assertFalse(any(legacy.values()))
        self.assertEqual(global_defs,{"alta","baixa"})
        self.assertEqual(counts["owned_trailer_def_files"],2)
        # O gerador NAO deve bloquear ausencia da estrutura antiga.
        result=g.generate(self.inp,self.root/"new_layout")
        self.assertEqual(len(result),3)

    def test_owned_trailer_without_legacy_or_global_defs(self):
        """Cargo e reboque proprio compatíveis nao exigem trailer_def por carga."""
        src=self.root/"rodotrem.scs"
        with zipfile.ZipFile(src) as z:
            content={x.filename:z.read(x) for x in z.infolist()
                     if not x.filename.startswith("def/cargo/carga") or
                     x.filename.endswith(".sui")}
        zip_write(src,content)
        result=g.generate(self.inp,self.root/"owned_only")
        self.assertEqual(len(result),3)

    def test_failed_eldorado_has_diagnostic_and_no_partial_scs(self):
        """Um ZIP desconhecido bloqueia os tres mapas e deixa evidencias uteis."""
        bad=self.root/"eldorado.zip"
        zip_write(bad,{
          "eldorado/def/companies/fazenda.sii":"SiiNunit\n{}\n",
          "eldorado/def/companys/empresa_a/in/milho_a.sii":old("milho_a"),
          "eldorado/README.txt":"Formato diferente da Company usual"})
        with self.assertRaisesRegex(ValueError,"DIAGNOSTICO_ARQUIVO"):
            g.generate(self.inp,self.root/"failure_out")
        self.assertEqual(list((self.root/"failure_out").glob("*.scs")),[])
        reports=list((self.root/"failure_out").glob("DIAGNOSTICO_ARQUIVO_*.json"))
        self.assertEqual(len(reports),1)
        detail=json.loads(reports[0].read_text(encoding="utf-8"))
        self.assertEqual(detail["total_arquivos"],3)
        self.assertTrue(any("companys" in p for p in detail["amostra_geral"]))
        self.assertTrue((self.root/"failure_out"/"FALHA_MAPAS_NAO_GERAR.txt").exists())

    def test_eldorado_actual_root_company_layout(self):
        """Teste baseado nos nomes de arquivos REAIS do diagnostico Eldorado.

        O ZIP vem com ambev/out/bebidas.sii e NAO def/company/.
        Nao publicamos arquivos do usuario; conteudos sinteticos.
        """
        src=self.root/"eldorado.zip"
        raw={
            "alc_cle/editor/clementina.sii":"SiiNunit\n{}\n",
            "alc_cle/in/tanquevazio.sii":old("tanquevazio"),
            "alc_cle/out/alcool.sii":old("alcool"),
            "alccana/editor/penapolis.sii":"SiiNunit\n{}\n",
            "alccana/in/tanquevazio.sii":old("tanquevazio"),
            "alccana/out/alcool.sii":old("alcool"),
            "ambev/editor/almirante.sii":"SiiNunit\n{}\n",
            "ambev/in/sugar.sii":old("sugar"),
            "ambev/out/bebidas.sii":old("bebidas"),
            "ambev/out/beverages.sii":old("beverages"),
            "ancapi/out/cement.sii":old("cement"),
            "ancapi/out/apples.sii":old("apples"),
            "trade2/in/cement.sii":old("cement"),
            "trade2/out/cement.sii":old("cement")
        }
        zip_write(src,raw)
        self.assertEqual(g.canonical_path("ambev/out/bebidas.sii"),
                         "def/company/ambev/out/bebidas.sii")
        self.assertEqual(g.canonical_path("alc_cle/editor/clementina.sii"),
                         "def/company/alc_cle/editor/clementina.sii")
        self.assertEqual(g.canonical_path("trade2/in/cement.sii"),
                         "def/company/trade2/in/cement.sii")
        self.assertIsNone(g.canonical_path("random/docs/readme.txt"))
        diag=g.describe_archive(src)
        self.assertEqual(diag["layout_detectado"],"company_direto_na_raiz")
        self.assertEqual(diag["company_na_raiz"],14)
        self.assertEqual(diag["caminhos_reconhecidos"],14)
        self.assertEqual(diag["empresas_raiz_identificadas"],5)
        companies,count=g.extract_map(src)
        self.assertEqual(len(companies),5)
        self.assertEqual(count,11)
        self.assertEqual(len(companies["ambev"].editor_files),1)
        self.assertIn("bebidas",companies["ambev"].old_out)
        self.assertIn("sugar",companies["ambev"].old_in)
        self.assertEqual(companies["ambev"].role,"cervejaria")
        result=g.generate(self.inp,self.root/"eldorado_root_result")
        self.assertEqual(len(result),3)
        eldorado=next((p for name,p,data in result if name=="Eldorado"),None)
        self.assertIsNotNone(eldorado)
        with zipfile.ZipFile(eldorado) as scs:
            self.assertIsNone(scs.testzip())
            self.assertIn("def/company/ambev/out/bebidas.sii",scs.namelist())
            self.assertIn("def/company/ambev/out/carga12.sii",scs.namelist())
            self.assertIn("def/company/alc_cle/in/tanquevazio.sii",scs.namelist())
            self.assertEqual(scs.read("def/company/ambev/editor/almirante.sii"),
                             raw["ambev/editor/almirante.sii"].encode("utf-8"))
            self.assertIn('cargo: ""',scs.read(
                "def/company/ambev/out/bebidas.sii").decode("utf-8"))

    def test_eldorado_large_flat_archive_14758_files(self):
        """Stress test com as contagens do diagnostico (dados sinteticos)."""
        archive=self.root/"eldorado.zip"
        inout_total=13892
        editor_total=866
        with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_STORED) as z:
            for i in range(inout_total):
                cid=f"eld_company_{i//70:03d}"
                direction="in" if i%2 else "out"
                unit=f"item_{i:05d}"
                z.writestr(f"{cid}/{direction}/{unit}.sii",old(unit))
            for i in range(editor_total):
                cid=f"eld_company_{i%199:03d}"
                z.writestr(f"{cid}/editor/city_{i:04d}.sii",
                           "SiiNunit\n{}\n")
        diag=g.describe_archive(archive)
        self.assertEqual(diag["total_arquivos"],14758)
        self.assertEqual(diag["caminhos_in_out"],13892)
        self.assertEqual(diag["caminhos_reconhecidos"],14758)
        self.assertEqual(diag["company_na_raiz"],14758)
        self.assertEqual(diag["layout_detectado"],"company_direto_na_raiz")
        companies,count=g.extract_map(archive)
        self.assertEqual(count,13892)
        self.assertEqual(len(companies),199)
        self.assertEqual(sum(len(c.editor_files) for c in companies.values()),866)
        out=g.generate(self.inp,self.root/"large_out")
        self.assertEqual(len(out),3)
        eldorado=next((data for name,p,data in out if name=="Eldorado"))
        self.assertEqual(eldorado["arquivos_inout_originais"],13892)
        self.assertEqual(eldorado["arquivos_editor_preservados"],866)

    def test_eldorado_root_collision_cannot_be_silently_overwritten(self):
        src=self.root/"eldorado.zip"
        zip_write(src,{
            "ambev/out/bebidas.sii":old("bebidas"),
            "def/company/ambev/out/bebidas.sii":old("otherbeer")})
        with self.assertRaisesRegex(ValueError,"Colisao"):
            g.extract_map(src)

    def test_diagnostic_supports_def_company_and_bare_root(self):
        diag=g.describe_archive(self.root/"minas.zip")
        self.assertGreater(diag["caminhos_in_out"],0)
        self.assertGreater(diag["caminhos_reconhecidos"],0)
        self.assertIn("pastas_raiz",diag)

    def test_no_legacy_company_permanent_list_is_silently_ignored(self):
        src=self.root/"minas.zip"
        with zipfile.ZipFile(src) as z:
            contents={x.filename:z.read(x) for x in z.infolist()}
        contents["def/company/agrish.sii"]=(
            'SiiNunit\n{\n company_permanent : company.agrish {\n'
            ' in_cargo[]: cargo.milho_a\n }\n}\n')
        zip_write(src,contents)
        with self.assertRaisesRegex(ValueError,"FALHA_MAPAS_NAO_GERAR"):
            g.generate(self.inp,self.root/"legacy_rejected")
        self.assertEqual(list((self.root/"legacy_rejected").glob("*.scs")),[])
        reports=list((self.root/"legacy_rejected").glob("DIAGNOSTICO_ARQUIVO_*.json"))
        self.assertEqual(len(reports),1)
        details=json.loads(reports[0].read_text(encoding="utf-8"))
        self.assertIn("company_permanent",details["erro_de_leitura"])

    def test_reproducible_output_and_source_hashes(self):
        one=g.generate(self.inp,self.root/"first")
        two=g.generate(self.inp,self.root/"second")
        from hashlib import sha256
        for (name,p,data),(_,p2,data2) in zip(one,two):
            self.assertEqual(sha256(Path(p).read_bytes()).digest(),
                             sha256(Path(p2).read_bytes()).digest())
            self.assertEqual(data["versao_gerador"],g.VERSION)
            self.assertEqual(len(data["fontes_sha256"]),4)
            self.assertTrue(all(len(x["sha256"])==64 for x in data["fontes_sha256"]))
            self.assertEqual(len(data2["cadeias"]),23)

    def test_pallet_probability_independent_of_skill_checkbox(self):
        result=g.generate(self.inp,self.root/"no_skill",fix_skills=False)
        with zipfile.ZipFile(result[0][1]) as z:
            pallet=z.read("def/cargo/carga16.sui").decode()
            beer_names=z.namelist()
            self.assertIn("prob_coef: 0.08",pallet)
            self.assertIn("valuable: true",pallet)
            self.assertNotIn("def/cargo/carga12.sui",beer_names)

    def test_realistic_grade_baixa_classification_is_directional(self):
        """Fabricante de carro NAO produz bobina; equipamento NAO e siderurgica."""
        cases=[
          ("fiat",{"steel_coil"},{"bobina"},"automotiva_fabrica",
           False,True),
          ("mc_equipamentos",{"bobina"},{"bobina"},"maquinas",
           False,True),
          ("carmoprem",{"cimento"},{"cimento"},"premoldados",
           False,False),
          ("metalurgica_calhas",{"bobina"},{"chapa_aco"},"metalurgica",
           False,True),
          ("construcao_betim",{"bobina"},{"sucata"},"obras",
           False,False),
          ("gerdau",{"bobina"},{"iron_ore"},"siderurgica",
           True,False),
          ("cofer",{"bobina"},{"ferro"},"siderurgica",
           True,False),
          ("empresa_desconhecida",{"bobina"},{"bobina"},"desconhecida",
           False,False)
        ]
        for name,old_out,old_in,role,can_out,can_in in cases:
            with self.subTest(empresa=name):
                c=g.Company(name,old_in=old_in,old_out=old_out)
                g.classify_company(c)
                self.assertEqual(c.role,role)
                self.assertEqual(bool(g.permits(c,"bobina","out")),can_out)
                self.assertEqual(bool(g.permits(c,"bobina","in")),can_in)
        factory=g.Company("carmoprem",old_out={"cimento"},
                          old_in={"cimento"})
        g.classify_company(factory)
        self.assertIsNone(g.permits(factory,"cimento","out"),
                          "Empresa de pre-moldados compra cimento, nao o fabrica")
        self.assertTrue(g.permits(factory,"cimento","in"))
        marm=g.Company("marmoraria_botrel",old_out={"granito"})
        g.classify_company(marm)
        self.assertEqual(marm.role,"marmoraria")
        self.assertTrue(g.permits(marm,"granito","out"))
        self.assertFalse(g.product_types({"barraferro"}) & {"bobina"},
                         "Barras de ferro nao sao bobinas de aco")

    def test_low_deck_realistic_end_to_end_no_false_origins(self):
        src=self.root/"minas.zip"
        with zipfile.ZipFile(src) as z:
            content={x.filename:z.read(x) for x in z.infolist()}
        for name,direction,token in [
            ("fiat","out","bobina"),("fiat","in","bobina"),
            ("mc_equipamentos","out","bobina"),("mc_equipamentos","in","bobina"),
            ("carmoprem","out","cimento"),("carmoprem","in","cimento"),
            ("gerdau","out","steel_coil"),("metalurgica_calhas","in","bobina"),
            ("construcao_betim","in","bobina"),
            ("marmoraria_botrel","out","granito"),
        ]:
            content[f"def/company/{name}/{direction}/{token}.sii"]=old(token)
        zip_write(src,content)
        results=g.generate(self.inp,self.root/"grade_baixa_qa")
        scs=next(p for name,p,data in results if name=="Minas_Gerais")
        audit=next(data for name,p,data in results if name=="Minas_Gerais")
        with zipfile.ZipFile(scs) as z:
            names=set(z.namelist())
            for company in ("fiat","mc_equipamentos","construcao_betim"):
                self.assertNotIn(f"def/company/{company}/out/carga9.sii",names)
            self.assertNotIn("def/company/carmoprem/out/carga6.sii",names)
            self.assertNotIn("def/company/carmoprem/out/carga10.sii",names)
            self.assertIn("def/company/carmoprem/in/carga6.sii",names)
            self.assertIn("def/company/fiat/in/carga9.sii",names)
            self.assertIn("def/company/gerdau/out/carga9.sii",names)
            self.assertIn("def/company/metalurgica_calhas/in/carga9.sii",names)
            self.assertIn("def/company/marmoraria_botrel/out/carga14.sii",names)
            for path in ("def/company/fiat/out/bobina.sii",
                         "def/company/mc_equipamentos/out/bobina.sii",
                         "def/company/carmoprem/out/cimento.sii"):
                self.assertIn('cargo: ""',z.read(path).decode())
        self.assertNotIn("fiat",audit["cadeias"]["carga9"]["origens_lista"])
        self.assertNotIn("mc_equipamentos",audit["cadeias"]["carga9"]["origens_lista"])
        self.assertNotIn("carmoprem",audit["cadeias"]["carga6"]["origens_lista"])
        rejected={(r["empresa"],r["categoria"]) for r in audit["rejeicoes_grade_baixa"]}
        self.assertIn(("fiat","bobina"),rejected)
        self.assertIn(("mc_equipamentos","bobina"),rejected)
        self.assertIn(("carmoprem","cimento"),rejected)
        self.assertTrue((self.root/"grade_baixa_qa"/
                         "Minas_Gerais_rotas_justificadas.csv").is_file())

    def test_eldorado_english_cargo_translation_without_false_equivalence(self):
        english={
            "potatoes":"batata","potatoes_b":"batata","orange":"laranja",
            "bananas":"banana","banana_a":"banana","fertilizer":"adubo",
            "soybeans":"soja","corn":"milho","sorghum":"sorgo",
            "rice":"arroz","wheat":"trigo","animal_feed":"racao",
            "beer":"cerveja","beverages":"bebidas_gerais",
            "bottle_water":"bebidas_gerais","cement":"cimento",
            "bricks":"tijolo","granite":"granito","steel_coils":"bobina",
        }
        for token,expected in english.items():
            with self.subTest(token=token):
                self.assertIn(expected,g.eldorado_translate({token}))
        self.assertNotIn("batata",g.eldorado_translate({"bananas"}))
        self.assertNotIn("laranja",g.eldorado_translate({"bananas"}))
        self.assertNotIn("cerveja",g.eldorado_translate({"beverages"}))
        self.assertNotIn("batata",g.eldorado_translate({"fruits"}))
        self.assertNotIn("laranja",g.eldorado_translate({"fruits"}))

    def test_eldorado_transporters_not_goods_factories_and_banana_not_potato(self):
        tests=[
            ("brasilog",{"potatoes","oranges"},set(),"transportadora"),
            ("rasador",{"beer","beverages"},set(),"transportadora"),
            ("cmm_transportes",{"potatoes"},set(),"transportadora"),
            ("avant_transportes",{"potatoes"},set(),"transportadora"),
            ("ttrlog",{"fertilizer"},set(),"transportadora"),
            ("eldorado_bananas",{"bananas"},{"potatoes","fertilizer"},"bananal"),
        ]
        for name,outs,ins,expected in tests:
            with self.subTest(company=name):
                c=g.Company(name,old_out=outs,old_in=ins)
                g.classify_company(c)
                g.eldorado_classify(c)
                self.assertEqual(c.role,expected)
                for commodity in ("batata","laranja","cerveja","milho","soja"):
                    self.assertIsNone(g.eldorado_permit(c,commodity,"out"))
                    self.assertIsNone(g.eldorado_permit(c,commodity,"in"))
                if expected=="bananal":
                    self.assertTrue(g.eldorado_permit(c,"adubo","in"))
                    self.assertIsNone(g.eldorado_permit(c,"adubo","out"))

    def test_eldorado_only_regeneration_preserves_minas_and_rbr_files(self):
        # Saida inicial representa as Companies ja aprovadas anteriormente.
        folder=self.root/"preserve_old_companies"
        folder.mkdir()
        a=folder/"ETS2_MINAS_GERAIS_COMPANY.scs"
        b=folder/"ETS2_RBR_COMPANY.scs"
        a.write_bytes(b"MINAS_ANTIGO_SCS_NAO_MODIFICAR")
        b.write_bytes(b"RBR_ANTIGO_SCS_NAO_MODIFICAR")
        eldorado_zip=self.root/"eldorado.zip"
        raw={}
        for name,direction,token in [
            ("brasilog","out","potatoes"),
            ("rasador","out","beverages"),
            ("avant_transportes","out","orange"),
            ("eldorado_bananas","out","bananas"),
            ("eldorado_bananas","in","potatoes"),
            ("eldorado_bananas","in","fertilizer"),
            ("fazenda_potato","out","potatoes"),
            ("fazenda_orange","out","oranges"),
            ("ceasa","in","potatoes"),
            ("ceasa","out","potatoes"),
            ("supermercado_centro","in","potatoes"),
            ("supermercado_centro","in","orange"),
            ("ambev","out","beer"),
            ("supermercado_centro","in","beer"),
            ("agrish","out","fertilizer"),
        ]:
            raw[f"{name}/{direction}/{token}.sii"]=old(token)
        raw["eldorado_bananas/editor/penapolis.sii"]="SiiNunit\n{}\n"
        zip_write(eldorado_zip,raw)
        original_a=a.read_bytes();original_b=b.read_bytes()
        inp={**self.inp,"maps":{"Eldorado":eldorado_zip}}
        result=g.generate(inp,folder,fix_skills=False)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0][0],"Eldorado")
        self.assertEqual(a.read_bytes(),original_a)
        self.assertEqual(b.read_bytes(),original_b)
        with zipfile.ZipFile(result[0][1]) as z:
            names=set(z.namelist())
            for company in ("brasilog","rasador","avant_transportes"):
                for n in (7,8,12,3):
                    self.assertNotIn(f"def/company/{company}/out/carga{n}.sii",names)
            for n in (7,8,12):
                self.assertNotIn(f"def/company/eldorado_bananas/in/carga{n}.sii",names)
            self.assertIn("def/company/eldorado_bananas/in/carga3.sii",names)
            self.assertIn("def/company/fazenda_potato/out/carga7.sii",names)
            self.assertIn("def/company/fazenda_orange/out/carga8.sii",names)
            self.assertIn("def/company/ceasa/in/carga7.sii",names)
            self.assertIn("def/company/ambev/out/carga12.sii",names)
            self.assertIn('cargo: ""',z.read("def/company/brasilog/out/potatoes.sii").decode())
            self.assertIn('cargo: ""',z.read(
                "def/company/eldorado_bananas/in/potatoes.sii").decode())
            self.assertIn("def/company/eldorado_bananas/editor/penapolis.sii",names)
        report=result[0][2]
        self.assertEqual(report["versao_gerador"],"2.3.0")
        self.assertEqual(report["total_empresas"],10)
        self.assertNotIn("eldorado_bananas",report["cadeias"]["carga7"]["destinos_lista"])
        self.assertNotIn("brasilog",report["cadeias"]["carga7"]["origens_lista"])
        self.assertIn("potatoes",report["traducoes_ingles_portugues"])
        self.assertIn("batata",report["traducoes_ingles_portugues"]["potatoes"])
        reject={(x["empresa"],x["direcao"],x["familia"])
                for x in report["rejeicoes_eldorado"]}
        self.assertIn(("brasilog","out","batata"),reject)
        self.assertIn(("eldorado_bananas","in","batata"),reject)
        self.assertTrue((folder/"Eldorado_traducoes_cargas_ingles.csv").is_file())
        self.assertTrue((folder/"Eldorado_permissoes_rejeitadas.csv").is_file())

    def test_neutralization(self):
        s=old("banana")
        self.assertEqual(g.cargo_tokens(g.neutralize(s.encode(),"x").decode()),[])
        self.assertIn('cargo: ""',g.neutralize(s.encode(),"x").decode())
    def test_company_root_without_def_prefix(self):
        src=self.root/"minas.zip"
        with zipfile.ZipFile(src) as z:
            content={x.filename:z.read(x) for x in z.infolist()}
        content={p.removeprefix("def/"):raw for p,raw in content.items()}
        zip_write(src,content)
        companies,count=g.extract_map(src)
        self.assertEqual(len(companies),len(self.company_raw))
        self.assertGreater(count,10)
        self.assertEqual(companies["fazenda_a"].role,"fazenda")

    def test_agro_name_with_crop_history_is_farm(self):
        c=g.Company("agro_fazenda",old_in={"adubo"},old_out={"milho_a","soja_b"})
        g.classify_company(c)
        self.assertEqual(c.role,"fazenda")

    def test_original_files_not_modified(self):
        before={str(p):p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        g.generate(self.inp,self.root/"output")
        after={str(p):p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        self.assertEqual(before,after)

    def test_not_zip(self):
        p=self.root/"bad.scs";p.write_bytes(b"not a ZIP")
        with self.assertRaisesRegex(ValueError,"SCS Extractor"):
            g.zip_members(p)

if __name__=="__main__":unittest.main()
