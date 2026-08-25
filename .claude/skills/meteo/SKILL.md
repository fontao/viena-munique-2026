---
name: meteo
description: Atualiza a previsão do tempo e avalia se vale a pena trocar dias da viagem por causa da chuva. Usar quando se pergunta pelo tempo, se vai chover, se convém trocar o dia do castelo com o de Rothenburg, ou quando se pede para regenerar o meteo.md.
allowed-tools: Bash(python meteo.py *), Read, Edit
---

# Tempo e trocas de dias

O `meteo.py` usa a Open-Meteo, sem chave e só com biblioteca padrão. Não há cache
nem estado guardado: atualizar é voltar a correr.

```bash
python meteo.py                  # matriz e tabelas horárias de todas as paragens
python meteo.py --matriz         # só a matriz paragens × dias, que é a vista de decisão
python meteo.py --hoje           # próximas 24 horas
python meteo.py --cidade Viena   # filtrar por nome parcial
python meteo.py --md meteo.md    # regenerar o relatório versionado
```

O `meteo.md` é um ficheiro **gerado**. Regenera-se, nunca se edita à mão.

## A honestidade é o ponto

Há três fontes, escolhidas automaticamente conforme a distância a que o dia está, e
**cada uma vem rotulada na saída**:

| Fonte | Aplica-se a | Dá |
|---|---|---|
| Previsão | dia a 16 dias ou menos | detalhe hora a hora, a sério |
| Tendência sazonal | dia a mais de 16 dias | conjunto de 50 membros: mediana, p10 a p90, anomalia |
| Climatologia | dia a mais de 16 dias | tabela horária que é a média ERA5 de 10 anos |

**Uma previsão detalhada a mais de 14 dias não existe.** A capacidade de previsão
determinística acaba aos 7 a 10 dias. Os sites que mostram 30 dias hora a hora
estão a apresentar climatologia com outra roupa.

Ao responder: nunca apresentar as linhas de climatologia ou de tendência sazonal
como se fossem previsão, e manter visíveis os rótulos («média dos últimos 10 anos»,
«sinal semanal apenas»). O intervalo p10 a p90 aparece de propósito, porque mostra
a incerteza em vez de a esconder atrás de um número só.

Datas úteis para esta viagem: por volta de **7 de setembro** os primeiros dias
entram na janela dos 16 dias, ainda com sinal fraco; por volta de **13 a 16 de
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

As paragens vivem na lista `STOPS`, no topo do `meteo.py`, e têm de espelhar a rota
do itinerário. **Se a rota mudar no `itinerario_viagem.md`, atualizar `STOPS`.**

A climatologia reconstrói o código meteorológico WMO a partir da chuva e da
nebulosidade médias, no `synth_code`, porque a média de códigos reais produz
contradições do género «céu limpo, 3 mm de chuva».

## Ao responder

Dizer sempre qual é a fonte de cada número. Se a pergunta for «vai chover no dia do
castelo?» e faltarem cinco semanas, a resposta honesta começa por dizer que ainda
não existe previsão nenhuma para esse dia, e só depois dá a média histórica.
