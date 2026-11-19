"""Plotly figure builders and reader-facing tables.

Interactions use built-in updatemenus/sliders; figure 4.2 adds a small inline
click handler (offline) for its detail panel. Conventions (shared with
PHG-TOOL01): Pearson r on a fixed -1..+1 scale (red positive, blue negative);
differences on a fixed -2..+2 brown/teal scale. Every figure's initial state
reads as a static image. Conditioned views keep the original result visible
and are labelled "conditioned on X". Facets appear by full name in Big Five
domain order (N, E, O, A, C); codes appear only in hover text.
"""
from __future__ import annotations

import html
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import analysis as A
from . import report as R
from . import stats

REV, AGR, OTH, FOCUS = "#c0392b", "#1f7a4d", "#9aa4b2", "#111111"
SCEN, SURV, HUM = "#2f5d9a", "#d9822b", "#222222"
RESCALED = "#1f7a4d"  # after-rescaling marker (prediction chart)
FMT_COLOR = {"scenario": SCEN, "survey_style": SURV}
PEARSON_SCALE = "RdBu_r"
DIFF_SCALE = "BrBG"
GROUP_STYLE = {
    "consistent_reversal": ("Reversed in Qwen (13)", REV, 9),
    "close_agreement": ("Close match (6)", AGR, 8),
    "other": ("Other pairs", OTH, 5),
}
FOCAL_PAIR = ("E1", "N2")


def fmt_name(fmt: str, cap: bool = False) -> str:
    s = A.FORMAT_NAME[fmt]
    return s[0].upper() + s[1:] if cap else s


def wrap_pair(a: str, b: str) -> str:
    return f"{A.name(a)} –<br>{A.name(b)}"


def note(text, yshift=4):
    """Annotation just above the plot area, right-anchored so it never clips at phone width."""
    return dict(xref="paper", yref="paper", x=1, y=1.0, xanchor="right", yanchor="bottom", showarrow=False,
                align="left", yshift=yshift, font=dict(size=11, color="#333"), text=text)


def base_layout(fig, title, height=520, menus=None, note_lines=0, extra_top=0, b=60, l=55, r=15, **kw):
    """Stack, from the top: dropdown menu, note lines, plot. The title names the quantity shown; it is stored in
    layout.meta and rendered as the HTML figure label ("Figure N. title") above the chart, which wraps at phone width
    and follows dropdown changes (buttons set a new meta). The legend sits at the bottom of the figure (container
    coordinates), inside margin b. Legend taps do not hide series: a stray tap on a phone left a series greyed out
    with no markers (iteration 8 bug in Figure E.5)."""
    menu_h = 46 if menus else 24  # without a menu, keep the note lines clear of the plotly toolbar
    t = 6 + menu_h + 15 * note_lines + 12 + extra_top
    plot_h = height - t - b
    for m in menus or []:
        m.update(y=1 + (t - 4) / plot_h, yanchor="top")
    fig.update_layout(
        meta=title, template="plotly_white", height=height, font=dict(size=12),
        margin=dict(l=l, r=r, t=t, b=b), updatemenus=menus or [],
        legend=dict(orientation="h", yref="container", yanchor="bottom", y=0.004, x=0, font=dict(size=11),
                    itemclick=False, itemdoubleclick=False),
        hoverlabel=dict(font_size=12), **kw)
    return fig


def menu(buttons, x=0.0):
    return dict(type="dropdown", direction="down", x=x, xanchor="left", buttons=buttons, showactive=True,
                pad=dict(r=2, t=2), font=dict(size=11))


def vis_mask(n, on):
    return [i in on for i in range(n)]


def _col(fmt):
    return "scenario" if fmt == "scenario" else "survey"


BEST_FIT = "#6b7a8f"  # muted solid best-fit line (iteration 11)
PERFECT = "Perfect agreement"


def two(x: float) -> str:
    """Correlation without the leading zero: .44, -.48."""
    return f"{x:.2f}".replace("0.", ".", 1)


def trend_trace(x, y, visible=True, x_range=(-1.0, 1.0), name="Trend", **kw):
    """Standardized major axis of y on x (iteration 13; replaces the least-squares line), drawn across x_range.
    Returns (trace, slope, intercept); the slope is the ratio of the two spreads."""
    slope, icpt = stats.sma(x, y)
    xs = np.array(x_range, float)
    return (go.Scatter(x=xs, y=icpt + slope * xs, mode="lines", name=name, visible=visible, hoverinfo="skip",
                       line=dict(color=BEST_FIT, width=2), **kw), slope, icpt)


MAIN_FMT = "scenario"  # iteration 9: the main text uses the scenario-prompt extraction only; survey-style is Appendix F


def _ttl(title, fmt):
    """Fixed figure title; the Appendix F (survey-style) versions say so."""
    return title if fmt == MAIN_FMT else f"{title}, survey-style prompts"


# ================================================================ Section 4
QWEN_AVG = "Qwen (average of scenario and survey prompts)"


def avg_agreement():
    """Pattern agreement (Pearson over 325 pairs) and sign agreement for the format-averaged Qwen r."""
    p = A.pairs325()
    return stats.pearson(p.human, p.qwen), float((np.sign(p.human) == np.sign(p.qwen)).mean())


def human_vs_qwen_scatter(fmt: str = MAIN_FMT) -> go.Figure:
    """Headline: people r vs Qwen r for one prompt format (scenario in the main text). The reversal / close-match classes
    keep their frozen definition (both formats separately)."""
    p = A.pairs325()
    col = _col(fmt)
    focal = p[(p.left == FOCAL_PAIR[0]) & (p.right == FOCAL_PAIR[1])].iloc[0]
    fig = go.Figure()
    for g in ["other", "close_agreement", "consistent_reversal"]:
        label, color, size = GROUP_STYLE[g]
        d = p[p.group_frozen == g]
        fig.add_trace(go.Scatter(
            x=d.human, y=d[col], mode="markers", name=label, legendgroup=g,
            marker=dict(size=size, color=color, line=dict(width=0.5, color="white"), opacity=0.95 if g != "other" else 0.6),
            customdata=np.column_stack([d.label, d.left + "–" + d.right]),
            hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>in people r %{x:+.3f}"
                          "<br>in Qwen r %{y:+.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[focal.human], y=[focal[col]], mode="markers", name="Friendliness–Anger", showlegend=False,
                             hoverinfo="skip", marker=dict(symbol="circle-open", size=20, color=FOCUS, line=dict(width=2.5))))
    fig.add_trace(go.Scatter(x=[-1, 1], y=[-1, 1], mode="lines", line=dict(color="#555", dash="dash", width=1),
                             name=PERFECT, hoverinfo="skip"))
    bf, slope, _ = trend_trace(p.human, p[col])
    fig.add_trace(bf)
    quad = [(-1, 1, "left", "top", "Opposite in people,<br>together in Qwen"), (1, 1, "right", "top", "Together in both"),
            (-1, -1, "left", "bottom", "Opposite in both"), (1, -1, "right", "bottom", "Together in people,<br>opposite in Qwen")]
    anns = [dict(x=x, y=y, xref="x", yref="y", xanchor=xa, yanchor=ya, text=t, showarrow=False, align="left" if xa == "left" else "right",
                 font=dict(size=10, color="#a3abb8")) for x, y, xa, ya, t in quad]
    pa, sa = format_agreement_with_people(fmt)
    anns.append(note(f"agreement r = {two(pa)} · Qwen links {slope:.1f}x as strong as people"))
    anns.append(dict(x=float(focal.human), y=float(focal[col]), xref="x", yref="y", ax=70, ay=40,
                     text="Friendliness–Anger:<br>Appendix H",
                     showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor="#111", font=dict(size=11, color="#111"), align="left"))
    base_layout(fig, _ttl("Trait-pair correlations in people and in Qwen", fmt), height=590, note_lines=1,
                annotations=anns, b=125)
    fig.update_xaxes(title="Correlation between the two traits in people (r)", range=[-1.05, 1.05], zeroline=True,
                     zerolinecolor="#bbb", dtick=0.5)
    fig.update_yaxes(title="Correlation between the two traits in Qwen (r)", range=[-1.05, 1.05], zeroline=True,
                     zerolinecolor="#bbb", dtick=0.5)
    return fig


def format_agreement_with_people(fmt: str = MAIN_FMT):
    """Pattern agreement (saved Pearson over the 325 pairs) and sign agreement (recomputed) for one prompt format."""
    p = A.pairs325()
    fp = A.S.csv("d30b_fingerprints").set_index("source")
    return float(fp.loc[fmt, "Pearson"]), float((np.sign(p.human) == np.sign(p[_col(fmt)])).mean())


def reversal_table_html() -> str:
    """Ranked list of the 13 reversals, full names, three r values (rank = frozen discrepancy rank)."""
    p = A.pairs325()
    od = A.S.csv("od_all_pairs").set_index("pair")
    d = p[p.group_frozen == "consistent_reversal"].copy()
    d["rank"] = d.pair.map(od.discrepancy_rank)
    d = d.sort_values("rank")
    t = pd.DataFrame({"#": range(1, len(d) + 1), "Trait pair": d.label, "People": d.human, "Qwen": d[_col(MAIN_FMT)]})
    return ("<p class='phg-listhead'>The 13 pairs where Qwen reverses the human pattern, largest gap first (correlation r)</p>"
            + R.table_html(t, float_fmt="{:+.2f}", cls="phg-ranked"))


DOMAIN_ABBR = {"N": "Neur.", "E": "Extr.", "O": "Open.", "A": "Agree.", "C": "Consc."}
BAND_W = 18          # band thickness, px
OFF_FACET = 104      # px from the matrix edge to the band: clears the 26 facet tick labels
OFF_DOMAIN = 6       # domain-average view: tick labels hidden, the band sits at the edge
BAND_TINT = ["#e9edf3", "#dbe2ec"]


def domain_bands(spans, xref, yref, off, kind):
    """Tinted label bands outside the top and left edges, one per Big Five domain.

    spans: (domain letter, first index, last index + 1) along both axes. Sizes are in pixels from the matrix edge
    (x/y index -0.5), so the bands follow the separators wherever the plot sits. Annotation names carry
    "domband|<kind>|<axis>|<letter>|<cells>" so the page script can abbreviate them when a block is too narrow.
    """
    shapes, anns = [], []
    for k, (d, p0, p1) in enumerate(spans):
        tint = BAND_TINT[k % 2]
        mid = (p0 + p1 - 1) / 2
        common = dict(type="rect", line=dict(width=0), fillcolor=tint, layer="above")  # bands never overlap cells
        # Outward dimension anchored to the subplot domain edge: shapes tied to an axis in that dimension are
        # clipped to the plot area. The plot is constrained toward the top-left, so domain top/left = matrix edge.
        ydom = "y domain" if yref == "y" else "y2 domain"
        xdom = "x domain" if xref == "x" else "x2 domain"
        shapes.append(dict(common, xref=xref, x0=p0 - 0.5, x1=p1 - 0.5, yref=ydom, ysizemode="pixel", yanchor=1,
                           y0=off, y1=off + BAND_W))
        shapes.append(dict(common, yref=yref, y0=p0 - 0.5, y1=p1 - 0.5, xref=xdom, xsizemode="pixel", xanchor=0,
                           x0=-(off + BAND_W), x1=-off))
        font = dict(size=10, color="#1d2430")
        anns.append(dict(name=f"domband|{kind}|x|{d}|{p1 - p0}", xref=xref, yref=yref, x=mid, y=-0.5, yshift=off + BAND_W / 2,
                         xanchor="center", yanchor="middle", showarrow=False, text=A.DOMAIN_NAME[d], font=font))
        anns.append(dict(name=f"domband|{kind}|y|{d}|{p1 - p0}", xref=xref, yref=yref, x=-0.5, xshift=-(off + BAND_W / 2),
                         y=mid, xanchor="center", yanchor="middle", textangle=-90, showarrow=False, text=A.DOMAIN_NAME[d],
                         font=font))
    return shapes, anns


def correlation_matrices(fmt: str = MAIN_FMT, domains: bool = True) -> go.Figure:
    """Full facet matrices (People, Qwen, Qwen − People) plus, in the main text, 5 x 5 domain-average views on a second
    axis pair. One prompt format per figure (scenario in the main text; survey-style in Appendix F, without domain views)."""
    M = A.matrices()
    mk = "scenario" if fmt == "scenario" else "survey_style"
    cs = list(A.codes())
    oc = list(A.ordered_codes())
    nf = len(oc)
    perm = [cs.index(c) for c in oc]
    names = [A.name(c) for c in oc]
    hover = [[f"{A.name(b)} ({b}) – {A.name(a)} ({a})" for a in oc] for b in oc]
    diag = np.eye(nf, dtype=bool)  # full matrix: each pair appears twice; only the diagonal is blank
    # Iteration 6: Qwen shown as the average of the two prompt formats.
    # (menu label, matrix, scale, lo, hi, colour-bar label)
    views = [
        ("People", M["human"], PEARSON_SCALE, -1, 1, "r"),
        ("Qwen", M[mk], PEARSON_SCALE, -1, 1, "r"),
        ("Qwen − People", M[mk] - M["human"], DIFF_SCALE, -2, 2, "Qwen r − people r"),
    ]
    cbar = dict(orientation="h", thickness=10, len=0.8, title_side="top")
    fig = go.Figure()
    for k, (label, Z, scale, lo, hi, unit) in enumerate(views):
        Zd = Z[np.ix_(perm, perm)].copy()
        Zd[diag] = np.nan
        fig.add_trace(go.Heatmap(z=Zd, x=names, y=names, colorscale=scale, zmin=lo, zmax=hi, zmid=0, visible=(k == 0),
                                 customdata=hover, name=label, xgap=0.5, ygap=0.5, hoverongaps=False,
                                 colorbar=dict(title=unit, **cbar),
                                 hovertemplate="%{customdata}<br>" + unit + " %{z:+.3f}<extra>" + label + "</extra>"))
    n_facet = len(fig.data)
    # Domain-average views (second axis pair), lower triangle of the 5 x 5 grid.
    doms = A.DOMAIN_ORDER
    dn = [A.DOMAIN_NAME[d] for d in doms]
    full = A.domain_blocks()
    dcol = "scenario" if fmt == "scenario" else "survey"
    dviews = [("People", full, "human", PEARSON_SCALE, -1, 1, "r", ""),
              ("Qwen", full, dcol, PEARSON_SCALE, -1, 1, "r", ""),
              ("Qwen − People", full, f"diff_{dcol}", DIFF_SCALE, -2, 2, "Qwen r − people r", "")] if domains else []
    for label, blocks, col, scale, lo, hi, unit, note_ in dviews:
        idx = {(r.row, r.col): r for r in blocks.itertuples()}
        Z = np.full((5, 5), np.nan)
        cnt = np.full((5, 5), "", dtype=object)
        txt = np.full((5, 5), "", dtype=object)
        for i_, di in enumerate(doms):
            for j_, dj in enumerate(doms):
                r = idx[(di, dj)] if (di, dj) in idx else idx[(dj, di)]  # blocks are stored once; mirror them
                Z[i_, j_] = getattr(r, col)
                txt[i_, j_] = f"{Z[i_, j_]:+.2f}".replace("-", "−")
                cnt[i_, j_] = (f"{A.DOMAIN_NAME[di]} × {A.DOMAIN_NAME[dj]}<br>average of {r.n_pairs} facet-pair correlations"
                               + note_)
        fig.add_trace(go.Heatmap(z=Z, x=dn, y=dn, xaxis="x2", yaxis="y2", colorscale=scale, zmin=lo, zmax=hi, zmid=0,
                                 visible=False, customdata=cnt, name="Domains: " + label, xgap=2, ygap=2,
                                 hoverongaps=False, text=txt, texttemplate="%{text}", textfont=dict(size=11),
                                 colorbar=dict(title=unit, **cbar),
                                 hovertemplate="%{customdata}<br>" + unit + " %{z:+.3f}<extra>" + label + "</extra>"))
    n = len(fig.data)

    # Domain separators within the lower triangle, and domain label bands outside the top and left edges.
    shapes, pos = [], 0
    starts = []
    for dom in doms:
        starts.append(pos)
        pos += sum(c[0] == dom for c in oc)
    for p0 in starts[1:]:
        shapes.append(dict(type="line", xref="x", yref="y", x0=p0 - 0.5, x1=p0 - 0.5, y0=-0.5, y1=nf - 0.5,
                           line=dict(color="#333", width=1.2)))
        shapes.append(dict(type="line", xref="x", yref="y", x0=-0.5, x1=nf - 0.5, y0=p0 - 0.5, y1=p0 - 0.5,
                           line=dict(color="#333", width=1.2)))
    band_shapes, edges = domain_bands([(d, p0, p1) for d, p0, p1 in zip(doms, starts, starts[1:] + [nf])], "x", "y", OFF_FACET, "facet")
    shapes += band_shapes
    # Iteration 30: outline the 13 frozen reversals (both mirrored cells), now that Figure 4.1 and its table sit just above.
    p325 = A.pairs325()
    rev = p325[p325.group_frozen == "consistent_reversal"]
    for a, b in zip(rev.left, rev.right):
        i, j = oc.index(a), oc.index(b)
        for (x0, y0) in [(j, i), (i, j)]:
            shapes.append(dict(type="rect", xref="x", yref="y", x0=x0 - 0.5, x1=x0 + 0.5, y0=y0 - 0.5, y1=y0 + 0.5,
                               line=dict(color="#111", width=1.6), fillcolor="rgba(0,0,0,0)", name="reversal"))
    dband_shapes, dedges = domain_bands([(d, k, k + 1) for k, d in enumerate(doms)], "x2", "y2", OFF_DOMAIN, "domain")
    dnote = [dict(xref="x2 domain", yref="y2 domain", x=0, y=0, xanchor="left", yanchor="top", yshift=-6, showarrow=False,
                  align="left",
                  font=dict(size=11, color="#333"), text="Domain averages: average of facet-pair<br>correlations, descriptive")]
    facet_layout = {"xaxis.visible": True, "yaxis.visible": True, "xaxis2.visible": False, "yaxis2.visible": False,
                    "shapes": shapes, "annotations": edges}
    # Keep one invisible shape on the facet axes: if nothing references them, Plotly drops that subplot while
    # its scale anchor remains and fails with "ax.dtick error: Infinity" on the first switch.
    anchor_shape = [dict(type="line", xref="x", yref="y", x0=0, x1=0, y0=0, y1=0, opacity=0, line=dict(width=0))]
    domain_layout = {"xaxis.visible": False, "yaxis.visible": False, "xaxis2.visible": True, "yaxis2.visible": True,
                     "shapes": anchor_shape + dband_shapes, "annotations": dnote + dedges}
    buttons = [dict(label=v[0], method="update", args=[{"visible": vis_mask(n, [k])}, facet_layout])
               for k, v in enumerate(views)]
    buttons += [dict(label="Domains: " + v[0], method="update", args=[{"visible": vis_mask(n, [n_facet + k])}, domain_layout])
                for k, v in enumerate(dviews)]
    # extra_top reserves room for the long top tick labels so they sit below the title.
    base_layout(fig, _ttl("Trait correlations (r)", fmt), height=900,
                menus=[menu(buttons)], b=75, l=OFF_FACET + BAND_W + 10, r=12, extra_top=OFF_FACET + BAND_W + 8,
                shapes=shapes, annotations=edges)
    mg = fig.layout.margin
    fig.update_traces(colorbar=dict(yref="paper", y=-(mg.b - 4) / (fig.layout.height - mg.t - mg.b), yanchor="bottom"))
    fig.update_layout(
        # Two overlapping subplots share this area: a transparent plot background stops the hidden one's
        # white background from covering the visible heatmap.
        plot_bgcolor="rgba(0,0,0,0)",
        # Facet labels unchanged: rows horizontal, column headings rotated (reading bottom to top). automargin off so the
        # fixed-pixel bands keep their place; the margins above leave room for the labels.
        # Explicit ranges so the square-cell constraint shrinks the plot area (toward the top-left) instead of
        # widening a range: the matrix edge then coincides with the axis edge the bands are measured from.
        xaxis=dict(tickfont=dict(size=9), tickangle=-90, side="top", dtick=1, range=[-0.5, nf - 0.5], autorange=False,
                   constrain="domain", constraintoward="left", showgrid=False, automargin=False),
        yaxis=dict(tickfont=dict(size=9), range=[nf - 0.5, -0.5], autorange=False, dtick=1, scaleanchor="x", scaleratio=1,
                   constrain="domain", constraintoward="top", showgrid=False, automargin=False),
        # Explicit ranges: the domain axes start hidden and empty, and Plotly cannot infer a tick step then.
        # Domain view: the bands replace the tick labels.
        xaxis2=dict(visible=False, anchor="y2", domain=[0, 1], side="top", showticklabels=False, constrain="domain",
                    constraintoward="left", showgrid=False, type="category", categoryarray=dn, range=[-0.5, 4.5], dtick=1,
                    automargin=False),
        yaxis2=dict(visible=False, anchor="x2", domain=[0, 1], showticklabels=False, type="category", categoryarray=dn,
                    range=[4.5, -0.5], dtick=1, scaleanchor="x2", scaleratio=1, constrain="domain", constraintoward="top",
                    showgrid=False, automargin=False))
    return fig


OFF_BFT = 88  # px from the matrix edge to the band: clears the 42 trait tick labels (Figure 1.3)


