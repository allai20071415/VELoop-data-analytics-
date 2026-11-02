"""Work Package J1: per-dataset profile and category/range summaries."""
import pandas as pd
from .config import DATASETS

_DATE_HINTS = ("datetime", "_at", "date", "session_start", "session_end")
_NUMERIC_KEEP = {"lifetime_sessions", "active_days", "xp_balance", "age", "session_duration_seconds"}

def date_range(df):
    mins, maxs = [], []
    for c in (c for c in df.columns if any(h in c for h in _DATE_HINTS)):
        p = pd.to_datetime(df[c], errors="coerce")
        if p.notna().any():
            mins.append(p.min()); maxs.append(p.max())
    return (min(mins), max(maxs)) if mins else (None, None)

def profile_dataset(name, df):
    pk = DATASETS[name][2]; lo, hi = date_range(df); nulls = df.isna().sum()
    return {"dataset": name, "records": len(df), "columns": df.shape[1],
            "earliest": str(lo)[:19] if lo is not None else "", "latest": str(hi)[:19] if hi is not None else "",
            "unique_ids": "; ".join(f"{c}={df[c].nunique()}" for c in df.columns if c.endswith("_id")),
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_pk": int(df[pk].duplicated().sum()) if pk else "n/a",
            "missing_cells": int(nulls.sum()),
            "missing_by_column": "; ".join(f"{c}:{int(v)}" for c, v in nulls.items() if v) or "none"}

def categories_and_ranges(name, df):
    rows = []
    for c in df.columns:
        s = df[c].dropna()
        if s.empty: continue
        num = pd.to_numeric(s, errors="coerce")
        if (num.notna().mean() > 0.95 and not c.endswith("_id") and "code" not in c) or c in _NUMERIC_KEEP:
            rows.append({"dataset": name, "field": c, "kind": "numeric",
                         "summary": f"min={num.min():g}, max={num.max():g}, mean={num.mean():.2f}, median={num.median():g}"})
        elif s.nunique() <= 30:
            rows.append({"dataset": name, "field": c, "kind": f"{s.nunique()} categories",
                         "summary": "; ".join(f"{k!r}={v}" for k, v in s.value_counts().items())})
    return rows
