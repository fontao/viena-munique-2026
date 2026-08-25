---
name: catalogo
description: Faz a gestão do catálogo de opções pesquisadas, ou seja, o que se pode fazer numa cidade, com preço, horário e fonte, antes de entrar no roteiro. Usar quando se pede para pesquisar sítios, restaurantes ou bares, para comparar alternativas, ou quando se quer saber o que ficou de fora do plano e porquê.
argument-hint: [cidade ou tema]
allowed-tools: Read, Edit, Write, Grep, Glob, WebSearch, WebFetch, mcp__osm__geocode, mcp__osm__find_nearby_pois
---

# O catálogo de opções

O `catalogo_viena.md` é **o conjunto de onde o roteiro é escolhido, e não o
roteiro**. Guarda mais opções do que cabem na viagem, de propósito: quando um dia
tem de mudar, a alternativa já está pesquisada e com preço, em vez de ser
pesquisada à pressa.

Não existe catálogo equivalente para a Baviera. Se se pesquisar a fundo Munique,
Augsburg ou os Alpes, cria-se um `catalogo_munique.md` com a mesma estrutura.

## A diferença que não se pode perder

| | Catálogo | Itinerário |
|---|---|---|
| Contém | tudo o que foi considerado | só o que foi escolhido |
| Horas | horário de funcionamento | hora a que o grupo lá está |
| Pessoas | preço por pessoa | total para 4 ou para 6 |
| Estado | pesquisado ou descartado | agendado |

**Nada passa do catálogo para o itinerário sem a skill `planear-dia`.** Uma opção
catalogada tem preço e horário. Um bloco do roteiro tem de caber no relógio do dia,
que é coisa diferente.

## Uma entrada nova

O que uma opção tem de trazer para ser utilizável mais tarde:

- **Onde é**, com morada, e com coordenadas se for entrar no mapa (`osm` MCP,
  ferramenta `geocode`).
- **Quanto custa**, por pessoa, e se existe bilhete de grupo.
- **Quando abre**, com atenção à época. Muitas atrações mudam de horário a 15 de
  outubro e a 28 de março, e a viagem é dias antes dessa fronteira.
- **Quanto tempo demora** a visita, a sério, e não o que o site diz.
- **A que distância** fica daquilo que já está no plano.
- **A fonte**, com marcador `✅` ou `⚠️`. A lista está em
  `.claude/referencia/fontes.md`.
- **Se precisa de reserva**, e com que antecedência.

## Descartar

Uma opção rejeitada **fica no catálogo com a razão da rejeição**, e não se apaga.
«Fechado à segunda», «45 minutos de desvio», «esgota com meses de antecedência». É
o que impede que a mesma ideia seja pesquisada de novo daqui a três semanas e
rejeitada pela mesma razão.

## Ao pesquisar

Fontes primárias, como em todo o resto: o site do próprio sítio, nunca uma lista de
«top 10». O `find_nearby_pois` do `osm` serve para descobrir o que existe à volta
de um ponto, e o preço e o horário vêm depois, do site oficial.

Escrever em português europeu, com a mesma voz do resto do dossiê, descrita em
`.claude/referencia/convencoes.md`: afirmar, dar a razão de cada número, e dizer o
que cada opção custa em tempo, que é a moeda que falta nesta viagem. Dinheiro não
é o problema.

## Ao acabar

Dizer ao utilizador quantas opções novas entraram, quais delas justificam uma
mudança ao roteiro atual e porquê, e o que se descartou. **Não mexer no itinerário
a partir desta skill.** Se alguma coisa merecer entrar, propõe-se e passa-se à
`planear-dia`.
