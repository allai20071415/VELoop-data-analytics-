"""Build the handover presentation. Run: python scripts/build_presentation.py"""
import pathlib, json
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
ROOT = pathlib.Path(__file__).resolve().parents[1]; FIG = ROOT / "figures"
NAVY, GREY, LIGHT = RGBColor(0x1F, 0x38, 0x64), RGBColor(0x6B, 0x72, 0x80), RGBColor(0xEE, 0xF2, 0xF8)
dq = pd.read_excel(ROOT / "outputs" / "VELOOP_Data_Profiling_and_DQ_Audit.xlsx", sheet_name="K_DQ_Report", header=2)
sev = dq.severity.value_counts()
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]
def tb(sl, x, y, w, h, text, size=16, bold=False, color=RGBColor(0x11, 0x18, 0x27), align=None):
    box = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = box.text_frame; tf.word_wrap = True
    lines = text if isinstance(text, list) else [text]
    for i, l in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); r = p.add_run(); r.text = l; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = "Arial"
        p.space_after = Pt(6)
        if align: p.alignment = align
    return box
def slide(title, note=None):
    sl = prs.slides.add_slide(blank)
    bar = sl.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.9)); bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    tb(sl, 0.5, 0.15, 12.3, 0.6, title, 26, True, RGBColor(255, 255, 255))
    tb(sl, 0.5, 7.05, 12.3, 0.35, "SIMULATED DATA / PROPOSED DESIGN. Not actual VELOOP results.", 10, False, GREY)
    if note: sl.notes_slide.notes_text_frame.text = note
    return sl
def bullets(sl, items, x=0.6, y=1.2, w=12.0, size=18):
    tb(sl, x, y, w, 5.6, ["\u2022  " + i for i in items], size)
def card(sl, x, y, w, h, big, small):
    s = sl.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h)); s.fill.solid(); s.fill.fore_color.rgb = LIGHT; s.line.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
    tb(sl, x + 0.15, y + 0.1, w - 0.3, 0.8, big, 30, True, NAVY); tb(sl, x + 0.15, y + 0.95, w - 0.3, h - 1.0, small, 13, False, GREY)

# 1 title
sl = prs.slides.add_slide(blank); bg = sl.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height); bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
tb(sl, 0.8, 2.2, 11.5, 1.2, "VELOOP Rewards", 48, True, RGBColor(255, 255, 255))
tb(sl, 0.8, 3.4, 11.5, 1.0, "Product Analytics, Data Readiness & Data Management Blueprint", 24, False, RGBColor(255, 255, 255))
tb(sl, 0.8, 4.6, 11.5, 1.2, ["Data Analyst Internship, Task 01. Handover presentation", "All data analysed is fictional/simulated (SIMULATED DATA - CREATED FOR ANALYTICAL TESTING)"], 15, False, RGBColor(0xCB, 0xD5, 0xE1))
# 2 objective
sl = slide("What this project had to answer")
bullets(sl, ["What should VELOOP collect?", "How should it be structured?", "How do we know the data is trustworthy?", "What should management measure?", "What should engineering implement?", "What should a future analytics team be able to see?",
             "Constraint: no real production volume exists, so the goal is a reliable, traceable foundation, not impressive numbers."])
