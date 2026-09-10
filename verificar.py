#!/usr/bin/env python3
"""Verificador de coerência do dossiê de viagem Viena + Munique 2026.

Faz as perguntas chatas que ninguém se lembra de fazer antes de dar por fechada
uma alteração: os horários do dia ainda fecham? o preço que alterei mudou nos dois
ficheiros? quantas pessoas diz este bilhete? o prazo já passou?

Não sabe nada sobre o mundo: não vai à internet e não valida se um preço está
certo, só se está *coerente* entre `itinerario_viagem.md` e `index.html`. A
verificação factual continua a ser confirmada em fonte primária, à mão.

Biblioteca padrão apenas. Sem dependências, sem rede.

Uso:
    python verificar.py                 # tudo
    python verificar.py --dia 4         # só o Dia 4
    python verificar.py --so-erros      # só o que está mal
    python verificar.py --seccao horarios precos
    python verificar.py --listar        # nomes das secções

Código de saída: 1 se houver algum ERRO, 0 caso contrário (os AVISOS não
chumbam, porque muitos são legítimos e têm de ser vistos por uma pessoa).
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
MD = RAIZ / "itinerario_viagem.md"
HTML = RAIZ / "index.html"
METEO = RAIZ / "meteo.md"

#  O bloco da previsão dentro do index.html, gerado pelo `meteo.py --html`. Os
#  marcadores são os mesmos que o meteo.py procura, e é isso que permite ao
#  verificador saber se o guia e o relatório saíram da mesma passagem.
WEATHER_START = "<!-- WEATHER-AUTO:START -->"
WEATHER_END = "<!-- WEATHER-AUTO:END -->"

#  A viagem. Se estas datas mudarem, muda tudo o resto.
ANO = 2026
MES = 9
DIAS_VIAGEM = {
    1: (date(ANO, MES, 23), "Quarta-feira"),
    2: (date(ANO, MES, 24), "Quinta-feira"),
    3: (date(ANO, MES, 25), "Sexta-feira"),
    4: (date(ANO, MES, 26), "Sábado"),
    5: (date(ANO, MES, 27), "Domingo"),
    6: (date(ANO, MES, 28), "Segunda-feira"),
    7: (date(ANO, MES, 29), "Terça-feira"),
}
ABREV = {
    "Quarta-feira": "Qua", "Quinta-feira": "Qui", "Sexta-feira": "Sex",
    "Sábado": "Sáb", "Domingo": "Dom", "Segunda-feira": "Seg", "Terça-feira": "Ter",
}

#  O grupo. É a armadilha que mais vezes apanhou este dossiê: 4 pessoas em Viena
#  nos dias 1 a 3, 6 a partir da noite do Dia 3. Sete nunca. Foram 7 numa versão
#  antiga do plano e ainda aparecem restos.
PAX_VIENA = 4
PAX_TOTAL = 6

#  Os únicos iconType que o getMarkerMeta() de index.html sabe desenhar. Um valor
#  fora desta lista não rebenta nada: cai no pin azul genérico, e o marcador fica
#  visualmente errado sem ninguém dar por isso.
ICON_TYPES = {"plane", "train", "hotel", "castle", "beer", "water", "car", "cocktail",
              "food", "monument"}

#  Caixa que contém a viagem toda, com folga. Serve para apanhar uma coordenada
#  trocada: uma latitude e uma longitude invertidas caem sempre fora desta área.
BBOX = (36.0, 51.0, -10.5, 18.0)  # lat_min, lat_max, lon_min, lon_max

ERRO, AVISO, INFO = "ERRO", "AVISO", "INFO"
PESO = {ERRO: 0, AVISO: 1, INFO: 2}
SIMBOLO = {ERRO: "🔴", AVISO: "⚠️ ", INFO: "· "}


@dataclass
class Achado:
    nivel: str
    onde: str
    texto: str


@dataclass
class Seccao:
    nome: str
    titulo: str
    achados: list[Achado] = field(default_factory=list)

    def erro(self, onde: str, texto: str) -> None:
        self.achados.append(Achado(ERRO, onde, texto))

    def aviso(self, onde: str, texto: str) -> None:
        self.achados.append(Achado(AVISO, onde, texto))

    def info(self, onde: str, texto: str) -> None:
        self.achados.append(Achado(INFO, onde, texto))


# ---------------------------------------------------------------- utilitários

def ler(caminho: Path) -> list[str]:
    if not caminho.exists():
        sys.exit(f"Falta o ficheiro {caminho.name}. Este script corre a partir da raiz do dossiê.")
    return caminho.read_text(encoding="utf-8").splitlines()


def sem_acentos(txt: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn")


def minutos(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def hhmm(mins: int) -> str:
    mins %= 1440
    return f"{mins // 60:02d}:{mins % 60:02d}"


#  Um bloco horário do itinerário. `- **10:30 – 12:05**: Condução pela B17`
#  O intervalo separa-se por meio travessão ou hífen, e a hora pode vir
#  aproximada (~02:30) ou com mínimo (≥1h), daí a tolerância no padrão.
#
#  O último grupo apanha os blocos em que não fica apenas a hora a negrito, mas
#  a ordem toda, como `- **22:20, sair da mesa. Não às 22:30.**`. Sem ele, o
#  bloco mais importante do Dia 6 passava despercebido à verificação. Aceita
#  vírgula, dois pontos e ponto médio além do hífen, porque a regra da casa
#  proibiu o travessão que ali estava e a pontuação de substituição varia.
RE_BLOCO = re.compile(
    r"^-\s+\*\*[~≈]?(?P<ini>\d{1,2}:\d{2})"
    r"(?:\s*[–—-]\s*[~≈]?(?P<fim>\d{1,2}:\d{2}))?"
    r"(?:\s*[–—,:·-][^*]*)?"
    r"\*\*"
)
RE_DIA_MD = re.compile(r"^###\s+.*?Dia\s+(?P<n>\d)\s*:\s*(?P<resto>.+)$")
RE_ACORDAR = re.compile(r"Acordar\s+[~≈]?(?P<acordar>\d{1,2}:\d{2})")
#  «Dia longo assumido: 20h15». Um dia que se sabe pesado diz quanto pesa.
RE_DIA_LONGO = re.compile(r"Dia longo assumido:\s*(?P<h>\d{1,2})h(?P<m>\d{2})", re.IGNORECASE)
RE_SAIR = re.compile(r"Sair\s+[~≈]?(?P<sair>\d{1,2}:\d{2})")
RE_DINHEIRO = re.compile(r"€\s?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)")

#  Início de um item de lista ou de uma linha de tabela. Serve para saber onde
#  acaba um item e começa o seguinte, quando um item ocupa várias linhas e a
#  marca que interessa ficou só na primeira.
RE_ITEM = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|\|)")

#  Pistas de que os números de um item são a decomposição de um total, e não
#  preços soltos: «total €427,58», «os €5,50 decompõem-se em €2,30 + €3,20».
#  Deliberadamente restrito a palavras que anunciam um total. Aceitar o «+» ou o
#  «=» sozinhos parecia natural e é demasiado: quase todas as linhas de preço
#  deste dossiê somam alguma coisa, e a verificação de preços emudeceu por
#  completo quando os incluí.
RE_DECOMPOSICAO = re.compile(r"\btotal\b|\bdecomp|\bdividido\b|\bsoma", re.IGNORECASE)

#  «daqui a duas semanas», «faltam ~6 semanas». Contagens ancoradas no dia em que
#  alguém as escreveu, que passam a mentir no dia seguinte.
RE_RELATIVA = re.compile(
    r"daqui a [^.,;)]{1,25}?(?:semanas?|dias?|meses|mês)"
    r"|faltam\s+~?\s?\d+\s+(?:semanas?|dias?|meses)",
    re.IGNORECASE)


@dataclass
class Bloco:
    linha: int
    ini: int
    fim: int | None
    texto: str


#  Marcas de que uma linha fala de uma opção rejeitada, corrigida ou retirada do
#  plano. Os preços que aparecem nessas linhas existem para justificar uma
#  decisão, não para serem pagos, e por isso não têm de ter correspondência no
#  outro documento. Um preço riscado (`~~`) não entra aqui de propósito: neste
#  dossiê riscado quer dizer «já comprado», e esse é bem real.
MARCAS_EMOJI = ("🚫", "❌", "🗑️")
MARCAS_TEXTO = ("desatualizad", "não existe", "foi retirado", "estimativa antiga")


def descartadas(linhas: list[str]) -> list[bool]:
    """Diz, para cada linha, se fala de uma opção descartada.

    A marca costuma estar na primeira linha de uma citação (`>`) e os números
    aparecem duas ou três linhas abaixo, ainda dentro da mesma citação, como no
    aviso sobre os revendedores da Oktoberfest. Daí arrastar o estado enquanto a
    citação durar.
    """
    resultado: list[bool] = []
    citacao_descartada = False
    for ln in linhas:
        baixa = ln.lower()
        marcada = (any(x in ln for x in MARCAS_EMOJI)
                   or any(x in baixa for x in MARCAS_TEXTO))
        if ln.lstrip().startswith(">"):
            citacao_descartada = citacao_descartada or marcada
        else:
            citacao_descartada = False
        resultado.append(marcada or citacao_descartada)
    return resultado


def dias_do_markdown(linhas: list[str]) -> dict[int, tuple[int, int, str]]:
    """Devolve {n_dia: (linha_inicio, linha_fim, cabeçalho)}, com as linhas numeradas a partir de 1."""
    marcas: list[tuple[int, int, str]] = []
    for i, ln in enumerate(linhas):
        m = RE_DIA_MD.match(ln)
        if m:
            marcas.append((i, int(m.group("n")), ln))
    dias: dict[int, tuple[int, int, str]] = {}
    for k, (i, n, cab) in enumerate(marcas):
        fim = marcas[k + 1][0] if k + 1 < len(marcas) else len(linhas)
        dias[n] = (i, fim, cab)
    return dias


# ------------------------------------------------------------------- secções

def check_dias(md: list[str], html: list[str]) -> Seccao:
    """Os sete dias existem nos dois ficheiros e falam da mesma data."""
    s = Seccao("dias", "Os sete dias, nos dois ficheiros")
    dias_md = dias_do_markdown(md)

    for n in sorted(DIAS_VIAGEM):
        if n not in dias_md:
            s.erro("itinerario_viagem.md", f"não há cabeçalho para o Dia {n}.")
    for n in sorted(set(dias_md) - set(DIAS_VIAGEM)):
        s.erro("itinerario_viagem.md", f"Dia {n} não pertence à viagem (23–29 de setembro).")

    #  Dois cabeçalhos com o mesmo número deixam metade do dia fora de todas as
    #  verificações seguintes, sem se notar em lado nenhum.
    vistos: dict[int, int] = {}
    for i, ln in enumerate(md):
        if m := RE_DIA_MD.match(ln):
            n = int(m.group("n"))
            if n in vistos:
                s.erro(f"itinerario_viagem.md:{i + 1}",
                       f"segundo cabeçalho para o Dia {n} (o primeiro está na linha {vistos[n]}).")
            vistos[n] = i + 1

    #  A data e o dia da semana escritos no cabeçalho têm de bater certo com o
    #  calendário real de 2026. Um "Sábado, 26" que na verdade é domingo passa
    #  despercebido a olho e desmonta o plano todo.
    for n, (i, _, cab) in sorted(dias_md.items()):
        if n not in DIAS_VIAGEM:
            continue
        esperada, semana = DIAS_VIAGEM[n]
        if not re.search(rf"\b{esperada.day}\s+de\s+[Ss]etembro", cab):
            s.erro(f"itinerario_viagem.md:{i + 1}", f"Dia {n} devia dizer «{esperada.day} de Setembro».")
        if sem_acentos(semana).lower() not in sem_acentos(cab).lower():
            s.erro(f"itinerario_viagem.md:{i + 1}", f"Dia {n} é {semana}, o cabeçalho diz outra coisa.")

    texto_html = "\n".join(html)
    for n, (esperada, semana) in sorted(DIAS_VIAGEM.items()):
        if f'id="day-view-{n}"' not in texto_html:
            s.erro("index.html", f"falta o painel <div id=\"day-view-{n}\">.")
        if f'data-day="{n}"' not in texto_html:
            s.erro("index.html", f"falta o separador data-day=\"{n}\".")
        etiqueta = f"{ABREV[semana]} {esperada.day}"
        if etiqueta not in texto_html:
            s.erro("index.html", f"o separador do Dia {n} devia mostrar «{etiqueta}».")

    n_paineis = texto_html.count('class="day-view-container')
    n_tabs = texto_html.count('class="day-tab-card')
    if n_paineis != len(DIAS_VIAGEM) or n_tabs != len(DIAS_VIAGEM):
        s.erro("index.html", f"{n_tabs} separadores para {n_paineis} painéis; deviam ser {len(DIAS_VIAGEM)} de cada.")

    return s


def check_horarios(md: list[str], filtro: int | None) -> Seccao:
    """Cada dia tem de fechar: sem andar para trás no relógio e sem sair antes de acordar."""
    s = Seccao("horarios", "Os horários fecham, dia a dia")
    dias_md = dias_do_markdown(md)

    for n, (i, fim, _) in sorted(dias_md.items()):
        if filtro and n != filtro:
            continue
        corpo = md[i:fim]

        acordar = sair = declarado = None
        for ln in corpo[:6]:
            if m := RE_ACORDAR.search(ln):
                acordar = minutos(m.group("acordar"))
            if m := RE_SAIR.search(ln):
                sair = minutos(m.group("sair"))
            if m := RE_DIA_LONGO.search(ln):
                declarado = int(m.group("h")) * 60 + int(m.group("m"))

        blocos: list[Bloco] = []
        for k, ln in enumerate(corpo):
            m = RE_BLOCO.match(ln)
            if not m:
                continue
            f = m.group("fim")
            blocos.append(Bloco(i + k + 1, minutos(m.group("ini")),
                                minutos(f) if f else None, ln.strip()[:70]))

        if not blocos:
            s.aviso(f"Dia {n}", "não encontrei blocos horários. O dia está escrito noutro formato?")
            continue

        if acordar is not None and sair is not None and sair < acordar:
            s.erro(f"Dia {n}", f"sai às {hhmm(sair)} mas só acorda às {hhmm(acordar)}.")

        primeiro = blocos[0]
        if sair is not None and primeiro.ini < sair:
            s.erro(f"Dia {n}:{primeiro.linha}",
                   f"o primeiro bloco começa às {hhmm(primeiro.ini)}, antes da hora de sair ({hhmm(sair)}).")
        elif acordar is not None and sair is None and primeiro.ini < acordar:
            s.erro(f"Dia {n}:{primeiro.linha}",
                   f"o primeiro bloco começa às {hhmm(primeiro.ini)}, antes de acordar ({hhmm(acordar)}).")

        #  `desvio` acumula as passagens de meia-noite: a noite do Dia 1 acaba às
        #  02:30 e isso não é andar para trás no tempo. Distingue-se de uma
        #  sobreposição verdadeira por um critério simples: se somar 24 horas
        #  coloca o bloco logo a seguir ao anterior (até 6 h depois), foi a
        #  meia-noite que passou; se o atira para o dia seguinte, é um erro.
        desvio = 0
        anterior: Bloco | None = None
        fim_anterior = None
        for b in blocos:
            ini_abs = b.ini + desvio
            if fim_anterior is not None and ini_abs < fim_anterior:
                if 0 <= (ini_abs + 1440) - fim_anterior <= 6 * 60:
                    desvio += 1440
                    ini_abs = b.ini + desvio
                else:
                    sobreposicao = fim_anterior - ini_abs
                    queixa = (f"começa às {hhmm(b.ini)} mas o bloco anterior "
                              f"({hhmm(anterior.ini)}) só acaba às {hhmm(fim_anterior)}, "
                              f"com {sobreposicao} min sobrepostos.")
                    #  Cinco minutos de sobreposição são arredondamento; meia hora
                    #  é uma visita que não cabe onde está escrita.
                    (s.erro if sobreposicao >= 10 else s.aviso)(f"Dia {n}:{b.linha}", queixa)
            if b.fim is not None:
                fim_abs = b.fim + desvio
                if fim_abs < ini_abs:
                    #  O próprio bloco atravessa a meia-noite (22:30 – 02:30).
                    #  O `desvio` sobe já aqui para que o bloco seguinte não
                    #  tenha de ser adivinhado pela heurística acima.
                    desvio += 1440
                    fim_abs += 1440
                if fim_abs == ini_abs:
                    s.aviso(f"Dia {n}:{b.linha}", f"bloco de duração zero às {hhmm(b.ini)}.")
                folga = ini_abs - fim_anterior if fim_anterior is not None else 0
                if folga >= 30:
                    s.info(f"Dia {n}:{b.linha}", f"{folga} min de folga antes das {hhmm(b.ini)}.")
                fim_anterior = fim_abs
            else:
                fim_anterior = ini_abs
            anterior = b

        if fim_anterior is not None:
            duracao = fim_anterior - (sair if sair is not None else blocos[0].ini)
            rotulo = f"{duracao // 60}h{duracao % 60:02d}"
            #  Um dia pode assumir-se longo, mas tem de dizer *quanto*. Se o
            #  número declarado bater certo com o medido, o dia é uma escolha e
            #  não um descuido, e fica em informação. Se alguém lhe acrescentar
            #  duas horas mais tarde, os números deixam de bater e o aviso
            #  volta, que é precisamente quando ele serve para alguma coisa.
            #  Um aviso permanente sobre um facto conhecido não é verificação,
            #  é ruído a tapar os avisos que interessam.
            if declarado is not None:
                if declarado == duracao:
                    s.info(f"Dia {n}", f"{rotulo} de programa seguido, assumido no documento.")
                else:
                    s.aviso(f"Dia {n}",
                            f"o dia declara {declarado // 60}h{declarado % 60:02d} de programa "
                            f"seguido mas tem {rotulo}. Atualizar a declaração ou encurtar o dia.")
            elif duracao > 17 * 60:
                s.aviso(f"Dia {n}", f"o dia tem {rotulo} de programa seguido.")

    return s


def check_precos(md: list[str], html: list[str]) -> Seccao:
    """Um preço que só existe num dos ficheiros é quase sempre um preço por atualizar."""
    s = Seccao("precos", "Preços presentes num ficheiro e ausentes no outro")

    def blocos_de(linhas: list[str]) -> list[int]:
        """Dá a cada linha o número do item ou parágrafo a que pertence.

        Um item de lista que ocupa quatro linhas é uma unidade só: é lá que vive
        «4 dias a €81,89 ... total €427,58», com o total três linhas abaixo da
        parcela.
        """
        ids, atual = [], 0
        for ln in linhas:
            if not ln.strip() or RE_ITEM.match(ln):
                atual += 1
            ids.append(atual)
        return ids

    def recolher(linhas: list[str]) -> tuple[dict[str, list[int]], dict[str, set[int]], set[int]]:
        achados: dict[str, list[int]] = defaultdict(list)
        onde: dict[str, set[int]] = defaultdict(set)
        fora = descartadas(linhas)
        ids = blocos_de(linhas)
        com_pista: set[int] = set()
        for i, ln in enumerate(linhas):
            if RE_DECOMPOSICAO.search(ln):
                com_pista.add(ids[i])
            if fora[i]:
                continue
            for m in RE_DINHEIRO.finditer(ln):
                achados[m.group(1)].append(i + 1)
                onde[m.group(1)].add(ids[i])
        return achados, onde, com_pista

    (a, onde_a, pista_a), (b, onde_b, pista_b) = recolher(md), recolher(html)
    comuns = set(a) & set(b)

    def e_parcela(v: str, onde: dict[str, set[int]], pista: set[int]) -> bool:
        """Um valor que partilha um item com um total que os dois ficheiros já
        têm é uma parcela desse total, não um preço órfão. É o caso da diária do
        carro ao lado do total, e das duas metades da tarifa do aeroporto."""
        for bloco in onde[v]:
            if bloco not in pista:
                continue
            if any(bloco in onde[outro] for outro in comuns):
                return True
        return False

    #  Valores de um só dígito são preços de gelado, portagens e bilhetes de
    #  elétrico espalhados pelo texto, e não vale a pena exigir simetria neles.
    def relevante(v: str) -> bool:
        return len(v.replace(".", "").replace(",", "")) >= 3

    so_md = sorted(v for v in a if v not in b and relevante(v)
                   and not e_parcela(v, onde_a, pista_a))
    so_html = sorted(v for v in b if v not in a and relevante(v)
                     and not e_parcela(v, onde_b, pista_b))

    for v in so_md:
        s.aviso(f"itinerario_viagem.md:{a[v][0]}", f"€{v} não aparece em index.html.")
    for v in so_html:
        s.aviso(f"index.html:{b[v][0]}", f"€{v} não aparece em itinerario_viagem.md.")
    if not so_md and not so_html:
        s.info("ambos", f"{len(set(a) & set(b))} valores em comum, nenhum órfão.")

    return s


def check_pessoas(md: list[str], html: list[str]) -> Seccao:
    """O grupo é de 4 em Viena e de 6 a partir do Dia 3 à noite. Nunca 7.

    Há subgrupos legítimos por todo o lado, como «2 amigos juntam-se em
    Augsburg» ou «máximo 5 pessoas por bilhete», por isso não se exige que cada
    número seja 4 ou 6. O que tem de bater certo é a *soma* dos bilhetes
    repartidos: é aí que o antigo plano de 7 pessoas continua escondido.
    """
    s = Seccao("pessoas", "Quantas pessoas em cada bilhete")
    padrao = re.compile(r"(\d+)\s*(?:pax|pessoas|amigos|adultos|viajantes)\b", re.IGNORECASE)
    #  «7 Viajantes» designa sempre o grupo inteiro. Foi assim que o cartão de
    #  destaque da página continuou a anunciar sete viajantes muito depois de
    #  serem seis. «Amigos» fica de fora de propósito: «os 2 amigos que se juntam
    #  em Augsburg» é uma frase legítima e frequente.
    re_grupo = re.compile(r"(\d+)\s*(viajantes)\b", re.IGNORECASE)
    re_pax = re.compile(r"(\d+)\s*pax\b", re.IGNORECASE)
    contagem: dict[int, int] = defaultdict(int)

    for nome, linhas in (("itinerario_viagem.md", md), ("index.html", html)):
        for i, ln in enumerate(linhas):
            for m in padrao.finditer(ln):
                contagem[int(m.group(1))] += 1

            for m in re_grupo.finditer(ln):
                n = int(m.group(1))
                if n not in (PAX_VIENA, PAX_TOTAL):
                    s.erro(f"{nome}:{i + 1}",
                           f"«{m.group(0)}»: o grupo é de {PAX_VIENA} ou {PAX_TOTAL}.")

            for m in padrao.finditer(ln):
                n = int(m.group(1))
                if n > PAX_TOTAL and not re_grupo.match(m.group(0)):
                    s.aviso(f"{nome}:{i + 1}",
                            f"menção a {n} pessoas; confirmar que é histórico ou lotação, não o grupo.")

            #  Bilhete repartido: dois ou mais «N pax» somados têm de dar o grupo
            #  inteiro. O «+» tem de estar *entre* eles, porque um «+» noutro sítio da
            #  linha não faz dela uma soma.
            pax = list(re_pax.finditer(ln))
            if len(pax) >= 2 and "+" in ln[pax[0].end():pax[-1].start()]:
                valores = [int(m.group(1)) for m in pax]
                total = sum(valores)
                if total not in (PAX_VIENA, PAX_TOTAL):
                    s.erro(f"{nome}:{i + 1}",
                           f"bilhete repartido {' + '.join(map(str, valores))} = {total} pessoas; "
                           f"deviam ser {PAX_VIENA} ou {PAX_TOTAL}.")

    for n in sorted(contagem):
        rotulo = " (o grupo)" if n in (PAX_VIENA, PAX_TOTAL) else ""
        quantas = "menção" if contagem[n] == 1 else "menções"
        plural = "pessoa" if n == 1 else "pessoas"
        s.info("ambos", f"{contagem[n]} {quantas} a {n} {plural}{rotulo}.")

    return s


def check_prazos(md: list[str], hoje: date) -> Seccao:
    """Prazos por tratar que já passaram, ou que passam nos próximos dias."""
    s = Seccao("prazos", "Prazos à data de hoje")
    meses = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
             "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
    padrao = re.compile(r"\b(\d{1,2})\s+de\s+(" + "|".join(meses) + r")\b", re.IGNORECASE)

    #  Onde vivem os prazos: a tabela do topo, o hub de bilhetes, e a checklist
    #  final, que também tem datas por cumprir e que ficava de fora.
    seccoes_com_prazos = ("Prazos Críticos", "Hub de Bilhetes", "Confirmar Antes de Fechar")
    #  Uma data dentro de um aviso sobre uma opção descartada não é um prazo do
    #  grupo: é a data de uma coisa que se decidiu não fazer. A marca costuma
    #  estar na primeira linha da citação, daí reaproveitar o mesmo arrasto que
    #  os preços já usavam.
    fora = descartadas(md)
    dentro_do_hub = False
    tratada = False
    for i, ln in enumerate(md):
        if ln.startswith("## "):
            dentro_do_hub = any(x in ln for x in seccoes_com_prazos)
        if not dentro_do_hub or fora[i]:
            continue
        #  Um prazo riscado ou marcado como comprado já não é um prazo. O estado
        #  arrasta-se pelas linhas de continuação do mesmo item, porque a marca
        #  fica na primeira linha e a data costuma estar duas linhas abaixo,
        #  onde já não há «~~» nenhum para a proteger.
        if RE_ITEM.match(ln):
            tratada = False
        elif not ln.strip():
            tratada = False
        if "~~" in ln or "✅" in ln or "COMPRADO" in ln.upper():
            tratada = True
        if tratada:
            continue
        for m in padrao.finditer(ln):
            dia_n, mes_nome = int(m.group(1)), m.group(2).lower()
            try:
                quando = date(ANO, meses[mes_nome], dia_n)
            except ValueError:
                #  «31 de abril» é uma gralha no documento, e não vale a pena abortar por isso.
                s.aviso(f"itinerario_viagem.md:{i + 1}", f"«{m.group(0)}» não é uma data que exista.")
                continue
            #  Datas dentro da própria viagem são o programa, não prazos.
            if date(ANO, MES, 23) <= quando <= date(ANO, MES, 29):
                continue
            faltam = (quando - hoje).days
            if faltam < 0:
                s.erro(f"itinerario_viagem.md:{i + 1}",
                       f"«{m.group(0)}» passou há {-faltam} dias e a linha não está marcada como tratada.")
            elif faltam <= 14:
                s.aviso(f"itinerario_viagem.md:{i + 1}", f"«{m.group(0)}» é daqui a {faltam} dias.")

    #  Expressões relativas ao presente apodrecem sozinhas, e ninguém volta lá.
    #  Este dossiê chegou a ter «daqui a duas semanas» a apontar para o dia
    #  seguinte. Percorre o documento inteiro, e não só o hub, porque a pior de
    #  todas estava no cabeçalho.
    ate_a_viagem = (date(ANO, MES, 23) - hoje).days
    for i, ln in enumerate(md):
        for m in RE_RELATIVA.finditer(ln):
            s.aviso(f"itinerario_viagem.md:{i + 1}",
                    f"«{m.group(0).strip()}» é uma contagem relativa e envelhece sozinha; "
                    f"hoje faltam {ate_a_viagem} dias para a viagem.")

    if not s.achados:
        s.info("itinerario_viagem.md", "nenhum prazo em aberto vencido, nem a expirar nos próximos 14 dias.")
    return s


def check_imagens(html: list[str]) -> Seccao:
    """Uma imagem em falta só se vê ao abrir a página, e ninguém abre as sete."""
    s = Seccao("imagens", "Imagens referidas que existem em disco")
    #  Dois sítios referem imagens, e durante muito tempo isto só via um. Os
    #  marcadores do mapa trazem-nas em `img:` dentro do array de localizações,
    #  e uma imagem apagada deixava lá a referência partida sem ninguém dar por
    #  isso: o popup só rebenta quando alguém carrega no pin certo.
    #  A terceira é a mais fácil de esquecer: o fundo do cabeçalho vem de uma
    #  regra CSS, `url('img/...')`, e não de um `<img>`. Não tem `src`, não tem
    #  `alt`, e escapa a qualquer procura pelas outras duas. Reapareceu quando as
    #  fotografias passaram de .jpg a .webp e só esta ficou por mudar.
    #  Os contextos contam-se em separado de propósito. A mesma fotografia
    #  no banner de um dia e no popup do pin desse mesmo sítio não é repetição,
    #  é o mesmo lugar visto em dois sítios da página. Repetição a sério é a
    #  mesma fotografia em dois pontos *diferentes*.
    contextos = {"na página": re.compile(r'src="(img/[^"]+)"'),
                 "em pins do mapa": re.compile(r'img:\s*"(img/[^"]+)"'),
                 "em CSS": re.compile(r"url\(['\"]?(img/[^'\")]+)")}
    vistas: set[str] = set()
    usos: dict[str, dict[str, int]] = {k: defaultdict(int) for k in contextos}
    for i, ln in enumerate(html):
        for nome, padrao in contextos.items():
            for m in padrao.finditer(ln):
                rel = m.group(1)
                vistas.add(rel)
                usos[nome][rel] += 1
                if not (RAIZ / rel).exists():
                    s.erro(f"index.html:{i + 1}", f"{rel} não existe em disco.")
    em_disco = {f"img/{p.name}" for p in (RAIZ / "img").glob("*") if p.is_file()}
    for orfa in sorted(em_disco - vistas):
        s.aviso("img/", f"{orfa} está no repositório mas não é usada.")
    #  Dois pontos diferentes com a mesma fotografia querem dizer que um deles
    #  mostra outra coisa. Foi assim que o popup do restaurante e o do clube
    #  noturno acabaram ambos com a fotografia do canal do Danúbio, e que a
    #  Fuggerei ficou a mostrar a praça da câmara de Augsburg.
    for nome in contextos:
        for rel, n in sorted(usos[nome].items()):
            if n > 1:
                s.aviso("index.html",
                        f"{rel} aparece {n} vezes {nome}; são sítios diferentes a mostrar a mesma foto?")
    if vistas:
        s.info("index.html", f"{len(vistas)} imagens: "
                             f"{len(usos['na página'])} na página, "
                             f"{len(usos['em pins do mapa'])} em pins, "
                             f"{len(usos['em CSS'])} em CSS.")
    return s


def check_mapa(html: list[str]) -> Seccao:
    """Coordenadas dentro da caixa da viagem e iconType que o mapa saiba desenhar."""
    s = Seccao("mapa", "Marcadores do mapa")
    padrao = re.compile(r'iconType:\s*"(?P<tipo>\w+)".*?coords:\s*\[\s*(?P<lat>-?[\d.]+)\s*,\s*(?P<lon>-?[\d.]+)\s*\]')
    lat_min, lat_max, lon_min, lon_max = BBOX
    total = 0
    for i, ln in enumerate(html):
        m = padrao.search(ln)
        if not m:
            continue
        total += 1
        tipo, lat, lon = m.group("tipo"), float(m.group("lat")), float(m.group("lon"))
        if tipo not in ICON_TYPES:
            s.aviso(f"index.html:{i + 1}",
                    f"iconType «{tipo}» não está em getMarkerMeta; o pin cai no azul genérico.")
        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            s.erro(f"index.html:{i + 1}", f"coordenada [{lat}, {lon}] fora da área da viagem.")
    s.info("index.html", f"{total} marcadores.")
    return s


def check_armazenamento(html: list[str]) -> Seccao:
    """As chaves de localStorage são `vm_*_2026`. Mudá-las apaga o estado dos utilizadores."""
    s = Seccao("armazenamento", "Chaves de localStorage")
    padrao = re.compile(r"localStorage\.(?:get|set|remove)Item\(\s*['\"]([^'\"]+)['\"]")
    chaves: set[str] = set()
    for i, ln in enumerate(html):
        for m in padrao.finditer(ln):
            chave = m.group(1)
            chaves.add(chave)
            if not re.fullmatch(r"vm_[a-z_]+_2026", chave):
                s.erro(f"index.html:{i + 1}", f"chave «{chave}» foge ao padrão vm_<nome>_2026.")
    for c in sorted(chaves):
        s.info("index.html", f"chave {c}")
    return s


def check_marcadores(md: list[str]) -> Seccao:
    """Contagem dos marcadores de confiança. Um ⚠️ não se promove a ✅ em silêncio."""
    s = Seccao("marcadores", "Estado de confirmação dos factos")
    texto = "\n".join(md)
    for simbolo, nome in (("✅", "confirmado"), ("⚠️", "estimativa"), ("🔴", "por tratar")):
        s.info("itinerario_viagem.md", f"{texto.count(simbolo)} × {simbolo} ({nome})")
    return s


def check_linguagem(md: list[str], html: list[str]) -> Seccao:
    """A regra 6 proíbe o travessão como pontuação. Ele reaparece sempre que
    alguém cola texto de outro sítio, e ninguém dá por isso a ler. Aqui dá.

    O meio travessão (–) fica de fora de propósito: é o que separa os
    intervalos de horas, e esse é para manter."""
    s = Seccao("linguagem", "Travessões, que a regra 6 não permite")
    for ficheiro, linhas in (("itinerario_viagem.md", md), ("index.html", html)):
        encontrados = [(i + 1, ln) for i, ln in enumerate(linhas) if "—" in ln]
        for numero, ln in encontrados[:10]:
            trecho = ln.strip()
            recorte = trecho[:70] + ("…" if len(trecho) > 70 else "")
            s.erro(f"{ficheiro}:{numero}", f"travessão em «{recorte}»")
        if len(encontrados) > 10:
            s.erro(ficheiro, f"e mais {len(encontrados) - 10} linhas com travessão.")
        if not encontrados:
            s.info(ficheiro, "sem travessões.")
    return s


def check_meteo(meteo: list[str], html: list[str]) -> Seccao:
    """O guia e o relatório saem do mesmo comando, e cada dia diz de que fonte vem.

    Não compara número a número: isso obrigaria o verificador a conhecer as
    paragens do roteiro, e ele não sabe nada do mundo. Compara o que denuncia uma
    meia-atualização, que é a data de geração, e o que faz cumprir a regra de
    nunca dar climatologia como previsão, que é o rótulo em cada dia.
    """
    s = Seccao("meteo", "A previsão do guia e a do relatório")
    texto_html = "\n".join(html)

    if WEATHER_START not in texto_html or WEATHER_END not in texto_html:
        s.erro("index.html", "faltam os marcadores WEATHER-AUTO: o guia perdeu a previsão.")
        return s

    bloco = texto_html.split(WEATHER_START, 1)[1].split(WEATHER_END, 1)[0]
    dias = bloco.count('class="weather-day-card"')
    rotulos = bloco.count('class="weather-src')
    if dias == 0:
        s.erro("index.html", "o bloco da previsão está vazio; correr `python meteo.py --html index.html`.")
    elif rotulos != dias:
        s.erro("index.html",
               f"{dias} dias mas {rotulos} rótulos de fonte: há um dia sem dizer de onde vem o número.")
    else:
        s.info("index.html", f"{dias} dias, todos com a fonte rotulada.")

    #  A data de geração tem de ser a mesma nos dois: se não for, alguém voltou a
    #  correr o meteo.py só para metade dos destinos, e o guia mostra números que
    #  já não são os do relatório.
    m_md = re.search(r"Actualizado a (.+?) · fonte: Open-Meteo", "\n".join(meteo))
    m_html = re.search(r"WEATHER-AUTO:START -->\s*<!-- Gerado por python meteo\.py "
                       r"--html index\.html a (.+?)\.", texto_html)
    if m_md and m_html and m_md.group(1) != m_html.group(1):
        s.aviso("meteo.md / index.html",
                f"gerados em datas diferentes ({m_md.group(1)} e {m_html.group(1)}): "
                "voltar a correr `python meteo.py --md meteo.md --html index.html`.")
    elif m_md and m_html:
        s.info("ambos", f"previsão de {m_md.group(1)}, nos dois ficheiros.")
    elif m_md and not m_html:
        #  Se a data deixar de ser legível, esta secção deixaria de comparar seja o
        #  que for sem avisar. Um rótulo que muda de forma tem de ser dito.
        s.aviso("index.html",
                "o bloco da previsão não traz a data de geração legível; não dá para "
                "confirmar que saiu da mesma passagem do meteo.md.")
    return s


# ---------------------------------------------------------------------- saída

SECCOES = ["dias", "horarios", "precos", "pessoas", "prazos", "imagens", "mapa",
           "armazenamento", "marcadores", "linguagem", "meteo"]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    p = argparse.ArgumentParser(description="Verifica a coerência do dossiê de viagem.")
    p.add_argument("--dia", type=int, metavar="N", help="limitar a verificação de horários a um dia")
    p.add_argument("--seccao", nargs="+", metavar="NOME", choices=SECCOES, help="correr só estas secções")
    p.add_argument("--so-erros", action="store_true", help="esconder avisos e informação")
    p.add_argument("--listar", action="store_true", help="listar as secções disponíveis e sair")
    p.add_argument("--hoje", metavar="AAAA-MM-DD", help="simular outra data de hoje (para testar prazos)")
    args = p.parse_args()

    if args.listar:
        for nome in SECCOES:
            print(nome)
        return 0

    hoje = date.fromisoformat(args.hoje) if args.hoje else date.today()
    md, html = ler(MD), ler(HTML)
    meteo = ler(METEO) if METEO.exists() else []

    todas = [
        check_dias(md, html),
        check_horarios(md, args.dia),
        check_precos(md, html),
        check_pessoas(md, html),
        check_prazos(md, hoje),
        check_imagens(html),
        check_mapa(html),
        check_armazenamento(html),
        check_marcadores(md),
        check_linguagem(md, html),
        check_meteo(meteo, html),
    ]
    if args.seccao:
        todas = [s for s in todas if s.nome in args.seccao]

    print(f"Dossiê Viena + Munique 2026, verificação de {hoje:%d/%m/%Y}")
    print("=" * 78)

    n_erros = n_avisos = 0
    for s in todas:
        achados = sorted(s.achados, key=lambda a: (PESO[a.nivel], a.onde))
        if args.so_erros:
            achados = [a for a in achados if a.nivel == ERRO]
        n_erros += sum(1 for a in s.achados if a.nivel == ERRO)
        n_avisos += sum(1 for a in s.achados if a.nivel == AVISO)
        if not achados and args.so_erros:
            continue
        print(f"\n▸ {s.titulo}")
        if not achados:
            print("  nada a assinalar.")
        for a in achados:
            print(f"  {SIMBOLO[a.nivel]} {a.onde}: {a.texto}")

    print("\n" + "=" * 78)
    def plural(n: int, singular: str, muitos: str) -> str:
        return f"{n} {singular if n == 1 else muitos}"

    if n_erros:
        print(f"{plural(n_erros, 'erro', 'erros')} e {plural(n_avisos, 'aviso', 'avisos')}. "
              f"{'O erro tem' if n_erros == 1 else 'Os erros têm'} de ser resolvido"
              f"{'' if n_erros == 1 else 's'}.")
    elif n_avisos:
        print(f"Sem erros. {plural(n_avisos, 'aviso', 'avisos')} para confirmar à mão.")
    else:
        print("Sem erros nem avisos.")
    return 1 if n_erros else 0


if __name__ == "__main__":
    sys.exit(main())
