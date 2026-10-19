# ETS2 Company Logistics — Ultimate

Gerador **offline** de DEF Company para Euro Truck Simulator 2. Mantém as abas originais do projeto (Arquivos, Empresas, Logística, Cadeias e Gerar SCS) e inclui a aba **Criação de Companys**, específica para as cargas do Librelato.

## Uso da aba Criação de Companys

1. Abra **index.html** no Chrome ou Edge.
2. Selecione a **DEF Company do mapa** (`.zip` ou `.scs` em formato ZIP).
3. Selecione a **DEF das cargas do Librelato** (`cargo/` ou `def/cargo/`, incluindo `cargo_data` e os `body_types`).
4. Clique em **Analisar e gerar Company**.
5. Confira o resultado. Clique em **Baixar Company .SCS** quando o pacote passar na validação.

O gerador usa somente **empresas existentes na DEF do mapa** e **IDs de carga existentes na DEF do reboque**. Pode distribuir cargas para grade alta e baixa conforme a compatibilidade realmente identificada; não cria ofertas artificiais para preencher uma grade.

## Compatibilidade de arquivos

O leitor detecta definições em:

- `company/<empresa>/in/`, `out/`, `editor/`.
- `def/company/<empresa>/in/`, `out/`, `editor/`.
- **Diretamente `<empresa>/editor/`, `<empresa>/in/` e `<empresa>/out/`**, quando o ZIP foi criado de dentro da pasta `company/` (como `alc_cle/editor/clementina.sii`).
- `def/<empresa>/...` ou os mesmos caminhos **dentro de subpastas de um ZIP**.
- Pacotes **ZIP/SCS ZIP dentro de outro ZIP/SCS**, em até três níveis, com limites para evitar processamento excessivo.
- `cargo/`, `def/cargo/`, `vehicle/` e manifestos de carga do Librelato, também em pacotes aninhados.

**Limite:** não é possível ler um `.scs` binário em formato nativo **HashFS** com JSZip. Ele precisa ser extraído previamente usando ferramenta compatível. Um arquivo contendo apenas `map/`, `model/` ou `prefab/` não é uma DEF Company. Pacotes com caminhos duplicados são recusados, nunca sobrescritos silenciosamente. Arquivos sem o prefixo `company/` devem ter pelo menos um `editor/*.sii` e um `in/*.sii` ou `out/*.sii` para não confundir pastas de modelos com empresas. ZIP/SCS internos desnecessários são ignorados se já existir uma DEF Company identificada no nível atual.

## Regras de precisão

- O `cargo:` **real** nos `IN/OUT` da DEF do mapa tem prioridade sobre palpites pelo nome.
- Quando não há correspondência direta, o motor utiliza **categorias econômicas comprovadas**. Por exemplo, lojas que trabalham com areia, brita, tijolos, pisos e telhas podem expedir cimento e outros materiais para obras, mesmo sem cimenteira.
- Distribuição agrícola e industrial usa fazendas, cooperativas, lojas, madeireiras, centros de distribuição e destinatários plausíveis — **não exige fábrica**.
- Os paletes do Librelato são priorizados para madeireiras e serrarias, com limites de origens e destinos para não dominar o mercado.
- O catálogo local de empresas originais da SCS é consultado **somente quando uma empresa do mapa corresponde ao registro**, sem adicionar empresas ao mapa.
- Empresas sem evidência suficiente podem permanecer sem cargas. A análise não garante fretes dentro do jogo.

O botão de download só é habilitado depois da validação estrutural do `.scs`. Trocar um dos ZIPs ou editar correções manuais invalida o download anterior.

## Organização

| Arquivo | Função |
|---|---|
| `index.html` | Aplicativo offline independente, com biblioteca ZIP e motor incorporados |
| `creator_tab.js` | Código-fonte da aba Criação de Companys |
| `scs_company_catalog.js` | Catálogo de referências SCS, conservado separadamente para consulta/manutenção |
| `tests/company-creator.smoke.cjs` | Testes de leitura, integridade da Company e download |
| `.github/workflows/company-smoke.yml` | Testes automatizados em alterações do site |

Como o HTML funciona **sem servidor ou internet**, sua versão distribui o motor e o catálogo incorporados. Ao modificar o código-fonte de `creator_tab.js`, é preciso sincronizá-lo com o último bloco `<script>` do HTML antes de publicar.

### Testes

Com Node.js 20+:

```bash
node tests/company-creator.smoke.cjs
```

O teste usa DEFs sintéticas e confirma: Company sem prefixo como `alc_cle/editor`, ZIP na raiz e arquivos aninhados, rejeição de modelos sem Company, erros HashFS, caminhos repetidos, mudanças no conteúdo do mapa, cargo_data, grade alta/baixa, integridade dos arquivos `editor`, ausência de empresas/cargas inventadas e download.

**Ainda é necessária a validação in-game no ETS2** com o mod principal do Librelato e a Company específica do mapa. Não mantenha as antigas DEF Companies genéricas 1 e 2 competindo pelas mesmas definições; confira `game.log` e ofertas do mercado após alterar a ordem/prioridade dos mods.