# 3 what was built
sl = slide("What was built")
for i, (b, s) in enumerate([("38", "proposed events, object_action naming"), ("100", "data dictionary fields"), ("46", "KPIs, no invented targets"), ("34", "data quality issues found, with counts"), ("7", "dashboards, 28 visuals, wireframed"), ("15", "developer requirements with acceptance tests")]):
    card(sl, 0.6 + (i % 3) * 4.15, 1.3 + (i // 3) * 2.8, 3.9, 2.5, b, s)
# 4 data received
sl = slide("What the simulated data pack contained")
bullets(sl, ["Received: two workbooks. Users (clean 1,000 rows and messy 1,008 rows) and behaviour data (7,913 sessions, 35,704 events, 9,846 task attempts, 4,799 milestones).",
             "Not supplied: Rewards, Wallet, Withdrawals, Referrals tables. Their KPIs stay design-only.",
             "The behaviour file calls itself 'Task 02'; used as extra simulated data. Needs confirmation.",
             "Period stated in the files: 1 April to 15 September 2026."], size=18)
# 5 ER
sl = slide("Logical data model"); sl.shapes.add_picture(str(FIG / "er_diagram.png"), Inches(0.9), Inches(1.0), height=Inches(5.95))
# 6 findings
sl = slide("Key findings from profiling and audit")
bullets(sl, ["Two Users tables use the same 1,000 IDs but disagree on every user's attributes. A master must be chosen.",
             "Relationships are sound: 0 orphan user or session references; 16 users never active.",
             "No reward amount or unit, and no task catalogue: all 80 task_ids map to several categories.",
             "Stored counts do not reconcile: events_in_session wrong for 7,537 of 7,913 sessions; 423 daily rows with completed > total tasks.",
             "Messy sheets: 8 duplicate users, 9 missing required values, 1 malformed date; 10 duplicate events.",
             "Personal data (name, email, age, gender, city) present for all users, against data minimisation."], size=17)
# 7 severity chart
sl = slide("34 data quality issues by severity")
for i, k in enumerate(["Critical", "High", "Medium", "Low"]): card(sl, 0.6 + i * 3.1, 1.4, 2.9, 2.0, str(int(sev.get(k, 0))), k)
bullets(sl, ["Every issue has detection logic, likely cause, correction, prevention and owner (sheet K_DQ_Report).", "Cleaning keeps traceability: input rows = clean + quarantined + removed duplicates. Unsafe rows are quarantined, never imputed.", "11 automated tests pass and guard the known counts."], y=3.8, size=17)
# 8 KPI test
sl = slide("Can the proposed KPIs be calculated from this data?")
bullets(sl, ["Yes (10 groups): registrations, DAU/WAU/MAU, returning and inactive users, task starts and completion, feature usage, activity-to-credit (count only).",
             "Partial (3): onboarding completion, failure analysis, pending/reversed rewards.",
             "No (5): reward amounts, wallet and reconciliation, withdrawals, referral funnel, support. The data to add is named for each in the workbook."], size=18)
# 9 scorecard
sl = slide("Analytics readiness scorecard"); sl.shapes.add_picture(str(FIG / "readiness_scorecard.png"), Inches(1.6), Inches(1.0), height=Inches(5.9))
# 10 wireframe
sl = slide("Dashboard blueprint (wireframe example)"); sl.shapes.add_picture(str(FIG / "wireframe_6_Withdrawals.png"), Inches(2.2), Inches(1.0), height=Inches(5.9))
# 11 roadmap
sl = slide("Implementation priorities")
bullets(sl, ["Critical (prelaunch): stable user_id and user master; immutable transaction_id with idempotent writes; unit and conversion rules; withdrawal state history; reward vs activity separation; events REQ-001 to 013.",
             "High: UTC timestamps; ingestion validation; failure classification; referral stage rules; role-based access; reward-to-wallet reconciliation.",
             "Medium and Low (postlaunch): session ID, acquisition source, support export, remaining dashboards, badge/level analytics."], size=17)
# 12 decisions
sl = slide("Decisions needed and next steps")
bullets(sl, ["Which Users table is the master (A016)?", "Is the 'Task 02' behaviour file intended input?", "Can the Rewards, Wallet, Withdrawals, Referrals datasets be supplied?", "Confirm the qualifying-activity list for DAU and the referral activation rule.",
             "Next: engineering verifies the 18 open assumptions; run the tested pipeline on production-like data when it exists; replace simulated data, never mix."], size=18)
prs.save(ROOT / "docs" / "VELOOP_Handover_Presentation.pptx"); print("saved", len(prs.slides._sldIdLst))
