# CONTEXTO DE CONTINUIDADE — ETS2 Company Logistics Ultimate

**Instrução para uma nova conversa:** Continue este projeto diretamente a partir do código existente no repositório do GitHub, sem reconstruí-lo do zero. Analise os arquivos antes de propor alterações e não declare versão final validada sem testes no Euro Truck Simulator 2.

## Projeto e arquivos

- Repositório: https://github.com/Lucas-Andrade-de-Carvalho/ets2-mod-builder
- HTML principal: `index.html` (abrir localmente no Chrome/Edge, com JSZip incorporado).
- Motor da aba nova: `creator_tab.js` (também incorporado como último `<script>` de `index.html`). Após alterar `creator_tab.js`, sincronize o script embutido em `index.html`.
- Catálogo SCS: `scs_company_catalog.js` (também incorporado no motor).
- Documentação: `README.md` e este arquivo.

O site original tem as abas **Arquivos, Empresas, Logística, Cadeias e Gerar SCS**. Acrescentamos **Criação de Companys**, mantendo as demais abas. A aba nova recebe somente dois arquivos obrigatórios: (1) DEF Company original de qualquer mapa; (2) DEF das cargas do reboque Librelato. Aceita `.zip` / `.scs` em formato ZIP, caminhos `company/` / `def/company/`, subpastas, DEFs com entradas em pastas de empresa e ZIP/SCS internos quando suportados.

## Objetivo irrenunciável

Gerar **uma Company específica para cada mapa**, com logística de fretes economicamente plausível e compatível com as cargas do Librelato, incluindo **grade alta e baixa quando existirem ofertas válidas**. A saída é `DEF_Company_Librelato_<MAPA>_<HASH>_Universal.scs`, baixável via **Baixar Company .SCS** depois da análise e validação.

**NUNCA criar IDs de empresas nem cargos que não estejam nos arquivos de entrada.** Não fabricar cimenteiras, olarias ou fábricas fictícias apenas para preencher o mercado. Uma empresa pode permanecer vazia quando nenhuma carga for compatível. Não modificar diretamente os arquivos originais de entrada, nem copiar cargo_data/vehicle do Librelato na Company.

A prioridade é a atividade econômica real:
1. Cargo específico `cargo: "cargo.<id>"` em `def/company/<empresa>/out|in/*.sii`;
2. Evidências de estoque/expedição/recebimento de mercadorias da **mesma família econômica** (areia, brita, telha, piso, tijolo, tubo etc.);
3. Ramo inferido por ID/nome e catálogo da SCS para empresas padrão;
4. Apenas como último recurso, inferências conservadoras identificadas no diagnóstico.

O OUT é um local que **pode expedir** a carga, NÃO necessariamente o produtor industrial dela. O IN é um local que pode recebê-la, NÃO necessariamente o consumidor final. Não exigir cadeia rígida produtor→intermediário→consumidor. Por exemplo:
- Cimento (incluindo carga de palete/cinta) e tijolos: loja de materiais/depósito → obra ou outra revenda. Não exigir fábrica.
- Madeira: madeireira, serraria ou depósito de materiais → obra/loja.
- Granito: mineração/marmoraria/depósito que já movimenta pedra, granito ou mármore → obra/loja. Apenas areia e brita NÃO provam granito.
- Pluma de algodão: fazendas (preferir lavouras comprovadas) → cooperativas, beneficiadoras ou indústrias têxteis.
- Batata e laranja: fazendas/centrais → supermercados/atacados.
- Ração mineral, xerém, sacaria de ração: empresas que de fato expedem ração, suplementos, farelo; destinos pecuários/cooperativas/fazendas pertinentes.
- Bobinas 2: provisoriamente tratadas como bobinas industriais, com origem/destino com evidência de materiais metálicos; nome não comprova conteúdo 3D.
- Carga16 `Pallets Alto TESTE`: paletes com oferta intencionalmente **muito restrita**: prioritariamente madeireiras/serrarias, até 3 origens x 6 destinos (máximo teórico 18 pares); não pode dominar o mercado. Verificar o 3D para confirmar se são paletes vazios/de madeira.

Não gerar fretes absurdos como adubo de posto, cimento de posto, canavial→batata ou laranja sem evidência, silo→silo indiscriminado, marmoraria sem evidência→tijolos, fábrica de cerveja→granito. Se a DEF de uma empresa contrariar o nome aparente, prevalece prova específica confiável: exemplo `acero` no mapa Minas expedindo `adubo`, `fertilizante`, `equipagrico`, `racao`: classificá-la como agroinsumos naquele mapa, não siderúrgica apenas pelo nome.

