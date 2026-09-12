---
name: bilhete
description: Acrescenta ou atualiza um bilhete, passe ou reserva no hub de bilhetes, nos dois documentos. Usar quando se compra alguma coisa, quando um preço ou prazo muda, quando se marca um bilhete como comprado, ou quando se acrescenta uma reserva nova.
argument-hint: [bilhete] [o que mudou]
allowed-tools: Bash(python scripts/verificar.py *), Read, Edit, Grep, WebSearch, WebFetch
---

# Bilhetes, passes e reservas

Um bilhete vive em três sítios e tem de dizer o mesmo nos três:

1. `itinerario_viagem.md`, na secção `## 🎫 Hub de Bilhetes, Passes & Reservas`, e
   também na tabela `## 🚨 Prazos Críticos` se tiver data-limite;
2. `itinerario_viagem.md`, no dia em que se usa;
3. `index.html`, no cartão da secção `#tickets` e na `callout-box` do bloco do dia.

## O que uma entrada tem de dizer

Sem exceção, e por esta ordem de importância:

- **Para quantas pessoas.** Quatro em Viena (Dias 1 a 3), seis a partir da noite do
  Dia 3. Bilhetes repartidos têm de somar o grupo: `5 pax + 1 pax = 6`, nunca 7.
- **Preço unitário e total**, com vírgula decimal: `€23,50/pax = €141`.
- **Onde se compra**, que é o site oficial e não um revendedor. A lista está em
   `.agents/referencia/fontes.md`.
- **Até quando**, e porque é urgente, se for.
- **O estado**, com marcador: `🔴` comprar já, `🟡` antes de partir, `🟢` no local,
  `✅` comprado com o valor pago, `⚠️` preço por confirmar.
- **A armadilha**, se houver. Levantamento obrigatório, partida de outra estação,
  número máximo de pessoas por bilhete, bilhete não reembolsável.

## Marcar como comprado

1. Na tabela de prazos: riscar a linha com `~~...~~`, pôr `✅` e substituir o
   motivo da urgência pelo valor realmente pago.
2. No hub: `✅` e o valor pago, que pode não ser o que estava estimado. Se mudou,
   dizê-lo em vez de apagar o número antigo em silêncio.
3. Em `index.html`: `ticket-badge success` com `✅ Comprado`. **Não se mexe na
   checkbox.** Quem indica o estado é a etiqueta, e não a caixa. Mantém-se
   `class="tkt-check"` e a `<span>` a dizer «Tratado», como já acontece na Westbahn
   e no ICE 116, que estão pagos e continuam a marcar-se à mão.
4. Guardar o detalhe que só existe depois da compra e que vai fazer falta no
   próprio dia: número do comboio, lugares, hora exata, referência da reserva.

**O `id` da checkbox (`tkt_<nome>`) nunca muda.** É a chave em
`vm_tickets_state_2026`, e renomeá-lo apaga a marcação de quem já a tinha feito.

Há dois cartões com `checked disabled` e sem `class="tkt-check"`, os voos e a
carrinha, porque são factos fechados que ninguém vai desmarcar. **Um bilhete novo
nunca nasce assim.**

## Um bilhete novo

Preço e horário de fonte primária, aberta nesse momento. Se não se abriu, fica
`⚠️`. Depois: entrada no hub, cartão em `#tickets` (modelo em
`.agents/referencia/anatomia-html.md`, com o `ticket-badge` conforme o estado),
`callout-box` no dia em que se usa, e linha na tabela de prazos se tiver
data-limite.

Se o bilhete tem hora marcada, **confirmar que a hora escolhida cabe no dia** antes
de a escrever, contando com a antecedência exigida por quem o vende.
Neuschwanstein pede 90 a 120 minutos na aldeia. Se não couber, é o dia que se
ajusta e não a margem que se encolhe. Ver a skill `planear-dia`.

## Nunca

- Subir um `⚠️` a `✅` sem ter aberto a fonte nesse momento.
- Escrever um preço de revendedor como se fosse o oficial.
- Deixar uma entrada sem o número de pessoas.
- Apagar um prazo que passou sem ter sido tratado. Pergunta-se antes ao utilizador
  o que aconteceu.

## Fechar

`python scripts/verificar.py --seccao pessoas precos` sem 🔴, e ao utilizador: o que mudou,
quanto custa agora o total, e o que continua por tratar com data marcada.
