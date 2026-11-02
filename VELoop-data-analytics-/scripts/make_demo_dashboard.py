"""Demo dashboard built ONLY from the supplied simulated behaviour data, plus a wireframe overview. Run: python scripts/make_demo_dashboard.py"""
import sys, pathlib
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from veloop_analytics.loaders import load_all
from veloop_analytics import quality
NAVY, BLUE, GREY, LIGHT = "#1F3864", "#2563EB", "#6B7280", "#EEF2F8"
d = load_all(); S, E, T, U = d["B:02_Sessions"], d["B:03_Feature_Events"], d["B:05_Task_Activity"], d["B:01_Users_1000"]
dq = pd.DataFrame(quality.run_all(d))
fig = plt.figure(figsize=(16, 9.5), facecolor="white")
fig.patches.append(plt.Rectangle((0, 0.94), 1, 0.06, transform=fig.transFigure, fc=NAVY))
fig.text(0.015, 0.97, "VELOOP analytics dashboard demo (built from the supplied simulated data)", color="white", fontsize=16, fontweight="bold", va="center")
fig.text(0.985, 0.97, "SIMULATED DATA - NOT ACTUAL VELOOP RESULTS", color="#FCA5A5", fontsize=11, fontweight="bold", ha="right", va="center")
cards = [("Simulated users", f"{len(U):,}"), ("Sessions", f"{len(S):,}"), ("Feature events", f"{len(E):,}"), ("Task attempts", f"{len(T):,}"), ("Data quality issues found", f"{len(dq)}")]
for i, (k, v) in enumerate(cards):
    x = 0.015 + i * 0.1965; fig.patches.append(plt.Rectangle((x, 0.835), 0.188, 0.085, transform=fig.transFigure, fc=LIGHT, ec="#CBD5E1"))
    fig.text(x + 0.01, 0.895, k, fontsize=9.5, color=GREY, va="center"); fig.text(x + 0.01, 0.857, v, fontsize=20, fontweight="bold", color=NAVY, va="center")
gs = fig.add_gridspec(2, 3, left=0.05, right=0.985, top=0.79, bottom=0.07, hspace=0.45, wspace=0.28)
def style(ax, title):
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold", color=NAVY)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax = fig.add_subplot(gs[0, 0]); w = pd.to_datetime(S.session_start).dt.to_period("W").dt.start_time
a = S.assign(w=w).groupby("w").user_id.nunique(); ax.plot(a.index, a.values, color=NAVY, lw=2); style(ax, "Weekly active users (K05 proxy; last week partial)"); ax.tick_params(axis="x", rotation=30, labelsize=8)
ax = fig.add_subplot(gs[0, 1]); ts = T.task_status.value_counts(); ax.bar(ts.index, ts.values, color=["#2563EB", "#D97706", "#B91C1C", "#6B7280"][:len(ts)]); style(ax, "Task attempts by status (K11-K13)")
for i, v in enumerate(ts.values): ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=8)
ax = fig.add_subplot(gs[0, 2]); fu = E.groupby("feature_name").user_id.nunique().sort_values().tail(10); ax.barh(fu.index, fu.values, color=BLUE); style(ax, "Feature usage: distinct users, top 10 (K15)"); ax.tick_params(labelsize=8)
ax = fig.add_subplot(gs[1, 0]); rs = T.reward_status.value_counts(); ax.bar(rs.index, rs.values, color="#94A3B8"); style(ax, "Reward status on tasks (counts only)")
for i, v in enumerate(rs.values): ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=8)
ax = fig.add_subplot(gs[1, 1]); ac = U.acquisition_source.value_counts().sort_values(); ax.barh(ac.index, ac.values, color="#94A3B8"); style(ax, "Registrations by source (K02)"); ax.tick_params(labelsize=8)
ax = fig.add_subplot(gs[1, 2]); sv = dq.severity.value_counts().reindex(["Critical", "High", "Medium", "Low"]).fillna(0); ax.bar(sv.index, sv.values, color=["#7F1D1D", "#B91C1C", "#D97706", "#6B7280"]); style(ax, "Data quality issues by severity (this audit)")
for i, v in enumerate(sv.values): ax.text(i, v, int(v), ha="center", va="bottom", fontsize=9)
fig.text(0.015, 0.015, "Built from the supplied simulated behaviour workbook only. The two Users tables conflict (master undecided), so user charts use the behaviour file. No reward amounts, wallet or withdrawal data exist in the pack. Counts describe the test data, not VELOOP.", fontsize=8.5, color=GREY)
FIGS = ROOT / "figures"; fig.savefig(FIGS / "dashboard_simulated_demo.png", dpi=110); plt.close(fig)
# wireframe overview
fs = sorted(FIGS.glob("wireframe_*.png")); ims = [Image.open(f).convert("RGB").resize((800, 515)) for f in fs]
sheet = Image.new("RGB", (800 * 2 + 30, 515 * 4 + 40 + 60), "white")
from PIL import ImageDraw; dr = ImageDraw.Draw(sheet); dr.text((10, 10), "VELOOP dashboard blueprint: wireframes of all 7 dashboards (layout only, no values; proposed design)", fill=(31, 56, 100))
for i, im in enumerate(ims): sheet.paste(im, (10 + (i % 2) * 810, 50 + (i // 2) * 525))
sheet.save(FIGS / "dashboard_wireframes_overview.png"); print("ok")