def bigfive_trait_matrix_figure(people: bool = False, models=("qwen", "gemma", "llama")) -> go.Figure:
    """Figure 1.3 (iteration 31): the 42 historical traits of the frozen strict Big Five mapping, grouped by domain in the
    Figure 4.1 order, correlated across the 275 characters within one model. Reverse-keyed traits are sign-flipped
    ("calm (−)"). Menu: Qwen, Gemma, Llama, then the same three as 5 x 5 domain averages (mean trait-pair r per block,
    as in Figure 4.1's domain view; the domain-score r is in the hover). No human view in the report figure.

    people=True (iteration 32 side preview): adds People (SAPA trait proxies) and each model − People, in both the trait
    and the domain views."""
    t = A.bf_traits()
    nt = len(t)
    names = list(t.label)
    fac = [f"{f} {n}" for f, n in zip(t.facet, t.facet_name)]
    hover = [[f"{names[i]} ({fac[i]}) – {names[j]} ({fac[j]})" for j in range(nt)] for i in range(nt)]
    models = list(models)  # Figure 3.1 (iteration 34): Qwen only, as in Figure 4.2
    # (menu label, source, minus-people?, scale, lo, hi, unit)
    views = ([("People (SAPA)", "people", False, PEARSON_SCALE, -1, 1, "r")] if people else []) + \
        [(A.MODEL_LABEL[m], m, False, PEARSON_SCALE, -1, 1, "r") for m in models] + \
        ([(f"{A.MODEL_LABEL[m]} − People", m, True, DIFF_SCALE, -2, 2, "model r − people r") for m in models] if people else [])
    cbar = dict(orientation="h", thickness=10, len=0.8, title_side="top")
    fig = go.Figure()
    for k, (lab, src, diff, scale, lo, hi, unit) in enumerate(views):
        Z = A.bf_corr(src) - (A.bf_corr("people") if diff else 0)
        Z = np.array(Z, float)
        np.fill_diagonal(Z, np.nan)
        fig.add_trace(go.Heatmap(z=Z, x=names, y=names, colorscale=scale, zmin=lo, zmax=hi, zmid=0, visible=(k == 0),
                                 customdata=hover, name=lab, xgap=0.5, ygap=0.5, hoverongaps=False,
                                 colorbar=dict(title=unit, **cbar),
                                 hovertemplate="%{customdata}<br>" + unit + " %{z:+.3f}<extra>" + lab + "</extra>"))
    n_tr = len(fig.data)
    doms = A.DOMAIN_ORDER
    dn = [A.DOMAIN_NAME[d] for d in doms]
    for lab, src, diff, scale, lo, hi, unit in views:
        Z = np.full((5, 5), np.nan)
        txt = np.full((5, 5), "", dtype=object)
        cd = np.full((5, 5), "", dtype=object)
        blocks = A.bf_domain_blocks(src)
        for i_, di in enumerate(doms):
            for j_, dj in enumerate(doms):
                v = A.bf_block(src, di, dj) - (A.bf_block("people", di, dj) if diff else 0)
                n_ = int(blocks[((blocks.row == di) & (blocks.col == dj)) | ((blocks.row == dj) & (blocks.col == di))].n_pairs.iloc[0])
                Z[i_, j_] = v
                txt[i_, j_] = f"{v:+.2f}".replace("-", "−")
                extra = ("" if (di == dj or src == "people" or diff)
                         else f"<br>domain-score r {A.bf_block(src, di, dj, 'domain_r'):+.2f}")
                cd[i_, j_] = f"{A.DOMAIN_NAME[di]} × {A.DOMAIN_NAME[dj]}<br>average of {n_} trait-pair correlations" + extra
        fig.add_trace(go.Heatmap(z=Z, x=dn, y=dn, xaxis="x2", yaxis="y2", colorscale=scale, zmin=lo, zmax=hi, zmid=0,
                                 visible=False, customdata=cd, name="Domains: " + lab, xgap=2, ygap=2, hoverongaps=False,
                                 text=txt, texttemplate="%{text}", textfont=dict(size=11), colorbar=dict(title=unit, **cbar),
                                 hovertemplate="%{customdata}<br>average " + unit + " %{z:+.3f}<extra>" + lab + "</extra>"))
    n = len(fig.data)
    shapes, starts, pos = [], [], 0
    for d in doms:
        starts.append(pos)
        pos += int((t.domain == d).sum())
    for p0 in starts[1:]:
        shapes.append(dict(type="line", xref="x", yref="y", x0=p0 - 0.5, x1=p0 - 0.5, y0=-0.5, y1=nt - 0.5,
                           line=dict(color="#333", width=1.2)))
        shapes.append(dict(type="line", xref="x", yref="y", x0=-0.5, x1=nt - 0.5, y0=p0 - 0.5, y1=p0 - 0.5,
                           line=dict(color="#333", width=1.2)))
    # Outline each within-domain block (the diagonal blocks), the trait-level analogue of a same-domain facet block.
    for p0, p1 in zip(starts, starts[1:] + [nt]):
        shapes.append(dict(type="rect", xref="x", yref="y", x0=p0 - 0.5, x1=p1 - 0.5, y0=p0 - 0.5, y1=p1 - 0.5,
                           line=dict(color="#111", width=1.8), fillcolor="rgba(0,0,0,0)", name="domain_block"))
    band_shapes, edges = domain_bands([(d, p0, p1) for d, p0, p1 in zip(doms, starts, starts[1:] + [nt])], "x", "y", OFF_BFT, "bft")
    shapes += band_shapes
    dband_shapes, dedges = domain_bands([(d, k, k + 1) for k, d in enumerate(doms)], "x2", "y2", OFF_DOMAIN, "domain")
    dnote = [dict(xref="x2 domain", yref="y2 domain", x=0, y=0, xanchor="left", yanchor="top", yshift=-6, showarrow=False,
                  align="left", font=dict(size=11, color="#333"),
                  text="Domain averages: average of trait-pair<br>correlations, descriptive")]
    trait_layout = {"xaxis.visible": True, "yaxis.visible": True, "xaxis2.visible": False, "yaxis2.visible": False,
                    "shapes": shapes, "annotations": edges}
    anchor_shape = [dict(type="line", xref="x", yref="y", x0=0, x1=0, y0=0, y1=0, opacity=0, line=dict(width=0))]
    domain_layout = {"xaxis.visible": False, "yaxis.visible": False, "xaxis2.visible": True, "yaxis2.visible": True,
                     "shapes": anchor_shape + dband_shapes, "annotations": dnote + dedges}
    buttons = [dict(label=v[0], method="update", args=[{"visible": vis_mask(n, [k])}, trait_layout])
               for k, v in enumerate(views)]
    buttons += [dict(label="Domains: " + v[0], method="update",
                     args=[{"visible": vis_mask(n, [n_tr + k])}, domain_layout]) for k, v in enumerate(views)]
    base_layout(fig, "Correlations among the historical traits, grouped by Big Five domain (r)", height=900,
                menus=[menu(buttons)], b=75, l=OFF_BFT + BAND_W + 10, r=12, extra_top=OFF_BFT + BAND_W + 8,
                shapes=shapes, annotations=edges)
    mg = fig.layout.margin
    fig.update_traces(colorbar=dict(yref="paper", y=-(mg.b - 4) / (fig.layout.height - mg.t - mg.b), yanchor="bottom"))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(size=9), tickangle=-90, side="top", dtick=1, range=[-0.5, nt - 0.5], autorange=False,
                   constrain="domain", constraintoward="left", showgrid=False, automargin=False),
        yaxis=dict(tickfont=dict(size=9), range=[nt - 0.5, -0.5], autorange=False, dtick=1, scaleanchor="x", scaleratio=1,
                   constrain="domain", constraintoward="top", showgrid=False, automargin=False),
        xaxis2=dict(visible=False, anchor="y2", domain=[0, 1], side="top", showticklabels=False, constrain="domain",
                    constraintoward="left", showgrid=False, type="category", categoryarray=dn, range=[-0.5, 4.5], dtick=1,
                    automargin=False),
        yaxis2=dict(visible=False, anchor="x2", domain=[0, 1], showticklabels=False, type="category", categoryarray=dn,
                    range=[4.5, -0.5], dtick=1, scaleanchor="x2", scaleratio=1, constrain="domain", constraintoward="top",
                    showgrid=False, automargin=False))
    return fig


def bigfive_phone_script(fig_id: str = "1.3", idx: int = 3) -> str:
    """Below 600 px, open Figure 1.3 on the Qwen domain view (42 trait labels do not fit a phone); the menu still offers
    the trait views."""
    return ("<script>(function(){var g=document.getElementById('fig-" + fig_id + "');"
            "function go(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(go,80);}"
            "if(window.innerWidth>=600)return;"
            "var b=g.layout.updatemenus[0].buttons[" + str(idx) + "];"
            # Shorter frame: the 900 px height and top margin are sized for the 42 trait labels. Menu and colour bar
            # positions are fractions of the plot height, so they are recomputed for the new frame.
            "var H=540,T=" + str(6 + 46 + 12 + OFF_DOMAIN + BAND_W + 8) + ",B=g.layout.margin.b,ph=H-T-B;"
            # Plotly's outer wrapper has a fixed pixel height; shrink it with the figure.
            "g.style.height=H+'px';if(g.parentNode&&g.parentNode.style.height)g.parentNode.style.height=H+'px';"
            "Plotly.update(g,b.args[0],b.args[1]).then(function(){"
            "return Plotly.restyle(g,{'colorbar.y':-(B-4)/ph});}).then(function(){"
            "Plotly.relayout(g,{'updatemenus[0].active':" + str(idx) + ",height:H,'margin.t':T,'updatemenus[0].y':1+(T-4)/ph});});}"
            "go();})();</script>") + domain_band_script(fig_id)


OFF_ROWS = 118  # px from the plot's left edge to the band: clears the facet row labels


def left_domain_band(oc, kind, off=OFF_ROWS):
    """Separators plus a shaded left band per Big Five domain (names rotated, reading bottom to top) for a
    chart whose rows are the facets in `oc` at y = 0..n-1 (as in 4.2)."""
    shapes, anns, pos = [], [], 0
    for k, dom in enumerate(A.DOMAIN_ORDER):
        p0 = pos
        pos += sum(c[0] == dom for c in oc)
        if p0:
            shapes.append(dict(type="line", xref="x domain", x0=0, x1=1, yref="y", y0=p0 - 0.5, y1=p0 - 0.5,
                               line=dict(color="#c3c9d2", width=1)))
        shapes.append(dict(type="rect", line=dict(width=0), fillcolor=BAND_TINT[k % 2], layer="above", yref="y",
                           y0=p0 - 0.5, y1=pos - 0.5, xref="x domain", xsizemode="pixel", xanchor=0, x0=-(off + BAND_W), x1=-off))
        anns.append(dict(name=f"domband|{kind}|y|{dom}|{pos - p0}", xref="x domain", x=0, xshift=-(off + BAND_W / 2), yref="y",
                         y=(p0 + pos - 1) / 2, xanchor="center", yanchor="middle", textangle=-90, showarrow=False,
                         text=A.DOMAIN_NAME[dom], font=dict(size=10, color="#1d2430")))
    return shapes, anns


def facet_fit_figure() -> go.Figure:
    """E.2: each facet's mean correlation with the other facets in its own domain (people, Qwen scenario, Qwen survey)."""
    d = A.facet_fit()
    oc = list(d.facet)
    ys = np.arange(len(oc))
    fig = go.Figure()
    cd = np.column_stack([d.name, d.facet, d.n_pairs])
    ht = "%{customdata[0]} (%{customdata[1]})<br>mean r with %{customdata[2]} same-domain facets: %{x:+.3f}<extra>"
    for col, name, sym, color, size in [("human", "People", "diamond", HUM, 9),
                                        ("scenario", "Qwen, scenario", "circle", SCEN, 8),
                                        ("survey", "Qwen, survey-style", "square", SURV, 7)]:
        fig.add_trace(go.Scatter(x=d[col], y=ys, mode="markers", name=name, marker=dict(symbol=sym, size=size, color=color),
                                 customdata=cd, hovertemplate=ht + name + "</extra>"))
    # Domain separators and the same left label band as 4.2.
    off = OFF_ROWS
    shapes, anns = left_domain_band(oc, "fit", off)
    base_layout(fig, "Average correlation of each facet with the other facets in its domain (r)", height=760, b=95, l=off + BAND_W + 10, r=12,
                shapes=shapes, annotations=anns)
    fig.add_vline(x=0, line=dict(color="#999", width=1))
    fig.update_xaxes(title="Average correlation with same-domain facets (r)", range=[-0.2, 1.0])
    fig.update_yaxes(tickvals=list(ys), ticktext=list(d.name), range=[len(ys) - 0.5, -0.5], tickfont=dict(size=10),
                     automargin=False, showgrid=False)
    return fig


def matrix_detail_script(fig_id: str = "4.2", fmt: str = MAIN_FMT) -> str:
    """Inline, offline click handler: shows people r, Qwen r and their difference for the tapped cell."""
    M = A.matrices()
    mk = "scenario" if fmt == "scenario" else "survey_style"
    cs = list(A.codes())
    oc = list(A.ordered_codes())
    perm = [cs.index(c) for c in oc]
    data = dict(names=[A.name(c) for c in oc], codes=oc,
                h=np.round(M["human"][np.ix_(perm, perm)], 4).tolist(),
                q=np.round(M[mk][np.ix_(perm, perm)], 4).tolist(),
                start=[oc.index(FOCAL_PAIR[0]), oc.index(FOCAL_PAIR[1])])
    pid = f"detail-{fig_id}"
    return f"""<div class='phg-detail' id='{pid}' aria-live='polite'></div>
<script>(function(){{
var D={json.dumps(data)};
function f(x){{return (x>=0?'+':'\\u2212')+Math.abs(x).toFixed(2);}}
function show(i,j){{
  var el=document.getElementById('{pid}'); if(!el) return;
  el.innerHTML='<div class="dt-title">'+D.names[i]+' \\u2013 '+D.names[j]+' <span class="dt-codes">('+D.codes[i]+'\\u2013'+D.codes[j]+')</span></div>'+
   '<table><tr><td>In people</td><td>'+f(D.h[i][j])+'</td></tr>'+
   '<tr><td>In Qwen</td><td>'+f(D.q[i][j])+'</td></tr>'+
   '<tr><td>Qwen \\u2212 people</td><td>'+f(D.q[i][j]-D.h[i][j])+'</td></tr></table>'+
   '<div class="dt-note">These are correlations in different samples (real respondents vs written characters), not effects of changing one trait.</div>';
  el.dataset.pair=D.codes[i]+'__'+D.codes[j];
}}
function bind(){{
  var gd=document.getElementById('fig-{fig_id}');
  if(!gd||!gd.on){{return setTimeout(bind,60);}}
  gd.on('plotly_click',function(e){{var p=e.points&&e.points[0]; if(!p) return;
    var i=D.names.indexOf(p.y), j=D.names.indexOf(p.x); if(i>=0&&j>=0&&i!==j) show(i,j);}});
}}
show(D.start[0],D.start[1]); bind();
}})();</script>""" + domain_band_script(fig_id)


def domain_band_script(fig_id: str = "4.2") -> str:
    """Abbreviate a domain band label only when its full name does not fit its block (e.g. at 390 px)."""
    full = {d: A.DOMAIN_NAME[d] for d in A.DOMAIN_ORDER}
    return f"""<script>(function(){{
var FULL={json.dumps(full)}, ABBR={json.dumps(DOMAIN_ABBR)}, NBFT={len(A.bf_traits())}, busy=false;
function fit(gd){{
  if(busy||!gd._fullLayout) return; var L=gd._fullLayout, anns=gd.layout.annotations||[], upd={{}};
  anns.forEach(function(a,i){{
    if(!a.name||a.name.indexOf('domband|')!==0) return;
    var p=a.name.split('|'), kind=p[1], ax=p[2], d=p[3], cells=+p[4];
    var cellAxes = (kind==='facet' || kind==='bft');  // trait-level views sit on the first axis pair
    var axis = cellAxes ? (ax==='x'?L.xaxis:L.yaxis) : (ax==='x'?L.xaxis2:L.yaxis2);
    var ncat = kind==='facet' ? 26 : (kind==='bft' ? NBFT : 5), room = axis._length/ncat*cells - 4;
    var want = (FULL[d].length*6.0 <= room) ? FULL[d] : ABBR[d];   // ~6 px per character at 10 px
    if(a.text!==want) upd['annotations['+i+'].text']=want;
  }});
  if(Object.keys(upd).length){{ busy=true; Plotly.relayout(gd,upd).then(function(){{busy=false;}}); }}
}}
function bind(){{ var gd=document.getElementById('fig-{fig_id}'); if(!gd||!gd.on) return setTimeout(bind,60);
  gd.on('plotly_afterplot',function(){{fit(gd);}}); fit(gd); }}
bind();
}})();</script>"""


def largest_differences_html(top: int = 15, fmt: str = MAIN_FMT) -> str:
    p = A.pairs325().copy()
    q = p[_col(fmt)]
    p["gap"] = (q - p.human).abs()
    d = p.sort_values("gap", ascending=False).head(top)
    t = pd.DataFrame({"#": range(1, len(d) + 1), "Trait pair": d.label, "People": d.human, "Qwen": q.loc[d.index],
                      "Qwen − People": q.loc[d.index] - d.human})
    return R.table_html(t, caption=f"Largest people-vs-Qwen differences (top {top})", float_fmt="{:+.2f}", cls="phg-ranked")


# Figure E.5: one line per facet; the human benchmark sits on it, the two Qwen markers just above and below.
OFF_CAL, OFF_QWEN = -0.2, 0.2  # y axis is reversed: negative offsets draw above the facet line
CAL_BLUE, QWEN_VERM = "#1452a8", "#d55e00"
SERIES_43 = ("Human benchmark", "Qwen, calibrated", "Qwen")


def heldout_r2(fmt: str = MAIN_FMT) -> go.Figure:
    """Held-out R² per facet for one prompt format (scenario in the main text, survey-style in Appendix F): human
    benchmark, Qwen, and Qwen calibrated (one common multiplier per format)."""
    t = A.r2_table().set_index("facet").loc[list(A.ordered_codes())].reset_index()
    ys = np.arange(len(t))
    names = list(t.name)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t.R2_human, y=ys, mode="markers", name=SERIES_43[0], legendrank=1, visible=True,
                             marker=dict(symbol="diamond", size=9, color=HUM), customdata=np.column_stack([names, t.facet]),
                             hovertemplate="%{customdata[0]} (%{customdata[1]})<br>human benchmark R² %{x:+.3f}<extra></extra>"))
    rs = A.rescaled_table()
    rs = rs[rs.source == fmt].set_index("facet").loc[list(t.facet)]
    cd = np.column_stack([names, t.facet, t[f"extr_lo_{fmt}"], t[f"extr_hi_{fmt}"], t[f"resp_lo_{fmt}"], t[f"resp_hi_{fmt}"]])
    fig.add_trace(go.Scatter(  # drawn first, so the primary (calibrated) series sits on top
        x=t[f"R2_{fmt}"], y=ys + OFF_QWEN, mode="markers", visible=True, name=SERIES_43[2], legendrank=3,
        marker=dict(symbol="circle-open", size=8, color=QWEN_VERM, line=dict(width=1.5, color=QWEN_VERM)),
        error_x=dict(type="data", symmetric=False, array=t[f"extr_hi_{fmt}"] - t[f"R2_{fmt}"],
                     arrayminus=t[f"R2_{fmt}"] - t[f"extr_lo_{fmt}"], thickness=1, width=3, color=QWEN_VERM),
        customdata=cd, hovertemplate="%{customdata[0]} (%{customdata[1]})<br>Qwen R² %{x:+.3f}"
                                      "<br>prompt extraction 95%: [%{customdata[2]:+.3f}, %{customdata[3]:+.3f}]"
                                      "<br>test respondents 95%: [%{customdata[4]:+.3f}, %{customdata[5]:+.3f}]<extra></extra>"))
    cd = np.column_stack([names, t.facet, rs.q_lo, rs.q_hi, rs.resp_lo, rs.resp_hi, rs.original])
    fig.add_trace(go.Scatter(
        x=rs.rescaled, y=ys + OFF_CAL, mode="markers", visible=True, name=SERIES_43[1], legendrank=2,
        marker=dict(symbol="circle", size=9, color=CAL_BLUE, line=dict(width=1, color="white")),
        error_x=dict(type="data", symmetric=False, array=rs.q_hi - rs.rescaled, arrayminus=rs.rescaled - rs.q_lo,
                     thickness=2, width=4, color=CAL_BLUE),
        customdata=cd, hovertemplate="%{customdata[0]} (%{customdata[1]})<br>Qwen, calibrated R² %{x:+.3f} "
                                      "(Qwen %{customdata[6]:+.3f})<br>prompt extraction 95%: [%{customdata[2]:+.3f}, "
                                      "%{customdata[3]:+.3f}]<br>test respondents 95%: [%{customdata[4]:+.3f}, "
                                      "%{customdata[5]:+.3f}]<extra></extra>"))
    fr = A.S.csv("d30b_facet_results")
    m = A.rescaled_macro().set_index("source").loc[fmt]
    mh = fr[(fr.condition == "human_reference") & (fr.source == fmt)].R2.mean()
    iv = lambda lo, hi: f"[{lo:+.3f}, {hi:+.3f}]"
    nt = note(f"Average R² (95% interval from prompt extraction):<br>Human benchmark {mh:+.3f} (no saved interval)"
              f"<br>Qwen, calibrated {m.rescaled:+.3f} {iv(m.q_lo, m.q_hi)}<br>Qwen {m.as_measured:+.3f} {iv(m.am_q_lo, m.am_q_hi)}")
    # Same left domain band as 4.2 and E.2.
    shapes, band = left_domain_band(list(A.ordered_codes()), "pred")
    base_layout(fig, _ttl("How well Qwen's trait links predict real people's facet scores", fmt), height=930,
                note_lines=4, annotations=[nt] + band, b=125, l=OFF_ROWS + BAND_W + 10, shapes=shapes)
    fig.add_vline(x=0, line=dict(color="#999", width=1))
    fig.update_xaxes(title=dict(text="Prediction accuracy (R²; below 0 is worse<br>than guessing the average)", font=dict(size=12)),
                     range=[-1.45, 0.95])
    fig.update_yaxes(tickvals=list(ys), ticktext=names, autorange="reversed", tickfont=dict(size=10), range=[len(ys) - 0.4, -0.6],
                     automargin=False, showgrid=True, gridcolor="#eef0f3")
    return fig


