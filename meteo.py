#!/usr/bin/env python3
"""Previsão meteorológica hora-a-hora para as cidades do roteiro Viena + Munique 2026.

Usa a API pública Open-Meteo (sem chave). Basta voltar a correr para actualizar:

    python meteo.py                # todas as paragens, tabela por dia
    python meteo.py --hoje         # só as próximas 24 h em cada cidade
    python meteo.py --cidade Viena # filtra por nome
    python meteo.py --md meteo.md  # escreve um relatório markdown
    python meteo.py --html index.html  # injeta o resumo por dia no guia HTML

O `--md` e o `--html` escrevem no mesmo sítio a mesma informação, por isso
correm-se juntos: `python meteo.py --md meteo.md --html index.html`.

A janela de previsão da Open-Meteo é de 16 dias. Para datas mais longínquas o
script cai automaticamente para duas fontes que dizem o que se pode mesmo saber
a esse prazo, ambas assinaladas como tal:

  * climatologia — média hora-a-hora dos últimos 10 anos (reanálise ERA5) nas
    mesmas datas, que preenche a tabela horária;
  * tendência sazonal — ensemble de 50 membros do modelo sazonal, resumido em
    mediana, intervalo p10–p90 e anomalia face à normal. É sinal semanal: diz
    se a semana vem mais quente ou mais chuvosa que o costume, nunca a que
    horas chove.

Nenhuma delas é uma previsão detalhada, porque a essa distância não existe.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
SEASONAL_URL = "https://seasonal-api.open-meteo.com/v1/seasonal"
FORECAST_HORIZON_DAYS = 16
CLIMATOLOGY_YEARS = 10


@dataclass(frozen=True)
class Stop:
    name: str
    lat: float
    lon: float
    tz: str
    days: tuple[date, ...]
    note: str = ""
    #  Quanto do programa nessa paragem é ao ar livre. É o que decide se vale a
    #  pena trocar o dia por causa da chuva: um castelo ao fundo de uma serra
    #  não se troca pelo mesmo motivo que uma tarde de museus.
    outdoor: bool = False


def forecast_horizon() -> date:
    """Último dia com previsão real.

    A Open-Meteo conta o dia de hoje como o primeiro dos 16 que dá, portanto o
    último dia pedível é hoje + 15, não hoje + 16.
    """
    return date.today() + timedelta(days=FORECAST_HORIZON_DAYS - 1)


def d(day: int) -> date:
    return date(2026, 9, day)


# Paragens do roteiro (ver itinerario_viagem.md, "Cronograma Detalhado Dia-a-Dia").
STOPS: list[Stop] = [
    Stop("Lisboa", 38.7223, -9.1393, "Europe/Lisbon", (d(23),), "Partida TP 1270"),
    Stop("Viena", 48.2082, 16.3738, "Europe/Vienna", (d(23), d(24), d(25)), "Dias 1-3", outdoor=True),
    Stop("Augsburg", 48.3705, 10.8978, "Europe/Berlin", (d(25), d(26), d(27), d(28)), "Base dias 3-5"),
    Stop("Neuschwanstein / Füssen", 47.5576, 10.7498, "Europe/Berlin", (d(26),), "Dia 4 — castelo", outdoor=True),
    Stop("Oberammergau", 47.5980, 11.0670, "Europe/Berlin", (d(26),), "Dia 4 — tarde", outdoor=True),
    Stop("Lago Eibsee", 47.4569, 10.9800, "Europe/Berlin", (d(26),), "Dia 4 — fim de tarde", outdoor=True),
    Stop("Rothenburg ob der Tauber", 49.3777, 10.1789, "Europe/Berlin", (d(27),), "Dia 5", outdoor=True),
    Stop("Munique", 48.1351, 11.5820, "Europe/Berlin", (d(28), d(29)), "Oktoberfest + regresso"),
]

# Todos os dias da viagem — a matriz cruza cada paragem com cada um destes.
TRIP_DAYS: tuple[date, ...] = tuple(sorted({x for s in STOPS for x in s.days}))

# O que o resumo do index.html mostra em cada dia: o dia, a zona e as paragens
# que o representam. Espelha os títulos dia-a-dia do itinerario_viagem.md e não
# a lista STOPS, porque o Dia 3 dorme em Augsburg e o Dia 4 tem três paragens ao
# ar livre, que valem por si.
DAY_SUMMARY: list[tuple[date, str, tuple[str, ...]]] = [
    (d(23), "Viena", ("Viena",)),
    (d(24), "Viena", ("Viena",)),
    (d(25), "Augsburg", ("Augsburg",)),
    (d(26), "Alpes", ("Neuschwanstein / Füssen", "Oberammergau", "Lago Eibsee")),
    (d(27), "Rothenburg", ("Rothenburg ob der Tauber",)),
    (d(28), "Munique", ("Munique",)),
    (d(29), "Munique", ("Munique",)),
]

# Nomes curtos para as células estreitas do index.html.
STOP_SHORT = {
    "Neuschwanstein / Füssen": "Neuschwanstein",
    "Rothenburg ob der Tauber": "Rothenburg",
    "Lago Eibsee": "Eibsee",
}

# Marcadores que o `--html` procura no index.html. O bloco entre eles é
# substituído inteiro, para que voltar a correr o comando nunca duplique nada.
WEATHER_HTML_START = "<!-- WEATHER-AUTO:START -->"
WEATHER_HTML_END = "<!-- WEATHER-AUTO:END -->"

HOURLY_VARS = [
    "temperature_2m",
    "apparent_temperature",
    "precipitation_probability",
    "precipitation",
    "weather_code",
    "wind_speed_10m",
    "wind_gusts_10m",
    "cloud_cover",
    "relative_humidity_2m",
]

# Variáveis diárias: normais do arquivo e membros do ensemble sazonal.
DAILY_VARS = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]

# WMO weather codes -> (emoji, descrição PT)
WMO = {
    0: ("☀️", "Céu limpo"), 1: ("🌤️", "Pouco nublado"), 2: ("⛅", "Parcialmente nublado"),
    3: ("☁️", "Encoberto"), 45: ("🌫️", "Nevoeiro"), 48: ("🌫️", "Nevoeiro gelado"),
    51: ("🌦️", "Chuvisco fraco"), 53: ("🌦️", "Chuvisco"), 55: ("🌧️", "Chuvisco forte"),
    56: ("🌧️", "Chuvisco gelado"), 57: ("🌧️", "Chuvisco gelado forte"),
    61: ("🌦️", "Chuva fraca"), 63: ("🌧️", "Chuva"), 65: ("🌧️", "Chuva forte"),
    66: ("🌧️", "Chuva gelada"), 67: ("🌧️", "Chuva gelada forte"),
    71: ("🌨️", "Neve fraca"), 73: ("🌨️", "Neve"), 75: ("❄️", "Neve forte"),
    77: ("❄️", "Grãos de neve"),
    80: ("🌦️", "Aguaceiros fracos"), 81: ("🌧️", "Aguaceiros"), 82: ("⛈️", "Aguaceiros fortes"),
    85: ("🌨️", "Aguaceiros de neve"), 86: ("❄️", "Aguaceiros de neve fortes"),
    95: ("⛈️", "Trovoada"), 96: ("⛈️", "Trovoada com granizo"), 99: ("⛈️", "Trovoada forte"),
}


def describe(code: int | None) -> tuple[str, str]:
    if code is None:
        return ("❔", "—")
    return WMO.get(int(code), ("❔", f"código {int(code)}"))


def synth_code(precip: float | None, cloud: float | None) -> int:
    """Código WMO aproximado a partir de chuva e nebulosidade (usado na climatologia)."""
    mm = precip or 0
    if mm >= 0.5:
        return 63
    if mm >= 0.1:
        return 61
    if mm > 0.02:
        return 51
    cover = cloud if cloud is not None else 0
    if cover >= 85:
        return 3
    if cover >= 50:
        return 2
    if cover >= 20:
        return 1
    return 0


def fetch(url: str, params: dict) -> dict:
    query = urllib.parse.urlencode(params, doseq=True)
    try:
        with urllib.request.urlopen(f"{url}?{query}", timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Erro HTTP {exc.code} da Open-Meteo: {exc.read().decode()[:200]}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"Sem ligação à Open-Meteo: {exc.reason}")


def fetch_forecast(stop: Stop, days: list[date]) -> dict[date, list[dict]]:
    """Previsão real hora-a-hora para as datas dentro do horizonte da API."""
    data = fetch(FORECAST_URL, {
        "latitude": stop.lat,
        "longitude": stop.lon,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": stop.tz,
        "start_date": min(days).isoformat(),
        "end_date": max(days).isoformat(),
    })
    return group_hours(data["hourly"], set(days))


def group_hours(hourly: dict, wanted: set[date]) -> dict[date, list[dict]]:
    out: dict[date, list[dict]] = {day: [] for day in wanted}
    for i, stamp in enumerate(hourly["time"]):
        moment = datetime.fromisoformat(stamp)
        if moment.date() in out:
            out[moment.date()].append(
                {"hour": moment, **{v: hourly[v][i] for v in HOURLY_VARS if v in hourly}}
            )
    return out


def fetch_climatology(stop: Stop, days: list[date]) -> tuple[dict[date, list[dict]], dict[date, dict]]:
    """Média hora-a-hora dos últimos anos nas mesmas datas (ERA5).

    Devolve também as normais diárias (máx./mín./precipitação) desses mesmos
    anos, que servem de referência para a anomalia sazonal.
    """
    this_year = date.today().year
    years = range(this_year - CLIMATOLOGY_YEARS, this_year)
    per_day: dict[date, dict[int, list[dict]]] = {day: {} for day in days}
    daily_samples: dict[date, dict[str, list[float]]] = {
        day: {v: [] for v in DAILY_VARS} for day in days
    }

    for year in years:
        starts = [day.replace(year=year) for day in days]
        data = fetch(ARCHIVE_URL, {
            "latitude": stop.lat,
            "longitude": stop.lon,
            "hourly": ",".join(v for v in HOURLY_VARS if v != "precipitation_probability"),
            "daily": ",".join(DAILY_VARS),
            "timezone": stop.tz,
            "start_date": min(starts).isoformat(),
            "end_date": max(starts).isoformat(),
        })
        hourly = data["hourly"]
        for i, stamp in enumerate(hourly["time"]):
            moment = datetime.fromisoformat(stamp)
            target = date(2026, moment.month, moment.day)
            if target not in per_day:
                continue
            row = {v: hourly[v][i] for v in HOURLY_VARS if v in hourly}
            per_day[target].setdefault(moment.hour, []).append(row)

        daily = data.get("daily", {})
        for i, stamp in enumerate(daily.get("time", [])):
            stamp_date = date.fromisoformat(stamp)
            target = date(2026, stamp_date.month, stamp_date.day)
            if target not in daily_samples:
                continue
            for var in DAILY_VARS:
                value = daily.get(var, [None] * (i + 1))[i]
                if value is not None:
                    daily_samples[target][var].append(value)

    norms = {
        day: {var: (round(statistics.fmean(vals), 1) if vals else None)
              for var, vals in per_var.items()}
        for day, per_var in daily_samples.items()
    }

    out: dict[date, list[dict]] = {}
    for day, by_hour in per_day.items():
        rows = []
        for hour in sorted(by_hour):
            samples = by_hour[hour]
            row: dict = {"hour": datetime.combine(day, datetime.min.time()) + timedelta(hours=hour)}
            for var in HOURLY_VARS:
                values = [s[var] for s in samples if s.get(var) is not None]
                if not values:
                    row[var] = None
                elif var == "weather_code":
                    continue  # médias de códigos WMO não têm significado — ver abaixo
                else:
                    row[var] = round(statistics.fmean(values), 1)
            # Sem probabilidade no arquivo: usa a fracção de anos com chuva nessa hora.
            wet = [s for s in samples if (s.get("precipitation") or 0) >= 0.1]
            row["precipitation_probability"] = round(100 * len(wet) / len(samples)) if samples else None
            # Em climatologia o "tempo" é reconstruído da chuva e da nebulosidade médias,
            # senão a moda dos códigos dá coisas como "céu limpo" com 3 mm de chuva.
            row["weather_code"] = synth_code(row.get("precipitation"), row.get("cloud_cover"))
            rows.append(row)
        out[day] = rows
    return out, norms


def fetch_seasonal(stop: Stop, days: list[date]) -> dict[date, dict]:
    """Tendência sazonal: ensemble de 50 membros (modelo sazonal da Open-Meteo).

    Não é uma previsão detalhada — é o sinal de conjunto para a semana. Devolve
    a mediana e o intervalo p10–p90 entre membros, além da fracção de membros
    com dia de chuva, que é a leitura honesta de "risco de chuva" a este prazo.
    """
    try:
        data = fetch(SEASONAL_URL, {
            "latitude": stop.lat,
            "longitude": stop.lon,
            "daily": ",".join(DAILY_VARS),
            "timezone": stop.tz,
            "start_date": min(days).isoformat(),
            "end_date": max(days).isoformat(),
        })
    except SystemExit:
        return {}  # o modelo sazonal pode não cobrir a janela; não é fatal

    daily = data.get("daily", {})
    wanted = set(days)
    out: dict[date, dict] = {}

    for i, stamp in enumerate(daily.get("time", [])):
        day = date.fromisoformat(stamp)
        if day not in wanted:
            continue
        entry: dict = {}
        for var in DAILY_VARS:
            members = [
                daily[key][i] for key in daily
                if key.startswith(f"{var}_member") and daily[key][i] is not None
            ]
            if not members:
                continue
            members.sort()
            entry[var] = {
                "median": statistics.median(members),
                "p10": members[max(0, int(0.10 * len(members)) - 1)],
                "p90": members[min(len(members) - 1, int(0.90 * len(members)))],
                "n": len(members),
            }
            if var == "precipitation_sum":
                entry["wet_share"] = round(100 * sum(1 for m in members if m >= 1.0) / len(members))
        if entry:
            out[day] = entry
    return out


def seasonal_block(outlook: dict[date, dict], norms: dict[date, dict], markdown: bool) -> list[str]:
    """Tabela de anomalia: ensemble sazonal face à normal dos últimos anos."""
    days = [x for x in sorted(outlook) if x in norms]
    if not days:
        return []

    n_members = next(
        (v["temperature_2m_max"]["n"] for v in outlook.values() if "temperature_2m_max" in v), 0
    )
    header = ["Dia", "Máx. normal", "Máx. sazonal", "Anomalia", "Mín. sazonal", "Chuva normal", "Chuva sazonal", "Membros com chuva"]
    widths = (6, 12, 16, 9, 13, 13, 14, 18)
    lines = [
        (f"**Tendência sazonal** — ensemble de {n_members} membros, sinal semanal apenas "
         f"(sem valor hora-a-hora a este prazo)") if markdown else
        (f"Tendencia sazonal — ensemble de {n_members} membros, sinal semanal apenas "
         f"(sem valor hora-a-hora a este prazo)"),
        "",
    ]
    if markdown:
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))
    else:
        lines.append("  " + "  ".join(h.ljust(w) for h, w in zip(header, widths)))

    for day in days:
        seas, norm = outlook[day], norms[day]
        tmax = seas.get("temperature_2m_max")
        tmin = seas.get("temperature_2m_min")
        rain = seas.get("precipitation_sum")
        norm_max = norm.get("temperature_2m_max")
        anomaly = (tmax["median"] - norm_max) if tmax and norm_max is not None else None
        cells = [
            day.strftime("%d/%m"),
            fmt(norm_max, " °C", 1),
            f"{tmax['median']:.0f} °C ({tmax['p10']:.0f}–{tmax['p90']:.0f})" if tmax else "—",
            f"{anomaly:+.1f} °C" if anomaly is not None else "—",
            f"{tmin['median']:.0f} °C ({tmin['p10']:.0f}–{tmin['p90']:.0f})" if tmin else "—",
            fmt(norm.get("precipitation_sum"), " mm", 1),
            f"{rain['median']:.1f} mm" if rain else "—",
            fmt(seas.get("wet_share"), "%"),
        ]
        if markdown:
            lines.append("| " + " | ".join(cells) + " |")
        else:
            lines.append("  " + "  ".join(c.ljust(w) for c, w in zip(cells, widths)))

    lines.append("")
    return lines


def day_summary(rows: list[dict]) -> str:
    temps = [r["temperature_2m"] for r in rows if r.get("temperature_2m") is not None]
    rain = sum(r.get("precipitation") or 0 for r in rows)
    prob = [r["precipitation_probability"] for r in rows if r.get("precipitation_probability") is not None]
    gust = [r["wind_gusts_10m"] for r in rows if r.get("wind_gusts_10m") is not None]
    codes = [int(r["weather_code"]) for r in rows if r.get("weather_code") is not None]
    emoji, desc = describe(statistics.mode(codes) if codes else None)
    parts = [f"{emoji} {desc}"]
    if temps:
        parts.append(f"{min(temps):.0f}–{max(temps):.0f} °C")
    parts.append(f"chuva {rain:.1f} mm" + (f", máx. {max(prob):.0f}% prob." if prob else ""))
    if gust:
        parts.append(f"rajadas até {max(gust):.0f} km/h")
    return " · ".join(parts)


def fmt(value, unit: str = "", nd: int = 0) -> str:
    if value is None:
        return "—"
    return f"{value:.{nd}f}{unit}"


def day_table(rows: list[dict], markdown: bool) -> list[str]:
    header = ["Hora", "Tempo", "Temp", "Sensação", "Chuva", "Prob.", "Vento", "Rajada", "Nuvens"]
    lines = []
    if markdown:
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))
    else:
        lines.append("  " + "  ".join(h.ljust(w) for h, w in zip(header, (5, 22, 7, 9, 8, 6, 9, 8, 6))))
    for r in rows:
        emoji, desc = describe(r.get("weather_code"))
        cells = [
            r["hour"].strftime("%H:%M"),
            f"{emoji} {desc}",
            fmt(r.get("temperature_2m"), " °C"),
            fmt(r.get("apparent_temperature"), " °C"),
            fmt(r.get("precipitation"), " mm", 1),
            fmt(r.get("precipitation_probability"), "%"),
            fmt(r.get("wind_speed_10m"), " km/h"),
            fmt(r.get("wind_gusts_10m"), " km/h"),
            fmt(r.get("cloud_cover"), "%"),
        ]
        if markdown:
            lines.append("| " + " | ".join(cells) + " |")
        else:
            lines.append("  " + "  ".join(c.ljust(w) for c, w in zip(cells, (5, 22, 7, 9, 8, 6, 9, 8, 6))))
    return lines


WEEKDAYS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MONTHS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
          "agosto", "setembro", "outubro", "novembro", "dezembro"]


def pretty_date(day: date) -> str:
    return f"{WEEKDAYS[day.weekday()]}, {day.day} de {MONTHS[day.month - 1]} de {day.year}"


def collect(stop: Stop, days: list[date], skip_seasonal: bool
            ) -> tuple[dict[date, list[dict]], dict[date, str], dict[date, dict], dict[date, dict]]:
    """Recolhe os dados de um sítio, escolhendo a fonte conforme a distância de cada dia."""
    horizon = forecast_horizon()
    near = [x for x in days if x <= horizon]
    far = [x for x in days if x > horizon]

    rows_by_day: dict[date, list[dict]] = {}
    source: dict[date, str] = {}
    norms: dict[date, dict] = {}
    outlook: dict[date, dict] = {}

    if near:
        rows_by_day.update(fetch_forecast(stop, near))
        source.update({x: "previsão" for x in near})
    if far:
        hourly_clim, norms = fetch_climatology(stop, far)
        rows_by_day.update(hourly_clim)
        source.update({x: "climatologia" for x in far})
        if not skip_seasonal:
            outlook = fetch_seasonal(stop, far)

    return rows_by_day, source, norms, outlook


def day_facts(rows: list[dict]) -> tuple[str, float | None, float]:
    """Tempo, máxima e chuva de um dia, para a matriz e para o resumo HTML.

    A máxima sai em bruto, e não já formatada, porque o markdown escreve «—»
    quando não há dado e o index.html não pode: a regra 6 proíbe o travessão lá.
    """
    temps = [r["temperature_2m"] for r in rows if r.get("temperature_2m") is not None]
    rain = sum(r.get("precipitation") or 0 for r in rows)
    codes = [int(r["weather_code"]) for r in rows if r.get("weather_code") is not None]
    emoji, _ = describe(statistics.mode(codes) if codes else None)
    return emoji, (max(temps) if temps else None), rain


def day_cell(rows: list[dict]) -> str:
    """Resumo de um dia numa célula: tempo, máxima e chuva."""
    emoji, tmax, rain = day_facts(rows)
    return f"{emoji} {fmt(tmax, '°')} {rain:.1f}mm"


def matrix_block(stops: list[Stop], markdown: bool) -> list[str]:
    """Todas as cidades em todos os dias da viagem, lado a lado.

    É a tabela para decidir trocas: se o sábado do Neuschwanstein vier
    encharcado e o domingo de Rothenburg vier seco, troca-se.
    """
    days = sorted(TRIP_DAYS)
    grid: dict[str, dict[date, str]] = {}
    wet: dict[str, dict[date, float]] = {}

    for stop in stops:
        rows_by_day, _, _, _ = collect(stop, days, skip_seasonal=True)
        grid[stop.name] = {}
        wet[stop.name] = {}
        for day, rows in rows_by_day.items():
            if rows:
                grid[stop.name][day] = day_cell(rows)
                wet[stop.name][day] = sum(r.get("precipitation") or 0 for r in rows)

    if not grid:
        return []

    name_w = max(len(n) for n in grid) + 4
    header = ["Paragem"] + [f"{WEEKDAYS[x.weekday()][:3]} {x.strftime('%d/%m')}" for x in days]
    lines = [
        f"{'## ' if markdown else ''}Matriz — todas as paragens, todos os dias",
        "",
        ("Para decidir trocas de dia. Cada célula: tempo · máxima · chuva total. "
         + ("🏞️ marca" if markdown else "* marca") + " as paragens em que o programa é ao ar livre."),
        "",
    ]
    if markdown:
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))
    else:
        lines.append("  " + "Paragem".ljust(name_w) + "  ".join(h.ljust(14) for h in header[1:]))

    for stop in stops:
        if stop.name not in grid:
            continue
        # Na consola o emoji ocupa duas colunas e desalinha a tabela; ali usa-se um asterisco.
        mark = ("🏞️ " if markdown else "* ") if stop.outdoor else ("" if markdown else "  ")
        cells = []
        for day in days:
            cell = grid[stop.name].get(day, "—")
            # Um asterisco marca os dias em que essa paragem está mesmo agendada.
            cells.append(f"**{cell}**" if markdown and day in stop.days else
                         (f"[{cell}]" if not markdown and day in stop.days else cell))
        if markdown:
            lines.append("| " + " | ".join([mark + stop.name] + cells) + " |")
        else:
            lines.append("  " + (mark + stop.name).ljust(name_w) + "  ".join(c.ljust(14) for c in cells))

    lines.append("")
    lines.append("Dias agendados marcados a negrito." if markdown
                 else "Dias agendados marcados [entre parenteses rectos].")
    lines.append("")
    lines.extend(swap_hints(stops, wet, markdown))
    return lines


def swap_hints(stops: list[Stop], wet: dict[str, dict[date, float]], markdown: bool) -> list[str]:
    """Assinala paragens ao ar livre cujo dia agendado é dos mais chuvosos."""
    hints: list[str] = []
    days = sorted(TRIP_DAYS)

    for stop in stops:
        if not stop.outdoor or stop.name not in wet:
            continue
        rain = wet[stop.name]
        scheduled = [x for x in stop.days if x in rain]
        if not scheduled:
            continue
        worst = max(rain[x] for x in scheduled)
        # Dias alternativos claramente mais secos: pelo menos metade da chuva e 1 mm menos.
        better = sorted(
            (x for x in days if x not in stop.days and x in rain
             and rain[x] < worst / 2 and worst - rain[x] >= 1.0),
            key=lambda x: rain[x],
        )
        if better:
            alts = ", ".join(f"{x.strftime('%d/%m')} ({rain[x]:.1f} mm)" for x in better[:3])
            hints.append(f"- **{stop.name}**: agendado com até {worst:.1f} mm; mais seco em {alts}."
                         if markdown else
                         f"  - {stop.name}: agendado com ate {worst:.1f} mm; mais seco em {alts}.")

    if not hints:
        return ["Nenhuma paragem ao ar livre calha num dia claramente pior que as alternativas.", ""]

    head = "**Possíveis trocas**" if markdown else "Possiveis trocas"
    tail = ("Sugestão baseada só na chuva — confirmar contra bilhetes com hora marcada "
            "(Neuschwanstein, Schönbrunn) e contra a rota, que nem todos os dias são trocáveis.")
    return [head, ""] + hints + ["", tail, ""]


def render_weather_html() -> list[str]:
    """Bloco do index.html: uma célula por dia da viagem, com a fonte rotulada.

    Sai embrulhado nos marcadores WEATHER_HTML_* para o `--html` ser idempotente.
    Não leva travessão nenhum: o verificar.py recusa o carácter no index.html.
    """
    by_name = {s.name: s for s in STOPS}
    needed: dict[str, list[date]] = {}
    for day, _, names in DAY_SUMMARY:
        for name in names:
            needed.setdefault(name, []).append(day)

    #  Uma recolha por paragem, com todos os seus dias de uma vez: agrupar poupa
    #  as dez chamadas de arquivo por cada ano da climatologia.
    facts: dict[tuple[str, date], tuple[str, float | None, float, str]] = {}
    for name, days in needed.items():
        rows_by_day, source, _, _ = collect(by_name[name], sorted(days), skip_seasonal=True)
        for day in days:
            emoji, tmax, rain = day_facts(rows_by_day.get(day, []))
            facts[(name, day)] = (emoji, tmax, rain, source.get(day, "previsão"))

    hoje = pretty_date(date.today())
    out = [
        WEATHER_HTML_START,
        f"<!-- Gerado por python meteo.py --html index.html a {hoje}."
        " Não editar à mão: correr o comando outra vez. -->",
        '<div class="weather-strip">',
    ]

    for day, place, names in DAY_SUMMARY:
        source = facts[(names[0], day)][3]
        forecast = source == "previsão"
        numero = (day - d(23)).days + 1
        rotulo = f"{WEEKDAYS[day.weekday()][:3].capitalize()} {day.day}"
        out.append('    <div class="weather-day-card">')
        out.append('        <div class="weather-day-head">')
        out.append(f'            <span class="weather-day-label">Dia {numero} · {rotulo}</span>')
        out.append(f'            <span class="weather-src {"is-forecast" if forecast else "is-clima"}">'
                   f'{"previsão" if forecast else "média 10 anos"}</span>')
        out.append('        </div>')
        if len(names) > 1:
            out.append(f'        <div class="weather-day-place">{place}</div>')
        for name in names:
            emoji, tmax, rain, _ = facts[(name, day)]
            curto = STOP_SHORT.get(name, name)
            temp = f"{tmax:.0f}°" if tmax is not None else "?"
            out.append('        <div class="weather-stop-row">')
            out.append(f'            <span class="weather-stop-name">{curto}</span>')
            out.append(f'            <span class="weather-stop-temp">{temp}</span>')
            out.append(f'            <span class="weather-stop-rain">{emoji} {rain:.1f} mm</span>')
            out.append('        </div>')
        out.append('    </div>')

    out.append('</div>')
    out.append('<p class="weather-note"><strong>Como ler isto.</strong> «previsão» é o modelo '
               'real, que só tem detalhe até cerca de 10 dias de distância. «média 10 anos» é a média '
               'dos últimos 10 anos (ERA5) para a mesma data, que não é uma previsão. A tabela hora a '
               'hora e a tendência sazonal estão no <strong>meteo.md</strong>, e o comando que gera '
               'estes números é o mesmo que o gera a ele.</p>')
    out.append(WEATHER_HTML_END)
    return out


def inject_html(path: str, block: list[str]) -> None:
    """Substitui o que estiver entre os marcadores pelo bloco novo.

    Aborta se os marcadores não existirem, em vez de não fazer nada em silêncio:
    um `--html` que corre e não escreve é pior do que um que falha.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        html = fh.read()
    if WEATHER_HTML_START not in html or WEATHER_HTML_END not in html:
        raise SystemExit(f"{path}: faltam os marcadores {WEATHER_HTML_START} / {WEATHER_HTML_END}.")

    #  Preservar o fim de linha do ficheiro, para o bloco não ficar com um
    #  terminador diferente do resto e a página inteira aparecer como alterada.
    nl = "\r\n" if "\r\n" in html else "\n"
    before, resto = html.split(WEATHER_HTML_START, 1)
    _, after = resto.split(WEATHER_HTML_END, 1)

    #  A indentação do marcador, lida da sua própria linha (a última do `before`).
    corte = before.rfind(nl) + len(nl)
    recuo = before[corte:] if not before[corte:].strip() else ""
    if not recuo:
        #  Marcador na coluna 1, como fica depois de uma injeção antiga: herda a
        #  indentação da última linha com conteúdo, para o bloco não desalinhar.
        anterior = before[:corte].rstrip(" \t" + nl).rsplit(nl, 1)[-1]
        recuo = anterior[:len(anterior) - len(anterior.lstrip(" \t"))]
    #  Normalizar os dois lados, para que uma injeção anterior não deixe para trás
    #  linhas só com espaços, que se acumulariam a cada passagem.
    antes = before[:corte].rstrip(" \t" + nl) if corte else before.rstrip(" \t" + nl)
    depois = after.lstrip(nl)

    corpo = nl.join((recuo + linha) if linha else linha for linha in block)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(f"{antes}{nl}{nl}{corpo}{nl}{nl}{depois}")


