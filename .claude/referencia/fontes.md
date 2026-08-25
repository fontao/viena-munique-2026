# Fontes primárias

Um preço ou um horário só passa a `✅` se veio de uma destas fontes, aberta nesse
momento e não de memória nem de um agregador. Blogues de viagem, listas de «top
10» e páginas de revenda estão fora, mesmo quando aparecem em primeiro lugar na
pesquisa.

## Transporte

| O quê | Fonte | Notas |
|---|---|---|
| Voos TAP | [flytap.com](https://www.flytap.com) | TP 1270 LIS ➔ VIE, TP 555 MUC ➔ LIS |
| Comboios da Áustria | [oebb.at](https://www.oebb.at) | Railjet, comboio do aeroporto |
| Comboios da Áustria, privados | [westbahn.at](https://westbahn.at) | Wien Westbahnhof, **não** Hauptbahnhof |
| Comboios da Alemanha | [bahn.de](https://www.bahn.de) | ICE, RE, Bayern-Ticket |
| Transportes de Viena | [wienerlinien.at](https://www.wienerlinien.at) | U-Bahn, bilhete de 24 horas |
| Transportes de Munique | [mvv-muenchen.de](https://www.mvv-muenchen.de) | S-Bahn até Hackerbrücke |
| Carro | [enterprise.de](https://www.enterprise.de) | Horário do balcão de Augsburg |

**Horários de comboio não se estimam nunca.** Estão comprados, e a hora que conta é
a do bilhete. O `osm` MCP não serve para troços de comboio.

## Bilhetes e atrações

| O quê | Fonte |
|---|---|
| Neuschwanstein | [shop.ticket-center-hohenschwangau.de](https://shop.ticket-center-hohenschwangau.de) |
| Estado da Marienbrücke | [hohenschwangau.de](https://www.hohenschwangau.de) |
| Schönbrunn | [imperialtickets.com](https://www.imperialtickets.com) |
| Castelos da Baviera, tabela de preços | [schloesser.bayern.de](https://www.schloesser.bayern.de) |
| Oktoberfest, mesas | [oktoberfest-booking.com](https://www.oktoberfest-booking.com/en) |
| Oktoberfest, site oficial | [oktoberfest.de](https://www.oktoberfest.de) |
| Nymphenburg e Residenz | [schloesser.bayern.de](https://www.schloesser.bayern.de) |
| Allianz Arena | [allianz-arena.com](https://allianz-arena.com) |
| BMW Welt e Museu | [bmw-welt.com](https://www.bmw-welt.com) |

Os sites de revenda de bilhetes (GetYourGuide, Tiqets, Viator e afins) servem para
uma coisa só, que é perceber qual é a margem que se está a evitar. Nunca como fonte
de preço nem de horário.

## Tempo e distâncias

| O quê | Como |
|---|---|
| Previsão e clima | `python meteo.py`, que usa a Open-Meteo. Nunca um site de meteorologia |
| Distâncias e tempos de carro | `osm` MCP, ferramenta `route` |
| Coordenadas | `osm` MCP, ferramenta `geocode` |

**Os tempos do OSRM são de trânsito livre.** Leem-se como um *piso* e não como uma
estimativa, porque não contam com trânsito real, com transportes públicos nem com
estacionamento. Somar margem no fim de semana da Oktoberfest à volta de Munique, e
no estacionamento de Hohenschwangau e do Eibsee.

Isto não é uma limitação que valha a pena contornar. A viagem é em setembro de
2026 e nenhum serviço prevê trânsito a um ano de distância, portanto uma leitura
com o trânsito de hoje não seria mais verdadeira.

Os serviços públicos do OSM têm um limite de cerca de um pedido por segundo. As
perguntas em lote fazem-se com `route_matrix`, e não com muitas chamadas ao
`route`.

## O que fazer quando as fontes discordam

Acontece: um preço de 2025 ainda em cache, um horário de época baixa, dois sites
oficiais com números diferentes.

1. Ganha a fonte que está mais perto de quem cobra o dinheiro. A loja do castelo
   vence a página institucional.
2. Se a dúvida se mantiver, escreve-se o intervalo e marca-se `⚠️`, com a data em
   que se consultou.
3. Não se escolhe o número mais simpático. Se um preço tanto pode ser €21 como
   €23,50, orçamenta-se pelo mais alto.
