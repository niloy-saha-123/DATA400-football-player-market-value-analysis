# Report outline

Statistics below are taken from the executed notebooks. Prose is not drafted;
each section lists what to say, which figure supports it, and the numbers
available. Re-check any number against the notebook before quoting it.

## 1. Introduction
- Transfermarkt values are quoted widely but it is unclear what they track.
- Purpose: describe which characteristics are associated with value; no prediction, no causation.
- Figure: none (or `01_value_distribution.png` as a teaser).

## 2. Research question
- "Which player characteristics and performance statistics are most strongly associated with a football player's market value?"
- Audience: students/instructor; football analysts and fans reading value figures.

## 3. Motivation
- Values influence transfer talk and contract discussions; knowing what they correlate with helps read them critically.
- Context: league gaps and role differences mean a single "value driver" list would mislead.

## 4. Data
- Source: transfermarkt-datasets (public, CC0, dcaribou); Transfermarkt's estimated values, not prices.
- Tables used: `players`, `appearances`, `games`, `player_valuations`, `clubs`, `competitions`.
- Scope: 14 Aug-May domestic top flights, 2020/21-2024/25. Calendar-year leagues and 9 leagues with no match-level appearances excluded (`DATA_PLAN.md`).
- Statistics: 32,046 player-seasons; 13,511 distinct players; Defender 10,942, Midfield 9,428, Attack 9,116, Goalkeeper 2,560; per season 6,671 / 5,860 / 6,700 / 6,679 / 6,136.
- Figures: none.

## 5. Data preparation
- Join appearances to games for season/competition; aggregate to player-season (minutes, goals, assists); primary club = most minutes (6.4% of player-seasons involve more than one club).
- Age at Aug 1; valuation = latest on or before July 31 after the season, at most 365 days old (median lag 55 days, 95th percentile 76).
- Exclusions (32,966 to 32,046): 9 missing position, 5 missing date of birth, 490 no valuation, 416 valuation older than 365 days.
- Per-90 eligibility >= 450 minutes: 23,328 rows (72.8%); before the rule per-90 values reached 90, after it max goals/90 = 1.50.
- Fixed identity issue: Russia and Ukraine share `premier-liga` in the source; unique `competition_id` used.
- Derived variables: age_group, goal_contributions, minutes_per_appearance, market_value_millions, log_market_value.
- Files: `exclusion_summary.csv`, `notebooks/02_build_player_season.ipynb`.

## 6. Exploratory analysis
- Distribution: median €1.3M, mean €5.4M, max €200M; skewness 5.25 raw vs 0.28 log10 (`01`).
- Age: age-group medians €0.8M / 1.8M / 2.0M / 1.8M / 0.75M; Spearman -0.03 (`02`).
- Position: medians Attack 1.5M, Midfield 1.5M, Defender 1.2M, Goalkeeper 0.8M (`03`).
- Minutes: Spearman 0.51; appearances 0.54; within position 0.47-0.57 (`04`).
- Performance: goals + assists per 90 vs value, Attack 0.45, Midfield 0.26, Defender 0.19, Goalkeeper 0.10 (`05`, `06`).
- League: Premier League €13M, Serie A/Bundesliga €4M, Ligue 1 €3.5M, LaLiga €3M, rest <= €1M, Ukraine €0.35M; 37x gap (`07`, `08`).
- Sub-position: little beyond main position (`09`).
- Association summary: eta squared of log value: league 0.355, age group 0.065, sub-position 0.010, position 0.007, season 0.004 (`10`).
- Confound check: minutes within-league median 0.56 (0.37-0.63); attackers' goals + assists/90 within-league median 0.53 (0.38-0.59).

## 7. Player segmentation
- Question, scope: 6,095 attackers with >= 450 minutes; features age, minutes, goals/90, assists/90; market value excluded from clustering.
- Choosing k: silhouette 0.219 / 0.215 / 0.207 / 0.214 / 0.209 for k = 2-6; no elbow; k = 4 chosen for interpretability (`11`).
- Stability: adjusted Rand index vs the seed-0 fit, minimum 0.92 / median 0.97 across 10 seeds; minimum 0.89 / median 0.92 on 80% subsamples.
- Clusters (n, median value): regular high-minute starters 1,576, €8M; creative 1,018, €5M; younger lower-output 2,046, €1.5M; older fewer minutes 1,455, €1M (`12`, `13`, `14`).
- Eta squared of log value: K-means clusters 0.230, league 0.430, age group 0.056, rule-based segments 0.142.
- Rule-based segments and cut-offs: goals/90 top quartile 0.40; assists/90 top quartile 0.23; sizes High scorers 1,524, Creative 1,074, Young 1,235, Prime 1,456, Experienced 806 (`15`).
- Honest conclusion: readable slices of a continuum, not distinct types. Midfielders: silhouettes 0.21-0.26; defenders/goalkeepers lack variables.

## 8. Findings
- See `FINDINGS.md`: six findings, each with evidence, interpretation and limitation.

## 9. Limitations
- Estimated values; associational only; overlapping age/minutes/output/club/league; club strength missing.
- No defensive/goalkeeper/injury/contract data; per-90 needs >= 450 minutes; thresholds are choices.
- Repeated players across seasons; war effects in Russia/Ukraine from 2022; 384 of 416 stale-valuation exclusions are in 2024 (cause not investigated).
- 2022+ Ukraine/Russia and cross-league comparability.

## 10. Conclusion
- Answer: league and playing time show the strongest associations; age is nonlinear; attacking output matters mainly for attackers; position alone separates values little.
- Segmentation is exploratory and modest.
- Future work (not done): club-level context, role-specific statistics, within-league models, injuries.
