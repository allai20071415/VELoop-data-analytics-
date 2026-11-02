"""Build the final Word report from the workbooks and figures. Run: python scripts/build_report_docx.py"""
import json, pathlib
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "outputs"; FIG = ROOT / "figures"; DOCS = ROOT / "docs"
NAVY = RGBColor(0x1F, 0x38, 0x64)
prof = pd.read_excel(OUT / "VELOOP_Data_Profiling_and_DQ_Audit.xlsx", sheet_name=None, header=2)
design = pd.read_excel(OUT / "VELOOP_Analytics_Foundation_Workbook.xlsx", sheet_name=None, header=2)
score = json.load(open(DOCS / "readiness_scorecard.json"))

doc = Document()
for s in doc.sections: s.left_margin = s.right_margin = Inches(1); s.top_margin = s.bottom_margin = Inches(0.9)
st = doc.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10); st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
for n, sz in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11)):
    h = doc.styles[n]; h.font.name = "Arial"; h.font.size = Pt(sz); h.font.bold = True; h.font.color.rgb = NAVY; h.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexcolor); tcPr.append(shd)
def para(text, bold=False, italic=False, size=None, color=None, align=None, space_after=6):
    p = doc.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(space_after); return p
def bullets(items):
    for t in items:
        p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = Pt(2)
        if isinstance(t, tuple): r = p.add_run(t[0]); r.bold = True; p.add_run(t[1])
        else: p.add_run(t)
def table(df, widths=None, size=8):
    t = doc.add_table(rows=1, cols=len(df.columns)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, c in enumerate(df.columns):
        cell = t.rows[0].cells[j]; cell.text = ""; r = cell.paragraphs[0].add_run(str(c)); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = RGBColor(255, 255, 255); shade(cell, "1F3864")
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = ""; r = cells[j].paragraphs[0].add_run("" if pd.isna(v) else str(v)); r.font.size = Pt(size)
    if not widths: widths = [6.5 / len(df.columns)] * len(df.columns)
    t.autofit = False
    for j, w in enumerate(widths):
        t.columns[j].width = Inches(w)
        for row in t.rows: row.cells[j].width = Inches(w)
    hdr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); hdr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
