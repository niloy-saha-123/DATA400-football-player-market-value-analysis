"""Matplotlib figure builders shared by the notebooks and the Streamlit app.

Every function takes a DataFrame and returns a Figure; an empty frame gives a
figure that says so instead of raising.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, NullFormatter
from scipy.stats import spearmanr

from .data import AGE_GROUPS, LOGMV, MV, POS_COLORS, POS_ORDER, SUBPOS_GROUP, eur

EUR_AXIS = FuncFormatter(lambda v, _: eur(v))
GREY = "#555555"
plt.rcParams.update({
    "figure.dpi": 90, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 10, "font.size": 10,
})


def _empty(msg="No data for the current selection"):
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.text(0.5, 0.5, msg, ha="center", va="center", color=GREY)
    ax.axis("off")
    return fig


def _log_axis(ax, axis="y"):
    getattr(ax, f"set_{axis}scale")("log")
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_formatter(EUR_AXIS)
    a.set_minor_formatter(NullFormatter())


def fig_value_distribution(df):
    if df.empty:
        return _empty()
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4))
    a.hist(df[MV] / 1e6, bins=60, color="#7A8CA5")
    a.set(title="Raw scale: a few very high values", xlabel="Market value (€ millions)", ylabel="Player-seasons")
    b.hist(df[MV], bins=np.logspace(np.log10(df[MV].min()), np.log10(df[MV].max()), 50), color="#7A8CA5")
    _log_axis(b, "x")
    med = df[MV].median()
    b.axvline(med, color="#D55E00", lw=1.5)
    b.text(med * 1.1, b.get_ylim()[1] * 0.92, f"median {eur(med)}", color="#D55E00")
    b.set(title="Log scale: closer to symmetric", xlabel="Market value (log scale)", ylabel="Player-seasons")
    fig.tight_layout()
    return fig


def fig_value_by_age(df, min_n=20):
    if df.empty:
        return _empty()
    d = df.assign(age_int=df["age"].astype(int).clip(17, 36))
    fig, ax = plt.subplots(figsize=(9, 5))
    for pos in POS_ORDER:
        g = d[d["position"] == pos].groupby("age_int")[MV].agg(["median", "size"])
        g = g[g["size"] >= min_n]
        if len(g):
            ax.plot(g.index, g["median"], marker="o", ms=3, lw=2, color=POS_COLORS[pos], label=pos)
    _log_axis(ax)
    ax.set(title="Median market value by age", xlabel="Age (17 and 36 include younger/older)",
           ylabel="Median market value (log scale)")
    ax.legend(title="Position", frameon=False)
    ax.text(0.01, 0.01, f"Age-position cells with fewer than {min_n} players omitted", transform=ax.transAxes,
            fontsize=8, color=GREY)
    fig.tight_layout()
    return fig


def fig_value_by_position(df):
    if df.empty:
        return _empty()
    pos = [p for p in POS_ORDER if (df["position"] == p).any()]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = [df.loc[df["position"] == p, MV] for p in pos]
    bp = ax.boxplot(data, orientation="vertical", patch_artist=True, showfliers=False, widths=0.6,
                    medianprops={"color": "black"})
    for patch, p in zip(bp["boxes"], pos):
        patch.set_facecolor(POS_COLORS[p])
        patch.set_alpha(0.7)
    ax.set_xticks(range(1, len(pos) + 1), [f"{p}\n(n={len(x):,})" for p, x in zip(pos, data)])
    for i, x in enumerate(data, 1):
        ax.text(i, x.median() * 1.08, eur(x.median()), ha="center", fontsize=9)
    _log_axis(ax)
    ax.set(title="Market value by position (box = middle 50%, line = median)", ylabel="Market value (log scale)")
    fig.tight_layout()
    return fig


def fig_value_vs_minutes(df):
    if df.empty:
        return _empty()
    edges = [0, 450, 900, 1800, 2700, 10_000]
    labels = ["<450", "450-899", "900-1,799", "1,800-2,699", "2,700+"]
    b = pd.cut(df["total_minutes"], edges, right=False, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    groups = [(l, df.loc[b == l, MV]) for l in labels]
    groups = [(l, g) for l, g in groups if len(g)]
    bp = ax.boxplot([g for _, g in groups], patch_artist=True, showfliers=False, widths=0.6,
                    medianprops={"color": "black"})
    for patch in bp["boxes"]:
        patch.set_facecolor("#7A8CA5")
    ax.set_xticks(range(1, len(groups) + 1), [f"{l}\n(n={len(g):,})" for l, g in groups])
    for i, (_, g) in enumerate(groups, 1):
        ax.text(i, g.median() * 1.08, eur(g.median()), ha="center", fontsize=9)
    _log_axis(ax)
    rho = spearmanr(df["total_minutes"], df[MV])[0]
    ax.set(title=f"Market value by minutes played (Spearman = {rho:.2f})", xlabel="Total minutes in the season",
           ylabel="Market value (log scale)")
    fig.tight_layout()
    return fig


PLURAL = {"Attack": "Attackers", "Midfield": "Midfielders", "Defender": "Defenders", "Goalkeeper": "Goalkeepers"}
PERF_LABELS = {"goals_per_90": "Goals per 90", "assists_per_90": "Assists per 90",
               "goal_contributions_per_90": "Goals + assists per 90"}


def fig_perf_vs_value(df, position, metrics, sample=2500, seed=0):
    """Scatter plus binned medians of per-90 metrics vs value; df is filtered to eligible rows here."""
    d = df[(df["position"] == position) & df["analysis_minutes_eligible"]]
    if len(d) < 30:
        return _empty(f"Fewer than 30 eligible {position} rows for the current selection")
    fig, axes = plt.subplots(1, len(metrics), figsize=(5.2 * len(metrics), 4.6), squeeze=False)
    for ax, m in zip(axes[0], metrics):
        s = d.sample(min(sample, len(d)), random_state=seed)
        ax.scatter(s[m], s[MV], s=8, alpha=0.25, color=POS_COLORS[position])
        q = pd.qcut(d[m].rank(method="first"), 8)
        g = d.groupby(q, observed=True).agg(x=(m, "median"), y=(MV, "median"))
        ax.plot(g["x"], g["y"], color="black", marker="o", lw=2, label="median of 8 equal-size bins")
        _log_axis(ax)
        rho = spearmanr(d[m], d[MV])[0]
        ax.set(title=f"{PERF_LABELS[m]} (Spearman = {rho:.2f})", xlabel=PERF_LABELS[m], ylabel="Market value (log scale)")
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle(f"{PLURAL[position]} with at least 450 minutes (n={len(d):,})", fontweight="bold")
    fig.tight_layout()
    return fig


def fig_value_by_league(df):
    if df.empty:
        return _empty()
    order = df.groupby("competition")[MV].median().sort_values().index
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(order) + 1.8))
    data = [df.loc[df["competition"] == c, MV] for c in order]
    bp = ax.boxplot(data, orientation="horizontal", patch_artist=True, showfliers=False, widths=0.65,
                    medianprops={"color": "black"})
    for patch in bp["boxes"]:
        patch.set_facecolor("#7A8CA5")
    ax.set_yticks(range(1, len(order) + 1),
                  [f"{c}\nmedian {eur(x.median())}, n={len(x):,}" for c, x in zip(order, data)], fontsize=8)
    _log_axis(ax, "x")
    ax.set(title="Market value by league (sorted by median)", xlabel="Market value (log scale)")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def fig_position_league_heatmap(df):
    if df.empty:
        return _empty()
    t = df.pivot_table(index="competition", columns="position", values=MV, aggfunc="median")
    t = t.reindex(columns=[p for p in POS_ORDER if p in t]).sort_values(t.columns[-1] if len(t.columns) else None)
    order = df.groupby("competition")[MV].median().sort_values().index
    t = t.reindex(order)
    fig, ax = plt.subplots(figsize=(7, 0.4 * len(t) + 1.8))
    im = ax.imshow(np.log10(t.values), cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(t.shape[1]), t.columns)
    ax.set_yticks(range(t.shape[0]), t.index)
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            v = t.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, eur(v), ha="center", va="center", fontsize=8,
                        color="white" if np.log10(v) > 6.3 else "black")
    ax.grid(False)
    ax.set_title("Median market value: league x position")
    fig.tight_layout()
    return fig


def fig_value_by_subposition(df):
    d = df.assign(sub=df["sub_position"].map(SUBPOS_GROUP)).dropna(subset=["sub"])
    if d.empty:
        return _empty()
    order = d.groupby("sub")[MV].median().sort_values().index
    data = [d.loc[d["sub"] == s, MV] for s in order]
    pos_of = d.groupby("sub")["position"].first()
    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(data, orientation="horizontal", patch_artist=True, showfliers=False, widths=0.65,
                    medianprops={"color": "black"})
    for patch, s in zip(bp["boxes"], order):
        patch.set_facecolor(POS_COLORS[pos_of[s]])
        patch.set_alpha(0.7)
    ax.set_yticks(range(1, len(order) + 1), [f"{s}\nmedian {eur(x.median())}, n={len(x):,}" for s, x in zip(order, data)],
                  fontsize=8)
    _log_axis(ax, "x")
    ax.set(title="Market value by sub-position (colour = main position)", xlabel="Market value (log scale)")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def _eta_sq(df, col):
    m = df.groupby(col)[LOGMV].transform("mean")
    return 1 - ((df[LOGMV] - m) ** 2).sum() / ((df[LOGMV] - df[LOGMV].mean()) ** 2).sum()


def association_tables(df):
    """(category eta-squared table, numeric Spearman table); both describe the given rows only."""
    cats = {"League": "competition", "Age group": "age_group", "Sub-position": "sub_position",
            "Position": "position", "Season": "season"}
    eta = pd.Series({k: _eta_sq(df, c) for k, c in cats.items()}).sort_values()
    rows = []
    for label, col, sub in [("Minutes played", "total_minutes", df), ("Appearances", "appearances", df),
                            ("Minutes per appearance", "minutes_per_appearance", df),
                            ("Age (not linear)", "age", df)]:
        rows.append((label, "All players", spearmanr(sub[col], sub[LOGMV])[0]))
    e = df[df["analysis_minutes_eligible"]]
    for pos in ["Attack", "Midfield", "Defender"]:
        s = e[e["position"] == pos]
        rows.append(("Goals + assists per 90", pos, spearmanr(s["goal_contributions_per_90"], s[LOGMV])[0]))
    return eta, pd.DataFrame(rows, columns=["variable", "group", "spearman"])


def fig_association_summary(df):
    if len(df) < 100:
        return _empty("Need at least 100 rows for association summary")
    eta, sp = association_tables(df)
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    a.barh(eta.index, eta.values, color="#7A8CA5")
    for i, v in enumerate(eta.values):
        a.text(v + 0.005, i, f"{v:.0%}", va="center")
    a.set(title="Categorical: share of log-value variance\nlying between groups", xlim=(0, max(0.45, eta.max() * 1.2)),
          xlabel="Between-group share (eta squared)")
    a.grid(axis="y", visible=False)
    labels = [f"{r.variable}\n[{r.group}]" for r in sp.itertuples()]
    colors = [POS_COLORS.get(g, "#7A8CA5") for g in sp["group"]]
    b.barh(labels[::-1], sp["spearman"].values[::-1], color=colors[::-1])
    for i, v in enumerate(sp["spearman"].values[::-1]):
        b.text(v + (0.01 if v >= 0 else -0.01), i, f"{v:.2f}", va="center", ha="left" if v >= 0 else "right")
    b.axvline(0, color="black", lw=0.8)
    b.set(title="Numeric: Spearman rank correlation\nwith market value", xlabel="Spearman rho",
          xlim=(-0.15, 0.7))
    b.grid(axis="y", visible=False)
    fig.suptitle("Association strength (descriptive, not causal, not a percentage contribution)", fontsize=11)
    fig.tight_layout()
    return fig
