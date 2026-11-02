"""Generate ER diagram, dashboard wireframes and readiness scorecard (PNG + xlsx). Run: python scripts/make_figures.py"""
import json, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
ROOT = pathlib.Path(__file__).resolve().parents[1]; FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
NAVY, GREY, LIGHT = "#1F3864", "#6B7280", "#EEF2F8"

# ---------------- ER diagram ----------------
ENT = {  # name: (x, ytop, supplied?, fields)
 "tasks": (0.5, 11.9, False, ["PK task_id", "task_type", "feature", "reward_unit", "provider"]),
 "task_activity": (5.5, 11.9, True, ["PK task_activity_id", "FK user_id", "FK task_id", "FK session_id", "task_status", "validation_status*", "reward_status"]),
 "rewards": (10.5, 11.9, False, ["PK reward_id", "FK user_id", "FK source_activity_id", "FK original_reward_id", "amount, unit", "status"]),
 "wallet_transactions": (15.5, 11.9, False, ["PK transaction_id", "FK user_id", "FK related_transaction_id", "reference_id", "type, amount, unit", "status"]),
 "sessions": (0.5, 7.0, True, ["PK session_id", "FK user_id", "session_start / end", "device, platform", "entry_point"]),
 "users": (5.5, 7.0, True, ["PK user_id", "registration_datetime", "acquisition_source", "primary_device", "account_status", "onboarding_status"]),
 "withdrawals": (10.5, 7.0, False, ["PK withdrawal_id", "FK user_id", "FK wallet_transaction_id", "requested_amount", "method, status", "requested/final_at"]),
 "referrals": (10.5, 3.0, False, ["PK referral_id", "FK referrer_user_id", "FK referred_user_id", "status", "created/registered/activated_at"]),
 "feature_events": (0.5, 3.0, True, ["PK event_id", "FK user_id", "FK session_id", "event_name", "feature_name", "event_datetime"]),
 "support_tickets": (5.5, 3.0, False, ["PK ticket_id", "FK user_id", "issue_category", "status", "created_at"]),
}
W, LH = 4.2, 0.42
def box(ax, name, x, y, supplied, fields):
    h = 0.7 + LH * len(fields)
    ax.add_patch(FancyBboxPatch((x, y - h), W, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc="white", ec=NAVY if supplied else GREY, lw=2 if supplied else 1.5, ls="-" if supplied else (0, (4, 3)), zorder=3))
    ax.add_patch(Rectangle((x, y - 0.6), W, 0.6, fc=NAVY if supplied else GREY, ec="none", zorder=4))
    ax.text(x + W / 2, y - 0.3, name, color="white", ha="center", va="center", fontsize=11, fontweight="bold", zorder=5)
    for i, f in enumerate(fields):
        ax.text(x + 0.15, y - 0.6 - LH * (i + 0.6), f, fontsize=8.5, va="center", zorder=5, fontweight="bold" if f.startswith("PK") else "normal")
    return (x + W / 2, y - h / 2)
def er():
    fig, ax = plt.subplots(figsize=(21, 12.5)); ax.set_xlim(0, 20.5); ax.set_ylim(-1.3, 12.3); ax.axis("off")
    ctr = {}
    for n, (x, y, s, f) in ENT.items():
        h = 0.7 + LH * len(f); ctr[n] = (x + W / 2, y - h / 2)
    rel = [("users", "task_activity", "1 : N"), ("tasks", "task_activity", "1 : N"), ("users", "sessions", "1 : N"), ("users", "feature_events", "1 : N"),
           ("sessions", "feature_events", "1 : N"), ("sessions", "task_activity", "1 : N"), ("task_activity", "rewards", "1 : 0..1"), ("users", "rewards", "1 : N"),
           ("rewards", "wallet_transactions", "1 : 0..1"), ("users", "wallet_transactions", "1 : N"), ("users", "withdrawals", "1 : N"), ("withdrawals", "wallet_transactions", "1 : 1"),
           ("users", "referrals", "1 : N (referrer)"), ("users", "support_tickets", "1 : N")]
    for a, b, lab in rel:
        (x1, y1), (x2, y2) = ctr[a], ctr[b]; ax.plot([x1, x2], [y1, y2], color="#9CA3AF", lw=1.4, zorder=1)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, lab, fontsize=8, ha="center", va="center", color="#111827", zorder=2, bbox=dict(fc="white", ec="none", pad=1.2))
    for n, (x, y, s, f) in ENT.items(): box(ax, n, x, y, s, f)
    ax.text(0.5, 12.15, "VELOOP logical data model (proposed). Solid navy = entity present in supplied simulated data; dashed grey = proposed, NOT supplied.", fontsize=12, fontweight="bold", color=NAVY, va="top")
    ax.text(0.5, -1.0, "* validation_status is proposed; not present in the supplied Task_Activity sheet. 0..1 cardinalities are assumptions to verify (A009, A006).   SIMULATED DATA / PROPOSED DESIGN", fontsize=9, color=GREY)
    fig.savefig(FIG / "er_diagram.png", dpi=110, bbox_inches="tight"); plt.close(fig)

