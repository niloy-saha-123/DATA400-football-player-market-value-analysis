"""Guided data story for the DATA 400 market-value project. Run: streamlit run app.py

All numbers are computed from data/processed/player_season.csv and
exclusion_summary.csv with the same functions the notebooks use (src/).
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import spearmanr
from sklearn.metrics import silhouette_score

from src import plots
from src.data import AGE_GROUPS, LOGMV, MIN_MINUTES, MV, POS_ORDER, ROOT, eur, filter_data, load_player_season, season_label
from src.plots import _eta_sq
from src.segments import FEATURES, K, SEED, attacker_groups, eligible_attackers, kmeans_fit, scale_features, segment_thresholds
from src.ui import callout, cards, css, html, section

REPO = "https://github.com/niloy-saha-123/DATA400-football-player-market-value-analysis"
SOURCE = "https://github.com/dcaribou/transfermarkt-datasets"
RAW_APPEARANCES = 1_894_350  # rows in raw appearances.csv.gz (notebook 01; raw data is not shipped with the app)
MULTI_CLUB_SHARE = "6.4%"  # share of player-seasons with more than one club (notebook 02, DATA_PLAN.md)

st.set_page_config(page_title="Football market value", layout="wide", initial_sidebar_state="collapsed")
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
                     "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11})
css()


@st.cache_data
def load():
    return load_player_season(), pd.read_csv(ROOT / "data" / "processed" / "exclusion_summary.csv")


@st.cache_data
def groups(df):
    return attacker_groups(df)


@st.cache_data
def k_scores(df):
    Z = scale_features(eligible_attackers(df))
    return {k: silhouette_score(Z, kmeans_fit(Z, k).labels_, sample_size=4000, random_state=SEED) for k in range(2, 7)}


FULL, HALF = 9.5, 4.5  # figure widths (inches) for full-width and half-width columns; ~100 px per inch on screen


def show(fig, width=FULL, max_h=6.5, height=None):
    """Resize before rendering so text renders at the same on-screen size in every column."""
    w, h = fig.get_size_inches()
    fig.set_size_inches(width, height or min(h * width / w, max_h))
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def rho(d, x):
    return spearmanr(d[x], d[LOGMV])[0]


df, excl = load()
elig = df[df["analysis_minutes_eligible"]]
n_start = int(excl.loc[0, "rows_remaining"])
drops = dict(zip(excl["step"], excl["rows_dropped"]))
first, last = df["season"].min(), df["season"].max()

html("""<div class="topnav">
<a href="#top">Overview</a><a href="#data">Data</a><a href="#value">Market value</a><a href="#age">Age</a>
<a href="#minutes">Playing time</a><a href="#position">Position</a><a href="#league">League</a>
<a href="#summary">Summary</a><a href="#profiles">Player profiles</a><a href="#findings">Findings</a>
<a href="#limits">Limitations</a></div>""")

# ---------------------------------------------------------------- 1. hero
html(f"""<div class="hero" id="top">
<div class="eyebrow">DATA 400 · Data Analytics Capstone</div>
<h1>What Factors Are Most Associated with Football Player Market Value?</h1>
<div class="eyebrow">Research question</div>
<div class="rq">"Which player characteristics and performance statistics are most strongly associated with a football
player's market value?"</div>
<p class="lead">Professional footballers with similar on-field output can carry very different market valuations.
This project uses five seasons of historical Transfermarkt-derived data to examine how age, position, playing time,
attacking output and league context are associated with a player's estimated market value.</p>
<div class="disclaimer">This is a descriptive and associational analysis. It does not try to determine a player's
"true" value, and it makes no causal claims.</div>
<div class="stats">
<div class="stat"><div class="num">{len(df):,}</div><div class="lbl">Player-seasons</div></div>
<div class="stat"><div class="num">{df['player_id'].nunique():,}</div><div class="lbl">Distinct players</div></div>
<div class="stat"><div class="num">{df['season'].nunique()}</div><div class="lbl">Seasons</div></div>
<div class="stat"><div class="num">{df['competition'].nunique()}</div><div class="lbl">Domestic leagues</div></div>
<div class="stat"><div class="num">{df['position'].nunique()}</div><div class="lbl">Main positions</div></div>
</div>
<p class="meta">Seasons {season_label(first)} → {season_label(last)} &nbsp;·&nbsp; Data source:
<a href="{SOURCE}">Transfermarkt Datasets</a> (public, CC0) &nbsp;·&nbsp; Scroll down to walk through the project.</p>
</div>""")

# ---------------------------------------------------------------- 2. what is market value
section("measure", "What exactly am I measuring?",
        "Before any chart: what does “market value” mean here?")
c1, c2 = st.columns([1, 1.25], gap="large")
with c1:
    html("""<div class="callout c-key"><div class="tag">Key idea</div>
