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
        contents["def/cargo/carga1/rodotrem.sii"]=(
            "SiiNunit\n{ trailer_def : .a { body_type: errado } }\n")
        zip_write(src,contents)
        with self.assertRaisesRegex(ValueError,"carga1"):
            g.generate(self.inp,self.root/"invalid")
        self.assertFalse((self.root/"invalid"/"ETS2_MINAS_GERAIS_COMPANY.scs").exists())
    def test_neutralization(self):
        s=old("banana")
        self.assertEqual(g.cargo_tokens(g.neutralize(s.encode(),"x").decode()),[])
        self.assertIn('cargo: ""',g.neutralize(s.encode(),"x").decode())
    def test_not_zip(self):
        p=self.root/"bad.scs";p.write_bytes(b"not a ZIP")
        with self.assertRaisesRegex(ValueError,"SCS Extractor"):
            g.zip_members(p)

if __name__=="__main__":unittest.main()