def build_report(stops: list[Stop], only_next_24h: bool, markdown: bool,
                 skip_seasonal: bool = False, show_matrix: bool = True,
                 all_days: bool = False) -> list[str]:
    today = date.today()
    out: list[str] = []
    h1, h2 = ("# ", "## ") if markdown else ("", "")

    out.append(f"{h1}Meteorologia — Viena & Munique 2026")
    out.append("")
    out.append(f"Actualizado a {pretty_date(today)} · fonte: Open-Meteo")
    out.append("")

    if show_matrix and not only_next_24h:
        out.extend(matrix_block(stops, markdown))

    for stop in stops:
        days = sorted(stop.days) if not all_days else sorted(TRIP_DAYS)
        if only_next_24h:
            days = [today, today + timedelta(days=1)]

        rows_by_day, source, norms, outlook = collect(stop, days, skip_seasonal)

        label = f"{stop.name}" + (f" — {stop.note}" if stop.note and not only_next_24h else "")
        out.append(f"{h2}{label}")
        out.append("")

        if outlook:
            out.extend(seasonal_block(outlook, norms, markdown))

        if only_next_24h:
            # Janela contínua de 24 h a partir da hora actual, atravessando a meia-noite.
            start = datetime.now().replace(minute=0, second=0, microsecond=0)
            window = [r for day in sorted(rows_by_day) for r in rows_by_day[day]
                      if start <= r["hour"] < start + timedelta(hours=24)]
            rows_by_day = {}
            for row in window:
                rows_by_day.setdefault(row["hour"].date(), []).append(row)

        for day in sorted(rows_by_day):
            rows = rows_by_day[day]
            if not rows:
                continue
            tag = "" if source[day] == "previsão" else \
                f"  ⚠️ média dos últimos {CLIMATOLOGY_YEARS} anos (fora do horizonte de previsão)"
            out.append(f"**{pretty_date(day)}** — {day_summary(rows)}{tag}" if markdown
                       else f"{pretty_date(day)} — {day_summary(rows)}{tag}")
            out.append("")
            out.extend(day_table(rows, markdown))
            out.append("")
    return out


