# ETS2 Company Logistics — Ultimate + Criação de Companys

Esta versão recupera a base **ETS2_Company_Logistics_ULTIMATE_UPDATE(3).html**, preserva suas abas e integra um segundo gerador em **Criação de Companys**.

## Abas

- **Arquivos**: leitura da Company do mapa, atualização usando uma versão anterior e DEF auxiliar opcional.
- **Empresas**: classificação da atividade econômica e justificativas.
- **Logística**: visualização da distribuição de cargas.
- **Cadeias**: representação das regras de origem e destino.
- **Gerar SCS**: exportação do modo original.
- **Criação de Companys**: geração de uma nova Company por mapa para o rodotrem Librelato, usando dois arquivos.

## Criação de Companys — modo novo

1. Selecione a **DEF Company do mapa** (SCS/ZIP contendo `company/` ou `def/company/`).
2. Selecione a **DEF das cargas do Librelato** (`def.zip` com `cargo/`, `cargo.librelato.sii` e, quando disponível, `vehicle/`).
3. Clique em **Analisar e gerar Company**.
4. O sistema identifica os cargos `carga1`, `carga2`, etc., e seus `body_types`, verifica a cadeia econômica por empresa e gera um único `.scs` para grade alta e baixa quando ambas estiverem disponíveis.
5. Use **Baixar diagnóstico TXT** se alguma carga for rejeitada.

Não é necessário anexar as antigas DEF Companies 1 e 2 à aba nova. O nome do arquivo final é derivado do arquivo do mapa; nenhuma cidade ou mapa específico está codificado como obrigatório.

O SCS novo preserva os arquivos **editor** e demais arquivos Company do ZIP original, remove as permissões antigas `IN/OUT` **do próprio ZIP usado como entrada**, e escreve apenas as novas relações validadas. Ele **não** copia nem substitui `def/cargo` ou `def/vehicle` do mod principal do reboque.

## Maior precisão no modo original

O gerador original continua disponível, porém o modo normal não inventa mais intermediários genéricos, não distribui pacotes arbitrários de cargas a hubs, nem preenche planos com mercadorias apenas pela categoria ampla da empresa. Para grãos, o motor evita autorizar OUT de silo automaticamente quando isso permitiria fretes silo→silo.

Isso pode reduzir o número de ofertas, propositalmente: empresa não reconhecida não passa a transportar produtos incompatíveis para aumentar cobertura.

## Identificação de empresas e correção opcional

Alguns IDs do mapa são abreviações e não identificam claramente o ramo econômico. A aba **Criação de Companys** foi ajustada para reconhecer casos claros, como `abconstru` (construção), `araserr` (serraria), `arnasuino` (pecuária) e `belgo2` (siderurgia). Uma empresa como `acero` continua incerta sem evidência adicional, para evitar inventar sua operação exata.

Na própria aba existe agora a seção opcional **Corrigir identificação de empresas**. Ao saber o ramo de uma empresa, informe, por exemplo, `empresa_olaria = ceramica`. Os dois arquivos ZIP/SCS continuam sendo as únicas entradas obrigatórias.

As rejeições de carga especificam quais setores de origem e destino ainda não foram reconhecidos. A correção é no motor de classificação, não exige obrigatoriamente modificar os arquivos originais do mapa.

## Limitações técnicas

- O navegador abre arquivos `.scs` em formato ZIP. HashFS precisa ser extraído antes.
- Não existe promessa de identificação perfeita de empresas com IDs opacos em qualquer mapa. Elas aparecem no diagnóstico, e podem permanecer sem cargas.
- Uma definição `cargo_def` baseada no ID da carga não comprova sozinha compatibilidade de modelos, método de carregamento, rota econômica ou oferta no jogo.
- O ETS2 combina origens OUT e destinos IN que usam o mesmo cargo; não é possível obrigar um percurso em estágios (ex.: fazenda → silo → indústria) apenas usando IN/OUT.
- Um SCS complementar não elimina arquivos que ainda estão dentro **de outro mod**. Para substituição completa, desative a Company-base antiga separada ou resolva o conflito dentro do mapa.
- É necessário validar o mod dentro do ETS2, conferir mercado de fretes e `game.log`.

