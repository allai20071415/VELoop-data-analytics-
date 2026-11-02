"""Command line: python run.py {profile|clean|all}"""
import argparse, time
import pandas as pd
from .config import PROCESSED, OUTPUTS, DATASETS
from .loaders import load_all
from . import profiling, relationships, quality, cleaning, report
from .kpi_test import KPI_TEST, KPI_TEST_COLUMNS

def cmd_profile():
    t = time.time(); d = load_all(); OUTPUTS.mkdir(exist_ok=True)
    report.write_workbook(OUTPUTS / "VELOOP_Data_Profiling_and_DQ_Audit.xlsx", {
        "J1_Profile": pd.DataFrame([profiling.profile_dataset(n, d[n]) for n in DATASETS]),
        "J1_Categories_Ranges": pd.DataFrame([r for n in DATASETS for r in profiling.categories_and_ranges(n, d[n])]),
        "J2_Relationships": pd.DataFrame(relationships.run_all(d)),
        "J2_Cross_File_Conflict": pd.DataFrame(relationships.cross_file_conflict(d)),
        "J3_KPI_Test": pd.DataFrame(KPI_TEST, columns=KPI_TEST_COLUMNS),
        "K_DQ_Report": pd.DataFrame(quality.run_all(d))})
    print(f"profile done in {time.time()-t:.1f}s")

def cmd_clean():
    d = load_all(); PROCESSED.mkdir(parents=True, exist_ok=True)
    cu, qu, s1 = cleaning.clean_users_messy(d["A:Users_Messy_Audit"]); ce, s2 = cleaning.clean_events_audit(d["B:10_Event_Data_Quality_Audit"])
    cu.to_csv(PROCESSED / "users_messy_cleaned.csv", index=False); qu.to_csv(PROCESSED / "users_messy_quarantine.csv", index=False)
    ce.to_csv(PROCESSED / "events_audit_cleaned.csv", index=False)
    s = pd.DataFrame([{"dataset": "Users_Messy_Audit", **s1}, {"dataset": "Event_Data_Quality_Audit", **s2}])
    s.to_csv(PROCESSED / "cleaning_summary.csv", index=False); print(s.to_string(index=False))

def main():
    p = argparse.ArgumentParser(prog="veloop_analytics"); p.add_argument("command", choices=["profile", "clean", "all"]); a = p.parse_args()
    if a.command in ("profile", "all"): cmd_profile()
    if a.command in ("clean", "all"): cmd_clean()
