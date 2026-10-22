# Company Logistics Ultimate V3.0 — motor econômico profissional

## Objetivo: a necessidade do comprador determina o frete

Esta versão preserva o funcionamento offline, os 7 arquivos originais do Librelato e as DEFs Minas Gerais, Eldorado e RBR, e acrescenta um **único motor de decisão econômica** usado tanto na geração quanto na correção de Companies existentes.

Fluxos reais exemplificados:

- **Obra** contrata o motorista para retirar **cimento ou tijolos** em uma loja de materiais de construção; a obra recebe (IN), e a loja fornece (OUT). Uma fábrica de pré-moldados recebe cimento, não vira automaticamente cimenteira.
- **Fazenda** contrata o motorista para retirar **adubo/ração** em agropecuária; culturas agrícolas compram fertilizante e criação de animais compra ração.
- **Fazenda que colheu milho/soja/sorgo** fornece à cooperativa/silo ou fábrica de ração, conforme atividade/evidência dos registros.
- **Produtor de batatas/laranjas** entrega em supermercado, CEASA ou hortifruti, nunca em bananal apenas por ser plantação.
- **Supermercado** solicita reposição de **cerveja** à Ambev, não a uma transportadora sem papel comprovado de fornecedor.
- **Siderúrgica** fornece bobinas para indústria automotiva/metalúrgica. A Fiat não passa a fabricar bobinas apenas porque havia OUT assim no mapa.
- **Madeireira** fornece madeira e paletes, enquanto **recicladora** recebe paletes.
- **Pedreira/marmoraria** fornece granito para beneficiamento ou construção em contexto compatível.

## O que é verificado

1. **23 cargos e carrocerias originais**: cargo_data e body_types verificados contra carrocerias próprias no MOD, DEF 1 e DEF 2; identifica Grade Alta, Grade Baixa e outras carrocerias presentes.
2. **Todos os IDs de empresas encontrados na DEF do mapa**: decisões IN/OUT separadas por mercadoria e papel (produtor, comprador, revendedor, armazenador), sem corte arbitrário por número de empresas.
3. **Unidades/cidades**: lista cada `def/company/<empresa>/editor/<cidade>.sii`; extrai cidade do campo SII ou nome do arquivo. Em ETS2 as permissões IN/OUT são geralmente compartilhadas pela definição da empresa; não implica que o prefab da cidade esteja funcionando. A confirmação de cada prefab exige dados completos do mapa e teste no jogo.
4. **Bloqueios**: no modo Gerar versão profissional, se faltar alguma cadeia 23/23, ou restar empresa de ramo desconhecido mas com evidência de mercadoria relevante, não publica SCS com aprovação enganosa. Gera JSON, CSV de lacunas e explicações. Não inventa cargas.
5. **Correção da Company existente**: botão 3 lê a Company atual e o DEF real, exige também MOD+DEF 1+DEF 2 para validar body_types, percorre arquivos IN/OUT, preserva o SCS original, remove incompatibilidades claras e acrescenta permissões justificadas; produz relatório antes/depois das 23 cargas, inventário de todas as empresas e cidades, registro de decisões e pendências.
6. **Resultados em CSV**: `*_EMPRESAS_E_CIDADES.csv` com as unidades detectadas, `*_EMPRESAS_SEM_CARGA_OU_SETOR.csv` com as possíveis lacunas, `COBERTURA_EMPRESA_CIDADE_*.csv` no fluxo de auditoria, e JSON detalhados.
7. **Sem perda de originais**: nunca altera nenhum ZIP/SCS de entrada e mantém hashes SHA-256 para rastrear fonte dos resultados.

## Escolher procedimento

- **Já tem Companies e quer apenas corrigir?** Selecione a Company existente de cada mapa, as DEFs dos mapas e os três originais do Librelato. Escolha **Todos os 3 mapas** e depois **3. AUDITAR / CORRIGIR SCS EXISTENTE**. É o caminho mais indicado para preservar as rotas válidas.
- **Quer criar novas Companies?** Escolha **2. GERAR COMPANY(S) SELECIONADA(S)**, após informar os 7 arquivos originais. A geração exige cadeias economicamente consistentes para todas as 23 cargas, não uma ligação fictícia.
- **Quer diagnosticar antes sem fazer alteração?** Selecione **Apenas auditar, sem gerar SCS**, e botão 3; ou botão 1 para diagnosticar arquivos de mapa.

## Limites que impedem afirmar perfeição sem teste

