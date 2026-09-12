# Anatomia do `index.html`

Os blocos que se copiam quando se escreve no guia interativo. Copiar daqui e
adaptar, mas **não inventar classes novas**: o CSS está todo escrito à mão, e uma
classe que não exista não dá erro nenhum, apenas fica sem estilo.

Ficheiro único, com cerca de 4500 linhas: `<style>` a partir da linha 23, o markup,
e um `<script>` a partir da linha 3713, dividido em secções numeradas por
comentário.

## Regra que atravessa tudo: nada de cores literais

Todas as cores vêm de variáveis CSS definidas em `:root` (escuro) e no bloco
`[data-theme="light"]`. **Claro é o tema por omissão.** Escrever `color: #f59e0b`
num bloco novo produz texto ilegível num dos temas, e só se dá por isso ao trocar
de tema, coisa que ninguém faz ao rever.

Se for preciso uma cor que ainda não existe, acrescenta-se a variável **nos dois
blocos**. Há comentários no próprio ficheiro a explicar escolhas de contraste
específicas, e uma nota sobre especificidade em `.leaflet-container a.popup-btn`.
Respeitar ambos.

## Um bloco do cronograma

Vive dentro de `<div class="timeline-stream">`, no painel do dia respetivo.

```html
<div class="timeline-node" data-category="cultura">
    <div class="node-bullet"></div>
    <div class="node-card">
        <div class="node-header">
            <div class="node-badges">
                <span class="time-pill">🏰 14:00 → 15:30</span>
                <span class="category-pill">Castelo de Conto de Fadas</span>
            </div>
        </div>
        <h4 class="node-title">Castelo de Neuschwanstein</h4>
        <p class="node-text">Texto corrido, com <strong>negrito nos números</strong>.</p>

        <div class="callout-box warning">
            <i class="fa-solid fa-person-hiking"></i>
            <div><strong>Título do aviso.</strong> O corpo do aviso.</div>
        </div>

        <div class="timeline-img-wrapper enlargeable">
            <img src="img/ficheiro.webp" alt="Descrição">
            <div class="timeline-img-overlay"><span>Legenda</span><i class="fa-solid fa-expand"></i></div>
        </div>
    </div>
</div>
```

Atenção ao **`→`** nas `time-pill`. O markdown usa `–` nos intervalos, o HTML usa
`→`.

**`data-category`** alimenta os filtros por pastilha. Os valores em uso são
`transporte`, `cultura`, `comida` e `festa`, isolados ou combinados com um espaço
(`data-category="cultura comida"`). Um valor fora desta lista desaparece de todos
os filtros.

**Variantes de `time-pill`:** sem modificador (genérico), `car`, `train`, `food`,
`party`, `oktober`.

**Variantes de `callout-box`:** `info` (contexto), `warning` (risco), `critical`
(erro caro se for ignorado), `success` (confirmado). O `<i>` do FontAwesome vem
primeiro e o `<div>` com o texto vem a seguir, porque a caixa é uma grelha de duas
colunas e inverter a ordem parte o alinhamento.

## Um cartão de bilhete

Vive em `<div class="tickets-grid">`, na secção `#tickets`.

```html
<!-- Ticket N: Nome curto -->
<div class="ticket-card glass-panel glass-panel-interactive">
    <div>
        <div class="ticket-top">
            <span class="ticket-badge critical">Comprar já</span>
            <span style="font-size: 1.2rem;">🏰</span>
        </div>
        <h3 class="ticket-title">Castelo de Neuschwanstein</h3>
        <p class="ticket-desc">Descrição com o <strong>número de pessoas</strong> e o porquê da hora.</p>
        <div class="ticket-meta">
            <div class="ticket-meta-row"><span>Preço:</span> <strong>€23,50/pax = €141</strong></div>
            <div class="ticket-meta-row"><span>Prazo:</span> <strong>Esgota semanas antes</strong></div>
        </div>
    </div>
    <div class="ticket-actions">
        <label class="pack-item-label" style="padding: 0; background: transparent; min-height: unset;">
            <input type="checkbox" id="tkt_neuschwanstein" class="tkt-check">
            <span style="font-size: 0.78rem; font-weight: 700;">Tratado</span>
        </label>
        <a href="https://shop.ticket-center-hohenschwangau.de" target="_blank" class="ticket-buy-btn">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> Site oficial
        </a>
    </div>
</div>
```

