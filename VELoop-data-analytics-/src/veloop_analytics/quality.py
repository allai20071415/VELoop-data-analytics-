"""Work Packages K/L: data-quality checks. Each check is a small function returning Issue objects."""
from dataclasses import dataclass, asdict
import pandas as pd
from .config import PERIOD_END
from .relationships import cross_file_conflict

@dataclass
class Issue:
    dataset: str; field: str; issue_type: str; records: int; severity: str
    detection: str; likely_cause: str; correction: str; prevention: str; owner: str; status: str = "Open"

def check_users_messy(d):
    um, uc = d["A:Users_Messy_Audit"], d["A:Users_1000_Clean"]
    out = [Issue("A:Users_Messy_Audit", "user_id", "duplicate IDs / duplicate rows", int(um.user_id.duplicated().sum()), "High",
                 f"user_id repeated; exact duplicate rows={int(um.duplicated().sum())}; IDs affected={um[um.user_id.duplicated(keep=False)].user_id.nunique()}",
                 "Double load or retry", "Keep first occurrence, quarantine copies", "UNIQUE constraint / ingestion dedup", "Engineering")]
    sev = {"age": "Medium", "gender": "Low", "city": "Medium", "registration_datetime": "Critical", "acquisition_source": "Medium",
           "primary_device": "Medium", "email_verification_status": "High", "onboarding_status": "High"}
    for c, s in sev.items():
        n = int(um[c].isna().sum() - uc[c].isna().sum())
        if n:
            out.append(Issue("A:Users_Messy_Audit", c, "unexpected null in required field", n, s, f"required field null (clean baseline has {int(uc[c].isna().sum())})",
                             "Missing capture or failed write", "Backfill from source; never impute silently", "Required-field check at app + ingestion", "Engineering"))
    n = int(um.drop_duplicates("user_id").last_login_datetime.isna().sum() - uc.last_login_datetime.isna().sum())
    if n:
        out.append(Issue("A:Users_Messy_Audit", "last_login_datetime", "unexpected null", n, "Medium",
                         "null where account is not Pending Verification (all clean nulls are Pending Verification)", "Login not recorded", "Recover from login events", "Require last_login for non-pending accounts", "Engineering"))
    n = int(pd.to_datetime(um.registration_datetime.dropna(), errors="coerce").isna().sum())
    if n:
        out.append(Issue("A:Users_Messy_Audit", "registration_datetime", "malformed date", n, "Critical", "value does not parse as a date (e.g. month 14)",
                         "Format / day-month swap", "Quarantine and correct from source", "ISO-8601 validation at ingestion", "Engineering"))
    m = um.drop_duplicates("user_id").merge(uc, on="user_id", suffixes=("", "_c"))
    ok = pd.to_datetime(m.registration_datetime, errors="coerce").notna()
    dv = m[ok & (m.registration_datetime != m.registration_datetime_c)]
    if len(dv):
        out.append(Issue("A:Users_Messy_Audit", "registration_datetime", "value conflicts with clean baseline", len(dv), "High",
                         "valid timestamp differs from clean sheet: " + ", ".join(dv.user_id), "Manual edit / wrong source",
                         "Investigate; clean sheet is baseline only if confirmed", "Immutable registration time + audit log", "Engineering/Data"))
    return out

def check_users_clean(d):
    uc = d["A:Users_1000_Clean"]; out = []
    ll = pd.to_datetime(uc.last_login_datetime); n = int((ll > PERIOD_END + pd.Timedelta(days=1)).sum())
    if n: out.append(Issue("A:Users_1000_Clean", "last_login_datetime", "date after dataset period end (15 Sep 2026)", n, "Medium",
                           f"last_login > 2026-09-15 23:59:59 (max {ll.max()})", "Period end not enforced / later extract", "Define cut-off, clip or flag", "event time <= extract time", "Data"))
    ds = pd.to_numeric(uc.days_since_registration); n = int((ds < 0).sum())
    if n: out.append(Issue("A:Users_1000_Clean", "days_since_registration", "negative value", n, "Medium", f"< 0 (min {ds.min():.1f})",
                           "Reference date earlier than registration", "Compute from documented as-of timestamp", "Parameterised as-of date in transformation", "Data"))
    out.append(Issue("A:Users_1000_Clean", "(table)", "personal data present beyond need", len(uc), "High",
                     "full_name, email, age, gender, city present for every row", "Source includes profile attributes",
                     "Drop from analytics layer; keep user_id and coarse attributes", "Column-level access; drop PII at ingestion", "Data/Engineering"))
    return out