FIG21_ORDER = [("qwen", "gemma"), ("qwen", "llama"), ("llama", "gemma")]  # iteration 27: Qwen–Gemma, Qwen–Llama, Llama–Gemma


def model_pairs_figure(bins: int = 160) -> go.Figure:
    """G.1 (was 2.1 until iteration 16): trait-pair correlations in one model against another, all 28,680 pairs of the 240 historical traits, drawn
    as density shading: a 160 x 160 2D histogram whose colour is the square root of the count, from white (no offset;
    empty cells transparent on the white plot). Individual points were tried and rejected (iteration 12): the bundled
    plotly.js has no WebGL scatter, and SVG points took 1.2 s per model-pair switch (2.8-5.5 s with 4x CPU throttling)."""
    edges = np.linspace(-1, 1, bins + 1)
    mids = (edges[:-1] + edges[1:]) / 2
    ag = A.model_pair_agreement().set_index(["a", "b"])
    foc = A.focal_hist_pairs()
    hists = {(a, b): np.histogram2d(A.hist_pair_cells(b), A.hist_pair_cells(a), bins=[edges, edges])[0] for a, b in FIG21_ORDER}
    cmax = float(max(H.max() for H in hists.values()))
    ticks = [c for c in [1, 5, 10, 20, 50, 100] if c <= cmax]
    fig = go.Figure()
    idx, notes, axes = {}, {}, {}
    for k, (a, b) in enumerate(FIG21_ORDER):
        x, y = A.hist_pair_cells(a), A.hist_pair_cells(b)
        H = hists[(a, b)]  # rows = y bins
        Z = np.where(H > 0, np.sqrt(H), np.nan).astype(np.float32)
        vis = k == 0
        la, lb = A.MODEL_LABEL[a], A.MODEL_LABEL[b]
        idx[(a, b)] = list(range(len(fig.data), len(fig.data) + 3))
        fig.add_trace(go.Heatmap(x=mids, y=mids, z=Z, customdata=H.astype(np.int16), colorscale=[[0, "#ffffff"], [1, "#08306b"]],
                                 zmin=0, zmax=float(np.sqrt(cmax)), showscale=(k == 0), visible=vis, hoverongaps=False,
                                 name="Trait pairs",
                                 colorbar=dict(orientation="h", thickness=8, len=0.5, x=1, xanchor="right", title_side="top",
                                               title=dict(text="Trait pairs per cell", font=dict(size=11)),
                                               tickvals=list(np.sqrt(ticks)), ticktext=[str(t) for t in ticks],
                                               tickfont=dict(size=10)),
                                 hovertemplate=la + " r %{x:+.2f}<br>" + lb + " r %{y:+.2f}<br>%{customdata} pairs<extra></extra>"))
        bf, slope, _ = trend_trace(x, y, visible=vis, showlegend=(k == 0), legendgroup="trend")
        fig.add_trace(bf)
        fig.add_trace(go.Scatter(x=foc[a], y=foc[b], mode="markers+text", text=foc.label, visible=vis,
                                 textposition=["bottom right", "top left", "top right"], showlegend=False,
                                 marker=dict(size=9, color=REV, line=dict(color="white", width=1)),
                                 textfont=dict(size=11, color="#111"), customdata=foc.label,
                                 hovertemplate="%{customdata}<br>" + la + " r %{x:+.3f}<br>" + lb + " r %{y:+.3f}<extra></extra>"))
        r = float(ag.loc[(a, b), "r"])
        notes[(a, b)] = f"agreement r = {two(r)} · {lb} links {slope:.2f}x as strong as {la}"
        axes[(a, b)] = {"xaxis.title.text": f"Correlation between the two traits in {la} (r)",
                        "yaxis.title.text": f"Correlation between the two traits in {lb} (r)"}
    fig.add_trace(go.Scatter(x=[-1, 1], y=[-1, 1], mode="lines", line=dict(color="#555", dash="dash", width=1), name=PERFECT,
                             hoverinfo="skip"))
    n = len(fig.data)
    buttons = [dict(label=f"{A.MODEL_LABEL[a]}–{A.MODEL_LABEL[b]}", method="update",
                    args=[{"visible": vis_mask(n, idx[(a, b)] + [n - 1])}, {"annotations": [note(notes[(a, b)])], **axes[(a, b)]}])
               for a, b in FIG21_ORDER]
    a0 = FIG21_ORDER[0]  # Qwen–Gemma on load
    base_layout(fig, "Trait correlations compared between models (r)", height=670, menus=[menu(buttons)], note_lines=1, b=135,
                annotations=[note(notes[a0])], plot_bgcolor="white")
    mg = fig.layout.margin
    fig.update_traces(selector=dict(type="heatmap"),
                      colorbar=dict(yref="paper", y=-(mg.b - 30) / (fig.layout.height - mg.t - mg.b), yanchor="bottom"))
    fig.update_xaxes(title=axes[a0]["xaxis.title.text"], range=[-1.02, 1.02], zeroline=True, zerolinecolor="#ccc", dtick=0.5,
                     showgrid=False, constrain="domain", autorange=False)
    fig.update_yaxes(title=axes[a0]["yaxis.title.text"], range=[-1.02, 1.02], zeroline=True, zerolinecolor="#ccc", dtick=0.5,
                     showgrid=False, scaleanchor="x", scaleratio=1, constrain="domain", autorange=False)
    return fig


def format_agreement_figure() -> go.Figure:
    """F.1 (was 3.2): per facet, the correlation between scenario- and survey-prompt scores across the 275 characters."""
    d = A.format_agreement()
    oc = list(d.facet)
    ys = np.arange(len(oc))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d.r, y=ys, mode="markers", name="Facet", showlegend=False,
                             marker=dict(symbol="circle", size=9, color=SCEN), customdata=np.column_stack([d.name, d.facet]),
                             hovertemplate="%{customdata[0]} (%{customdata[1]})<br>r between methods %{x:.3f}<extra></extra>"))
    med = float(np.median(d.r))
    lo = d.loc[d.r.idxmin()]
    shapes, anns = left_domain_band(oc, "agree", OFF_ROWS)
    shapes.append(dict(type="line", xref="x", x0=med, x1=med, yref="y domain", y0=0, y1=1, line=dict(color="#999", dash="dot", width=1)))
    two = lambda x: f"{x:.2f}".replace("0.", ".", 1)
    base_layout(fig, "Agreement between the two elicitation methods", height=720, note_lines=1, b=95,
                l=OFF_ROWS + BAND_W + 10, r=12, shapes=shapes,
                annotations=anns + [note(f"Median {two(med)} (dotted) · lowest {two(lo.r)} ({lo['name']})")])
    fig.update_xaxes(title="Correlation between scenario<br>and survey-style scores<br>across 275 characters (r)", range=[0.4, 1.02])
    fig.update_yaxes(tickvals=list(ys), ticktext=list(d.name), range=[len(ys) - 0.5, -0.5], tickfont=dict(size=10),
                     automargin=False, showgrid=False)
    return fig


def calibration_slider() -> go.Figure:
    c = A.calibration()
    facets = [f for f in A.ordered_codes() if f in set(c.facet)]
    ylab = [A.name(f) for f in facets]
    ks = np.round(np.arange(0, 1.2001, 0.02), 2)
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.13, row_heights=[0.55, 0.45],
                        subplot_titles=("Prediction accuracy (R²) at multiplier k", "Ordering agreement (S)"))
    curves = {}
    for fmt in A.FORMATS:
        cc = c[c.source == fmt].set_index("facet").loc[facets]
        curves[fmt] = np.array([stats.r2_curve(np.array([r.a, r.b, r.c]), r.SST, ks) for r in cc.itertuples()])
    k0 = int(np.where(ks == 1.0)[0][0])
    for fmt in A.FORMATS:
        fig.add_trace(go.Bar(x=curves[fmt][:, k0], y=ylab, orientation="h", name=f"Qwen, {fmt_name(fmt).replace(' prompts', '')}",
                             marker_color=FMT_COLOR[fmt], hovertemplate="%{y}<br>R² %{x:+.3f}<extra></extra>"), 1, 1)
    hr = c[c.source == "scenario"].set_index("facet").loc[facets].R2_human
    fig.add_trace(go.Scatter(x=hr, y=ylab, mode="markers", name="Human benchmark",
                             marker=dict(symbol="diamond", color=HUM, size=8)), 1, 1)
    S0 = {f: c[c.source == f].set_index("facet").loc[facets].S.to_numpy() for f in A.FORMATS}
    for fmt in A.FORMATS:
        fig.add_trace(go.Bar(x=S0[fmt], y=ylab, orientation="h", marker_color=FMT_COLOR[fmt], showlegend=False,
                             hovertemplate="%{y}<br>S %{x:+.3f}<extra></extra>"), 2, 1)
    lam = c.groupby("source").k_common.first()
    subt = [a.to_plotly_json() for a in fig.layout.annotations]

    def nt(k):
        mac = {f: curves[f][:, list(ks).index(k)].mean() for f in A.FORMATS}
        order = "S undefined at k = 0 (constant prediction)" if k == 0 else "S unchanged (k > 0 keeps ranks)"
        return [note(f"k = {k:.2f} · average R² scenario {mac['scenario']:+.3f}, survey-style {mac['survey_style']:+.3f}"
                     f"<br>{order}<br>Post hoc. Fitted λ: {lam['scenario']:.3f} scenario, {lam['survey_style']:.3f} survey-style",
                     yshift=26)] + subt
    steps = []
    for j, k in enumerate(ks):
        Sx = [S0[f] * (np.nan if k == 0 else 1) for f in A.FORMATS]
        steps.append(dict(label=f"{k:.2f}", method="update",
                          args=[{"x": [curves["scenario"][:, j], curves["survey_style"][:, j], hr.to_numpy(), Sx[0], Sx[1]]},
                                {"annotations": nt(k)}]))
    base_layout(fig, "Prediction accuracy (R²) and ordering (S) at multiplier k (earlier nine-facet experiment, illustrative)",
                height=900, note_lines=3,
                extra_top=22, annotations=nt(1.0), barmode="group", b=170)
    fig.update_layout(sliders=[dict(active=k0, steps=steps, currentvalue=dict(prefix="multiplier k = ", font=dict(size=12)),
                                    pad=dict(t=50), x=0, len=1, y=0, yanchor="top")])
    fig.update_xaxes(range=[-1.0, 0.85], row=1, col=1, title="Prediction accuracy (R²)")
    fig.update_xaxes(range=[0, 0.85], row=2, col=1, title="Ordering agreement (S)")
    fig.update_yaxes(tickfont=dict(size=10), autorange="reversed")
    return fig


# ================================================================ Section 5
def ctf_bars() -> go.Figure:
    d = A.ctf_contributions()
    order = list(d[(d.source == "scenario") & (d.geometry == "F")].sort_values("model_marginal_r", ascending=False).pair)
    fig = go.Figure()
    combos = [(g, MAIN_FMT) for g in ["F", "C", "T"]]
    idx = {}
    for g, f in combos:
        x = d[(d.geometry == g) & (d.source == f)].set_index("pair").loc[order]
        lab = [wrap_pair(a, b) for a, b in zip(x.left, x.right)]
        vis = (g, f) == ("F", "scenario")
        cd = np.column_stack([x.label, x.left + "–" + x.right])
        idx[(g, f)] = list(range(len(fig.data), len(fig.data) + 4))
        ht = "%{customdata[0]} (%{customdata[1]})<br>"
        fig.add_trace(go.Bar(x=x.projected_additive_contribution, y=lab, orientation="h", name="Five-dimension part",
                             marker_color="#4c6a92", visible=vis, customdata=cd, hovertemplate=ht + "projected %{x:+.3f}<extra></extra>"))
        fig.add_trace(go.Bar(x=x.residual_additive_contribution, y=lab, orientation="h", name="Remainder",
                             marker_color="#c9a227", visible=vis, customdata=cd, hovertemplate=ht + "residual %{x:+.3f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=x.model_marginal_r, y=lab, mode="markers", name="Qwen r (total)", visible=vis,
                                 marker=dict(symbol="line-ns-open", size=14, color="#000", line=dict(width=2)), customdata=cd,
                                 hovertemplate=ht + "Qwen r %{x:+.3f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=x.human_marginal_r, y=lab, mode="markers", name="People r", visible=vis,
                                 marker=dict(symbol="diamond", size=8, color=REV), customdata=cd,
                                 hovertemplate=ht + "people r %{x:+.3f}<extra></extra>"))
    n = len(fig.data)
    gname = {"F": "F (each model's factors)", "C": "D (shared directions)", "T": "T (Qwen trait PCA)"}
    glab = {"F": "F (factors)", "C": "D (shared)", "T": "T (Qwen PCA)"}
    buttons = [dict(label=glab[g], method="update", args=[{"visible": vis_mask(n, idx[(g, f)])}]) for g, f in combos]
    base_layout(fig, "Qwen r for each reversed pair: five-dimension part and remainder", height=760, menus=[menu(buttons)],
                barmode="relative", b=85)
    fig.add_vline(x=0, line=dict(color="#999", width=1))
    fig.update_xaxes(title="Contribution to Qwen's correlation (r)", range=[-1, 1])
    fig.update_yaxes(tickfont=dict(size=10), autorange="reversed")
    return fig


SCHEME_SHORT = {"exclude_semantic__": "− semantic: ", "exclude_legacy_canonical__": "− legacy family: ",
                "exclude_legacy_consensus__": "− consensus family: "}


def influence_figure() -> go.Figure:
    loo = A.loo_e1n2()
    grp = A.group_exclusions_e1n2()
    p = A.pairs325().set_index("pair").loc["E1__N2"]
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1, row_heights=[0.25, 0.75],
                        subplot_titles=("Leave one character out (275 each)", "Exclude one analytical group"))
    for f in [MAIN_FMT]:
        d = loo[loo.source == f]
        fig.add_trace(go.Box(x=d.r_without, y=["Qwen"] * len(d), orientation="h", boxpoints="all", jitter=0.5,
                             pointpos=0, marker=dict(size=4, color=FMT_COLOR[f]), line=dict(color=FMT_COLOR[f]),
                             fillcolor="rgba(0,0,0,0)", showlegend=False, customdata=np.column_stack([d.persona, d.change]),
                             hovertemplate="without <b>%{customdata[0]}</b>: r %{x:+.4f} (Δ %{customdata[1]:+.4f})<extra></extra>"), 1, 1)

    def short(c):
        for k, v in SCHEME_SHORT.items():
            c = c.replace(k, v)
        return c.replace("ordinary_human_roles", "only ordinary roles").replace("_", " ")
    for f in [MAIN_FMT]:
        d = grp[grp.source == f]
        fig.add_trace(go.Scatter(x=d.r, y=[f"{short(c)} ({n})" for c, n in zip(d.condition, d.n)], mode="markers",
                                 marker=dict(size=8, color=FMT_COLOR[f]), name="Qwen", showlegend=False,
                                 hovertemplate="%{y}<br>r %{x:+.3f}<extra></extra>"), 2, 1)
    for f in [MAIN_FMT]:
        for row in (1, 2):
            fig.add_vline(x=p[_col(f)], line=dict(color=FMT_COLOR[f], dash="dot", width=1), row=row, col=1)
    for row in (1, 2):
        fig.add_vline(x=p.human, line=dict(color=REV, width=1.5), row=row, col=1)
        fig.add_vline(x=0, line=dict(color="#999", width=1), row=row, col=1)
    subt = [a.to_plotly_json() for a in fig.layout.annotations]
    base_layout(fig, "Qwen's Friendliness–Anger correlation (r) with characters or groups left out", height=820, note_lines=2,
                extra_top=22,
                annotations=[note(f"Red line: people r {p.human:+.2f}. Dotted: Qwen r with all characters"
                                  f" ({p.scenario:+.2f}).<br>(n) = characters kept", yshift=26)] + subt, b=60)
    fig.update_xaxes(range=[-0.4, 1.0], title="Correlation between Friendliness and Anger in Qwen (r)", row=2, col=1)
    fig.update_xaxes(range=[-0.4, 1.0], row=1, col=1)
    fig.update_yaxes(tickfont=dict(size=9), row=2, col=1)
    return fig


def style_scatter() -> go.Figure:
    ids, _ = A.profiles()
    St = A.styles()
    formal = St[:, 0]
    conds = [("raw", None), ("conditioned on Formal", St[:, :1]), ("conditioned on five styles", St)]
    fig = go.Figure()
    idx, notes = {}, {}
    for f in [MAIN_FMT]:
        x0, y0 = A.e1n2(f)
        r_raw = stats.pearson(x0, y0)
        for cname, C in conds:
            rx, ry = stats.residualize(x0, C), stats.residualize(y0, C)
            zx, zy = rx / rx.std(), ry / ry.std()
            r = stats.pearson(rx, ry)
            vis = (f, cname) == ("scenario", "raw")
            idx[(f, cname)] = list(range(len(fig.data), len(fig.data) + 3))
            fig.add_trace(go.Scatter(
                x=zx, y=zy, mode="markers", visible=vis, name="Characters",
                marker=dict(size=6, color=formal, colorscale="Viridis", showscale=True,
                            colorbar=dict(title="Formal style score", orientation="h", yref="container", y=0.07, yanchor="bottom",
                                          thickness=10, len=0.7)),
                customdata=np.array(ids), hovertemplate="<b>%{customdata}</b><br>Friendliness %{x:+.2f}<br>Anger %{y:+.2f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=[-3, 3], y=[-3 * r, 3 * r], mode="lines", visible=vis, line=dict(color=FMT_COLOR[f], width=2.5),
                                     name=f"Best fit (r = {r:+.3f})",
                                     hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=[-3, 3], y=[-3 * r_raw, 3 * r_raw], mode="lines", visible=vis and C is not None,
                                     line=dict(color="#000", dash="dash", width=1.5),
                                     name=f"Original fit (r = {r_raw:+.3f})", hoverinfo="skip"))
            if C is None:
                notes[(f, cname)] = f"Raw: Qwen r = {r:+.3f}<br>People r = −0.280"
            else:
                vx, vy = stats.variance_removed(x0, C), stats.variance_removed(y0, C)
                notes[(f, cname)] = (f"{cname[0].upper() + cname[1:]}: r = {r:+.3f} (original {r_raw:+.3f})"
                                     f"<br>Variance removed: Friendliness {vx:.0%}, Anger {vy:.0%}")
    n = len(fig.data)
    short = {"raw": "Raw", "conditioned on Formal": "Formal", "conditioned on five styles": "5 styles"}

    def axes(cname):
        if cname == "raw":
            return {"xaxis.title.text": "Friendliness score (standardized, z)", "yaxis.title.text": "Anger score (standardized, z)"}
        return {"xaxis.title.text": "Friendliness score, style removed (standardized, z)",
                "yaxis.title.text": "Anger score, style removed (standardized, z)"}
    buttons = []
    for f in [MAIN_FMT]:
        for cname, C in conds:
            on = idx[(f, cname)] if C is not None else idx[(f, cname)][:2]
            buttons.append(dict(label=short[cname], method="update",
                                args=[{"visible": vis_mask(n, on)}, {"annotations": [note(notes[(f, cname)])], **axes(cname)}]))
    base_layout(fig, "Friendliness and Anger scores of 275 characters in Qwen", height=640, menus=[menu(buttons)], note_lines=2, b=150,
                annotations=[note(notes[("scenario", "raw")])])
    fig.update_xaxes(title=axes("raw")["xaxis.title.text"], range=[-3.2, 3.2], zeroline=True)
    fig.update_yaxes(title=axes("raw")["yaxis.title.text"], range=[-3.2, 3.2], zeroline=True)
    return fig


def item_columns_html() -> str:
    """Friendliness | Anger item wording side by side; reverse-keyed items marked."""
    it = A.S.csv("od_items")

    def col(code):
        d = it[it.facet_code == code].sort_values("item_number")
        return [f"{html.escape(w)}" + (" <span class='rk' title='reverse-keyed'>(R)</span>" if s < 0 else "")
                for w, s in zip(d.wording, d.original_response_sign)]
    a, b = col("E1"), col("N2")
    rows = "".join(f"<tr><td>{x}</td><td>{y}</td></tr>" for x, y in zip(a, b))
    return ("<div class='tablewrap'><table class='phg-table phg-items'><thead><tr><th>Friendliness</th><th>Anger</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div><p class='phg-small'>(R) reverse-keyed item. The source file stores these already "
            "reversed, so no further reversal is applied.</p>")


