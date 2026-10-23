# COMPANY LOGISTICS V3 — CHECKLIST FINAL DE SEGURANÇA

O objetivo é reduzir retrabalho sem declarar 100% perfeito antes de testar os três mapas no ETS2.

## Mudanças verificadas no código

1. **Arquivos .scs imutáveis por versão:** o nome de saída contém o hash da entrada e o hash da saída. A mesma entrada produz o mesmo arquivo. Versões diferentes não devem sobrescrever resultados anteriores; colisão de nomes com conteúdo distinto bloqueia a publicação.
2. **Integridade interna:** pós-exportação reabre o ZIP, testa integridade, compara IN/OUT com o inventário da auditoria e bloqueia duplicatas reconhecidas.
3. **SII com codificações antigas:** campos cargo são neutralizados em bytes, preservando comentários cp1252/Latin-1, UTF-8 com BOM e CRLF.
4. **Publicação com recuperação:** relatórios antigos são restaurados em caso de falha; aviso AUDITORIA_INCOMPLETA.txt registra o problema.
5. **Proteção de cadeias:** se a Company tinha o catálogo inteiro com origem/destino, o programa bloqueia a publicação que eliminaria uma cadeia. Não fabrica fornecedor.
6. **Fila conjunta:** TRIAGEM_PENDENCIAS_3_MAPAS.csv organiza revisão por empresa, carga, IN/OUT e prioridade.
7. **Empresas fictícias:** identificação por atividade e produtos IN/OUT, sem depender de cadastro de empresas reais na internet.
8. **Pluma/coco:** distribuição simulada em fazendas e destinos plausíveis autorizada somente em Minas Gerais e Eldorado; RBR não recebe a exceção.

## Para usar

- Faça backup das Companies originais e corrigidas.
- Selecione Todos os 3 mapas e AUDITAR / CORRIGIR SCS EXISTENTE somente quando quiser consolidar os três. Para um mapa, use escopo isolado.
- Escolha pasta de saída diferente dos insumos, conservando versões antigas.
- Confirme 24 tipos no catálogo Librelato; examine AUDITORIA, QUALIDADE_LOGISTICA e PAINEL_GERAL_LOGISTICA_V3 dos três mapas.
- Verifique TRIAGEM_PENDENCIAS_3_MAPAS.csv e os CSVs de pendências; hipóteses plausíveis ainda não são prova do produto na DEF.
- Preencha MATRIZ_ENSAIOS_ETS2_<MAPA>.csv com mercado de fretes, modelo da carga, empresa/cidade de coleta e entrega e game.log.txt.

## Limites reais

- Minas Gerais: os arquivos de auditoria anteriores não contêm referências company_def com cidade/prefab suficientes para comprovar rotas territoriais.
- Eldorado/RBR: par IN/OUT cadastrado e referências editor não garantem frete visível e concluído dentro do ETS2.
- Os testes automatizados comprovam cenários sintéticos e regressões; não certificam todas as Companies reais.

**Regra final:** Gerador compilado/testado NÃO significa Companies homologadas no ETS2. Somente declarar cada mapa homologado com as 24 entregas e game.log verificados.