def check_users_b(d):
    U = d["B:01_Users_1000"]; dup = U[U.referral_code.duplicated(keep=False)]
    out = [Issue("B:01_Users_1000", "referral_code", "duplicate IDs (codes should be unique)", int(U.referral_code.duplicated().sum()), "High",
                 "shared by: " + "; ".join(f"{k}->{','.join(g.user_id)}" for k, g in dup.groupby("referral_code")), "Code collision", "Regenerate", "UNIQUE constraint", "Engineering")]
    cf = cross_file_conflict(d)
    out.append(Issue("A vs B", "user_id (cross-file)", "conflicting attributes for identical user_ids", 1000, "Critical",
                     "same 1000 IDs in both files; " + ", ".join(f"{r['field']} differs {r['users_where_A_differs_from_B']}" for r in cf),
                     "Two populations reuse the ID range", "Declare one user master; never join the two", "Single user master + ID governance", "Data (decision)/Engineering"))
    return out

def check_behaviour(d):
    U, S, E, D = d["B:01_Users_1000"], d["B:02_Sessions"], d["B:03_Feature_Events"], d["B:04_Daily_Activity"]
    T, M = d["B:05_Task_Activity"], d["B:06_Milestones"]; out = []
    cnt = E.groupby("session_id").size().reindex(S.session_id).fillna(0).astype(int).values
    out.append(Issue("B:02_Sessions", "events_in_session", "aggregate cannot be reconciled with Feature_Events", int((S.events_in_session.astype(int).values != cnt).sum()), "High",
                     "events_in_session != COUNT(events)", "Independently generated aggregate", "Recompute from events", "Derive counts in transformation", "Data"))
    out.append(Issue("B:02_Sessions", "session_id", "sessions with no events", int((~S.session_id.isin(E.session_id)).sum()), "Medium",
                     "session without Feature_Events rows", "Event loss or empty sessions", "Investigate", "Session-to-event reconciliation rule", "Engineering"))
    inactive = set(U.user_id) - set(S.user_id)
    out.append(Issue("B:01_Users_1000", "user_id", "users with no sessions/events/tasks", len(inactive), "Low", "user_id absent from Sessions", "Registered, never active (plausible)", "None", "-", "Data"))
    out.append(Issue("B:06_Milestones", "user_id", "milestones for users with no activity", int(M.user_id.isin(inactive).sum()), "Medium", "milestone rows for users absent from Sessions", "Milestones generated independently", "Validate against source events", "Milestone must reference a source event", "Data"))
    out.append(Issue("B:06_Milestones", "session_id", "missing session reference", int(M.session_id.isna().sum()), "Medium", "session_id null", "Not tied to a session", "Populate or document", "Required reference", "Engineering"))
    cc, tc = pd.to_numeric(D.completed_task_count), pd.to_numeric(D.task_count)
    out.append(Issue("B:04_Daily_Activity", "completed_task_count", "impossible value (completed > total)", int((cc > tc).sum()), "High", "completed_task_count > task_count", "Independent counters", "Recompute from Task_Activity", "completed <= total rule", "Data"))
    sd = S.assign(d=pd.to_datetime(S.session_start).dt.normalize()).groupby(["user_id", "d"]).size().reset_index(name="n")
    x = D.assign(dt=pd.to_datetime(D.activity_date)).merge(sd, left_on=["user_id", "dt"], right_on=["user_id", "d"], how="left")
    out.append(Issue("B:04_Daily_Activity", "session_count", "does not match Sessions", int((x.n.fillna(0) != pd.to_numeric(x.session_count)).sum()), "Medium",
                     f"session_count != COUNT(sessions per user-day); {int(x.n.isna().sum())} rows have no session", "Independent aggregation", "Rebuild from Sessions", "Derive aggregates from facts", "Data"))
    out.append(Issue("B:05_Task_Activity", "task_id", "one task_id mapped to several categories", int(T.groupby("task_id").task_category.nunique().gt(1).sum()), "High",
                     f"task_id with >1 category (of {T.task_id.nunique()})", "No task catalogue", "Create Tasks master table", "Catalogue + FK", "Product/Engineering"))
    bad = ((T.task_status == "Failed") & (T.failure_reason == "User exited")) | ((T.task_status == "Abandoned") & T.failure_reason.isin(["Validation failed", "Task unavailable", "Timeout"]))
    out.append(Issue("B:05_Task_Activity", "failure_reason", "status/reason contradiction", int(bad.sum()), "Medium", "Failed+'User exited' or Abandoned+system reason", "Reason not constrained by status", "Define allowed reason per status", "Status-reason matrix", "Product/Data"))
    out.append(Issue("B:05_Task_Activity", "reward amount / unit", "missing required analytical field", len(T), "High", "no reward_amount / reward_unit column", "Not in structure", "Add reward_amount, reward_unit, reward_id", "Reward linkage in schema", "Engineering"))
    out.append(Issue("B:03_Feature_Events", "sequence_number", "not unique within session", int(E.duplicated(["session_id", "sequence_number"]).sum()), "Medium", "duplicate (session_id, sequence_number)", "Not a true ordering key", "Order by event_datetime + event_id", "Strictly increasing sequence", "Engineering"))
    out.append(Issue("B:03_Feature_Events", "event_status", "'Started' used for view-type events", int((E.event_status == "Started").sum()), "Low", "views carry status Started", "Status mixes view and attempt", "Separate event class", "Event taxonomy standard", "Product/Data"))
    return out