def anger_items_figure() -> go.Figure:
    d = A.anger_items().sort_values("anger_keyed_r_E1")
    lab = [f"{w}" + (" (R)" if s < 0 else "") for w, s in zip(d.wording, d.original_response_sign)]
    fac = A.S.csv("ha_facets").set_index(["outcome", "metric"]).anger_facet_r
    fig = go.Figure()
    for out, color, nm in [("E1", "#2f5d9a", "Friendliness"), ("E3", "#8e44ad", "Assertiveness")]:
        fig.add_trace(go.Scatter(
            x=d[f"anger_keyed_r_{out}"], y=lab, mode="markers", name=nm, marker=dict(size=9, color=color),
            error_x=dict(type="data", symmetric=False, array=d[f"simultaneous_95_upper_{out}"] - d[f"anger_keyed_r_{out}"],
                         arrayminus=d[f"anger_keyed_r_{out}"] - d[f"simultaneous_95_lower_{out}"], color=color, width=3),
            customdata=d.item_number, hovertemplate="item %{customdata}: %{y}<br>r %{x:+.3f}<extra>" + nm + "</extra>"))
        fig.add_vline(x=fac.loc[(out, "Pearson")], line=dict(color=color, dash="dot", width=1))
    fig.add_vline(x=0, line=dict(color="#999", width=1))
    base_layout(fig, "Correlation of each Anger item with Friendliness and with Assertiveness in people (r)", height=600,
                note_lines=2,
                annotations=[note("n = 117,259. (R) reverse-keyed. Dotted: whole-scale r."
                                  "<br>Bars: simultaneous 95%, 224-endpoint family.")], b=70)
    fig.update_xaxes(title="Correlation between the Anger item and the other trait in people (r)", range=[-0.5, 0.15])
    fig.update_yaxes(tickfont=dict(size=10))
    return fig


def anger_bands_figure() -> go.Figure:
    d = A.S.csv("ha_bins")
    fine = d[d.bin_kind == "fine"]
    broad = d[d.bin_kind == "broad"]
    names = {1: "low", 2: "moderate", 3: "high"}
    fig = go.Figure()
    for b in broad.itertuples():
        fig.add_trace(go.Scatter(
            x=[b.lower_inclusive, b.upper_exclusive], y=[b.mean_friendliness] * 2, mode="lines",
            line=dict(color="#9fb3cf", width=8), name="Average in each band", showlegend=bool(b.bin == 1), legendgroup="broad",
            hovertemplate=(f"{names[b.bin]} Anger [{b.lower_inclusive:g}, {b.upper_exclusive:g}{']' if b.upper_closed else ')'}"
                           f"<br>mean Friendliness {b.mean_friendliness:.3f}<br>simultaneous 95% "
                           f"[{b.simultaneous_mean_lower:.3f}, {b.simultaneous_mean_upper:.3f}]<br>n {b.n:,}<extra></extra>")))
    fig.add_trace(go.Scatter(
        x=fine.mean_anger, y=fine.mean_friendliness, mode="markers+lines", name="Half-point steps",
        marker=dict(size=7, color="#222"), line=dict(color="#222", width=1),
        error_y=dict(type="data", symmetric=False, array=fine.simultaneous_mean_upper - fine.mean_friendliness,
                     arrayminus=fine.mean_friendliness - fine.simultaneous_mean_lower, width=3),
        customdata=fine.n, hovertemplate="mean Anger %{x:.2f}<br>mean Friendliness %{y:.3f}<br>n %{customdata:,}<extra></extra>"))
    base_layout(fig, "Average Friendliness score at each level of Anger in people", height=490, note_lines=2,
                annotations=[note("n = 117,259 adults; scores are 1–5 item averages.<br>Bars: simultaneous 95%.")], b=95)
    for b in broad.itertuples():
        fig.add_annotation(x=(b.lower_inclusive + b.upper_exclusive) / 2, y=b.mean_friendliness, yshift=13, showarrow=False,
                           text=f"{names[b.bin]} {b.mean_friendliness:.2f}", font=dict(size=11, color="#4c6a92"))
    fig.update_xaxes(title="Anger score (1–5 item average)", range=[1, 5])
    fig.update_yaxes(title="Average Friendliness score (1–5)", range=[2.8, 4.0])
    return fig


def cross_model_figure() -> go.Figure:
    d = A.cross_model_table()
    rels = list(dict.fromkeys(d.relationship))
    models = ["Qwen", "Llama", "Gemma"]
    mcol = {"Qwen": "#2f5d9a", "Llama": "#c0392b", "Gemma": "#1f7a4d"}
    off = {"Qwen": -0.22, "Llama": 0.0, "Gemma": 0.22}
    fig = go.Figure()
    ypos = {r: i for i, r in enumerate(rels)}
    idx = {}
    for m in models:
        raw = d[(d.model == m) & (d.view == "raw")].set_index("relationship").loc[rels]
        fig.add_trace(go.Scatter(x=raw.adjusted_Pearson, y=[ypos[r] + off[m] for r in rels], mode="markers",
                                 name=f"{m}, raw", marker=dict(symbol="circle-open", size=10, color=mcol[m], line=dict(width=2)),
                                 error_x=dict(type="data", symmetric=False, array=raw.upper - raw.adjusted_Pearson,
                                              arrayminus=raw.adjusted_Pearson - raw.lower, color=mcol[m], thickness=1),
                                 customdata=rels, hovertemplate="%{customdata}<br>" + m + " raw r %{x:+.3f}<extra></extra>"))
    for view in ["conditioned on Formal", "conditioned on five styles"]:
        idx[view] = []
        for m in models:
            c = d[(d.model == m) & (d.view == view)].set_index("relationship").loc[rels]
            idx[view].append(len(fig.data))
            fig.add_trace(go.Scatter(x=c.adjusted_Pearson, y=[ypos[r] + off[m] for r in rels], mode="markers",
                                     name=f"{m}, {'Formal' if view.endswith('Formal') else '5 styles'} removed", visible=False, marker=dict(symbol="circle", size=8, color=mcol[m]),
                                     error_x=dict(type="data", symmetric=False, array=c.upper - c.adjusted_Pearson,
                                                  arrayminus=c.adjusted_Pearson - c.lower, color=mcol[m], thickness=2),
                                     customdata=rels, hovertemplate="%{customdata}<br>" + m + f" {view} r %{{x:+.3f}}<extra></extra>"))
    n = len(fig.data)
    ttl0 = "Correlations between historical traits in Qwen, Llama and Gemma (r)"
    buttons = [dict(label="Raw", method="update", args=[{"visible": vis_mask(n, [0, 1, 2])}])]
    for view in idx:
        buttons.append(dict(label="Raw + " + ("Formal" if view.endswith("Formal") else "5 styles"), method="update",
                            args=[{"visible": vis_mask(n, [0, 1, 2] + idx[view])}]))
    base_layout(fig, ttl0, height=640, menus=[menu(buttons)],
                note_lines=2, b=130, annotations=[note("275 characters, historical trait readouts (not IPIP facets)."
                                                        "<br>Bars: character-bootstrap 95%.")])
    fig.add_vline(x=0, line=dict(color="#999", width=1))
    fig.update_yaxes(tickvals=list(range(len(rels))), ticktext=[r.replace(" – ", " –<br>") for r in rels],
                     autorange="reversed", tickfont=dict(size=10))
    fig.update_xaxes(title="Correlation between the two traits (r, oriented)", range=[-1, 1])
    return fig


FOCAL_TRAITS = ["hostile", "charismatic", "nurturing", "flirty", "avoidant", "gregarious"]


def factor_pattern_figure(n_label: int = 6) -> go.Figure:
    w = A.factor_patterns()
    fig = go.Figure()
    comps = [("Llama_F1", "Llama F1"), ("Gemma_F3", "Gemma F3")]
    idx, notes = {}, {}
    for k, (col, lab) in enumerate(comps):
        x, y = w["Qwen_F1"], w[col]
        diff = (y - x).abs()
        disagree = ((np.sign(x) != np.sign(y)) & (x.abs() >= 0.3) & (y.abs() >= 0.3)) | (diff >= 0.6)
        top = set(diff[disagree].sort_values(ascending=False).index[:n_label]) | set(FOCAL_TRAITS)
        vis = k == 0
        idx[col] = list(range(len(fig.data), len(fig.data) + 4))
        fig.add_trace(go.Scatter(x=x[~disagree], y=y[~disagree], mode="markers", visible=vis, name="Traits (240)",
                                 marker=dict(size=5, color=OTH), customdata=x[~disagree].index,
                                 hovertemplate="%{customdata}<br>Qwen F1 %{x:+.3f}<br>" + lab + " %{y:+.3f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=x[disagree], y=y[disagree], mode="markers", visible=vis,
                                 name="Traits that disagree", marker=dict(size=7, color=REV),
                                 customdata=x[disagree].index,
                                 hovertemplate="%{customdata}<br>Qwen F1 %{x:+.3f}<br>" + lab + " %{y:+.3f}<extra></extra>"))
        L = [t for t in w.index if t in top]
        fig.add_trace(go.Scatter(x=x[L], y=y[L], mode="markers+text", text=L, textposition="top center", visible=vis,
                                 marker=dict(size=9, symbol="circle-open", color="#000"),
                                 textfont=dict(size=10, color="#000"), showlegend=False, hoverinfo="skip"))
        bf, slope, _ = trend_trace(x, y, visible=vis, showlegend=(k == 0), legendgroup="trend")
        fig.add_trace(bf)
        notes[col] = (f"Qwen F1 vs {lab}: pattern congruence {A.factor_congruence('Qwen_F1', col):+.2f}"
                      f"<br>agreement r = {two(stats.pearson(x, y))} · {int(disagree.sum())} traits disagree"
                      f"<br>{lab} links {slope:.2f}x as strong as Qwen F1"
                      "<br>Disagree: opposite signs with both |r| ≥ 0.3, or a gap ≥ 0.6")
    fig.add_trace(go.Scatter(x=[-1, 1], y=[-1, 1], mode="lines", line=dict(dash="dash", color="#555", width=1),
                             name=PERFECT, hoverinfo="skip"))
    n = len(fig.data)
    buttons = [dict(label=lab, method="update",
                    args=[{"visible": vis_mask(n, idx[col] + [n - 1])},
                          {"annotations": [note(notes[col])], "yaxis.title.text": f"Correlation of each trait with {lab} (r)"}])
               for col, lab in comps]
    base_layout(fig, "Each trait's correlation with Qwen F1 and with the matching factor in another model (r)", height=620, menus=[menu(buttons)], note_lines=4, b=105,
                annotations=[note(notes["Llama_F1"])])
    fig.update_xaxes(title="Correlation of each trait with Qwen F1 (r)", range=[-1.05, 1.05])
    fig.update_yaxes(title="Correlation of each trait with Llama F1 (r)", range=[-1.05, 1.05])
    return fig


# ================================================================ Appendix G (iteration 14)
def persona_agreement_figure() -> go.Figure:
    """G.2: per trait, r of the 275 character scores between two models; one strip per model pair, median marked."""
    d = A.persona_score_agreement()
    fig = go.Figure()
    rng = np.random.default_rng(20261105)  # fixed vertical jitter for display only
    labels = []
    for k, (a, b) in enumerate(A.MODEL_PAIRS):
        g = d[(d.a == a) & (d.b == b)]
        lab = f"{A.MODEL_LABEL[a]}–{A.MODEL_LABEL[b]}"
        labels.append(lab)
        fig.add_trace(go.Scatter(x=g.r, y=k + rng.uniform(-0.28, 0.28, len(g)), mode="markers", name="Trait", showlegend=(k == 0),
                                 marker=dict(size=5, color=SCEN, opacity=0.45), customdata=g.trait,
                                 hovertemplate="%{customdata}<br>" + lab + " r %{x:+.3f}<extra></extra>"))
        med = float(g.r.median())
        fig.add_trace(go.Scatter(x=[med, med], y=[k - 0.38, k + 0.38], mode="lines", name="Median", showlegend=(k == 0),
                                 line=dict(color="#111", width=3), hoverinfo="skip"))
        fig.add_annotation(x=med, y=k - 0.38, yanchor="bottom", yshift=-2, xanchor="right", xshift=-4, showarrow=False,
                           text=f"median {two(med)}", font=dict(size=11, color="#111"))
    base_layout(fig, "Agreement of character scores between models, per trait (r)", height=420, b=95, l=95)
    fig.add_vline(x=0, line=dict(color="#999", width=1))
    fig.update_xaxes(title="Correlation of a trait's 275 character scores<br>between the two models (r)", range=[-0.2, 1.02])
    fig.update_yaxes(tickvals=list(range(3)), ticktext=labels, range=[2.6, -0.6], showgrid=False)
    return fig


def pc_heatmap_figure() -> go.Figure:
    """Figure 2.1 (iteration 16; was G.3): saved signed r between Qwen PC1-6 (rows) and the other model's PC1-6
    (columns), one heatmap with a menu (Qwen–Gemma first, then Qwen–Llama) that also updates the x-axis title."""
    ticks = [f"PC{i}" for i in range(1, 6)]
    order = ["gemma", "llama"]
    fig = go.Figure()
    for k, m in enumerate(order):
        Z = A.pc_correspondence(m)[:5, :5]  # iteration 25: PC1-PC5 only
        txt = [[f"{v:+.2f}".replace("-", "−") for v in r] for r in Z]
        fig.add_trace(go.Heatmap(z=Z, x=ticks, y=ticks, colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0, text=txt,
                                 texttemplate="%{text}", textfont=dict(size=12), visible=(k == 0), xgap=1, ygap=1,
                                 colorbar=dict(thickness=10, len=0.8, title=dict(text="r", side="top")),
                                 hovertemplate="Qwen %{y} vs " + A.MODEL_LABEL[m] + " %{x}: r %{z:+.3f}<extra></extra>"))
    xt = {m: f"{A.MODEL_LABEL[m]}'s activation axes" for m in order}
    buttons = [dict(label=f"Qwen–{A.MODEL_LABEL[m]}", method="update",
                    args=[{"visible": [i == k for i in range(len(order))]}, {"xaxis.title.text": xt[m]}])
               for k, m in enumerate(order)]
    base_layout(fig, "Correlation between the models' main activation axes (r)", height=520, menus=[menu(buttons)], b=60, l=60)
    fig.update_xaxes(title=xt["gemma"], side="bottom")
    fig.update_yaxes(title="Qwen's activation axes", autorange="reversed")
    return fig


def pc1_scatter_figure() -> go.Figure:
    """G.3b: the 275 characters, Qwen PC1 against the other model's PC1 (menu, Qwen–Gemma first)."""
    from . import landscape as LS
    P = LS.persona_order()
    q = LS.pcs("qwen").loc[P, "pc1"].to_numpy(float)
    fig = go.Figure()
    order = ["gemma", "llama"]
    notes = {}
    for k, m in enumerate(order):
        y = LS.pcs(m).loc[P, "pc1"].to_numpy(float)
        fig.add_trace(go.Scatter(x=q, y=y, mode="markers", visible=(k == 0), name="Character", showlegend=False,
                                 marker=dict(size=6, color=SCEN, opacity=0.6), customdata=P,
                                 hovertemplate="%{customdata}<br>Qwen PC1 %{x:+.2f}<br>" + A.MODEL_LABEL[m] + " PC1 %{y:+.2f}<extra></extra>"))
        notes[m] = f"r = {two(stats.pearson(q, y))} (saved: {two(A.pc_correspondence(m)[0, 0])})"
    buttons = [dict(label=f"Qwen–{A.MODEL_LABEL[m]}", method="update",
                    args=[{"visible": [i == k for i in range(len(order))]},
                          {"annotations": [note(notes[m])], "yaxis.title.text": f"Position on {A.MODEL_LABEL[m]}'s PC1"}])
               for k, m in enumerate(order)]
    base_layout(fig, "Characters on Qwen's first activation axis and another model's", height=560, menus=[menu(buttons)],
                note_lines=1, b=70, annotations=[note(notes["gemma"])])
    fig.update_xaxes(title="Position on Qwen's PC1", zeroline=True, zerolinecolor="#ccc")
    fig.update_yaxes(title="Position on Gemma's PC1", zeroline=True, zerolinecolor="#ccc")
    return fig


def factor_match_figure() -> go.Figure:
    """G.4: AA17 factor-to-factor Tucker congruence per model pair (PHG-CM01 original pattern), matched pairs outlined."""
    fig = go.Figure()
    shapes_by, notes = {}, {}
    pairs = A.MODEL_PAIRS  # iteration 27 order
    for k, (a, b) in enumerate(pairs):
        fa, fb, C, Mk = A.factor_match_matrix(a, b)
        xs = [f.split("_")[1] for f in fb]
        ys = [f.split("_")[1] for f in fa]
        txt = [[f"{v:+.2f}".replace("-", "−") for v in r] for r in C]
        fig.add_trace(go.Heatmap(z=C, x=xs, y=ys, colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0, text=txt,
                                 texttemplate="%{text}", textfont=dict(size=11), visible=(k == 0), xgap=1, ygap=1,
                                 showscale=(k == 0), name="Congruence",
                                 colorbar=dict(orientation="h", thickness=8, len=0.6, title=dict(text="Congruence", side="top")),
                                 hovertemplate=A.MODEL_LABEL[a] + " %{y} vs " + A.MODEL_LABEL[b] + " %{x}: %{z:+.3f}<extra></extra>"))
        shapes_by[(a, b)] = [dict(type="rect", xref="x", yref="y", x0=j - 0.5, x1=j + 0.5, y0=i - 0.5, y1=i + 0.5,
                                  line=dict(color="#111", width=2.5)) for i in range(len(fa)) for j in range(len(fb)) if Mk[i, j]]
        mabs = np.abs(C[Mk])
        notes[(a, b)] = f"Matched pairs (outlined): |congruence| {two(mabs.min())} to {two(mabs.max())}"
    buttons = [dict(label=f"{A.MODEL_LABEL[a]}–{A.MODEL_LABEL[b]}", method="update",
                    args=[{"visible": [i == k for i in range(len(pairs))]},
                          {"shapes": shapes_by[(a, b)], "annotations": [note(notes[(a, b)])],
                           "xaxis.title.text": f"{A.MODEL_LABEL[b]} factor", "yaxis.title.text": f"{A.MODEL_LABEL[a]} factor"}])
               for k, (a, b) in enumerate(pairs)]
    p0 = pairs[0]
    base_layout(fig, "Matching each model's factors to another model's (Tucker congruence)", height=560, menus=[menu(buttons)],
                note_lines=1, b=130, l=60, shapes=shapes_by[p0], annotations=[note(notes[p0])])
    mg = fig.layout.margin
    fig.update_traces(selector=dict(type="heatmap"), colorbar=dict(yref="paper", y=-(mg.b - 8) / (560 - mg.t - mg.b), yanchor="bottom"))
    fig.update_xaxes(title=f"{A.MODEL_LABEL[p0[1]]} factor", side="bottom", type="category")
    fig.update_yaxes(title=f"{A.MODEL_LABEL[p0[0]]} factor", autorange="reversed", type="category")
    return fig


# ------------------------------------------------------------ Iteration 15: Appendix F.2 table (replaces Figures F.2–F.4)
def format_results_table_html() -> str:
    """Side-by-side headline results for the two prompt methods, each row linking to the body figure that shows it."""
    d = A.format_results()
    sc, sv = d.loc["scenario"], d.loc["survey_style"]
    link = lambda k, t: f"<a href='#wrap-{k}'>{t}</a>"
    rows = [
        ("Agreement with people's trait-pair pattern (r)", f"{sc.pattern_r:.3f}", f"{sv.pattern_r:.3f}", link("H", "Figure 4.1")),
        ("Pairs with the same direction as people", f"{sc.same_sign:.0%}", f"{sv.same_sign:.0%}", link("H", "Figure 4.1")),
        ("Spread ratio, Qwen vs people (trend slope)", f"{sc.spread:.2f}", f"{sv.spread:.2f}", link("H", "Figure 4.1")),
        ("Reversals and close matches (frozen screen, uses both methods)", f"{int(sc.n_reversal)} and {int(sc.n_close)}",
         f"{int(sv.n_reversal)} and {int(sv.n_close)}", link("H", "Figure 4.1")),
        ("Trait correlation matrix", "Figure 4.2", "values in the pairs table below", link("4.2", "Figure 4.2")),
        ("Average prediction R², as measured", f"{sc.r2_measured:.3f}", f"{sv.r2_measured:.3f}", link("4.3", "Figure E.6")),
        ("Average prediction R², after common rescaling", f"{sc.r2_rescaled:.3f}", f"{sv.r2_rescaled:.3f}", link("4.3", "Figure E.6")),
        ("Common rescaling multiplier", f"{sc.multiplier:.3f}", f"{sv.multiplier:.3f}", link("4.3", "Figure E.6")),
    ]
    head = "".join(f"<th>{t}</th>" for t in ["Measure", "Main text (scenario)", "Survey-style", "Shown in"])
    body = "".join("<tr>" + "".join(f"<td>{html.escape(c) if i < 3 else c}</td>" for i, c in enumerate(r)) + "</tr>"
                   for r in rows)
    return (f"<div class='tablewrap' id='table-F.2'><table class='phg-table'><thead><tr>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table></div>")


