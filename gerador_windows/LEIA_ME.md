## V2.1 — ZIP Eldorado reconhecido

O diagnostico original confirmou 14.758 arquivos SII, incluindo 13.892 entradas IN/OUT com pastas de empresas diretamente na raiz (ex.: ambev/out/bebidas.sii, alc_cle/editor/clementina.sii). O leitor agora converte automaticamente para def/company/<empresa>/<in|out|editor>/<arquivo>.sii e preserva os editores byte a byte. Nao altere o ZIP original. Testes de volume usando dados sinteticos reproduzem as contagens do mapa. Nenhum arquivo privado do mapa foi publicado neste repositorio. O mercado dentro do ETS2 ainda exige validacao real com reboque proprio, perfil e carroceria.

---

# ETS2 Company Logistics Ultimate v2.0 — Gerador offline para Windows

## O que muda nesta versão

- **Diagnóstico dos três mapas antes de gerar:** o botão "1. DIAGNOSTICAR OS 3 MAPAS" funciona mesmo que o Eldorado tenha uma estrutura de Company ainda não reconhecida. Ele produz DIAGNOSTICO_ARQUIVO_*.json com os caminhos originais dos arquivos do ZIP, extensões, pastas e amostras de empresas.
- **Nao aceita resultado parcial:** o botão "2. VALIDAR E GERAR 3 COMPANIES" analisa os tres mapas ANTES de publicar qualquer SCS. Um erro no Eldorado gera FALHA_MAPAS_NAO_GERAR.txt e nao publica a Company de Minas separadamente.
- **Interface responsiva:** o trabalho e realizado fora da thread principal; os caminhos dos 7 arquivos sao salvos localmente no Windows e recuperados na proxima abertura.
- **Auditoria com rastreabilidade:** cada JSON tem o hash SHA-256 dos arquivos fonte usados, justificativas de cada IN/OUT, total de empresas e cargas sem cadeia completa. O ZIP SCS gerado e reproducivel com entradas em ordem estavel.
- **Melhor inspecao do reboque:** registros cargo_data, tipos de carroceria, def/vehicle/trailer_defs e manifestos de cargo sao verificados. Um aviso NAO equivale a compatibilidade confirmada no jogo.
- **Bloqueio de defs legadas:** empresas com in_cargo/out_cargo no company_permanent recebem diagnostico de incompatibilidade, ja que o ETS2 soma essas listas mesmo quando arquivos in/out sao neutralizados.
- **Palete Alto:** o ajuste de frequencia relativa (prob_coef 0.08) independe da opcao de remover a habilidade de Alto Valor. Madeireiras ficam OUT e recicladoras IN quando o mapa permite.

## Instalacao / procedimento recomendado

1. No GitHub, abra **Actions > Compilar Gerador Windows**, selecione o resultado mais recente com **Success** e baixe o artefato **Gerador-ETS2-Windows**.
2. Extraia o ZIP, feche e substitua a versão anterior de ETS2_Company_Gerador.exe.
3. Abra o EXE e selecione os sete arquivos reais do seu Librelato e dos mapas e a pasta de saida. O programa salva esses caminhos apenas no PC do usuario.
4. **Antes de gerar, clique em "1. DIAGNOSTICAR OS 3 MAPAS"**. Se Eldorado nao for reconhecido, compartilhe somente seu arquivo DIAGNOSTICO_ARQUIVO_*Eldorado*.json para evoluirmos o suporte sem inventar empresas.
5. Depois clique em "2. VALIDAR E GERAR 3 COMPANIES". O sistema nao publica arquivos SCS desta execucao se um dos tres mapas tiver a estrutura desconhecida.
6. Se gerar os tres, confira auditorias JSON e CSV. Instale apenas a Company do mapa utilizado e teste no ETS2 em Grade Alta e Grade Baixa, com as prioridades de mods corretas. Colete game.log.txt para erros.

**Limite honesto:** esta ferramenta NAO verifica ao vivo as ofertas de mercado e nao tem acesso automatico a prefabs, versao do ETS2, perfil, habilidade de motorista e carroceria instalada. A auditoria estatica e a compilacao do EXE NAO garantem funcionalidade in-game. So considere uma Company apta para cliente apos homologacao no jogo.

## Segurança dos originais

Nenhum dos sete arquivos e alterado, sobrescrito, publicado ou enviado a um servidor; o programa trabalha totalmente offline com copias em memoria. Os JSON de auditoria contem somente hashes e nomes dos arquivos, nao os caminhos completos de origem. A pasta de saida e controlada pelo usuario.

---

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