<p style="font-size:1.6rem;font-weight:800;margin:0.3rem 0 0.6rem 0">Market value ≠ transfer fee</p>
<p>Market value is the <b>estimated</b> valuation Transfermarkt records for a player at a point in time.</p></div>""")
with c2:
    html("""<ul>
<li><b>Transfermarkt</b> is a football website that publishes estimated market values for players, updated a few times a year.</li>
<li>These values are <b>not</b> actual transfer fees paid between clubs.</li>
<li>They are <b>not</b> an objective “true price” either; they are expert and community estimates with their own biases.</li>
<li>Their strength is consistency: the same kind of estimate exists for thousands of players across many seasons, so they
can be compared.</li></ul>""")

# ---------------------------------------------------------------- 3. data pipeline
section("data", f"From {RAW_APPEARANCES / 1e6:.1f} million match records to one analytical dataset",
        "The raw data is organised around matches and dates. The question is about players and seasons.")
st.markdown(f"The source is a set of linked tables. The largest has one row for every player in every match "
            f"({RAW_APPEARANCES:,} rows). I combined them into one table where **one row = one player in one season**, "
            "called a *player-season*. The same player appears once per season they played.")
html("""<div class="pipeline">
<div class="step"><b>Appearances</b><span>minutes, goals, assists per match</span></div><div class="arrow">→</div>
<div class="step"><b>Games</b><span>which season and league each match was in</span></div><div class="arrow">→</div>
<div class="step"><b>Add up per season</b><span>total minutes, goals, assists</span></div><div class="arrow">→</div>
<div class="step"><b>Player details</b><span>position, date of birth → age</span></div><div class="arrow">→</div>
<div class="step"><b>Market value</b><span>the valuation at the end of that season</span></div><div class="arrow">→</div>
<div class="step final"><b>Player-season table</b><span>one row per player per season</span></div></div>""")
ex = df[(df["player_name"] == "Bukayo Saka") & (df["season"] == 2022)]
ex = (ex if len(ex) else df.head(1)).iloc[0]
demo = [("Player", ex["player_name"]), ("Season", season_label(ex["season"])), ("Age", f"{ex['age']:.0f}"),
        ("Position", ex["position"]), ("League", ex["competition"]), ("Minutes", f"{ex['total_minutes']:,}"),
        ("Goals", ex["goals"]), ("Assists", ex["assists"]), ("Goals/90", f"{ex['goals_per_90']:.2f}"),
        ("Assists/90", f"{ex['assists_per_90']:.2f}"), ("Market value", eur(ex[MV]))]
html("<p style='margin-top:1.2rem'><b>Example of one row</b> in the final dataset:</p><div class='rowdemo'>"
     + "".join(f"<div><div class='h'>{h}</div>{v}</div>" for h, v in demo) + "</div>")
st.markdown(f"<p class='meta' style='margin-top:0.8rem'>“Per 90” means per 90 minutes played (one full match), so players "
            f"with different playing time can be compared. Final dataset: <b>{len(df):,} player-seasons</b>, "
            f"<b>{df.shape[1]} variables</b>, {df['competition'].nunique()} top-flight leagues that run August to May.</p>",
            unsafe_allow_html=True)

# ---------------------------------------------------------------- 4. decisions
section("decisions", "Before analysing the data, I had to make a few decisions",
        "Real data needs rules. Each rule below is a practical choice, documented and applied consistently.")
cards([
    ("Rule 1", f"{MIN_MINUTES}-minute rule for per-90 stats",
     f"<p>Rates explode for players who barely played: 1 goal in 1 minute = <b>90 goals per 90</b> "
     f"(the raw maximum here is {df['goals_per_90'].max():.0f}).</p><p>Per-90 stats are only used for players with at least "
     f"{MIN_MINUTES} minutes (five full matches). With the rule, the maximum is {elig['goals_per_90'].max():.2f}. "
     f"Low-minute players stay in the data for everything else.</p>"),
    ("Rule 2", "Which market value belongs to a season?",
     f"<p>Valuations are recorded on irregular dates. For each season I take the most recent valuation on or before "
     f"<b>July 31</b> after the season ends, which captures the usual end-of-season update. "
     f"Median gap: {df['valuation_age_days'].median():.0f} days.</p>"),
    ("Rule 3", "No stale valuations",
     f"<p>If the latest valuation was more than <b>365 days</b> old, the row was excluded "
     f"({drops['Valuation older than 365 days at cutoff']:,} rows). Otherwise some seasons would be matched to values "
     f"several years out of date.</p>"),
    ("Rule 4", "Players who changed clubs",
     f"<p>{MULTI_CLUB_SHARE} of player-seasons involve more than one club. Season totals are kept, and the row is "
     "labelled with the club where the player played the most minutes.</p>"),
], min_px=200)
lost = n_start - len(df)
st.markdown(f"<p class='meta'>In total {lost:,} of {n_start:,} player-seasons ({lost / n_start:.1%}) were excluded: "
            f"{drops['Missing position']} missing position, {drops['Missing date of birth']} missing date of birth, "
            f"{drops['No valuation on/before July 31 cutoff']} with no valuation, "
            f"{drops['Valuation older than 365 days at cutoff']} with a stale valuation.</p>", unsafe_allow_html=True)

# ---------------------------------------------------------------- 5. distribution
section("value", "Football market values are extremely unequal",
        "What does the distribution of player values actually look like?")
show(plots.fig_value_distribution(df))
c1, c2 = st.columns(2, gap="large")
with c1:
    callout("shows", "What this shows",
            f"<p>Most player-seasons sit at fairly low values, while a small number of elite players reach extreme "
            f"valuations. Median: <b>{eur(df[MV].median())}</b>. Maximum: <b>{eur(df[MV].max())}</b>.</p>")
with c2:
    callout("key", "Reading the right-hand chart: log scale",
            "<p>On a log scale each step is ×10 (€100K → €1M → €10M) instead of +€X. It spreads out the lower values "
            "and compresses the extreme top end, so differences among typical players stay visible. Most value charts "
            "below use it, and compare <b>medians</b> (the middle player) rather than averages.</p>")

# ---------------------------------------------------------------- 6. age
section("age", "Does a player's age relate to market value?",
        "Each line is the median value of players of that age, one line per position.")
show_pos = st.pills("Positions shown", POS_ORDER, default=POS_ORDER, selection_mode="multi", key="age_pos")
sub = filter_data(df, positions=show_pos or [])
if sub.empty:
    st.info("Select at least one position.")
else:
    show(plots.fig_value_by_age(sub), max_h=4.8)
ag = df.groupby("age_group")[MV].median().reindex(AGE_GROUPS)
c1, c2 = st.columns(2, gap="large")
with c1:
    callout("shows", "What the data shows",
            "<p>Value rises through the early twenties, stays high through most of the twenties, and falls for older "
            "players. Goalkeepers sit lower and peak a little later.</p><p>Median by age group: "
            + ", ".join(f"{g} <b>{eur(v)}</b>" for g, v in ag.items()) + ".</p>")
with c2:
    callout("key", "Why visualisation matters here",
            f"<p>The overall Spearman correlation between age and value is <b>{rho(df, 'age'):.2f}</b>, close to zero. "
            "That does <b>not</b> mean age is unrelated to value. A correlation measures a steady up or down trend; this "
            "relationship rises and then falls, so the two halves cancel out.</p>")
st.caption("Spearman correlation: from −1 to +1, how consistently one variable goes up as the other goes up (based on ranks). "
           "0 = no consistent trend. Cross-sectional data: these are different players at different ages, not one player ageing.")

# ---------------------------------------------------------------- 7. minutes
section("minutes", "Do more valuable players play more?",
        "Players grouped by total minutes played in the season.")
show(plots.fig_value_vs_minutes(df), max_h=4.3)
pos_r = {p: rho(df[df["position"] == p], "total_minutes") for p in POS_ORDER}
c1, c2 = st.columns(2, gap="large")
with c1:
    callout("shows", "What this shows",
            f"<p>Playing time has one of the strongest simple numeric associations with market value: Spearman "
            f"<b>{rho(df, 'total_minutes'):.2f}</b> overall, between {min(pos_r.values()):.2f} and "
            f"{max(pos_r.values()):.2f} within each position.</p>")
with c2:
    callout("caution", "Association ≠ causation",
            "<p>Players who perform well earn more minutes; clubs pick the players they value; and club quality or "
            "ability can drive both. More minutes are <b>associated</b> with higher value, but this analysis does not "
            "show that playing more <b>causes</b> value to rise.</p>")

# ---------------------------------------------------------------- 8. position
section("position", "Football positions should not be evaluated the same way",
        "Do the four main positions differ in value?")
c1, c2 = st.columns([1.5, 1], gap="large")
with c1:
    show(plots.fig_value_by_position(df), width=5.4, height=4.8)
with c2:
    pm = df.groupby("position")[MV].median()
    callout("shows", "What this shows",
            "<p>Outfield positions have similar medians (" + ", ".join(f"{p} {eur(pm[p])}" for p in POS_ORDER[1:])
            + f"); goalkeepers are lowest ({eur(pm['Goalkeeper'])}). Position on its own separates values much less "
            "than you might expect.</p>")
    callout("key", "Why position matters for the analysis",
            "<p>An attacker and a goalkeeper have different jobs. Goals and assists are core output for attackers but "
            "say little about centre-backs, full-backs or goalkeepers. So performance stats are read "
            "<b>position by position</b>.</p>")
st.caption("Box = middle 50% of players; line = median; whiskers = typical range (extreme outliers hidden).")

# ---------------------------------------------------------------- 9. attacking output
section("attack", "For attackers, does scoring relate to value?",
        f"Explore a position. Per-90 stats use players with at least {MIN_MINUTES} minutes.")
pos = st.segmented_control("Position", ["Attack", "Midfield", "Defender", "Goalkeeper"], default="Attack",
                           key="perf_pos", label_visibility="collapsed") or "Attack"
if pos == "Attack":
    show(plots.fig_perf_vs_value(df, pos, ["goals_per_90", "goal_contributions_per_90"]))
elif pos == "Midfield":
    show(plots.fig_perf_vs_value(df, pos, ["assists_per_90", "goals_per_90"]))
else:
    callout("caution", f"No suitable performance statistics for {pos.lower()}s",
            "<p>The dataset has no " + ("tackles, interceptions, aerial duels or blocks" if pos == "Defender"
                                        else "saves, save percentage or goals prevented")
            + f". Goals and assists are not used as a quality measure for {pos.lower()}s; only age and playing time "
            "are shown.</p>")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        show(plots.fig_value_by_age(df[df["position"] == pos]), width=HALF)
    with c2:
        show(plots.fig_value_vs_minutes(df[df["position"] == pos]), width=HALF)
g90 = {p: rho(elig[elig["position"] == p], "goals_per_90") for p in POS_ORDER}
gc90 = {p: rho(elig[elig["position"] == p], "goal_contributions_per_90") for p in POS_ORDER}
c1, c2 = st.columns(2, gap="large")
with c1:
    callout("shows", "What this shows",
            "<p>Black dots are the median value of players grouped by output. For attackers, value rises steadily with "
            f"output. Spearman correlation of goals per 90 with value: Attack <b>{g90['Attack']:.2f}</b>, Midfield "
            f"<b>{g90['Midfield']:.2f}</b>, Defender <b>{g90['Defender']:.2f}</b>. For goals + assists per 90: "
            f"{gc90['Attack']:.2f}, {gc90['Midfield']:.2f}, {gc90['Defender']:.2f}.</p>")
with c2:
    callout("caution", "Careful interpretation",
            "<p>This does not mean goals are unimportant for defenders; goals are simply a much more central part of an "
            "attacker's role and market profile. Even for attackers the spread at any output level is wide, and the "
            "association does not show that goals cause value.</p>")

# ---------------------------------------------------------------- 10. league
section("league", "Where a player competes matters enormously",
        "Market value in each of the 14 leagues, sorted by median.")
all_lg = sorted(df["competition"].unique())
chosen = st.multiselect("Compare leagues", all_lg, key="lg", placeholder="All 14 leagues shown. Pick leagues to compare them.")
show(plots.fig_value_by_league(df[df["competition"].isin(chosen or all_lg)]), max_h=7.5)
lm = df.groupby("competition")[MV].median().sort_values(ascending=False)
eta_lg, eta_pos = _eta_sq(df, "competition"), _eta_sq(df, "position")
c1, c2 = st.columns(2, gap="large")
with c1:
    callout("shows", "What this shows",
            f"<p>The {lm.index[0]} median is <b>{eur(lm.iloc[0])}</b>; {int((lm <= 1e6).sum())} of the 14 leagues have "
            f"medians of €1M or less, down to {eur(lm.iloc[-1])} ({lm.index[-1]}). That is a "
            f"<b>{lm.iloc[0] / lm.iloc[-1]:.0f}×</b> gap between league medians.</p><p>League grouping accounts for far "
            f"more of the variation in (log) market value than broad position grouping: about "
            f"<b>{eta_lg:.0%}</b> of the variation lies between leagues, versus about <b>{eta_pos:.0%}</b> between "
            "positions.</p>")
with c2:
    callout("caution", "League is context, not a cause",
            "<p>This does not show that playing in the Premier League makes a player worth more. Leagues differ in "
            "clubs, finances, player quality, media exposure, competition and transfer markets. League is a major "
            "contextual factor that overlaps with everything else. Russian and Ukrainian leagues are affected by the "
            "war from 2022.</p>")
with st.expander("Position × league: median value table as a heatmap"):
    show(plots.fig_position_league_heatmap(df), width=7, max_h=8)

# ---------------------------------------------------------------- 11. association summary
section("summary", "So which characteristics appear most related to value?",
        "Two different measures, shown side by side, never added together.")
show(plots.fig_association_summary(df))
c1, c2 = st.columns(2, gap="large")
with c1:
    callout("shows", "How to read this",
            "<p><b>Left, group differences:</b> for categories (league, age group, position), the share of variation in "
            "log value that lies <i>between</i> the groups (eta squared). <b>Right, numeric associations:</b> Spearman "
            "correlations for numbers like minutes and output. League and playing time stand out; attacking output "
            "matters mainly for attackers; age needs the curve from above.</p>")
with c2:
    callout("caution", "No percentage breakdown",
            "<p>There is no valid “age = 20%, goals = 30%, league = 40%” split from this analysis. The measures are "
            "different, and the factors overlap (bigger leagues, more minutes, prime age often go together). The chart "
            "compares the strength of individual relationships, not shares of a whole.</p>")

# ---------------------------------------------------------------- 12. clustering explained
g = groups(df)
sil = k_scores(df)
section("profiles", "Do similar attackers naturally form distinct player types?",
        "My professor suggested testing whether players fall into natural groups.")
c1, c2 = st.columns([1.2, 1], gap="large")
with c1:
    st.markdown(f"""**K-means** is an algorithm that groups observations that are similar across selected