# ------------------------------------------------------------ Iteration 18: Figure 2.2
def consensus_pc_figure() -> go.Figure:
    """Figure 2.2: r between each model's scores on the consensus directions C1-C5 (rows) and its activation PC1-6
    (columns), one heatmap with a model menu (Qwen, Gemma, Llama)."""
    ticks = [f"PC{i}" for i in range(1, 6)]  # iteration 25: PC1-PC5 only
    ylab = [f"{A.dlab(c)} · {A.CONSENSUS_LABEL[c][1]}" for c in A.CONSENSUS]  # iteration 19: short meaning on the axis
    order = ["qwen", "gemma", "llama"]
    fig = go.Figure()
    for k, m in enumerate(order):
        Z = A.consensus_pc_corr(m)
        txt = [[f"{v:+.2f}".replace("-", "−") for v in r] for r in Z]
        fig.add_trace(go.Heatmap(z=Z, x=ticks, y=ylab, colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0, text=txt,
                                 texttemplate="%{text}", textfont=dict(size=12), visible=(k == 0), xgap=1, ygap=1,
                                 colorbar=dict(thickness=10, len=0.8, title=dict(text="r", side="top")),
                                 hovertemplate="%{y} vs " + A.MODEL_LABEL[m] + " %{x}: r %{z:+.3f}<extra></extra>"))
    xt = {m: f"{A.MODEL_LABEL[m]}'s activation axes" for m in order}
    buttons = [dict(label=A.MODEL_LABEL[m], method="update",
                    args=[{"visible": [i == k for i in range(len(order))]}, {"xaxis.title.text": xt[m]}])
               for k, m in enumerate(order)]
    base_layout(fig, "Shared directions and each model's main activation axes (r)", height=460, menus=[menu(buttons)],
                b=60, l=170)
    fig.update_xaxes(title=xt["qwen"], side="bottom")
    fig.update_yaxes(title="Shared direction", autorange="reversed")
    return fig


def consensus_key_html() -> str:
    """Iteration 19: key to C1-C5 shown above Figure 2.2: AA18's candidate meaning, the traits at each end, the matching
    activation axis per model (largest |r| in Figure 2.2) and AA19's human status."""
    k = A.consensus_key()
    fmt = lambda pc, r: f"PC{pc} ({r:+.2f})".replace("-", "−")
    head = "".join(f"<th>{t}</th>" for t in ["", "Candidate meaning", "High end", "Low end", "Qwen", "Gemma", "Llama",
                                              "In people (Section 3)"])
    body = "".join(
        "<tr>" + f"<td><b>{A.dlab(r.component)}</b></td><td><b>{html.escape(r.label)}</b></td><td>{html.escape(r.high)}</td>"
        f"<td>{html.escape(r.low)}</td>"
        + "".join(f"<td class='{'kweak' if abs(getattr(r, m + '_r')) < 0.6 else ''}'>{fmt(getattr(r, m + '_pc'), getattr(r, m + '_r'))}</td>"
                  for m in ["qwen", "gemma", "llama"])
        + f"<td>{html.escape(r.human)}</td></tr>" for r in k.itertuples())
    return ("<style>.phg-ckey td.kweak{color:#8a94a3}.phg-ckey td{font-size:13px}</style>"
            "<p class='phg-listhead' id='consensus-key'>Key to the shared directions</p>"
            f"<div class='tablewrap phg-ckey' id='table-ckey'><table class='phg-table'><thead><tr>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table></div>"
            "<p class='phg-small'>Meanings are candidate readings of the traits loading most strongly at each end; "
            "they are descriptions of the trait scores, not demonstrated human personality dimensions. Model columns give "
            "the activation axis each direction matches best in Figure 2.3, with its r; the sign only says which end of the "
            "axis is which (for example, characters high on Qwen's PC1 sit at the factual, moderate end of D1). Grey: under "
            ".6, so the direction is spread over several axes.</p>")


# ------------------------------------------------------------ Iteration 20: Figures 2.3 and 3.1
def _signed(v: float) -> str:
    return f"{v:+.2f}".replace("-", "−")


def factor_pc_figure() -> go.Figure:
    """Figure E.4 (was 1.2 in iteration 20): r between each model's own AA17 factors (rows) and its activation PC1-6 (columns), model menu
    (Qwen, Gemma, Llama). Hover gives the share of each factor that PC1-6 explain together."""
    ticks = [f"PC{i}" for i in range(1, 7)]
    order = ["qwen", "gemma", "llama"]
    fig = go.Figure()
    for k, m in enumerate(order):
        Z = A.factor_pc_corr(m)
        r2 = A.factor_pc_r2(m)
        ylab = [f"F{i + 1} · {A.FACTOR_LABEL[f'F{i + 1}']}" if m == "qwen" else f"{A.MODEL_LABEL[m]} F{i + 1}" for i in range(len(Z))]
        fig.add_trace(go.Heatmap(z=Z, x=ticks, y=ylab, colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0,
                                 text=[[_signed(v) for v in r] for r in Z], texttemplate="%{text}", textfont=dict(size=12),
                                 visible=(k == 0), xgap=1, ygap=1, customdata=[[x] * 6 for x in r2],
                                 colorbar=dict(thickness=10, len=0.8, title=dict(text="r", side="top")),
                                 hovertemplate="%{y} vs %{x}: r %{z:+.3f}<br>PC1–PC6 together explain %{customdata:.0%} of this factor<extra></extra>"))
    xt = {m: f"{A.MODEL_LABEL[m]}'s activation axes" for m in order}
    buttons = [dict(label=A.MODEL_LABEL[m], method="update", args=[{"visible": [i == k for i in range(len(order))]},
                                                                    {"xaxis.title.text": xt[m]}])
               for k, m in enumerate(order)]
    base_layout(fig, "Each model's own trait factors and its main activation axes (r)", height=480, menus=[menu(buttons)],
                b=60, l=190)
    fig.update_xaxes(title=xt["qwen"])
    fig.update_yaxes(title="Trait factors (AA17)", autorange="reversed")
    return fig


def factor_key_html() -> str:
    """Key to Qwen's AA17 factors (Figure E.4): short reading, top-3 traits at each end, the activation axis each factor
    correlates with most."""
    k = A.factor_poles()
    Z = A.factor_pc_corr("qwen")
    head = "".join(f"<th>{t}</th>" for t in ["", "Short reading", "High end", "Low end", "Strongest activation axis"])
    body = ""
    for i, r in enumerate(k.itertuples()):
        j = int(np.argmax(np.abs(Z[i])))
        cls = " class='kweak'" if abs(Z[i, j]) < 0.6 else ""
        body += (f"<tr><td><b>{r.factor}</b></td><td><b>{html.escape(r.label)}</b></td><td>{html.escape(r.high)}</td>"
                 f"<td>{html.escape(r.low)}</td><td{cls}>PC{j + 1} ({_signed(Z[i, j])})</td></tr>")
    return ("<style>.phg-ckey td.kweak{color:#8a94a3}.phg-ckey td{font-size:13px}</style>"
            "<p class='phg-listhead' id='factor-key'>Key to Qwen's own factors</p>"
            f"<div class='tablewrap phg-ckey' id='table-fkey'><table class='phg-table'><thead><tr>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table></div>"
            "<p class='phg-small'>Traits at each end are the three historical traits most correlated with the factor score "
            "across the 275 characters (Oct 26 study). The short readings are ours, not validated names. Grey: under .6, so "
            "the factor mixes several activation axes.</p>")


def facets_geometry_figure() -> go.Figure:
    """Figure 3.2 (3.1 in iterations 20-28): Qwen's 26 facets (rows, by domain) against five directions; menu: consensus C1-C5 (default) or Qwen's
    activation axes PC1-PC5 (Qwen's factors F1-F5 were a third view until iteration 21; now Appendix E.4). Hover gives the share of each facet the five explain together."""
    order = list(A.ordered_codes())
    ylab = [A.name(f) for f in order]
    cp = A.consensus_pc_corr("qwen")
    xs = {"C": [f"<b>{A.dlab(c)}</b><br>{A.CONSENSUS_LABEL[c][1]}" for c in A.CONSENSUS],
          "F": [f"<b>F{k}</b><br>{A.FACTOR_LABEL[f'F{k}']}" for k in range(1, 6)],
          "PC": [f"<b>PC{k + 1}</b><br>≈ {A.dlab(A.CONSENSUS[int(np.argmax(np.abs(cp[:, k])))])} "
                 f"(r {_signed(cp[int(np.argmax(np.abs(cp[:, k]))), k])})" for k in range(5)]}
    what = {"C": "D1–D5", "PC": "PC1–PC5"}
    views = ["C", "PC"]  # iteration 21: Qwen's factors moved to Appendix E.4
    fig = go.Figure()
    for k, v in enumerate(views):
        Z, r2 = A.facet_direction_matrix(v)
        fig.add_trace(go.Heatmap(z=Z, x=xs[v], y=ylab, colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0,
                                 text=[[_signed(x) for x in row] for row in Z], texttemplate="%{text}", textfont=dict(size=11),
                                 visible=(k == 0), xgap=1, ygap=1, customdata=[[r] * 5 for r in r2],
                                 colorbar=dict(thickness=10, len=0.6, title=dict(text="r", side="top")),
                                 hovertemplate="%{y}<br>r %{z:+.3f}<br>" + what[v]
                                 + " together explain %{customdata:.0%} of this facet<extra></extra>"))
    labels = {"C": "Shared directions D1–D5", "PC": "Qwen's activation axes PC1–PC5"}
    buttons = [dict(label=labels[v], method="update", args=[{"visible": [i == k for i in range(len(views))]}])
               for k, v in enumerate(views)]
    base_layout(fig, "Qwen's facets and its main directions (r)", height=880, b=30, l=225, menus=[menu(buttons)])
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=11))
    fig.update_xaxes(side="top", tickfont=dict(size=11), tickangle=0)
    DN = {"N": "Neuroticism", "E": "Extraversion", "O": "Openness", "A": "Agreeableness", "C": "Conscientiousness"}
    doms = [f[0] for f in order]
    starts = [i for i in range(len(order)) if i == 0 or doms[i] != doms[i - 1]] + [len(order)]
    shapes, ann = [], []
    for a, b in zip(starts[:-1], starts[1:]):
        if a:
            shapes.append(dict(type="line", xref="paper", x0=-0.29, x1=1, yref="y", y0=a - 0.5, y1=a - 0.5,
                               line=dict(color="#1d2430", width=1.5)))
        ann.append(dict(xref="paper", x=-0.27, y=(a + b - 1) / 2, yref="y", text=DN[doms[a]], textangle=-90, showarrow=False,
                        font=dict(size=11, color="#5b6b82")))
    fig.update_layout(shapes=shapes, annotations=list(fig.layout.annotations) + ann, margin=dict(t=150))
    fig.layout.updatemenus[0].update(y=1.10, yanchor="bottom", x=0, xanchor="left")
    return fig


def phone_compact_script(fig_id: str, left: int, short_y: bool = True) -> str:
    """Iteration 20: below 600 px, shorten heatmap axis labels to their codes ("C1 · charged vs moderate" -> "C1",
    "<b>PC1</b><br>≈ C1 ..." -> "PC1"), shrink cell text, hide the colour bar and the rotated domain labels, and narrow
    the left margin. The full labels stay in the keys, hover text and wide layouts."""
    return ("<script>(function(){var g=document.getElementById('fig-" + fig_id + "');"
            "function go(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(go,80);}"
            "if(window.innerWidth>=600)return;"
            "var sx=function(s){return String(s).replace(/<[^>]+>/g,' ').trim().split(/\\s+/)[0];};"
            "var sy=function(s){return String(s).split(' · ')[0];};"
            "var u={x:g.data.map(function(t){return t.x.map(sx);}),'textfont.size':9,showscale:false};"
            + ("u.y=g.data.map(function(t){return t.y.map(sy);});" if short_y else "")
            + "Plotly.restyle(g,u).then(function(){var a=(g.layout.annotations||[]).filter(function(n){return n.textangle!==-90;});"
            "Plotly.relayout(g,{'margin.l':" + str(left) + ",'margin.r':8,annotations:a,'xaxis.tickangle':0,'xaxis.tickfont.size':10});});}"
            "go();})();</script>")


# ------------------------------------------------------------ Iteration 21: Figure 1.2 (what the main axes separate)
def pc_trait_map_figure() -> go.Figure:
    """Figure 1.1 (1.2 in iterations 21-26): characters on a model's PC1 (across) and PC2 or PC3 (up), coloured by one trait's score
    (standardized within the model). The three menus (model, vertical axis, trait) are HTML controls added by
    pc_trait_map_script(), because the trait list depends on the model and axis. The initial view is Qwen, PC2,
    transparent."""
    from . import landscape as LS
    P = LS.persona_order()
    pcs = LS.pcs("qwen").loc[P]
    x, y = pcs.pc1.to_numpy(float), pcs.pc2.to_numpy(float)
    t = A.trait_matrix("qwen")
    tr = A.pc_map_options("qwen", "PC2")[0][0]
    v = t[tr].to_numpy()
    z = (v - v.mean()) / v.std()
    r = A.trait_pc_corr("qwen")
    sg = lambda q: (f"{q:+.2f}").replace("0.", ".").replace("-", "−")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers", showlegend=False, customdata=P, name="Characters",
                             marker=dict(size=8, color=z, colorscale=PEARSON_SCALE, cmin=-2.2, cmax=2.2,
                                         line=dict(color="white", width=0.5),
                                         colorbar=dict(thickness=10, len=0.7, title=dict(text="Trait score", side="top"),
                                                       tickvals=[-2, 0, 2], ticktext=["low", "average", "high"])),
                             hovertemplate="%{customdata}<br>" + tr + " %{marker.color:+.2f} SD<extra></extra>"))
    idx = [P.index(n) for n in A.PC_MAP_NAMES]
    fig.add_trace(go.Scatter(x=x[idx], y=y[idx], mode="text", text=A.PC_MAP_NAMES, textposition="top right",
                             textfont=dict(size=10, color="#1d2430",
                                           # Iteration 38: white halo so names read over the dense factual-end cluster.
                                           shadow="0 0 2px #fff, 0 0 3px #fff, 0 0 4px #fff"),
                             hoverinfo="skip", showlegend=False, name="Names"))
    note0 = f"r with PC1 {sg(r.loc[tr, 'PC1'])} · PC2 {sg(r.loc[tr, 'PC2'])} · PC3 {sg(r.loc[tr, 'PC3'])}"
    base_layout(fig, "Characters on each model's activation axes, coloured by one trait", height=580, note_lines=1,
                b=60, annotations=[note(note0)])
    fig.update_xaxes(title="Position on Qwen's PC1", zeroline=True, zerolinecolor="#ddd")
    fig.update_yaxes(title="Position on Qwen's PC2", zeroline=True, zerolinecolor="#ddd")
    return fig


def pc_trait_map_payload() -> dict:
    """Data for the Figure 1.1 controls: per model, PC1-PC3 positions, the standardized scores and r (PC1-PC3) of every
    trait that appears in its menus, and the menu options per vertical axis."""
    from . import landscape as LS
    P = LS.persona_order()
    idx = [P.index(n) for n in A.PC_MAP_NAMES]
    out = {"names": A.PC_MAP_NAMES, "idx": idx, "label": {m: A.MODEL_LABEL[m] for m in A.PC_MAP_MODELS}, "models": {}}
    for m in A.PC_MAP_MODELS:
        pcs = LS.pcs(m).loc[P]
        t = A.trait_matrix(m)
        r = A.trait_pc_corr(m)
        opts = {ax: A.pc_map_options(m, ax) for ax in ["PC2", "PC3"]}
        traits = sorted({tr for o in opts.values() for tr, _ in o})
        z = {}
        for tr in traits:
            v = t[tr].to_numpy()
            z[tr] = [round(float(q), 4) for q in (v - v.mean()) / v.std()]
        out["models"][m] = {
            "pc": {f"PC{j}": [round(float(q), 3) for q in pcs[f"pc{j}"]] for j in range(1, 4)},
            "z": z, "r": {tr: [round(float(r.loc[tr, f"PC{j}"]), 4) for j in range(1, 4)] for tr in traits},
            "opts": {ax: [[tr, lab] for tr, lab in o] for ax, o in opts.items()}}
    return out


def pc_trait_map_script() -> str:
    """HTML menus (model, vertical axis, trait) above Figure 1.1 and the script that redraws it. The trait menu is rebuilt
    for each model and axis. On phones the colour bar is hidden."""
    from pathlib import Path
    data = json.dumps(pc_trait_map_payload(), separators=(",", ":"))
    js = (Path(__file__).with_name("pc_map.js")).read_text().replace("__DATA__", data)
    css = ("<style>.pm-ctl{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 4px}.pm-ctl label{font-size:13px;color:#5b6b82;"
           "display:flex;align-items:center;gap:4px}.pm-ctl select{font-size:13px;padding:3px 6px;border:1px solid #c9ced6;"
           "border-radius:4px;background:#fff;color:#1d2430;max-width:240px}</style>")
    return css + "<script>" + js + "</script>"


def axis_guide_html() -> str:
    """Table under Figure 1.1 (three models since iteration 25; PC1-PC3 since iteration 26): rows grouped by axis (Qwen, Gemma, Llama),
    the three traits most correlated with each end (with r) and the two characters furthest toward each end; rows whose
    strongest trait r is under .7 are greyed."""
    gs = {m: A.axis_guide(m) for m in A.PC_MAP_MODELS}
    K = 3  # iteration 26: PC1-PC3 only (PC4 and PC5 are loose mixtures)
    fmt = lambda ts, rs: ", ".join(f"{t.replace('_', ' ')} {two(v)}" for t, v in zip(ts, rs))
    head = "".join(f"<th>{h}</th>" for h in ["Axis", "Model", "Share of variation", "High end: traits (r)", "High-end characters",
                                            "Low end: traits (r)", "Low-end characters"])
    body = ""
    for k in range(K):
        for i, m in enumerate(A.PC_MAP_MODELS):
            row = gs[m].iloc[k]
            var = A.pca_variance(m).loc[k + 1]
            top = " class='pm-first'" if i == 0 else ""
            body += (f"<tr class='{'kweak' if row.strongest < 0.7 else ''}'><td{top}><b>{row.axis}</b></td><td>{A.MODEL_LABEL[m]}</td>"
                     f"<td>{var:.0%}</td><td>{html.escape(fmt(row.high, row.high_r))}</td><td>{html.escape(', '.join(row.high_chars))}</td>"
                     f"<td>{html.escape(fmt(row.low, row.low_r))}</td><td>{html.escape(', '.join(row.low_chars))}</td></tr>")
    return ("<style>.phg-ckey tr.kweak td{color:#8a94a3}.phg-ckey td{font-size:13px}"
            "#table-axes tbody tr:nth-child(3n+1) td{border-top:2px solid #b8c0cc}</style>"
            "<p class='phg-listhead' id='axis-guide'>What each model's first three activation axes separate</p>"
            f"<div class='tablewrap phg-ckey' id='table-axes'><table class='phg-table'><thead><tr>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table></div>"
            "<p class='phg-small'>For each axis, the traits whose scores correlate most strongly with the characters' "
            "positions on it, across all 275 characters, and the characters furthest toward each end; computed in this "
            "notebook. Each model has its own axes, so Qwen's PC2 and Gemma's PC2 need not mean the same thing (Section 2 "
            "compares them). Share of variation is from the saved PCA. Later axes are looser mixtures of traits and are "
            "left out. Signs are arbitrary.</p>")


def pc_map_phone_script(fig_id: str = "1.2") -> str:
    """Iteration 22: below 600 px, hide Figure 1.2's colour bar (red high / blue low is in the caption) so the two menus
    fit side by side and the plot gets the width."""
    return ("<script>(function(){var g=document.getElementById('fig-" + fig_id + "');"
            "function go(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(go,80);}"
            "if(window.innerWidth>=600)return;"
            "var n=g.data.length-1,idx=[];for(var i=0;i<n;i++)idx.push(i);"
            "Plotly.restyle(g,{'marker.showscale':false},idx).then(function(){Plotly.relayout(g,{'margin.r':8,"
            "'updatemenus[0].x':-0.14,'updatemenus[1].x':-0.14});});}"
            "go();})();</script>")


def bigfive_trait_domain_figure() -> go.Figure:
    """Iteration 32 side preview: the 42 Figure 1.3 traits (rows, grouped by mapped domain) against the five Big Five
    domains (columns). People: SAPA proxy r with the official IPIP100 domain scales. Models: r with leave-one-out domain
    scores built from the other mapped traits. Each row's mapped domain is outlined. Menu: People, the three models, and
    each model − People."""
    t = A.bf_traits()
    nt = len(t)
    rows = list(t.label)
    cols = [A.DOMAIN_NAME[d] for d in A.DOMAIN_ORDER]
    models = ["qwen", "gemma", "llama"]
    views = [("People (SAPA)", "people", False, PEARSON_SCALE, -1, 1, "r")] + \
        [(A.MODEL_LABEL[m], m, False, PEARSON_SCALE, -1, 1, "r") for m in models] + \
        [(f"{A.MODEL_LABEL[m]} − People", m, True, DIFF_SCALE, -2, 2, "model r − people r") for m in models]
    fac = np.array([[f"{rows[i]} ({t.facet[i]} {t.facet_name[i]}) with {c}" for c in cols] for i in range(nt)])
    P = A.bf_domains("people").to_numpy()
    cbar = dict(orientation="h", thickness=10, len=0.8, title_side="top")
    fig = go.Figure()
    for k, (lab, src, diff, scale, lo, hi, unit) in enumerate(views):
        Z = A.bf_domains(src).to_numpy() - (P if diff else 0)
        txt = np.vectorize(lambda v: f"{v:+.2f}".replace("-", "−"))(Z)
        fig.add_trace(go.Heatmap(z=Z, x=cols, y=rows, colorscale=scale, zmin=lo, zmax=hi, zmid=0, visible=(k == 0),
                                 text=txt, texttemplate="%{text}", textfont=dict(size=9), customdata=fac, name=lab,
                                 xgap=1, ygap=1, colorbar=dict(title=unit, **cbar),
                                 hovertemplate="%{customdata}<br>" + unit + " %{z:+.3f}<extra>" + lab + "</extra>"))
    shapes, pos = [], 0
    for j, d in enumerate(A.DOMAIN_ORDER):
        p0 = pos
        pos += int((t.domain == d).sum())
        if p0:
            shapes.append(dict(type="line", xref="x", yref="y", x0=-0.5, x1=4.5, y0=p0 - 0.5, y1=p0 - 0.5,
                               line=dict(color="#333", width=1.2)))
        shapes.append(dict(type="rect", xref="x", yref="y", x0=j - 0.5, x1=j + 0.5, y0=p0 - 0.5, y1=pos - 0.5,
                           line=dict(color="#111", width=2), fillcolor="rgba(0,0,0,0)", name="own_domain"))
    sp, an = left_domain_band(list(t.domain + "0"), "tdom", off=96)
    n = len(fig.data)
    buttons = [dict(label=v[0], method="update", args=[{"visible": vis_mask(n, [k])}]) for k, v in enumerate(views)]
    base_layout(fig, "Each historical trait's correlation with the five Big Five domains (r)", height=1150,
                menus=[menu(buttons)], b=75, l=96 + BAND_W + 10, r=12, shapes=shapes + sp, annotations=an)
    mg = fig.layout.margin
    fig.update_traces(colorbar=dict(yref="paper", y=-(mg.b - 4) / (fig.layout.height - mg.t - mg.b), yanchor="bottom"))
    fig.update_xaxes(side="top", tickfont=dict(size=10), showgrid=False)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=10), showgrid=False, dtick=1)
    return fig


