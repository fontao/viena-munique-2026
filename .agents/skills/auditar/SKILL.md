---
name: auditar
description: Auditoria completa ao dossiê. Exequibilidade dos sete dias, prazos vencidos, preços por confirmar, coerência entre os documentos, e segunda opinião do Gemini. Usar antes de dar uma revisão por fechada, quando se pergunta se está tudo bem, ou quando se retoma o dossiê depois de semanas parado.
allowed-tools: Bash(python scripts/verificar.py *), Bash(python scripts/meteo.py *), Bash(agy *), Read, Edit, Grep, Glob, WebSearch, WebFetch
effort: high
---

# Auditoria ao dossiê

Uma passagem completa. Demora, e é para demorar. Corre-se antes de fechar uma
revisão, não a cada alteração. Para uma verificação rápida de coerência existe a
skill `sincronizar`.

## Coerência interna

```!
python scripts/verificar.py
```

Resolver todos os 🔴 e classificar cada ⚠️ como real ou como legítimo e explicado.

**Aqui os avisos vão mais longe do que na skill `sincronizar`.** Lá basta decidir
se os dois ficheiros concordam. Aqui, um preço assimétrico que pese no orçamento
abre-se na fonte primária e confirma-se o valor verdadeiro, mesmo que os dois
documentos já concordem um com o outro. Dois ficheiros de acordo sobre um número
errado é exatamente a falha que esta skill existe para apanhar.

## Prazos, à data de hoje

O dossiê envelhece sozinho. Percorrer `## 🚨 Prazos Críticos` e o
`## 🎫 Hub de Bilhetes`:

- Prazo passado e ainda `🔴`: perguntar ao utilizador o que aconteceu. Não assumir
  que foi tratado, nem apagar a linha.
- Prazo a menos de duas semanas: sobe na lista e é a primeira coisa a dizer no
  relatório final.
- Prazo cumprido: risca-se com `~~...~~`, marca-se `✅` e escreve-se o valor pago.

## Exequibilidade dos sete dias

Para cada dia, com o `osm` MCP a validar os troços de carro. Uma chamada `route`
por dia, com todos os pontos de uma vez, e não uma chamada por troço:

- A cadeia horária fecha, incluindo o regresso a casa.
- As antecedências dos bilhetes com hora marcada estão respeitadas.
- Nada precisa do carro fora da janela de aluguer, de sexta às 17:00 a terça às
  17:00.
- O número de pessoas está certo em cada linha.
- A ordem da tarde respeita a hora do pôr do sol.

Lembrar que o OSRM dá trânsito livre. É um piso, não uma estimativa.

## Factos que envelheceram

Listar tudo o que está `⚠️` e tem mais de dois meses. Os que pesam no orçamento ou
numa decisão abrem-se na fonte primária e atualizam-se. Os restantes ficam `⚠️`, e
**não se promovem a `✅` só por parecerem plausíveis**.

Sinais de que um facto apodreceu: preços dos castelos da Baviera, que mudam em
janeiro; horários de época, que na maioria mudam a 15 de outubro e a 28 de março;
janelas de reserva da Oktoberfest; e horários de comboio, que mudam em dezembro.

## Tempo

Se faltarem menos de 16 dias para a viagem, correr `python scripts/meteo.py --matriz` e
avaliar as sugestões de troca **à luz das restrições reais**: bilhetes de hora
marcada, janela do carro, e o grupo só ser de seis a partir do Dia 3. A sugestão
do script olha só para a chuva e não sabe nada disto.

## Segunda opinião

Obrigatória nesta skill. A forma está na skill `segunda-opiniao`. Pedir ao Gemini
uma passagem por cada dia e outra pela tabela de prazos, **pedindo tudo o que
encontrar** e filtrando depois. Cada coisa que ele levantar confirma-se em
fonte primária antes de se tocar nos documentos.

## Relatório

Ao utilizador, por esta ordem:

1. **O que tem de ser tratado esta semana:** prazos e decisões com data.
2. **O que está partido:** erros de coerência e horários impossíveis, com o que se
   fez a cada um.
3. **O que continua por confirmar:** a lista dos `⚠️` que sobreviveram, e porquê.
4. **O que se mudou nos documentos.**

Sem embelezar. Se ficou coisa por verificar, diz-se qual.
