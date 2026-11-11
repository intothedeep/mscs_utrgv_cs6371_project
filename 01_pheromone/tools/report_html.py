"""Pure HTML builders for the stage reports and the summary page (no file access).

Theme: a copy of .claude/skills/html-theme/theme.css sits in results/assets/ so the
pages work when opened from disk. The page rules below only add layout.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape

__all__ = ["Stage", "page", "table", "stage_page", "index_page"]

THEME_HREF = "../../assets/theme.css"  # pages live in results/<mock|real>/<phase>/
EXTRA_CSS = """
.field { width: 100%; }
.field th, .field td { white-space: normal; text-align: left; vertical-align: top; }
.field th { width: 190px; }
.step { border: 1px solid var(--border); border-top: 4px solid var(--foreground);
        padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.fig img { max-width: 100%; height: auto; border: 1px solid var(--rule); }
a { color: inherit; }
"""
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700"
         "&family=IBM+Plex+Sans+KR:wght@400;500&display=swap")


@dataclass(frozen=True)
class Stage:
    """One stage report. Fields follow .claude/CLAUDE.md 'System build phasing'."""
    key: str
    title: str
    what: str
    why: str
    inputs: str
    outputs: str
    result: str    # numbers read from saved outputs
    verdict: str   # one line: what was good or bad
    status: str    # ran, reused, skipped or failed, with the reason
    figure: str    # ready HTML (an <img>) or "" when skipped
    table: str     # ready HTML (a <table>) or "" when skipped


def page(title: str, body: str) -> str:
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            f"<title>{escape(title)}</title>\n"
            f'<link rel="stylesheet" href="{FONTS}">\n'
            f'<link rel="stylesheet" href="{THEME_HREF}">\n'
            f"<style>{EXTRA_CSS}</style></head>\n"
            f'<body><div class="wrap">\n{body}\n</div></body></html>\n')


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>"
                   for row in rows)
    return f'<div class="scroll-x"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def _is_skipped(status: str) -> bool:
    return status.startswith(("skipped", "failed"))


def stage_page(stage: Stage, step: int, total: int) -> str:
    rows = [("What", stage.what), ("Why", stage.why), ("Input data", stage.inputs),
            ("Output data", stage.outputs), ("Result (numbers)", stage.result),
            ("Result (good or bad)", stage.verdict), ("Status", stage.status)]
    cls = ' class="dead"' if _is_skipped(stage.status) else ""
    fields = "".join(f"<tr{cls if name == 'Status' else ''}><th>{name}</th>"
                     f"<td>{escape(value)}</td></tr>" for name, value in rows)
    body = (f'<p class="label">Stage report, step {step} of {total}. '
            f'<a href="index.html">Back to summary</a></p>\n'
            f"<h1>{escape(stage.title)}</h1>\n"
            f'<div class="panel"><table class="field">{fields}</table></div>\n'
            f'<div class="panel fig"><p class="label">Figure and table</p>'
            f'{stage.figure or "<p class=\"muted\">No figure: stage has no saved output.</p>"}'
            f'{stage.table}</div>')
    return page(stage.title, body)


def _pipeline_svg(stages: list[Stage]) -> str:
    """Boxes left to right: why a picture first, the flow is the point of MVP1."""
    w, gap = 250, 60
    parts = ['<svg viewBox="0 0 900 90" width="100%" role="img" aria-label="stage flow">',
             '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" '
             'orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>']
    for i, s in enumerate(stages):
        x = 15 + i * (w + gap)
        parts.append(f'<rect x="{x}" y="15" width="{w}" height="60" fill="var(--card)" '
                     f'stroke="var(--border)"/>')
        parts.append(f'<text x="{x + 12}" y="40" style="fill:var(--foreground);font-size:14px">'
                     f'{i + 1}. {escape(s.key)}</text>')
        state = "skipped" if _is_skipped(s.status) else "ran"
        parts.append(f'<text x="{x + 12}" y="60">status: {state}</text>')
        if i < len(stages) - 1:
            parts.append(f'<line x1="{x + w}" y1="45" x2="{x + w + gap - 4}" y2="45" '
                         f'stroke="currentColor" marker-end="url(#arr)"/>')
    parts.append("</svg>")
    return "".join(parts)


def index_page(title: str, intro: str, stages: list[Stage], extras: list[tuple[str, str]]) -> str:
    """Summary page. extras: (link text, href) for non-stage files such as the chart."""
    n = len(stages)
    nav = "".join(f'<li><a href="#step-{i}">Step {i} of {n}: {escape(s.title)}</a></li>'
                  for i, s in enumerate(stages, 1))
    boxes = "".join(
        f'<section class="step" id="step-{i}"><p class="label">Step {i} of {n}</p>'
        f'<h2><a href="{escape(s.key)}.html">{escape(s.title)}</a></h2>'
        f'<p{" class=\"dead\"" if _is_skipped(s.status) else ""}>Status: {escape(s.status)}</p>'
        f"<p>{escape(s.result)}</p><p class=\"muted\">{escape(s.verdict)}</p></section>"
        for i, s in enumerate(stages, 1))
    links = "".join(f'<li><a href="{escape(h)}">{escape(t)}</a></li>' for t, h in extras)
    body = (f"<h1>{escape(title)}</h1>\n<p>{escape(intro)}</p>\n{_pipeline_svg(stages)}\n"
            f"<ol>{nav}</ol>\n{boxes}\n<div class=\"panel\"><p class=\"label\">Other files</p>"
            f"<ul>{links}</ul></div>")
    return page(title, body)
