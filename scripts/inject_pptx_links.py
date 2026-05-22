#!/usr/bin/env python3
"""
Post-render hook for the Sherley Quarto site.

After `quarto render`, scan each rendered HTML page in docs/qmd/ for
<img src="..._files/figure-html/<chunk-label>-N.png"> figures, and inject
an editable-PowerPoint download link immediately below the image when a
matching pptx exists in docs/plots/carbo/.

Mapping rule (matches .save_plot_pptx in sherley_carbo.qmd):
  chunk_label = strip trailing "-<digits>.png" from the PNG basename
  pptx_slug   = chunk_label with [^A-Za-z0-9]+ collapsed to "_"
  pptx_file   = docs/plots/carbo/<pptx_slug>.pptx
"""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PPTX_DIR_ABS = ROOT / "docs" / "plots" / "carbo"
PPTX_DIR_REL = "../plots/carbo"

IMG_RE = re.compile(
    r'<img\s+src="([^"]*figure-html/[^"]+?\.png)"[^>]*?/?>',
    flags=re.IGNORECASE,
)
LINK_DIV_TMPL = (
    '\n<div class="pptx-link" '
    'style="margin:-0.5em 0 1.3em 0;font-size:0.85em;text-align:center;">'
    '<a href="{href}" download>📥 Download editable PowerPoint</a>'
    '</div>\n'
)


def slugify(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", label)


def inject(html: str) -> tuple[str, int]:
    n_added = 0

    def replace(m: re.Match[str]) -> str:
        nonlocal n_added
        img_tag = m.group(0)
        src = m.group(1)
        # Strip trailing "-<digits>.png" to recover the chunk label
        fname = os.path.basename(src)
        m2 = re.match(r"(.+?)-\d+\.png$", fname)
        if not m2:
            return img_tag
        chunk_label = m2.group(1)
        pptx_slug = slugify(chunk_label)
        pptx_file = PPTX_DIR_ABS / f"{pptx_slug}.pptx"
        if not pptx_file.exists():
            return img_tag
        href = f"{PPTX_DIR_REL}/{pptx_slug}.pptx"
        link = LINK_DIV_TMPL.format(href=href)
        n_added += 1
        return img_tag + link

    new_html = IMG_RE.sub(replace, html)
    return new_html, n_added


def main() -> None:
    pages = list((ROOT / "docs" / "qmd").glob("sherley_*.html"))
    if not pages:
        print("[inject_pptx_links] no docs/qmd/sherley_*.html pages found — skipping.")
        return
    for page in pages:
        text = page.read_text(encoding="utf-8")
        new_text, n = inject(text)
        if n > 0:
            page.write_text(new_text, encoding="utf-8")
        print(f"[inject_pptx_links] {page.relative_to(ROOT)}: +{n} pptx link(s)")


if __name__ == "__main__":
    main()
