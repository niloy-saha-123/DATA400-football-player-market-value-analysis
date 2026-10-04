# Findings

All numbers come from `data/processed/player_season.csv` (32,046 player-seasons,
14 leagues, 2020/21-2024/25) via `notebooks/04_final_eda.ipynb` and
`notebooks/05_player_segmentation.ipynb`. Everything is associational.
Market value is Transfermarkt's estimate.

## 1. Value is extremely right-skewed; age follows a hump, not a line

**Evidence:** Skewness 5.25 raw vs 0.28 on log10 scale; median €1.3M, max €200M
(`figures/final/01_value_distribution.png`). Median value by age group: under 21
€0.8M, 21-23 €1.8M, 24-26 €2.0M, 27-29 €1.8M, 30+ €0.75M
(`02_value_by_age.png`). Spearman(age, value) = -0.03.

**Interpretation:** Value rises through the early 20s, plateaus at about 22-28
and falls after 30. A single correlation coefficient hides this, so age has to
be read from the curve.

**Limitation:** Cross-sectional. Players of different ages are different people
(and leagues, clubs, minutes), so this is not the path one player follows.

## 2. League is the largest single grouping in the data

**Evidence:** About 35% of the variance in log value lies between leagues,
against 6.5% between age groups, 1% between positions and 0.4% between seasons
(`10_association_summary.png`). Median value: Premier League €13M, Serie A and
Bundesliga €4M, Ligue 1 €3.5M, LaLiga €3M, all other leagues €1M or less, down
to €0.35M in Ukraine (`07_value_by_league.png`).

**Interpretation:** Market-value distributions differ substantially between
leagues, with a clear gap between five large leagues and the rest. Any pooled
relationship partly reflects which league a player is in.

**Limitation:** Does not say why. League is bundled with club wealth, revenue
and player pool, and club identity is not modelled. The Russian and Ukrainian
leagues are affected by the war from 2022. The share-of-variance figure is a
descriptive measure, not an effect size and not a "percentage contribution".

## 3. Playing time has the strongest simple numeric association

**Evidence:** Spearman(minutes, value) = 0.51; appearances 0.54; within
positions 0.47-0.57 (`04_value_by_minutes.png`). Within leagues the median
coefficient is 0.56 (range 0.37-0.63), so it is not only a league effect.

**Interpretation:** Higher-valued players play more, in every position and every
league.

**Limitation:** Works both ways: clubs play players they value, and playing
raises visibility and value. Injuries, club level and age are also tied to
minutes. This is not evidence that minutes cause value.

## 4. Goal involvement is more associated with value for attackers than for others

**Evidence:** Spearman(goals + assists per 90, value), players with at least
450 minutes: Attack 0.45, Midfield 0.26, Defender 0.19, Goalkeeper 0.10
(`05_attackers_performance.png`, `06_midfielders_performance.png`). For
attackers the within-league median is 0.53 (range 0.38-0.59).

**Interpretation:** Attacking output is associated with value mainly for
attackers, and remains after separating leagues. Even for attackers the spread at
any output level is wide (moderate correlation).

**Limitation:** Goals and assists are not a quality measure for defenders or
goalkeepers, and the data has no defensive or goalkeeping statistics.
Per-90 rates need at least 450 minutes (a practical threshold), and they are
noisy and partly reflect team and teammates.

## 5. Position and sub-position separate values little

**Evidence:** Median value: Attack and Midfield €1.5M, Defender €1.2M,
Goalkeeper €0.8M (`03_value_by_position.png`). Position explains about 1% of
log-value variance, sub-position about 1%. Grouped sub-position medians run from
€0.8M (goalkeeper) to €1.5M (`09_value_by_subposition.png`). Goalkeepers are the
lowest-valued position in nearly every league (`08_position_league_heatmap.png`).

**Interpretation:** Position matters far less than league or playing time;
goalkeepers are the main exception.

**Limitation:** Left/Right Midfield and Second Striker (under 300 rows each) are
left out of the sub-position chart. Similar medians do not mean similar
distributions: star attackers sit far above the rest.

## 6. K-means on attackers gives readable but weakly separated groups

**Evidence:** Four K-means clusters of 6,095 attackers with at least 450 minutes
(features: age, minutes, goals/90, assists/90; market value not used): regular
high-minute starters (median value €8M), creative attackers (€5M), younger
lower-output (€1.5M), older with fewer minutes (€1M)
(`12_kmeans_profiles.png`, `14_kmeans_value.png`). Silhouette is about 0.21 for
every k from 2 to 6 and there is no sharp elbow; repeated fits agree (adjusted Rand
index vs the seed-0 fit: minimum 0.92, median 0.97 across 10 seeds; minimum 0.89,
median 0.92 on 80% subsamples). Clusters explain 23% of log-value
variance among these attackers, league 43%.

**Interpretation:** K-means produced these groups from the selected variables.
They describe profiles that make football sense, but the data form a continuum
rather than separate lumps, and k = 4 was chosen for interpretability, not
because a metric selected it. Rule-based segments (high scorers, creative, young,
prime age, experienced; boundaries in notebook 05) are simpler to explain and
capture less of the value variation (14%).

**Limitation:** Exploratory. Cluster value differences mostly reflect minutes and
age, which are already associated with value. Not applied to midfielders (similar
silhouettes, goals/assists are weak descriptors), defenders or goalkeepers (no
suitable variables).

## 7. Young high-output attackers have the highest median values

**Evidence:** Attackers with at least 450 minutes, split by age band and by
whether goals + assists per 90 is in the top quartile (at least 0.595)
(`notebooks/05_player_segmentation.ipynb` §6b, `16_age_output_attackers.png`):

| Age band | High output: median (n) | Lower output: median (n) |
|---|---|---|
| Under 24 | €10M (513) | €2.3M (1,643) |
| 24-28 | €8M (625) | €2.0M (1,883) |
| 29+ | €3.5M (387) | €1.0M (1,044) |

The ordering holds inside the five largest leagues (young high output €31M vs
prime high output €25M) and outside them (€5M vs €4.5M). The share of
top-five-league players is similar across the groups (39-48%).

**Interpretation:** At the same output level, younger attackers carry higher
median values, and within every age band high-output attackers are valued far
above lower-output ones. This is consistent with value reflecting expected
future performance and resale potential, but the data cannot test that.

**Limitation:** Descriptive cross-tabulation with a practical quartile cut-off;
contract length, club level and potential are not in the data. The
high-output groups are fairly small (387-625 rows each).
