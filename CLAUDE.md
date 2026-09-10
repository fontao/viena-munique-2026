# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Not a software project: a **travel dossier** for a 6-person trip to Vienna + Munich,
23–29 September 2026. Content is written in **European Portuguese (pt-PT)** and must stay
that way: headings, UI strings, dates ("quarta, 23 de setembro"), currency (€, comma
decimal separator).

The work here is mostly *fact-keeping*: prices, opening hours, train times and booking
deadlines that go stale. Commit messages read as editorial statements about what changed in
the plan (e.g. "Six travellers, not seven, and lock the car booking times").

## Files and how they relate

| File | Role |
|---|---|
| `itinerario_viagem.md` | **Source of truth** for the plan: deadlines, ticket hub, day-by-day schedule, prices. Holds the *decision*, never the history of how it changed. |
| `index.html` | Single-file interactive guide rendering that same plan. Must be kept in sync with the markdown. |
| `historico.md` | **Why the plan is what it is**: decisions taken, alternatives rejected, what each choice cost, and errors already made. Not checked by `verificar.py`. |
| `catalogo_viena.md` | Research backlog of Vienna options: the pool the itinerary is chosen *from*, not the plan itself. |
| `meteo.py` / `meteo.md` | Weather script and its generated report. `meteo.md` is output. The same script also generates the guide's forecast card, between the `WEATHER-AUTO` markers in `index.html`. Regenerate both, never hand-edit them. |
| `verificar.py` | Consistency checker across both documents. Knows nothing about the world, only whether the two files agree. |
| `img/` | Local photos referenced by `index.html`. |
| `.claude/skills/` | The procedures for changing the dossier. See **Skills** below. |
| `.claude/referencia/` | Shared reference the skills load on demand: writing conventions, HTML block templates, primary sources. |

When a fact changes (a price, a time, a headcount), it usually has to change in **both**
`itinerario_viagem.md` and `index.html`. Grep the number across both before declaring done.

Two recurring traps the git history shows: **headcount** (4 people in Vienna days 1–3, 6
from day 3 evening onward, and every ticket line states which) and **timings** that must remain
physically possible end to end within a day.

## The rules

Non-negotiable, whatever the task. The *procedure* for each kind of change lives in the
skills below; these are the constraints that hold regardless.

1. **`itinerario_viagem.md` is the source of truth.** When the two documents disagree, the
   markdown wins, unless it is plainly the stale one, in which case you say so out loud rather
   than quietly aligning to it.
2. **A fact changes in both files or in neither.** Run `python verificar.py` before calling
   any change done; it exists so this stops being a matter of memory.
3. **Never promote a ⚠️ to a ✅ without opening a primary source in that moment.** A plausible
   number is not a confirmed number. `.claude/referencia/fontes.md` lists what counts.
4. **Every ticket line states how many people it covers.** 4 in Vienna (days 1–3), 6 from the
   evening of day 3. Split tickets must sum to the group. The old 7-traveller plan still
   leaves residue.
5. **A day has to close on the clock**, including the drive home, ticket lead times, closing
   hours, the car rental window and sunset. Car durations come from the `osm` MCP and are a
   *floor*; train times come from ÖBB/DB/Westbahn and are never estimated.
6. **Write in European Portuguese**, in the dossier's voice: state the decision, give the
   reason for every number, and name what the choice cost. **No em-dashes (—) as
   punctuation**, in any language, in prose or in comments: use a comma, a colon, brackets or
   a full stop. The en-dash (–) stays only in time ranges. See
   `.claude/referencia/convencoes.md`.
9. **The itinerary carries the decision, not the archaeology.** Never write "a versão anterior
   dizia X" into `itinerario_viagem.md` or `index.html`. Keep the reason that still governs
   behaviour (why 14:00, why this train, what the choice cost) and put what changed, what was
   rejected and why into `historico.md`.
7. **Get a second opinion from Gemini** before closing a replanned day or a batch of price
   updates. Ask it for everything and filter afterwards.
8. **Say what you did not verify.** An honest gap beats a confident invention.

## Skills

Nine project skills in `.claude/skills/`. Invoke with `/<name>`, or let them load when the
request matches.

