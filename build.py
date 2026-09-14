"""
Build index.html from partials.

Concatenates all HTML partials in order into the final index.html.
Run before committing or after editing any partial.

Guardrail: detects if index.html was edited directly (i.e. differs
from what the partials produce) and prints a warning.
"""

import os
import re
import sys

PARTIALS_DIR = "partials"
OUTPUT = "index.html"

ORDER = [
    "head.html",
    "header.html",
    "hero.html",
    "map.html",
    "itinerary.html",
    "tickets.html",
    "oktoberfest.html",
    "weather.html",
    "dossier.html",
    "footer.html",
]

# The generated-file warning banner that build.py prepends.
BANNER = (
    "<!-- ====================================================================\n"
    "     GENERATED FILE - DO NOT EDIT DIRECTLY.\n"
    "     This file is built from partials/ by build.py.\n"
    "     Edit partials/head.html, partials/itinerary.html, etc. then run:\n"
    "         python build.py\n"
    "     GitHub Actions rebuilds this on every push to main.\n"
    "     ==================================================================== -->\n"
)


def _strip_banner(text):
    """Remove the generated-file banner for comparison."""
    return re.sub(r"<!-- =+.*?=+ -->\s*", "", text, count=1, flags=re.DOTALL).lstrip(
        "\n"
    )


def build():
    parts = []
    for name in ORDER:
        path = os.path.join(PARTIALS_DIR, name)
        if not os.path.exists(path):
            print(f"ERROR: missing partial {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            parts.append(f.read())

    html = BANNER + "".join(parts)

    # Check if existing index.html was edited directly
    if os.path.exists(OUTPUT):
        with open(OUTPUT, "r", encoding="utf-8") as f:
            existing = f.read()

        existing_body = _strip_banner(existing)
        generated_body = _strip_banner(html)

        if existing_body != generated_body:
            # Check if index.html was modified AFTER partials were updated
            out_mtime = os.path.getmtime(OUTPUT)
            partials_mtime = max(
                os.path.getmtime(os.path.join(PARTIALS_DIR, p))
                for p in ORDER
                if os.path.exists(os.path.join(PARTIALS_DIR, p))
            )
            if out_mtime > partials_mtime:
                # Find first difference for diagnostics
                for i, (a, b) in enumerate(zip(existing_body, generated_body)):
                    if a != b:
                        line_num = existing_body[:i].count("\n") + 1
                        print(
                            f"WARNING: {OUTPUT} was edited directly (modified after partials; "
                            f"first diff at ~line {line_num}). "
                            f"Overwriting with partials build.",
                            file=sys.stderr,
                        )
                        break
                else:
                    print(
                        f"WARNING: {OUTPUT} was edited directly "
                        f"(length mismatch: {len(existing_body):,} vs "
                        f"{len(generated_body):,}). Overwriting with partials build.",
                        file=sys.stderr,
                    )

        changed = existing_body != generated_body
    else:
        changed = True

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    status = "updated" if changed else "unchanged"
    print(f"build.py: {OUTPUT} ({len(html):,} bytes, {status})")


if __name__ == "__main__":
    build()
