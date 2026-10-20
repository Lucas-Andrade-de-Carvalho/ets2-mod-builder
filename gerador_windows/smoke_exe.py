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
    finally:
        case.tearDown()

if __name__=="__main__":
    main(sys.argv[1])
