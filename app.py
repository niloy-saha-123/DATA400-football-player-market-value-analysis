"""Streamlit companion to the DATA 400 market-value analysis. Run: streamlit run app.py"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src import plots
from src.data import AGE_GROUPS, MV, POS_ORDER, eur, filter_data, load_player_season, season_label
from src.segments import FEATURES, attacker_groups, segment_thresholds

REPO = "https://github.com/niloy-saha-123/DATA400-football-player-market-value-analysis"
st.set_page_config(page_title="Football market value analysis", layout="wide")


@st.cache_data
def load():
    return load_player_season()


@st.cache_data
def groups(df):
    return attacker_groups(df)


def show(fig):
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def sidebar_filters(df, position=True):
    seasons = st.sidebar.multiselect("Season", sorted(df["season"].unique()), default=sorted(df["season"].unique()),
                                     format_func=season_label)
    leagues = st.sidebar.multiselect("League", sorted(df["competition"].unique()), default=sorted(df["competition"].unique()))
    positions = None
    if position:
        positions = st.sidebar.multiselect("Position", POS_ORDER, default=POS_ORDER)
    lo, hi = int(df["age"].min()), int(df["age"].max()) + 1
    age = st.sidebar.slider("Age range", lo, hi, (lo, hi))
    out = filter_data(df, seasons, leagues, positions, age)
    st.sidebar.caption(f"{len(out):,} of {len(df):,} player-seasons selected")
    return out


df = load()
page = st.sidebar.radio("Page", ["Overview", "Player characteristics", "Position analysis", "League analysis",
                                 "Player segments", "Methodology & limitations"])
st.sidebar.divider()

if page == "Overview":
    st.title("What Factors Are Most Associated with Football Player Market Value?")
    st.markdown("**Research question:** Which player characteristics and performance statistics are most strongly "
                "associated with a football player's market value? Descriptive and associational only; no causal claims.")
    c = st.columns(5)
    c[0].metric("Player-seasons", f"{len(df):,}")
    c[1].metric("Distinct players", f"{df['player_id'].nunique():,}")
    c[2].metric(f"Seasons ({season_label(df['season'].min())} to {season_label(df['season'].max())})", df["season"].nunique())
    c[3].metric("Leagues", df["competition"].nunique())
    c[4].metric("Positions", df["position"].nunique())
    show(plots.fig_value_distribution(df))
    st.markdown(f"Market values are heavily right-skewed (median {eur(df[MV].median())}, maximum {eur(df[MV].max())}), "
                "so every value chart in this app uses a **log scale** and medians rather than means. "
                "Values are Transfermarkt's estimates, not prices.")
    st.subheader("Association summary")
    show(plots.fig_association_summary(df))
    st.caption("Left and right panels use different measures and cannot be added up or read as percentage contributions.")

elif page == "Player characteristics":
    st.title("Player characteristics")
    sub = sidebar_filters(df)
    if sub.empty:
        st.warning("No player-seasons match the current filters.")
    else:
        a, b = st.columns(2)
        with a:
            show(plots.fig_value_by_age(sub))
        with b:
            show(plots.fig_value_vs_minutes(sub))
        st.caption("Age: median value by age, one line per position (cells with fewer than 20 players are omitted). "
                   "Minutes: playing time works both ways: valued players play more, and playing raises value.")
        show(plots.fig_value_by_position(sub))
        st.dataframe(sub.groupby("age_group")[MV].agg(["size", "median"]).reindex(AGE_GROUPS).dropna()
                     .rename(columns={"size": "player-seasons", "median": "median value (EUR)"}))

elif page == "Position analysis":
    st.title("Position analysis")
    pos = st.sidebar.selectbox("Position", POS_ORDER[::-1])
    leagues = st.sidebar.multiselect("League", sorted(df["competition"].unique()), default=sorted(df["competition"].unique()))
    sub = filter_data(df, leagues=leagues, positions=[pos])
    st.sidebar.caption(f"{len(sub):,} {pos} player-seasons selected")
    if sub.empty:
        st.warning("No player-seasons match the current filters.")
    elif pos == "Attack":
        st.info("Per-90 rates use players with at least 450 minutes.")
        show(plots.fig_perf_vs_value(sub, pos, ["goals_per_90", "assists_per_90", "goal_contributions_per_90"]))
    elif pos == "Midfield":
        st.info("Per-90 rates use players with at least 450 minutes. Goals and assists capture only part of "
                "what midfielders do, so read these correlations as modest.")
        show(plots.fig_perf_vs_value(sub, pos, ["assists_per_90", "goals_per_90"]))
    else:
        st.warning(f"The dataset has no {'tackle, interception, aerial or block' if pos == 'Defender' else 'save or goals-prevented'} "
                   f"statistics, and goals/assists say little about {pos.lower()}s. They are not used as a quality measure "
                   "here; only age, playing time and league are shown.")
        a, b = st.columns(2)
        with a:
            show(plots.fig_value_by_age(sub))
        with b:
            show(plots.fig_value_vs_minutes(sub))
    if not sub.empty:
        st.subheader("Sub-position")
        show(plots.fig_value_by_subposition(sub))

elif page == "League analysis":
    st.title("League analysis")
    leagues = st.sidebar.multiselect("Leagues to compare", sorted(df["competition"].unique()),
                                     default=sorted(df["competition"].unique()))
    sub = filter_data(df, leagues=leagues)
    if sub.empty:
        st.warning("Select at least one league.")
    else:
        show(plots.fig_value_by_league(sub))
        a, b = st.columns(2)
        with a:
            show(plots.fig_position_league_heatmap(sub))
        with b:
            st.markdown("**Position mix by league (share of player-seasons)**")
            mix = pd.crosstab(sub["competition"], sub["position"], normalize="index")[POS_ORDER]
            st.bar_chart(mix.mul(100).round(1), horizontal=True)
        st.caption("Market-value distributions differ substantially between leagues. This does not show that the league "
                   "itself changes value: club wealth, revenue and player pool are bundled with it.")

elif page == "Player segments":
    st.title("Player segments (attackers)")
    g = groups(df)
    st.markdown(f"{len(g):,} attacker player-seasons with at least 450 minutes. Market value was **not** used to form "
                "the groups; it is compared across them afterwards.")
    view = st.radio("Grouping", ["K-means clusters", "Rule-based segments"], horizontal=True)
    col = "kmeans_group" if view == "K-means clusters" else "domain_segment"
    if view == "K-means clusters":
        st.info("K-means (k = 4) on age, total minutes, goals/90 and assists/90 (per-90 rates capped at the 99th percentile, "
                "then standardised). Silhouette is about 0.21 for every k from 2 to 6, so the structure is weak: K-means "
                "cut a continuum of attacker profiles into four readable slices and did not find distinct player types. "
                "k = 4 was chosen for interpretability.")
    else:
        t = segment_thresholds(g)
        st.info(f"Segments are defined by explicit rules, not by an algorithm. In order: **High scorers** (goals/90 >= "
                f"{t['goals_q3']:.2f}, top quartile), **Creative attackers** (assists/90 >= {t['assists_q3']:.2f}, top "
                "quartile, not a high scorer), then by age: **Young** (under 24), **Prime age** (24-28), **Experienced** (29+).")
    prof = (g.groupby(col).agg(players=("age", "size"), median_age=("age", "median"), median_minutes=("total_minutes", "median"),
                               goals_per_90=("goals_per_90", "median"), assists_per_90=("assists_per_90", "median"),
                               median_value_eur=(MV, "median")).sort_values("median_value_eur", ascending=False).round(2))
    st.dataframe(prof.rename_axis("Group").rename(columns={
        "players": "Players", "median_age": "Median age", "median_minutes": "Median minutes",
        "goals_per_90": "Goals/90 (median)", "assists_per_90": "Assists/90 (median)",
        "median_value_eur": "Median value (EUR)"}))
    a, b = st.columns(2)
    with a:
        show(plots.fig_group_heatmap(g, col, FEATURES))
    with b:
        show(plots.fig_value_by_group(g, col))
    if view == "K-means clusters":
        show(plots.fig_pca(g, col))
        st.caption("PCA is a 2-D drawing of the four features. Overlap between clusters means they are not cleanly separated.")
    st.subheader("Highest-valued examples per group")
    top = g.sort_values(MV, ascending=False).groupby(col).head(3)[[col, "player_name", "season", "club", "age", "total_minutes",
                                                                    "goals_per_90", "assists_per_90", MV]]
    st.dataframe(top.sort_values([col, MV], ascending=[True, False]).round(2), hide_index=True)
    st.caption("Group differences in value mostly reflect minutes and age, which are already associated with value. "
               "Midfielders, defenders and goalkeepers are not segmented: the variables do not describe their roles.")

else:
    st.title("Methodology & limitations")
    st.markdown(f"""