def fig(name, width=6.4, caption=None):
    doc.add_picture(str(FIG / name), width=Inches(width)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption: para(caption, italic=True, size=8, align=WD_ALIGN_PARAGRAPH.CENTER)

NOTICE = ("DATA AUTHENTICITY NOTICE. VELOOP is a real product under development, but all data analysed in this report is fictional/simulated "
          "(SIMULATED DATA - CREATED FOR ANALYTICAL TESTING). No figure here describes actual VELOOP users, earnings, withdrawals, revenue, retention or performance. "
          "Every event, field and KPI is Proposed or To Be Verified unless marked Confirmed.")
# ---------- title ----------
para("VELOOP REWARDS", bold=True, size=26, color=NAVY, space_after=0)
para("Product Analytics, Data Readiness & Data Management Blueprint", size=15, color=NAVY, space_after=2)
para("Data Analyst Internship, Task 01. Final Consolidated Report, version 1.0, 31 October 2026", size=10, space_after=14)
para(NOTICE, italic=True, size=9, space_after=12)
doc.add_heading("Contents of this deliverable pack", 2)
table(pd.DataFrame([
 ("01 Executive summary", "Section 1"), ("02 Product data audit", "Section 3; workbook sheets 01-03"), ("03 Data coverage matrix", "Workbook sheet 02"),
 ("04 User analytics specification", "Section 4; sheet 04"), ("05-07 Earning/reward, wallet/withdrawal, referral/engagement", "Sections 5-7"),
 ("08 Event tracking plan", "Section 8; sheet 05"), ("09 Data dictionary", "Sheet 06 (100 fields)"), ("10 Logical data model", "Section 9; figure er_diagram.png"),
 ("11 KPI catalogue", "Section 10; sheet 08 (46 KPIs)"), ("12 Simulated data profiling", "Section 11; Data_Profiling_and_DQ_Audit.xlsx"),
 ("13 Data quality audit", "Section 12; sheet K_DQ_Report (34 issues)"), ("14 Dashboard blueprint", "Section 13; wireframes (figures/)"),
 ("15 Developer handoff", "Section 14; sheet 12"), ("16 Pipeline proposal", "Section 15"), ("17 Privacy & governance", "Section 16"),
 ("18 Readiness assessment", "Section 17"), ("19 Assumption register", "Section 18; sheet 16"), ("20 Implementation backlog", "Section 19; sheet 17"),
 ("21 Final consolidated report", "This document"), ("Code, tests, cleaning", "src/, tests/, README.md")], columns=["Required deliverable", "Where"]), widths=[3.4, 3.1], size=9)
doc.add_page_break()

# ---------- 1 executive summary ----------
doc.add_heading("1. Executive summary", 1)
para("What was investigated", bold=True, space_after=2)
para("The brief's product scope (accounts, earning tasks, rewards, wallet, withdrawals, referrals, engagement and support) was turned into a complete analytics foundation: a data-readiness audit, a 38-event tracking plan, a 100-field data dictionary, a logical data model, 46 KPIs, quality controls, dashboard specifications, an engineering handoff, a pipeline, governance rules, a change process and a prioritised backlog. Two simulated workbooks were then profiled and audited with reusable, tested code.")
para("What was discovered", bold=True, space_after=2)
bullets([("Two Users tables contradict each other. ", "Both files use the same 1,000 user IDs (VLUSR000001 to VLUSR001000), yet names, emails and registration times differ for all 1,000 users. One table must be declared the user master before any join."),
 ("The supplied pack is incomplete. ", "Rewards, Wallet, Withdrawals and Referrals tables, which the brief lists, were not supplied. The behaviour file contains users, sessions, 35,704 events, daily activity, task activity and milestones only."),
 ("Structure is sound but not production-ready. ", "No orphan user or session references exist, but task attempts carry no reward amount or unit, the task catalogue is missing (every task_id maps to several categories), and stored counts do not reconcile (events_in_session wrong for 7,537 of 7,913 sessions; 423 daily rows with more completed than total tasks)."),
 ("The messy sheet behaves as designed. ", "Automated checks found 8 duplicate user rows, 9 missing required values, 1 malformed date and 2 conflicting registration times; the event audit sheet holds 10 duplicate events, 4 trailing-space statuses and 5 inconsistent feature names."),
 ("Personal data is over-collected. ", "Full name, email, age, gender and city are present for every user, contrary to the brief's data-minimisation rule.")])
para("What is currently unknown", bold=True, space_after=2)
para("Whether any event, session ID, transaction ID, reward pending state, withdrawal state history, acquisition source or the Spin/Mining/Missions/Badges features exist in production. 18 such unknowns are in the assumption register; none has been converted into a fact.")
para("What VELOOP should implement first", bold=True, space_after=2)
bullets(["A stable user_id and one user master table.", "An immutable transaction_id with idempotent wallet writes, and separate reward-versus-activity records.", "Defined value units (VE, XP, Gems, Tokens) with conversion rules, so amounts are never summed across units.",
 "Withdrawal state and timestamp history; UTC timestamps everywhere.", "The Critical events REQ-001 to REQ-013, validated at ingestion by the proposed rules."])
para("Major risks", bold=True, space_after=2)
para("Reporting activity as earnings; summing across units; duplicate credits; unreliable daily metrics without a UTC standard; third-party outcomes outside VELOOP's control; and silently mixing simulated with production data.")
para("Major priorities", bold=True, space_after=2)
para("Six Critical, seven High, five Medium and two Low backlog items (Section 19). The Critical items are all Prelaunch.")
doc.add_heading("Key figures from this work (simulated data and design artefacts)", 3)
table(pd.DataFrame([
 ("Proposed events / data-dictionary fields / KPIs", "38 / 100 / 46"),
 ("Dashboards / visuals / developer requirements", "7 / 28 / 15"),
 ("Quality rules designed / automated tests passing", "20 / 11 of 11"),
 ("Simulated datasets profiled (sheets) / records in largest", "9 / 35,714 (event audit sheet)"),
 ("Data quality issues found (Critical / High / Medium / Low)", " / ".join(str(int((prof["K_DQ_Report"].severity == v).sum())) for v in ["Critical", "High", "Medium", "Low"]) + f" ({len(prof['K_DQ_Report'])} in total; see Section 12)"),
 ("Referential-integrity orphans between users, sessions, events, tasks", "0"),
 ("Proposed KPI groups testable on supplied data (yes / partial / no)", "10 / 3 / 5"),
 ("Open unknowns in the assumption register", "18, none converted into a fact")], columns=["Measure", "Value"]), widths=[4.4, 2.1], size=9)
doc.add_heading("Recommended roadmap", 3)
bullets([("Before launch (Critical and High): ", "user master and stable user_id; transaction_id and idempotent wallet writes; unit and conversion rules; reward-versus-activity separation; withdrawal state history; UTC timestamps; ingestion validation; role-based access to curated tables."),
 ("At launch: ", "emit events REQ-001 to REQ-013; run the quality checks and the reward-to-wallet reconciliation (K29) daily; certify the analytical tables that power Dashboards 1, 5 and 6."),
 ("After launch: ", "session identifier, acquisition source capture, support categories, engagement events for Spin, Missions and Streaks; remaining dashboards; replace simulated data with governed production data, never mixing them.")])
doc.add_heading("Decisions needed from the team", 3)
bullets(["Which of the two Users tables is the user master (assumption A016).", "Whether the behaviour workbook ('Task 02') is intended input for this task.", "Whether Rewards, Wallet, Withdrawals and Referrals datasets exist and can be supplied.", "The qualifying-activity list that defines DAU and the referral activation rule (A017, A010)."])
doc.add_page_break()

# ---------- 2 scope ----------
doc.add_heading("2. Scope, method and evidence discipline", 1)
para("Method: (1) read the brief and record each product fact in a Source & Verification Register with status Confirmed, Proposed or To Be Verified; (2) design the analytics model from the product areas; (3) profile and audit the two supplied workbooks with a Python package whose checks are small functions and are covered by automated tests; (4) test whether each proposed KPI can actually be calculated from what was supplied; (5) consolidate.")
table(design["01_Sources"][["ID", "Information", "Source Type", "Status"]], widths=[0.5, 4.0, 0.9, 1.1])
para("Naming standard. Events use object_action in lowercase snake_case and past tense (task_completed, withdrawal_rejected). One object, one action, no feature prefixes: the feature is a property. This matches the brief's examples, sorts by object, and is easy for engineers to implement and test. Every event carries a common envelope: event_id, event_name, event_timestamp_utc, user_id, schema_version, platform, app_version, session_id (if available), source_system.")

# ---------- 3 product data audit ----------
doc.add_heading("3. Product data audit and coverage", 1)
para("31 product-area rows are mapped (user action, system action, business outcome, data required, proposed event, source, business question, status, priority). Events are classed as User Event (the user did something), System Event (the system recorded an outcome) or Business Outcome (a derived result computed in the analytics layer, for example a converted referral).")
cm = design["02_Coverage_Matrix"][["Product Area", "Feature", "Proposed Event", "Status", "Priority"]]
table(cm, widths=[1.3, 1.3, 2.4, 0.9, 0.7], size=7)
doc.add_heading("Fifteen analytics gaps", 2)
table(design["03_Analytics_Gaps"][["Gap ID", "Gap", "Priority", "Reason"]], widths=[0.5, 2.6, 0.7, 2.7], size=8)

# ---------- 4-7 specs ----------
doc.add_heading("4. User and account analytics specification", 1)
para("Identifiers: user_id (stable join key across everything; immutable, never reused), event_id (deduplication of events), session_id (groups activity; its existence is To Be Verified), transaction_id (ledger deduplication and reconciliation). No names, emails, phone numbers or addresses are required for analytics.")
table(design["04_User_Spec"][["Field", "Type", "Required?", "Purpose", "Status"]], widths=[1.5, 1.3, 0.9, 2.1, 0.9], size=8)
doc.add_heading("5. Earning and reward analytics", 1)
para("Lifecycle measured: Discovery (task_viewed) > Start (task_started) > Completion (task_completed, emitted only after the applicable validation) > Validation (validation_status) > Reward (reward_pending, reward_credited). Activity occurring and a reward actually being credited are two separate records, linked by source_activity_id; the KPI 'activity-to-credit rate' (K24) exposes any gap between them.")
bullets(["Failed activity is classified with a Proposed category list: user_abandoned, tracking_failed, validation_failed, provider_error, system_error, unknown. These are not existing VELOOP codes.",
 "Reward events: reward_credited, reward_pending, reward_reversed (references original_reward_id), reward_corrected (carries amount_delta).",
 "Third parties: ads, surveys, offers and games may fail, change or charge back outside VELOOP's control, so provider and provider_ref are recorded and provider-caused outcomes are reported separately."])
doc.add_heading("6. Wallet and withdrawal analytics", 1)
para("Wallet transaction model: transaction_id, user_id, timestamp, transaction_type, amount (always positive; direction gives the sign), unit, status, source, reference_id, related_transaction_id (reversal/correction chain). Transaction types reward_credit, redemption, reversal, adjustment and exchange are all Proposed.")
para("Withdrawal lifecycle: requested > processing > completed, with rejected and reversed as alternatives. Fields: withdrawal_id, user_id, requested_amount, final_amount, method (a category, never account details), requested_at, processing_started_at, finalized_at, status, reason_category. Withdrawal KPIs are K30 to K38 in the catalogue (requests, completed, pending queue, rejected, reversed, processing time, completion rate, volume, method distribution), each with definition, formula, data required, source, frequency, stakeholder, purpose and limitation.")
doc.add_heading("7. Referral and engagement analytics", 1)
para("Referral stages are kept separate: created > registered > activated > converted. Registration never counts as conversion; the activation rule is an open question (A010). Engagement is measured through DAU/WAU/MAU, returning users, feature adoption, repeat usage, task activity and stickiness (K03 to K05, K08, K15 to K17), all defined over a documented list of qualifying events.")

# ---------- 8 events ----------
doc.add_heading("8. Event tracking plan", 1)
para("38 events are catalogued with trigger, definition, class, properties, data type, validation, deduplication, source, purpose, KPI dependency and implementation status ('Proposed - To Be Verified' for all). The table below lists them; the complete specification is sheet 05.")
ev = design["05_Event_Plan"][["Event Name", "Class", "Feature", "Required Properties", "Priority"]]
table(ev, widths=[1.5, 0.9, 0.8, 2.7, 0.6], size=7)

# ---------- 9 model ----------
doc.add_heading("9. Logical data model", 1)
para("Ten entities, each with a primary key and foreign keys. Solid entities exist in the supplied simulated data; dashed entities are proposed only.")
fig("er_diagram.png", 6.5, "Figure 1. Logical data model (proposed).")
table(design["07_Data_Model"].dropna(subset=["Primary Key"])[["Entity", "Primary Key", "Foreign Keys", "Grain"]], widths=[1.2, 1.2, 2.9, 1.2], size=7)
para("Relationships: users 1:N task_activity, sessions, feature_events, rewards, wallet_transactions, withdrawals, support_tickets; tasks 1:N task_activity; sessions 1:N feature_events; task_activity 1:0..1 rewards; rewards 1:0..1 wallet_transactions; withdrawals 1:1 wallet_transactions (debit entry); rewards and wallet_transactions each relate to themselves for reversal chains; referrals link two users (referrer, referred), many-to-many through users. The 0..1 cardinalities are assumptions to verify.", size=9)

# ---------- 10 KPI ----------
doc.add_heading("10. KPI catalogue", 1)
para("46 KPIs across user, engagement, reward, wallet, withdrawal, referral, support/content and data-quality areas. No targets are set; each KPI has a reproducible definition, formula, required fields, data source, frequency, stakeholder, purpose, interpretation, limitation and status. Example: Daily Active Users = unique users generating a qualifying activity event within a UTC calendar day.")
k = design["08_KPI_Catalogue"]; table(k[["KPI ID", "KPI Name", "Area", "Definition", "Frequency"]], widths=[0.5, 1.4, 0.9, 3.0, 0.7], size=7)

# ---------- 11 profiling ----------
doc.add_heading("11. Simulated data profiling (Work Package J)", 1)
para("All statements describe the supplied simulated datasets only. Reference period stated in the files: 1 April to 15 September 2026.", italic=True)
p = prof["J1_Profile"][["dataset", "records", "columns", "earliest", "latest", "duplicate_rows", "missing_cells"]]
table(p, widths=[1.7, 0.6, 0.6, 1.1, 1.1, 0.7, 0.7], size=7)
doc.add_heading("Relationship tests", 2)
table(prof["J2_Relationships"][["parent", "child", "child_rows", "orphans", "parents_without_children", "result"]], widths=[1.6, 1.8, 0.6, 0.6, 0.9, 0.6], size=7)
para("Result: every user_id and session_id reference resolves (0 orphans). 16 users have no sessions, events or tasks. The cross-file test passes on IDs but fails on content: the two Users tables disagree (see below).")
doc.add_heading("Cross-file conflict between the two Users tables", 2)
table(prof["J2_Cross_File_Conflict"], widths=[2.5, 2.5, 1.0], size=8)
doc.add_heading("KPI test: can the proposed KPIs be calculated from what was supplied?", 2)
table(prof["J3_KPI_Test"][["kpi", "name", "calculable", "limitation_or_data_required"]], widths=[0.9, 1.9, 0.9, 2.8], size=7)

# ---------- 12 DQ ----------
doc.add_heading("12. Data quality audit (Work Package K)", 1)
dq = prof["K_DQ_Report"]
sev = dq.severity.value_counts().reindex(["Critical", "High", "Medium", "Low"]).fillna(0).astype(int)
para("34 issues were found by automated checks: " + ", ".join(f"{v} {k}" for k, v in sev.items()) + ". Each has detection logic, likely cause, correction, prevention and owner in the workbook; the critical, high and most informative issues are listed here.")
table(dq[dq.severity.isin(["Critical", "High"])][["issue_id", "dataset", "field", "issue_type", "records", "severity"]], widths=[0.6, 1.5, 1.3, 2.0, 0.5, 0.6], size=7)
doc.add_heading("Cleaning demonstration", 2)
cs = pd.read_csv(ROOT / "data" / "processed" / "cleaning_summary.csv")
table(cs.fillna("-"), size=8)
para("Rules: exact duplicates are removed by ID (first kept); rows with a malformed date or a missing required value are quarantined, never imputed; status and feature names are trimmed and normalised to their most frequent spelling. Rows are traceable: input rows equal clean plus quarantined plus removed duplicates.")
doc.add_heading("Data quality control framework (Work Package L)", 2)
table(design["10_DQ_Controls"][["Rule ID", "Rule", "Layer", "Action on Failure"]], widths=[0.6, 2.0, 1.8, 2.1], size=7)

# ---------- 13 dashboards ----------
doc.add_heading("13. Dashboard blueprint", 1)
para("Seven dashboards with 28 visuals, each specified with metric, calculation, source, visualization, filters, dimensions, date range, refresh, business question and decision supported (workbook sheet 11). Wireframes show layout only. They carry no values.")
table(design["11_Dashboards"][["Dashboard", "Metric", "Visualization", "Refresh", "Decision Supported"]], widths=[1.3, 1.9, 1.3, 0.6, 1.4], size=7)
for f in sorted(FIG.glob("wireframe_*.png")): fig(f.name, 6.0, f"Wireframe: {f.stem.replace('wireframe_', '').replace('_', ' ')}")

# ---------- 14 handoff ----------
doc.add_heading("14. Developer analytics handoff", 1)
para("15 requirements (REQ-001 to REQ-015) specify, per event: trigger, payload with type, required flag and validation, deduplication key, timestamp rule, source, why needed, KPI dependency, acceptance test and priority. Example:")
h = design["12_Dev_Handoff"]; r = h[h["Event"] == "task_completed"].iloc[0]
table(pd.DataFrame({"Item": ["Requirement ID", "Event", "Trigger", "Payload", "Deduplication", "Timestamp", "Acceptance test", "Priority"],
                    "Specification": [r["Requirement ID"], r["Event"], r["Trigger"], str(r["Payload (field:type:required:validation)"]).replace("\n", "; "), r["Deduplication"], r["Timestamp"], r["Acceptance Test"], r["Priority"]]}), widths=[1.3, 5.2], size=8)
table(h[["Requirement ID", "Event", "KPI Dependency", "Priority"]], widths=[1.1, 3.0, 1.5, 0.9], size=8)

# ---------- 15-16 ----------
doc.add_heading("15. Data pipeline and operating model", 1)
fig("pipeline_architecture.png", 6.5, "Figure 2. Proposed analytics pipeline with owners, quarantine path and monitoring.")
para("A practical flow, deliberately without expensive infrastructure: VELOOP application and backend > event emitters (REQ-001 to 015) > collection endpoint or queue > raw append-only store > validation (rules Q01 to Q19; failures go to quarantine and alert) > staging and transformation (SQL models) > certified analytical tables > BI dashboards > business reporting, with monitoring on freshness, volume and schema drift.")
bullets([("Start small: ", "the application database plus one managed warehouse (or a relational database) with scheduled SQL transformations and a low-cost BI tool. Move to streaming or heavier tooling only when volume or latency requires it."),
 ("Refresh: ", "daily batch; hourly only for the withdrawal queue."), ("Failure handling: ", "failed loads retried; bad rows quarantined, never dropped; owners alerted."),
 ("Ownership: ", "Engineering owns emitters and the raw layer; Data owns validation, transformation, KPI definitions and dashboards; Product and Operations own definitions of qualifying activity and states.")])
doc.add_heading("16. Privacy, access and governance", 1)
table(design["13_Governance"], widths=[1.2, 2.2, 1.9, 1.2], size=7)
para("Never collected or stored in analytics: passwords, authentication secrets, API keys, payment credentials, card or bank numbers, security-control details, fraud thresholds. Payout provider references are Restricted. The supplied Users data breaks the minimisation rule (DQ-015) and should be reduced to user_id plus coarse attributes in the analytics layer.")
doc.add_heading("Change management", 2)
para("Every change to an event, field, reward mechanic, withdrawal method, KPI or dashboard is logged (date, change, old and new definition, reason, affected KPIs, dashboards and reports, owner, version). Event schemas are versioned; renamed events keep an alias for a declared period; a changed KPI becomes a new version annotated on its dashboards; every new feature passes an analytics checklist (events, dictionary entries, KPIs, quality rules) before launch.")

# ---------- 17 readiness ----------
doc.add_heading("17. Analytics readiness assessment", 1)
para("Rubric (not a company metric): 0 = nothing verified, 1 = designed only, 2 = designed and tested on simulated data, 3 = verified in production. No dimension can reach 3 until production data exists.")
fig("readiness_scorecard.png", 5.8, "Figure 3. Readiness scorecard.")
table(pd.DataFrame(score, columns=["Dimension", "Score", "Priority", "Evidence"]), widths=[1.5, 0.5, 0.7, 3.8], size=8)
table(design["15_Gap_Assessment"][["Dimension", "Priority", "Reason"]], widths=[1.6, 0.8, 4.1], size=8)

# ---------- 18-19 ----------
doc.add_heading("18. Assumption and verification register", 1)
table(design["16_Assumptions"][["ID", "Unknown", "Why It Matters", "Risk", "Verification Owner", "Status"]], widths=[0.5, 2.4, 1.4, 0.5, 1.0, 0.8], size=7)
doc.add_heading("19. Implementation backlog", 1)
table(design["17_Backlog"], widths=[0.7, 2.4, 1.4, 1.1, 0.9], size=7)

# ---------- 20 limitations ----------
doc.add_heading("20. Limitations and decisions needed", 1)
bullets(["Rewards, Wallet, Withdrawals and Referrals datasets were not supplied: related KPIs and tables are design-only.",
 "The behaviour workbook labels itself 'Task 02'. It was used as additional simulated data because it overlaps the Task 01 scope; please confirm.",
 "Decision needed: which Users table is the master (A016).",
 "Nothing is marked Confirmed beyond the brief and the supplied files' own READMEs; engineering verification is required before any proposed event or field is treated as real.",
 "When production data exists, the simulated datasets must be replaced by governed production data and never silently mixed with it."])
doc.add_heading("Integrity checklist (brief section 34)", 2)
table(pd.DataFrame([("Never fabricate production data", "Met"), ("Never represent simulated data as actual VELOOP statistics", "Met: every sheet and section is labelled"), ("No fake company performance claims", "Met: no targets, no success rates"),
 ("No invented security mechanisms or fraud thresholds", "Met"), ("No credentials requested", "Met"), ("No proposed event claimed to exist", "Met: all 'Proposed - To Be Verified'"), ("Uncertainty not hidden", "Met: 18-item register, Section 20"),
 ("No unnecessary personal-data fields", "Met in design; supplied data violates it (DQ-015)"), ("Conclusions traceable to dataset, source or assumption", "Met: issue IDs, KPI IDs, assumption IDs")], columns=["Rule", "Status"]), widths=[3.6, 2.9], size=8)

# footer
for s in doc.sections:
    fp = s.footer.paragraphs[0]; fp.text = "VELOOP Analytics Foundation | SIMULATED DATA / PROPOSED DESIGN | not actual VELOOP results"; fp.runs[0].font.size = Pt(7.5); fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.save(DOCS / "VELOOP_Final_Report.docx"); print("saved")