## Logística flexível: expedição e recebimento

Na aba **Criação de Companys**, a relação `OUT` significa **local que pode expedir a mercadoria**, não necessariamente a fábrica que a produziu. `IN` significa **local que pode recebê-la**, não apenas consumidor final.

- Cimento: cimenteiras, lojas e depósitos de materiais, e centros logísticos compatíveis podem **expedir**; obras, lojas e centros logísticos podem **receber**.
- Tijolos: olarias **ou depósitos** expedem; obras e depósitos recebem.
- Granito: pedreiras, mineradoras e depósitos expedem; obras e lojas de materiais recebem.
- Bebidas, hortifrúti e outros produtos: distribuição e revenda podem atuar nos dois sentidos.
- `Pallets Alto TESTE` é tratado como mercadoria **paletizada** sem conteúdo detalhado, habilitada em vários setores comercialmente plausíveis. Isso **não** equivale a paletes vazios e não libera automaticamente postos de combustível, Correios ou outros negócios sem indício de expedição.
- Silos agrícolas recebem grãos; não se habilita OUT de grãos em silos indiscriminadamente, para evitar combinações não fundamentadas como silo→silo.

A presença de um mesmo setor em IN e OUT é intencional para representar transferência entre depósitos, revenda e redistribuição. Se o mapa não identifica a atividade econômica da empresa, a análise pode manter o ponto sem frete em vez de inventar atividade. A identificação de modelos, carrocerias e ofertas ainda deve ser testada no jogo.

## Estratégia de redistribuição econômica ampliada

A aba **Criação de Companys** passou a considerar múltiplas maneiras legítimas de expedir mercadorias:

- **Siderurgia / metalurgia:** bobinas industriais de nome genérico (ex. `Bobinas 2`) podem partir de empresas do setor; essa interpretação é identificada como **hipótese**, porque o nome não prova o conteúdo físico 3D da bobina.
- **Agroinsumos e cooperativas:** adubo pode partir de distribuidores rurais ou, com evidência contextual, de cooperativas que comercializem insumos.
- **Transportadoras e armazéns:** expedição e recebimento de cimento, materiais industriais, madeira e pluma de algodão somente em setores compatíveis.
- **Transferências entre construtoras:** quando não existir fábrica, depósito ou distribuidor identificável, e houver pelo menos duas empresas de obras, admite-se uma expedição limitada como hipótese de remanejamento de estoque. A hipótese aparece no diagnóstico.
- **Permissões antigas de carga:** são usadas apenas como indício pontual se a empresa tiver um conjunto pequeno de IN/OUT e a carga antiga corresponder semanticamente à mercadoria. Isso evita herdar a distribuição genérica e indiscriminada das DEF Companies originais.
- **Identificação por ID:** `agrotec`, `arralog` e `acero` são tratados de maneira setorial conservadora; empresas sem indício continuam desconhecidas.
- **Preservação de maiúsculas e minúsculas:** as pastas das empresas mantêm a grafia do mapa ao gerar os novos `IN/OUT`.

O diagnóstico mostra exemplos de IDs de origem/destino e marca quaisquer hipóteses. Se um mapa realmente não tiver ao menos um par plausível, a carga permanece excluída; não são fabricadas empresas novas. A versão não garante fretes no ETS2 sem teste no jogo.

## Correções após revisão de rotas do mapa

As primeiras simulações de empresas reais revelaram expedições economicamente improváveis: adubo saindo de `acero`, batatas/laranjas saindo de canaviais ou usinas de cana, tijolos saindo de marmorarias e cimento saindo automaticamente de uma construtora. O motor foi alterado para:

