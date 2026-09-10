---
name: sincronizar
description: Verifica e repara a coerência entre itinerario_viagem.md e index.html. Usar sempre que se muda um preço, uma hora, um número de pessoas ou um estado de bilhete, e quando se pergunta se os dois documentos estão a dizer a mesma coisa.
allowed-tools: Bash(python verificar.py *), Read, Edit, Grep
---

# Pôr os dois documentos a dizer o mesmo

O guia HTML e o itinerário em markdown contam a mesma viagem duas vezes. Quando um
facto muda, tem de mudar nos dois. A maneira de este dossiê se estragar não é
alguém escrever uma coisa errada, é alguém corrigir só metade.

## Estado atual

```!
python verificar.py
```

## Como ler o que está em cima

- **🔴 ERRO:** está mal, resolve-se.
- **⚠️ AVISO:** tem de ser visto por uma pessoa. Muitos são legítimos, porque o
  markdown tem detalhe que o HTML não tem, e um preço que só existe no markdown
  pode ser deliberado.
- **· INFO:** contexto, como as folgas de cada dia, as contagens e os marcadores.

O verificador **não sabe nada sobre o mundo**. Não valida se um preço está certo,
apenas se está coerente entre os dois ficheiros.

**Esta skill fica-se por aí, de propósito.** Verifica se os documentos concordam
entre si, e não vai à internet confirmar se o número em que concordam é o
verdadeiro. Isso é trabalho da skill `auditar`, que abre as fontes primárias e por
isso demora. Se durante uma sincronização surgir a suspeita de que um preço está
desatualizado nos *dois* ficheiros, diz-se ao utilizador e sugere-se `/auditar`,
em vez de alargar esta passagem.

## Reparar

`itinerario_viagem.md` é o documento que manda. Perante uma divergência, o markdown
ganha, **exceto** quando é evidente que foi o markdown que ficou para trás. Nesse
caso diz-se isso explicitamente ao utilizador, em vez de alinhar em silêncio.

Ordem de trabalho:

1. **Erros de soma de pessoas**, primeiro. São sempre reais e são sempre restos do
   antigo plano de 7 viajantes. Quatro pessoas nos Dias 1 a 3, seis a partir da
   noite do Dia 3, e bilhetes repartidos que somem o grupo.
2. **Sobreposições de horário.** Uma sobreposição de 30 minutos é uma visita que
   não cabe onde está escrita. Decide-se qual dos dois blocos encolhe, e diz-se
   porquê. Abaixo de 10 minutos sai como aviso e costuma ser arredondamento.
3. **Preços órfãos.** Para cada um, procurar o número nos dois ficheiros e decidir
   se está desatualizado de um dos lados ou se é detalhe que só existe no markdown.
4. **Marcadores.** Um `⚠️` nunca sobe a `✅` sem fonte primária aberta nesse
   momento.

Depois de cada correção, correr `python verificar.py --so-erros` outra vez.

## O que o verificador não apanha

Confirmar à mão sempre que a alteração os afete:

- Texto descritivo que contradiz um número correto, como «chega de manhã» num
  bloco que agora começa às 14:00.
- O campo `desc:` dos marcadores do mapa, quando tem horas ou preços lá dentro.
- O botão de copiar o sumário (`btn-export-summary`) e a lista da mala.
- A lista `STOPS` do `meteo.py` e a `DAY_SUMMARY` logo abaixo dela, se a rota passou a
  incluir outra cidade ou outro dia. A secção `meteo` confirma que o bloco gerado no
  `index.html` existe e que cada dia traz a fonte rotulada, mas **não compara número a
  número** com o `meteo.md`: se as datas de geração baterem certo, assume que batem.
  Quem quiser os números alinhados volta a correr
  `python meteo.py --md meteo.md --html index.html`.
- O bloco `## 🔄 Trocar dias?`, se a decisão que ali está descrita deixou de valer.

## Fechar

`python verificar.py` sem 🔴, e ao utilizador: o que estava dessincronizado, por
qual dos dois lados se alinhou, e o que ficou como aviso por decisão humana.
