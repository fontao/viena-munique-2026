---
name: mapa
description: Acrescenta, corrige ou remove um marcador no mapa interativo do index.html. Usar quando se acrescenta um sítio novo ao roteiro, quando um pin está no sítio errado, ou quando se pedem as coordenadas de um lugar.
argument-hint: [sítio]
allowed-tools: Bash(python verificar.py *), Read, Edit, Grep
---

# Marcadores do mapa

O mapa é Leaflet e os pins vêm todos do array `locations` em `index.html`, por
volta da linha 3819.

```js
{ name: "Palácio de Nymphenburg", city: "munich", iconType: "castle",
  coords: [48.1582, 11.5036], desc: "Uma ou duas frases.", img: "img/nymphenburg_palace.jpg" },
```

## Coordenadas

**Vêm do `osm` MCP, ferramenta `geocode`.** Nunca de memória, nunca de um blogue.
Latitude primeiro. Para vários sítios de uma vez faz-se uma pergunta em lote,
porque os serviços públicos do OSM têm um limite de cerca de um pedido por segundo.

Uma latitude trocada com a longitude dá um pin algures na Somália, e o verificador
apanha isso: `python verificar.py --seccao mapa` rejeita coordenadas que caiam
fora da área da viagem.

## `iconType`, a armadilha silenciosa

Só existem dez, que são os que o `getMarkerMeta()` sabe desenhar:

| Valor | Pin | Para |
|---|---|---|
| `plane` | ✈️ azul-claro | aeroportos |
| `train` | 🚆 índigo | estações |
| `hotel` | 🏨 roxo | onde se dorme |
| `castle` | 🏰 rosa | castelos, palácios, vilas históricas |
| `beer` | 🍺 âmbar | cervejarias, Oktoberfest |
| `water` | 🌊 ciano | lagos, rios |
| `car` | 🚗 esmeralda | aluguer e tudo o que seja de automóvel |
| `cocktail` | 🍸 rosa-claro | bares, discotecas |
| `food` | 🍴 laranja | restaurantes, mercados |
| `monument` | 🏛️ ardósia | catedrais, praças, bairros históricos, o estádio |

Qualquer outro valor **não dá erro**. Cai no pin azul genérico 📍 e fica errado sem
ninguém reparar, que foi como sete marcadores passaram meses com `monument` e
`road` antes de o `verificar.py` dar por isso. Ou se usa um dos dez, ou se
acrescenta o tipo novo ao `getMarkerMeta()`, com a sua cor e o seu emoji.

## `city` e os filtros

**Os filtros são por `city`, não por `iconType`.** O código faz
`marker.category = loc.city`, portanto acrescentar um tipo de pin não obriga a
mexer em filtro nenhum.

Os valores são `lisbon`, `vienna`, `augsburg`, `alps`, `rothenburg` e `munich`, e
alimentam os botões em `#map-filters`. É um valor novo de **`city`** que precisa de
um botão novo, senão o pin fica invisível assim que alguém filtrar.

## `desc`

Uma ou duas frases, em português europeu. Pode conter horas e preços, e nesse caso
passa a fazer parte do que tem de ser sincronizado: se o preço mudar no itinerário,
muda aqui também. O `verificar.py` não lê dentro das `desc`, por isso este é um dos
sítios onde um número velho sobrevive mais tempo.

## Ao acabar

`python verificar.py --seccao mapa` sem 🔴, e confirmar que o sítio novo também
existe no dia respetivo do itinerário e do HTML. Um pin no mapa que não aparece em
dia nenhum é um sítio que ninguém vai visitar.
