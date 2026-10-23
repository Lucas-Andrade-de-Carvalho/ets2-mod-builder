# RBR — diagnostico e correcoes na auditoria (5)

## Dados da Company ANTES desta rodada

- 24/24 cargas com pelo menos uma origem e destino cadastrados
- 182 decisoes REVISAR, 54 MANTER_PLAUSIVEL, 129 permissoes antigas sem evidencia
- 252 empresas de ramo desconhecido na DEF; 116 empresas com pendencias na planilha
- 995 instancias editor detectadas; fretes ainda NAO HOMOLOGADOS dentro do ETS2

## Problemas identificados nos IN/OUT originais

1. **Extracao de madeira**: extracao2, extracao_ju, extracao_sb, extracao_sc e mt_extracao1 recebem maquinas Ponsse e expedem troncos. Company antiga possuia milho/soja no IN e racao no OUT. O gerador passou a identificar as extracoes pelo fluxo, neutralizar os fretes agricolas herdados sem suporte e preservar cargas de madeira.
2. **Postos de combustivel**: go_p_riobra (Auto Posto Rio Branco) e p_abobrao (Posto Abobrao) recebem diesel/gasolina/etanol e expedem tanque vazio/filtro usado. Nao podem receber cimento/tijolos como se fossem lojas de materiais. A classificacao agora reconhece a funcao pelos fluxos, mesmo com IDs abreviados.
3. **Fazenda AC**: o nome exibido AG - Armazenagem de Graos, com milho/soja em IN e OUT, indica silo/entreposto, nao producao agricola comprovada.
4. **Operadores de distribuicao**: GGR, GMP, MIT, TSB e Thunay recebem e expedem vestuario, eletronicos, pneus, embalagens, alimentos e adubo. O fluxo multi-setorial pode identificar centro logistico; os produtos da Librelato sao permitidos apenas na mesma direcao documentada.
5. **Portos**: pr_porto_pr (Porto Paranagua) movimenta cargas documentadas e nao as fabrica. Porto1 sem IN/OUT permanece pendente de evidencia.

## Escopo e protecoes

- As correcoes de setor foram implementadas no gerador, e testes de SCS verificam a neutralizacao de fretes contraditorios.
- O arquivo original da Company nao deve ser alterado; use Somente RBR e AUDITAR/CORRIGIR SCS EXISTENTE.
- A regra EXTRA de pluma/coco em fazendas sem OUT comprovado continua exclusiva de Minas Gerais e Eldorado; nao foi autorizada no RBR.
- Nao afirmar que a contagem de 182 revisoes caiu sem executar esta revisao sobre os MOD/DEF/Company originais do cliente. Os tres relatorios permitem diagnosticar, mas nao substituem os arquivos originais binarios.
- A manutencao de 24/24 pares deve ser confirmada nos relatorios DEPOIS de gerar a nova Company. Nao significa frete no mercado ou entrega feita no ETS2.

## Validacao

1. Em Somente RBR, carregue MOD Librelato, DEF Company 1/2, TXT, DEF RBR e Company RBR anterior.
2. Use AUDITAR/CORRIGIR SCS EXISTENTE. O programa produz uma nova Company, sem sobrescrever a original.
3. Confira AUDITORIA_RBR.json, COBERTURA_MAXIMA_RBR.csv, PENDENCIAS_CLASSIFICACAO_RBR.csv e QUALIDADE_LOGISTICA_RBR.json.
4. Confirme carga1..carga24 ainda com pares; analise as acoes REMOVER especificamente nas madeireiras e postos. Nao conclua que cada mercadoria foi homologada so pelo JSON.
5. Rode a pre-homologacao com o SCS recem-gerado e teste fretes de coleta e entrega dentro do ETS2 com game.log.txt.
