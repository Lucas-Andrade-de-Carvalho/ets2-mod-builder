# Auditoria técnica — ETS2 Company Logistics (v4)

Escopo: os sete arquivos originais do repositório e os fluxos HTML de Arquivos, Empresas, Logística, Cadeias, Gerar SCS e Criação de Companys; testes automatizados e documentação. Esta revisão melhora segurança e confiabilidade, não promete 100% de cobertura semântica de qualquer mapa.

## Corrigido

| Severidade | Falha identificada | Tratamento |
| --- | --- | --- |
| Alta | Catálogo SCS podia sobrescrever classificação informada manualmente ao simular | Classificação confirmada preservada; consulta ao catálogo fica auxiliar |
| Alta | Leitura reconhecia só a primeira unidade `cargo:` por arquivo | Parser suporta vários campos `cargo:`, incluindo arquivos com blocos múltiplos |
| Alta | Referências grandes eram ignoradas silenciosamente | Erro explícito com caminho; limite de 1 MB para um IN/OUT textual |
| Alta | Arquivos e setores podiam ser interpretados a partir de nomes de `.sii` | Perfil logístico novo considera somente valores reais declarados no `cargo:` |
| Média | Neutralização por busca textual podia modificar comentários e destruir unidades vazias | Máscara de comentários + neutralização pelos campos localizados; preserva arquivo sem `cargo:` |
| Alta | ZIP comprimido podia expandir excessivamente e travar o navegador | Limites de entradas, tamanho individual e tamanho expandido, nos dois modos de leitura |
| Média | Dois modos de geração distintos eram pouco evidentes | Interface explica modo de atualização e modo de criação com neutralização integral |
| Média | Motor HTML incorporado podia divergir de `creator_tab.js` | Teste estático de sincronismo e utilitário `scripts/sync-company-engine.cjs` |
| Média | `engine_universal.js` histórico podia ser confundido com a versão em produção | Marcado como legado, documentado como não carregado por `index.html` |
| Média | Alteração de outra aba podia quebrar JavaScript em silêncio | CI verifica sintaxe dos três scripts, preservação das seis abas e regressão funcional |

## Pipeline de qualidade

`node tests/project-integrity.cjs` confere estrutura, abas e sincronismo. `node tests/company-creator.smoke.cjs` testa carga/Company, ZIP, parser com comentários, múltiplas referências, arquivos grandes, classificações, economia, geração `.scs`, neutralização integral e download. Ambos são executados por GitHub Actions usando Node 22. O site distribuído permanece um único HTML que roda no navegador, sem Node ou Python para o usuário.

Para editar `creator_tab.js` no futuro, execute `node scripts/sync-company-engine.cjs` antes de publicar. O utilitário usa uma função de substituição para que sequências como `$&` no código não sejam interpretadas como conteúdo de substituição e não corrompam o HTML.

## Limites conhecidos e trabalho posterior

1. **Teste in-game pendente:** a auditoria automatizada é estrutural. Conferir ETS2, `game.log`, prioridade do mod sobre a DEF original e renovação do mercado de fretes.
2. **Compatibilidade econômica exige critérios por mercadoria:** nem toda DEF declara explicitamente a mercadoria do reboque; as inferências não devem ser promovidas a fatos. Empresas vazias são resultado válido.
3. **HashFS não é ZIP:** necessita extração prévia; o browser não regrava o formato HashFS da SCS.
4. **Fluxos diferentes:** `Gerar SCS` reorganiza uma Company existente; `Criação de Companys` substitui integralmente permissões antigas, neutralizando caminhos. Não intercambiar as regras dos dois modos.
5. **Parser de texto SII:** novas variantes de sintaxe devem ser acompanhadas de exemplos reais e testes. Não adivinhar com base em nomes de pastas ou forçar rotas.
6. **HTML monolítico:** manter o HTML único para uso offline e o fonte separado para manutenção. Uma modularização maior pode ser feita futuramente, desde que não quebre compatibilidade offline e as seis abas.