characteristics. You choose the number of groups (*k*); it places players with similar numbers in the same group.

I applied it to **{len(g):,} attacker player-seasons** with at least {MIN_MINUTES} minutes, using four characteristics:
**age, minutes played, goals per 90, assists per 90** (scaled so that each counts equally).

Only attackers were used: they are the one position where the available statistics describe the role reasonably well.""")
with c2:
    callout("key", "Market value was NOT used to form the groups",
            "<p>Market value is the thing we want to compare <i>after</i> forming groups of similar players. Using it "
            "to build the groups would make the comparison circular.</p>")

# ---------------------------------------------------------------- 13. did it work
section("kmeans", "The players did not separate into clean natural clusters",
        "Did K-means find real player types?")
cards([
    ("Tested", "k = 2 to 6", "<p>Five different numbers of groups were tried.</p>"),
    ("Silhouette score", f"{min(sil.values()):.2f} to {max(sil.values()):.2f}",
     "<p>Measures how well separated groups are (−1 to 1). Around 0.2 means heavy overlap; roughly 0.25 or less is "
     "usually read as weak structure.</p>"),
    ("Elbow", "No clear elbow", "<p>The fit improved smoothly as k grew, with no point where extra groups stopped helping.</p>"),
    ("Chosen", f"k = {K}", "<p>Chosen because the four groups are readable, <b>not</b> because the data showed four "
                           "objectively correct types.</p>"),
], min_px=200)
prof = (g.groupby("kmeans_group").agg(n=("age", "size"), age=("age", "median"), mins=("total_minutes", "median"),
                                      g90=("goals_per_90", "median"), a90=("assists_per_90", "median"), v=(MV, "median"))
        .sort_values("v", ascending=False))
cards([(f"{int(r.n):,} players", name,
        f"<p>Median age {r.age:.0f} · {r.mins:,.0f} min · {r.g90:.2f} goals/90 · {r.a90:.2f} assists/90</p>"
        f"<p class='big'>{eur(r.v)}</p><p>median market value</p>")
       for name, r in prof.iterrows()], min_px=200)
c1, c2 = st.columns([1.2, 1], gap="large")
with c1:
    show(plots.fig_pca(g, "kmeans_group"), width=5.6, height=4.6)
with c2:
    callout("shows", "What the picture shows",
            "<p>PCA squeezes the four characteristics into two dimensions so they can be drawn. Each dot is an attacker, "
            "coloured by K-means group. The colours blend into each other instead of forming separate islands: "
            "a picture of overlap, not proof of real groups.</p>")
show(plots.fig_value_by_group(g, "kmeans_group"), height=3.6)
st.caption("Value differs between the groups mostly through minutes and age, which were already associated with value.")
callout("key", "Conclusion on clustering",
        "<p>These groups are <b>overlapping slices of a continuous population of attackers, not four natural types of "
        f"attacker</b>. K-means produced them from the selected variables. The groups account for about "
        f"{_eta_sq(g, 'kmeans_group'):.0%} of the variation in log value among these attackers; league alone accounts "
        f"for about {_eta_sq(g, 'competition'):.0%}.</p>")
with st.expander("Cluster profile heatmap"):
    show(plots.fig_group_heatmap(g, "kmeans_group", FEATURES), width=8)

# ---------------------------------------------------------------- 14. rule-based segments
section("segments", "A transparent alternative: rule-based player segments",
        "Because K-means did not produce strongly separated groups, I also defined simple football-oriented segments.")
t = segment_thresholds(g)
seg = g.groupby("domain_segment").agg(n=("age", "size"), v=(MV, "median"))
rules = [("High scorers", f"Goals/90 ≥ {t['goals_q3']:.2f} (top quarter of attackers)"),
         ("Creative attackers", f"Assists/90 ≥ {t['assists_q3']:.2f} (top quarter), not already a high scorer"),
         ("Young (under 24)", "Everyone else, younger than 24"),
         ("Prime age (24-28)", "Everyone else, aged 24 to 28"),
         ("Experienced (29+)", "Everyone else, 29 or older")]
cards([(f"Rule {i}", name, f"<p>{rule}</p><p class='big'>{eur(seg.loc[name, 'v'])}</p>"
                           f"<p>median value · {seg.loc[name, 'n']:,} players</p>")
       for i, (name, rule) in enumerate(rules, 1)], min_px=165)
show(plots.fig_value_by_group(g, "domain_segment"), height=4.0)
c1, c2 = st.columns(2, gap="large")
with c1:
    callout("key", "Segments are not clusters",
            "<p>These groups are <b>defined by me with explicit rules</b> (applied in the order shown, so each attacker "
            "gets one segment). They are easy to explain, but they are not discovered by machine learning, and their "
            "sizes reflect my cut-offs.</p>")
with c2:
    callout("shows", "What this shows",
            "<p>High scorers and creative attackers have the highest median values; experienced attackers the lowest. "
            f"Segments account for about {_eta_sq(g, 'domain_segment'):.0%} of the variation in log value, less than "
            f"the K-means groups ({_eta_sq(g, 'kmeans_group'):.0%}).</p>")
with st.expander("Who is in each group? Highest-valued examples"):
    view = st.segmented_control("Grouping", ["K-means clusters", "Rule-based segments"], default="K-means clusters",
                                key="ex_view") or "K-means clusters"
    col = "kmeans_group" if view == "K-means clusters" else "domain_segment"
    top = g.sort_values(MV, ascending=False).groupby(col).head(3)
    cards([("", name, "".join(f"<p>{r.player_name} · {season_label(r.season)} · {r.club} · {eur(r.market_value_in_eur)}</p>"
                               for r in s.itertuples()))
           for name, s in top.groupby(col)])

# ---------------------------------------------------------------- 15. findings
section("findings", "What did the analysis show?")
lg_first = lm.index[0]
html(f"""<div class="cards">
<div class="finding"><div class="n">01 · AGE</div><h4>Value follows a curve, not a line</h4>
<p>It rises into the early twenties, plateaus, and falls after about 30.</p>
<div class="s">{rho(df, 'age'):.2f}</div><div class="sl">Spearman correlation, which hides the curve</div></div>
<div class="finding"><div class="n">02 · PLAYING TIME</div><h4>Among the strongest simple associations</h4>
<p>Players who play more tend to be valued more, in every position.</p>
<div class="s">{rho(df, 'total_minutes'):.2f}</div><div class="sl">Spearman, minutes vs value</div></div>
<div class="finding"><div class="n">03 · POSITION</div><h4>Stats matter differently by role</h4>
<p>Position alone separates values little; what matters is which statistics describe each role.</p>
<div class="s">{eur(pm['Goalkeeper'])}–{eur(pm.max())}</div><div class="sl">range of position medians</div></div>
<div class="finding"><div class="n">04 · ATTACKING OUTPUT</div><h4>Linked to value mainly for attackers</h4>
<p>Goals + assists per 90 relate to value far more for attackers than for defenders.</p>
<div class="s">{gc90['Attack']:.2f} vs {gc90['Defender']:.2f}</div><div class="sl">Spearman, attackers vs defenders</div></div>
<div class="finding"><div class="n">05 · LEAGUE</div><h4>Distributions differ dramatically</h4>
<p>League is the largest single grouping in the data.</p>
<div class="s">{lm.iloc[0] / lm.iloc[-1]:.0f}×</div><div class="sl">gap between highest and lowest league medians</div></div>
<div class="finding"><div class="n">06 · PLAYER TYPES</div><h4>No clean natural groups</h4>
<p>K-means found overlapping slices; transparent rule-based segments were easier to interpret.</p>
<div class="s">≈{np.mean(list(sil.values())):.2f}</div><div class="sl">silhouette score at every k tested</div></div>
</div>""")

# ---------------------------------------------------------------- 16. what not to conclude
section("not", "What should we NOT conclude?", "The data supports associations only. These statements go too far:")
html('<div class="cards">' + "".join(f'<div class="no"><b>✕</b> “{s}”</div>' for s in [
    "Scoring goals causes market value to rise.",
    "Playing more minutes causes value to rise.",
    f"Playing in the {lg_first} makes a player worth more.",
    "These clusters are the true categories of football players.",
    "Transfermarkt market value is the player's real price.",
]) + "</div>")
st.markdown("The same player can appear in up to five seasons, so the rows are not fully independent individuals.")

# ---------------------------------------------------------------- 17. limitations
section("limits", "Data limitations")
cards([
    ("1", "Values are estimates", "<p>Transfermarkt values have their own timing and biases.</p>"),
    ("2", "No defensive statistics", "<p>No tackles, interceptions, aerial duels or blocks.</p>"),
    ("3", "No goalkeeper statistics", "<p>No saves, save percentage or goals prevented.</p>"),
    ("4", "No injury history", "<p>Missing time is visible only as fewer minutes.</p>"),
    ("5", "Little contract or reputation data", "<p>Contract length, transfer demand and fame are not included.</p>"),
    ("6", "Overlapping factors", "<p>Club, league, age and playing time are intertwined; club strength is not measured.</p>"),
    ("7", "Russia and Ukraine after 2022", "<p>War conditions affect those leagues and their valuations.</p>"),
    ("8", "Practical thresholds", "<p>450 minutes, July 31 and 365 days are reasonable choices, not universally correct cut-offs.</p>"),
], min_px=210)

# ---------------------------------------------------------------- 18. technical details
with st.expander("Want the technical details?"):
    st.markdown(f"""
