# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Not a software project: a **travel dossier** for a 6-person trip to Vienna + Munich,
23–29 September 2026. Content is written in **European Portuguese (pt-PT)** and must stay
that way — headings, UI strings, dates ("quarta, 23 de setembro"), currency (€, comma
decimal separator).

The work here is mostly *fact-keeping*: prices, opening hours, train times and booking
deadlines that go stale. Commit messages read as editorial statements about what changed in
the plan (e.g. "Six travellers, not seven, and lock the car booking times").

## Files and how they relate

| File | Role |
|---|---|
| `itinerario_viagem.md` | **Source of truth** for the plan: deadlines, ticket hub, day-by-day schedule, prices. |
| `index.html` | Single-file interactive guide rendering that same plan. Must be kept in sync with the markdown. |
| `catalogo_viena.md` | Research backlog of Vienna options — the pool the itinerary is chosen *from*, not the plan itself. |
| `meteo.py` / `meteo.md` | Weather script and its generated report. `meteo.md` is output — regenerate, never hand-edit. |
| `img/` | Local photos referenced by `index.html`. |

When a fact changes (a price, a time, a headcount), it usually has to change in **both**
`itinerario_viagem.md` and `index.html`. Grep the number across both before declaring done.

Two recurring traps the git history shows: **headcount** (4 people in Vienna days 1–3, 6
from day 3 evening onward — every ticket line states which) and **timings** that must remain
physically possible end to end within a day.

## Commands

```bash
python meteo.py                  # hourly forecast for every stop, to stdout
python meteo.py --hoje           # next 24 h only
python meteo.py --cidade Viena   # filter stops by (partial) name
python meteo.py --listar         # list stops and exit
python meteo.py --md meteo.md    # regenerate the committed report
```

Standard library only, no dependencies, no build step, no tests. `index.html` is opened
directly in a browser — there is no server or bundler.

`meteo.py` uses Open-Meteo (no API key). Beyond its 16-day forecast horizon it falls back to
10-year ERA5 climatology and labels those days "média dos últimos 10 anos" — keep that
distinction visible in any output change. Trip stops live in the `STOPS` list at the top of
the file and must match the itinerary's day-by-day route.

## index.html structure

~4500 lines: `<style>` (from line ~23), markup, then one `<script>` (~line 3713) split into
numbered comment sections (theme, countdown, navbar, map, day tabs, phrases, tickets,
packing, lightbox, toasts).

- **Theming**: `data-theme="light"|"dark"` on `<html>`, all colors via CSS custom properties
  defined in `:root` (dark) and a `[data-theme="light"]` block. Light is the default. Never
  hardcode a color; add a variable and define it for both themes. Contrast has been fixed
  deliberately in places — see the inline comments explaining specific hex choices and the
  `.leaflet-container a.popup-btn` specificity note.
- **Persistence**: `localStorage` keys are namespaced `vm_*_2026` (`vm_theme_2026`,
  `vm_tickets_state_2026`, packing list). Keep the naming and don't change keys casually —
  users lose their checked tickets.
- **Map**: Leaflet from unpkg; markers come from a locations array keyed by `iconType`
  (`plane`, `train`, `hotel`, `castle`, `beer`, `water`, `car`, `cocktail`, `food`), each
  mapped to a color + emoji in `getMarkerMeta`. Tile layer swaps with the theme.
- **Day tabs** are `div`s with `data-day="1..7"` given explicit ARIA tab/tablist semantics
  and roving tabindex in JS. Accessibility was a deliberate pass — preserve it when editing
  tabs or adding interactive elements.
- External deps (Google Fonts, FontAwesome, Leaflet) load from CDNs; the page is otherwise
  self-contained.

## Verifying facts

Prices, opening times and transport schedules must come from **primary sources** (official
ticket shops, ÖBB/DB/Westbahn, oktoberfest-booking.com), not aggregator blogs. Where a claim
is estimated rather than confirmed, mark it as the documents already do (✅ confirmed,
⚠️ estimate, 🔴 changed). Don't silently upgrade an ⚠️ to a ✅.
