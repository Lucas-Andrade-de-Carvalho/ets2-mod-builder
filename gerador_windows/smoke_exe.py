"""Windows binary smoke test: run packaged EXE against a synthetic three-map job."""
from pathlib import Path
import subprocess
import os
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
        # Diagnostico binario deve funcionar com SCS/TXT SEM nenhuma DEF de mapa.
        independent=case.root/"diagnostico_librelato_exe"
        pre=[str(Path(exe_path).resolve()),"--cli","--diagnose-librelato",
             "--mod",str(p["mod"]),"--def1",str(p["def1"]),
             "--def2",str(p["def2"]),"--txt",str(case.root/"cargas.txt"),
             "--output",str(independent)]
        checked=subprocess.run(pre,timeout=120,check=False)
        if checked.returncode:
            raise RuntimeError("EXE falhou em diagnosticar so o Librelato/TXT")
        import json
        source_report=json.loads(
            (independent/"DIAGNOSTICO_LIBRELATO_CARGAS_ORIGINAIS.json").read_text(
                encoding="utf-8"))
        assert source_report["total_cargas_catalogo"]==23
        assert not source_report["erros"]
        print("EXE diagnosticou MOD/DEF1/DEF2 e TXT sem DEFs de mapas")
        r=subprocess.run(cmd,timeout=120,check=False)
        # O mapa simples dos testes nao contem 23 cadeias economicamente
        # corretas. Modo profissional deve REJEITAR e emitir lacunas.
        if r.returncode==0:
            raise RuntimeError("EXE V3 aceitou tres Companies com fretes ficticios")
        generated=list(out.glob("*.scs"))
        assert not generated,"EXE nao pode publicar Companies parciais"
        assert list(out.glob("*_COBERTURA_23_CARGAS.json"))
        print("EXE Windows rejeitou corretamente mapas sem 23 rotas profissionais")
        # Executa a interface REAL de dentro do EXE nos tamanhos de janela
        # 1024x720 e 960x600. Os botoes devem aparecer acima do formulario.
        env=os.environ.copy()
        env["ETS2_GUI_LAYOUT_SMOKE"]="1"
        gui=subprocess.run([str(Path(exe_path).resolve())],env=env,
                           timeout=40,check=False)
        if gui.returncode:
            raise RuntimeError("Interface com botoes visiveis falhou: "+
                               str(gui.returncode))
        print("EXE Windows mostra botoes Diagnosticar/Gerar/Auditar/Abrir Pasta em tamanhos reduzidos")

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
            # Protocolo final deve funcionar EMBUTIDO no EXE Windows e
            # rejeitar os 23 cargos sinteticos quando sao exigidos 24.
            prescan=fixture.root/"exe_real_preflight"
            checklist_cmd=[str(Path(exe_path).resolve()),"--cli","--preflight-real",
                "--mod",str(p["mod"]),"--def1",str(p["def1"]),
                "--def2",str(p["def2"]), "--txt",str(case.root/"cargas.txt"),
                "--minas",str(fixture.baseline),
                "--eldorado",str(fixture.baseline),
                "--rbr",str(fixture.baseline),
                "--existing-minas",str(fixture.existing),
                "--existing-eldorado",str(fixture.existing),
                "--existing-rbr",str(fixture.existing),
                "--output",str(prescan)]
            checked=subprocess.run(checklist_cmd,timeout=120,check=False)
            if checked.returncode==0:
                raise RuntimeError("Preflight aprovou erroneamente 23 cargas como 24")
            summary_path=prescan/"RESULTADO_PRE_HOMOLOGACAO.json"
            if not summary_path.is_file():
                raise RuntimeError("Preflight do EXE nao gerou relatorio de bloqueio")
            import json
            summary=json.loads(summary_path.read_text(encoding="utf-8"))
            assert summary["status_pre_homologacao"]=="BLOQUEADO_TECNICO"
            assert not summary["homologado_no_ets2"]
            print("EXE: pre-homologacao bloqueou 23/24 cargas; relatorio preservado")
            target=fixture.root/"exe_audit_existing"
            audittxt=fixture.root/"auditoria_cargas.txt"
            from gerador import MANIFEST
            audittxt.write_text(
                "\n".join(f"carga{n} = {title}"
                          for n,(_category,title) in MANIFEST.items()),
                encoding="utf-8")
            command=[str(Path(exe_path).resolve()),"--cli","--audit-existing",
                     "--only-eldorado","--existing-eldorado",str(fixture.existing),
                     "--eldorado",str(fixture.baseline),
                     "--mod",str(fixture.fixture.inp["mod"]),
                     "--def1",str(fixture.fixture.inp["def1"]),
                     "--def2",str(fixture.fixture.inp["def2"]),
                     "--txt",str(audittxt),
                     "--output",str(target)]
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
            # Compilado de verdade: 24 cargas + 3 mapas ->
            # SCS candidatos somente apos segunda auditoria sem mutacoes.
            with zipfile.ZipFile(fixture.fixture.inp["mod"]) as arc:
                items={name:arc.read(name) for name in arc.namelist()}
            items["def/cargo/carga24.sui"]=(
                b"cargo_data : cargo.carga24 {\n body_types[]: alta\n}\n")
            mod24=fixture.root/"mod_real_24.scs"
            with zipfile.ZipFile(mod24,"w") as arc:
                for k,data in items.items():
                    arc.writestr(k,data)
            cargostxt=fixture.root/"24_cargas.txt"
            cargostxt.write_text(audittxt.read_text(encoding="utf-8")+
                                 "\ncarga24 = Coco\n",encoding="utf-8")
            delivered=fixture.root/"exe_finalizacao_offline"
            cmd=[str(Path(exe_path).resolve()),"--cli","--finalize-offline",
                 "--mod",str(mod24),
                 "--def1",str(fixture.fixture.inp["def1"]),
                 "--def2",str(fixture.fixture.inp["def2"]),
                 "--txt",str(cargostxt),
                 "--minas",str(fixture.baseline),
                 "--eldorado",str(fixture.baseline),
                 "--rbr",str(fixture.baseline),
                 "--existing-minas",str(fixture.existing),
                 "--existing-eldorado",str(fixture.existing),
                 "--existing-rbr",str(fixture.existing),
                 "--output",str(delivered)]
            called=subprocess.run(cmd,timeout=180,check=False)
            if called.returncode:
                raise RuntimeError("EXE falhou ao finalizar offline tres SCS")
            result=json.loads((delivered/"RESULTADO_FINALIZACAO_OFFLINE.json")
                              .read_text(encoding="utf-8"))
            assert len(result["arquivos_corrigidos"])==3
            assert result["reescritas_residuais"]==0
            assert not result["homologado_no_ets2"]
            print("EXE Windows gerou tres SCS candidatos, reabriu ZIP e reauditorou todos")
        finally:
            fixture.tearDown()
    finally:
        case.tearDown()

if __name__=="__main__":
    main(sys.argv[1])
