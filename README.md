# ETS2 Company Logistics — Universal

Versão simplificada do gerador de Company para Euro Truck Simulator 2, usando **dois arquivos**.

## Uso

1. Abra `index.html` no Chrome ou Edge.
2. No campo **DEF Company do mapa**, carregue o `.zip` ou `.scs` ZIP que contém as empresas (`company/` ou `def/company/`).
3. Em **DEF das cargas do Librelato**, carregue o ZIP com `cargo/`, `vehicle/` e `cargo.librelato.sii`, como `def(1).zip`.
4. Clique **Gerar Company simulada**. O site identifica o nome do mapa pelo arquivo e considera automaticamente cargas de **grade baixa** e **grade alta**.
5. O arquivo `DEF_Company_Librelato_<MAPA>_Universal.scs` será baixado quando houver cargas e destinos válidos nas duas grades.

## O que faz

- Classifica as empresas a partir de IDs e nomes encontrados nos arquivos.
- Atribui cargas apenas a setores compatíveis, por exemplo milho: fazenda → silo, moinho ou fábrica de ração.
- Conserva arquivos das empresas e editores do mapa, neutralizando as antigas referências `IN/OUT` que constem no arquivo fornecido.
- Cria os arquivos `def/company/<empresa>/in|out/<carga>.sii` sem precisar anexar as antigas DEF Companies 1 e 2.
- Inclui no SCS resultante a DEF das cargas (cargo_data e definições de veículo presentes no ZIP da segunda entrada).
- Preserva empresas vazias quando não houver correspondência econômica reconhecível.
- Não obriga o uso de uma cidade, empresa ou nome de mapa específico.

## Limites reais

- O arquivo do mapa precisa ser um ZIP/SCS com pasta `company/` ou `def/company/`. Se for HashFS, deve ser extraído previamente.
- Não é possível inferir com segurança o setor de toda empresa de qualquer mapa apenas de um ID opaco. Empresas não reconhecidas permanecem vazias, e o diagnóstico mostra as cargas não distribuídas.
- A geração é bloqueada se não houver ao menos uma carga economicamente válida para cada uma das carrocerias `alta` e `baixa`.
- O sistema reproduz cadeias por mercadoria, mas o ETS2 combina qualquer origem OUT válida com qualquer destino IN válido para a mesma carga. Para evitar fretes silo→silo, esta versão não autoriza automaticamente silos a expedir grãos que também recebem.
- A validação em ZIP **não substitui** um teste real no ETS2 1.61.1, incluindo trailer_defs, métodos de carga, geografia, mercado de fretes e `game.log`.
- No Gerenciador de Mods, mantenha o mod principal Librelato e a Company exclusiva gerada ativos e **desative as DEF Companies genéricas 1 e 2**.

## Ajustes no reconhecimento das empresas e cargas

- As cargas personalizadas do Librelato com IDs `carga1`, `carga2` etc. são identificadas separadamente das definições genéricas como `corn_b` e `soybean_b`.
- Reconhecimento ajustado para `Sojaalto`, `Milhoalto`, `Sorgoalto`, `Cervejas`, `Sacos de Batatas` e `Sacos de Laranjas`.
- IDs compactos rurais (`faz_01`, `agropec...`, `silos...`) são reconhecidos quando indicam atividade econômica concreta.
- A auditoria apresenta exemplos de empresas desconhecidas e motivos de rejeição. Empresas incertas não são transformadas artificialmente em produtoras.
- Teste estrutural adicional: uma DEF sintética com 23 cargas Librelato e cinco genéricas produziu ligações de grade alta e baixa, ignorando corretamente as cargas genéricas.

## Verificações

- Sintaxe do motor JavaScript verificada.
- Teste de ponta a ponta com ZIPs simulados: milho grade baixa (fazenda → silo), tijolos grade alta (olaria → construtora).
- SCS resultante foi reaberto e confirmou `cargo_data`, manifest, empresas, arquivos editor e neutralizadores, sem modificar os originais.

**Status:** gerador funcional em testes estruturais; teste in-game com o mod e mapa reais ainda pendente.
