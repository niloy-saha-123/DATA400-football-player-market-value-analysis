# Second Instructor Meeting

## Research Question

Which player characteristics and performance statistics are most strongly
associated with a football player's market value? (Associational only. No
causal claims.)

Framing: a data-cleaning, EDA and visualization project. No modeling is
planned or required.

## Meeting Talking Points

1. Question: what is associated with Transfermarkt market value? Descriptive,
   not causal.
2. Data: public Transfermarkt dataset, 14 European leagues, 2020/21–2024/25,
   32,046 player-seasons.
3. Quality rules: valuation no older than 365 days; per-90 stats only for
   >= 450 minutes; 920 rows excluded (2.8%).
4. Value is very right-skewed, so everything is on a log scale.
5. Age is a hump, not a line: rises to about 22–29, then falls.
6. Playing time is the strongest simple correlate (Spearman about 0.5);
   goals/assists per 90 matter more for attackers than defenders.
7. League is a big confound (Premier League median €13M vs Ukraine €0.35M).
8. Ask for advice on league handling, the valuation rule, and whether the EDA
   needs another comparison or visualization.

## Figures to Show Professor

1. `market_value_distribution.png`: player-season market value on a log axis,
   with the median marked.
   *Say:* "Values are extremely right-skewed, so I use a log scale everywhere."
2. `market_value_by_age_position.png`: median value by age, one line per
   position.
   *Say:* "Value rises to a plateau in the mid-20s and then falls, and
   goalkeepers sit lower and peak later, so a straight-line age correlation
   is misleading."
3. `value_vs_per90_by_position.png`: goals/assists per 90 vs value for
   attackers and midfielders (>= 450 minutes).
   *Say:* "Attackers' value rises with goals per 90; midfielders' assists
   flatten out. Performance stats matter differently by role."
4. `market_value_by_league.png`: value distribution per league, sorted by
   median.
   *Say:* "League medians differ by about 37x, which is my biggest concern and
   my main question for you."

## Data

- **Source:** transfermarkt-datasets (public, CC0, scraped from Transfermarkt).
  Value is Transfermarkt's estimate, not a sale price.
- **Scope:** 2020/21–2024/25; 14 Aug–May domestic top flights (LaLiga, Serie A,
  Premier League, Bundesliga, Ligue 1, Süper Lig, Liga Portugal, Eredivisie,
  Belgian Pro League, Scottish Premiership, Greek Super League, Danish
  Superliga, Russian and Ukrainian Premier Leagues).
- **Rows:** 32,046 player-seasons. Defender 10,942 · Midfield 9,428 ·
  Attack 9,116 · Goalkeeper 2,560.
- **Construction:** appearances → join games (season, league) → aggregate to
  player-season (minutes, goals, assists) → join players (position, age) →
  join historical valuation → apply quality rules. Multi-club seasons (6.4%)
  keep one row, labeled by most minutes.
- **Valuation rule:** latest valuation on or before July 31 of the season's end
  year, no more than 365 days old at that cutoff.
- **Per-90 rule:** rates only analysed for rows with >= 450 minutes (23,328
  rows, 72.8%). Low-minute rows are kept. 450 is a practical stability rule
  (before it, goals/90 reached 90), not a "correct" number.
- **Exclusions (32,966 → 32,046):** 9 missing position, 5 missing date of birth,
  490 no valuation by the cutoff, 416 valuation older than 365 days.
- **Fixed:** the source labels Russia and Ukraine both as `premier-liga`;
  leagues now use unique `competition_id` plus readable names.

## Preliminary Findings

Numbers are from `notebooks/03_initial_eda.ipynb`.

1. **Age is a hump, not a line.** Median value is about €1.8–2.5M from age
   22 to 29 for outfield players and about €0.3–0.6M by the mid-30s
   (`market_value_by_age_position.png`). Spearman(age, value) is only −0.03
   because the relationship is not monotonic. *Limit:* cross-sectional; age is
   not separated from playing time, club or league.
2. **Playing time has the strongest simple association.** Spearman(minutes,
   value) is 0.51 pooled and 0.47–0.57 within each position. *Limit:* partly
   reverse/shared causation (valued players get picked), so not purely
   "performance".
3. **Goal/assist rates matter more for attackers.** Spearman(goals/90, value):
   Attack 0.37, Midfield 0.23, Defender 0.18 (>= 450 min)
   (`value_vs_per90_by_position.png`). *Limit:* moderate correlations and
   noisy rates; no defensive or goalkeeping stats.
4. **League is a large confound.** Median value: Premier League €13M; Serie A
   and Bundesliga €4M; Ligue 1 €3.5M; LaLiga €3M; all others €1M or less, down
   to the Ukrainian league at €0.35M (`market_value_by_league.png`). Within-league
   correlations for minutes and per-90 rates are similar to or higher than the
   pooled ones, so findings 2–3 are not just a league effect. *Limit:*
   describes differences only; club strength is not in the data.

## Important Limitations

- Transfermarkt value is an estimate with its own timing and biases.
- League differences are not yet controlled for.
- Goals/assists don't describe defenders or goalkeepers.
- The July 31 / 365-day valuation rule is an assumption; 384 of the 416 stale
  exclusions are in 2024 (cause not investigated).
- Russian and Ukrainian leagues are kept, but 2022+ is affected by the war.
- Age, minutes and performance are correlated with each other; simple
  correlations do not separate them.

## Decisions I Want Professor Feedback On

1. **League:** market values differ dramatically across leagues. Should I keep
   all 14 leagues and compare/stratify them, or narrow the scope to a smaller
   set of leagues?
2. **Valuation rule:** is "latest valuation on or before July 31, no older than
   365 days" a reasonable season-end mapping?
3. **Depth:** does the current position-aware EDA and visualization approach
   provide enough depth for the mini-project, or is there another comparison
   or visualization you think would strengthen the analysis?

## Presentation Story

1. Research question / why it matters
2. Data and player-season construction
3. Overall market-value patterns
4. Position-aware findings
5. League/context effects and limitations
6. Main conclusions
