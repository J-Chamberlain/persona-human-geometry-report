"""Persona Landscape Explorer: data assembly from saved inputs only.

No PCA or factor model is refitted and no new association table is computed.
Inputs (snapshot, pinned at main 65da790):
  persona_pcs      saved model-local persona PCA scores (PC1-PC6 of saved PC1-PC10)
  role_coords      terrain-viewer native PC1-PC3 (cross-check)
  traits_*         saved 275 x 240 historical trait cosine matrices
  pc_trait_qwen_ext  saved Qwen PC4-PC13 x 240-trait Pearson associations
  pca_xmodel       saved cross-model persona PC score correlations
The only computation is within-model standardization of trait scores (z across
the 275 personas, population SD) for display.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from . import sources as S

MODELS = ["qwen", "gemma", "llama"]  # iteration 27: Qwen, Gemma, Llama order
MODEL_LABEL = {"qwen": "Qwen", "llama": "Llama", "gemma": "Gemma"}
XMODEL_NAME = {"qwen": "Qwen/Qwen3-32B", "llama": "Llama-3.3-70B", "gemma": "Gemma-2-27B"}
N_PCS = 6
TAG_TRAITS = 3
SCALE = 10000  # embedded values are integers = value x 1e4 (4 decimals)
DEFAULT_RULE = ("Persona A and B are the characters at the two extremes of Qwen PC1 (A lowest, B highest) among the "
                "130 characters in the frozen ordinary-role subset (outlier diagnostics, c556609).")


@lru_cache(None)
def traits_raw(model: str) -> pd.DataFrame:
    return S.csv(f"traits_{model}").set_index("persona")


def zscore(raw: pd.DataFrame) -> pd.DataFrame:
    """Within-model standardization: z across the 275 personas (population SD)."""
    return (raw - raw.mean(axis=0)) / raw.std(axis=0, ddof=0)


@lru_cache(None)
def pcs(model: str) -> pd.DataFrame:
    p = S.csv("persona_pcs")
    return p[p.model == model].set_index("persona")[[f"pc{k}" for k in range(1, N_PCS + 1)]]


def persona_order() -> list[str]:
    return list(traits_raw("qwen").index)


def trait_order() -> list[str]:
    return list(traits_raw("qwen").columns)


def axis_tags() -> dict[str, dict[int, str]]:
    """Short axis tags for the explorer: three traits at each end. Iteration 27: PC1-PC3 for every model come from the
    Figure 1.1 axis guide (computed in this notebook); Qwen PC4-PC6 keep the saved 240-trait table."""
    from . import analysis as A
    a = S.csv("pc_trait_qwen_ext")
    out: dict[str, dict[int, str]] = {m: {} for m in MODELS}
    for k in range(1, N_PCS + 1):
        g = a[a.component == k]
        if g.empty:
            continue
        g = g.sort_values("pearson_correlation")
        low = ", ".join(g.trait.head(TAG_TRAITS))
        high = ", ".join(g.trait.tail(TAG_TRAITS).iloc[::-1])
        out["qwen"][k] = f"{low} ↔ {high}".replace("_", " ")
    for m in MODELS:
        gd = A.axis_guide(m, k=3, n=TAG_TRAITS)
        for row in gd.itertuples():
            out[m][int(row.axis[2:])] = f"{', '.join(row.low)} ↔ {', '.join(row.high)}".replace("_", " ")
    return out


def xmodel_pc1() -> dict[str, float]:
    d = S.csv("pca_xmodel")
    d = d[(d.reference_component == 1) & (d.target_component == 1)]
    out = {}
    for m in ["llama", "gemma"]:
        out[f"qwen-{m}"] = float(d[d.target_model == XMODEL_NAME[m]].pearson_correlation.iloc[0])
    return out


def default_pair() -> tuple[str, str]:
    cls = S.csv("od_persona_class", keep_default_na=False).set_index("persona")
    ordinary = cls.index[cls.ordinary_role_subset.astype(str).str.lower() == "true"]
    pc1 = pcs("qwen").loc[ordinary, "pc1"]
    return str(pc1.idxmin()), str(pc1.idxmax())


def _ints(a: np.ndarray) -> list:
    return np.rint(np.asarray(a, float) * SCALE).astype(int).tolist()


def payload() -> dict:
    personas = persona_order()
    traits = trait_order()
    data = dict(scale=SCALE, personas=personas, traits=[t.replace("_", " ") for t in traits], models={}, tags=axis_tags(), xmodel=xmodel_pc1(),
                default=list(default_pair()), labels=MODEL_LABEL, n_pcs=N_PCS)
    for m in MODELS:
        raw = traits_raw(m).loc[personas, traits]
        # Standardized scores only (raw cosine is described in Appendix A, not embedded).
        data["models"][m] = dict(pcs=_ints(pcs(m).loc[personas].to_numpy()), z=_ints(zscore(raw).to_numpy()))
    return data
