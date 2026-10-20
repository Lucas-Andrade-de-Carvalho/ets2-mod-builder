# Qualidade V5 — inteligência logística por evidências

## Critérios de autorização
- Empresas: apenas as presentes na DEF do mapa.
- Mercadorias: apenas as presentes na DEF do reboque.
- As decisões exigem IN/OUT no sentido correto, destino e origem distintos e carroceria compatível.
- A categoria econômica não vale como prova de produto físico idêntico: milho não é sorgo; metal/sucata não são bobinas; algodão bruto não é pluma.
- Se não houver compatibilidade suficiente, a empresa fica sem novas cargas e as permissões anteriores são neutralizadas.
- Não inferir a identidade de um produto apenas do ID numérico cargaN. Uma descrição @@... sem tradução resolvida fica pendente.

## Qualidade da evidência
- Documental: o produto é identificado em cargo: da DEF original. Não é verificação presencial de uma empresa real.
- Categoria relacionada: há produto fisicamente próximo, mas a mercadoria exata não está comprovada (exemplo: pedras vs. granito).
- Inferida: é uma hipótese apoiada pela movimentação IN/OUT, apresentada como tal.
- A base de conhecimento contém 13 referências rastreáveis e está incorporada ao HTML offline. A consulta online atualiza o catálogo do próprio projeto; não é pesquisa aberta com um LLM.

## Validação
- CI: integridade do HTML e das seis abas, sincronismo da base documental, parser SII/ZIP e testes da geração de SCS.
- O empacotador verifica cargos declarados no ZIP final pelo mesmo parser utilizado na leitura.
- Os dados de teste não substituem ensaios no ETS2 com ordem de mods, game.log e atualização da economia.

## Motor V6 — evidência econômica estruturada
- A: cargo idêntico no IN/OUT; B: contexto econômico forte (setor + fluxo IN/OUT correlato); C: hipótese contextual conservadora; D: incompatível/sem evidência.
- Relações B/C nunca são relatadas como prova documental da DEF; apenas empresas e cargos reais entram no arquivo final.
- Cimento nas lojas e pré-moldados, bobinas nas siderúrgicas/metalúrgicas, sorgo em suprimentos pecuários, pluma beneficiada e retorno de paletes têm verificadores distintos; cereal não é ração industrial, chapa não é bobina, algodão bruto não é pluma.
- Registros de decisões contextuais aceitas ficam no diagnóstico. A natureza ambígua de “Pallets Alto TESTE” permanece pendente.


## V6.1 — categoria como regra principal
Uma mercadoria literal da DEF é prova forte; a categoria nos IN/OUT ou atividade da empresa é inferência sinalizada, mesmo quando habilita carga. Empresas podem atuar nos dois sentidos por estoque/distribuição. Cargas não são impostas a setores incompatíveis, e um SCS requer empresa de saída e outra de entrada.