**Data source:** [transfermarkt-datasets]({SOURCE}) by David Caribou (CC0), tables `players`, `appearances`, `games`,
`player_valuations`, `clubs`, `competitions`. **Code:** [{REPO}]({REPO})

**Construction:** appearances joined to games (season, league) → filtered to 14 August–May top flights and seasons
{season_label(first)}–{season_label(last)} → summed per player-season → primary club/league = most minutes →
age at August 1 → valuation = latest on or before July 31 of the following year, ≤ 365 days old.

**Exclusions:** {n_start:,} → {len(df):,} rows. Missing position {drops['Missing position']}, missing date of birth
{drops['Missing date of birth']}, no valuation {drops['No valuation on/before July 31 cutoff']}, stale valuation
{drops['Valuation older than 365 days at cutoff']}. Per-90 eligible (≥ {MIN_MINUTES} min): {len(elig):,} rows
({len(elig) / len(df):.1%}); other rows are kept.

**Excluded scope:** 8 calendar-year leagues (different season calendar) and 9 leagues with no match-level data in the source.

**Measures:** Spearman rank correlation with log10 value; eta squared = between-group share of log10-value variance.
K-means: scikit-learn, k = {K}, 20 starts, seed {SEED}; per-90 rates capped at the 99th percentile, all four features
standardised; silhouette on a 4,000-row sample.

**Notebooks:** `01_data_inspection` → `02_build_player_season` → `03_initial_eda` → `04_final_eda` →
`05_player_segmentation`. **Libraries:** pandas, numpy, matplotlib, scipy, scikit-learn, streamlit.
""")
    st.dataframe(excl, hide_index=True)

html(f'<div class="footer">DATA 400 · Dickinson College · <a href="{REPO}">GitHub repository</a></div>')
