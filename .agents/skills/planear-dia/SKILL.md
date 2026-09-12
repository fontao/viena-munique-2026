---
name: planear-dia
description: Planeia ou replaneia um dia da viagem de ponta a ponta e escreve-o nos dois documentos. Usar quando se pede para mudar o programa de um dia, acrescentar ou trocar uma visita, ajustar horários, inverter a ordem da tarde, ou quando se pergunta se um dia ainda cabe no tempo que tem.
argument-hint: [n.º do dia] [o que mudar]
allowed-tools: Bash(python scripts/verificar.py *), Bash(python scripts/meteo.py *), Bash(agy *), Read, Edit, Grep, Glob, WebSearch, WebFetch, mcp__osm__route, mcp__osm__route_matrix, mcp__osm__geocode
---

# Planear ou replanear um dia

O objetivo não é produzir um programa bonito. É produzir um programa que **fecha
no relógio** e que fica escrito igual nos dois documentos.

As regras de escrita estão em `.agents/referencia/convencoes.md` (língua,
pontuação, marcadores, número de pessoas, voz). Os blocos de HTML a copiar estão
em `.agents/referencia/anatomia-html.md`. As fontes aceitáveis estão em
`.agents/referencia/fontes.md`.

## 1. Ler o que já lá está, primeiro

Ler a secção do dia em `itinerario_viagem.md` **inteira**, incluindo os blocos
`> ### Porque é que este dia foi reconstruído`. Esses blocos existem para evitar
que uma revisão desfaça outra sem dar por isso.

Se aquilo que se está prestes a mudar já foi decidido e justificado antes, **isso é
uma informação, não um obstáculo**. Diz-se ao utilizador o que a decisão anterior
resolvia e o que se perde ao invertê-la, e segue-se em frente.

Ler também a secção `## 🔄 Trocar dias? O que se mexeu e o que fica`, que guarda
decisões já tomadas e decisões já rejeitadas, com a razão de cada uma.

## 2. Recolher os factos antes de escrever uma hora

Nunca estimar de cabeça:

- **Tempos de carro:** `osm` MCP, ferramenta `route`, com todos os pontos do dia
  numa só chamada, que devolve o desdobramento por troço. O resultado é trânsito
  livre, portanto é um **piso** e não uma estimativa. Somar margem.
- **Comboios:** ÖBB, DB ou Westbahn. Nunca o `osm`. Se o bilhete já está comprado,
  a hora é a do bilhete e não se discute.
- **Horários e preços:** fonte primária da lista, aberta agora. Se não se abriu, o
  facto fica `⚠️`.
- **Luz do dia:** a hora do pôr do sol decide a ordem da tarde. Este roteiro já se
  enganou nisso uma vez, e ia fotografar Oberammergau no escuro.
- **Tempo:** `python scripts/meteo.py --cidade <nome>`, se o dia tiver programa ao ar
  livre. Até meados de setembro os números são climatologia e não previsão, e isso
  diz-se ao utilizador em vez de os apresentar como previsão. Se o `meteo.py`
  sugerir uma troca de dias, **a decisão é do utilizador**, porque a sugestão olha
  só para a chuva e não sabe de bilhetes com hora marcada nem da janela do carro.

## 3. Montar o dia e pô-lo à prova no relógio

Escrever a cadeia completa, bloco a bloco, sem buracos:

```
- **10:30 – 12:05**: Condução de Augsburg até Hohenschwangau (**113 km, ~1h35**).
- **12:05 – 14:00**: **115 minutos de margem. É isto que faz o dia funcionar.**
```

Cada bloco começa quando o anterior acaba. Confirmar, antes de dar o dia por feito:

- **Bilhetes de hora marcada:** respeitar a antecedência exigida por quem os
  vende. Neuschwanstein pede 90 a 120 minutos na aldeia, e o levantamento é
  obrigatório.
- **Horas de fecho:** as bilheteiras fecham antes das atrações.
- **A janela do carro:** levantamento na sexta às 17:00 em Augsburg, devolução na
  terça às 17:00 no aeroporto de Munique. Nada pode precisar do carro fora disto.
- **Refeições:** um jantar de 6 pessoas num fim de semana de Oktoberfest reserva-se.
- **Quem está lá:** 4 pessoas até à noite do Dia 3, 6 a partir daí.
- **O regresso:** o dia acaba em casa, e a condução de volta conta.

Esta passagem faz-se **antes de escrever**, sobre o plano ainda em rascunho. O
`verificar.py` só lê os ficheiros e não tem nada a dizer sobre um dia que ainda só
existe na cabeça. Corre-se a seguir, no passo 5.

## 4. Escrever nos dois documentos

**`itinerario_viagem.md` é o documento que manda, e é aí que se escreve primeiro.**

No markdown:

- a linha `**⏰ Acordar HH:MM · Sair HH:MM**` por baixo do cabeçalho;
- os blocos horários, com os números a negrito e a razão de cada um;
- subpontos indentados para o detalhe (`⚠️` riscos, `🎫` bilhetes, `🅿️`
  estacionamento, `🏞️` alternativa se sobrar tempo);
- se a mudança contraria uma decisão anterior, um bloco `> ### O que estava errado
  e mudou`, a explicar o quê, porquê e o que custou a troca.

Em `index.html`, no painel `#day-view-N`: o cartaz do dia (`day-banner-tag`,
título, `day-banner-meta`), os `timeline-node` pela mesma ordem, e o separador
`data-day="N"` se o resumo do dia mudou. Os blocos a copiar estão em
`.agents/referencia/anatomia-html.md`. Atenção a um pormenor fácil de falhar: o
markdown usa `–` nos intervalos e as `time-pill` do HTML usam `→`.

Se o dia ganhou ou perdeu um sítio, atualizar também o array `locations` do mapa
(ver a skill `mapa`) e, se a rota mudou de cidade, a lista `STOPS` do `scripts/meteo.py`.

## 5. Fechar

1. `python scripts/verificar.py --dia N` e depois `python scripts/verificar.py`, sem 🔴. Agora sim:
   o dia já está escrito e há alguma coisa para verificar.
2. Segunda opinião do Gemini sobre a exequibilidade do dia, com a skill
   `segunda-opiniao`. É um modelo com pesquisa própria e apanha horários
   impossíveis que uma autorrevisão não apanha.
3. Ao utilizador: o que mudou, porquê, e **o que custou**. Que horas se
   sacrificaram, o que ficou de fora, o que ficou por confirmar.

Nunca dar um dia por fechado com um facto inventado. Um `⚠️` honesto vale mais do
que um `✅` que ninguém verificou.
