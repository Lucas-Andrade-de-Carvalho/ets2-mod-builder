# Correção das lacunas documentais — auditorias (4), 22/10/2026

## Arquivos analisados
- `AUDITORIA_RBR(4).json`
- `AUDITORIA_ELDORADO(4).json`
- `AUDITORIA_MINAS_GERAIS(4).json`

São relatórios de uma execução **anterior** à revisão aqui documentada; não equivalem a um novo ensaio do gerador contra a DEF e Company atuais.

## Achados verificáveis

| Mapa | Carga | Tipo | Antes | Tratamento |
| --- | --- | --- | --- | --- |
| Eldorado | carga16 | palete | 10 empresas expedidoras, **0 recebedoras** | **BUG CONFIRMADO E CORRIGIDO NO MOTOR**: `empty_palet` agora equivale a palete; `spani` recebe e expede `empty_palet` na DEF, `kaarfor2` expede e `madereira` movimenta em ambos os sentidos |
| Eldorado | carga5 | pluma de algodão | 0 origens e 0 destinos | **SEM SUPORTE DOCUMENTAL PARA CRIAR FORNECEDOR**: não há `cotton`, `cott_seed`, `pluma` na lista IN/OUT analisada, nem unidade identificada como produtora de pluma. Não confundir roupa ou sementes com pluma |
| Minas Gerais | carga5 | pluma de algodão | 0 origens e 0 destinos | **SEM SUPORTE DOCUMENTAL**: não adicionar automaticamente às fazendas genéricas |
| Minas Gerais | carga24 | coco | 0 origens e 10 compradores (supermercados) | **FALTA ORIGEM**: sem `coco/coconut` no OUT das Companies analisadas; supermercado é comprador, não produtor. Sem fazenda/fornecedor de coco confirmado, NÃO inventar a origem |
| RBR | — | 24 cargas | sem falta de par IN/OUT | Preservar as cadeias documentadas; não significa frete testado no ETS2 |

### Correções no código
- `politica_economica.ALIASES["palete"]`: inclui `empty_palet`, `empty_palets`, `empty_pallet`, `empty_pallets` e `supaletes`. Esses identificadores são paletes vazios/de retorno; não são outras mercadorias.
- `politica_economica.decide`: permite palete **somente na direção original da DEF** para setores capazes de armazenar, devolver ou reutilizar paletes, inclusive supermercados e madeireiras. Continua proibindo tratar uma transportadora como produtora.
- Em Minas, `abcatacado` contém `supaletes` no OUT original; isso é saída de paletes, **não** comprovação de fornecimento de coco.
- Testes direcionais de `spani`, `kaarfor2`, `madereira`, `abcatacado`, transportadora e espécies algodão/coco; teste de ponta a ponta inspeciona os novos `.sii` no SCS e a existência de par distinto.

## Como confirmar a melhoria com arquivos reais

1. No executável mais recente, abra os mesmos arquivos **MOD, DEF 1/2, TXT, DEF mapa e Company anterior** utilizados nos relatórios (4).
2. Execute **AUDITAR/CORRIGIR SCS EXISTENTE** de Eldorado usando a mesma DEF. Não sobrescreva as entradas.
3. Confira `AUDITORIA_ELDORADO.json` → `rotas_depois.carga16`: deve haver ao menos uma origem e um destino, com par de empresas distintas. `QUALIDADE_LOGISTICA_ELDORADO.json` deve apontar os nomes e as razões.
4. Se não estiver documentado ou houver erro de importação, **não declarar corrigido no ETS2**. Guarde a auditoria e `game.log.txt` para diagnóstico.

## Limites que impedem prometer 100% automaticamente
- A geração de paletes foi comprovada por teste sintético do SCS, mas o próprio **ETS2 não foi executado** nesta sessão.
- Para as outras três lacunas não há base documental suficiente para atribuir uma fazenda/empresa à produção de algodão ou de coco; uma oferta fabricada para satisfazer uma contagem de 24/24 seria enganosa.
- Minas Gerais permanece sem `company_def` com cidade+prefab nos arquivos disponíveis. Nada aqui inventa essas informações.

**Estado:** correção codificada para 1 cadeia; **3 lacunas econômicas exigem fontes adicionais ou seleção explícita, baseada em evidência, de um fornecedor compatível**. Nenhum SCS real novo foi produzido dos três JSON isolados, pois JSON de auditoria não contém todas as entradas binárias da Company.
