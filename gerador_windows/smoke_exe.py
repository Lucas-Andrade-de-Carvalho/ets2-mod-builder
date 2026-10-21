"""Windows binary smoke test: run packaged EXE against a synthetic three-map job."""
from pathlib import Path
import subprocess
import sys

from test_gerador import Regression

def main(exe_path):
    case=Regression()
    case.setUp()
    try:
        p=case.inp
        out=case.root/"binary_out"
        cmd=[str(Path(exe_path).resolve()),
             "--cli",
             "--mod",str(p["mod"]),
             "--def1",str(p["def1"]),
             "--def2",str(p["def2"]),
             "--txt",str(case.root/"cargas.txt"),
             "--minas",str(p["maps"]["Minas_Gerais"]),
             "--eldorado",str(p["maps"]["Eldorado"]),
             "--rbr",str(p["maps"]["RBR"]),
             "--output",str(out)]
        # Texto de carga sintetico para o CLI; corresponde ao manifesto.
        (case.root/"cargas.txt").write_text(
            "\n".join(f"carga{n} = {name}" for n,(_,name) in case.g.MANIFEST.items())
            if hasattr(case,"g") else
            "\n".join(f"carga{n} = {name}" for n,(_,name) in __import__("gerador").MANIFEST.items()),
            encoding="utf-8")
        r=subprocess.run(cmd,timeout=120,check=False)
        if r.returncode:
            raise RuntimeError(f"EXE retornou codigo {r.returncode}")
        generated=list(out.glob("*.scs"))
        assert len(generated)==3, f"Esperado 3 SCS; encontrados {len(generated)}"
        assert len(list(out.glob("*_auditoria.json")))==3
        print("EXE Windows executou e gerou tres mods sinteticos:",*[x.name for x in generated])
        # Executar tambem a funcao cliente: atualizar apenas Eldorado.
        # Prova que nao precisamos carregar os arquivos MG/RBR nesse modo.
        only=case.root/"eldorado_only_exe"
        only.mkdir()
        mg=only/"ETS2_MINAS_GERAIS_COMPANY.scs"
        rbr=only/"ETS2_RBR_COMPANY.scs"
        mg.write_bytes(b"MINAS_CLIENTE_NAO_MODIFICAR")
        rbr.write_bytes(b"RBR_CLIENTE_NAO_MODIFICAR")
        command=[str(Path(exe_path).resolve()),"--cli","--only-eldorado",
                 "--mod",str(p["mod"]),"--def1",str(p["def1"]),
                 "--def2",str(p["def2"]),
                 "--txt",str(case.root/"cargas.txt"),
                 "--eldorado",str(p["maps"]["Eldorado"]),
                 "--output",str(only)]
        rr=subprocess.run(command,timeout=120,check=False)
        # A DEF sintetica nao tem as 23 cadeias completas: o comportamento
        # correto V2.4 e BLOQUEAR o Eldorado incompleto.
        if rr.returncode==0:
            raise RuntimeError("EXE aceitou Company Eldorado com cargas sem rota!")
        assert not (only/"ETS2_ELDORADO_COMPANY.scs").exists()
        assert (only/"Eldorado_COBERTURA_23_CARGAS.json").is_file()
        assert (only/"Eldorado_COBERTURA_INCOMPLETA.txt").is_file()
        assert mg.read_bytes()==b"MINAS_CLIENTE_NAO_MODIFICAR"
        assert rbr.read_bytes()==b"RBR_CLIENTE_NAO_MODIFICAR"
        print("EXE Windows BLOQUEOU corretamente Eldorado incompleto; MG e RBR intactos")
        # Auditar e corrigir SCS JA EXISTENTE. A executavel precisa
        # importar o modulo de auditoria em ambiente PyInstaller isolado.
        from test_auditor_existentes import AuditorSCSRegression
        fixture=AuditorSCSRegression()
        fixture.setUp()
        try:
            target=fixture.root/"exe_audit_existing"
            command=[str(Path(exe_path).resolve()),"--cli","--audit-existing",
                     "--only-eldorado","--existing-eldorado",str(fixture.existing),
                     "--eldorado",str(fixture.baseline),"--output",str(target)]
            returned=subprocess.run(command,timeout=120,check=False)
            if returned.returncode:
                raise RuntimeError("EXE nao corrigiu Company existente: "+str(returned.returncode))
            corrected=list(target.glob("ETS2_ELDORADO_AUDITADA_V25_*.scs"))
            assert len(corrected)==1,"Companhia corrigida inexistente"
            import zipfile,json
            with zipfile.ZipFile(corrected[0]) as z:
                assert b'cargo: ""' in z.read("def/company/brasilog/out/carga7.sii")
                assert b'cargo.carga12' in z.read("def/company/ambev/out/carga12.sii")
            audit_json=json.loads((target/"AUDITORIA_ELDORADO.json").read_text(
                encoding="utf-8"))
            assert audit_json["permissoes_removidas"]>=3
            print("EXE Windows auditou SCS existente, corrigiu rotas e preservou original")
        finally:
            fixture.tearDown()
    finally:
        case.tearDown()

if __name__=="__main__":
    main(sys.argv[1])