def check_event_audit(d):
    E, EA = d["B:03_Feature_Events"], d["B:10_Event_Data_Quality_Audit"]
    m = EA.drop_duplicates("event_id").merge(E, on="event_id", suffixes=("", "_o"))
    return [
        Issue("B:10_Event_Data_Quality_Audit", "event_id", "duplicate events", int(EA.event_id.duplicated().sum()), "High", "same event_id and full row repeated", "Retry / double send", "Keep first by event_id", "Dedup on event_id at ingestion", "Engineering"),
        Issue("B:10_Event_Data_Quality_Audit", "event_status", "trailing spaces / inconsistent value", int((EA.event_status != EA.event_status.str.strip()).sum()), "Medium", "'success ' vs 'Success'", "Unnormalised client value", "TRIM + case-normalise", "Enum validation", "Engineering"),
        Issue("B:10_Event_Data_Quality_Audit", "feature_name", "inconsistent capitalization", int((m.feature_name != m.feature_name_o).sum()), "Medium", "differs from Feature_Events for same event_id", "Unnormalised client value", "Map to approved list", "Enum validation", "Engineering")]

def check_dictionaries(d):
    dA = d["A:Data_Dictionary"].field_name.tolist(); miss = [c for c in d["A:Users_1000_Clean"].columns if c not in dA]
    dB = d["B:08_Data_Dictionary"]
    names = {"Users": "B:01_Users_1000", "Sessions": "B:02_Sessions", "Events": "B:03_Feature_Events", "Daily Activity": "B:04_Daily_Activity", "Tasks": "B:05_Task_Activity", "Milestones": "B:06_Milestones"}
    nB = sum(len([c for c in d[v].columns if c not in dB[dB.dataset == k].field_name.tolist()]) for k, v in names.items())
    return [Issue("A:Data_Dictionary", "(coverage)", "field in data not in dictionary", len(miss), "Low", "missing: " + ", ".join(miss), "Dictionary not updated", "Add fields", "Dictionary versioning", "Data"),
            Issue("B:08_Data_Dictionary", "(coverage)", "fields in data not in dictionary", nB, "Low", f"dictionary lists {len(dB)} fields for 6 sheets; FKs/flags undocumented", "Partial dictionary", "Complete it", "Dictionary versioning", "Data")]

def run_all(d):
    issues = []
    for fn in (check_users_messy, check_users_clean, check_users_b, check_behaviour, check_event_audit, check_dictionaries):
        issues += fn(d)
    return [{"issue_id": f"DQ-{k:03d}", **asdict(i)} for k, i in enumerate(issues, 1)]
