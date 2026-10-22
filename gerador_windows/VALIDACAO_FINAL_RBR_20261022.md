# Validação final RBR — protocolo executável (22/10/2026)

Este protocolo é a **última etapa técnica documentada antes de homologar no ETS2**, não um certificado automático. A mesma engine se aplica a Minas Gerais e Eldorado, mas o RBR pode ser validado **sozinho**.

## Corrigido no motor econômico

1. **IN/OUT e empresas fictícias**: a atividade é inferida por padrões de mercadorias e pelo nome, com prioridade à DEF original.
2. **Reclassificação comercial**: unidade com adubo no IN/OUT e ração no OUT, sem colheita, é fornecedora de insumos, não lavoura automaticamente (caso RBR Galo Prod. Agrícolas).
3. **Madeira industrial**: troncos/madeira serrada no IN e móveis no OUT representam fabricação de móveis (caso `extracao1`).
4. **Mineração e postos**: fornecedores de brita, calcário, minério ou combustível não expedem milho, soja, bobina ou granito **sem produto específico na DEF** (casos `mineracao1`, `go_petrobras`).
5. **Paletes de retorno**: `empty_palet`, `supaletes` e `paletev` são identificadores de paletes; conservam a direção do IN/OUT original.
6. **Sorgo**: quando uma fazenda colhe outros cereais, ou quando silo/cooperativa movimenta cereais, uma permissão `carga23` **já herdada** pode ser economicamente plausível. Essa permissão recebe o status `MANTER_PLAUSIVEL`: **não autoriza criar um novo sorgo em toda fazenda/silo**, não é tratada como cultura documentada e exige validação adicional.
7. **Limpeza cautelosa**: neutraliza cargas existentes comprovadamente incompatíveis, mas não remove automaticamente mercadorias de empresas ambíguas que ainda podem operar atividades múltiplas.

## Como validar somente o RBR pela interface

1. Abra `ETS2_Company_Gerador.exe`.
2. Selecione os arquivos **MOD Librelato**, **DEF Company 1**, **DEF Company 2** e **TXT das 24 cargas**.
3. Selecione **DEF do RBR** e **Company RBR EXISTENTE**.
4. Selecione uma **pasta de saída vazia**; não escolha a pasta de mods do jogo como origem e destino.
5. Na opção **Quais Companies deseja atualizar?**, marque **Somente RBR**.
6. Clique **3. AUDITAR / CORRIGIR SCS EXISTENTE**.
7. Confira `AUDITORIA_RBR.json`, `RESUMO_VALIDACAO_RBR.txt`, `QUALIDADE_LOGISTICA_RBR.json`, `COBERTURA_MAXIMA_RBR.csv`, `PENDENCIAS_CLASSIFICACAO_RBR.csv` e o arquivo `ETS2_RBR_AUDITADA_*.scs`.
8. **Antes de pré-homologar, altere o campo Company RBR EXISTENTE para o `.scs` CORRIGIDO que acabou de gerar.** Caso contrário, a auditoria conferirá de novo o arquivo antigo. Clique **4. PRE-HOMOLOGAR MAPAS SELECIONADOS** (ainda com **Somente RBR**). Esta ação é somente leitura, pode receber o `game.log.txt` e gera `MATRIZ_ENSAIOS_ETS2.csv` **com 24 linhas** para o RBR. A auditoria também cria `MATRIZ_ENSAIOS_ETS2_RBR.csv`.

As rotas da linha de comando também permitem validar só o RBR, com `--cli --audit-existing --only-rbr` ou `--cli --preflight-real --only-rbr`. Para esses modos basta fornecer `--mod`, `--def1`, `--def2`, `--txt`, `--rbr`, `--existing-rbr` e `--output`.

## Homologação do jogo — 24 ensaios

Para cada uma das **24 cargas**, em perfil dedicado com MOD/DEFs e mapa compatíveis:

- Verificar que uma empresa A possui realmente a origem e uma empresa **distinta** B o destino, no mercado de fretes.
- Verificar que a carga aparece visualmente no reboque e que o tipo de carroceria é compatível.
- Coletar e entregar a carga. Registrar as empresas/cidades exatas e algum arquivo de evidência (imagem ou gravação).
- Inspecionar `game.log.txt` do teste para erros de carga, empresa, prefab ou incompatibilidade de versão.
- Marcar o CSV do teste **somente depois** de observar o resultado dentro do ETS2. Teste de código não preenche esses campos.

Critério mínimo de aceitação do RBR: as 24 linhas registradas com frete visível, modelo correto, coleta e entrega reais, origem diferente do destino, evidência concreta e ausência de falha relevante atribuível à Company. A matriz é uma ferramenta de coleta de evidências e não confirma automaticamente nenhum resultado. Uma rota por carga não prova todas as combinações de empresas.

## Linha de base, antes desta versão

A `AUDITORIA_RBR(4).json` fornecida pelo cliente registrou:
- 642 empresas na DEF e 995 instâncias editor;
- 24/24 cargas com pelo menos um par IN/OUT cadastrado;
- 24/24 cargas candidatas ao teste no editor;
- **224 revisões pontuais** e **229 permissões antigas sem evidência**;
- nenhuma carga sem par cadastrado.

**Esses são números ANTERIORES às alterações deste documento.** Não se conhece ainda a recontagem real de pendências sem reexecutar a ferramenta sobre os mesmos arquivos de MOD/DEF/Company. O status `MANTER_PLAUSIVEL` também permanece pendência de prova, ainda que deixe de ser um erro categórico.

## Demais mapas

- **Eldorado**: corrigido o alias `empty_palet` da `carga16`; ainda falta comprovar disponibilidade de fornecedor de pluma de algodão para `carga5` dentro da DEF.
- **Minas Gerais**: nenhuma origem de coco `carga24` nem cadeia de pluma `carga5` apareceu na auditoria disponível; nunca inventar uma fazenda para fechar 24/24. A DEF enviada não continha os `company_def` com `city` e `prefab` suficientes para homologação territorial.
- Pode ser economicamente válido aceitar parceiros comerciais ou fornecedores secundários documentados pela DEF. Não é válido criar cidades, mercadorias ou origens não presentes nos arquivos.

## Estado da entrega

**EXE com testes automatizados, simulações de SCS e checklist RBR**: verificáveis no workflow de compilação.

**RBR 100% homologado no ETS2**: **PENDENTE** até execução com os arquivos reais completos e prova dos 24 fretes no jogo. Nem CI, relatório em JSON, presença de prefabs nem `game.log` limpo sozinhos comprovam entregas.
