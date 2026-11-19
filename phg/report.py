"""Display helpers: evidence panels, verification records and figure output.

Verification tiers (shared with INVENTORY.md):
  RECOMPUTED  independently recalculated here from upstream inputs
  CHECKED     compared with a saved result (or two saved results compared)
  HASH-ONLY   source integrity only (SHA-256 of the pinned file)
"""
from __future__ import annotations

import html
import re
import json
import math
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

TIERS = ("RECOMPUTED", "CHECKED", "HASH-ONLY")
READER, REPRODUCTION = "READER", "REPRODUCTION"


def draft() -> bool:
    """DRAFT build flag (default on): outline slots render in a muted "Draft outline" box; off omits them."""
    return os.environ.get("PHG_DRAFT", "1").strip().lower() not in ("0", "false", "no", "off")


def mode() -> str:
    m = os.environ.get("PHG_MODE", READER).upper()
    if m not in (READER, REPRODUCTION):
        raise ValueError(f"PHG_MODE must be READER or REPRODUCTION, got {m}")
    return m


# ------------------------------------------------------------ verification
@dataclass
class Check:
    id: str
    tier: str
    description: str
    expected: Any
    observed: Any
    tol: float = 1e-9
    status: str = ""
    note: str = ""
    section: str = ""

    def __post_init__(self):
        if self.tier not in TIERS:
            raise ValueError(self.tier)
        if not self.status:
            self.status = evaluate(self.expected, self.observed, self.tol)


def evaluate(expected, observed, tol) -> str:
    if observed is None:
        return "SKIPPED"
    if isinstance(expected, bool) or isinstance(observed, bool):
        return "PASS" if expected == observed else "FAIL"
    try:
        e, o = float(expected), float(observed)
        if math.isnan(e) and math.isnan(o):
            return "PASS"
        return "PASS" if abs(e - o) <= tol else "FAIL"
    except (TypeError, ValueError):
        return "PASS" if expected == observed else "FAIL"


class Ledger:
    """Collects checks across the notebook; exported at the end."""

    def __init__(self):
        self.checks: list[Check] = []

    def add(self, *args, section: str = "", **kw) -> Check:
        c = Check(*args, section=section, **kw)
        self.checks.append(c)
        return c

    def section(self, name: str) -> list[Check]:
        return [c for c in self.checks if c.section == name]

    def to_json(self) -> str:
        def clean(v):
            if isinstance(v, float) and not math.isfinite(v):
                return str(v)
            return v
        return json.dumps([{k: clean(v) for k, v in asdict(c).items()} for c in self.checks], indent=1, default=str)

    def summary(self) -> dict:
        out: dict = {}
        for c in self.checks:
            out.setdefault(c.tier, {}).setdefault(c.status, 0)
            out[c.tier][c.status] += 1
        return out


def fmt(v) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return f"{v:+.6f}" if abs(v) < 1e4 else f"{v:.6g}"
    return html.escape(str(v))


def verification_html(checks: list[Check], title: str) -> str:
    rows = []
    for tier in TIERS:
        for c in [c for c in checks if c.tier == tier]:
            rows.append(
                f"<tr class='st-{c.status.lower()}'><td><span class='tier tier-{tier.lower().replace('-', '')}'>{tier}</span></td>"
                f"<td>{html.escape(c.id)}</td><td>{html.escape(c.description)}</td>"
                f"<td>{fmt(c.expected)}</td><td>{fmt(c.observed)}</td><td>{c.tol:g}</td>"
                f"<td><b>{c.status}</b>{(' · ' + html.escape(c.note)) if c.note else ''}</td></tr>")
    counts = {}
    for c in checks:
        counts[c.status] = counts.get(c.status, 0) + 1
    tally = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
    return (f"<div class='phg-verify'><div class='phg-verify-title'>{html.escape(title)} <span class='tally'>({tally})</span></div>"
            "<div class='tablewrap'><table><thead><tr><th>Tier</th><th>Check</th><th>Description</th>"
            "<th>Expected</th><th>Observed</th><th>Tol</th><th>Status</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table></div></div>")


