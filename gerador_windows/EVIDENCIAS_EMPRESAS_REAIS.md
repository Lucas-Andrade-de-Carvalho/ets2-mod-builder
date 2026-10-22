# Empresas dos mapas: revisao economica rastreavel

Origem das identificacoes: campos `empresa` e `nome_exibido_def` do
`AUDITORIA_RBR(2).json` enviado pelo cliente. Evidencias externas
complementam a atividade de empresas reais, mas **nao comprovam**
que o prefab ou instalacao especifica do mapa seja acessivel no ETS2.

| IDs/nomes reais do relatorio | Papel aceito | Cargas do Librelato | Restricao | Evidencia |
|---|---|---|---|---|
| cimoagro / Cimoagro | agroinsumos | Adubo IN/OUT | Nao torna qualquer empresa `agro` uma distribuidora | https://www.cimoagro.com.br/sobre-nos/ |
| amaggi / AMAGGI | comercio_graos | Milho, soja e sorgo IN/OUT | Exige que a mercadoria conste na DEF original | https://www.amaggi.com.br/areas-negocio/commodities/ |
| g_cereal_rv, g_cereal_stb / Grupo Cereal | comercio_graos | Graos IN/OUT | Exige evidencia da mercadoria na DEF; unidade pode ter atividade especifica | https://www.grupocereal.com.br/ |
| grupo_p, grupo_p2 / Grupo Petropolis | cervejaria | Cerveja OUT | Nao autoriza alcool generico ou outras cargas | https://carreiras.grupopetropolis.com.br/content/O-Grupo/ |
| cercrystal / Cerveja Crystal | cervejaria | Cerveja OUT | Marca de cerveja nao torna todas as empresas de bebidas produtoras de cerveja | https://carreiras.grupopetropolis.com.br/content/O-Grupo/ |
| polimix1, polimix_rib / Polimix | concreteira | Cimento IN | Nao fabrica cimento na unidade sem evidencia adicional | https://polimixconcreto.com/ |
| nutrition / Trouw Nutrition | fabrica_racao | Racao OUT, graos IN | Nao distribui adubo apenas por trabalhar no agro | https://www.trouwnutrition.com.br/pt-br/ |
| raguife / Raguife Racoes | revenda_racao | Racao IN/OUT | Nao inclui sorgo ou adubo automaticamente | Nome exibido na DEF; tipo de varejo requer comprovacao adicional no mapa |
| batata_f, batata_ms1 / Batata Fazenda, Fazenda de Batatas | fazenda_batata | Batata OUT | Nao se converte em fazenda de soja ou de laranja | Nome publico da DEF |
| depos_ribas / Deposito Materiais de Construcao | materiais | Cimento, tijolos, madeira IN/OUT | Loja nao e obra, nem vende granito sem evidencia | Nome publico da DEF |
| guarezi_m / Guarezi Material de Construcao | materiais | Materiais compativeis IN/OUT | Sem outros produtos fora das 24 cargas | Nome publico da DEF |
| ms_alg_ib / Algodoeira Irmaos Burgel | beneficiadora_algodao | Pluma de algodao OUT | Pluma beneficiada nao e algodao bruto | Nome publico da DEF |
| bechara, moveis1, marcenaria1 / Fabricantes de moveis | fabrica_moveis | Madeira IN | Nao fabrica carga de toras/madeira a granel | Nome publico da DEF |
| mer_bh_itabi, compre_bem, martinmina / Supermercados e atacarejos | supermercado | Cerveja, hortifruti, coco IN | Nao e produtor de mercadoria sem OUT documentado | Nome publico da DEF |

## Erros anteriores efetivamente corrigidos

- O auditor confundia `Fazenda de Batatas` com dupla classificacao
  (fazenda + fazenda_batata), deixando a atividade `desconhecida`.
- O mesmo ocorria com `Material de Construcao` (obras + materiais).
  Agora a loja prevalece apenas quando o texto deixa isso claro.
- Industriais como beneficiadoras de algodao, moveleiras e concreteiras
  nao eram identificados, embora pudessem receber ou expedir
  uma das mercadorias solicitadas.
- Atacadistas de graos podiam ter a atividade indefinida; agora exigem
  identificacao nominal e mercadorias da DEF original.

## Pendencias que NAO devem ser marcadas como resolvidas

- Os 883 registros `atividade=desconhecida` nos tres mapas incluem
  dezenas/centenas de IDs sinteticos sem nome legivel na DEF analisada.
- O Eldorado possui varias empresas cujo ID sozinho nao demonstra setor.
- A DEF de Minas Gerais fornecida possui ZERO instancias editor; nao
  e possivel certificar cobertura por cidade com esse insumo isolado.
- Nao se pode inventar origem de coco/algodao ou destino para outra
  mercadoria apenas para alcancar 24/24 em cada mapa.
- Os totais apos a nova classificacao so poderao ser medidos ao
  reexecutar as tres auditorias nos dados originais do cliente.

## Politica de validacao

Caso a empresa seja desconhecida e nao haja setor explicitamente
comprovado, mante-la pendente; nao presumir producao a partir da
presenca de uma carga herdada da Company. A ausencia de correspondencia
no catalogo das 24 mercadorias pode ser legitima. O objetivo e
**cobrir todas as empresas comprovadamente compativeis**, nunca
forcar qualquer empresa ou cidade a trabalhar com cargas ficticias.