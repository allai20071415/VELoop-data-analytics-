"""Work Package J2: referential-integrity tests between datasets."""
def test_fk(parent_name, parent, pk, child_name, child, fk, note=""):
    s = child[fk].dropna(); orphans = int((~s.isin(parent[pk])).sum())
    return {"parent": parent_name, "parent_key": pk, "child": child_name, "child_key": fk,
            "child_rows": len(child), "child_nulls": int(child[fk].isna().sum()), "orphans": orphans,
            "orphan_pct": round(orphans / max(len(s), 1) * 100, 2),
            "parents_without_children": len(set(parent[pk]) - set(s)),
            "result": "PASS" if orphans == 0 else "FAIL", "note": note}

def run_all(d):
    U, S = d["B:01_Users_1000"], d["B:02_Sessions"]; out = []
    for n in ["02_Sessions", "03_Feature_Events", "04_Daily_Activity", "05_Task_Activity", "06_Milestones", "10_Event_Data_Quality_Audit"]:
        out.append(test_fk("B:01_Users_1000", U, "user_id", "B:" + n, d["B:" + n], "user_id"))
    for n in ["03_Feature_Events", "05_Task_Activity", "06_Milestones"]:
        out.append(test_fk("B:02_Sessions", S, "session_id", "B:" + n, d["B:" + n], "session_id"))
    out.append(test_fk("A:Users_1000_Clean", d["A:Users_1000_Clean"], "user_id", "B:02_Sessions", S, "user_id",
                       "IDs match but attributes conflict (see cross-file conflict sheet)"))
    out.append(test_fk("A:Users_1000_Clean", d["A:Users_1000_Clean"], "user_id", "A:Users_Messy_Audit", d["A:Users_Messy_Audit"], "user_id"))
    return out

def cross_file_conflict(d):
    m = d["A:Users_1000_Clean"].merge(d["B:01_Users_1000"], on="user_id", suffixes=("_a", "_b"))
    cols = ["full_name", "email", "age", "gender", "state", "city", "registration_datetime",
            "acquisition_source", "account_status", "onboarding_status", "primary_device", "referral_code"]
    return [{"field": c, "users_where_A_differs_from_B": int((m[c + "_a"] != m[c + "_b"]).sum()), "of": len(m)} for c in cols]