**Variantes de `ticket-badge`:** `booked` (reservado ou confirmado), `success`
(✅ comprado e pago), `critical` (comprar já), `local` (compra-se no local).

**O `id` da checkbox é permanente.** Chama-se `tkt_<nome>` e é a chave dentro de
`vm_tickets_state_2026`. Mudar o `id` de um cartão que já existe apaga a marcação
de quem o tinha assinalado. Só se acrescentam `id` novos.

**Há dois tipos de checkbox, e a diferença não é o bilhete estar comprado:**

| Marcação | Para | Exemplos atuais |
|---|---|---|
| `class="tkt-check"` | tudo o que o grupo acompanha, **incluindo o que já foi comprado**. A `<span>` diz «Tratado» e o estado guarda-se em `localStorage` | Westbahn, ICE 116, Neuschwanstein, Bayern-Ticket |
| `checked disabled`, sem classe | factos fechados antes de o dossiê existir, que ninguém vai desmarcar. A `<span>` diz «Comprado», a verde, com `color: var(--accent-emerald);` | só os voos TAP e a carrinha |

**Um bilhete novo leva sempre `class="tkt-check"`.** Quem indica o estado é o
`ticket-badge`, e não a checkbox: um bilhete já pago mostra
`<span class="ticket-badge success">✅ Comprado</span>` e mantém a checkbox
utilizável.

## Um separador de dia

São sete, dentro de `<div class="day-selector-bar" id="day-selector">`. Cada um
tem o painel correspondente, `<div class="day-view-container" id="day-view-N">`.

```html
<div class="day-tab-card" data-day="4">
    <div class="day-tab-top"><span>Dia 4</span><span>Sáb 26</span></div>
    <div class="day-tab-title">🏔️ Alpes & Eibsee</div>
    <div class="day-tab-badge"><i class="fa-solid fa-mountain"></i> Oberammergau</div>
</div>
```

Os separadores recebem semântica ARIA de `tab` e `tablist`, e *roving tabindex*
em JS. **Foi uma passagem de acessibilidade deliberada.** Ao mexer nos separadores
ou ao acrescentar elementos interativos, preservar tudo isso. Não converter para
`<button>` nem retirar os atributos gerados.

O painel abre com o cartaz do dia:

```html
<div class="day-hero-banner glass-panel">
    <img src="img/foto.webp" alt="Alt" class="enlargeable">
    <div class="day-banner-content">
        <span class="day-banner-tag">SÁB 26 SETEMBRO • DIA 4</span>
        <h3 class="day-banner-title">Título do dia</h3>
        <div class="day-banner-meta">
            <span><i class="fa-solid fa-bed"></i> Acordar 10:00</span>
            <span><i class="fa-solid fa-route"></i> ~285 km Roadtrip</span>
        </div>
    </div>
</div>
```

A `day-banner-tag` escreve-se em maiúsculas, com `•` a separar. Fica `Sáb 26` no
separador e `SÁB 26 SETEMBRO` no cartaz, e o `scripts/verificar.py` confirma que a data
bate certo com o cabeçalho do markdown.

## Um marcador no mapa

Entrada no array `locations`, por volta da linha 3819.

```js
{ name: "Nome do sítio", city: "munich", iconType: "castle", coords: [48.1582, 11.5036],
  desc: "Uma ou duas frases.", img: "img/foto.webp" },
```

