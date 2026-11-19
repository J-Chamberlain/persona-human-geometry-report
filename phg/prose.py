"""Reader-facing prose lives in research/notebooks/prose.md, not in code.

Format: ``## <key>`` starts an entry (a section such as ``section.4`` or a
result such as ``4.1``); ``### <slot>`` starts a slot. HTML comments are
ignored. Empty slots are omitted from the report and listed in
EDITORIAL_TRACKER.md.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import sources

PROSE_FILE = sources.ROOT / "report" / "prose.md"
SLOTS = ("lead", "how_to_read", "shows", "limitation")
SECTION_SLOTS = ("lead",)
OUTLINE_SLOTS = ("outline",)

# Every key the report renders, in reading order, with a short label for the tracker.
ENTRIES = [
    ("summary", "Introduction (body text)"),
    ("H", "4.1 Trait pairs: Qwen links some traits as people do, and reverses others (former headline figure)"),
    ("section.1", "1 The persona landscape"),
    ("1.1", "What the main activation axes separate"),
    ("chars", "1 Characters that personify the axes (body text)"),
    ("tmap", "1.2 Where the 240 traits sit on each model's main activation axes"),
    ("1.2", "1.3 Exploring the persona landscape (Persona Landscape Explorer)"),
    ("1.3", "3.1 People and the three models through the Big Five"),
    ("section.2", "2 The three models arrange traits in largely the same way"),
        ("2.1", "Main activation axes compared between models"),
    ("2.2", "Character scores compared between models, per trait"),
    ("2.3", "Consensus directions C1-C5 and each model's activation axes"),
    ("section.sapa", "3 Do people arrange the traits the same way? (SAPA bridge)"),
    ("section.3", "4 Measuring the Big Five facets directly inside Qwen"),
    ("s3.1", "4 How each facet was extracted (body text)"),
    ("3.2", "Where the facets sit in Qwen\'s geometry"),
    ("4.2", "Correlation matrices and domain averages"),
    ("4.3", "Predicting real people's scores (held-out R² per facet)"),
    ("4.4", "4 Closing notes after Figure 4.2 (body text)"),
    ("section.5", "5 Case study: why do Friendliness and Anger go together in Qwen?"),
    ("5a", "Unusual personas? (influence)"),
    ("5b", "Response style? (Friendliness vs Anger by Formal)"),
    ("5c", "Where in the geometry? (C/T/F projected vs residual)"),
    ("5d.1", "Questionnaire wording: Friendliness and Anger items"),
    ("5d.2", "Anger items vs Friendliness and Assertiveness"),
    ("5d.3", "Friendliness by Anger level"),
    ("5e.1", "Other models: historical relationships"),
    ("5e.2", "PHG-CM01 focal relationships"),
    ("5e.3", "Trait–factor patterns, Qwen F1 vs Llama F1 / Gemma F3"),
    ("discussion.0", "5 Discussion opening (body text)"),
    ("discussion", "5 Discussion after Figure 5.1 (body text)"),
    ("6.1", "6.1 Big Five domain correlations: people, model answers, model activations"),
    ("limitations", "7 Limitations"),
    ("related", "8 Related work"),
    ("open", "9 Open questions and next steps"),
    ("about", "About this work"),
    ("section.E", "Appendix E: Technical explorations"),
    ("E.1", "Appendix E: calibration slider (earlier nine-facet experiment)"),
    ("E.2", "Appendix E: how well each facet fits its domain"),
    ("E.4", "Appendix E: each model's own trait factors (AA17)"),
    ("G.1", "Appendix G: trait-pair correlations (Figure G.1)"),
    ("G.2", "Appendix G: persona scores (pointer to Figure 2.2)"),
    ("G.3", "Appendix G: main activation axes (pointer to Figure 2.1)"),
    ("elbow", "G.3a How much of the variation among characters the activation axes carry"),
    ("G.3b", "Appendix G: PC1 scatter (Figure 2.2 candidate)"),
    ("G.4", "Appendix G: factor matching"),
    ("G.5", "Appendix G: consensus directions C1-C5"),
    ("G.6", "Appendix G: beyond personas"),
    ("G.7", "Appendix G: not yet compared"),
    ("method.extraction", "Appendix A.14 Facet extraction and the convergence rule (body text)"),
]
OUTLINE_KEYS: set = set()  # iteration 49: every former outline is written text (BODY_KEYS)


# Iteration 39: running text in several paragraphs (blank line between paragraphs), rendered as ordinary body text.
BODY_KEYS = {"chars", "summary", "discussion.0", "s3.1", "4.4", "discussion", "limitations", "related", "open", "about",
             "method.extraction"}
BODY_SLOTS = ("body",)


def slots_for(key: str) -> tuple[str, ...]:
    if key in BODY_KEYS:
        return BODY_SLOTS
    if key in OUTLINE_KEYS:
        return OUTLINE_SLOTS
    return SECTION_SLOTS if key.startswith("section.") else SLOTS


def parse(text: str) -> dict[str, dict[str, str]]:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out: dict[str, dict[str, str]] = {}
    key = slot = None
    buf: list[str] = []

    def flush():
        if key and slot:
            out.setdefault(key, {})[slot] = "\n".join(buf).strip()

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            key, slot, buf = line[3:].strip(), None, []
            out.setdefault(key, {})
        elif line.startswith("### "):
            flush()
            slot, buf = line[4:].strip(), []
        elif slot:
            buf.append(line)
    flush()
    return out


def load(path: Path = PROSE_FILE) -> dict[str, dict[str, str]]:
    return parse(Path(path).read_text()) if Path(path).exists() else {}


def get(key: str, slot: str, prose: dict | None = None) -> str:
    prose = load() if prose is None else prose
    return prose.get(key, {}).get(slot, "").strip()


def template() -> str:
    lines = ["# Report prose", "",
             "<!-- One entry per section or result. Write plain text under each ### slot.",
             "     Empty slots are left out of the report and listed in EDITORIAL_TRACKER.md.",
             "     lead: one or two sentences above the figure. how_to_read: caption under it.",
             "     shows / limitation: the evidence panel. -->", ""]
    for key, label in ENTRIES:
        lines += [f"## {key}", f"<!-- {label} -->"]
        for s in slots_for(key):
            lines += [f"### {s}", ""]
        lines.append("")
    return "\n".join(lines)


def tracker(prose: dict, skeleton_sections: dict[str, list[str]]) -> str:
    lines = ["# Editorial tracker", "",
             "Generated by `python research/notebooks/build_notebook.py` from `prose.md`. Empty slots are omitted from",
             "the report; fill them in `prose.md` and rebuild. Outline slots render in a \"Draft outline\" box only when the",
             "build flag DRAFT is on (default); with DRAFT off they are omitted.", "",
             "## Standing conventions", "",
             "- **No repeated figures in the appendices** (iteration 15). An appendix never redraws a figure whose design",
             "  already appears in the body, even with different data. It links to the body figure (\"see Figure 4.2\") and",
             "  gives the differing values as a table. A new appendix figure is allowed only when it shows something no body",
             "  figure shows.",
             "- **Figure moves follow the same rule** (iteration 16): the activation-axes heatmap is Figure 2.1 and Appendix G.3",
             "  links to it; the trait-pair density figure is Figure G.1 and is not repeated in Section 2. Iteration 17: the",
             "  per-trait character-score figure is Figure 2.2 and Appendix G.2 links to it.",
             "- **Build stamp and publishing** (iteration 15). The page carries \"Iteration N · <source commit> · <date>\" at the",
             "  top, and each iteration is republished to the existing artifact https://claude.ai/artifact/KjYMB8y1amsifp7XhRRwBY",
             "  (never a new one).", "",
             "## Outline slots", "", "| Key | Section | Status |", "|---|---|---|"]
    for key, label in ENTRIES:
        if key in OUTLINE_KEYS:
            text = get(key, "outline", prose)
            status = f"draft outline ({len([l for l in text.splitlines() if l.startswith('- ')])} bullets)" if text else "empty"
            lines.append(f"| `{key}` | {label} | {status} |")
    lines += ["", "## Empty prose slots", "", "| Key | Result | Empty slots |", "|---|---|---|"]
    n_empty = n_total = 0
    for key, label in ENTRIES:
        if key in OUTLINE_KEYS:
            continue
        empty = [s for s in slots_for(key) if not get(key, s, prose)]
        n_empty += len(empty)
        n_total += len(slots_for(key))
        if empty:
            lines.append(f"| `{key}` | {label} | {', '.join(empty)} |")
    lines += ["", f"{n_empty} of {n_total} non-outline slots are empty.", "", "## Skeleton sections", "",
              "These sections have headings (and outline slots) only; their planned figures are listed in INVENTORY.md.", ""]
    for sec, figs in skeleton_sections.items():
        lines.append(f"- **Section {sec}**: " + "; ".join(figs))
    lines.append("")
    return "\n".join(lines)
