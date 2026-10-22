# Company Logistics V3 — Entrega técnica candidata (22/10/2026)

## Escopo realmente concluído

- O programa audita **empresa por empresa** diretamente na DEF de cada mapa, inclusive empresas fictícias.
- Motor determinístico e offline: combina nome/identificador com entradas IN e saídas OUT originais.
- Reconhece produção e revenda agrícola, fábricas, intermediários, compras de materiais, supermercados e atividades sem ramo identificado.
- Em empresas fictícias ambíguas, converte somente a mercadoria já presente no IN/OUT da DEF para as variantes correspondentes do Librelato, preservando a direção original.
- Catálogo verificado nos arquivos originais de **carga1 a carga24**, incluindo coco.
- Mantém separados: permissões no SCS, permissões economicamente justificadas, pares com IN/OUT documentado, pares com setor confirmado, pares com editor cidade/prefab e fretes homologados dentro do ETS2.
- Preserva os arquivos originais, gera novo SCS e hashes dos arquivos, reauditoria opcional e relatórios por empresa.
- Nunca gera empresas, city/prefab, produtor de coco ou rota interurbana sem evidência.

## Fontes necessárias

1. MOD original do reboque Librelato.
2. DEF Company 1 e DEF Company 2 originais desse reboque.
3. TXT original com a descrição das cargas.
4. DEF original de Minas Gerais + sua Company existente.
5. DEF original de Eldorado + sua Company existente.
6. DEF original do RBR + sua Company existente.
7. Opcional: definição de editor/cidade/prefab de Minas Gerais **se ela existir de fato**; não criar city ou prefab fictícios.

## Uso recomendado: gerar as três Companies para testes

Abra o executável **ETS2_Company_Gerador.exe**, selecione todos os arquivos acima,
escolha **Todos os 3 mapas** e **AUDITAR / CORRIGIR SCS EXISTENTE**.

Comando equivalente (substitua as rotas entre aspas pelos seus arquivos):

```powershell
.\ETS2_Company_Gerador.exe --cli --audit-existing `
  --mod "D:\ETS2\Librelato.scs" `
  --def1 "D:\ETS2\DefCompany1.scs" `
  --def2 "D:\ETS2\DefCompany2.scs" `
  --txt "D:\ETS2\cargas.txt" `
  --minas "D:\ETS2\def_minas.zip" `
  --existing-minas "D:\ETS2\company_minas.scs" `
  --eldorado "D:\ETS2\def_eldorado.zip" `
  --existing-eldorado "D:\ETS2\company_eldorado.scs" `
  --rbr "D:\ETS2\def_rbr.zip" `
  --existing-rbr "D:\ETS2\company_rbr.scs" `
  --output "D:\ETS2\Saida_Final"
```

A ferramenta emite **três SCS independentes** como candidatos de teste,
sem alterar seus arquivos de entrada. **Não classifique os SCS como homologados
antes de concluir os ensaios no jogo.**

## Como interpretar o resultado

- `PAINEL_GERAL_LOGISTICA_V3.txt`: resumo legível dos 3 mapas.
- `PAINEL_GERAL_LOGISTICA_V3.json`: métricas, bloqueios e hashes.
- `COBERTURA_MAXIMA_<MAPA>.csv`: TODAS as empresas do mapa, incluindo nome
  fictício, IN/OUT originais, ramo sugerido, permissões previstas, permissões
  existentes e lacunas.
- `AUDITORIA_<MAPA>.json`: trilha técnica completa de decisões.
- `QUALIDADE_LOGISTICA_<MAPA>.json`: diferenças entre par cadastrado,
  par documental, par econômico com setor identificado e candidato com editor.
- `<MAPA>_REVISAO_ECONOMICA_PRIORIZADA.csv`: casos que continuam ambíguos.
- `COBERTURA_CIDADES_<MAPA>.csv`: cidades somente quando existe
  `company_def` com `city` e `prefab` explícitos.

### Métricas com nomes parecidos **não são equivalentes**

A cobertura de permissões justificadas pode atingir 100% quando **todas as
associações documentáveis por regras e IN/OUT originais** foram incluídas.
Isso não comprova que todas as empresas do jogo foram classificadas,
que existam pares origem/destino para as 24 cargas, que os prefabs existam
no mapa carregado ou que fretes apareçam no mercado.

O campo `homologado_no_ets2` é **false** enquanto não houver ensaios de jogo
reais para os 24 tipos de carga em cada um dos 3 mapas (72 ensaios).

## Portão rigoroso de homologação offline

A função **FINALIZAÇÃO OFFLINE**/ `--finalize-offline` exige cadeias
econômicas e dados editor em todos os mapas. Se faltar evidência, ela
**bloqueia a publicação comercial** e entrega relatório de bloqueio.

Para usar o gerador como candidato de teste enquanto há pendências
documentais, escolha **AUDITAR / CORRIGIR SCS EXISTENTE**. Esta opção
não certifica o jogo nem inventa empresas.

## Teste final no ETS2

1. Faça backup do perfil. Ative **um mapa de cada vez** e apenas sua Company
   gerada, mantendo MOD, DEF 1/DEF 2 e dependências corretas.
2. Verifique a ordem dos mods e a compatibilidade com a versão do jogo.
3. Confira o `game.log.txt` e erros de carga/cargo, empresa e prefab.
4. Confira existência de um frete de cada carga no mercado; anote empresa,
   cidade e origem/destino (empresas distintas), colete e conclua a entrega.
5. Repita em Minas Gerais, Eldorado e RBR, total de **72 tipos de ensaios**
   (24 por mapa). Uma linha por tipo de carga é o mínimo de amostragem;
   isso não substitui testar todas as combinações de rotas.
6. Anexe evidências da conclusão antes de usar a palavra "homologado".

## Limitações reais encontradas nos arquivos anteriores

Na auditoria documental anterior (não é resultado pós-correção):

| Mapa | Empresas da DEF | Cadeias com par econômico | Editor cidade/prefab |
|------|----------------:|--------------------------:|--------------------:|
| Minas Gerais | 370 | 22/24 | 0 |
| Eldorado | 214 | 8/24 | 646 instâncias |
| RBR | 642 | 24/24 | 995 instâncias |

Minas Gerais **não contém** editor nos pacotes fornecidos até então.
Sem dados adicionais verdadeiros do mapa e sem executar o jogo, é
impossível provar 100% de cobertura territorial.

## Critério de entrega

**Versão técnica candidata:** testes automatizados aprovados, EXE compilado,
SCS tecnicamente gerado e relatórios reais auditados.

**Homologação ETS2:** evidência de frete visível, modelo de carga, coleta,
entrega concluída, `game.log.txt` sem erros relevantes e documentação da
versão do ETS2/mapa. Não é substituída por CI ou por hashes.