A ferramenta não pode deduzir com garantia absoluta o ramo real de empresas com identificadores obscuros nem confirmar se determinado prefab realmente está carregado numa cidade. A política é **não inventar**: empresas não reconhecidas com mercadorias relevantes bloqueiam a publicação de um SCS apresentado como completo, e o auditor marca pendências. Mesmo 23/23 e cobertura IN/OUT por empresas não substituem teste no ETS2, conferência do `game.log.txt`, versões do mapa, ordem de mods e configuração real das carrocerias. Para resolver pendências, revisar o CSV e fornecer os identificadores reais das empresas/cidades.

A V3.0 é uma evolução técnica comprovável por testes automatizados; **não afirmar cobertura total real dos três mapas antes de executar com os arquivos do usuário e validar o jogo**.

---

# ETS2 Company Logistics Ultimate V2.5 — Auditor de Companies existentes

## Novo método: você entrega as Companies atuais, não precisa recriar do zero

Agora o programa possui o botão **3. AUDITAR / CORRIGIR SCS EXISTENTE**. Ele aceita o SCS que você já usa no ETS2 para Eldorado, Minas Gerais ou RBR e a DEF original correspondente (para comprovar a atividade de cada empresa). O arquivo original permanece INTACTO. O resultado é outro SCS com sufixo `_AUDITADA_V25_<hash>.scs`, acompanhado de JSON/CSV de cada decisão.

### Como usar

1. Baixe o EXE da última compilação do GitHub Actions, extraia e abra a versão V2.5.
2. Escolha **Somente Eldorado** ou **Todos os três mapas**, conforme o que quer revisar. Se a versão do Minas está boa, selecione somente o Eldorado.
3. Selecione o ZIP **DEF do mapa** e o arquivo **Company EXISTENTE (.scs)** que já usa nesse mapa. Para três mapas, informe os seis arquivos.
4. Escolha a pasta de saída. Selecione **Auditar e corrigir SCS EXISTENTE**, ou, para apenas investigar, **Apenas auditar sem gerar SCS**.
5. Clique em **3. AUDITAR / CORRIGIR SCS EXISTENTE**. O EXE pode levar tempo conforme o número de arquivos da Company. A janela não trava.
6. Veja **AUDITORIA_ELDORADO.json** e **AUDITORIA_ELDORADO.csv**. Cada permissão tem empresa, ramo classificado, IN/OUT, carga, arquivo, motivo, confiança e decisão: MANTER, REMOVER, REMOVER_DUPLICADO, ADICIONAR ou REVISAR.
7. O SCS novo não sobrescreve o anterior. Use o corrigido somente após conferir pendências e testar no ETS2 com cada carroceria. Deixe a antiga desativada para evitar sobreposição.

### Política de correção

- Mantém toda permissão cuja origem ou destino seja compatível com o ramo da empresa, conforme o motor econômico do mapa.
- Remove só incompatibilidades de empresa com ramo **identificado com confiança**. Por exemplo, Fiat não é origem de bobinas, bananal não recebe batatas e transportadora não fabrica cerveja.
- Elimina permissões ativas duplicadas para a mesma carga, empresa e direção.
- Detecta empresas do mapa sem a carga do Librelato e **acrescenta** a permissão quando a DEF original e o setor comprovam a função econômica. Não tenta inventar fornecedores para obter 23/23.
- Se o ramo não puder ser interpretado com segurança, mantém a configuração existente e marca **REVISAR**. Isso é importante: auditoria conservadora não deve eliminar fretes bons por um falso positivo.
- Preserva byte a byte o conteúdo dos arquivos internos não alterados (incluindo manifest, editor e cargo_data) e preserva o SCS original separado.
- Contabiliza antes/depois os 23 tipos de carga, indicando se há ao menos uma empresa OUT e uma IN diferentes; isso ainda não substitui validar disponibilidade e prefabs no ETS2.

### Limite de qualidade

O programa é **offline** e audita o que os arquivos efetivamente demonstram. Uma empresa com ID obscuro e sem evidência econômica na DEF continua requerendo verificação humana. A mesma empresa pode aparecer em muitas cidades; o auditor atua sobre a definição da empresa, enquanto identificar as instâncias de cidade e seus prefabs exige também as definições completas do mapa e teste no jogo.

**Não existe homologação 100% automática a partir apenas do nome da empresa.** Se o JSON apresentar pendências `REVISAR` ou alguma carga sem par OUT/IN, não entregue ao cliente como versão definitiva. Traga o relatório para avaliação individual.

