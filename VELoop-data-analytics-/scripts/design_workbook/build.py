"""Generate the design workbook (events, dictionary, KPIs, specs). Run from this folder: python build.py"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from content_sources_coverage import *; from content_events import *; from content_dictionary import *; from content_kpis import *; from content_specs import *
wb=Workbook(); wb.remove(wb.active)
HF=Font(name="Arial",bold=True,color="FFFFFF",size=10); HFill=PatternFill("solid",fgColor="1F3864")
BF=Font(name="Arial",size=9); thin=Side(style="thin",color="BFBFBF"); BR=Border(left=thin,right=thin,top=thin,bottom=thin)
BAN="PROPOSED DESIGN / SIMULATED CONTEXT. Nothing here describes actual VELOOP production data or confirmed implementation unless Status says Confirmed."
def sheet(name,headers,rows,widths=None,banner=BAN):
    ws=wb.create_sheet(name[:31]); ws["A1"]=banner; ws["A1"].font=Font(name="Arial",bold=True,size=9,color="C00000")
    for j,h in enumerate(headers,1):
        c=ws.cell(row=3,column=j,value=h); c.font=HF; c.fill=HFill; c.alignment=Alignment(wrap_text=True,vertical="center"); c.border=BR
    for i,r in enumerate(rows,4):
        for j,v in enumerate(r,1):
            c=ws.cell(row=i,column=j,value=v); c.font=BF; c.alignment=Alignment(wrap_text=True,vertical="top"); c.border=BR
    for j,h in enumerate(headers,1):
        w=(widths[j-1] if widths else min(40,max(14,len(h)+4))); ws.column_dimensions[get_column_letter(j)].width=w
    ws.freeze_panes="A4"; ws.auto_filter.ref=f"A3:{get_column_letter(len(headers))}{3+len(rows)}"
    return ws
# README
ws=wb.create_sheet("README")
lines=["VELOOP Rewards - Data Analyst Task 01: Analytics Foundation Workbook (v0.1, "+CHECKED+")",
"DATA AUTHENTICITY: contains NO production data. All events, fields, KPIs are PROPOSED. Supplied dataset is simulated (SIMULATED DATA - CREATED FOR ANALYTICAL TESTING).",
"DATASET PROFILING (J) AND DQ AUDIT (K): completed on the supplied simulated files; see VELOOP_Data_Profiling_and_DQ_Audit.xlsx. Sheet 09 here is only the generic check catalogue.",
"Status vocabulary: Confirmed / Proposed / To Be Verified. Priority: Critical / High / Medium / Low.",
"Sheets: 01_Sources, 02_Coverage_Matrix(A1,A4), 03_Analytics_Gaps, 04_User_Spec(B2), 05_Event_Plan(F), 06_Data_Dictionary(G), 07_Data_Model(H), 08_KPI_Catalogue(I), 09_DQ_Checks(K), 10_DQ_Controls(L), 11_Dashboards(M), 12_Dev_Handoff(N), 13_Governance(P), 14_Change_Log(Q), 15_Gap_Assessment(R), 16_Assumptions(S), 17_Backlog",
"Naming standard: object_action, lowercase snake_case, past tense (task_completed). One object, one action, no feature prefixes; feature goes in the 'feature' property. Reason: consistent sorting/grepping, matches the brief's examples, easy for engineers to implement and validate.",
ENVELOPE]
for i,l in enumerate(lines,1):
    ws.cell(row=i,column=1,value=l).font=Font(name="Arial",size=10,bold=(i==1)); ws.cell(row=i,column=1).alignment=Alignment(wrap_text=True)
ws.column_dimensions["A"].width=140
sheet("01_Sources",["ID","Information","Source","Source Type","Date Checked","Status","Notes"],SOURCES,[7,60,35,12,12,14,55])
sheet("02_Coverage_Matrix",["Product Area","Feature","User Action","System Action","Business Outcome","Data Required","Proposed Event","Source","Business Question","Status","Priority"],COV,[18,18,20,22,20,34,34,14,34,14,10])
sheet("03_Analytics_Gaps",["Gap ID","Gap","Consequence","Priority","Reason"],GAPS,[8,50,45,10,45])
sheet("04_User_Spec",["Field","Type","Required?","Purpose","Source","Validation","Status"],USERSPEC,[24,22,16,34,28,40,14])
evrows=[]
for e in EV:
    n,cls,trig,defn,feat,st,req,opt,src,purp,k,pri=e
    evrows.append((n,cls,trig,defn,"yes (envelope)","yes (envelope)","event_timestamp_utc",feat,st,req,opt,GEN_TYPES,GEN_VAL+"; "+DEDUP,src,purp,KPIMAP[n],"Proposed - To Be Verified",pri))
sheet("05_Event_Plan",["Event Name","Class","Trigger","Definition","User ID","Event ID","Timestamp","Feature","Status values","Required Properties","Optional Properties","Data Type","Validation / Dedup","Source","Business Purpose","KPI Dependency","Implementation Status","Priority"],evrows,[28,14,34,26,10,10,16,12,12,40,28,26,50,14,26,14,16,9],banner=BAN+" "+ENVELOPE)
dd=[]
for ent,items in DD_RAW.items():
    for s in items:
        f=s.split("|"); assert len(f)==10,(ent,s)
        field,typ,dfn,ex,req,allowed,val,src,sens,use=f
        status="To Be Verified" if "TBV" in allowed or ent=="sessions" else "Proposed"
        dd.append((ent,field,typ,dfn,ex,req,allowed,val,src,sens,use,status))
sheet("06_Data_Dictionary",["Entity","Field Name","Data Type","Definition","Example (illustrative)","Required","Allowed Values","Validation","Source","Sensitivity","Analytical Use","Status"],dd,[18,26,12,36,20,9,36,30,14,11,26,14],banner=BAN+f" Total fields: {len(dd)}. Examples are illustrative, not real.")
print("fields",len(dd))
sheet("07_Data_Model",["Entity","Primary Key","Foreign Keys","Grain"],ENT,[22,22,70,34])
ws=wb["07_Data_Model"]; r=5+len(ENT); ws.cell(row=r,column=1,value="Relationships").font=Font(name="Arial",bold=True)
for i,(a,b) in enumerate(REL,r+1):
    ws.cell(row=i,column=1,value=a).font=BF; ws.cell(row=i,column=2,value=b).font=BF
sheet("08_KPI_Catalogue",["KPI ID","KPI Name","Area","Definition","Formula","Required Fields","Data Source","Frequency","Stakeholder","Business Purpose","Interpretation","Limitation","Status"],[k+("Proposed",) for k in KPI],[7,26,12,44,44,28,20,12,14,24,24,34,10],banner=BAN+f" {len(KPI)} KPIs. No targets are set; none are tested on production data.")
sheet("09_DQ_Checks",["Issue ID","Dataset","Field","Issue Type","Records Affected","Severity","Detection Logic","Likely Cause","Correction","Prevention","Owner","Status"],
 [(f"DQ-{i:02d}","Messy_Data (to profile)","(per profile run)",c,"See K_DQ_Report",sv,d,"To be assessed","Quarantine/fix at source, never overwrite silently","See 10_DQ_Controls","Data/Engineering","Open") for i,(c,d,sv) in enumerate(KCHK,1)],[9,20,18,26,22,10,36,18,34,20,16,9],banner="Generic check catalogue. Counts from the supplied simulated data are in VELOOP_Data_Profiling_and_DQ_Audit.xlsx (K_DQ_Report).")
sheet("10_DQ_Controls",["Rule ID","Rule","Check","Layer","Action on Failure","Owner"],DQR,[8,30,60,26,34,16])
sheet("11_Dashboards",["Dashboard","Metric","Calculation","Source","Visualization","Filters","Dimensions","Date Range","Refresh","Business Question","Decision Supported"],DASH,[20,30,30,18,22,16,12,14,10,28,24])
sheet("12_Dev_Handoff",["Requirement ID","Event","Trigger","Payload (field:type:required:validation)","Deduplication","Timestamp","Source","Why Needed","KPI Dependency","Acceptance Test","Priority"],HAND,[10,24,28,50,24,18,12,20,12,50,9])
sheet("13_Governance",["Role","Access Scope","Level","Notes"],GOV,[20,50,50,40])
sheet("14_Change_Log",["Date","Change","Old Definition","New Definition","Reason","Affected KPIs","Affected Dashboards","Affected Reports","Owner","Version"],CHANGELOG,[12,24,20,20,20,14,14,14,14,22])
sheet("15_Gap_Assessment",["Dimension","Currently Available/Verified","Needed Eventually","Priority","Reason"],GAPASSESS,[24,40,38,10,50])
sheet("16_Assumptions",["ID","Unknown","Why It Matters","Source Checked","Risk","Verification Owner","Status"],ASSUME,[7,55,30,22,8,22,16])
sheet("17_Backlog",["Priority","Requirement","Reason","Dependency","Owner","Stage"],BACKLOG,[10,50,30,22,18,16])
wb.save("../../outputs/VELOOP_Analytics_Foundation_Workbook.xlsx")
print(len(EV),"events",len(KPI),"kpis")