# ------------------------------------------------------------ Iteration 32: Figure 6.1 (Discussion)
SOURCE_STYLE = {
    # key: (legend label, marker, colour, filled)
    "people_bbc": ("People, BBC (BFI-44)", "diamond", "#222222", True),
    "people_ipip": ("People, IPIP-NEO (our 26 facets)", "diamond", "#222222", False),
    "gpt35_generic": ("GPT-3.5 answers", "square", "#2f5d9a", False),
    "gpt4_generic": ("GPT-4 answers", "square", "#2f5d9a", True),
    "gpt35_silicon": ("GPT-3.5 answers", "square", "#2f5d9a", False),
    "gpt4_silicon": ("GPT-4 answers", "square", "#2f5d9a", True),
    "qwen_facets": ("Qwen activations, facets", "circle", "#c4501b", False),
    "qwen_traits": ("Qwen activations, trait words", "circle", "#c4501b", True),
    "gemma_traits": ("Gemma activations, trait words", "triangle-up", "#8a5a00", True),
    "llama_traits": ("Llama activations, trait words", "triangle-down", "#6a3d9a", True),
}
VIEWS_61 = [
    ("Answers: generic personas", ["people_bbc", "people_ipip", "gpt35_generic", "gpt4_generic", "qwen_facets", "qwen_traits"]),
    ("Answers: demographic personas", ["people_bbc", "people_ipip", "gpt35_silicon", "gpt4_silicon", "qwen_facets", "qwen_traits"]),
    ("Activations: three models", ["people_bbc", "people_ipip", "qwen_traits", "gemma_traits", "llama_traits"]),
]


def domain_sources_figure() -> go.Figure:
    """Figure 6.1: correlation between Big Five domain scores, ten domain pairs (rows, N-E first), in people, in GPT-3.5 /
    GPT-4 questionnaire answers given in persona (Petrov et al. 2024, published values) and in model activations (this
    report). Menu: generic or demographic personas for the GPT answers, or the three activation models."""
    D = A.domain_corr_sources()
    pairs = list(D.index)
    lab = [f"{A.DOMAIN_NAME[a]} – {A.DOMAIN_NAME[b]}" for a, b in pairs]
    ys = np.arange(len(pairs))
    keys = list(dict.fromkeys(k for _, ks in VIEWS_61 for k in ks))
    fig = go.Figure()
    for k in keys:
        name, sym, col, filled = SOURCE_STYLE[k]
        # Spread the markers of one row a little so they do not hide each other.
        pos = [ks.index(k) for _, ks in VIEWS_61 if k in ks][0]
        off = (pos - 2.5) * 0.11
        vis = k in VIEWS_61[0][1]
        fig.add_trace(go.Scatter(x=D[k], y=ys + off, mode="markers", name=name, visible=vis, legendrank=pos,
                                 marker=dict(symbol=sym if filled else sym + "-open", size=10, color=col,
                                             line=dict(width=1.6, color=col)),
                                 customdata=lab, hovertemplate="%{customdata}<br>r %{x:+.2f}<extra>" + name + "</extra>"))
    n = len(fig.data)
    buttons = []
    for vlab, ks in VIEWS_61:
        idx = [keys.index(k) for k in ks]
        # The same series sits at a different slot in each view: recompute the vertical offsets per view.
        yy = [list(ys + (ks.index(k) - (len(ks) - 1) / 2) * 0.11) if k in ks else list(ys) for k in keys]
        buttons.append(dict(label=vlab, method="update", args=[{"visible": vis_mask(n, idx), "y": yy}]))
    # Apply the first view's offsets now (the loop above used a fixed slot).
    first = buttons[0]["args"][0]
    for i, tr in enumerate(fig.data):
        tr.y = first["y"][i]
    shapes = [dict(type="rect", xref="x domain", x0=0, x1=1, yref="y", y0=-0.5, y1=0.5, fillcolor="rgba(196,80,27,0.08)",
                   line=dict(width=0), layer="below")]
    base_layout(fig, "Correlation between Big Five domain scores: people, model answers and model activations (r)",
                height=640, menus=[menu(buttons)], b=120, l=200, r=16, shapes=shapes)
    fig.add_vline(x=0, line=dict(color="#999", width=1))
    fig.update_xaxes(title="Correlation between the two domain scores (r)", range=[-1.02, 1.02], zeroline=False)
    fig.update_yaxes(tickvals=list(ys), ticktext=lab, range=[len(ys) - 0.5, -0.5], tickfont=dict(size=11), showgrid=False)
    for y in ys[1:]:
        fig.add_hline(y=y - 0.5, line=dict(color="#e6e9ee", width=1))
    return fig


def domain_sources_phone_script(fig_id: str = "6.1") -> str:
    """Below 600 px: abbreviated row labels ("Neur. – Extr."), narrower left margin, shorter axis title."""
    short = [f"{DOMAIN_ABBR[a]} – {DOMAIN_ABBR[b]}" for a, b in A.DOMAIN_PAIRS]
    return ("<script>(function(){var g=document.getElementById('fig-" + fig_id + "');"
            "function go(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(go,80);}"
            "if(window.innerWidth>=600)return;"
            "Plotly.relayout(g,{'yaxis.ticktext':" + json.dumps(short) + ",'margin.l':96,'margin.r':8,"
            "'xaxis.title.text':'Correlation (r)'});}"
            "go();})();</script>")


# ------------------------------------------------------------ Iteration 33: Figures 4.1-4.2 (elicitation)
def stopping_figure() -> go.Figure:
    """Figure 4.2: for each of the 30 IPIP-NEO facets, the number of accepted questions at which each prompt format met
    the stopping rule (first scheduled checkpoint with n >= 16, bootstrap p05 cosine >= .95, cosine to the previous
    checkpoint >= .98). Formats that never met it sit in the 'Not converged' column at their last checkpoint's label."""
    t = A.stopping_table()
    codes = A.all30_codes()
    cats = [str(c) for c in A.CHECKPOINTS[2:6]] + ["Not converged"]
    lab = [f"{c} {A.facet_label30(c)}" for c in codes]
    ys = np.arange(len(codes))
    fig = go.Figure()
    for fmt, nm, sym, col, off in [("scenario", "Scenario prompts", "circle", SCEN, -0.17), ("survey_style", "Survey-style prompts", "square", SURV, 0.17)]:
        d = t[t.format == fmt].set_index("facet").loc[codes]
        x = [str(int(v)) if pd.notna(v) else "Not converged" for v in d.stopping_n]
        cd = [(f"{lab[i]}<br>{nm}: stopped at {int(r.stopping_n)} questions<br>p05 cosine {r.p05:.3f}, cosine to previous {r.prev:.3f}"
               if pd.notna(r.stopping_n) else
               f"{lab[i]}<br>{nm}: did not converge ({r.available} accepted questions; last checkpoint {r.last_checkpoint})")
              for i, r in enumerate(d.itertuples())]
        filled = [bool(v) for v in d.qualified]
        fig.add_trace(go.Scatter(x=x, y=ys + off, mode="markers", name=nm, customdata=cd, hovertemplate="%{customdata}<extra></extra>",
                                 marker=dict(symbol=[sym if f else sym + "-open" for f in filled], size=10, color=col,
                                             line=dict(width=1.5, color=col))))
    shapes, anns = left_domain_band([c for c in codes], "stop", off=150)
    for c in A.EXCLUDED_NAMES:
        i = codes.index(c)
        shapes.append(dict(type="rect", xref="x domain", x0=0, x1=1, yref="y", y0=i - 0.5, y1=i + 0.5,
                           fillcolor="rgba(120,120,120,0.10)", line=dict(width=0), layer="below"))
    base_layout(fig, "Questions needed before each facet's direction stopped changing", height=820, b=95, l=150 + BAND_W + 10,
                r=12, shapes=shapes, annotations=anns)
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=cats, title="Accepted questions at the stopping point",
                     side="top", showgrid=True)
    fig.update_yaxes(tickvals=list(ys), ticktext=lab, range=[len(ys) - 0.5, -0.5], tickfont=dict(size=10), showgrid=False)
    return fig


def question_cloud_figure(fmt: str = "scenario") -> go.Figure:
    """Figure 4.1: each saved question's contrast direction (high minus low persona answer) for one facet, as cosines with
    Qwen's block-48 PC1-48 and PC2-48; filled = counted in the final estimate, hollow = accepted after the stop (weight 0).
    The line traces the running mean at each scheduled checkpoint; the star is the final estimate. Facet menu."""
    codes = list(A.ordered_codes())
    fig = go.Figure()
    per = 4
    notes = []
    st = A.stopping_table().set_index(["facet", "format"])
    for k, c in enumerate(codes):
        q, run, fin = A.question_cloud(c, fmt)
        on, off_ = q[q.formal_endpoint_member], q[~q.formal_endpoint_member]
        v = k == codes.index("E1")
        fig.add_trace(go.Scatter(x=on.cos_pc1, y=on.cos_pc2, mode="markers", visible=v, name="Questions in the estimate",
                                 legendgroup="q", showlegend=True, marker=dict(size=8, color=SCEN, opacity=0.75),
                                 customdata=on.question_id, hovertemplate="%{customdata}<br>PC1-48 %{x:+.2f} · PC2-48 %{y:+.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=off_.cos_pc1, y=off_.cos_pc2, mode="markers", visible=v, name="Accepted after the stop (not used)",
                                 legendgroup="x", marker=dict(size=8, color=SCEN, symbol="circle-open", opacity=0.6),
                                 customdata=off_.question_id, hovertemplate="%{customdata}<br>PC1-48 %{x:+.2f} · PC2-48 %{y:+.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=run.cos_pc1, y=run.cos_pc2, mode="lines+markers", visible=v, name="Running mean at each checkpoint",
                                 legendgroup="r", line=dict(color="#222", width=1.5), marker=dict(size=5, color="#222"),
                                 customdata=run.n, hovertemplate="mean of first %{customdata} questions<extra></extra>"))
        fig.add_trace(go.Scatter(x=fin.cos_pc1, y=fin.cos_pc2, mode="markers", visible=v, name="Final estimate", legendgroup="f",
                                 marker=dict(symbol="star", size=16, color="#c4501b", line=dict(color="#fff", width=1)),
                                 hovertemplate="final estimate<br>PC1-48 %{x:+.2f} · PC2-48 %{y:+.2f}<extra></extra>"))
        r = st.loc[(c, fmt)]
        notes.append(f"{A.name(c)} ({c}): stopped at {int(r.stopping_n)} questions · {len(on)} in the estimate, {len(off_)} after the stop")
    n = len(fig.data)
    ann = dict(xref="paper", yref="paper", x=0, y=1.0, xanchor="left", yanchor="bottom", showarrow=False, align="left",
               font=dict(size=12, color="#333"))
    buttons = [dict(label=f"{c} {A.name(c)}", method="update",
                    args=[{"visible": vis_mask(n, list(range(k * per, k * per + per)))}, {"annotations": [dict(ann, text=notes[k])]}])
               for k, c in enumerate(codes)]
    base_layout(fig, "Each question's direction for one facet, on Qwen's block-48 PC1-48 and PC2-48 (cosine)", height=600,
                menus=[menu(buttons)], note_lines=1, b=110, l=60, r=16, annotations=[dict(ann, text=notes[codes.index("E1")])])
    fig.layout.updatemenus[0].active = codes.index("E1")
    fig.add_vline(x=0, line=dict(color="#bbb", width=1))
    fig.add_hline(y=0, line=dict(color="#bbb", width=1))
    # Equal scales: the square plot area shrinks horizontally (constrain="domain") instead of widening the x range.
    fig.update_xaxes(title="Cosine with PC1-48", range=[-0.55, 0.55], zeroline=False, constrain="domain")
    fig.update_yaxes(title="Cosine with PC2-48", range=[-0.55, 0.55], zeroline=False, scaleanchor="x", scaleratio=1, constrain="domain")
    return fig


def stopping_phone_script(fig_id: str = "conv") -> str:
    """Below 600 px: facet codes only on the rows, narrower left margin, no domain band labels."""
    return ("<script>(function(){var g=document.getElementById('fig-" + fig_id + "');"
            "function go(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(go,80);}"
            "if(window.innerWidth>=600)return;"
            "var t=g.layout.yaxis.ticktext.map(function(s){return String(s).split(' ')[0];});"
            "var a=(g.layout.annotations||[]).filter(function(n){return n.textangle!==-90;});"
            "var sh=(g.layout.shapes||[]).filter(function(x){return x.xsizemode!=='pixel';});"
            "Plotly.relayout(g,{'yaxis.ticktext':t,'margin.l':44,'margin.r':8,annotations:a,shapes:sh,'xaxis.tickfont.size':10,'xaxis.title.text':''});}"
            "go();})();</script>")


def trait_domain_phone_script(fig_id: str = "sapa2") -> str:
    """Below 600 px: abbreviated domain column headings (Neur., Extr., ...) so they stay horizontal under the menu."""
    m = {A.DOMAIN_NAME[d]: DOMAIN_ABBR[d] for d in A.DOMAIN_ORDER}
    return ("<script>(function(){var g=document.getElementById('fig-" + fig_id + "'),M=" + json.dumps(m) + ";"
            "function go(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(go,80);}"
            "if(window.innerWidth>=600)return;"
            "Plotly.restyle(g,{x:g.data.map(function(t){return t.x.map(function(v){return M[v]||v;});})}).then(function(){"
            "Plotly.relayout(g,{'xaxis.tickangle':0,'xaxis.tickfont.size':9,'margin.r':6});});}"
            "go();})();</script>")


# ------------------------------------------------------------ Iteration 40: Figure 1.2 (Big Five traits on the axes)
def bigfive_pc_figure() -> go.Figure:
    """Figure 1.2: the 42 Big Five traits of Figure 1.3 (rows, grouped by domain, reverse-keyed traits flipped) against each
    model's PC1-PC3 (r across the 275 characters). Menu: Qwen, Gemma, Llama, then the five domain scores per model."""
    t = A.bf_traits()
    models = ["qwen", "gemma", "llama"]
    cols = ["PC1", "PC2", "PC3"]
    fac = [f"{f} {n}" for f, n in zip(t.facet, t.facet_name)]
    cbar = dict(orientation="h", thickness=10, len=0.8, title_side="top")
    fmt = np.vectorize(lambda v: f"{v:+.2f}".replace("-", "−"))
    fig = go.Figure()
    for k, m in enumerate(models):
        Z = A.bf_pc_corr(m).to_numpy()
        cd = np.array([[f"{lab} ({fac[i]}) with {A.MODEL_LABEL[m]}'s {c}" for c in cols] for i, lab in enumerate(t.label)])
        fig.add_trace(go.Heatmap(z=Z, x=cols, y=list(t.label), colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0, visible=(k == 0),
                                 text=fmt(Z), texttemplate="%{text}", textfont=dict(size=9), customdata=cd, xgap=1, ygap=1,
                                 name=A.MODEL_LABEL[m], colorbar=dict(title="r", **cbar),
                                 hovertemplate="%{customdata}<br>r %{z:+.3f}<extra></extra>"))
    n_tr = len(fig.data)
    dn = [A.DOMAIN_NAME[d] for d in A.DOMAIN_ORDER]
    for m in models:
        Z = A.bf_domain_pc_corr(m).to_numpy()
        cd = np.array([[f"{d} score with {A.MODEL_LABEL[m]}'s {c}" for c in cols] for d in dn])
        fig.add_trace(go.Heatmap(z=Z, x=cols, y=dn, xaxis="x2", yaxis="y2", colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0,
                                 visible=False, text=fmt(Z), texttemplate="%{text}", textfont=dict(size=12), customdata=cd,
                                 xgap=2, ygap=2, name="Domains: " + A.MODEL_LABEL[m], colorbar=dict(title="r", **cbar),
                                 hovertemplate="%{customdata}<br>r %{z:+.3f}<extra></extra>"))
    n = len(fig.data)
    shapes, anns = left_domain_band(list(t.domain + "0"), "bfpc", off=92)
    for p0 in [int(i) for i in np.flatnonzero(np.r_[False, t.domain.values[1:] != t.domain.values[:-1]])]:
        shapes.append(dict(type="line", xref="x", yref="y", x0=-0.5, x1=2.5, y0=p0 - 0.5, y1=p0 - 0.5, line=dict(color="#333", width=1.2)))
    trait_layout = {"xaxis.visible": True, "yaxis.visible": True, "xaxis2.visible": False, "yaxis2.visible": False,
                    "shapes": shapes, "annotations": anns, "height": 1000}
    domain_layout = {"xaxis.visible": False, "yaxis.visible": False, "xaxis2.visible": True, "yaxis2.visible": True,
                     "shapes": [], "annotations": [], "height": 1000}
    buttons = [dict(label=A.MODEL_LABEL[m], method="update", args=[{"visible": vis_mask(n, [k])}, trait_layout])
               for k, m in enumerate(models)]
    buttons += [dict(label="Domains: " + A.MODEL_LABEL[m], method="update", args=[{"visible": vis_mask(n, [n_tr + k])}, domain_layout])
                for k, m in enumerate(models)]
    base_layout(fig, "Big Five traits on each model's activation axes (r)", height=1000, menus=[menu(buttons)], b=80,
                l=92 + BAND_W + 10, r=12, shapes=shapes, annotations=anns)
    mg = fig.layout.margin
    fig.update_traces(colorbar=dict(yref="paper", y=-(mg.b - 4) / (fig.layout.height - mg.t - mg.b), yanchor="bottom"))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(side="top", tickfont=dict(size=11), showgrid=False),
        yaxis=dict(autorange="reversed", tickfont=dict(size=10), showgrid=False, dtick=1),
        xaxis2=dict(visible=False, anchor="y2", side="top", showgrid=False, type="category", categoryarray=cols),
        yaxis2=dict(visible=False, anchor="x2", showgrid=False, type="category", categoryarray=dn, autorange="reversed",
                    domain=[0.6, 1]))
    return fig


# ------------------------------------------------------------ Iteration 41: Figure 1.2 (Big Five, one figure, three menus)
BF_PCS = ["PC1", "PC2", "PC3", "PC4", "PC5"]


def _left_band(domains, yref, xdom, off, kind):
    """Shaded left band per Big Five domain for rows at y = 0..n-1 on the given axis (names rotated)."""
    shapes, anns, pos = [], [], 0
    for k, dom in enumerate(A.DOMAIN_ORDER):
        p0 = pos
        pos += sum(d == dom for d in domains)
        if p0:
            shapes.append(dict(type="line", xref=xdom, x0=0, x1=1, yref=yref, y0=p0 - 0.5, y1=p0 - 0.5, line=dict(color="#333", width=1.2)))
        shapes.append(dict(type="rect", line=dict(width=0), fillcolor=BAND_TINT[k % 2], layer="above", yref=yref, y0=p0 - 0.5,
                           y1=pos - 0.5, xref=xdom, xsizemode="pixel", xanchor=0, x0=-(off + BAND_W), x1=-off))
        anns.append(dict(name=f"pcband|{kind}|{dom}", xref=xdom, x=0, xshift=-(off + BAND_W / 2), yref=yref, y=(p0 + pos - 1) / 2,
                         xanchor="center", yanchor="middle", textangle=-90, showarrow=False, text=A.DOMAIN_NAME[dom],
                         font=dict(size=10, color="#1d2430")))
    return shapes, anns