### CLI para automatizar revisões no Windows

Somente Eldorado:

```powershell
ETS2_Company_Gerador.exe --cli --audit-existing --only-eldorado --existing-eldorado "Eldorado_Antiga.scs" --eldorado "def_company (Eldorado).zip" --output "D:\Auditadas"
```

Para só inspecionar, sem criar .scs corrigido, inclua `--audit-only`.

A opção tradicional de **gerar Company do zero** permanece no programa. A auditoria de Companies prontas é um fluxo novo e independente.

---

## Versão V2.4 — 23/23 cargas, Grade Alta e Grade Baixa, com verificação individual

**Regra obrigatória no modo Somente Eldorado:** a Company somente é publicada se cada uma das 23 cargas da lista original tiver (a) uma empresa de origem/OUT com justificativa econômica, (b) uma empresa de destino/IN com justificativa, (c) ao menos um par origem-destino de empresas diferentes e (d) cargo_data e body_types validados com as carrocerias originais. A classificação da carroceria vem de body_types nas DEFs originais; além de Grade Alta e Grade Baixa, há cargas que podem exigir hopper/graneleiro.

O programa **não deve simular aleatoriamente** a falta de uma empresa compatível. Se a DEF do Eldorado não tiver evidências suficientes, ele interrompe a geração SEM criar um SCS novo e grava:

- Eldorado_COBERTURA_23_CARGAS.json (23 mercadorias, origens, destinos, carroceria, evidências, candidatos para revisão)
- Eldorado_COBERTURA_23_CARGAS.csv (mesmas informações em tabela)
- Eldorado_COBERTURA_INCOMPLETA.txt (quais cargas faltam e por quê)

Se uma Company Eldorado antiga estiver na pasta de saída, ela **continua antiga**; o gerador não remove arquivos do usuário automaticamente. Nesse caso não use o SCS antigo nem o entregue ao cliente. Compartilhe o JSON e o TXT de lacunas para uma revisão pontual das empresas/atividades reais do mapa e do reboque. A ausência de compatibilidade documental não autoriza inventar rotas.

Quando o relatório indicar **23/23** com todas as categorias e carrocerias, a etapa de análise estrutural estará aprovada. Ainda será preciso verificar ofertas no ETS2 e game.log.txt antes da entrega ao cliente. As Companies de Minas Gerais e RBR não são reprocessadas no modo exclusivo do Eldorado.

---
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


## V3.0 — Cargas reais detectadas no MOD/DEF1/DEF2 (sem cadastro manual)

**A antiga secao Gerenciamento de Cargas foi retirada.** Nao e necessario
cadastrar mercadorias pela interface nem preencher um catalogo JSON.

### Novo procedimento

1. Forneca o MOD principal do reboque atualizado, DEF Company 1 atualizada,
   DEF Company 2 atualizada e o TXT que explica cada carga (carga1, carga2, ...).
2. O programa le os registros cargo_data encontrados nos tres SCS. IDs
   adicionais no formato carga24, carga25 etc. so sao reconhecidos se existirem
   nos arquivos reais e forem descritos no TXT. IDs de mercadorias de outros
   reboques nao sao incorporados automaticamente.
3. A compatibilidade e apurada pelas definicoes de body_types e pelas carrocerias
   efetivamente presentes no material original. O programa nao cria cargo_data ficticio.
4. Novas cargas sem regras IN/OUT economicamente verificadas sao sinalizadas
   como PENDENTES e nao recebem empresas inventadas automaticamente.
   A atualizacao das politicas economicas deve ocorrer com base nas DEFs reais
   dos mapas e na explicacao da mercadoria.
5. Apos conferir politicas e classificacao, use Gerar ou Auditar/Corrigir.
   O SCS original nunca e sobrescrito.

### Auditoria segura

Para carga adicional ao conjunto original, informe tambem o TXT no formulario
ou --txt no CLI de auditoria. Sem texto correspondente, a analise e bloqueada
para evitar considerar mercadoria nao identificada como correta.

As pendencias de classificacao nao equivalem a erros: apenas inconsistencias
comprovadas justificam remocao automatica. Prefab/cidade exige verificacao
independente dentro do jogo, mesmo quando existe arquivo editor.

### Testes

Execute: python -m unittest discover -s gerador_windows -p test_*.py -v

O GitHub Actions compila o EXE e executa testes sinteticos. Dados reais e
testes no ETS2 continuam obrigatorios para homologacao.

