"""Reference cleaning rules. Rows that cannot be fixed safely are QUARANTINED, never silently altered."""
import pandas as pd

def clean_users_messy(df):
    before = len(df); out = df.drop_duplicates(subset="user_id", keep="first").copy()
    bad_date = pd.to_datetime(out.registration_datetime, errors="coerce").isna()
    required = ["registration_datetime", "acquisition_source", "primary_device", "email_verification_status", "onboarding_status", "age", "gender", "city"]
    quarantine = out[bad_date | out[required].isna().any(axis=1)]; clean = out.drop(quarantine.index)
    return clean, quarantine, {"input_rows": before, "duplicates_removed": before - len(out), "quarantined": len(quarantine), "clean_rows": len(clean)}

def clean_events_audit(df):
    before = len(df); out = df.drop_duplicates(subset="event_id", keep="first").copy()
    out["event_status"] = out.event_status.str.strip().str.capitalize()
    # canonical feature names are taken from the data itself: the most frequent spelling per lower-case key
    canon = df.assign(k=df.feature_name.str.strip().str.lower()).groupby("k").feature_name.agg(lambda s: s.str.strip().value_counts().index[0]).to_dict()
    out["feature_name"] = out.feature_name.str.strip().map(lambda x: canon.get(x.lower(), x))
    return out, {"input_rows": before, "duplicates_removed": before - len(out),
                 "status_normalised": int((df.event_status != df.event_status.str.strip()).sum()), "clean_rows": len(out)}
