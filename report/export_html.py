#!/usr/bin/env python3
"""Execute phg_report.ipynb and export one self-contained HTML file.

plotly.js is embedded once in <head> (no CDN). Code is kept in collapsed
<details> blocks (hidden by default). No Python kernel is needed to view it.

Usage: python research/notebooks/export_html.py [--mode READER|REPRODUCTION] [--no-execute]
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

import nbformat
import plotly.offline
from nbclient import NotebookClient
from nbconvert.filters.markdown_mistune import markdown2html_mistune

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from phg.report import DETAILS_SCRIPT, STYLE  # noqa: E402

# Custom plotly.js 3.7.0 bundle (MIT, vendored; recipe in vendor/bundle_recipe): cartesian traces + scatter3d, ~1.7 MB.
VENDOR_JS = HERE / "vendor" / "plotly-phg.min.js"

PAGE_CSS = """
<style>
:root{--fg:#1d2430;--muted:#5b6b82;--bg:#ffffff;--line:#dde1e7}
html,body{margin:0;padding:0;background:var(--bg);color:var(--fg)}
body{font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:980px;margin:0 auto;padding:12px 16px 60px;box-sizing:border-box}
h1{font-size:26px;line-height:1.25}h2{font-size:21px;margin-top:38px;border-bottom:2px solid var(--line);padding-bottom:4px}
h3{font-size:17px;margin-top:26px}
p,li{max-width:76ch}
code{font-size:13px;background:#f2f4f7;padding:0 3px;border-radius:3px;word-break:break-word}
.md table{border-collapse:collapse;font-size:14px;display:block;overflow-x:auto;max-width:100%}
.md td,.md th{border:1px solid var(--line);padding:3px 8px}
details.code{margin:2px 0;font-size:11px;opacity:.75}
details.code summary{cursor:pointer;color:var(--muted)}
details.code pre{background:#f6f8fa;border:1px solid var(--line);padding:8px;overflow-x:auto;max-width:100%;box-sizing:border-box}
pre.stream{background:#f6f8fa;padding:6px;overflow-x:auto;font-size:12px}
.err{background:#fde8e8;border:1px solid #e0a0a0;padding:6px}
nav.toc{font-size:14px;border:1px solid var(--line);border-radius:6px;padding:6px 12px;margin:10px 0}
nav.toc a{color:#2f5d9a;text-decoration:none;display:block;padding:1px 0}
nav.toc .toc-title{font-weight:700;margin-bottom:2px}
.phg-stamp{font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:#5b6b82;margin:4px 0 6px}
.phg-mode{background:#eef4ff;border:1px solid #b9cdf0;border-radius:6px;padding:6px 10px;font-size:14px;margin:8px 0}
.js-plotly-plot,.plotly-graph-div{max-width:100%}
img{max-width:100%}
</style>
"""


def plotly_js() -> str:
    return VENDOR_JS.read_text() if VENDOR_JS.exists() else plotly.offline.get_plotlyjs()


def execute(path: Path, mode: str, draft: bool = True) -> nbformat.NotebookNode:
    nb = nbformat.read(path, as_version=4)
    os.environ["PHG_MODE"] = mode
    os.environ["PHG_DRAFT"] = "1" if draft else "0"
    # Optional IPC kernel transport permits validation with all network sockets denied.
    from traitlets.config import Config
    config = Config()
    if os.environ.get("PHG_KERNEL_IPC") == "1":
        config.KernelManager.transport = "ipc"
    NotebookClient(nb, timeout=1200, kernel_name="python3", config=config, resources={"metadata": {"path": str(HERE)}}).execute()
    return nb


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render(nb: nbformat.NotebookNode, title: str, stamp: str = "") -> str:
    parts, toc = [], []
    for cell in nb.cells:
        tags = cell.get("metadata", {}).get("tags", [])
        if cell.cell_type == "markdown":
            body = markdown2html_mistune(cell.source)

            def add_id(m):
                level, inner = m.group(1), m.group(2)
                plain = html.unescape(re.sub("<[^>]+>", "", inner))  # e.g. "Qwen's": unescape before slug and Contents
                sid = slug(plain.replace("'", ""))
                if level == "2":
                    toc.append((sid, plain))
                return f"<h{level} id='{sid}'>{inner}</h{level}>"
            body = re.sub(r'<a class="anchor-link"[^>]*>.*?</a>', "", body)  # drop pilcrow anchors
            body = re.sub(r"<h([23])[^>]*>(.*?)</h\1>", add_id, body)
            parts.append(f"<div class='md'>{body}</div>")
            continue
        if cell.cell_type != "code":
            continue
        parts.append(f"<details class='code'><summary>Show code</summary><pre><code>{html.escape(cell.source)}</code></pre></details>")
        if "plotly-init" in tags:
            # plotly.js and CSS are already in <head>; keep only the mode banner.
            for out in cell.get("outputs", []):
                h = out.get("data", {}).get("text/html", "")
                for m in re.finditer(r"<div class='phg-mode'>.*?</div>", h, re.S):
                    parts.append(m.group(0))
            continue
        for out in cell.get("outputs", []):
            ot = out.get("output_type")
            if ot == "stream":
                parts.append(f"<pre class='stream'>{html.escape(out.get('text', ''))}</pre>")
            elif ot == "error":
                parts.append(f"<pre class='err'>{html.escape(out.get('ename', ''))}: {html.escape(out.get('evalue', ''))}</pre>")
            elif ot in ("display_data", "execute_result"):
                data = out.get("data", {})
                if "text/html" in data:
                    parts.append(data["text/html"])
                elif "text/plain" in data:
                    parts.append(f"<pre class='stream'>{html.escape(data['text/plain'])}</pre>")
    nav = ("<nav class='toc'><div class='toc-title'>Contents</div>"
           + "".join(f"<a href='#{s}'>{html.escape(t)}</a>" for s, t in toc) + "</nav>")
    body = "".join(parts)
    # Insert the table of contents after the first markdown block.
    i = body.find("</div>") + len("</div>")
    body = body[:i] + nav + body[i:]
    # Build stamp (iteration 15): which iteration and source commit this page was built from.
    if stamp:
        body = f"<div class='phg-stamp' id='build-stamp'>{html.escape(stamp)}</div>" + body
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>{html.escape(title)}</title>{PAGE_CSS}{STYLE}"
            f"<script type='text/javascript'>{plotly_js()}</script>{DETAILS_SCRIPT}"
            f"</head><body><main>{body}</main></body></html>")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="READER", choices=["READER", "REPRODUCTION"])
    ap.add_argument("--no-execute", action="store_true")
    ap.add_argument("--draft", default="on", choices=["on", "off"], help="show draft outline boxes (default on)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--stamp", default="", help='build stamp shown at the top, e.g. "Iteration 15 · 3f2a1bc · Nov 5"')
    a = ap.parse_args()
    src = HERE / "phg_report.ipynb"
    if a.no_execute:
        nb = nbformat.read(src, as_version=4)
    else:
        nb = execute(src, a.mode, draft=(a.draft == "on"))  # the committed .ipynb stays output-free; the HTML is the rendered copy
    out = Path(a.out) if a.out else HERE / ("phg_report.html" if a.mode == "READER" else "phg_report_reproduction.html")
    out.write_text(render(nb, "Persona–Human Geometry", stamp=a.stamp))
    errors = sum(o.get("output_type") == "error" for c in nb.cells for o in c.get("outputs", []))
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB), {errors} error outputs")
