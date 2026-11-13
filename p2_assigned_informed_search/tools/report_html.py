"""HTML pieces of report.py: one page, one table, one figure. No number is computed here."""
from __future__ import annotations

from html import escape
from pathlib import Path

__all__ = ["page", "table", "figure"]

# Theme cells are nowrap and right aligned. Long text needs the wrap class (1040 px page).
PAGE_CSS = """
.wrap p, .wrap li { max-width: 100ch; }
td.text, th.text { white-space: normal; text-align: left; }
figure { margin: 0; display: flex; flex-direction: column; gap: 8px; }
figure img { max-width: 100%; height: auto; border: 1px solid var(--rule); }
.mockbar { background: var(--signal-flag-fill); box-shadow: inset 2px 0 0 var(--signal-flag-line); padding: 8px 12px; }
"""


def page(title: str, theme_css: str, body: str, is_mock: bool) -> str:
    banner = ('<p class="mockbar"><b>MOCK DATA.</b> Every value here is invented. '
              "No simulator ran.</p>") if is_mock else ""
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            f"<title>{escape(title)}</title>\n<style>{theme_css}\n{PAGE_CSS}</style></head>\n"
            f'<body><div class="wrap">\n<h1>{escape(title)}</h1>\n{banner}\n{body}\n'
            "</div></body></html>\n")


def table(header: list[str], rows: list[list[str]], caption: str, text_cols: tuple[int, ...] = (),
          raw_cols: tuple[int, ...] = ()) -> str:
    """Narrow table. text_cols wrap. raw_cols hold ready HTML (links), the rest is escaped."""
    def cell(tag: str, i: int, v: str) -> str:
        cls = ' class="text"' if i in text_cols else ""
        return f"<{tag}{cls}>{v if i in raw_cols and tag == 'td' else escape(v)}</{tag}>"
    head = "".join(cell("th", i, h) for i, h in enumerate(header))
    body = "\n".join("<tr>" + "".join(cell("td", i, v) for i, v in enumerate(r)) + "</tr>"
                     for r in rows)
    return (f'<div class="scroll-x"><table>\n<caption class="muted" style="text-align:left">'
            f"{escape(caption)}</caption>\n<tr>{head}</tr>\n{body}\n</table></div>")


def figure(src: Path | str, caption: str, alt: str) -> str:
    return (f'<figure><img src="{escape(str(src))}" alt="{escape(alt)}">'
            f'<figcaption class="muted">{escape(caption)}</figcaption></figure>')
