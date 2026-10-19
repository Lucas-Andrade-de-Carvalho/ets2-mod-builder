# ETS2 Company Logistics V10

Sistema HTML de processamento local de DEF Company por mapa, derivado do arquivo `ETS2_Company_Logistics_ULTIMATE_UPDATE(2).html`.

## Como usar

1. Abra `index.html` no navegador e selecione **V10 por mapa**.
2. Selecione a **Company original do mapa** em ZIP/SCS com `def/company/` na raiz.
3. Adicione as **DEF Company 1 e 2** como fonte de **templates** (não precisam ficar ativas no ETS2).
4. Selecione o ZIP com **`def/cargo.librelato.sii` e `def/cargo/carga*.sui`** (ou estrutura equivalente do mod, mantendo `def/`).
5. Confira os nomes das cargas e selecione **grade baixa** ou **grade alta**, informando o token `body_type` verdadeiro.
6. Analise o relatório. Apenas cargas que têm origem, destino, templates e compatibilidade comprovados são habilitadas.
7. Escolha **mod acima do mapa** para neutralizar definições antigas que continuam no mapa, ou **substituir company-base** para remover fisicamente os arquivos antigos do ZIP.
8. Gere o SCS. **Não mantenha as DEF Companies genéricas 1 e 2 ativas junto do substituto.** Mantenha o mod principal do Librelato ativo.

## Decisões de segurança e realismo

- Empresas sem produtos compatíveis permanecem sem fretes.
- A classificação de ramo exige nomes ou correções manuais verificáveis: nomes opacos permanecem como **incertos**.
- Sorgo não sai de laticínios; milho não é destinado automaticamente a indústrias de refrigerantes.
- Silos não expedem os mesmos grãos nessa configuração: isso evita fretes entre silos/cooperativas sem comprovação de transferência.
- As relações são validadas por carga, origem, destino, `cargo_def` e `body_types`; cargas insuficientemente documentadas ficam fora da company, com motivo no relatório.
- O modo complementar reutiliza os próprios arquivos `.sii` do mapa para neutralizar as definições antigas, preservando a sintaxe.
- `in_cargo`/`out_cargo` legados bloqueiam a geração, porque podem reintroduzir cargas antigas.
- `index.html` mantém o motor anterior na aba **Modo legado**.

## Validação

- 16/16 testes internos de classificação e preservação de regras econômicas.
- Teste de ZIP em memória: fazenda → silo com milho compatível, templates reais simulados e geração/reabertura da saída de sobreposição.
- Sintaxe JS da V10 verificada.
- **Pendente:** teste dentro do ETS2 com os arquivos completos do usuário e compatibilidade de modelos/métodos de carga da versão 1.54+. A validação de `body_types` não basta para garantir que os fretes aparecerão na carroceria.

## Referências

- https://modding.scssoft.com/wiki/Documentation/Engine/Units/cargo_def
- https://modding.scssoft.com/wiki/Documentation/Engine/Units/cargo_data
- https://modding.scssoft.com/wiki/Games/ETS2/Modding_guides/1.54