**`iconType` só pode ser um destes dez**, que são os que o `getMarkerMeta()` sabe
desenhar: `plane` ✈️, `train` 🚆, `hotel` 🏨, `castle` 🏰, `beer` 🍺, `water` 🌊,
`car` 🚗, `cocktail` 🍸, `food` 🍴, `monument` 🏛️. Qualquer outro valor cai no pin
azul genérico 📍 sem dar erro nenhum, e foi assim que sete marcadores ficaram com
`monument` e `road` sem ninguém reparar durante meses. Ou se usa um dos dez, ou se
acrescenta o tipo novo ao `getMarkerMeta()`, com cor e emoji.

**Acrescentar um `iconType` não mexe nos filtros.** Os botões de `#map-filters`
filtram por **`city`**, não por tipo: o código faz `marker.category = loc.city`. Os
valores são `lisbon`, `vienna`, `augsburg`, `alps`, `rothenburg` e `munich`, e é um
valor **novo de `city`** que precisa de um botão novo, senão o pin fica invisível
assim que alguém filtrar.

**As coordenadas vêm do `osm` MCP** (`geocode`), nunca de memória nem de um
blogue. Latitude primeiro. O `scripts/verificar.py` rejeita qualquer par que caia fora da
caixa da viagem, que é o que apanha uma latitude trocada com a longitude.

## As fotografias em `img/`

**WebP, 1600 px de largura, qualidade 86.** Uma fotografia nova entra assim, senão
a página volta a engordar sem ninguém dar por isso.

A largura não é arbitrária. É a maior que a página chega a mostrar: a caixa de
conteúdo tem 1240 px e o lightbox tem `max-width: 92vw`, que num telemóvel a DPR 3
dá 1076 px físicos. Guardar 1920 era pagar 44% mais bytes por pixéis que só se
veem numa janela de desktop com mais de ~1740 px, e aí a diferença é uma ampliação
de 10% que ninguém distingue.

O formato também foi medido, não escolhido por moda: a 1600 px, o WebP a 86 dá
ficheiros mais pequenos **e** PSNR mais alto do que o JPEG a 85 nas vinte
fotografias, sem uma única exceção.

```python
im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS).save(
    destino, "WEBP", quality=86, method=6, icc_profile=im.info.get("icc_profile"))
```

⚠️ **A extensão aparece em três sítios**, e esquecer um deixa a foto partida sem
erro nenhum: o `src` do `<img>`, o campo `img:` do marcador no mapa, e a regra CSS
`.hero-bg-overlay`, que é a única referência que não é um `<img>` e por isso escapa
a qualquer procura por `src=`. O `scripts/verificar.py --seccao imagens` conta as três.

E **não confundir com os `.jpg` da tabela de créditos**: esses são os nomes dos
ficheiros originais no Wikimedia Commons, ficam como estão.

## O cartão do tempo é gerado, e não se toca

Na secção `#logistics`, o bloco entre `<!-- WEATHER-AUTO:START -->` e
`<!-- WEATHER-AUTO:END -->` **não é escrita à mão**: é escrito pelo
`python scripts/meteo.py --html index.html`, com uma célula por dia da viagem. Editá-lo à mão
perde-se na atualização seguinte.

O estilo dele vive nas regras `.weather-strip`, `.weather-day-card`, `.weather-src`
(com `.is-forecast` a verde e `.is-clima` a âmbar) e `.weather-note`. A alteração que
fizer sentido fazer no cartão faz-se **no `scripts/meteo.py`**, não aqui.

## Persistência

Três chaves em `localStorage`, todas com a forma `vm_<nome>_2026`:

| Chave | Guarda |
|---|---|
| `vm_theme_2026` | tema escolhido |
| `vm_tickets_state_2026` | bilhetes assinalados |
| `vm_pack_state_2026` | mala arrumada |

**Não se renomeiam.** Quem já tem bilhetes marcados perde-os.

## Dependências externas

Google Fonts, FontAwesome e Leaflet vêm de CDN, e o resto é autossuficiente. A
camada de tiles do mapa troca com o tema. Não acrescentar dependências novas,
porque o ficheiro abre-se diretamente no browser, sem servidor nem build.