| Skill | For |
|---|---|
| `planear-dia` | Plan or replan a day end to end and write it into both documents |
| `sincronizar` | Check and repair markdown ↔ HTML parity after any fact changes |
| `auditar` | Full pass: feasibility, deadlines, stale prices, coherence, Gemini review |
| `bilhete` | Add or update a ticket, pass or booking across the three places it lives |
| `catalogo` | Research and curate the pool of options a day is later chosen from |
| `mapa` | Add or fix a map marker (`osm` geocode, the nine valid `iconType`s) |
| `meteo` | Refresh the forecast and judge day swaps against the real constraints |
| `segunda-opiniao` | Independent review from Gemini 3.7 Flash via the Antigravity CLI |
| `publicar` | Verify, commit in the repository's editorial style, publish to GitHub Pages |

They divide the work deliberately: `sincronizar` is the fast local check that the two files
agree, `auditar` is the slow pass that goes to primary sources to ask whether what they agree
on is *true*, and `catalogo` researches options without ever touching the itinerary.

## Commands

```bash
python verificar.py                # coherence check across both documents
python verificar.py --dia 4        # just day 4's timings
python verificar.py --so-erros     # only what is broken
python verificar.py --seccao pessoas precos
python verificar.py --seccao linguagem   # em-dashes, which rule 6 forbids
python verificar.py --listar       # list the check sections

python meteo.py                    # matrix + hourly tables for every stop, to stdout
python meteo.py --matriz           # just the stops × days matrix (the day-swap view)
python meteo.py --hoje             # next 24 h only
python meteo.py --cidade Viena     # filter stops by (partial) name, ignoring accents
python meteo.py --listar           # list stops and exit
python meteo.py --md meteo.md      # regenerate the committed report
python meteo.py --html index.html  # inject the per-day forecast into the HTML guide
python meteo.py --sem-sazonal      # skip the seasonal model (fewer calls, faster)
python meteo.py --sem-matriz       # hourly tables only
python meteo.py --todos-os-dias    # hourly tables for every stop on every trip day

python meteo.py --md meteo.md --html index.html   # the refresh: one run, both documents
```

`--hoje`, `--todos-os-dias`, `--matriz`/`--sem-matriz`, `--sem-sazonal` and `--cidade` shape the
report that goes to stdout. Naming two that contradict each other (`--hoje --todos-os-dias`,
`--matriz --sem-matriz`) is an error instead of a silent pick, and `--md` refuses all of them: it
regenerates the canonical report, and a partial one would be committed while `verificar.py`
stayed quiet. A flag whose request is already granted is fine, so `--matriz --sem-sazonal` and
`--html` with `--sem-matriz` both work. `--cidade` matches without accents, so `fussen` finds
`Füssen`.

Standard library only, no dependencies, no build step. `verificar.py` is the closest thing
this repository has to a test suite: it is deterministic, it never touches the network, and
it answers only "do the two documents agree with each other", never "is this fact true".
`index.html` is opened directly in a browser, with no server and no bundler.

## Refreshing the weather

`meteo.py` uses Open-Meteo (no API key, stdlib only). Refreshing is just re-running it,
because there is no cache or state. Regenerate the committed report with `python meteo.py --md
meteo.md`; `meteo.md` is output and is never hand-edited.

