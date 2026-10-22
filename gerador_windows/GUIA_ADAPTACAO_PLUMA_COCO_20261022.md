# Adaptação regional de pluma e coco — Minas Gerais e Eldorado

**Escopo exclusivamente autorizado:** Minas Gerais e Eldorado. **RBR não deve ser aberto, recriado ou modificado.**

## Relações permitidas automaticamente

| Carga | Onde buscar (OUT) | Onde entregar (IN) |
|---|---|---|
| `carga5` — pluma de algodão | Fazendas do próprio mapa, mesmo que a DEF não registre algodão | Silos, armazéns/galpões, cooperativas, beneficiadoras de algodão, indústrias têxteis e distribuidores com atividade coerente |
| `carga24` — coco | Fazendas do próprio mapa, mesmo sem registro de coco | Supermercados, mercearias, mercadinhos, quitandas, CEASAs e hortifrutis |

O algoritmo não cria empresa, cidade ou prefab; aplica permissões `.sii` somente a empresas **presentes na DEF original**. **Obras, postos de combustível, transportadoras, siderúrgicas e outras unidades incompatíveis não recebem essas cargas.**

## Regra autorizada versus prova original

As permissões recebem marcação `ADICIONAR_ADAPTACAO_REGIONAL` ou `MANTER_ADAPTACAO_REGIONAL`, e `fonte=SIMULACAO_ECONOMICA_REGIONAL_AUTORIZADA`. Isso representa a *logística fictícia plausível*, com uma rede agrícola comercial ampliada conforme pedido do usuário. **Não significa que a DEF original comprovou cultivo de algodão ou coco na fazenda**.

Nos relatórios `QUALIDADE_LOGISTICA_*.json`, os pares simulados aparecem em `pares_simulacao_regional` e os candidatos com editor em `candidatos_simulacao_regional`, **separados** de `pares_economicos_distintos` e `pares_com_evidencia_inout_distintos`.

## Passo a passo para não alterar o RBR

1. Abra `ETS2_Company_Gerador.exe`.
2. Escolha **Somente MINAS + ELDORADO — adicionar pluma/coco, NÃO mexer no RBR**. Esta seleção já é a **padrão nesta compilação**.
3. Indique os arquivos originais do reboque Librelato: MOD principal, DEF Company 1 e DEF Company 2, mais o TXT das 24 cargas.
4. Indique **DEF Minas**, **DEF Eldorado**, suas duas Companies existentes e uma **pasta nova de saída**. **Nenhum arquivo do RBR é exigido nesse modo**.
5. Escolha **AUDITAR / CORRIGIR SCS EXISTENTE** para atualizar as duas Companies sem sobrescrever os originais.
6. Confira `AUDITORIA_MINAS_GERAIS.json`, `AUDITORIA_ELDORADO.json`, `RESUMO_VALIDACAO_*.txt` e `MATRIZ_ENSAIOS_ETS2_*.csv`.
7. Teste as duas Companies corrigidas, **um mapa por vez**, em perfil de testes do ETS2. Verifique frete no mercado, modelo de carga, coleta, entrega e `game.log.txt`.

**Modo CLI equivalente:** `--cli --audit-existing --only-mg-eldorado` mais `--mod`, `--def1`, `--def2`, `--txt`, `--minas`, `--existing-minas`, `--eldorado`, `--existing-eldorado` e `--output`.

**Proteção adicional:** o botão **5. FINALIZAR OFFLINE** é uma rotina global de 3 mapas e fica bloqueado quando você seleciona **Somente MINAS + ELDORADO**. Não mude para **Todos** se sua intenção é preservar o RBR. Para estes dois mapas, use as ações 3 e 4.

**Aviso:** ver um par de empresas no relatório prova apenas o cadastro no SCS e sua plausibilidade econômica, não a exibição/entrega dentro do ETS2. Ausência de editor em Minas pode impedir comprovar a rota territorial sem recursos adicionais reais.
