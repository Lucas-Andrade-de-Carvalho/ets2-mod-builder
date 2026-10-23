# Auditoria conjunta V3 — Minas Gerais, Eldorado e RBR (22/10/2026)

Relatórios examinados:
- `AUDITORIA_MINAS_GERAIS(5).json`, `COBERTURA_MAXIMA_MINAS_GERAIS.json`, `PENDENCIAS_CLASSIFICACAO_MINAS_GERAIS.csv`;
- `AUDITORIA_ELDORADO(5).json`, `COBERTURA_MAXIMA_ELDORADO.json`, `PENDENCIAS_CLASSIFICACAO_ELDORADO.csv`;
- `AUDITORIA_RBR(5).json` e as planilhas de cobertura/pendências do RBR já enviadas e analisadas anteriormente.

## Linha de base dos relatórios ANTERIORES às novas correções

| Indicador | Minas Gerais | Eldorado | RBR |
|---|---:|---:|---:|
| Empresas na DEF | 370 | 214 | 642 |
| Tipos de carga no catálogo | 24 | 24 | 24 |
| Cargas com par de origem e destino cadastrado | 24 | 24 | 24 |
| Pares economicamente documentáveis por carga (tipos cobertos) | 22/24 | 20/24 | 24/24 |
| Cargas candidatas a teste por referências de editor | 0 | 20 | 24 |
| Instâncias editor com cidade+prefab | 0 | 646 | 995 |
| Empresas sem classificação na DEF inteira | 182 | 147 | 252 |
| Revisões pontuais de permissões antigas | 129 | 125 | 182 |
| Permissões antigas sem comprovação | 60 | 86 | 129 |
| Permissões herdadas plausíveis, ainda sem comprovação | 16 | 1 | 54 |
| Novas autorizações regionais de pluma/coco | 139 | 19 | 0 |

**Cuidado:** os 24/24 pares cadastrados NÃO são 24/24 cargas comprovadas pelo editor/mercado do jogo. A cobertura publicada como 100% é só do universo de permissões consideradas justificadas pelo classificador atual, não de todas as empresas desconhecidas. Pluma/coco nos dois primeiros mapas são **simulações regionais autorizadas pelo usuário**, não prova do cultivo original.

## Diagnóstico concreto — casos de erro de classificação

### Eldorado

- `cmddiesel`, `midwest`, `drekkar2`, `gnt2`, `norrsk` e similares: o antigo `revenda_fertilizante` surgiu porque a DEF registra fertilizante nos dois sentidos, **mas também bebidas, roupas, brinquedos, pneus, alimentos e utensílios**. O classificador novo reconhece movimentação logística multissetorial pela combinação bruta de IN e OUT, não pela palavra `fertilizer` isolada.
- `sellplan2`, identificado pelo ID como supermercado, e `sanbuilders2`, identificado como obra: os IN/OUT incluem múltiplos químicos perigosos nos dois sentidos (`arsenic`, `cyanide`, `chlorine`, `sulfuric`, `mercuric`, `nitrocel` etc.). A inferência com evidência química forte tem prioridade sobre esses IDs; as cargas comerciais antigas sem correspondência ao fluxo original podem ser neutralizadas, preservando o fertilizante realmente documentado.
- A exceção regional de pluma e coco continua válida, com destinatários específicos; não autorizar descarregamento em obras ou postos só para fechar números.

### Minas Gerais

- `emersonmaqui`: no IN/OUT aparecem `trator`, `escavadeira`, `pneutrator_s`, implementos e fertilizante. A atividade mista é **revenda de máquinas/insumos agrícolas**, não comércio exclusivo de adubo. Remover permissões de grãos sem suporte nesse tipo de unidade.
- `copobras` e `copobras2`: no OUT constam `coposdesc`, `pratosdesc` e `talheresdesc`. O ramo é fabricação de descartáveis; **nenhum desses produtos equivale a tijolos, cimento ou outro cargo Librelato**.
- `acomais`: trabalha com papel, plástico, sucata metálica e `supaletes`; classificar como reciclagem com paletes somente onde o IN/OUT original registra.
- `abcatacado`: atacadista de alimentos/bebidas que aparece recebendo `carga5` (pluma) de uma regra regional anterior excessivamente ampla. A autorização de pluma passou a exigir armazém/atividade têxtil/agroindustrial plausível, **não qualquer distribuidor**; permissões herdadas de pluma podem ser neutralizadas se a DEF original só documenta alimentos.
- **Pendência estrutural não solucionável só por relatório:** a DEF Minas analisada possui **0 referências company_def cidade+prefab**. Não se pode inventar localização para comprovar origem/destino no editor.

## Proteções implementadas

1. A nova classificação para esses setores **não consulta cadastro externo de empresas reais**.
2. Produtos originais documentados no IN/OUT são preservados; mercadorias herdadas sem compatibilidade clara, e que contradizem a atividade comprovada, podem ser neutralizadas no novo SCS.
3. As exceções de **pluma saindo de fazendas para silos/armazéns/beneficiamento** e **coco saindo de fazendas para mercados/mercearias/CEASAs** aplicam-se apenas a Minas e Eldorado. O RBR não recebe essa exceção.
4. Quando as três Companies são auditadas juntas, a saída inclui `TRIAGEM_PENDENCIAS_3_MAPAS.csv`, com decisão individual por mapa, setor, empresa, carga, direção e mercadorias IN/OUT.
5. Se uma Company possuía **todas as cargas com par cadastrado** e uma correção deixaria alguma carga sem par, a publicação é bloqueada. O programa não inventa origem ou destino para mascarar regressão.
6. Os arquivos originais são preservados; não marcar arquivos de saída como homologados antes de executar fretes no ETS2.

## O que ainda impede afirmar "definitivo"

- Os relatórios novos são informações de **execuções anteriores a este commit**. Para calcular quantas pendências foram efetivamente eliminadas no RBR/MG/Eldorado, é obrigatório **rodar o gerador novo com as mesmas DEFs e Companies reais** e comparar o resultado.
- Os **seis relatórios de MG e Eldorado NÃO são as DEFs nem os arquivos binários .scs**. Não há aqui base para editar esses SCS diretamente.
- A ausência de editor em MG é uma falta real de fonte territorial: buscar um `company_def` legítimo do mapa ou saída do editor; nunca atribuir cidade/prefab fictícios.
- O ETS2 não foi rodado e o `game.log` dessas novas Companies não foi fornecido. Não declarar frete disponível, coletado e entregue.

## Próximos ensaios no gerador

Escolher `Todos os 3 mapas` e `AUDITAR / CORRIGIR SCS EXISTENTE`, com os 4 fontes do reboque, DEFs e Companies dos três mapas e pasta de saída nova. Conferir `PAINEL_GERAL_LOGISTICA_V3.json`, `TRIAGEM_PENDENCIAS_3_MAPAS.csv`, os relatórios de cada mapa e as três Companies `.scs`. Conferir que nenhuma carga anteriormente completa ficou sem par. Aplicar as três Companies em perfis separados do ETS2 e testar fretes, cidades, prefabs, carreta e entrega antes de homologar.

**Critério técnico de qualidade:** empresa fictícia classificada por cadeia econômica demonstrada, máximo de fretes plausíveis com IN/OUT correto, ausência de cargas ilógicas, sem quebrar rotas válidas e sem converter a contagem 24/24 em certificado de jogo.
