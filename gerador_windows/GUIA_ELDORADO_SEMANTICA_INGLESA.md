# Eldorado — tradução da DEF e logística econômica (motor isolado)

## Objetivo
Interpretar os 225 identificadores de cargas presentes na DEF original
`def_company (Eldorado)`, distinguir produtores, consumidores, comércio e
armazenagem e simular fretes coerentes do Librelato sem inventar empresas,
cidades, prefabs ou produtos de culturas diferentes.

As regras deste módulo não são ativadas na auditoria ou geração de Minas
Gerais e RBR. A Company anterior fica inalterada. Para aplicar a regra
ao Eldorado, **é necessário reauditar a Company do Eldorado** com a nova
compilação e salvar um novo SCS em outra pasta.

## Entregas adicionais da auditoria Eldorado
- `TRADUCAO_DEF_ELDORADO.csv`: ID original, tradução PT, direção IN/OUT,
  número de empresas da DEF em que aparece.
- `PERFIS_ECONOMICOS_ELDORADO.csv`: empresas com atividade definida por
  fluxo bruto, evidências e mercadorias de entrada/saída.
- Auditorias normais `AUDITORIA_ELDORADO.json`, `COBERTURA_MAXIMA_ELDORADO.csv`,
  `PAINEL_GERAL_LOGISTICA_V3.txt` e o novo arquivo SCS.

O glossário cobre os **225 nomes distintos de cargas identificados na DEF
original**; algumas possuem extensões de DLC que usam a tradução do ID-base.
Descrição em português não altera ID de carga do jogo.
Exemplos: fertilizer=adubo; tractors=tratores; big_bag_seed=sementes;
bois=gado vivo; leite=leite; potatoes=batatas; oranges=laranjas;
beans=feijão (não soja); rice=arroz (não milho); graos=grãos genéricos
(não espécie); nonalco_beer=cerveja sem álcool (não cerveja Librelato);
beverages=bebidas genéricas (não cerveja Librelato).

## Motor econômico: sentido do pedido de frete
- **Lavoura mista documentada**: plantou milho/soja? O OUT original deve
  demonstrar a espécie (milho, soja); adubo chega no IN da lavoura.
  Se a cultura é batata, somente batata sai. Sementes e tratores ajudam
  a reconhecer lavoura, sem comprovar uma colheita específica sozinhos.
- **Pecuária de corte / leite**: gado em OUT ou gado recebido e leite
  expedido caracteriza atividade pecuária. Recebe ração e sorgo; não
  expede milho, soja, coco ou pluma apenas por conter 'fazenda' no nome.
- **Canavial**: cana no OUT e canavazio no IN comprovam cana-de-açúcar.
  A propriedade recebe adubo, mas cana não vira soja/milho fictícios.
- **Comércio de insumos e grãos**: milho e soja documentados no IN não
  autorizam expedição se o OUT só declara 'graos' genéricos ou
  fertilizante. Revendas podem expedir o que a DEF realmente indica.
- **Armazém**: movimenta a mesma espécie no IN/OUT quando documentada.
- **Distribuidor de múltiplos produtos**: centro de expedição com
  dezenas de itens NÃO equivale a fazenda/fábrica de cada tipo.
- **Restante das empresas**: política econômica anterior conservada.
  Classes não identificáveis não são preenchidas por palpite.

## Evidência e confiança
- **DOCUMENTO**: o produto/espécie está literalmente em IN/OUT da DEF.
- **SIMULAÇÃO ECONÔMICA**: uma atividade demonstrada recebe insumo
  plausível (ração para pecuária; adubo para canavial) mesmo sem a mesma
  mercadoria original. Essa hipótese é rotulada nos relatórios.
- **NÃO COMPROVADO**: produto ou direção ausente e ramo ambíguo; evitar
  adicionar ou preservar frete contraditório.
- As adaptações regionais de pluma/coco continuam específicas do
  Minas/Eldorado, mas deixam de tratar pecuária como lavoura.

## Teste sugerido — sem regressões
1. Selecionar 'Somente ELDORADO' e 'Auditar e corrigir SCS EXISTENTE'.
2. Usar DEF do Eldorado, Company anterior e MOD/DEF1/DEF2/TXT
   do Librelato, mantendo os originais e escolhendo uma pasta de saída nova.
3. Comparar relatório novo com auditoria (7): cargas com OUT e IN,
   `carga9` (CSN → Ita Aços), setor das fazendas e agropecuárias,
   novas permissões de ração/sorgo e remoção de pluma/coco indevida.
4. Conferir o CSV de tradução das 225 mercadorias (nomes
   de ID em inglês são mantidos no próprio SCS).
5. Testar no ETS2 uma carga de cada categoria relevante e confirmar
   coleta, entrega, integridade do game.log e existência de ofertas.
   A auditoria não é homologação automática no jogo.

**Não espere que toda carga apareça simultaneamente no mercado**.
Os relatórios indicam combinações possíveis, não a frequência e a
oferta calculadas pela economia do ETS2. Lembre-se também de priorização
de mods e compatibilidade da carroceria.