## Catálogo SCS

Catálogo offline com cerca de 143 empresas padrão e fontes de fórum/wiki. Na simulação, conferir **cada empresa existente na DEF**: correspondência exata ID ou nome com empresa padrão ⇒ usar ramo do catálogo; se não, analisar como customizada pelo próprio IN/OUT. **Não importar empresas do catálogo.** Um ID parecido (`EuroAcresBR`) NÃO deve ser tratado como `EuroAcres`.

## Cargas do Librelato e variantes

IDs conhecidos:
1 milho; 2 soja; 3 adubo; 4 madeira; 5 pluma de algodão; 6 cimento; 7 sacos de batatas; 8 sacos de laranjas; 9 Bobinas 2; 10 cimento e palete; 11 cimento e cinta; 12 cervejas; 13 tijolos; 14/15 granito; 16 Pallets Alto TESTE; 17 ração mineral laranja (NÃO fruta); 18 xerém; 19/20 sacaria ração; 21 soja alto; 22 milho alto; 23 sorgo alto.
Ler `body_types` e `trailer_def` dos arquivos reais; não fixar a distribuição por grade em código. Auditorias anteriores encontraram cerca de 17 cargas de grade alta e 6 de grade baixa, mas os arquivos podem mudar.

## Bugs anteriores e últimas alterações

Antes a aba gerava 0 cargas ou rejeitava todas porque buscava produtor industrial/fábrica. Depois passou a distribuir cargas, mas gerou rotas incoerentes por nome/setor mal classificado. Foram corrigidas as prioridades por `cargo:`, o catálogo, leitura de ZIPs de mapas variados, a classificação por categoria econômica e as restrições de paletes.

Em 19/10/2026, o diagnóstico do usuário ainda mostrou **8 cargas sem rota** num mapa diferente: `carga14, carga15` (granito), `carga17, carga18, carga19, carga20` (ração), `carga5` (pluma), `carga9` (bobinas). `carga16` (paletes) e `carga23` (sorgo) tinham observações técnicas. Foi corrigido o *fallback* por mercadorias reais para empresas com IDs opacos: pedra/mármore, ração/farelo/suplementos, lavouras com múltiplos grãos, siderurgia com chapa de aço/vergalhões etc. Mantiveram-se bloqueios contra empresas sem evidência.

**Testes feitos após a correção:** oito verificações pontuais de classificação, depois geração end-to-end de SCS em mapa sintético com 11 empresas, 5 cargos (`carga14`, `carga17`, `carga5`, `carga9`, `carga16`), 14 checagens IN/OUT/editor/ausência de rotas absurdas, 13 associações IN/OUT, nenhum cargo/empresa novo, download acionado. **Estes testes são estruturais; não confirmam mercado de fretes em jogo.**

## Trabalho ainda pendente

1. Obter **a DEF Company real do mapa que apresentou as oito cargas sem rota** e a DEF de carga efetivamente usada. Sem esses arquivos não é possível garantir que existam origens/destinos economicamente válidos para todas as oito cargas. Não forçar 100% artificial.
2. Auditar cada cargo: origem, destino, evidência `cargo:`, compatibilidade de body_type/trailer_def e quantidade de empresas.
3. Gerar SCS e verificar ZIP, `editor`, `in`, `out`, colisões, preservação de IDs, remoção de autorizações antigas da **própria entrada**. Um SCS complementar não pode apagar permissões presentes **dentro de outro mod** ativo.
4. Testar no Euro Truck Simulator 2 com **mod principal Librelato ativo**, DEF Companies genéricas 1/2 desativadas, Company específica com prioridade adequada. Conferir `game.log` e o mercado real, inclusive grade alta/baixa. Não declarar resultado definitivo antes de confirmar.

## Estilo de trabalho solicitado

Falar diretamente em português do Brasil, sem notas repetitivas. Fazer correções efetivas no GitHub, preservar todas as abas e não reconstruir o site do zero. Simplificar e profissionalizar o código com prudência, sem regressões. Cada commit deve ser seguido de teste. Quando o usuário pedir continuação, **retomar exatamente do código existente** e registrar honestamente o que foi testado em simulação e o que ainda depende do jogo.
