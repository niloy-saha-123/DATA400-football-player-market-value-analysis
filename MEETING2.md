# Second Instructor Meeting

## Research Question

Which player characteristics and performance statistics are most strongly
associated with a football player's market value?

(Associational only. No causal claims.)

## Current Data

- **Source:** transfermarkt-datasets (public, CC0 dataset scraped from
  Transfermarkt). Market value is Transfermarkt's estimate, not a sale price.
- **Seasons:** 2020/21–2024/25 (5).
- **Leagues:** 14 Aug–May European top flights (LaLiga, Serie A, Premier
  League, Bundesliga, Ligue 1, Süper Lig, Liga Portugal, Eredivisie, Belgian
  Pro League, Scottish Premiership, Greek Super League, Danish Superliga,
  Russian Premier League, Ukrainian Premier League).
- **Rows:** 32,046 player-seasons (one per player per season).
- **Positions:** Defender 10,942 · Midfield 9,428 · Attack 9,116 ·
  Goalkeeper 2,560.
- **Valuation rule:** latest Transfermarkt valuation on or before July 31 of
  the season's end year, and no more than 365 days old at that cutoff.
- **Exclusions (sequential, 32,966 → 32,046):** 9 missing position, 5 missing
  date of birth, 490 no valuation by the cutoff, 416 valuation older than 365
  days. (`data/processed/exclusion_summary.csv`)
- **Per-90 rule:** goals/assists per 90 are only analysed for rows with
  >= 450 minutes (23,328 rows, 72.8%). Low-minute rows are kept, just not
  used for rates. 450 is a practical stability rule, not a "correct" number:
  below it, per-90 values were absurd (up to 90 goals/90).

## Data Construction

appearances → join games → identify season and league → aggregate to
player-season (minutes, goals, assists; summed over clubs) → join players
(position, age) → join historical valuation → apply quality rules.
Multi-club seasons (6.4%) keep one row; club/league label = most minutes.

Fixed along the way: the source labels Russia and Ukraine both as
`premier-liga`; leagues are now keyed by unique `competition_id` with
readable names.

## Preliminary Findings

Figures are in `figures/`; numbers are from `notebooks/03_initial_eda.ipynb`.

**1. Value rises to a mid-20s plateau, then falls; a plain age correlation
hides this.**
- *Evidence:* `market_value_by_age_position.png`. Median values sit at roughly
  €1.8–2.5M from about age 22 to 29 for outfield players and fall to about
  €0.3–0.6M by the mid-30s. Goalkeepers are lower overall (median €0.8M vs
  €1.2–1.5M outfield) and peak later. Spearman(age, value) is only −0.03
  pooled, because the relationship is not monotonic.
- *Interpretation:* Age matters, but as a hump, not a straight line, so a
  linear age term would be misleading.
- *Limitation:* Cross-sectional. Older players in the data are survivors, and
  age is not separated from playing time, club or league.

**2. Playing time has the strongest simple association with value.**
- *Evidence:* Table 1. Spearman(total_minutes, value) = 0.51 pooled and
  0.47–0.57 within each position; the median within-league correlation is
  0.49–0.62 by position (Table 2).
- *Interpretation:* Players who play more are valued higher.
- *Limitation:* This is likely partly reverse or shared causation (valued
  players get selected; good clubs have valued players who play), so it is not
  a "performance" effect. Minutes also stand in for role and club.

**3. Goal and assist rates matter more for attackers than for defenders.**
- *Evidence:* `value_vs_per90_by_position.png` and Table 1 (>= 450 min).
  Spearman(goals/90, value): Attack 0.37, Midfield 0.23, Defender 0.18.
  Within-league medians are similar or higher (0.44, 0.31, 0.19). For
  midfielders, median value rises with assists/90 and then flattens.
- *Interpretation:* The stat that best reflects the role tracks value more
  strongly. For defenders and goalkeepers, goals/assists are weak proxies and
  this dataset has no defensive or goalkeeping stats.
- *Limitation:* Rates from >= 450 minutes are still noisy. Correlations are
  moderate (well under 0.5 for rates), and much variance is unexplained.

**4. League is a large confound.**
- *Evidence:* `market_value_by_league.png`. Median value: Premier League €13M;
  Serie A and Bundesliga €4M; Ligue 1 €3.5M; LaLiga €3M; every other league
  €1M or less, down to the Ukrainian Premier League at €0.35M (37x lower than
  the Premier League). Within-league correlations for minutes and per-90 rates (Table 2) are
  similar to or higher than the pooled ones, so findings 2–3 are not just a
  league effect.
- *Interpretation:* Pooling leagues mixes very different value scales.
- *Limitation:* Only shows differences, not reasons. Club strength and
  reputation are not in the data.

## Important Limitations

- Transfermarkt value is an estimate with its own update timing and biases.
- League differences (above) are not yet controlled for.
- Position-specific roles: goals/assists don't describe defenders or
  goalkeepers; no defensive, passing or goalkeeping data.
- Valuation timing: values are irregular; the July 31 / 365-day rule is an
  assumption. 384 of the 416 stale-valuation exclusions are in 2024 (cause not
  investigated).
- Russian and Ukrainian leagues are kept, but 2022+ is affected by the war.
- Age, minutes and performance are correlated with each other; simple
  correlations do not separate them.

## Questions for Professor

1. **League:** Market values differ by ~37x between leagues. Should I keep all
   14 and stratify or control for league, or narrow the analysis to the major
   leagues?
2. **Valuation rule:** Is "latest valuation on or before July 31, no older than
   365 days" a reasonable season-end mapping? Would you handle stale values
   differently?
3. **Method:** Is position-aware EDA plus correlations enough for this
   mini-project, or would a simple regression (e.g. log value on age, age²,
   minutes, per-90 stats, position, league) materially improve the answer?

## Presentation Story

1. **Research question / why it matters:** what tracks Transfermarkt value?
2. **Data and player-season construction:** source, scope, quality rules,
   exclusion counts.
3. **Overall market-value patterns:** right-skewed distribution (log scale),
   position differences.
4. **Position-aware findings:** age hump by position; goals/assists for
   attackers; playing time.
5. **League/context effects and limitations:** the league confound and what
   the data cannot say.
6. **Main conclusions:** what is associated with value, what is not shown, and
   what would come next.
