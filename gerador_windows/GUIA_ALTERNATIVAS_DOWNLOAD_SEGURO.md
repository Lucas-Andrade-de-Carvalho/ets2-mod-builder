# Alternativas de distribuicao do Gerador ETS2 Windows

O Chrome pode bloquear o pacote com ETS2_Company_Gerador.exe mesmo quando
baixado do proprio GitHub. A origem GitHub e o status verde do GitHub Actions
nao certificam ausencia de malware; tampouco o bloqueio prova malware.

## Tres formatos do mesmo codigo

- `Gerador-ETS2-Windows`: executavel unico feito com PyInstaller --onefile.
- `Gerador-ETS2-Windows-Pasta`: aplicativo PyInstaller --onedir. Extraia TODOS
  os arquivos e a pasta `_internal`, sem separa-los. O programa se encontra em
  `ETS2_Company_Gerador/ETS2_Company_Gerador.exe`. Pode ou nao disparar
  o mesmo alerta: nao e uma tecnica de burlar antivírus.
- `Gerador-ETS2-Codigo-Fonte`: scripts .py sem executavel Windows. Usa
  Python 3.12 com tkinter e somente a biblioteca padrao em tempo de execucao.

## Para usar o codigo-fonte

1. Baixe o artefato `Gerador-ETS2-Codigo-Fonte` na mesma execucao GitHub Actions,
   extraia para uma pasta e confira os arquivos `gerador.py`,
   `politica_economica.py`, `auditor_existentes.py` e os outros .py juntos.
2. Instale o Python 3.12 pelo site oficial python.org, se ainda nao estiver
   instalado. Nao use download de Python de sites desconhecidos.
3. Abra o Prompt de Comando nessa pasta, rode `py -3.12 gerador.py`.
   Se o iniciador `py` nao estiver instalado, rode `python gerador.py`.
4. Execute a auditoria e geracao pelo mesmo formulario.

## Validacao antes de executar

- Verifique na pagina GitHub Actions se a compilacao terminou com sucesso.
- Confira o commit e os hashes SHA-256 registrados no arquivo
  `PROVENIENCIA_SHA256.txt` (EXE unico) e `PROVENIENCIA_PASTA_SHA256.txt`
  (EXE em pasta). O hash comprova integridade em relacao ao build, nao
  seguranca nem assinatura de codigo.
- Execute uma analise com o Microsoft Defender e investigue qualquer
  deteccao. Caso indique malware, nao rode o executavel.
- A versao PyInstaller gerada automaticamente nao e assinada digitalmente.
  Assinatura por editor identificado requer certificado de assinatura de
  codigo e configuracao de CI/entrega confiavel.

Nao desative a Navegacao Segura e nao altere extensoes, criptografe arquivos
ou use outro navegador apenas para contornar a deteccao.

Nenhum desses formatos homologa fretes dentro do ETS2; a verificacao real
continua necessaria nos tres mapas.
