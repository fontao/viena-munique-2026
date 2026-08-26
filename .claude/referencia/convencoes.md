# Convenções de escrita do dossiê

Referência partilhada pelas skills do projeto. Não é para ler de fio a pavio, mas
para consultar a regra concreta na altura de escrever.

## Língua

**Português europeu, sempre.** Não é uma preferência de estilo. É o que os seis
viajantes vão ler no telemóvel à porta de um castelo.

- Nada de português do Brasil: *comboio* (não trem), *autocarro* (não ónibus),
  *pequeno-almoço* (não café da manhã), *casa de banho*, *bilhete*, *elétrico*,
  *auscultadores* (não fones de ouvido).
- Nada de gerúndio à brasileira: «está a chover», nunca «está chovendo».
- Nomes próprios estrangeiros ficam como são: *Neuschwanstein*, *Marienplatz*,
  *Hauptbahnhof*, *Bayern-Ticket*, *Maß*. Traduzem-se só os que já têm forma
  portuguesa consagrada: *Munique*, *Viena*, *Salzburgo*, *Baviera*.
- Termos locais úteis no terreno vão em itálico, com a tradução à frente na
  primeira vez: *Lüftlmalerei* (fachadas pintadas), *Wiesn* (o recinto da
  Oktoberfest).

## Pontuação

**Não usar o travessão longo (—) como pontuação.** É um tique de escrita
automática e dá um texto todo igual. Onde apetecer um travessão, quase sempre
serve melhor uma vírgula, dois pontos, um parêntesis ou um ponto final.

| Em vez de | Escrever |
|---|---|
| «Usar o shuttle — a pé são 40 min.» | «Usar o shuttle. A pé são 40 minutos.» |
| «Tudo em Viena — transfers, Schönbrunn — é para 4.» | «Tudo em Viena (transfers, Schönbrunn) é para 4.» |
| «Há três razões — e a primeira é o tempo.» | «Há três razões, e a primeira é o tempo.» |

O meio travessão (–) continua a usar-se nos intervalos de horas, que é uma
convenção tipográfica e não pontuação: `10:30 – 12:05`.

**Isto é verificado, não é uma questão de memória.** `python verificar.py --seccao
linguagem` dá **erro** em qualquer travessão longo que apareça nos dois documentos,
e o `verificar.py` sai com código 1. O travessão volta sempre que alguém cola texto
vindo de fora, e a leitura não o apanha.

### O que conta como aviso, e porque é que devem ser poucos

Um `verificar.py` com dezasseis avisos permanentes não é um verificador, é ruído: ninguém os
lê e o aviso verdadeiro passa despercebido no meio deles. **A regra é que todo o aviso ou se
corrige, ou se explica ao verificador.** Três mecanismos, por ordem de preferência:

1. **Corrigir o documento.** Se um preço só existe num ficheiro, quase sempre falta mesmo no
   outro. Foi o caso do `€39,49/pessoa` do ICE 116 e do `€3,00` do bilhete na app.
2. **Escrever de outra maneira.** É o caso dos algarismos acima, e do bilhete de 7 dias de
   Viena, que agora diz `❌ não serve` em vez de mostrar um preço que nunca se paga.
3. **Ensinar o verificador**, quando o padrão é legítimo e se repete. Já sabe que um preço
   dentro de uma opção descartada não precisa de par, que um item riscado não é um prazo, e
   que uma parcela ao lado de um total que os dois ficheiros partilham não é um preço órfão.

O único aviso que fica de pé de propósito é o **Dia 1 ter 20h15 de programa seguido**. É
verdade, é o dia de chegada, e é uma coisa que vale a pena voltar a ver a cada revisão.

⚠️ **Ao substituir travessões em massa, reler o resultado.** Uma vírgula no sítio de
um travessão dá com frequência uma frase agramatical ou uma sequência ilegível de
vírgulas, sobretudo em cabeçalhos, em células de tabela (`| — |`) e onde a frase já
tinha dois pontos. Também parte os padrões do `verificar.py` que contavam com o
travessão, como o `RE_BLOCO`, que hoje aceita `,`, `:` e `·` por causa disso.

## Datas, horas e dinheiro

| Coisa | Forma | Exemplo |
|---|---|---|
| Data por extenso | dia, mês em minúscula | `quarta, 23 de setembro` |
| Data em cabeçalho | dia da semana capitalizado | `Quarta-feira, 23 de Setembro` |
| Hora | 24 horas, dois dígitos | `08:05`, `14:00` |
| Intervalo | meio travessão (–) com espaços | `10:30 – 12:05` |
| Duração | sem espaço no meio | `1h35`, `~35 min` |
| Dinheiro | euro antes, vírgula decimal | `€23,50`, `€141`, `€1.250,00` |
| Preço por pessoa | barra, sem espaços | `€21/pax`, `€5/pessoa` |
| Distância | vírgula decimal | `1,5 km`, `113 km` |

Aproximações levam `~` colado ao número: `~1h50`, `~285 km`. Uma hora aproximada
dentro de um bloco (`22:30 – ~02:30`) é legítima, e o `verificar.py` sabe lê-la.

## Marcadores de confiança

Todo o facto sujeito a mudar carrega um marcador. **A regra que não se quebra: um
`⚠️` nunca sobe a `✅` sem uma fonte primária consultada nesse momento.** Se a
fonte não foi aberta agora, o marcador fica como está.

