## V2.3 — Mapa Eldorado: logística bilíngue e atualização isolada

**Por que mudou:** um teste real no mercado do Eldorado mostrou fretes absurdos, como batatas expedidas por transportadoras e entregues em plantações de banana. O problema era uma classificação ampla de hortifruti/atacadista e a reutilização pouco criteriosa dos IN/OUT originais.

**Correção restrita ao Eldorado:** use a opção marcada por padrão **Somente ELDORADO — manter Minas Gerais e RBR intactos**. O programa exige apenas o mod original Librelato, suas duas DEFs, o TXT das 23 cargas, o ZIP Eldorado e a pasta de saída. Não lê, recria nem sobrescreve os SCS de Minas e RBR. A opção de gerar todos os três continua disponível mediante escolha explícita.

### Critérios específicos do Eldorado

- Transportadoras e centrais genéricas de carga **não** são produtoras nem destinos finais por terem mercadorias no IN/OUT original. Empresas com enorme catálogo heterogêneo recebem classificação conservadora.
- Bananais/plantações de banana podem receber insumos agrícolas, como adubo, mas **não recebem batatas ou laranjas** por serem simplesmente fazendas ou empresas de hortifruti.
- Batatas e laranjas são cadeias distintas: produção na fazenda daquela cultura, revenda/armazenagem por empresas com movimentação documentada e consumo por comércio/indústria compatíveis.
- Cerveja sai de cervejarias identificadas, ou de revendas que comprovem comercialização de cerveja; transporte de terceiros não vira fabricação.
- Os IDs ingleses de mercadorias são interpretados por famílias econômicas sem colapsar banana, orange, potatoes e fruits na mesma carga. Ex.: potatoes=batata; orange=laranja; fertilizer=adubo; beer=cerveja; beverages=bebidas diversas (não prova que seja cerveja); bananas=banana (não é carga de batata).
- Grãos, ração, madeira, paletes, bobinas, cimento, tijolos e granito também têm restrições direcionais por papel econômico. Cargas sem produtor ou destino confiável permanecem sinalizadas, sem inventar cadeia.
- Dois relatórios novos: **Eldorado_traducoes_cargas_ingles.csv** e **Eldorado_permissoes_rejeitadas.csv**; o JSON Eldorado inclui justificativas, traduções e decisões rejeitadas.

A automação passou por testes sintéticos de classificação e geração, mas NÃO equivale a analisar linha a linha todos os arquivos reais do Eldorado nem confirma o mercado dentro do ETS2. Antes de entregar ao cliente, confira o JSON/CSV do Eldorado e teste cargas usando as carrocerias adequadas e game.log.txt.

### Como substituir somente a Company do Eldorado

1. Baixe o executável mais recente na aba GitHub Actions e abra a V2.3.
2. Selecione ou confirme os arquivos originais e a DEF do Eldorado. Deixe selecionado **Somente ELDORADO**.
3. Clique em **GERAR COMPANY(S) SELECIONADA(S)**.
4. Instale SOMENTE o novo arquivo **ETS2_ELDORADO_COMPANY.scs** no lugar do Eldorado antigo. Desative o SCS anterior desse mapa; mantenha Minas Gerais/RBR como estão.
5. Confira os relatórios. Se alguma carga ficar sem saída/destino, não preencha artificialmente: reporte a lacuna no JSON.
6. Dentro do ETS2, confirme as empresas, configurações e as ofertas; um relatório estrutural não prova homologação.

**CLI:** usar a flag --only-eldorado dispensa --minas e --rbr e preserva os arquivos desses mapas na pasta de saída.

---

## V2.2 — Logistica realista da Grade Baixa

A tela do Mercado de Cargas revelou falsas origens para bobinas e cimento.
Agora o gerador separa rigorosamente os papeis de produtores e consumidores.

- **Bobinas de aço (carga9)**: somente siderurgicas identificadas (como Gerdau/Cofer) podem expedir. Fiat e outras montadoras podem receber insumos, mas nao sao produtoras de bobinas. Fabricantes de equipamentos so recebem bobinas se a DEF original comprovar a entrada. Obras genericas nao recebem bobinas sem justificativa.
- **Cimento (carga6, 10, 11)**: sai de cimenteiras e revendas com historico de venda; fabricas de pre-moldados, como Carmoprem, recebem cimento para fabricar outros produtos, mas nao sao cimenteiras.
- **Granito (carga14, 15)**: origens em pedreiras e marmorarias identificadas, com destino coerente em beneficiamento, revenda ou obra.
- **Classificacao segura**: uma empresa nao vira siderurgica so porque o arquivo OUT original tem bobinas. Diferenciacao entre produtos como vergalhoes, barras de ferro e bobinas.
- **Auditoria adicional**: gerados MAPA_rotas_justificadas.csv e o campo rejeicoes_grade_baixa nos JSON. A planilha inclui o setor da empresa, origem/destino, cargo e motivo da atribuicao.

Regere as tres Companies com o V2.2. Desative os SCS antigos que apresentam rotas de FIAT/MC Equipamentos expedindo bobinas ou Carmoprem expedindo cimento; nao basta substituir o executavel. Os testes automatizados sao sinteticos e nao certificam todas as empresas reais; audite os arquivos produzidos e teste no ETS2.

---

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
