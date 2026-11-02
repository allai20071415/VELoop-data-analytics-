"""Central configuration: file names, sheet roles, reference dates."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"

FILE_A = "1793188481774_VELoop_Rewards_Data_01.xlsx"                # Users (clean + messy)
FILE_B = "1793188525986_VELOOP_Simulated_User_Behavior_1000.xlsx"  # behaviour dataset ("Task 02")
PERIOD_END = pd.Timestamp("2026-09-15")                             # stated in both dataset READMEs

# logical name -> (file, sheet, primary id or None)
DATASETS = {
    "A:Users_1000_Clean":            (FILE_A, "Users_1000_Clean", "user_id"),
    "A:Users_Messy_Audit":           (FILE_A, "Users_Messy_Audit", "user_id"),
    "B:01_Users_1000":               (FILE_B, "01_Users_1000", "user_id"),
    "B:02_Sessions":                 (FILE_B, "02_Sessions", "session_id"),
    "B:03_Feature_Events":           (FILE_B, "03_Feature_Events", "event_id"),
    "B:04_Daily_Activity":           (FILE_B, "04_Daily_Activity", None),
    "B:05_Task_Activity":            (FILE_B, "05_Task_Activity", "activity_id"),
    "B:06_Milestones":               (FILE_B, "06_Milestones", None),
    "B:10_Event_Data_Quality_Audit": (FILE_B, "10_Event_Data_Quality_Audit", "event_id"),
}
