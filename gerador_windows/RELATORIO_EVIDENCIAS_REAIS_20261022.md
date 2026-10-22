# ETS2 Company Logistics — Evidências reais e bloqueios de homologação (22/10/2026)

## Fontes recuperadas (sha256 verificado contra auditoria V3)

| Mapa | DEF original | SHA-256 |
| --- | --- | --- |
| Minas Gerais | `def_compan (Minas Gerais)y(1).zip` | `f653950fc8bae3a75211cc7075f9c4f5de0e4f16ab42d472d266b2fd58fc38c1` |
| Eldorado | `def_company (Eldorado)(1).zip` | `36c56d80dc8ffa483764823531aa1ded2f4ee93077dbe52044a9df872bd2416e` |
| RBR | `def_company (RBR)(1).zip` | `13e2426f3f5d26c7f11ffd4f35eff90bc29d0cc6feb70dc80f8098f1de60ed0e` |

O TXT original traz carga1–carga24, sendo `carga24 = Coco`. Os SCS independentes mais antigos chamados `ETS2_*_COMPANY_FINAL.scs` contêm apenas 23 cargo_data e NÃO são prova de 24/24.

## Última auditoria real disponível — anterior às melhorias desta branch

Relatórios analisados: `AUDITORIA_MINAS_GERAIS(3).json`,
`AUDITORIA_ELDORADO(3).json`, `AUDITORIA_RBR(3).json`.
Estes valores não devem ser apresentados como resultados de nova execução.

| Mapa | Empresas na DEF | Sem classificação na matriz | Sem classificação entre empresas revisadas | Cadeias economicamente demonstradas | Cadeias candidatas ao teste |
| --- | ---: | ---: | ---: | ---: | ---: |
| Minas Gerais | 370 | 229 | 54 | 22/24 | 0/24 |
| Eldorado | 214 | 184 | 87 | 8/24 | 8/24 |
| RBR | 642 | 418 | 103 | 24/24 | 24/24 |

Esses dois contadores de desconhecidas têm universos DIFERENTES: matriz de todas
as empresas versus empresas com permissões auditadas. Não os misturar.

A auditoria de Minas Gerais não identificou `company_def` editor com `city`
e `prefab` suficientes; nenhum par territorial foi comprovado.
A de Eldorado carece de origem/destino econômicos para várias mercadorias,
e a do RBR ainda tem unidades sem classificação documentada.

## Correções implementadas na V3 (código e regressões)

- IDs completos do Librelato `carga1`–`carga24` viraram prova exata de categoria
  somente quando encontrados no IN/OUT da DEF; nunca inferir a partir de nome livre.
- `company_permanent` sem IN/OUT participa do inventário completo.
- As contagens de empresas e cidades usam a MESMA atividade da matriz documental.
- Editor vazio, ou arquivo cujo nome imita cidade, não produz cidade/prefab candidato.
- Pareamento econômico com editor requer documentação `company_def` de cidade
  e prefab em origem e destino; esse pareamento ainda não prova jogabilidade.
- A empresa compatível sem editor válido BLOQUEIA a bandeira de cobertura
  territorial integral, mesmo quando as 24 cargas têm alguma rota.
- `csnarcos` e variantes descrevem extração de calcário/brita na DEF MG,
  e não fornecimento de bobinas/placas de granito para este catálogo.
- `casabatata`, `jmbebidas`, `batatfazpgra` e `araragrao` têm regras
  limitadas à mercadoria documentada na DEF e à direção correspondente.
- Redes alimentares claramente identificáveis podem receber as cargas compatíveis,
  sem serem promovidas a produtoras.

Referência externa para CSN em Arcos:
https://www.csn.com.br/quem-somos/grupo-csn/unidades-fabris-csn/
e https://www.csn.com.br/cimento/

## O que falta para uma certificação comercial real

1. Executar a **mesma compilação aprovada** sobre os arquivos reais: MOD,
   DEF1, DEF2, TXT, as 3 DEFs e as 3 Companies **exatamente usadas pelo
   cliente**. Repetir auditoria e validar hashes para registrar o novo estado.
2. Resolver economicamente toda empresa ainda desconhecida com evidência
   identificável ou marcá-la justificadamente como incompatível (não inventar).
3. Confirmar todos os pontos de carga/descarga e prefabs de MG/Eldorado/RBR;
   uma cidade existente no mapa NÃO nasce de nome de arquivo.
4. Verificar as 24 cargas e body_types nos originais do Librelato; não usar
   pacote antigo de 23 cargas como fonte da 24ª.
5. Validar no jogo *ao menos* 72 cadeias (24 x 3 mapas) com origens e destinos
   distintos, e **adicionalmente cada unidade/empresa compatível** que a meta
   de cobertura total exige. Verificar ofertas, carroceria, coleta, entrega,
   renderização, pagamento e `game.log.txt`.
6. Comparar a matriz final com todas as empresas/cidades; reprovar se houver
   permissões herdadas injustificadas ou unidades economicamente compatíveis
   sem IN/OUT.

**Status da certificação ETS2: NÃO HOMOLOGADO.** O workflow Windows prova
apenas integridade do software nos testes executados; não executa o jogo.
Nunca classificar como 100% homologado com base somente em CI ou CSV.