# ------------------------------------------------------------ evidence panel
def evidence_panel(key: str, prose_map: Optional[dict] = None) -> str:
    """Evidence panel with only the filled slots from prose.md; empty string if none."""
    from . import prose
    p = prose.load() if prose_map is None else prose_map
    slots = [("What it shows", prose.get(key, "shows", p)), ("Principal limitation", prose.get(key, "limitation", p))]
    filled = [(label, text) for label, text in slots if text]
    if not filled:
        return ""
    body = "".join(f"<div class='ev-slot'><div class='ev-label'>{label}</div><div class='ev-text'>{html.escape(text)}</div></div>"
                   for label, text in filled)
    return f"<div class='phg-evidence' data-key='{html.escape(key)}'>{body}</div>"


def lead_html(key: str, prose_map: Optional[dict] = None) -> str:
    from . import prose
    t = prose.get(key, "lead", prose_map)
    return f"<p class='phg-lead'>{html.escape(t)}</p>" if t else ""


def _inline(t: str) -> str:
    """Escape, then allow **bold** and [text](https://link) inside body text (iteration 49)."""
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|#[\w.-]+)\)", r"<a href='\2'>\1</a>", t)  # iteration 54: in-page anchors


def body_html(key: str, prose_map: Optional[dict] = None) -> str:
    """Body slot as running text (iteration 39; lists and subheadings since iteration 49). Blocks are separated by a blank
    line in prose.md. A block whose lines start with "- " is a bulleted list (indented lines continue an item); a block
    that is a single line "#### Heading" is a subheading; any other block is a paragraph. **bold** and [text](url) work
    inline."""
    from . import prose
    t = prose.get(key, "body", prose_map)
    out = []
    for block in [b for b in re.split(r"\n\s*\n", t) if b.strip()]:
        lines = block.strip().splitlines()
        if lines[0].startswith("- "):
            items, cur = [], None
            for ln in lines:
                if ln.startswith("- "):
                    if cur is not None:
                        items.append(cur)
                    cur = ln[2:].strip()
                else:
                    cur = (cur or "") + " " + ln.strip()
            items.append(cur)
            out.append("<ul class='phg-list'>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
        elif len(lines) == 1 and lines[0].startswith("#### "):
            out.append(f"<p class='phg-subhead'>{_inline(lines[0][5:].strip())}</p>")
        else:
            out.append(f"<p class='phg-body'>{_inline(' '.join(block.split()))}</p>")
    return "".join(out)


def caption_html(key: str, prose_map: Optional[dict] = None) -> str:
    from . import prose
    t = prose.get(key, "how_to_read", prose_map)
    return f"<p class='phg-caption'>{html.escape(t)}</p>" if t else ""


def outline_html(key: str, prose_map: Optional[dict] = None) -> str:
    """Outline slot as a "Draft outline" box (DRAFT on) or nothing (DRAFT off / empty slot)."""
    from . import prose
    if not draft():
        return ""
    text = prose.get(key, "outline", prose_map)
    if not text:
        return ""
    items, cur = [], None
    for line in text.splitlines():
        if line.startswith("- "):
            if cur is not None:
                items.append(cur)
            cur = line[2:].strip()
        elif cur is not None:
            cur += " " + line.strip()
    if cur is not None:
        items.append(cur)
    body = "".join(f"<li>{html.escape(i)}</li>" for i in items)
    return f"<div class='phg-outline' data-key='{html.escape(key)}'><div class='ol-label'>Draft outline</div><ul>{body}</ul></div>"


def source_tag(*parts: str) -> str:
    return "<p class='phg-source'>" + " · ".join(html.escape(p) for p in parts) + "</p>"


def details(summary: str, inner: str, cls: str = "supporting") -> str:
    return f"<details class='phg-details {cls}'><summary>{html.escape(summary)}</summary>{inner}</details>"


def tag(text: str) -> str:
    return f"<div class='phg-tag'>{html.escape(text)}</div>"


def audit_line(L: "Ledger", section) -> str:
    """section: one ledger section key, or a tuple of keys (Section 4 holds the former Sections 3 and 4)."""
    cs = [c for sec in ((section,) if isinstance(section, str) else section) for c in L.section(sec)]
    n = sum(c.status == "PASS" for c in cs)
    extra = []
    for st, word in [("NOTE", "note"), ("FAIL", "failed"), ("SKIPPED", "skipped")]:
        k = sum(c.status == st for c in cs)
        if k:
            extra.append(f"{k} {word}{'s' if st == 'NOTE' and k > 1 else ''}")
    tail = (", " + ", ".join(extra)) if extra else ""
    return (f"<p class='phg-auditline'>Numerical checks for this section: see "
            f"<a href='#appendix-d-numerical-audit'>Appendix D</a> ({n} passed{tail}).</p>")


# Iteration 33: reader-facing numbers after the restructure. Internal keys (element ids, checks, inventory, prose) are
# unchanged; only the label a reader sees follows this map. Keys not listed keep their own number.
DISPLAY_NUMBER = {
    "tmap": "1.2", "1.2": "1.3",                    # Iteration 47: trait map is 1.2; the explorer moves to 1.3
    "1.3": "3.1",                                   # Iteration 46: one Big Five matrix (people and models); former 3.2 (sapa1) merged in
    "elbow": "G.3a",
    "G.1": "2.1", "2.1": "2.2", "2.2": "G.2",       # Iteration 53: trait-pair comparison opens Section 2; per-trait agreement to G.2                                # Iteration 48: variance per axis moves to Appendix G (Section 2 back to 2.1-2.3)
    "H": "4.1", "4.2": "4.2",                        # Section 4 (iteration 36): trait pairs, then the matrix outlining them
    "4.3": "E.6", "6.1": "5.1",                      # prediction to Appendix E; GPT comparison opens the Discussion
    "3.2": "E.5",                                    # facet geometry in Qwen's own axes, Appendix E since iteration 35
    "5a": "H.1", "5b": "H.2", "5c": "H.3", "5d.2": "H.4", "5d.3": "H.5", "5e.1": "H.6", "5e.3": "H.7",  # Appendix H
}


def fig_number(fig_id: str) -> str:
    """Reader-facing figure number (DISPLAY_NUMBER)."""
    return DISPLAY_NUMBER.get(fig_id, fig_id)


def fig_label_html(fig_id: str, title: str = "") -> str:
    """Bold "Figure N." with the short descriptive title on the same line, directly above the figure. The title is fixed:
    it never changes with a dropdown (iteration 9)."""
    t = f" <span class='fig-title'>{html.escape(title)}</span>" if title else ""
    return f"<div class='fig-id' id='label-{html.escape(fig_id)}'><b>Figure {html.escape(fig_number(fig_id))}.</b>{t}</div>"


def figure_html(fig, fig_id: str, height: Optional[int] = None, post_script: str = "") -> str:
    """Plotly figure as an HTML fragment that relies on the page-level plotly.js."""
    cfg = dict(responsive=True, displaylogo=False, modeBarButtonsToRemove=["lasso2d", "select2d"])
    if height:
        fig.update_layout(height=height)
    div = fig.to_html(full_html=False, include_plotlyjs=False, div_id=f"fig-{fig_id}", config=cfg)
    title = fig.layout.meta if isinstance(fig.layout.meta, str) else ""
    return (f"<div class='phg-figure' id='wrap-{fig_id}'>{fig_label_html(fig_id, title)}{div}"
            f"{post_script}</div>")


def table_html(df, caption: str = "", float_fmt: str = "{:+.3f}", max_rows: int = 400, cls: str = "") -> str:
    def cell(v):
        if isinstance(v, float):
            return "" if math.isnan(v) else float_fmt.format(v)
        return html.escape(str(v))
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    body = "".join("<tr>" + "".join(f"<td>{cell(v)}</td>" for v in row) + "</tr>"
                   for row in df.head(max_rows).itertuples(index=False))
    cap = f"<caption>{html.escape(caption)}</caption>" if caption else ""
    return f"<div class='tablewrap {cls}'><table class='phg-table'>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


# Plotly cannot size a figure inside a closed <details>; resize when it opens.
DETAILS_SCRIPT = """<script>document.addEventListener('toggle',function(e){var d=e.target;
if(d&&d.tagName==='DETAILS'&&d.open&&window.Plotly){d.querySelectorAll('.js-plotly-plot').forEach(function(g){Plotly.Plots.resize(g);});}},true);</script>"""

STYLE = """
<style>
.phg-evidence{border:1px solid #c9ced6;border-left:4px solid #5b6b82;border-radius:6px;padding:8px 12px;margin:8px 0 22px;background:#f7f8fa;font-size:14px}\n.phg-lead{font-size:inherit;font-weight:400;max-width:76ch;margin:8px 0}\n.phg-caption{font-size:14px;color:#3b475a;margin:4px 0 10px;max-width:76ch}\n.phg-tag{display:inline-block;font-size:12px;font-weight:600;color:#3b475a;background:#eef1f5;border-radius:10px;padding:1px 9px;margin:2px 0 6px}\n.phg-auditline{font-size:12px;color:#7a8698;margin:14px 0 4px}\n.phg-outline{border:1px dashed #b8c0cc;background:#f7f8fa;color:#5b6b82;border-radius:6px;padding:6px 12px;margin:8px 0 14px;font-size:14px}\n.phg-outline .ol-label{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#7a8698}\n.phg-outline ul{margin:4px 0 2px;padding-left:20px}.phg-outline li{margin:3px 0}\n.phg-source{font-size:12px;color:#5b6b82;margin:-4px 0 10px;font-style:italic}\n.phg-methodlink{font-size:13px;margin:4px 0}.phg-auditline a{color:#7a8698}\n.phg-details{margin:6px 0;font-size:14px}.phg-details>summary{cursor:pointer;color:#2f5d9a}\n.phg-ranked td:nth-child(n+3){text-align:right;font-variant-numeric:tabular-nums}\n.phone-only{display:none}@media (max-width:599px){.phone-only{display:block}}\n.phg-small{font-size:13px;color:#5b6b82;max-width:76ch}\n.phg-body{max-width:76ch;margin:8px 0}.phg-list{max-width:76ch;margin:6px 0 10px;padding-left:22px}.phg-list li{margin:5px 0}.phg-subhead{font-size:16px;font-weight:600;margin:16px 0 4px;max-width:76ch}.phg-refs li{font-size:14px}.phg-listhead{font-size:14px;font-weight:600;margin:10px 0 2px}\n.phg-items td{width:50%}.rk{color:#8e44ad;font-weight:600;font-size:12px}\n.phg-detail{border:1px solid #c9ced6;border-radius:6px;padding:8px 12px;margin:6px 0 10px;background:#f7f8fa;font-size:14px;max-width:520px}\n.phg-detail .dt-title{font-weight:600}.phg-detail .dt-codes{color:#7a8698;font-weight:400;font-size:12px}\n.phg-detail table{border-collapse:collapse;margin:4px 0}.phg-detail td{padding:1px 10px 1px 0}.phg-detail td+td{text-align:right;font-variant-numeric:tabular-nums}\n.phg-detail .dt-note{font-size:12px;color:#5b6b82}\n.phg-details.technical>summary,.phg-details.audit-root>summary{font-weight:600}
.phg-evidence .ev-head{font-weight:600;color:#3b475a;margin-bottom:4px}
.ev-slot{display:flex;gap:10px;padding:3px 0;border-top:1px dashed #dde1e7}
.ev-label{flex:0 0 150px;font-weight:600;color:#5b6b82}
.ev-text{flex:1}
@media (max-width:560px){.ev-slot{flex-direction:column;gap:0}.ev-label{flex:none}}
.phg-todo{border:1px dashed #b07d00;background:#fff8e6;padding:6px 10px;border-radius:6px;margin:6px 0;font-size:14px}
.phg-figure{margin:10px 0 0;max-width:100%;overflow:hidden}
.fig-id{font-size:16.5px;line-height:1.35;color:#1d2430;font-weight:500;margin:14px 0 6px}.fig-id b{font-weight:700}
.tablewrap{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.tablewrap table{border-collapse:collapse;font-size:13px;margin:6px 0}
.tablewrap th,.tablewrap td{border:1px solid #dde1e7;padding:3px 6px;text-align:left;vertical-align:top}
.tablewrap th{background:#eef1f5}
.phg-verify{margin:10px 0 18px;border:1px solid #c9ced6;border-radius:6px;padding:6px 10px}
.phg-verify-title{font-weight:600;margin-bottom:4px}
.tier{display:inline-block;padding:1px 6px;border-radius:10px;font-size:11px;font-weight:700;color:#fff}
.tier-recomputed{background:#1f6f43}.tier-checked{background:#2f5d9a}.tier-hashonly{background:#7a6a55}
tr.st-fail td{background:#fde8e8}tr.st-note td{background:#fff8e6}
.phg-mode{background:#eef4ff;border:1px solid #b9cdf0;border-radius:6px;padding:6px 10px;font-size:14px;margin:8px 0}tr.st-skipped td{background:#f4f4f4;color:#666}
</style>
"""


# ------------------------------------------------------------ notebook output
def init_page():
    """Load page CSS and an embedded (offline) plotly.js. Tagged 'plotly-init'
    so the HTML exporter can replace it with a single <head> copy."""
    from IPython.display import HTML, display
    import plotly.offline
    display(HTML(STYLE + "<script type='text/javascript'>" + plotly.offline.get_plotlyjs() + "</script>" + DETAILS_SCRIPT))


def show(fig, key: str, after: str = "", post_script: str = "", before: str = ""):
    """Layered result: lead, figure, how-to-read caption, optional extra HTML, evidence panel."""
    from IPython.display import HTML, display
    lead = lead_html(key) + before
    if lead:
        display(HTML(lead))
    frag = figure_html(fig, key, post_script=post_script)
    display({"text/html": frag, "application/vnd.plotly.v1+json": json.loads(fig.to_json())}, raw=True)
    rest = caption_html(key) + after + evidence_panel(key)
    if rest:
        display(HTML(rest))


def show_block(key: str, inner: str):
    """Layered result for a table or other non-figure result."""
    show_html(lead_html(key) + inner + caption_html(key) + evidence_panel(key))


def show_html(s: str):
    from IPython.display import HTML, display
    display(HTML(s))


def mode_banner_text(m: str) -> str:
    return ("Built in READER mode: saved results with light computation (correlations, conditioning, influence, calibration curve)."
            if m == READER else
            "Built in REPRODUCTION mode: everything recomputable here is recomputed, every snapshot file is re-derived from Git, "
            "independent bootstrap checks run, and the human matrix is recomputed if the raw OSF file is present.")


def mode_banner(m: str) -> str:
    text = ("READER: saved results with light computation (correlations, conditioning, influence, calibration curve)."
            if m == READER else
            "REPRODUCTION: recomputes everything recomputable here, Git re-derivation of every snapshot file, independent bootstrap checks, and human recomputation if the raw OSF file is present.")
    return f"<div class='phg-mode'><b>Mode: {m}.</b> {html_escape(text)}</div>"


def html_escape(s):
    import html as _h
    return _h.escape(s)


def tier_tables(L: "Ledger", section: str) -> str:
    out = []
    for tier in TIERS:
        cs = [c for c in L.section(section) if c.tier == tier]
        if cs:
            out.append(verification_html(cs, f"Section {section} · {tier}"))
    return "".join(out)


AUDIT_GROUPS = [("Section 1", ("1",)), ("Section 2", ("2",)), ("Section 3", ("S",)), ("Section 4", ("3", "4")),
                ("Section 5", ("6",)), ("Appendix E", ("E",)), ("Appendix F", ("F",)), ("Appendix G", ("G",)),
                ("Appendix H", ("5",))]


def audit_appendix(L: "Ledger", groups=None) -> str:
    """All tiered verification tables, one collapsed block per reader-facing section (ledger keys mapped in AUDIT_GROUPS)."""
    parts = []
    for label, keys in groups or AUDIT_GROUPS:
        cs = [c for k in keys for c in L.section(k)]
        if cs:
            n = sum(c.status == "PASS" for c in cs)
            parts.append(details(f"{label}: {len(cs)} checks, {n} passed", "".join(tier_tables(L, k) for k in keys if L.section(k)),
                                 cls="audit"))
    return "".join(parts)
