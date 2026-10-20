# Gerador Offline ETS2 Company Logistics (Windows)

O programa analisa IN/OUT originais e gera tres mods de Company independentes (Minas Gerais, Eldorado e RBR) para o Rodotrem 9 Eixos Librelato.

**AVISO:** valida arquivos e referencias, mas nao prova que o mercado do ETS2 vai ficar preenchido. Esse teste exige o jogo, o perfil e a configuracao real do reboque. Se as definicoes originais estiverem incorretas, o gerador interrompe a entrega e produz FALHA_DIAGNOSTICO.txt.

## Como usar sem programar

1. Acesse Actions > Compilar Gerador Windows neste repositorio.
2. Abra uma execucao concluida com sucesso e, em Artifacts, baixe Gerador-ETS2-Windows.
3. Descompacte o ZIP e execute ETS2_Company_Gerador.exe.
4. Selecione os 7 arquivos: mod principal, duas DEFs do rodotrem, TXT e os tres mapas. Selecione a pasta de saida.
5. Clique em ANALISAR E GERAR 3 COMPANIES.
6. Confira os JSON e CSV de auditoria. Instale somente o SCS do mapa ativo, com prioridade acima das DEFs que ele substitui.

O executavel e compilado no GitHub Actions a partir do Python deste diretorio; nao exige instalar Python no Windows. Como nao e assinado, o SmartScreen pode solicitar confirmacao. Verifique a origem antes de executa-lo.

## Regras de seguranca e fidelidade

- Nao modifica os arquivos originais.
- Detecta cargas declaradas, body_types de cargo_data e trailer_def e rejeita incompatibilidades essenciais.
- Preserva as empresas do mapa; neutraliza antigas referencias IN/OUT por sobreposicao dos mesmos caminhos, conforme orientacao da SCS.
- Nao inventa produtor ou comprador obrigatorio se a DEF nao sustenta tal cadeia; registra cargos sem rota em auditoria.
- Corrige opcionalmente valuable: true das 23 cargas comuns somente no SCS gerado; reduz apenas a probabilidade do Palete Alto.
- Se o SCS original nao for ZIP legivel, exige extracao oficial e aceita uma pasta extraida.
- Nao detecta a carroceria atualmente instalada pelo jogador, restricoes do prefab nem a disponibilidade no perfil; por isso nao e homologacao in-game.

## CLI opcional

Com Python 3.10+:

    python gerador.py --cli --mod "Librelato.scs" --def1 "Def Company 1.scs" --def2 "Def Company 2.scs" --txt "cargas.txt" --minas "minas.zip" --eldorado "eldorado.zip" --rbr "rbr.zip" --output "saida"

Documentacao: https://modding.scssoft.com/wiki/Documentation/Engine/Units/cargo_data e https://modding.scssoft.com/wiki/Documentation/Engine/Units/cargo_def e https://modding.scssoft.com/wiki/Documentation/Engine/Units/trailer_def .
