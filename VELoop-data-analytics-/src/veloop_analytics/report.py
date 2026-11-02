"""Write the profiling / DQ workbook."""
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from . import BANNER

def write_workbook(path, sheets):
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        pd.DataFrame({"README": [BANNER, "Reproduce: python run.py profile"]}).to_excel(w, sheet_name="README", index=False)
        for name, df in sheets.items():
            sn = name[:31]; df.to_excel(w, sheet_name=sn, index=False, startrow=2); ws = w.sheets[sn]
            ws["A1"] = BANNER; ws["A1"].font = Font(bold=True, color="C00000", size=9)
            for j, col in enumerate(df.columns, 1):
                c = ws.cell(row=3, column=j); c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3864")
                wd = min(70, max(10, len(str(col)) + 2, int(df[col].astype(str).str.len().quantile(0.9)) + 2)) if len(df) else 14
                ws.column_dimensions[get_column_letter(j)].width = wd
                for i in range(len(df)): ws.cell(row=4 + i, column=j).alignment = Alignment(wrap_text=True, vertical="top")
            ws.freeze_panes = "A4"