# ---------------- wireframes ----------------
DASH = {
 "1_Executive_Overview": ("Dashboard 1 - Executive Overview", ["Registrations (K01)", "DAU / MAU (K03,K05)", "Task completion rate (K12)", "Withdrawal queue (K32)"],
    [("Registrations trend (K01)", "line"), ("Reward credited by unit (K19)", "bar"), ("Referral funnel (K39-K42)", "funnel"), ("Withdrawal processing time (K35)", "line"), ("Data quality pass rate (K46)", "bar")]),
 "2_User_Analytics": ("Dashboard 2 - User Analytics", ["New users", "Returning users (K04)", "Inactive users (K07)", "Pending verification"],
    [("Registrations by source (K02)", "bar"), ("Cohort retention heatmap", "heat"), ("Platform / device mix", "bar"), ("Account status (K10)", "bar")]),
 "3_Engagement": ("Dashboard 3 - Engagement", ["Task starts (K11)", "Completion rate (K12)", "Repeat usage (K16)", "Feature adoption (K17)"],
    [("Task funnel: viewed > opened > started > completed", "funnel"), ("Feature usage (K15)", "bar"), ("Failure categories (K14)", "bar"), ("Activity trend", "line")]),
 "4_Rewards": ("Dashboard 4 - Rewards", ["Reward transactions (K18)", "Credited amount per unit (K19)", "Reversal rate (K21)", "Pending rewards (K22)"],
    [("Credited by source (K23)", "bar"), ("Reward status mix", "bar"), ("Activity-to-credit rate (K24)", "line"), ("Reversals by reason", "bar")]),
 "5_Wallet": ("Dashboard 5 - Wallet", ["Wallet transactions (K25)", "Credit volume (K26)", "Redemptions (K27)", "Reconciliation gap (K29)"],
    [("Transactions by type", "bar"), ("Credits vs redemptions (per unit)", "line"), ("Reversals (K28)", "line"), ("Unmatched rewards table (should be empty)", "table")]),
 "6_Withdrawals": ("Dashboard 6 - Withdrawals", ["Requests (K30)", "Completed (K31)", "Pending queue (K32)", "Median processing time (K35)"],
    [("Status distribution", "bar"), ("Processing time trend (median / P90)", "line"), ("Method distribution (K38)", "bar"), ("Rejection reasons (K33)", "bar")]),
 "7_Referrals": ("Dashboard 7 - Referrals", ["Created (K39)", "Registered (K40)", "Activated (K41)", "Conversion rate (K42)"],
    [("Referral funnel", "funnel"), ("Time created > registered > activated", "box"), ("Referrals by channel", "bar"), ("Weekly trend", "line")]),
}
def tile(ax, x, y, w, h, label, kind):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.01", fc="white", ec="#CBD5E1", lw=1.2))
    ax.text(x + 0.015, y + h - 0.03, label, fontsize=9.5, fontweight="bold", color=NAVY, va="top")
    ix, iy, iw, ih = x + 0.03, y + 0.04, w - 0.06, h - 0.14
    if kind == "bar":
        for i, v in enumerate([.5, .8, .35, .65, .9, .45]): ax.add_patch(Rectangle((ix + i * iw / 6.5, iy), iw / 9, ih * v, fc="#94A3B8", ec="none"))
    elif kind == "line":
        xs = [ix + iw * i / 7 for i in range(8)]; ys = [iy + ih * v for v in (.3, .5, .4, .7, .55, .8, .65, .9)]; ax.plot(xs, ys, color=NAVY, lw=2)
    elif kind == "funnel":
        for i in range(4): ax.add_patch(Rectangle((ix + iw * i * .08, iy + ih * (0.75 - i * .22)), iw * (1 - i * .16), ih * .18, fc="#94A3B8", ec="none"))
    elif kind == "heat":
        for r in range(5):
            for c in range(7): ax.add_patch(Rectangle((ix + c * iw / 7, iy + r * ih / 5), iw / 7 - .004, ih / 5 - .006, fc=plt.cm.Blues(0.15 + 0.1 * ((r * 3 + c) % 6)), ec="none"))
    elif kind == "table":
        for r in range(5): ax.plot([ix, ix + iw], [iy + ih * (1 - r / 5)] * 2, color="#CBD5E1", lw=1)
    elif kind == "box":
        for i in range(3): ax.add_patch(Rectangle((ix + iw * (.15 + i * .3), iy + ih * .25), iw * .15, ih * .5, fc="#94A3B8", ec=NAVY))
