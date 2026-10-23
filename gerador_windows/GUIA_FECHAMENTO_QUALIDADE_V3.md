# Company Logistics V3 — fechamento de qualidade

Esta revisão é a consolidação do gerador de Companies do Euro Truck Simulator 2 para **Minas Gerais, Eldorado e RBR**, com foco em não exigir novas rodadas de correções por falhas triviais ou silenciosas. O produto é uma **candidata técnica à entrega**; a comprovação de cada frete em ETS2 continua distinta dos testes automatizados.

## Proteções obrigatórias desta revisão

**Saídas versionadas e reproduzíveis.** Cada Company exportada agora recebe um nome contendo uma impressão digital do arquivo de entrada e do **conteúdo real de saída** (`ETS2_<MAPA>_AUDITADA_V25_<entrada>_<saida>.scs`). Processar a mesma origem sem mudanças produz o mesmo arquivo, sem sobrescrever uma versão anterior; se a DEF, as regras ou a Company corrigida mudarem, o novo conteúdo recebe outro nome. As Companys antigas do usuário permanecem intactas.

**Publicação em conjunto com rollback.** O programa prepara os relatórios e Companies numa área temporária; ao publicar no diretório final, desloca arquivos preexistentes para um diretório de restauração. Se houver erro no meio da publicação, remove os resultados incompletos e tenta restaurar integralmente os anteriores. Quando termina com sucesso, remove um marcador antigo `AUDITORIA_INCOMPLETA.txt`.

**Verificação depois de compactar.** O gerador reabre cada novo `.scs` e verifica integridade ZIP, presença de todos os arquivos, invariantes sobre entradas originais não modificadas, **igualdade entre permissões ativas do SCS e o relatório**, e inexistência de duplicidades ativas para empresas presentes na DEF. O campo `validacao_pos_exportacao` em `AUDITORIA_<MAPA>.json` contém a comprovação automatizada. Isso NÃO substitui testar o motor do ETS2.

**Leitura conservadora de cargos.** Aceita comentários `#` e `//` ao final de `cargo:`. Se encontrar um campo `cargo: cargo.*` que pareça ativo mas cujo formato não pode ser interpretado com segurança, **interrompe a publicação**. Nunca ignora a mercadoria para criar duplicatas ou alterar permissões fora de controle.

**Proteção de cadeias.** Quando uma Company recebida tinha todas as cadeias cadastradas, o gerador se recusa a publicar uma nova versão que deixe alguma carga sem nenhuma origem e destino. Isso não autoriza inventar fornecedores; sinaliza claramente o bloqueio para correção fundamentada pela DEF.

**Rastreabilidade econômica.** As decisões são separadas em comprovadas por IN/OUT original, inferidas pelo setor, herdadas ainda sem evidência, **adaptação regional autorizada** e situações pendentes. `TRIAGEM_PENDENCIAS_3_MAPAS.csv` permite examinar as falhas dos três mapas sem confundir 24/24 cadastro com teste de jogo concluído.

## Política por mapa

- **RBR:** reconhecer empresas fictícias pelos seus IN/OUT, incluindo portos, extrações de toras, postos de combustível, comércio agrícola, silos e distribuidoras. Não criar produção de pluma/coco sem comprovação.
- **Eldorado:** reconhecer centros multissetoriais e terminais químicos pelos fluxos reais, evitando colocar cargas de supermercado ou obra em instalações que manipulam produtos incompatíveis.
- **Minas Gerais:** reconhecer revenda de máquinas agrícolas, descartáveis, recicladoras e outros setores por entradas e saídas reais.
- **Exceção autorizada somente Minas/Eldorado:** pluma pode partir de fazendas existentes para silos, cooperativas, armazéns e beneficiadoras; coco pode partir de fazendas para supermercados, mercearias, CEASAs e hortifrutis. Não levar pluma a lojas genéricas de alimentos, postos ou obras; não levar coco a obras, mineradoras ou indústrias químicas. Essas associações têm status de simulação econômica autorizada.

## Instrução única de processamento

1. Faça backup das três Companies atuais e abra o novo executável.
2. Selecione **Todos os 3 mapas**. Não confunda com a opção padrão `Somente MINAS + ELDORADO`, que é para processar dois mapas preservando o RBR.
3. Indique MOD Librelato, DEF1, DEF2, TXT de cargas, as três DEFs dos mapas e as três Companies existentes; use uma pasta nova de saída.
4. Execute **3. AUDITAR / CORRIGIR SCS EXISTENTE**, sem marcar `Apenas auditar`.
5. Confira os três `.scs` versionados, `AUDITORIA_*.json`, `QUALIDADE_LOGISTICA_*.json`, `PAINEL_GERAL_LOGISTICA_V3.json` e `TRIAGEM_PENDENCIAS_3_MAPAS.csv`. Não coloque uma Company antiga e uma nova do mesmo mapa ativas ao mesmo tempo no Gerenciador de Mods.
6. Teste **um mapa de cada vez**, em perfil do ETS2 dedicado, e confirme ofertas, modelos, carrocerias, coleta e entrega, guardando `game.log.txt`. O checklist `MATRIZ_ENSAIOS_ETS2_<MAPA>.csv` prevê uma linha por carga.

## Limites que nenhum algoritmo pode resolver só com estes relatórios

- **Minas Gerais sem company_def de cidade/prefab:** os relatórios fornecidos mostram 0 referências editor válidas. Sem fonte legítima adicional não é possível verificar onde cada empresa aparece no mapa. Não inventar coordenadas ou prefabs.
- **Empresas sem ramo seguro:** muitas empresas fictícias continuam sem prova suficiente de atividade. O programa pode preservar as permissões antigas com identificação de pendência, mas não pode afirmar que elas são corretas.
- **Homologação ETS2:** mesmo 100% dos testes automatizados não valida instalação do conjunto de mods, dependências, prioridade, versões, visibilidade de fretes ou entregas reais.

**Critério de excelência:** zero modificações silenciosas, ausência de fretes fisicamente ilógicos comprovados, rastreabilidade de toda mudança, exportação determinística e verificável, nenhum original sobrescrito e reconhecimento explícito dos impedimentos que dependem de fontes externas. A resposta a uma evidência ausente deve ser um bloqueio diagnosticado, nunca um dado inventado.