**Data source:** [Transfermarkt datasets](https://github.com/dcaribou/transfermarkt-datasets) (public, CC0). Market value is
Transfermarkt's own estimate, not a sale price or transfer fee.

**Unit of observation:** one row per player-season (summed over clubs; labelled by the club with most minutes).
**Seasons:** 2020/21-2024/25. **Scope:** 14 August-May domestic top-flight leagues.

**Valuation rule:** latest valuation on or before July 31 after the season, no more than 365 days old.
**Per-90 rule:** goals/assists per 90 only for players with at least 450 minutes; other rows stay in the data for
age, position, minutes and value analyses.

**Groupings:** K-means clusters and rule-based segments are described on the *Player segments* page.

**Limitations**
- Transfermarkt values are estimates with their own timing and biases.
- Associations only: age, minutes, output, club and league overlap; no causal conclusions.
- League context is large (about 35% of log-value variance lies between leagues); club strength is not in the data.
- Attackers have the most relevant statistics. There are no defensive or goalkeeping metrics.
- Transfer fees are not the target.
- Thresholds (450 minutes, July 31, 365 days) are practical analytical decisions.
- The same players appear in several seasons; Russian and Ukrainian leagues are affected by war from 2022.

**Code and notebooks:** [{REPO}]({REPO})
""")