def bigfive_combined_figure() -> tuple:
    """Figure 1.2 (iteration 41): the Big Five trait matrix and the Big Five traits on the activation axes in one figure.
    Three HTML menus (Model; Show: traits or domain scores; Columns: Big Five or PC1-PC5) pick one of 12 views. Axis pairs:
    x/y traits x traits, x2/y2 domains x domains, x3/y3 traits x PCs, x4/y4 domains x PCs. Returns (figure, view payload)."""
    base = bigfive_trait_matrix_figure()  # traces 0-2: traits x traits (x/y); 3-5: domains x domains (x2/y2)
    tl, dl = base.layout.updatemenus[0].buttons[0].args[1], base.layout.updatemenus[1 - 1].buttons[3].args[1]
    fig = go.Figure(data=list(base.data), layout=base.layout)
    fig.layout.updatemenus = ()  # replaced by HTML menus (update_layout merges and would keep the old menu)
    fig.update_layout(meta="Big Five traits: how they relate to one another and to the activation axes (r)")
    t = A.bf_traits()
    models = ["qwen", "gemma", "llama"]
    fac = [f"{f} {n}" for f, n in zip(t.facet, t.facet_name)]
    dn = [A.DOMAIN_NAME[d] for d in A.DOMAIN_ORDER]
    cbar = dict(orientation="h", thickness=10, len=0.8, title_side="top")
    fmt = np.vectorize(lambda v: f"{v:+.2f}".replace("-", "−"))
    mg = fig.layout.margin
    cb_y = -(mg.b - 4) / (fig.layout.height - mg.t - mg.b)
    for m in models:  # traits x PC1-PC5 on x3/y3
        Z = A.bf_pc_corr(m, 5).to_numpy()
        cd = np.array([[f"{lab} ({fac[i]}) with {A.MODEL_LABEL[m]}'s {c}" for c in BF_PCS] for i, lab in enumerate(t.label)])
        fig.add_trace(go.Heatmap(z=Z, x=BF_PCS, y=list(range(len(t))), xaxis="x3", yaxis="y3", colorscale=PEARSON_SCALE, zmin=-1,
                                 zmax=1, zmid=0, visible=False, text=fmt(Z), texttemplate="%{text}", textfont=dict(size=9),
                                 customdata=cd, xgap=1, ygap=1, name="PCs: " + A.MODEL_LABEL[m],
                                 colorbar=dict(title="r", yref="paper", y=cb_y, yanchor="bottom", **cbar),
                                 hovertemplate="%{customdata}<br>r %{z:+.3f}<extra></extra>"))
    for m in models:  # domains x PC1-PC5 on x4/y4
        Z = A.bf_domain_pc_corr(m, 5).to_numpy()
        cd = np.array([[f"{d} score with {A.MODEL_LABEL[m]}'s {c}" for c in BF_PCS] for d in dn])
        fig.add_trace(go.Heatmap(z=Z, x=BF_PCS, y=dn, xaxis="x4", yaxis="y4", colorscale=PEARSON_SCALE, zmin=-1, zmax=1, zmid=0,
                                 visible=False, text=fmt(Z), texttemplate="%{text}", textfont=dict(size=11), customdata=cd, xgap=2,
                                 ygap=2, name="Domain PCs: " + A.MODEL_LABEL[m],
                                 colorbar=dict(title="r", yref="paper", y=cb_y, yanchor="bottom", **cbar),
                                 hovertemplate="%{customdata}<br>r %{z:+.3f}<extra></extra>"))
    s3, a3 = _left_band(list(t.domain), "y3", "x3 domain", 92, "traitpc")
    fig.update_layout(
        xaxis3=dict(visible=False, anchor="y3", domain=[0, 0.62], side="top", showgrid=False, type="category", categoryarray=BF_PCS,
                    range=[-0.5, 4.5], autorange=False, tickfont=dict(size=11)),
        yaxis3=dict(visible=False, anchor="x3", domain=[0, 1], showgrid=False, range=[len(t) - 0.5, -0.5], tickvals=list(range(len(t))),
                    ticktext=list(t.label), tickfont=dict(size=9), automargin=False),
        xaxis4=dict(visible=False, anchor="y4", domain=[0, 1], side="top", showgrid=False, type="category", categoryarray=BF_PCS,
                    range=[-0.5, 4.5], autorange=False, constrain="domain", constraintoward="left", tickfont=dict(size=11)),
        yaxis4=dict(visible=False, anchor="x4", domain=[0, 1], showgrid=False, type="category", categoryarray=dn, range=[4.5, -0.5],
                    autorange=False,
                    scaleanchor="x4", scaleratio=1, constrain="domain", constraintoward="top", tickfont=dict(size=11)))
    n = len(fig.data)
    # One invisible shape per axis pair in every view: an unreferenced subplot is dropped while its scale anchor remains,
    # and Plotly then fails with "ax.dtick error: Infinity" (see correlation_matrices).
    anchor = [dict(type="line", xref=f"x{s_}", yref=f"y{s_}", x0=0, x1=0, y0=0, y1=0, opacity=0, line=dict(width=0))
              for s_ in ["", "2", "3", "4"]]
    hide = {f"{a}axis{s}.visible": False for a in "xy" for s in ["", "2", "3", "4"]}

    def lay(on, shapes, anns):
        d = dict(hide)
        d.update({f"{a}axis{on}.visible": True for a in "xy"})
        d.update(shapes=shapes, annotations=anns)
        return d
    dnote = [a for a in dl["annotations"] if a.get("text", "").startswith("Domain averages")]
    views = {}
    for k, m in enumerate(models):
        # Frame per view: the trait matrix needs room above for its rotated labels; the other views do not.
        views[f"{m}|traits|bf"] = dict(visible=vis_mask(n, [k]), layout=lay("", list(tl["shapes"]) + anchor, tl["annotations"]),
                                       h=900, t=int(mg.t))
        views[f"{m}|domains|bf"] = dict(visible=vis_mask(n, [3 + k]), layout=lay("2", list(dl["shapes"]) + anchor, dl["annotations"]),
                                        h=600, t=70)
        views[f"{m}|traits|pc"] = dict(visible=vis_mask(n, [6 + k]), layout=lay("3", anchor + s3, a3), h=900, t=60)
        views[f"{m}|domains|pc"] = dict(visible=vis_mask(n, [9 + k]), layout=lay("4", anchor, []), h=600, t=60)
    _ = dnote
    return fig, views


def bigfive_combined_script(fig_id: str, views: dict) -> str:
    """HTML menus above Figure 1.2 (Model, Show, Columns) and the script that applies one of the 12 views. Phones open on the
    Qwen domain view with Big Five columns, in a shorter frame."""
    data = json.dumps(views, separators=(",", ":"), default=lambda o: o.to_plotly_json() if hasattr(o, "to_plotly_json") else str(o))
    sel = lambda i, lab, opts: (f"<label>{lab} <select id='{i}'>" + "".join(f"<option value='{v}'>{t}</option>" for v, t in opts)
                                + "</select></label>")
    ctl = ("<div class='pm-ctl' id='bf-ctl'>" + sel("bf-m", "Model", [("qwen", "Qwen"), ("gemma", "Gemma"), ("llama", "Llama")])
           + sel("bf-l", "Show", [("traits", "Traits"), ("domains", "Domain scores")])
           + sel("bf-c", "Columns", [("bf", "Big Five traits"), ("pc", "PC1–PC5")]) + "</div>")
    return ("<script>(function(){var V=" + data + ",g=document.getElementById('fig-" + fig_id + "');"
            "var st={m:'qwen',l:'traits',c:'bf'};var phone=window.innerWidth<600;"
            "function apply(){var v=V[st.m+'|'+st.l+'|'+st.c];var L=Object.assign({},v.layout);"
            "['m','l','c'].forEach(function(k){var e=document.getElementById('bf-'+k);if(e)e.value=st[k];});"
            "var H=(phone&&st.l==='domains')?520:v.h,T=v.t,B=g.layout.margin.b;L.height=H;L['margin.t']=T;"
            "if(phone&&st.c==='pc'&&st.l==='traits'){L['xaxis3.domain']=[0,1];}"
            "g.style.height=H+'px';if(g.parentNode&&g.parentNode.style.height)g.parentNode.style.height=H+'px';"
            "Plotly.update(g,{visible:v.visible,'colorbar.y':-(B-4)/(H-T-B)},L);var w=document.getElementById('wrap-" + fig_id + "');"
            "w.dataset.model=st.m;w.dataset.level=st.l;w.dataset.cols=st.c;}"
            "function init(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(init,80);}"
            "var d=document.createElement('div');d.innerHTML=" + json.dumps(ctl) + ";var c=d.firstChild;"
            "var host=g.parentNode;host.parentNode.insertBefore(c,host);"
            "if(phone){st.l='domains';document.getElementById('bf-l').value='domains';}"
            "['m','l','c'].forEach(function(k){document.getElementById('bf-'+k).onchange=function(e){st[k]=e.target.value;apply();};});"
            "apply();window.BF={state:st,apply:apply,views:V};}init();})();</script>")


# ------------------------------------------------------------ Iteration 42-43: Figure 2.2 with a contributing-traits view
CONTRIB_N = 3  # traits shown at each end of a consensus direction (iteration 43)


def consensus_contrib(c: str, n: int = CONTRIB_N) -> pd.DataFrame:
    """Top-n and bottom-n traits of consensus direction c by AA18 consensus loading. Bottom traits carry sign -1 so every row
    points toward the direction's high end; label adds "(−)". Columns: trait, v (loading), sign, label, sign_consistent."""
    d = A.S.csv("aa18_loadings")
    x = d[d.component == c].assign(v=lambda t: t.consensus_loading.astype(float)).sort_values("v", ascending=False)
    out = pd.concat([x.head(n).assign(sign=1.0), x.tail(n).iloc[::-1].assign(sign=-1.0)])
    out["label"] = [t.replace("_", " ") + (" (−)" if sg < 0 else "") for t, sg in zip(out.trait, out.sign)]
    return out[["trait", "v", "sign", "label", "sign_consistent"]].reset_index(drop=True)


def consensus_combined_figure() -> tuple:
    """Figure 2.2 (iteration 43): two HTML menus, Show and Model; columns are always PC1-PC5. Show = Consensus directions
    (C1-C5 x PCs, as before) or Contributing traits: for each direction, its 3 strongest traits at each end by AA18
    consensus loading, the low-end traits sign-flipped ("(−)") so all six point toward the direction's high end, each
    correlated with the model's PC1-PC5. Returns (figure, view payload)."""
    base = consensus_pc_figure()
    fig = go.Figure(data=list(base.data), layout=base.layout)
    fig.layout.updatemenus = ()
    fig.update_layout(meta="Shared directions and their strongest traits on each model's main activation axes (r)",
                      plot_bgcolor="rgba(0,0,0,0)")
    ticks = [f"PC{i}" for i in range(1, 6)]
    rows = pd.concat([consensus_contrib(c).assign(component=c) for c in A.CONSENSUS]).reset_index(drop=True)
    fmt = np.vectorize(lambda v: f"{v:+.2f}".replace("-", "−"))
    for m in ["qwen", "gemma", "llama"]:
        r = A.trait_pc_corr(m)
        Z = np.array([r.loc[t, ticks].to_numpy(float) * sg for t, sg in zip(rows.trait, rows.sign)])
        cd = np.array([[f"{lab} ({A.dlab(c)}, loading {v:+.2f}) with {A.MODEL_LABEL[m]}'s {pc}" for pc in ticks]
                       for lab, c, v in zip(rows.label, rows.component, rows.v)])
        fig.add_trace(go.Heatmap(z=Z, x=ticks, y=list(range(len(rows))), xaxis="x2", yaxis="y2", colorscale=PEARSON_SCALE,
                                 zmin=-1, zmax=1, zmid=0, visible=False, text=fmt(Z), texttemplate="%{text}", textfont=dict(size=10),
                                 xgap=1, ygap=1, customdata=cd, name="Traits: " + A.MODEL_LABEL[m],
                                 colorbar=dict(thickness=10, len=0.8, title=dict(text="r", side="top")),
                                 hovertemplate="%{customdata}<br>r %{z:+.3f}<extra></extra>"))
    shapes, anns = [], []
    for k, c in enumerate(A.CONSENSUS):
        p0, p1 = 2 * CONTRIB_N * k, 2 * CONTRIB_N * (k + 1)
        if k:
            shapes.append(dict(type="line", xref="x2 domain", x0=0, x1=1, yref="y2", y0=p0 - 0.5, y1=p0 - 0.5, line=dict(color="#333", width=1.2)))
        shapes.append(dict(type="rect", line=dict(width=0), fillcolor=BAND_TINT[k % 2], layer="above", yref="y2", y0=p0 - 0.5, y1=p1 - 0.5,
                           xref="x2 domain", xsizemode="pixel", xanchor=0, x0=-(118 + BAND_W), x1=-118))
        anns.append(dict(xref="x2 domain", x=0, xshift=-(118 + BAND_W / 2), yref="y2", y=(p0 + p1 - 1) / 2, xanchor="center",
                         yanchor="middle", textangle=-90, showarrow=False, text=A.dlab(c), font=dict(size=10, color="#1d2430"),
                         name="cband|" + A.dlab(c)))
    fig.update_layout(
        xaxis2=dict(visible=False, anchor="y2", domain=[0, 1], side="bottom", type="category", categoryarray=ticks, range=[-0.5, 4.5],
                    autorange=False, showgrid=False),
        yaxis2=dict(visible=False, anchor="x2", domain=[0, 1], range=[len(rows) - 0.5, -0.5], autorange=False, showgrid=False,
                    tickvals=list(range(len(rows))), ticktext=list(rows.label), tickfont=dict(size=10)))
    n = len(fig.data)
    anchor = [dict(type="line", xref=f"x{s_}", yref=f"y{s_}", x0=0, x1=0, y0=0, y1=0, opacity=0, line=dict(width=0))
              for s_ in ["", "2"]]
    views = {}
    for k, m in enumerate(["qwen", "gemma", "llama"]):
        views[f"axes|{m}"] = dict(visible=vis_mask(n, [k]), h=460, layout={
            "xaxis.visible": True, "yaxis.visible": True, "xaxis2.visible": False, "yaxis2.visible": False, "shapes": anchor,
            "annotations": [], "xaxis.title.text": f"{A.MODEL_LABEL[m]}'s activation axes", "margin.l": 170})
        views[f"traits|{m}"] = dict(visible=vis_mask(n, [3 + k]), h=820, layout={
            "xaxis.visible": False, "yaxis.visible": False, "xaxis2.visible": True, "yaxis2.visible": True,
            "xaxis2.title.text": f"{A.MODEL_LABEL[m]}'s activation axes", "shapes": anchor + shapes, "annotations": anns,
            "margin.l": 118 + BAND_W + 10})
    return fig, views


def consensus_combined_script(fig_id: str, views: dict) -> str:
    """HTML menus above Figure 2.2 (iteration 43): Show (Consensus directions / Contributing traits) and Model. Phones get
    short row labels on the direction view and no colour bar."""
    ctl = ("<div class='pm-ctl' id='cs-ctl'><label>Show <select id='cs-v'><option value='axes'>Shared directions</option>"
           "<option value='traits'>Contributing traits</option></select></label>"
           "<label>Model <select id='cs-2'><option value='qwen'>Qwen</option><option value='gemma'>Gemma</option>"
           "<option value='llama'>Llama</option></select></label></div>")
    return ("<script>(function(){var V=" + json.dumps(views, separators=(",", ":")) + ","
            "g=document.getElementById('fig-" + fig_id + "'),st={v:'axes',m:'qwen'},phone=window.innerWidth<600;"
            "function apply(){document.getElementById('cs-v').value=st.v;document.getElementById('cs-2').value=st.m;"
            "var v=V[st.v+'|'+st.m],L=Object.assign({},v.layout);L.height=v.h;"
            "if(phone&&st.v==='axes'){L['margin.l']=60;}"
            "g.style.height=v.h+'px';if(g.parentNode&&g.parentNode.style.height)g.parentNode.style.height=v.h+'px';"
            "Plotly.update(g,{visible:v.visible},L);var w=document.getElementById('wrap-" + fig_id + "');w.dataset.view=st.v;w.dataset.model=st.m;}"
            "function init(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(init,80);}"
            "var d=document.createElement('div');d.innerHTML=" + json.dumps(ctl) + ";var c=d.firstChild;var host=g.parentNode;host.parentNode.insertBefore(c,host);"
            "if(phone){var sy=function(s){return String(s).split(' · ')[0];};"
            "Plotly.restyle(g,{y:[0,1,2].map(function(i){return g.data[i].y.map(sy);}),'textfont.size':9,showscale:false},[0,1,2]);"
            "Plotly.restyle(g,{showscale:false},[3,4,5]);}"
            "document.getElementById('cs-v').onchange=function(e){st.v=e.target.value;apply();};"
            "document.getElementById('cs-2').onchange=function(e){st.m=e.target.value;apply();};"
            "apply();window.CS={state:st,apply:apply};}init();})();</script>")


# ------------------------------------------------------------ Iteration 44: Figure 2.1 (variance per principal component)
MODEL_COLOR = {"qwen": "#c4501b", "gemma": "#8a5a00", "llama": "#6a3d9a"}  # as in Figures 4.4 and 5.1
MODEL_SYMBOL = {"qwen": "circle", "gemma": "triangle-up", "llama": "triangle-down"}