def wireframes():
    for key, (title, cards, charts) in DASH.items():
        fig, ax = plt.subplots(figsize=(14, 9)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        ax.add_patch(Rectangle((0, 0.93), 1, 0.07, fc=NAVY)); ax.text(0.015, 0.965, title, color="white", fontsize=15, fontweight="bold", va="center")
        ax.text(0.985, 0.965, "Filters: date range | platform | feature | unit", color="white", fontsize=9, ha="right", va="center")
        for i, c in enumerate(cards):
            x = 0.015 + i * 0.2475; ax.add_patch(FancyBboxPatch((x, 0.78), 0.235, 0.12, boxstyle="round,pad=0.005", fc=LIGHT, ec="#CBD5E1"))
            ax.text(x + 0.012, 0.865, c, fontsize=9.5, color=GREY, va="center"); ax.text(x + 0.012, 0.81, "value", fontsize=17, fontweight="bold", color=NAVY, va="center")
        n = len(charts); cols = 2 if n != 5 else 3; rows = -(-n // cols); tw = (0.97 - 0.015 * (cols - 1)) / cols; th = (0.70 - 0.02 * rows) / rows
        for i, (lab, kind) in enumerate(charts):
            r, c = divmod(i, cols); tile(ax, 0.015 + c * (tw + 0.015), 0.74 - (r + 1) * th - r * 0.02, tw, th, lab, kind)
        ax.text(0.015, 0.012, "WIREFRAME - layout only. No values shown. SIMULATED/PROPOSED. Metrics reference KPI IDs in the KPI catalogue.", fontsize=8, color=GREY)
        fig.savefig(FIG / f"wireframe_{key}.png", dpi=90, bbox_inches="tight"); plt.close(fig)

# ---------------- readiness scorecard ----------------
SCORE = [  # dimension, score(0-3), priority, evidence
 ("Event coverage", 1, "Critical", "38 events designed; none verified as implemented; supplied events do not follow the catalogue"),
 ("Data model", 1, "Critical", "Model designed; keys/links tested only for users, sessions, events, tasks. Rewards, wallet, withdrawals, referrals not supplied"),
 ("Data dictionary", 1, "High", "100 fields proposed; supplied dictionaries cover 2 + 26 fields and miss columns (DQ-033, DQ-034)"),
 ("KPI definitions", 2, "High", "46 KPIs defined; 18 KPI groups tested against supplied structure (10 calculable, 3 partial, 5 not)"),
 ("Data quality", 2, "High", "20 rules designed; 34 issues detected by automated checks with 11 passing tests; cleaning rules implemented"),
 ("Dashboard readiness", 1, "Medium", "7 dashboards specified and wireframed; no certified tables to power them"),
 ("Engineering instrumentation", 0, "Critical", "Nothing verified: IDs, idempotency, UTC timestamps and event emitters are all unknown (A001-A011)"),
 ("Access control", 1, "High", "Role model proposed; supplied data contains unnecessary personal fields (DQ-015)"),
 ("Documentation", 2, "Medium", "README, report, workbook, ER diagram, handoff spec; versioned in this project"),
 ("Reporting", 0, "Medium", "No governed recurring report exists; depends on production data"),
]
def scorecard():
    fig, ax = plt.subplots(figsize=(11, 6)); names = [s[0] for s in SCORE][::-1]; vals = [s[1] for s in SCORE][::-1]
    cols = ["#B91C1C" if v == 0 else "#D97706" if v == 1 else "#2563EB" for v in vals]
    ax.barh(names, vals, color=cols); ax.set_xlim(0, 3.4); ax.set_xticks([0, 1, 2, 3]); ax.set_xticklabels(["0 none", "1 designed", "2 tested on\nsimulated", "3 verified in\nproduction"])
    ax.set_title("Analytics readiness (rubric score 0-3, evidence-based; not a company metric)", fontsize=11, color=NAVY, loc="left")
    for i, v in enumerate(vals): ax.text(v + 0.04, i, str(v), va="center", fontsize=9)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    fig.savefig(FIG / "readiness_scorecard.png", dpi=110, bbox_inches="tight"); plt.close(fig)
    json.dump(SCORE, open(ROOT / "docs" / "readiness_scorecard.json", "w"), indent=1)

# ---------------- pipeline architecture ----------------
def pipeline():
    stages = [("VELOOP app\n+ backend", "source systems", "Engineering"), ("Event emitters\nREQ-001..015", "event producers", "Engineering"), ("Collection\nendpoint / queue", "collection", "Engineering"),
              ("Raw store\n(append-only)", "raw layer", "Engineering"), ("Validation\nQ01-Q19", "quality checks", "Data"), ("Staging +\ntransform (SQL)", "transformation", "Data"),
              ("Certified\nanalytical tables", "analytical layer", "Data"), ("BI dashboards\n(7 specified)", "dashboard", "Data / Product"), ("Business\nreporting", "reporting", "Product / Ops")]
    fig, ax = plt.subplots(figsize=(21.8, 6.2)); ax.set_xlim(0, 21.8); ax.set_ylim(0, 6.2); ax.axis("off")
    w, gap = 2.0, 0.37
    for i, (t, role, owner) in enumerate(stages):
        x = 0.2 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 3.0), w, 1.7, boxstyle="round,pad=0.03,rounding_size=0.12", fc=LIGHT, ec=NAVY, lw=1.8))
        ax.text(x + w / 2, 4.15, t, ha="center", va="center", fontsize=10, fontweight="bold", color=NAVY)
        ax.text(x + w / 2, 3.35, role, ha="center", va="center", fontsize=8.5, color=GREY)
        ax.text(x + w / 2, 2.65, "Owner: " + owner, ha="center", va="center", fontsize=8, color="#111827")
        if i < len(stages) - 1: ax.annotate("", xy=(x + w + gap - 0.03, 3.85), xytext=(x + w + 0.03, 3.85), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8))
    x5 = 0.2 + 4 * (w + gap)
    ax.add_patch(FancyBboxPatch((x5, 0.9), w, 1.0, boxstyle="round,pad=0.03", fc="white", ec="#B91C1C", lw=1.5, ls=(0, (4, 3))))
    ax.text(x5 + w / 2, 1.4, "Quarantine + alert\n(never drop rows)", ha="center", va="center", fontsize=8.5, color="#B91C1C")
    ax.annotate("", xy=(x5 + w / 2, 1.95), xytext=(x5 + w / 2, 3.0), arrowprops=dict(arrowstyle="->", color="#B91C1C", lw=1.5, ls="--"))
    xm = 0.2 + 6 * (w + gap)
    ax.add_patch(FancyBboxPatch((xm, 0.9), w + 2.4, 1.0, boxstyle="round,pad=0.03", fc="white", ec=GREY, lw=1.5, ls=(0, (4, 3))))
    ax.text(xm + (w + 2.4) / 2, 1.4, "Monitoring: freshness, volume, schema drift", ha="center", va="center", fontsize=8.5, color=GREY)
    ax.annotate("", xy=(xm + 1.0, 1.95), xytext=(xm + 1.0, 3.0), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.5, ls="--"))
    ax.text(0.2, 5.8, "VELOOP analytics pipeline (proposed). Start simple: app database + one warehouse + scheduled SQL + low-cost BI; daily refresh (hourly for the withdrawal queue).", fontsize=12, fontweight="bold", color=NAVY)
    ax.text(0.2, 0.25, "PROPOSED DESIGN. Not a claim about current VELOOP infrastructure (assumptions A001-A011).", fontsize=9, color=GREY)
    fig.savefig(FIG / "pipeline_architecture.png", dpi=100, bbox_inches="tight"); plt.close(fig)

if __name__ == "__main__":
    er(); wireframes(); scorecard(); pipeline(); print("figures written:", sorted(p.name for p in FIG.iterdir()))
