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

## Busca por famílias comerciais (atualização 19/10/2026)

A aba **Criação de Companys** procura primeiramente referências exatas de mercadorias em `cargo:` no histórico IN/OUT da DEF do mapa. Quando faltam, usa relações de **categorias econômicas relacionadas**, sem criar empresas nem cargos:

- **Granito (carga14/15):** expedição por mineração/marmoraria com OUT de pedras ou mármore e recebimento por empresas de construção compatíveis.
- **Ração, xerém e sacaria (carga17–20):** IN/OUT de ração, suplementos e matérias-primas para alimentação animal, com setores agropecuários coerentes.
- **Sorgo (carga23):** fazendas que expedem cereais; silos/cooperativas e fábricas de ração que recebam insumos agrícolas.
- **Pluma de algodão (carga5):** fazendas com algodão ou produção agrícola diversificada comprovada, e destinos de fibras/cooperativas.
- **Bobinas (carga9):** empresas com IN/OUT de produtos siderúrgicos e empresas metalúrgicas receptoras. A interpretação física do conteúdo da carga continua sujeita a confirmação.

A busca usa limites de empresas candidatas por carga, não inventa produto, não inclui postos/Correios em atividades incompatíveis e preserva o tratamento especial de **paletes** (até 3 origens e 6 destinos, sobretudo madeireiras). Empresas com IDs opacos são classificadas pelo conjunto de cargas IN e OUT somente quando os sinais são consistentes.

A validação incluiu a geração e releitura de um ZIP/SCS de teste, com nove cargas anteriormente rejeitadas agora encontrando relações IN/OUT em um mapa sintético. Ainda é necessário conferir o resultado com o mapa específico e o mercado do ETS2.

## Continuidade e testes do último ajuste (19/10/2026)

O contexto consolidado para outra conversa está em [HANDOFF_COMPANY_LOGISTICS.md](HANDOFF_COMPANY_LOGISTICS.md).

Última correção do motor: ao analisar granito, ração, pluma e bobinas, utilizar pistas fortes dos cargos `IN/OUT` existentes **mesmo quando o ID da empresa é opaco**. O filtro mantém restrições para impedir areia/brita→granito automático, posto→bobinas ou fazenda de uma única cultura→pluma sem evidência.

- Testes unitários/simulados: oito cenários de evidência por mercadoria passaram.
- Teste integral do `index.html` com ZIP de mapa em subpasta, DEF do Librelato também em subpasta, cinco cargas das duas grades e 11 empresas: pacote SCS aberto novamente, 13 relações IN/OUT, 14 verificações de integridade e regras concluídas, download funcionando, nenhuma empresa ou cargo inventado.
- **Pendente:** análise da DEF do mapa real que apresentou oito cargas sem rota e teste com o `game.log` no ETS2. Os testes automatizados não comprovam ofertas in-game.


## Diagnóstico de DEFs genéricas (correção 20/10/2026)

O gerador agora detecta quando a DEF enviada é composta quase totalmente por permissões `cargo.cargaN` (situação observada nas antigas DEF Companies 1/2 do Librelato). Essas permissões não comprovam a atividade econômica das empresas, portanto um arquivo dessa natureza não pode substituir a **DEF Company original do mapa**. Em arquivos grandes, a geração é bloqueada com orientação explícita. O diagnóstico registra a quantidade de registros genéricos e exibe os IDs reais em `cargo:` encontrados nos IN/OUT, não apenas os nomes dos arquivos `.sii`. As regras também identificam revendas de construção e agropecuárias por entradas de estoque e saídas de mercadorias relacionadas. Não se garante rota quando as provas faltam.


### Correção com DEF real de 208 empresas (20/10/2026)

Nova rotina de recuperação de rotas para granito, rações, pluma e bobinas: cruza **produtos reais** em IN e OUT, com limites conservadores por empresa, e marca explicitamente relações inferidas. Quando os cargos exatos não estão presentes na DEF original, disponibilidade no mapa não equivale a produção comprovada dessa mercadoria. Versão do motor aparece no status da aba para permitir identificar HTML antigo. Validação local do ZIP de entrada: 208 empresas, 6739 OUT e 7088 IN, oito cargos em questão; os testes no GitHub usam perfis amostrados dessas empresas, não o pacote completo ou o ETS2.


### Substituição integral dos arquivos IN/OUT da DEF do mapa

A partir de 20/10/2026, o gerador produz um **mod de sobrescrita integral**. Além das novas permissões Librelato, ele escreve, nos mesmos caminhos virtuais dos arquivos IN/OUT antigos, definições de `cargo: ""`. Conforme a SCS, cargo vazio desativa a permissão original, mesmo quando a empresa não tem nova carga compatível. O número total de arquivos originais neutralizados aparece no status da geração.

**Obrigatório:** No Gerenciador de Mods, coloque a Company gerada **acima do pacote DEF do mapa** e de qualquer outro mod Company. Sem prioridade maior, os arquivos antigos podem prevalecer. O mod principal do Librelato deve permanecer ativo; desative antigas DEF Companies genéricas que também mudam essas permissões. A alteração da oferta existente em saves pode exigir tempo de atualização de economia. Empresas sem mercadoria compatível permanecem no mapa, mas ficam sem rotas Librelato.

Fonte oficial: https://eurotrucksimulator2.com/modding_changes.php ("Changes in company definition": `cargo` vazio desativa permissão).


## Geração universal empresa por empresa (2026-10-20)

