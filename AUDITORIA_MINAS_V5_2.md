# Diagnóstico MINAS e DEF Librelato — motor v5.2

Análise estática dos arquivos realmente fornecidos ao projeto, em 20/10/2026. Estes números descrevem **as definições**, não são confirmação do mercado de fretes dentro do ETS2.

## Escopo comprovado

- MINAS: **370 empresas**, **1.397 arquivos OUT** e **2.165 arquivos IN** (3.562 caminhos canônicos em `company/<empresa>/in|out/*.sii`).
- DEF do reboque: **23 cargos** enumerados em `cargo.librelato.sii`, com `@include "cargo/carga1.sui"` até `@include "cargo/carga23.sui"`.
- Arquivos `corn_b`, `cott_seed`, `potatoes_b`, `soybean_b` e `sugar_beet_b` estão no ZIP mas **não** constam do manifesto de 23 cargas. Não devem entrar na distribuição deste reboque só porque têm `cargo_data`.

## Caso de falha confirmada: cervejas

A DEF MINAS registra cada uma das marcas comerciais `amstel`, `antarctica`, `brahma`, `budweiser`, `devassa`, `heineken`, `schin` e `skol` em **6 empresas OUT** e **17 empresas IN**. Portanto, uma carga genérica "Cervejas" pode ser distribuída para essas empresas se as outras verificações de carroceria/setor forem respeitadas. Os `cargo:` que contêm somente `bebidas` não provam cerveja e não devem autorizar uma rota de cerveja.

Exemplos de expedidores com cerveja em OUT: `ambev`, `ebs`, `jjdistibuido`, `jmbebidas`, `modesto`, `rodowilson`. Esses IDs vêm da DEF, não são nomes inventados pelo motor.

## Mercadorias sem prova literal na DEF MINAS

- Cimento: **0 empresas OUT** e **0 IN** com `cimento` ou `cement`. Há outras mercadorias de construção (como `tijolos`, `pedra`, `calcario`, `brita`), mas isso não comprova cimento. Cargas 6, 10 e 11 devem permanecer sem rota até haver evidência adequada ou uma regra de inferência explicitamente aprovada.
- Bobinas: `chapaaco` e `ferroconst` aparecem em empresas, porém não são bobinas. Uma carga física de bobinas não deve ser deduzida automaticamente delas.
- Sorgo: há milho e soja, mas não sorgo literal. Não deduzir cultura específica de outras culturas.
- Pluma beneficiada: não identificada; algodão em caroço e sementes não a comprovam.
- `carga16` traz a descrição "Pallets Alto TESTE", sem especificar se movimenta paletes vazios ou mercadorias paletizadas. O rótulo é insuficiente para inventar o produto.

## Mudanças da v5.2

1. Reconhecimento documental de marcas de cerveja pela classe física cerveja (não por bebidas genéricas).
2. Determinação do catálogo **efetivo** de cargas por manifesto `@include`. Sem manifesto, procurar modelos em `vehicle/cargo/<id>/...`. Sem qualquer dessas provas, manter leitura ampla explicitamente diagnosticada.
3. Retirar as cargas extras do ZIP da distribuição e informar IDs excluídos no TXT.
4. Preservar empresas sem compatibilidade, neutralizar permissões antigas e exigir origem e destino diferentes.

## Limite desta auditoria

A evidência é dos arquivos de configuração. A confirmação de fretes disponíveis requer carregar o SCS com prioridade acima da DEF do mapa e dos overrides concorrentes, atualizar a economia, verificar `game.log` e conferir o mercado de fretes dentro do ETS2.
