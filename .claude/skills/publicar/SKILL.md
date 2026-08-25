---
name: publicar
description: Fecha uma alteração ao dossiê, com verificação, commit no estilo do repositório e publicação no GitHub Pages. Usar quando se pede para guardar, fazer commit, publicar ou pôr no ar as alterações.
allowed-tools: Bash(python verificar.py *), Bash(git status *), Bash(git diff *), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(git log *), Read
---

# Fechar e publicar

O guia está no ar em <https://fontao.github.io/viena-munique-2026/>, servido a
partir do `main` de `github.com/fontao/viena-munique-2026`. Um push publica.

## Antes de tocar no git

1. `python verificar.py`, **sem 🔴**. Um erro de coerência publicado é um erro que
   alguém vai ler no telemóvel à porta de um castelo.
2. `git status --short` e `git diff`, para ler o que vai no commit. Confirmar que
   não vai nada a mais: o `.omc/`, o `.roundtable/` e o `.playwright-mcp/` estão no
   `.gitignore`, mas ficheiros temporários novos não estão.
3. O `meteo.md` é um ficheiro gerado. Se aparece alterado, foi porque o
   regeneraram, e se foi regenerado hoje pode ir.

## A mensagem de commit

Frase declarativa em **inglês**, no presente, a dizer o que mudou **no plano** e
não no ficheiro. É a única parte do repositório que não é em português.

```
Six travellers, not seven, and lock the car booking times
Fix the last train, the Neuschwanstein margin and six stale prices
Optimise the Vienna route and fix an impossible Day 2 timing
Confirm the airport transfer choice and add the practical detail
```

Não: `feat: add weather script`, `update itinerary`, `fix typo`, `wip`. Existe um
commit `feat:` no histórico. É a exceção, não o padrão.

Se a alteração for grande, o corpo do commit lista as decisões, uma por linha. Nada
de listas de ficheiros, porque isso o `git` já sabe.

## Publicar

Confirmar com o utilizador antes do `push`, porque publicar é uma ação para fora e
o site é lido pelos seis viajantes. Depois:

```bash
git add <ficheiros>       # explicitamente, nunca `git add -A`
git commit -m "..."
git push
```

O GitHub Pages leva um minuto ou dois. Confirmar que a página no ar já tem a
alteração antes de a dar por publicada:

```bash
curl -s "https://fontao.github.io/viena-munique-2026/" | grep -c "<termo que mudou>"
```

## Regras

- **Nunca `git push --force`** neste repositório. O histórico é o registo de como o
  plano evoluiu, e as mensagens de commit são a única memória da razão por que cada
  decisão foi tomada.
- Um commit por decisão editorial, e não um commit gigante ao fim do dia.
- Se o `verificar.py` der 🔴 e o utilizador quiser publicar na mesma, publica-se,
  dizendo numa frase o que fica por resolver e registando-o no commit.