O motor percorre cada empresa real da DEF e examina seus `IN` e `OUT` antes de associar as mercadorias efetivamente presentes na DEF do reboque. Associações inferidas por produtos relacionados ficam marcadas no diagnóstico. Se nenhuma carga for economicamente compatível, aquela empresa fica sem novas permissões e suas permissões originais são neutralizadas pela sobrescrita integral. Não há tabelas obrigatórias de empresas nem limites globais de produtores por carga. Cargas sem origem e destino distintos permanecem sem rota.


### Prioridade do conteúdo IN/OUT sobre nomes (v3.1)

O campo `cargo:` encontrado na DEF original é agora prova primária; um nome ou ID sugerindo setor diferente não bloqueia um cargo realmente declarado. Se houver conflito, ele será registrado no diagnóstico. Nomes de arquivos `.sii` podem auxiliar apenas como evidência inferida quando `cargo:` não foi identificado. Nomes e catálogo SCS não criam novas associações por si sós. Empresas sem mercadoria compatível seguem com IN/OUT antigos neutralizados.


### Coerência econômica (v3.2, 20/10/2026)

A presença literal de `cargo:` é forte evidência documental, mas **não autorização absoluta**. Empresas de ramos especializados (siderurgia, postos, concessionárias, pedreiras, etc.) não recebem/expedem mercadorias de outros setores apenas por uma definição isolada. A contradição só pode ser superada automaticamente se várias categorias independentes de produtos reais em IN e OUT indicarem atividade alternativa **e não houver prova do ramo original nem identificação exata no catálogo SCS**. Eventos rejeitados aparecem no diagnóstico, e nenhuma empresa recebe carga obrigatória. Não é necessário conhecer previamente o mapa.


## Arquitetura e fluxo de qualidade — revisão v4

**Fonte de verdade do gerador de Company:** `creator_tab.js`, incorporado ao último `<script>` de `index.html`. O arquivo `engine_universal.js` é legado histórico, não é executado pelo HTML; mantido apenas para compatibilidade de referências antigas. Não editar o código inline do gerador e esquecer de sincronizar o arquivo fonte. O CI falhará se divergir.

**Arquivos:** `index.html` contém as seis abas e o fluxo de interface; `creator_tab.js` cuida da leitura da DEF de mapa, análise IN/OUT, compatibilidade econômica, neutralização de cargas antigas e empacotamento do SCS; `scs_company_catalog.js` é um catálogo de referência não autoritativo; `tests/company-creator.smoke.cjs` cobre comportamento e geração; `tests/project-integrity.cjs` valida integridade de scripts, abas e sincronização.

**Regras técnicas:** analisar `cargo:` REAL, não somente o nome do arquivo; ler todas as referências de uma definição, ignorando comentários; não ignorar silenciosamente um IN/OUT grande ou inválido; manter empresas sem cargas e neutralizar antigas permissões corretamente; não alterar a atividade manual ao consultar o catálogo; recusar ZIPs absurdamente expandidos. Usar apenas empresas presentes no mapa e mercadorias presentes na DEF anexada. 

**Validação:** o GitHub Actions executa testes estáticos e funcionais com Node 22 a cada modificação dos arquivos relevantes. Aprovação em CI não comprova comportamento no jogo. Para confirmar o resultado final, testar no Euro Truck Simulator 2 com mods na prioridade correta e conferir `game.log`, mercado de fretes e empresas vazias. Caso a DEF contiver outra forma de declarar cargas que o parser não reconheça, ampliar o suporte explicitamente e criar teste correspondente, em vez de assumir que não há mercadorias.


**Relatório técnico:** consulte [CODE_AUDIT_V4.md](CODE_AUDIT_V4.md) para falhas corrigidas, testes e limites conhecidos. Para sincronizar o código fonte com o HTML distribuído use `node scripts/sync-company-engine.cjs` (desenvolvimento apenas). O navegador não precisa de Node nem Python.


## Inteligência logística documental integrada (v4.1)

Ao clicar **Analisar e gerar Company**, o assistente combina automaticamente os produtos reais das definições IN/OUT do mapa com a base de conhecimento em `logistics_knowledge.json`. O HTML contém uma cópia offline das fontes e regras, permitindo funcionamento local sem API paga. Quando houver internet, consulta o mesmo conjunto de conhecimento público atualizado do próprio repositório; não envia nem conteúdo nem nomes das empresas ou arquivos do usuário para servidores externos. Esta consulta não é uma busca geral em mecanismos de pesquisa nem envolve modelo generativo. As fontes oficiais incluídas foram pesquisadas em 20/10/2026: Embrapa (grãos, ração, pluma), Instituto Aço Brasil (siderurgia) e ABCP (cimento). Novas fontes só devem entrar após validação documental.

O assistente preserva a regra fundamental: o conhecimento geral sobre uma cadeia produtiva **não comprova a atividade de uma empresa específica**. Uma fazenda de milho não é automaticamente expedidora de pluma; tubos ou sucata não provam fabricação de bobinas; milho/soja não provam expedição de ração. Esses casos são bloqueados se não houver produtos compatíveis declarados em OUT. O TXT de auditoria registra fontes e razões das decisões. Não há garantia de 100% de cargas distribuídas; a ausência de rota pode ser correta.


## Política de evidências v5

Consulte [QUALITY_V5.md](QUALITY_V5.md). O assistente exige evidências por mercadoria física, não usa IDs numéricos como definição de produto, distingue confiança documental/relacionada/inferida e mantém empresas sem fretes quando não há compatibilidade. O catálogo offline reúne 13 fontes documentais; a consulta de rede apenas atualiza essa base curada. A aprovação no GitHub Actions não substitui o teste no jogo.