| Marcador | Significa | Quando se usa |
|---|---|---|
| `✅` | Confirmado em fonte primária | Preço lido hoje no site oficial; bilhete já comprado |
| `⚠️` | Estimativa ou por confirmar | Preço de 2025 projetado para 2026; horário tirado de um blogue |
| `🔴` | Por tratar, com urgência | Prazo aberto, decisão pendente |
| `🟡` | Tratar antes de partir | Sem urgência, mas não se esquece |
| `🟢` | Compra-se no local | Sem reserva prévia |
| `~~riscado~~` + `✅` | Já resolvido | Linha de prazo cumprida |

## O grupo, a armadilha número um

**Quatro pessoas nos Dias 1 a 3. Seis a partir da noite do Dia 3.** Dois amigos
juntam-se em Augsburg quando os outros quatro chegam de comboio de Viena.

Consequências práticas, todas já erradas alguma vez neste dossiê:

- Tudo o que é em Viena (transfers, Schönbrunn, Riesenrad, Stephansdom, o comboio
  Viena ➔ Augsburg) é para **4**.
- Tudo o que é na Alemanha a partir da noite do Dia 3 é para **6**.
- **Cada linha de bilhete diz para quantas pessoas é.** Sem exceção.
- Bilhetes repartidos têm de somar o grupo: `5 pax + 1 pax = 6`. O plano antigo era
  de 7 pessoas e ainda aparecem restos. Foi assim que um Bayern-Ticket ficou a
  dizer `5 pax + 2 pax`, e que o cartão de destaque da página continuou muito tempo
  a anunciar sete viajantes.
- A carrinha é de **7 lugares** para 6 pessoas. É o único «7» legítimo do dossiê, e
  é precisamente aí que o erro se esconde.

### Algarismos são para bilhetes, o resto escreve-se por extenso

**`4 pax`, `6 pessoas`, `5 pax + 1 pax`: algarismo seguido de `pax`/`pessoas` fica
reservado para dizer quantos viajantes um bilhete cobre.** Qualquer outra quantidade de
gente escreve-se por extenso: «mais de uma centena de pessoas» na ronda do vigia noturno,
«o consumo de oito a dez lugares» numa mesa da Oktoberfest, «com sete pessoas isto era o
risco n.º 1» a falar do plano antigo.

Não é preciosismo. O `verificar.py` assinala todo o `N pessoas` com N maior que 6, porque é
assim que o plano de sete viajantes reaparece. Se as lotações e as notas históricas usarem
algarismos, a verificação passa a ter quatro avisos permanentes que ninguém lê, e o aviso a
sério perde-se no meio. Com esta regra, **um algarismo grande ao lado de `pessoas` é sempre
uma coisa a corrigir.**

⚠️ A recíproca também vale: **uma linha de bilhete que escreva o número por extenso é
suspeita**, porque foge à verificação. Bilhetes, sempre em algarismos.

## Voz

Os documentos não são um folheto turístico. São um dossiê de trabalho escrito por
alguém que já foi confirmar as coisas e explica porquê.

- **Afirmar, não sugerir.** «Usar o shuttle, não subir a pé», e não «pode ser boa
  ideia considerar o shuttle».
- **Dar sempre a razão de um número.** Não «chegar às 12:05», mas «chegar às 12:05
  porque o Ticket Center exige 90 a 120 minutos de antecedência». Um horário sem
  justificação é um horário que alguém há de mudar por engano daqui a um mês.
- **Registar o que mudou e porquê.** Quando uma decisão é revista, fica escrita.
  São dois blocos distintos, que se distinguem pela posição no dia:

  | Bloco | Onde | Diz |
  |---|---|---|
  | `> ### 🚨 O que estava errado e mudou` | logo a seguir ao cabeçalho do dia | o erro concreto que a revisão corrigiu, e porque era um erro |
  | `> ### Porque é que este dia foi reconstruído` | no fim do dia | o raciocínio completo da nova ordem, e o que custou |

  Uma revisão parcial **acrescenta** ao bloco existente em vez de o substituir. É
  assim que se impede a revisão seguinte de desfazer a anterior sem dar por isso.
  Um dia que nunca foi reconstruído não tem nenhum dos dois blocos.
- **Nomear o custo de cada escolha.** «O custo de tudo isto: jantar às 21:15 em vez
  das 20:45.» Um plano sem contrapartidas explícitas não foi pensado.
- Emoji com parcimónia e sempre com função. Sinaliza a categoria de uma linha
  (`🎫` bilhete, `⏰` hora crítica, `⚠️` risco, `🅿️` estacionamento, `🚌`
  transporte, `🏞️` alternativa ao ar livre). Nunca decorativo.

## Mensagens de commit

Frase declarativa em **inglês**, no presente, a dizer o que mudou *no plano* e não
no ficheiro. É a única parte do repositório que não é em português.

```
Six travellers, not seven, and lock the car booking times
Fix the last train, the Neuschwanstein margin and six stale prices
Optimise the Vienna route and fix an impossible Day 2 timing
```

Não: `feat: add weather script`, `update itinerary`, `fix typo`. Há um commit
`feat:` no histórico. É a exceção que não se repete.
