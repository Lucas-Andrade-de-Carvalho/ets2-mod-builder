# Diagnostico das tres auditorias reais — 22/10/2026

**Fontes:** `AUDITORIA_RBR(2).json`, `AUDITORIA_ELDORADO(2).json`,
`AUDITORIA_MINAS_GERAIS(2).json` enviados pelo cliente. Este documento
analisa os relatorios; NAO inspeciona diretamente os SCS resultantes
nem significa homologacao no ETS2.

## Interpretacao correta da cobertura

| Mapa | Empresas na DEF | Editor | Cargas com pares SCS | Cadeias economicas | Candidatas ETS2 | Empresas sem atividade identificada | Empresa com permissão herdada sem classificação |
|---|---:|---:|---:|---:|---:|---:|---:|
| RBR | 642 | 995 instancias | 24/24 | 22/24 | 22/24 | 458 | 132 |
| Eldorado | 214 | 646 instancias | 15/24 | 5/24 | 5/24 | 193 | 90 |
| Minas Gerais | 370 | **0 instancias** | 22/24 | 21/24 | **0/24** | 232 | 57 |
| TOTAL | 1.226 | 1.641 | 61/72 | **48/72** | **27/72** | **883** | **279** |

**Nao confundir**: o contador de 279 mostra SOMENTE empresas desconhecidas
que tiveram permissoes herdadas preservadas sem evidencia. O total de
empresas sem atividade identificada na DEF e 883. A falta de classificacao
nao prova que sejam empresas realmente incompativeis: pode ocultar
fornecedores, compradores e lojas esquecidas.

**Nota:** `empresas_compativeis_esquecidas=[]` vale somente para
empresas que o classificador ja reconheceu. Nao e prova de cobertura
da DEF inteira. O valor zero de editor em Minas Gerais e limitacao da
DEF efetivamente entregue, nao prova de que o mapa nao tenha cidades.

## Lacunas por mercadoria

- **RBR:** carga3 (adubo) e carga23 (sorgo) possuem OUT e IN registrados,
  mas nao existe par com ambos os lados comprovados pela politica.
  Adubo: 15 origens registradas, nenhuma aceita economicamente;
  sorgo: 45 origens registradas, nenhuma aceita economicamente.
- **Eldorado:** apenas carga3 (adubo) e carga17–carga20 (racao) tem
  cadeias economicamente justificadas. Sem par SCS distinto:
  carga5 algodao, carga6 cimento, carga9 bobinas, carga10/11 cimento,
  carga13 tijolos, carga16 paletes, carga23 sorgo, carga24 coco.
  Demais cargas com par SCS, mas sem evidencia economica suficiente:
  carga1 milho, carga2 soja, carga4 madeira, carga7 batata,
  carga8 laranja, carga12 cerveja, carga14/15 granito,
  carga21 soja alto, carga22 milho alto.
- **Minas Gerais:** carga5 algodao sem nenhum IN/OUT; carga24 coco
  tem 6 destinos, mas nenhuma origem. Carga23 sorgo possui pares SCS
  sem origem economicamente comprovada. As outras 21 cargas tem pares
  economicos, mas ZERO pares editor devido a falta de arquivos editor
  na DEF analisada.

## Problemas de identidade economica concretos

No RBR, varias origens de `carga3` ainda estao como `desconhecida`
apesar de o nome indicar possivel atividade agro: `agro_capim`
(nome publicado `Agro Capim`), `cimoagro` (`Cimoagro`),
`mt_agrogarca` (`AgroGarças`) e `viasafra` (`Via Safra`).
**Nao classificar todos como loja de adubo automaticamente**: agro
tambem pode significar servicos, maquinario, industria ou producao.
`agromecvo` mostra o nome `Agromec` e exemplifica essa ambiguidade.

## Correcao segura aplicada no codigo

`politica_economica.py`: sorgo (alimento animal) pode sair de
agropecuarias, entrar em estabelecimentos pecuarios e em fazendas
que tenham evidencia de compra de racao/sorgo na DEF. Fazenda
sem evidencia de criacao NAO recebe nem produz sorgo ficticio.
`gerador.py`: resumo de auditoria agora diferencia desconhecidas
na DEF inteira de empresas com permissoes herdadas pendentes
e identifica mapas sem `editor`.

## Condicoes para cobertura final

1. Identificar o setor de cada empresa que tenha indicios crediveis
   de fornecer/receber alguma das 24 cargas; nao inferir a partir
   somente de `agro`, `log`, `material` ou outro trecho ambiguo.
2. Em Minas Gerais, obter os arquivos `editor` reais das unidades
   ou a DEF completa; sem eles nao e possivel garantir cidades/prefabs.
3. Para cada uma das 24 cargas POR mapa, exigir produtor e comprador
   distintos e economicamente fundamentados; se o mapa nao contiver
   cadeia legitima, registrar ausencia ao inves de forcar 72/72.
4. Reauditar SCS gerados e documentar empresa+cidade+IN/OUT/mercadoria,
   seguindo de testes em ETS2 para aparicao, coleta e entrega.

**Estado real: auditoria executada, correcoes parciais publicadas,
cobertura economica e territorial integral NAO comprovada.**