**The guide's forecast card is generated too, by the same command.** `python meteo.py --html
index.html` rewrites the block between the `WEATHER-AUTO:START` and `WEATHER-AUTO:END` markers
in `index.html`: one cell per trip day, with the source labelled on each. Never hand-edit
inside those markers, and run the two flags together, `--md meteo.md --html index.html`, so
both documents come from one fetch of one model run. `python verificar.py --seccao meteo`
compares their generation dates and flags a half-refresh.

`DAY_SUMMARY` at the top of `meteo.py` decides which stops represent each day in that card,
including the three alpine stops of Day 4. It mirrors the itinerary's day titles, so update it
alongside `STOPS` when a day's route changes.

Which of the three sources answers for a given day is decided automatically by how far away
that day is, and each is labelled in the output:

| Source | Applies to | What it gives |
|---|---|---|
| Forecast | inside the 16-day window, i.e. up to today + 15 | real hour-by-hour detail |
| Seasonal trend | beyond today + 15 | 50-member ensemble: median, p10–p90, anomaly vs. normal |
| Climatology | beyond today + 15 | hourly table = 10-year ERA5 mean for the same dates |

Open-Meteo counts today as the first of its 16 days, so the last day it answers for is **today
+ 15**, not today + 16: asking for today + 16 is an HTTP 400, not an empty table.
`forecast_horizon()` in `meteo.py` is the single place that boundary is computed.

**A detailed forecast further out than ~14 days does not exist.** Deterministic skill runs
out at ~7–10 days. Sites showing hour-by-hour 30-day forecasts are dressing up climatology.
Never present the climatology or seasonal rows as a forecast, and keep their warning labels
("média dos últimos 10 anos", "sinal semanal apenas") visible in any output change. The
seasonal block reports the p10–p90 spread on purpose: it shows the uncertainty rather than
hiding it behind a single number.

### The matrix, and why it exists

Every stop is fetched for **every day of the trip**, not just its scheduled day, and the
report opens with a stops × days matrix (`--matriz` shows it alone). The point is that the
route is partly reorderable: if the Neuschwanstein Saturday comes in soaked and the
Rothenburg Sunday comes in dry, swapping them is the cheapest fix available. Scheduled days
are bolded in the cells so a bad pairing is visible at a glance.

Stops carry an `outdoor` flag (Vienna, Neuschwanstein, Oberammergau, Eibsee, Rothenburg).
Those are the ones worth swapping, and `swap_hints()` only flags them, when an alternative
day has less than half the rain and at least 1 mm less. **The hint is rain-only**: it knows
nothing about timed tickets (Neuschwanstein, Schönbrunn), the car rental window, or the fact
that the group is only 6 from Day 3 evening. Always check a suggested swap against the
itinerary before acting on it, and remember that until mid-September the numbers behind it
are climatology, so a swap decided now is a swap decided on averages.

Useful refresh dates for this trip: **~8 Sept** the first trip days cross into the forecast
window (weak signal), **~13–16 Sept** the first forecast with useful skill, **~18–20 Sept**
reliable enough to decide clothing and the Eibsee rain plan.

Trip stops live in the `STOPS` list at the top of the file and must match the itinerary's
day-by-day route. If the route changes in `itinerario_viagem.md`, update `STOPS` too.
Climatology reconstructs its WMO weather code from mean rain and cloud cover (`synth_code`)
because averaging real codes produces contradictions like "clear sky · 3 mm of rain".

## index.html structure

~4500 lines: `<style>` (from line ~23), markup, then one `<script>` (~line 3713) split into
numbered comment sections (theme, countdown, navbar, map, day tabs, phrases, tickets,
packing, lightbox, toasts).

- **Theming**: `data-theme="light"|"dark"` on `<html>`, all colors via CSS custom properties
  defined in `:root` (dark) and a `[data-theme="light"]` block. Light is the default. Never
  hardcode a color; add a variable and define it for both themes. Contrast has been fixed
  deliberately in places, so see the inline comments explaining specific hex choices and the
  `.leaflet-container a.popup-btn` specificity note.
- **Persistence**: `localStorage` keys are namespaced `vm_*_2026` (`vm_theme_2026`,
  `vm_tickets_state_2026`, packing list). Keep the naming and don't change keys casually,
  because users lose their checked tickets.
- **Map**: Leaflet from unpkg; markers come from a locations array keyed by `iconType`
  (`plane`, `train`, `hotel`, `castle`, `beer`, `water`, `car`, `cocktail`, `food`), each
  mapped to a color + emoji in `getMarkerMeta`. Tile layer swaps with the theme.
- **Day tabs** are `div`s with `data-day="1..7"` given explicit ARIA tab/tablist semantics
  and roving tabindex in JS. Accessibility was a deliberate pass, so preserve it when editing
  tabs or adding interactive elements.
- External deps (Google Fonts, FontAwesome, Leaflet) load from CDNs; the page is otherwise
  self-contained.

## Verifying facts

Prices, opening times and transport schedules must come from **primary sources** (official
ticket shops, ÖBB/DB/Westbahn, oktoberfest-booking.com), not aggregator blogs. Where a claim
is estimated rather than confirmed, mark it as the documents already do (✅ confirmed,
⚠️ estimate, 🔴 changed). Don't silently upgrade an ⚠️ to a ✅.

### Second opinion from Gemini 3.7 Flash

When something needs reviewing (a revised day plan, a batch of price updates, a claim you
are not sure of), get an independent pass from **Gemini 3.7 Flash at high effort** via the
Antigravity CLI. It is a separate model with its own web access, so it catches stale facts
and impossible timings that a self-review will not.

```bash
agy --model gemini-3.7-flash-high --effort high --print "<prompt>"
```

- The binary is `agy` (Antigravity CLI), not `agt`. `agy models` lists the model ids.
- Use it directly rather than `omc ask antigravity`, because that route is guarded on Windows.
- Point it at files by path in the prompt (it reads the workspace), e.g.
  `"Read itinerario_viagem.md, Dia 4. Is the schedule physically possible end to end? List every timing that does not add up."`
- Ask it for **everything** it finds, then filter yourself. Asking for "only serious issues"
  suppresses real findings.
- Treat its output as input, not verdict: confirm anything it flags against a primary source
  before editing the documents.

### Real travel times

Use the **`osm` MCP** (OpenStreetMap: Nominatim + OSRM, no API key) rather than guessing or
trusting a blog. Configured in `.mcp.json`; runs via `npx -y osm-mcp`.

The tools that matter here:

- `route`: distance and duration through up to 25 waypoints, `profile` is `car`/`foot`/`bike`.
  This is the check for "does Day 4 actually fit"; it returns a per-leg breakdown, which is
  what you want when a single day chains castle → village → lake.
- `route_matrix`: many origins × destinations at once, for comparing bases or orderings.
- `optimize_route`: best visiting order for 3–12 stops (set `roundtrip` deliberately).
- `geocode` / `find_nearby_pois`: coordinates and venues; coordinates feed the `index.html`
  map markers.

Waypoints are plain strings: a place name, an address, or `"lat,lon"`.

**Read durations correctly.** OSRM returns **free-flow times with no live traffic and no
public transport**. So:

- Treat a car duration as a *floor*, not an estimate. Add margin for the Oktoberfest weekend
  around Munich and for parking at Hohenschwangau and Eibsee.
- Never use it for the train legs, which are booked and whose times come from
  ÖBB/DB/Westbahn, which stay the primary source.
- Free-flow is a fair basis anyway: the trip is in **September 2026**, and no service
  predicts traffic a year out. A live-traffic reading of today would not be more accurate.

Public OSM services are rate-limited (~1 req/s), so batch questions with `route_matrix`
instead of firing many `route` calls. For weather use `meteo.py`, not a maps tool.

Findings still belong in `itinerario_viagem.md` and `index.html`; the MCP is a check, not a
record.

### The page in a real browser

`verificar.py` reads the HTML as text, so it cannot see a layout that overflows, a colour that
fails contrast, or a panel that renders empty. For that there is a second MCP, **`playwright`**
in `.mcp.json`, which drives a headless Chromium over the `file://` page.

It is the check for anything the text tools cannot answer:

- **Does the generated block actually render?** Count the day cards in the DOM and read their
  text back, rather than trusting the markup.
- **Does anything overflow?** Compare each child's edges against its container,
  `scrollWidth > clientWidth`, and the same for height, **at several widths** (1340, 1024, 768,
  390). A `white-space: nowrap` child that does not fit does not overflow itself: it overflows
  its parent, so a per-element check alone misses it.
- **Is the text legible?** Compute the WCAG ratio from `getComputedStyle`, compositing the
  translucent backgrounds up the tree. Text needs 4.5:1, or 3:1 at 24 px and above.
- **Are there console errors?** The page has a `localStorage`-driven theme and Leaflet in it.

Two traps, both hit while building the weather card: `body` has a 0.4 s colour transition, so
read colours **after** switching theme or you measure mid-animation; and `html` has
`scroll-behavior: smooth`, so a screenshot taken right after `scrollIntoView` captures the
previous screen.

For files it writes, the server is configured with `--output-dir .playwright-mcp`, which
`.gitignore` already excludes. The page opens from `file://`, which Playwright blocks by
default, hence `--allow-unrestricted-file-access`.
