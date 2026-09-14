# Regras de Espaço de Trabalho - Viena + Munique 2026

## 🔴 HARD RULES - NÃO NEGOCIÁVEIS

1. **NUNCA editar `index.html` diretamente. Editar SEMPRE em `partials/`.**
   - `index.html` é um artefacto gerado automaticamente pelo `build.py` a partir dos 10 ficheiros em `partials/`.
   - Qualquer alteração feita diretamente a `index.html` é estritamente proibida e será esmagada no próximo build ou deploy.
   - Qualquer edição de HTML tem de ser feita exclusivamente no partial relevante em `partials/`:
     - `partials/head.html` (meta, links externos, estilos CSS globais)
     - `partials/header.html` (navbar e navegação)
     - `partials/hero.html` (hero banner e métricas da viagem)
     - `partials/map.html` (estrutura da secção do mapa)
     - `partials/itinerary.html` (linha temporal dos Dias 1 a 7, cartões e nós)
     - `partials/tickets.html` (hub de bilhetes e passes)
     - `partials/oktoberfest.html` (guia e tendas da Oktoberfest)
     - `partials/weather.html` (cartão meteorológico e lista de bagagem)
     - `partials/dossier.html` (alojamentos, carrinha e contactos de emergência)
     - `partials/footer.html` (rodapé, lightbox e scripts JS incluindo array locations)
   - Imediatamente após editar qualquer ficheiro em `partials/`, correr SEMPRE:
     ```bash
     python build.py
     ```

2. **`itinerario_viagem.md` é a fonte da verdade.**
   - Quando os dois documentos divergirem, o markdown prevalece.
   - Um facto muda em ambos os documentos (`itinerario_viagem.md` e `partials/`) ou em nenhum.

3. **Validar sempre com `python scripts/verificar.py`.**
   - Nenhuma tarefa é dada por concluída sem a execução limpa de `python scripts/verificar.py` com 0 erros e 0 preços órfãos.

4. **Português Europeu (pt-PT) estrito e sem travessões de pontuação.**
   - Nunca usar travessão (`—`) como pontuação em prosa ou comentários. Usar vírgulas, dois pontos, parênteses ou ponto final.
   - O meio-travessão (`–`) é reservado unicamente para intervalos horários ou numéricos.

5. **Sem meta-talk de planeador nem carimbos de confirmação na prosa.**
   - O guia e o itinerário são manuais práticos de terreno, não diários de conceção.
   - Não incluir marcas como `(confirmado a DD/MM/AAAA)` ou desculpas de desenho de percurso.