def variance_elbow_figure(k: int = 5) -> go.Figure:
    """Figure 2.1: share of the variation among the 275 characters carried by each of PC1..PCk, three models (saved persona
    PCA diagnostics). Menu: cumulative (default) or each component (elbow)."""
    d = A.S.csv("pca_diag")
    pcs = [f"PC{i}" for i in range(1, k + 1)]
    fig = go.Figure()
    for mode in ["each", "cum"]:
        for m in ["qwen", "gemma", "llama"]:
            x = d[d.model == m].sort_values("component").head(k)
            y = 100 * (x.explained_variance_ratio if mode == "each" else x.cumulative_explained_variance).astype(float)
            fig.add_trace(go.Scatter(x=pcs, y=y, mode="lines+markers+text", name=A.MODEL_LABEL[m], visible=(mode == "cum"),
                                     legendgroup=m, showlegend=(mode == "cum"),
                                     text=[f"{v:.0f}%" if (i == 0 if mode == "each" else i in (2, 4)) else "" for i, v in enumerate(y)], textposition="top center", textfont=dict(size=10, color=MODEL_COLOR[m]),
                                     line=dict(color=MODEL_COLOR[m], width=2),
                                     marker=dict(symbol=MODEL_SYMBOL[m], size=9, color=MODEL_COLOR[m]),
                                     hovertemplate=A.MODEL_LABEL[m] + " %{x}: %{y:.1f}%<extra></extra>"))
    yt = {"each": "Variation carried by this axis alone (%)", "cum": "Variation carried by PC1 through this axis (%)"}
    buttons = [dict(label=lab, method="update", args=[{"visible": [i // 3 == j for i in range(6)]},
                                                     {"yaxis.title.text": yt[mode], "yaxis.range": rng}])
               for j, (lab, mode, rng) in enumerate([("Each component", "each", [0, 36]), ("Cumulative", "cum", [0, 72])])]
    base_layout(fig, "How much of the variation among characters the activation axes carry (%)", height=440,
                menus=[dict(menu(buttons), active=1)], b=70, l=60, r=16)
    fig.update_yaxes(title=yt["cum"], range=[0, 72], ticksuffix="%")
    fig.update_xaxes(title="Activation axis")
    return fig


# ------------------------------------------------------------ Iteration 46: Figure 3.1, one Big Five matrix (replaces 3.1 + 3.2)
BM_SOURCES = ["people", "qwen", "gemma", "llama"]
BM_LABEL = {"people": "People (SAPA)", **A.MODEL_LABEL}
BM_RS = [[0, "#2166ac"], [0.25, "#92c5de"], [0.5, "#f7f7f7"], [0.75, "#f4a582"], [1, "#b2182b"]]  # r: blue low, red high
BM_DS = [[0, "#8c510a"], [0.25, "#dfc27d"], [0.5, "#f5f5f5"], [0.75, "#80cdc1"], [1, "#01665e"]]  # difference: brown, teal


def _bm_clean(M) -> list:
    M = np.array(M, float)
    return [[None if not np.isfinite(v) else round(float(v), 4) for v in r] for r in M]


def bigfive_matrix_payload() -> dict:
    """Every matrix the Figure 3.1 menus can show. T: 42 x 42 trait r (diagonal blank); D: 5 x 5 domain averages (mean
    trait-pair r per block); TB: 42 x 5 trait with domain score (people: IPIP domain scales; models: leave-one-out
    composites); TP / DP: model traits / domain scores with PC1-PC5. Rows in bf_traits order, reverse-keyed flipped."""
    t = A.bf_traits()
    D = A.DOMAIN_ORDER
    P = dict(traits=list(t.label), tdom=[A.DOMAIN_NAME[d] for d in t.domain],
             facet=[f"{f} {n}" for f, n in zip(t.facet, t.facet_name)], doms=[A.DOMAIN_NAME[d] for d in D], pcs=BF_PCS,
             lab=BM_LABEL, T={}, D={}, TB={}, TP={}, DP={})
    for s in BM_SOURCES:
        M = np.array(A.bf_corr(s), float)
        np.fill_diagonal(M, np.nan)
        P["T"][s] = _bm_clean(M)
        dm = np.array([[A.bf_block(s, a, b) for b in D] for a in D], float)
        np.fill_diagonal(dm, np.nan)
        P["D"][s] = _bm_clean(dm)
        P["TB"][s] = _bm_clean(A.bf_domains(s).to_numpy())
    for m in BM_SOURCES[1:]:
        P["TP"][m] = _bm_clean(A.bf_pc_corr(m, 5).to_numpy())
        P["DP"][m] = _bm_clean(A.bf_domain_pc_corr(m, 5).to_numpy())
    return P


def bm_split(lo, hi) -> np.ndarray:
    """Row source below the diagonal, column source above it, diagonal blank."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    i, j = np.indices(lo.shape)
    return np.where(i > j, lo, np.where(i < j, hi, np.nan))


def bigfive_matrix_figure() -> go.Figure:
    """Figure 3.1 (iteration 46): people and the three models through the Big Five in one matrix. HTML menus (Rows, Columns,
    Show) re-draw a single heatmap (bigfive_matrix_script). The static figure is the opening view: Qwen below the diagonal,
    people above it, five domain scores."""
    P = bigfive_matrix_payload()
    Z = bm_split(np.array(P["D"]["qwen"], dtype=float), np.array(P["D"]["people"], dtype=float))
    txt = [["" if not np.isfinite(v) else f"{v:+.2f}".replace("-", "−") for v in r] for r in Z]
    fig = go.Figure(go.Heatmap(z=Z, x=P["doms"], y=P["doms"], colorscale=BM_RS, zmin=-1, zmax=1, zmid=0, xgap=2, ygap=2,
                               text=txt, texttemplate="%{text}", hoverongaps=False, name="Qwen | People (SAPA)",
                               colorbar=dict(orientation="h", thickness=10, len=0.6, title=dict(text="r", side="top"))))
    fig.update_layout(meta="Big Five traits and domains in people and the three models (r)", template="plotly_white", height=520,
                      margin=dict(l=120, r=10, t=40, b=60), font=dict(size=12))
    fig.update_xaxes(side="top", showgrid=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return fig


BM_JS = r"""
var SRC=['people','qwen','gemma','llama'];
function valid(r,c,s){var d=(s==='ddom'||s==='dtr');
  if(c==='pc') return r!=='people'&&!d;
  if(c==='bf') return !(d&&r==='people');
  if(d) return r!==c; return true;}
function fmt(v){return v==null?'':(v>=0?'+':'−')+Math.abs(v).toFixed(2);}
function sub(a,b){return a.map(function(row,i){return row.map(function(v,j){return (v==null||b[i][j]==null)?null:v-b[i][j];});});}
function split(lo,hi){return lo.map(function(row,i){return row.map(function(v,j){return i>j?v:(i<j?hi[i][j]:null);});});}
function view(r,c,s){
  var R=P.lab[r],tr=(s==='tr'||s==='dtr'),diff=(s==='ddom'||s==='dtr'),z,x,y,cap,who=null;
  var rowlab=tr?P.traits.map(function(t,i){return t+' ('+P.facet[i]+')';}):P.doms;
  if(c==='bf'||c==='pc'){
    y=tr?P.traits:P.doms; x=(c==='pc')?P.pcs:P.doms;
    if(c==='pc'){ z=tr?P.TP[r]:P.DP[r];
      cap='<b>'+R+'</b>: each '+(tr?'trait':'Big Five domain score')+' correlated with '+R+"'s first five activation axes, across the 275 characters."; }
    else if(diff){ z=tr?sub(P.TB[r],P.TB.people):sub(P.D[r],P.D.people);
      cap='<b>'+R+' − People (SAPA)</b>: '+(tr?'each trait with each domain score':'domain against domain')+' in '+R+', minus the same in people.'; }
    else { z=tr?P.TB[r]:P.D[r];
      cap=tr?'<b>'+R+'</b>: each trait correlated with each Big Five domain score'+(r==='people'?' (IPIP domain scales).':' (built from the other traits, so no trait is compared with itself).')
            :'<b>'+R+'</b>: domain against domain (average trait-pair r in each block); the same as '+R+' in both Rows and Columns.'; }
  } else {
    var A=tr?P.T:P.D; x=y=tr?P.traits:P.doms; var C=P.lab[c];
    if(diff){ z=sub(A[r],A[c]); cap='<b>'+R+' − '+C+'</b>, '+(tr?'trait by trait':'domain by domain')+'. Teal: the link is more positive in '+R+'; brown: more positive in '+C+'.'; }
    else if(r===c){ z=A[r]; cap='<b>'+R+'</b>: '+(tr?'the 42 traits correlated with one another.':'domain against domain (average trait-pair r in each block).'); }
    else { z=split(A[r],A[c]); who=[R,C]; cap='<b>Below the diagonal: '+R+'</b> · <b>above: '+C+'</b>. A cell and its mirror are the same pair in the two sources.'; }
  }
  var cd=z.map(function(row,i){return row.map(function(_,j){var src=who?(i>j?who[0]:who[1]):'';
    var a=(y===P.traits)?rowlab[i]:y[i], b=(x===P.traits)?rowlab[j]:x[j]; return a+' × '+b+(src?'<br>'+src:'');});});
  return {z:z,x:x,y:y,cap:cap,diff:diff,tr:tr,sq:!(c==='bf'||c==='pc'),split:!!who,cd:cd};
}
function bands(nR,nC,rowsT,colsT){var sh=[],st=[];P.tdom.forEach(function(d,i){if(i>0&&d!==P.tdom[i-1])st.push(i);});
  var L={color:'#333',width:1.1};
  if(rowsT) st.forEach(function(p){sh.push({type:'line',line:L,x0:-0.5,x1:nC-0.5,y0:p-0.5,y1:p-0.5});});
  if(colsT) st.forEach(function(p){sh.push({type:'line',line:L,y0:-0.5,y1:nR-0.5,x0:p-0.5,x1:p-0.5});});
  return sh;}
"""


def bigfive_matrix_script(fig_id: str) -> str:
    """HTML menus above Figure 3.1 (Rows, Columns, Show) and the script that re-draws its single heatmap. Combinations
    without data are disabled (people have no activation axes; a source minus itself). window.BM exposes the state."""
    P = bigfive_matrix_payload()
    sel = lambda i, lab, opts, d: (f"<label>{lab} <select id='{i}'>" + "".join(
        f"<option value='{v}'{' selected' if v == d else ''}>{t}</option>" for v, t in opts) + "</select></label>")
    srcs = [(s, BM_LABEL[s]) for s in BM_SOURCES]
    ctl = ("<div class='pm-ctl' id='bm-ctl'>" + sel("bm-r", "Rows", srcs, "qwen")
           + sel("bm-c", "Columns", srcs + [("bf", "Big Five domains"), ("pc", "PC1–PC5")], "people")
           + sel("bm-s", "Show", [("dom", "Domain scores"), ("tr", "Traits"), ("ddom", "Difference: domain scores"),
                                  ("dtr", "Difference: traits")], "dom")
           + "</div><div class='phg-small' id='bm-cap' style='margin:2px 0 4px'></div>")
    cfg = json.dumps(dict(responsive=True, displaylogo=False, modeBarButtonsToRemove=["lasso2d", "select2d"]))
    return ("<script>(function(){var P=" + json.dumps(P, separators=(",", ":")) + ",RS=" + json.dumps(BM_RS) + ",DS=" + json.dumps(BM_DS)
            + ",CFG=" + cfg + ";" + BM_JS +
            "var g=document.getElementById('fig-" + fig_id + "');var st={r:'qwen',c:'people',s:'dom'};"
            "function $(k){return document.getElementById('bm-'+k);}"
            "function sync(){var r=st.r,c=st.c,s=st.s;"
            "[].forEach.call($('c').options,function(o){o.disabled=!valid(r,o.value,s)&&!valid(r,o.value,'dom');});"
            "[].forEach.call($('r').options,function(o){o.disabled=!valid(o.value,c,s)&&!valid(o.value,c,'dom');});"
            "[].forEach.call($('s').options,function(o){o.disabled=!valid(r,c,o.value);});"
            "$('r').value=r;$('c').value=c;$('s').value=s;}"
            "function apply(){if(!valid(st.r,st.c,st.s)){if(st.s==='ddom')st.s='dom';if(st.s==='dtr')st.s='tr';"
            "if(!valid(st.r,st.c,st.s))st.c='bf';}sync();"
            "var v=view(st.r,st.c,st.s);$('cap').innerHTML=v.cap;"
            "var w=g.clientWidth||g.parentNode.clientWidth||700,ph=w<600,nR=v.y.length,nC=v.x.length;"
            "var dcol=(ph&&v.x===P.doms),lm=v.tr?(ph?112:150):(ph?100:125),tm=(v.tr&&v.sq)?(ph?112:140):(dcol?96:40);"
            "var rm=dcol?44:10,cell=Math.min((w-lm-rm-4)/nC,v.tr?(v.sq?20:80):90);"
            "var ch=v.tr?(v.sq?cell:17):Math.min(cell,v.sq?90:70),H=Math.round(Math.max(280,nR*ch+tm+70));"
            "var text=(v.tr&&v.sq)?null:v.z.map(function(row){return row.map(fmt);});"
            "var t={type:'heatmap',z:v.z,x:v.x.map(function(_,i){return i;}),y:v.y.map(function(_,i){return i;}),"
            "zmin:v.diff?-1.5:-1,zmax:v.diff?1.5:1,zmid:0,colorscale:v.diff?DS:RS,xgap:(v.tr&&v.sq)?0.5:2,ygap:(v.tr&&v.sq)?0.5:2,"
            "hoverongaps:false,text:text,texttemplate:text?'%{text}':'',textfont:{size:v.tr?9:12},customdata:v.cd,"
            "name:st.r+'|'+st.c+'|'+st.s,"
            "hovertemplate:'%{customdata}<br>'+(v.diff?'difference in r':'r')+' %{z:+.3f}<extra></extra>',"
            "colorbar:{orientation:'h',thickness:10,len:0.6,y:-0.02,yanchor:'top',title:{text:v.diff?'difference in r':'r',side:'top'}}};"
            "function ax(lab,n){return {tickvals:Array.apply(null,Array(n)).map(function(_,i){return i;}),ticktext:lab,showgrid:false,"
            "zeroline:false,tickfont:{size:v.tr?(ph?8:9.5):(ph?10:12)},fixedrange:true};}"
            "var xa=ax(v.x,nC);xa.side='top';xa.tickangle=(v.tr&&v.sq)?-60:(dcol?-45:0);xa.range=[-0.5,nC-0.5];"
            "var ya=ax(v.y,nR);ya.autorange=false;ya.range=[nR-0.5,-0.5];"
            "var shapes=bands(nR,nC,v.tr,v.tr&&v.sq);"
            "if(v.split)shapes.push({type:'line',x0:-0.5,y0:-0.5,x1:nC-0.5,y1:nR-0.5,line:{color:'#111',width:1.5,dash:'dot'}});"
            "var lay={height:H,margin:{l:lm,r:rm,t:tm,b:60},template:g.layout.template,font:{size:12},paper_bgcolor:'#fff',"
            "plot_bgcolor:'#fff',xaxis:xa,yaxis:ya,shapes:shapes,meta:g.layout.meta,hoverlabel:{font:{size:12}}};"
            "g.style.height=H+'px';if(g.parentNode&&g.parentNode.style.height)g.parentNode.style.height=H+'px';"
            "Plotly.react(g,[t],lay,CFG);var wr=document.getElementById('wrap-" + fig_id + "');"
            "wr.dataset.rows=st.r;wr.dataset.cols=st.c;wr.dataset.show=st.s;}"
            "function init(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(init,80);}"
            "var d=document.createElement('div');d.innerHTML=" + json.dumps(ctl) + ";var host=g.parentNode;"
            "while(d.firstChild){host.parentNode.insertBefore(d.firstChild,host);}"
            "['r','c','s'].forEach(function(k){$(k).onchange=function(e){st[k]=e.target.value;apply();};});"
            "var lastW=g.clientWidth;window.addEventListener('resize',function(){if(Math.abs(g.clientWidth-lastW)>20){lastW=g.clientWidth;apply();}});"
            "apply();window.BM={state:st,apply:apply,valid:valid,P:P};}init();})();</script>")


# ------------------------------------------------------------ Iteration 47: Figure 1.2, the 240 traits on the activation axes
TM_MODELS = ["qwen", "gemma", "llama"]


def trait_map_payload() -> dict:
    """r across the 275 characters between each of the 240 trait scores and the model's PC1-PC3 (A.trait_pc_corr)."""
    P = {"label": dict(A.MODEL_LABEL), "models": {}}
    for m in TM_MODELS:
        r = A.trait_pc_corr(m)
        P["models"][m] = {"t": [t.replace("_", " ") for t in r.index],
                          "r": {c: [round(float(v), 4) for v in r[c]] for c in ["PC1", "PC2", "PC3"]}}
    return P


def trait_map_labels(x, y, gap: float = 0.2) -> list:
    """Traits to label: the end of each axis, then the furthest trait along each diagonal, then the next three along each
    axis end; a candidate is kept only if no kept label lies within `gap` (same rule as the page script)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    top = lambda v, k: list(np.argsort(v, kind="stable")[:k])
    ends = lambda k: [top(x, k), top(-x, k), top(y, k), top(-y, k)]
    cand = [i for a in ends(1) for i in a]
    cand += [top(-(a * x + b * y), 1)[0] for a, b in [(1, 1), (1, -1), (-1, 1), (-1, -1)]]
    cand += [i for a in ends(4) for i in a]
    keep = []
    for i in cand:
        if i not in keep and all(np.hypot(x[i] - x[j], y[i] - y[j]) > gap for j in keep):
            keep.append(int(i))
    return keep


def _tm_traces(m: str, ya: str, P: dict, phone: bool = False) -> list:
    D = P["models"][m]
    x, y = np.array(D["r"]["PC1"]), np.array(D["r"][ya])
    R2 = x ** 2 + y ** 2
    L = trait_map_labels(x, y, 0.3 if phone else 0.2)
    pos = lambda i: ("top " if y[i] >= 0 else "bottom ") + ("right" if x[i] >= 0 else "left")
    return [go.Scatter(x=x, y=y, mode="markers", text=D["t"], customdata=np.round(100 * R2), showlegend=False, name="traits",
                       marker=dict(size=6, color=["#b8c0cc" if v < 0.5 else "#5b6b82" for v in R2], opacity=0.85),
                       hovertemplate="<b>%{text}</b><br>r with PC1 %{x:+.2f}<br>r with " + ya
                       + " %{y:+.2f}<br>the two axes explain %{customdata}% of it<extra></extra>"),
            go.Scatter(x=x[L], y=y[L], mode="markers+text", text=[D["t"][i] for i in L], textposition=[pos(i) for i in L],
                       textfont=dict(size=11, color="#1d2430"), marker=dict(size=7, color="#c4501b"), hoverinfo="skip",
                       showlegend=False, name="labelled", cliponaxis=False)]


def trait_map_figure() -> go.Figure:
    """Figure 1.2 (iteration 47): every trait at its r with PC1 (x) and PC2 or PC3 (y). The axes are uncorrelated across the
    characters, so r1² + r2² ≤ 1: the outer circle is the limit, the dashed circle marks half of a trait explained. HTML
    menus (Model, Vertical axis) re-draw it (trait_map_script). The static figure is the opening view, Qwen PC1 x PC2."""
    P = trait_map_payload()
    fig = go.Figure(_tm_traces("qwen", "PC2", P))
    circ = lambda r, dash: dict(type="circle", xref="x", yref="y", x0=-r, y0=-r, x1=r, y1=r,
                                line=dict(color="#9aa3ae" if r == 1 else "#b8c0cc", width=1, dash=dash))
    fig.update_layout(meta="Where the 240 traits sit on each model's main activation axes (r)", template="plotly_white",
                      height=640, margin=dict(l=50, r=10, t=10, b=45), font=dict(size=12),
                      shapes=[circ(1, "solid"), circ(float(np.sqrt(0.5)), "dash")])
    fig.update_xaxes(range=[-1.2, 1.2], constrain="domain", dtick=0.5, title="r with PC1", zerolinecolor="#d0d4da", fixedrange=True)
    fig.update_yaxes(range=[-1.2, 1.2], dtick=0.5, title="r with PC2", zerolinecolor="#d0d4da", scaleanchor="x", fixedrange=True)
    return fig


TM_JS = r"""
function labels(x,y,gap){var n=x.length,idx=[];for(var i=0;i<n;i++)idx.push(i);
  function top(f,k){return idx.slice().sort(function(a,b){return (f(a)-f(b))||(a-b);}).slice(0,k);}
  function ends(k){return [function(i){return x[i];},function(i){return -x[i];},function(i){return y[i];},function(i){return -y[i];}].map(function(f){return top(f,k);});}
  var cand=[];ends(1).forEach(function(a){cand=cand.concat(a);});
  [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(function(ab){cand=cand.concat(top(function(i){return -(ab[0]*x[i]+ab[1]*y[i]);},1));});
  ends(4).forEach(function(a){cand=cand.concat(a);});
  var keep=[];cand.forEach(function(i){if(keep.indexOf(i)<0&&keep.every(function(j){return Math.hypot(x[i]-x[j],y[i]-y[j])>gap;}))keep.push(i);});
  return keep;}
"""


def trait_map_script(fig_id: str) -> str:
    """HTML menus above Figure 1.2 (Model; Vertical axis PC2 or PC3), a caption line with the count of traits the two axes
    explain at least half of, and the script that re-draws the figure. window.TM exposes the state."""
    P = trait_map_payload()
    sel = lambda i, lab, opts: (f"<label>{lab} <select id='{i}'>" + "".join(f"<option value='{v}'>{t}</option>" for v, t in opts)
                                + "</select></label>")
    ctl = ("<div class='pm-ctl' id='tm-ctl'>" + sel("tm-m", "Model", [(m, A.MODEL_LABEL[m]) for m in TM_MODELS])
           + sel("tm-y", "Vertical axis", [("PC2", "PC2"), ("PC3", "PC3")])
           + "</div><div class='phg-small' id='tm-cap' style='margin:2px 0 4px'></div>")
    cfg = json.dumps(dict(responsive=True, displaylogo=False, modeBarButtonsToRemove=["lasso2d", "select2d"]))
    return ("<script>(function(){var P=" + json.dumps(P, separators=(",", ":")) + ",CFG=" + cfg + ";" + TM_JS +
            "var g=document.getElementById('fig-" + fig_id + "');var st={m:'qwen',y:'PC2'};"
            "function $(k){return document.getElementById('tm-'+k);}"
            "function apply(){$('m').value=st.m;$('y').value=st.y;var D=P.models[st.m],x=D.r.PC1,y=D.r[st.y],n=x.length;"
            "var w=g.clientWidth||g.parentNode.clientWidth||700,ph=w<600;"
            "var R2=x.map(function(v,i){return v*v+y[i]*y[i];}),outer=R2.filter(function(v){return v>=0.5;}).length;"
            "$('cap').textContent=P.label[st.m]+': PC1 and '+st.y+' together explain at least half of '+outer+' of the '+n+' traits (outside the dashed circle); '+(n-outer)+' lie inside it.';"
            "var L=labels(x,y,ph?0.3:0.2);function pos(i){return (y[i]>=0?'top ':'bottom ')+(x[i]>=0?'right':'left');}"
            "var t0={type:'scatter',mode:'markers',x:x,y:y,text:D.t,customdata:R2.map(function(v){return Math.round(v*100);}),"
            "marker:{size:ph?5:6,color:R2.map(function(v){return v<0.5?'#b8c0cc':'#5b6b82';}),opacity:0.85},name:'traits',showlegend:false,"
            "hovertemplate:'<b>%{text}</b><br>r with PC1 %{x:+.2f}<br>r with '+st.y+' %{y:+.2f}<br>the two axes explain %{customdata}% of it<extra></extra>'};"
            "var t1={type:'scatter',mode:'markers+text',x:L.map(function(i){return x[i];}),y:L.map(function(i){return y[i];}),"
            "text:L.map(function(i){return D.t[i];}),textposition:L.map(pos),textfont:{size:ph?10:11,color:'#1d2430'},"
            "marker:{size:ph?6:7,color:'#c4501b'},hoverinfo:'skip',showlegend:false,name:'labelled',cliponaxis:false};"
            "var H=Math.round(Math.min(w,720)*(ph?1:0.9)),r=Math.SQRT1_2;"
            "function circ(rr,d){return {type:'circle',xref:'x',yref:'y',x0:-rr,y0:-rr,x1:rr,y1:rr,line:{color:rr===1?'#9aa3ae':'#b8c0cc',width:1,dash:d}};}"
            "var lay={height:H,margin:{l:50,r:10,t:10,b:45},template:g.layout.template,font:{size:12},meta:g.layout.meta,"
            "xaxis:{range:ph?[-1.6,1.6]:[-1.2,1.2],constrain:ph?'range':'domain',dtick:0.5,title:{text:'r with PC1'},zerolinecolor:'#d0d4da',fixedrange:true},"
            "yaxis:{range:[-1.2,1.2],dtick:0.5,title:{text:'r with '+st.y},zerolinecolor:'#d0d4da',scaleanchor:'x',fixedrange:true},"
            "shapes:[circ(1,'solid'),circ(r,'dash')],hoverlabel:{font:{size:12}}};"
            "g.style.height=H+'px';if(g.parentNode&&g.parentNode.style.height)g.parentNode.style.height=H+'px';"
            "Plotly.react(g,[t0,t1],lay,CFG);var wr=document.getElementById('wrap-" + fig_id + "');wr.dataset.model=st.m;wr.dataset.yaxis=st.y;}"
            "function init(){if(!window.Plotly||!g||!g.data||!g._fullLayout){return setTimeout(init,80);}"
            "var d=document.createElement('div');d.innerHTML=" + json.dumps(ctl) + ";var host=g.parentNode;"
            "while(d.firstChild){host.parentNode.insertBefore(d.firstChild,host);}"
            "['m','y'].forEach(function(k){$(k).onchange=function(e){st[k]=e.target.value;apply();};});"
            "var lastW=g.clientWidth;window.addEventListener('resize',function(){if(Math.abs(g.clientWidth-lastW)>20){lastW=g.clientWidth;apply();}});"
            "apply();window.TM={state:st,apply:apply,P:P};}init();})();</script>")
