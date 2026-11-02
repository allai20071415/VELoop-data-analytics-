"""Unit tests on tiny synthetic frames: run without the raw data files."""
import sys, pathlib
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from veloop_analytics import cleaning, relationships, profiling

def _users():
    return pd.DataFrame({
        "user_id": ["U1", "U2", "U2", "U3", "U4"],
        "registration_datetime": ["2026-04-01 10:00:00", "2026-04-02 10:00:00", "2026-04-02 10:00:00", "2026-14-02 12:00:00", "2026-04-04 10:00:00"],
        "acquisition_source": ["Organic", "Organic", "Organic", "Organic", None],
        "primary_device": ["Android"] * 5, "email_verification_status": ["Verified"] * 5, "onboarding_status": ["Completed"] * 5,
        "age": ["20"] * 5, "gender": ["F"] * 5, "city": ["Chennai"] * 5})

def test_user_cleaning_dedupes_and_quarantines():
    clean, quarantine, s = cleaning.clean_users_messy(_users())
    assert s["duplicates_removed"] == 1
    assert set(quarantine.user_id) == {"U3", "U4"}      # malformed date, missing required value
    assert list(clean.user_id) == ["U1", "U2"]
    assert s["input_rows"] == s["duplicates_removed"] + s["quarantined"] + s["clean_rows"]

def test_event_cleaning_normalises_and_dedupes():
    df = pd.DataFrame({"event_id": ["E1", "E1", "E2", "E3"], "event_status": ["Success", "Success", "success ", "Failed"],
                       "feature_name": ["Missions", "Missions", "missions", "Wallet"]})
    out, s = cleaning.clean_events_audit(df)
    assert out.event_id.is_unique and set(out.event_status) == {"Success", "Failed"}
    assert set(out.feature_name) == {"Missions", "Wallet"} and s["duplicates_removed"] == 1

def test_fk_detects_orphans():
    parent = pd.DataFrame({"user_id": ["U1", "U2", "U3"]}); child = pd.DataFrame({"user_id": ["U1", "U1", "U9", None]})
    r = relationships.test_fk("p", parent, "user_id", "c", child, "user_id")
    assert r["orphans"] == 1 and r["child_nulls"] == 1 and r["parents_without_children"] == 2 and r["result"] == "FAIL"

def test_fk_passes_when_clean():
    parent = pd.DataFrame({"user_id": ["U1"]}); child = pd.DataFrame({"user_id": ["U1"]})
    assert relationships.test_fk("p", parent, "user_id", "c", child, "user_id")["result"] == "PASS"

def test_profile_counts_duplicates_and_missing():
    df = pd.DataFrame({"user_id": ["U1", "U1", "U2"], "registration_datetime": ["2026-04-01", "2026-04-01", None]})
    p = profiling.profile_dataset("A:Users_1000_Clean", df)
    assert p["records"] == 3 and p["duplicate_rows"] == 1 and p["duplicate_pk"] == 1 and p["missing_cells"] == 1
