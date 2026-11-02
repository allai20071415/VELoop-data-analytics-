import sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from veloop_analytics.config import RAW, FILE_A, FILE_B
from veloop_analytics.loaders import load_all
from veloop_analytics import quality, relationships, cleaning
pytestmark = pytest.mark.skipif(not ((RAW / FILE_A).exists() and (RAW / FILE_B).exists()), reason="raw data missing")

@pytest.fixture(scope="module")
def d(): return load_all()

def issue(rows, dataset, field, kind):
    return next(r for r in rows if r["dataset"] == dataset and r["field"] == field and r["issue_type"].startswith(kind))

def test_known_messy_user_issues(d):
    rows = quality.run_all(d)
    assert issue(rows, "A:Users_Messy_Audit", "user_id", "duplicate")["records"] == 8
    assert issue(rows, "A:Users_Messy_Audit", "registration_datetime", "malformed date")["records"] == 1

def test_event_audit_issues(d):
    rows = quality.run_all(d)
    assert issue(rows, "B:10_Event_Data_Quality_Audit", "event_id", "duplicate")["records"] == 10
    assert issue(rows, "B:10_Event_Data_Quality_Audit", "event_status", "trailing")["records"] == 4

def test_no_orphans(d):
    assert all(r["orphans"] == 0 for r in relationships.run_all(d))

def test_cross_file_conflict_found(d):
    cf = {r["field"]: r["users_where_A_differs_from_B"] for r in relationships.cross_file_conflict(d)}
    assert cf["email"] == 1000 and cf["registration_datetime"] == 1000

def test_user_cleaning(d):
    clean, q, s = cleaning.clean_users_messy(d["A:Users_Messy_Audit"])
    assert s["duplicates_removed"] == 8 and clean.user_id.is_unique and len(q) > 0 and len(clean) + len(q) == 1000

def test_event_cleaning(d):
    ev, s = cleaning.clean_events_audit(d["B:10_Event_Data_Quality_Audit"])
    assert ev.event_id.is_unique and (ev.event_status == ev.event_status.str.strip()).all() and s["duplicates_removed"] == 10
    assert ev.feature_name.nunique() == d["B:03_Feature_Events"].feature_name.nunique()