def main() -> int:
    # Consolas Windows usam cp1252 por omissão e rebentam com os emojis.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description="Previsão hora-a-hora do roteiro Viena + Munique.")
    parser.add_argument("--cidade", help="filtra por nome (parcial, sem distinção de maiúsculas)")
    parser.add_argument("--hoje", action="store_true", help="mostra só as próximas 24 h em cada paragem")
    parser.add_argument("--md", metavar="FICHEIRO", help="escreve o relatório em markdown")
    parser.add_argument("--html", metavar="FICHEIRO",
                        help="injeta o resumo por dia no index.html, entre os marcadores WEATHER-AUTO")
    parser.add_argument("--listar", action="store_true", help="lista as paragens e sai")
    parser.add_argument("--sem-sazonal", action="store_true",
                        help="não consulta o modelo sazonal (mais rápido)")
    parser.add_argument("--sem-matriz", action="store_true",
                        help="não mostra a matriz paragens × dias")
    parser.add_argument("--matriz", action="store_true",
                        help="mostra só a matriz paragens × dias, sem as tabelas horárias")
    parser.add_argument("--todos-os-dias", action="store_true",
                        help="tabelas horárias de cada paragem para todos os dias da viagem")
    args = parser.parse_args()

    if args.listar:
        for stop in STOPS:
            dias = ", ".join(x.strftime("%d/%m") for x in sorted(stop.days))
            print(f"{stop.name:28} {dias:20} {stop.note}")
        return 0

    stops = STOPS
    if args.cidade:
        needle = args.cidade.casefold()
        stops = [s for s in STOPS if needle in s.name.casefold()]
        if not stops:
            print(f"Nenhuma paragem corresponde a {args.cidade!r}. Use --listar.", file=sys.stderr)
            return 1

    escrever_md = bool(args.md)
    #  Não se constrói o relatório quando o destino é só o index.html: ninguém lê
    #  a matriz em texto e montá-la custa uma recolha inteira. Mas o `--matriz` é
    #  um pedido explícito, e aí imprime-se mesmo com `--html` ao lado.
    if escrever_md or args.matriz or not args.html:
        if args.matriz:
            lines = matrix_block(stops, markdown=escrever_md)
        else:
            lines = build_report(stops, args.hoje, markdown=escrever_md,
                                 skip_seasonal=args.sem_sazonal,
                                 show_matrix=not args.sem_matriz,
                                 all_days=args.todos_os_dias)
        if escrever_md:
            with open(args.md, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
            print(f"Relatório escrito em {args.md}")
        else:
            print("\n".join(lines))

    if args.html:
        inject_html(args.html, render_weather_html())
        print(f"Previsão por dia injetada em {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