- Dar preferência à atividade econômica identificada sobre associações legadas e **impedir que o histórico contradiga um setor conhecido**.
- Reconhecer usinas/canaviais de cana como especialidade própria; podem receber fertilizantes, mas não expedem automaticamente grãos, batatas ou laranjas.
- Reconhecer marmorarias como expedidoras/recebedoras possíveis de granito, sem habilitá-las a fabricar tijolos.
- Exigir especialização documentada para fazendas que expedem batatas ou laranjas; uma fazenda de batatas não expede milho automaticamente.
- Remover a escolha arbitrária de uma construtora como expedidora de cimento ou tijolos quando o mapa não fornece fábrica/loja/depósito.
- Não usar lojas de materiais como expedidoras de adubo agrícola pesado sem evidência de agroinsumos.
- Identificar no diagnóstico cargas cuja única origem é um centro logístico, indicando que o estoque específico não está comprovado.

**Teste de regressão:** geração integral de SCS com mapa sintético de 16 empresas e 9 cargos do Librelato, verificando 11 permissões válidas, 8 ausências obrigatórias e a exclusão das antigas referências do ZIP de entrada. Este teste não substitui validação com o mapa real no ETS2.

## Catálogo de empresas SCS e leitura da DEF original (outubro de 2026)

A aba **Criação de Companys** contém agora um catálogo **offline** com **143 referências únicas** de empresas padrão e seus ramos, compiladas a partir de discussões no Fórum SCS (2014, 2020) e da Truck Simulator Wiki. Cada referência inclui nome, ramo e ligação à fonte. A lista **não é exaustiva**: o catálogo comunitário atual reúne mais empresas, e as empresas mudam entre versões e DLCs.

**Fontes:** 
- https://forum.scssoft.com/viewtopic.php?p=195482
- https://forum.scssoft.com/viewtopic.php?t=285506
- https://forum.scssoft.com/viewtopic.php?t=3897
- https://trucksimulator.wiki.gg/wiki/Companies/Euro_Truck_Simulator_2
- https://modding.scssoft.com/wiki/Documentation/Engine/Units/cargo_def
- https://modding.scssoft.com/wiki/Documentation/Engine/Units/company_permanent

O catálogo é usado **somente para classificar empresas que já estão presentes nos arquivos da DEF do mapa**; nenhuma dessas referências vira empresa no mod gerado.

A leitura do ZIP do mapa analisa:
- Os IDs reais dos arquivos `def/company/<id>/editor/` e dos arquivos `def/company/<id>.sii`.
- As permissões antigas `def/company/<id>/in/*.sii` e `out/*.sii`.
- **O campo efetivo** `cargo: "cargo.<id>"` de cada cargo_def, e não apenas o nome do arquivo SII.
- A categoria econômica inferível do identificador de carga e os indícios cruzados de entrada e saída da empresa.

Em caso de ausência de evidência, a empresa permanece como desconhecida. O relatório exibe setor, evidência, categorias IN/OUT e, quando se tratar de referência SCS, a fonte consultada.

**Restrições rígidas de exportação:** somente empresas do arquivo de entrada e somente IDs de cargas lidos na DEF do Librelato podem receber novas permissões de `IN/OUT`. Os cargos/empresas do catálogo nunca são adicionados ao mapa. O pacote gerado remove as antigas relações do ZIP fornecido e preserva os arquivos editor. Se houver regras antigas dentro de outro mod/arquivo de mapa, é necessário substituí-lo ou remover o conflito à parte. O catálogo classifica empresas, mas não certifica que o mercado esteja funcionando dentro do ETS2.

## Testes realizados

- Verificação de sintaxe da aplicação original e do motor da aba nova.
- Teste da aba nova com Company e DEF simuladas, cobrindo milho para grade baixa e tijolos para grade alta.
- Inspeção do SCS produzido: novos `IN/OUT` presentes, permissões antigas do ZIP excluídas, arquivo `editor` preservado.
- Teste de regressão no motor original: empresa desconhecida não vira hub automático, milho sai de fazenda para silo e moinho, sem OUT automático de silo.
- **Pendente:** execução com os dois ZIPs reais do usuário e teste in-game.

O aplicativo é um HTML independente com JSZip incorporado. Abra `index.html` localmente no Chrome ou Edge.
