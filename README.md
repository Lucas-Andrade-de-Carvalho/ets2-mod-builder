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

## Limitações técnicas

- O navegador abre arquivos `.scs` em formato ZIP. HashFS precisa ser extraído antes.
- Não existe promessa de identificação perfeita de empresas com IDs opacos em qualquer mapa. Elas aparecem no diagnóstico, e podem permanecer sem cargas.
- Uma definição `cargo_def` baseada no ID da carga não comprova sozinha compatibilidade de modelos, método de carregamento, rota econômica ou oferta no jogo.
- O ETS2 combina origens OUT e destinos IN que usam o mesmo cargo; não é possível obrigar um percurso em estágios (ex.: fazenda → silo → indústria) apenas usando IN/OUT.
- Um SCS complementar não elimina arquivos que ainda estão dentro **de outro mod**. Para substituição completa, desative a Company-base antiga separada ou resolva o conflito dentro do mapa.
- É necessário validar o mod dentro do ETS2, conferir mercado de fretes e `game.log`.

## Testes realizados

- Verificação de sintaxe da aplicação original e do motor da aba nova.
- Teste da aba nova com Company e DEF simuladas, cobrindo milho para grade baixa e tijolos para grade alta.
- Inspeção do SCS produzido: novos `IN/OUT` presentes, permissões antigas do ZIP excluídas, arquivo `editor` preservado.
- Teste de regressão no motor original: empresa desconhecida não vira hub automático, milho sai de fazenda para silo e moinho, sem OUT automático de silo.
- **Pendente:** execução com os dois ZIPs reais do usuário e teste in-game.

O aplicativo é um HTML independente com JSZip incorporado. Abra `index.html` localmente no Chrome ou Edge.
