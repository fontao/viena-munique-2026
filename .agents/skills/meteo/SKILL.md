---
name: meteo
description: Atualiza a previsão do tempo e avalia se vale a pena trocar dias da viagem por causa da chuva. Usar quando se pergunta pelo tempo, se vai chover, se convém trocar o dia do castelo com o de Rothenburg, ou quando se pede para regenerar o meteo.md.
allowed-tools: Bash(python scripts/meteo.py *), Read, Edit
---

# Tempo e trocas de dias

O `scripts/meteo.py` usa a Open-Meteo, sem chave e só com biblioteca padrão. Não há cache
nem estado guardado: atualizar é voltar a correr.

```bash
python scripts/meteo.py                  # matriz e tabelas horárias de todas as paragens
python scripts/meteo.py --matriz         # só a matriz paragens × dias, que é a vista de decisão
python scripts/meteo.py --hoje           # próximas 24 horas
python scripts/meteo.py --cidade Viena   # filtrar por nome parcial, sem maiúsculas nem acentos
python scripts/meteo.py --md meteo.md    # regenerar o relatório versionado
python scripts/meteo.py --html index.html  # injetar o resumo por dia no guia HTML
```

Os filtros que mudam a vista (`--hoje`, `--todos-os-dias`, `--matriz`, `--sem-matriz`,
`--sem-sazonal`, `--cidade`) são para a saída do terminal. Combinar dois que se contradizem
(`--hoje --todos-os-dias`, `--matriz --sem-matriz`) **dá erro**, em vez de escolher um por
conta própria, e o `--md` recusa-os todos: ele escreve o relatório completo, e uma versão
parcial dele ficaria commitada sem que o `scripts/verificar.py` desse por isso. Um pedido já satisfeito
passa: `--matriz --sem-sazonal` é legítimo, porque a matriz nunca consulta o modelo sazonal.
O `--cidade` ignora maiúsculas **e acentos**, portanto `fussen` encontra `Füssen`.

O `meteo.md` é um ficheiro **gerado**. Regenera-se, nunca se edita à mão.

**O cartão do tempo do guia também é gerado, pelo mesmo comando.** O `--html` reescreve
o bloco entre os marcadores `WEATHER-AUTO:START` e `WEATHER-AUTO:END` no `index.html`:
uma célula por dia da viagem, com a fonte rotulada em cada uma. **Não se edita nada lá
dentro à mão.** Correr os dois juntos, para os dois ficheiros saírem da mesma leitura:

```bash
python scripts/meteo.py --md meteo.md --html index.html
```

Quem decide que paragens representam cada dia nesse cartão é a lista `DAY_SUMMARY`, no
topo do `scripts/meteo.py`, incluindo as três paragens alpinas do Dia 4. Espelha os títulos
dia-a-dia do itinerário, portanto muda com eles.

`python scripts/verificar.py --seccao meteo` compara as datas de geração dos dois e assinala uma
atualização feita só a metade.

## A honestidade é o ponto

Há três fontes, escolhidas automaticamente conforme a distância a que o dia está, e
**cada uma vem rotulada na saída**:

| Fonte | Aplica-se a | Dá |
|---|---|---|
| Previsão | dentro da janela dos 16 dias, ou seja até hoje + 15 | detalhe hora a hora, a sério |
| Tendência sazonal | a mais de hoje + 15 | conjunto de 50 membros: mediana, p10 a p90, anomalia |
| Climatologia | a mais de hoje + 15 | tabela horária que é a média ERA5 de 10 anos |

A Open-Meteo conta o dia de hoje como o primeiro dos seus 16, portanto o último dia que
responde é **hoje + 15**, e não hoje + 16: pedir hoje + 16 devolve HTTP 400, não uma tabela
vazia. É o `forecast_horizon()` que guarda essa fronteira.

**Uma previsão detalhada a mais de 14 dias não existe.** A capacidade de previsão
determinística acaba aos 7 a 10 dias. Os sites que mostram 30 dias hora a hora
estão a apresentar climatologia com outra roupa.

Ao responder: nunca apresentar as linhas de climatologia ou de tendência sazonal
como se fossem previsão, e manter visíveis os rótulos («média dos últimos 10 anos»,
«sinal semanal apenas»). O intervalo p10 a p90 aparece de propósito, porque mostra
a incerteza em vez de a esconder atrás de um número só.

Datas úteis para esta viagem: por volta de **8 de setembro** os primeiros dias
entram na janela de previsão, ainda com sinal fraco; por volta de **13 a 16 de
setembro** aparece a primeira previsão com capacidade real; e de **18 a 20 de
setembro** já é fiável ao ponto de decidir a roupa e o plano B do Eibsee.

## A matriz e as trocas

Cada paragem é consultada em **todos os dias da viagem**, e não só no seu. O
relatório abre com uma matriz de paragens por dias porque a rota é parcialmente
reordenável: se o sábado de Neuschwanstein vier encharcado e o domingo de
Rothenburg vier seco, trocar os dois é a correção mais barata que existe. Os dias
agendados aparecem a negrito.

As paragens ao ar livre são Viena, Neuschwanstein, Oberammergau, Eibsee e
Rothenburg, e são as únicas que vale a pena trocar. O `swap_hints()` só assinala
essas, e apenas quando um dia alternativo tem menos de metade da chuva e pelo menos
1 mm a menos.

**A sugestão olha só para a chuva.** Não sabe nada de:

- bilhetes com hora marcada (Neuschwanstein, Schönbrunn), que não são reembolsáveis
  e têm a data fechada;
- a janela do carro, de sexta às 17:00 a terça às 17:00;
- o grupo só ser de seis a partir da noite do Dia 3;
- a ordem geográfica da rota e o sítio onde se dorme cada noite.

**Confrontar sempre uma troca sugerida com o `itinerario_viagem.md` antes de a
propor.** Até meados de setembro os números por trás dela são climatologia, ou
seja, uma troca decidida hoje é uma troca decidida sobre médias. Isso diz-se.

## Manutenção

As paragens vivem na lista `STOPS`, no topo do `scripts/meteo.py`, e têm de espelhar a rota
do itinerário. **Se a rota mudar no `itinerario_viagem.md`, atualizar `STOPS`.**

**A `DAY_SUMMARY`, logo abaixo, também muda com a rota:** é ela que diz quais das
paragens representam cada dia no cartão do guia. O Dia 3 tem uma só (Augsburg), o
Dia 4 tem três (Neuschwanstein, Oberammergau e Eibsee).

A climatologia reconstrói o código meteorológico WMO a partir da chuva e da
nebulosidade médias, no `synth_code`, porque a média de códigos reais produz
contradições do género «céu limpo, 3 mm de chuva».

## Ao responder

Dizer sempre qual é a fonte de cada número. Se a pergunta for «vai chover no dia do
castelo?» e faltarem cinco semanas, a resposta honesta começa por dizer que ainda
não existe previsão nenhuma para esse dia, e só depois dá a média histórica.