## Correção da auditoria — revisão de 2.350 ocorrências

Os JSONs reais de Minas Gerais, RBR e Eldorado mostraram 2.207 permissões
herdadas em empresas cujo ramo econômico não pôde ser concluído, além de
143 casos cujo ramo foi reconhecido, mas a mercadoria não ficou comprovada.

**Correção estrutural:** o auditor agora usa `PRESERVAR_SEM_EVIDENCIA` para
cada permissão herdada de empresa não classificada, preservando byte a byte
o arquivo. Esses registros continuam rastreáveis em `AUDITORIA_*.json`
e `AUDITORIA_*.csv`, mas não são contabilizados como erros individuais.

- `pendencias_revisao`: somente decisões `REVISAR` que exigem checagem
  direta; NÃO inclui automaticamente todas as permissões herdadas.
- `permissoes_sem_evidencia_preservadas`: associações antigas NÃO validadas;
  não equivalem a associações aprovadas nem comprovadamente erradas.
- `empresas_classificacao_pendente`: número de empresas distintas
  envolvidas nessas associações, que precisa de identificação de ramo.
- `cargas_sem_rota_validada`: mercadorias sem par origem/destino
  distinto segundo o SCS auditado.
- `RESUMO_VALIDACAO_*.txt`: totais separados por mapa e aviso de
  homologação pendente.
- `PENDENCIAS_CLASSIFICACAO_*.csv`: fila única por empresa, sem 10 a 15
  mensagens repetidas para cada unidade.
- Status `PENDENTE_VALIDACAO_ECONOMICA`: SCS de saída é uma revisão técnica
  e NÃO pode ser apresentado como entrega homologada ao cliente.

**Limite inevitável:** uma DEF que só contém um identificador obscuro
não fornece evidência suficiente para declarar uma empresa como produtor,
comprador ou revendedor de todas as mercadorias. Eliminar a incerteza
exige examinar e confirmar a DEF completa, as companhias e o
funcionamento real no ETS2. O programa nunca deve ocultar esse bloqueio
nem distribuir cargas aleatoriamente apenas para zerar pendências.


## Verificacao dos tres SCS originais com TXT (24+ mercadorias)

Selecione somente **MOD principal**, **DEF1**, **DEF2**, **TXT atualizado**
e **pasta de saida**. Clique em **1. DIAGNOSTICAR LIBRELATO / MAPAS**.
As DEFs de Minas Gerais, Eldorado e RBR agora sao **opcionais apenas
para o diagnostico tecnico**; se forem informadas, tambem serao
inspecionadas. O aplicativo gera
`DIAGNOSTICO_LIBRELATO_CARGAS_ORIGINAIS.json` na pasta de saida.

O arquivo registra: hashes SHA-256 dos tres SCS, numero de arquivos DEF,
todos os cargos encontrados, nome exato retirado do TXT, categoria economica,
body_types, carrocerias identificadas, origem da definicao e possiveis conflitos.

Copias repetidas de uma mercadoria com SHA diferentes mas mesmos body_types
sao relatadas como avisos: podem ter parametros diferentes, exigindo checagem.
Body_types divergentes, carga ausente ou TXT incompleto geram resultado
**BLOQUEADO**. O sistema NAO edita os tres originais.

Esse diagnostico nao verifica sozinho a existencia de prefabs, o mercado
de fretes ou o comportamento no ETS2. Para completar a auditoria de MG,
RBR e Eldorado, ainda e necessario fornecer DEFs e Companies de cada mapa.

### Diagnostico independente pelo terminal do Windows

Para conferir os 3 SCS e as 24 cargas **antes** de fornecer as DEFs dos
mapas, use o executavel compilado em modo CLI:

```powershell
.\ETS2_Company_Gerador.exe --cli --diagnose-librelato --mod "Librelato tr adson.scs" --def1 "Def Company 1.scs" --def2 "Def Company 2.scs" --txt "cargas reboque limeira.txt" --output "resultado"
```

A verificacao falha com codigo diferente de zero se houver problemas
tecnicos conhecidos e deixa o relatorio JSON com os detalhes. Nao tenta
gerar Companies, nao altera SCS originais e nao exige mapa instalado.

**Gerar e Auditar/Corrigir** continuam a exigir as DEFs dos mapas escolhidos.
Na auditoria, o TXT e obrigatorio porque a identificacao das cargas
adicionais depende da especificacao recebida. O diagnostico tecnico
nao prova fretes jogaveis nem viabilidade economica de empresas.

