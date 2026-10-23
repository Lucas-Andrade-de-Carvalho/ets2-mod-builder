# COMPANY LOGISTICS — consolidação dos três mapas

**Escopo:** Minas Gerais + Eldorado + RBR.

Esta versão gera candidatas para teste; não afirma que uma Company foi homologada no jogo porque passou nos testes de código.

## Fontes necessárias

Na aplicação Windows, são necessários os arquivos originais **MOD principal Librelato**, **DEF Company 1**, **DEF Company 2** e **TXT das 24 cargas**; além de **DEF do Minas**, **DEF do Eldorado**, **DEF do RBR** e as **três Companies existentes** (.scs). Editor externo de Minas, quando existente, pode ser fornecido para comprovar cidades/prefabs. Não misture Company de um mapa com a DEF de outro.

## Operação recomendada

1. Faça backup das três Companies. Escolha uma pasta NOVA para saída, separada de todos os insumos.
2. Na seção de escopo, mude de `Somente MINAS + ELDORADO` para `Todos os 3 mapas`.
3. Selecione os 10 arquivos: 4 originais do reboque, 3 DEFs dos mapas e 3 Companies existentes.
4. Execute **3. AUDITAR / CORRIGIR SCS EXISTENTE** e deixe a caixa **Apenas auditar, sem gerar SCS** desmarcada.
5. A execução cria três novas Companies .scs, relatórios separados e `PAINEL_GERAL_LOGISTICA_V3.txt`, `TRIAGEM_PENDENCIAS_3_MAPAS.csv` e `TRIAGEM_PENDENCIAS_3_MAPAS.json`.
6. Confira que as 24 cargas **continuam** tendo pelo menos um par de origem/destino em cada mapa onde o par já existia. Se todas estavam completas e alguma ficaria sem par, o programa **bloqueia a publicação**, em vez de apresentar um falso resultado definitivo.
7. Analise a fila de pendências, da prioridade 1 à 4. Permissões com **IN/OUT original da mercadoria** e setor condizente devem ser priorizadas; somente nomes/arquivos da Company herdada não provam atividade econômica.
8. Coloque em um perfil exclusivo do ETS2 a Company corrigida de **cada mapa separadamente**, junto com o respectivo mapa e o MOD do reboque. Confirme disponibilidade e conclusão do frete e verifique o game.log.

**Atenção:** o botão **5. FINALIZAR OFFLINE** aplica um gate rigoroso: exige 24/24 pares econômicos/editor e zero pendências documentais nos três mapas. Ele pode bloquear a saída corretamente mesmo depois de exportar as três candidatas com o botão 3. Não interprete isso como falha da geração.

## Política econômica fixa

- Empresas fictícias são analisadas por sua **atividade e IN/OUT documentados**, não pela existência da empresa no mundo real.
- **RBR:** a produção de algodão ou coco em fazendas não é inventada; mantém-se a correção dos terminais, portos, madeireiras, fazendas, silos e postos.
- **Minas Gerais e Eldorado:** regra regional aprovada: `carga5` (pluma) sai de fazendas existentes e é entregue em silos/armazéns/cooperativas/beneficiadoras; `carga24` (coco) sai de fazendas e chega a CEASAs, mercados, mercearias e hortifrutis. Essas rotas são identificadas como **adaptação regional**, não como produção comprovada na DEF original.
- Obras e postos não recebem pluma/coco por essa exceção. Não transformar mercadorias dos armazéns em prova de fabricação própria.
- Preservar arquivos originais, identificar permissões herdadas suspeitas e garantir que toda alteração tenha trilha de auditoria.

## Quais arquivos usar para a próxima revisão

Para cada mapa, anexe:
- `AUDITORIA_<MAPA>.json`
- `COBERTURA_MAXIMA_<MAPA>.csv`
- `PENDENCIAS_CLASSIFICACAO_<MAPA>.csv`
- `QUALIDADE_LOGISTICA_<MAPA>.json` (quando gerado)

Para a análise conjunta, anexe também `TRIAGEM_PENDENCIAS_3_MAPAS.csv` e `PAINEL_GERAL_LOGISTICA_V3.json`.

Se desejar que os **arquivos .scs reais sejam revisados e corrigidos fora do seu gerador**, anexe os três .scs, as três DEFs originais e os arquivos do reboque. **Só os relatórios não bastam para reescrever com segurança os .scs originais.**

**Resultado de sucesso verdadeiro:** associação economicamente coerente + arquivo SCS estruturalmente íntegro + frete disponibilizado, coletado e entregue no ETS2 sem erros associados. Não confundir 24/24 cadastro com homologação de jogo.
