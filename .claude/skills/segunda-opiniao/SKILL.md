---
name: segunda-opiniao
description: Pede uma revisão independente ao Gemini 3.7 Flash através do Antigravity CLI. Usar quando um dia foi replaneado, quando se atualizou um lote de preços, quando há uma dúvida sobre um facto, ou sempre que se quer uma opinião externa antes de fechar uma alteração.
argument-hint: [o que rever]
allowed-tools: Bash(agy *), Read
---

# Segunda opinião do Gemini 3.7 Flash

Um modelo diferente, com pesquisa web própria. Serve para apanhar aquilo que uma
autorrevisão não apanha: preços que caducaram, horários que não fecham, um museu
que fechou para obras.

```bash
agy --model gemini-3.7-flash-high --effort high --print "<prompt>"
```

- O binário é o `agy` (Antigravity CLI), e não o `agt`. O comando `agy models`
  lista os identificadores disponíveis.
- Usar diretamente, e não através do `omc ask antigravity`, porque essa rota está
  bloqueada em Windows.
- Ele lê o workspace, portanto apontam-se-lhe ficheiros por caminho em vez de se
  colar o conteúdo.

## Como pedir

**Pedir tudo o que encontrar, e filtrar depois.** Escrever «só problemas graves» ou
«sê conservador» é seguido à letra e suprime achados reais.

Um prompt bom nomeia o ficheiro, a secção e o critério:

```bash
agy --model gemini-3.7-flash-high --effort high --print \
  "Lê itinerario_viagem.md, Dia 4. O horário é fisicamente possível de ponta a ponta,
   contando com o levantamento obrigatório dos bilhetes em Hohenschwangau e o regresso
   a Augsburg? Lista TODAS as horas que não batem certo, por mais pequenas que sejam,
   e todos os preços que já não correspondem a 2026. Não filtres por gravidade."
```

Perguntas úteis, conforme o tipo de revisão:

| A rever | Pedir |
|---|---|
| Um dia replaneado | exequibilidade de ponta a ponta, margens dos bilhetes, luz do dia, regresso |
| Um lote de preços | quais já não correspondem a 2026, e a fonte de cada um |
| Prazos | janelas de reserva que abriram ou fecharam desde a última revisão |
| Um facto isolado | confirmação, e o endereço oficial de onde vem |

Dividir por dia ou por tema, em vez de mandar o documento todo de uma vez. As
respostas ficam concretas em vez de genéricas.

## Como usar a resposta

**É entrada, não é veredicto.** O Gemini erra, inventa horários e às vezes discorda
de coisas que foram decididas de propósito neste dossiê.

1. Separar o que é factual (um preço, uma hora, um horário de abertura) do que é
   opinião («seria melhor visitar de manhã»).
2. **Cada facto que ele levanta confirma-se em fonte primária** antes de se
   tocar nos documentos. A lista está em `.claude/referencia/fontes.md`.
3. As opiniões avaliam-se à luz das decisões já registadas. Muitas já foram
   consideradas e rejeitadas, com a razão escrita no bloco `> ### Porque é que este
   dia foi reconstruído` ou na secção `## 🔄 Trocar dias?`.
4. Aquilo que ele levantar e não se confirmar diz-se ao utilizador na mesma: foi
   levantado e não se confirmou. Não desaparece em silêncio.

## No relatório

Dizer o que se perguntou, o que ele respondeu, o que se confirmou e o que se
rejeitou. Uma revisão externa cujo resultado não é mostrado não serviu para nada.