## Auditoria de qualidade logistica por carga (etapa de homologacao)

A partir da versao refinada da V3.0, **Auditar/Corrigir** tambem escreve:
- `QUALIDADE_LOGISTICA_<MAPA>.json`: evidencia de setor/produto,
  fonte e destino, vagas de transporte existentes no SCS e candidatos a
  teste fisico no ETS2.
- `CADEIAS_COMPROVADAS_<MAPA>.csv`: um registro por carga com pares
  cadastrados, pares sustentados pela atividade economica, pares cuja
  origem e destino tem `editor` e bloqueios de cada cadeia.

**Definicoes rigorosas:**
1. `total_pares_no_scs`: pares de empresas IN/OUT diferentes,
   nao significam fretes verdadeiros; podem incluir permissoes antigas
   preservadas sem evidencia.
2. `pares_economicos_distintos`: existe produtor/fornecedor + comprador
   com identificacao de setor inequivoca e regra da mercadoria.
3. `pares_com_editor_em_ambas_empresas`: a DEF informava instancia
   editor para ambas as empresas. E apenas um **candidato** a teste,
   nao comprova conexao no mapa, disponibilidade nem distancia.
4. `homologado_no_ets2` permanece `false` sem uma verificacao
   documentada no jogo real; o gerador nao deve inferir esse status.

A aplicacao NAO cria fretes sem origem e destino economicos validos para
preencher contagem. Empresas ambiguas conservam as permissoes antigas,
mas elas nao entram nos totais de pares economicamente comprovados.

**Status de entrega:** codigo/EXE aprovado em testes sinteticos nao
equivale a `scs` do cliente homologado. Para fechar MG, Eldorado e RBR
comprove os hashes do MOD/DEF1/DEF2 e TXT, as DEFs dos tres mapas,
as Companies geradas, o `game.log.txt` e a aparicao dos fretes no jogo.


## Pré-homologação dos arquivos reais (3 mapas, 24 cargas)

Clique em **4. PRE-HOMOLOGAR OS 3 MAPAS** com os seguintes caminhos:
MOD principal, DEF Company 1, DEF Company 2, TXT de 24 mercadorias,
DEF de Minas Gerais, DEF de Eldorado, DEF de RBR, e as respectivas
Companies EXISTENTES. Informe game.log.txt se disponível e selecione
a pasta de saída.

Alternativamente, use `--cli --preflight-real` com os argumentos
`--mod`, `--def1`, `--def2`, `--txt`,
`--minas`, `--eldorado`, `--rbr`,
`--existing-minas`, `--existing-eldorado`,
`--existing-rbr`, `--output` e opcionalmente `--game-log`.

A verificação é **não destrutiva**: não sobrescreve os mods
e só audita as Companies existentes com `mode=auditar`.

A pasta de saída recebe:
- `01_LIBRELATO/DIAGNOSTICO_LIBRELATO_CARGAS_ORIGINAIS.json`,
  com identificações, hashes, cargo_data, body_types e conflitos.
- `02_MAPAS/AUDITORIA_*.json` e relatórios econômicos,
  um conjunto para cada mapa.
- `RESULTADO_PRE_HOMOLOGACAO.json`: RESUMO UNIFICADO. Bloqueia
  catálogo diferente de 24 cargas, empresas pendentes, ausência de
  rota economicamente fundamentada e ausência de candidatos com editor.
- `MATRIZ_ENSAIOS_ETS2.csv`: 72 linhas (3 mapas × 24 cargas)
  para registrar mercado, coleta, entrega, modelo visível e evidências.
- `COMO_HOMOLOGAR_NO_JOGO.txt`: procedimento de testes no jogo.

`PRONTO_PARA_TESTES_NO_JOGO` significa que a análise estática
passou, **não** que o mod está homologado. `game.log.txt` sem erros
também NÃO comprova que um frete apareceu ou foi concluído.

**Condição de homologação:** instalar a configuração do mod no ETS2
na versão exata do cliente, verificar IN/OUT válidos, conferir rota
acessível, frete disponível, carga visível, coleta, transporte e entrega,
com evidências e logs em cada mapa. Não há como realizar esses ensaios
a partir de arquivos SII ou do GitHub Actions.

Se o computador do cliente não estiver acessível, reportar
`HOMOLOGACAO_PENDENTE_DE_TESTE_REAL` e não apresentar resultados
como comprovados.
