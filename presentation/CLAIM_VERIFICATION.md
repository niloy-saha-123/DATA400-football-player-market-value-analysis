# Claim verification

Every number in the main deck (slides 1-11) and the backup deck (Backup A-E), where it comes from, and how it is calculated. All
values were recomputed from `data/processed/player_season.csv` and
`exclusion_summary.csv` with the functions in `src/` on 2026-10-04 and match the
executed notebooks. Abbreviations: NB04 = `notebooks/04_final_eda.ipynb`,
NB05 = `notebooks/05_player_segmentation.ipynb`, df = player_season.csv,
elig = rows with `analysis_minutes_eligible` (≥ 450 min), att = eligible attackers.

| Slide | Claim | Source | Calculation | Verified |
|---|---|---|---|---|
| 2 | Values range from tens of thousands to hundreds of millions of euros | NB04 §2 | min €20K, max €200M of `market_value_in_eur` | Y |
| 3 | 32,046 player-seasons | NB02 §9, NB04 §1 | `len(df)` | Y |
| 3 | 13,511 distinct players | NB04 §1 | `df.player_id.nunique()` | Y |
| 3 | 14 leagues; 5 seasons 2020/21-2024/25 | NB02 §9 | `nunique` of `competition`, `season` (2020-2024) | Y |
| 4 | About 1.9 million match rows | NB01 output | `appearances.csv.gz`: 1,894,350 rows | Y |
| 4 | 32,966 → 32,046; 920 excluded (2.8%) | `exclusion_summary.csv` | 9 + 5 + 490 + 416 + 0 | Y |
| 4 | 1 goal in 1 minute = 90 per 90; raw max goals/90 = 90 | NB02 §6, NB04 §1 | `goals_per_90.max()` over all rows | Y |
| 5 | Age-group medians €0.8M / €1.8M / €2.0M / €1.8M / €0.75M | NB04 §3 | `df.groupby(age_group)[MV].median()` | Y |
| 5 | Spearman(age, value) = -0.03 | NB04 §3 | `spearmanr(age, log_market_value)` = -0.034 | Y |
| 5 | Peak at 24-26 | NB04 §3 | highest age-group median (€2.0M) | Y |
| 6 | Goals/90 vs value: 0.37 / 0.23 / 0.18 | NB04 §6 | Spearman on elig by position (Attack, Midfield, Defender) | Y |
| 6 | n = 6,095 attackers with ≥ 450 min | NB05 §0 | `len(att)` | Y |
| 7 | League medians, €13M (Premier League) down to €350K (Ukraine) | NB04 §7 | `df.groupby(competition)[MV].median()` | Y |
| 7 | Top-five €4.5M vs other nine €600K | audit; recomputed | pooled median of Premier League, LaLiga, Serie A, Bundesliga, Ligue 1 vs rest | Y |
| 7 | ~35% of log-value variation between leagues; ~1% between positions | NB04 §10 | eta squared of `log_market_value` by `competition` (0.355), `position` (0.007) | Y |
| 8 | High output = top quartile of goals + assists per 90 (≥ 0.59) | NB05 §6b | `att.goal_contributions_per_90.quantile(0.75)` = 0.595 | Y |
| 8 | €10M (n=513) / €8M (625) / €3.5M (387) high output; €2.3M (1,643) / €2.0M (1,883) / €1.0M (1,044) lower | NB05 §6b | `age_output_groups(att)` then median by group | Y |
| 8 | Top-five: €31M vs €25M; other leagues: €5M vs €4.5M | NB05 §6b | same, split by league group | Y |
| 9 | 6,095 attacker-seasons; inputs age, minutes, goals/90, assists/90; value and league not used | `src/segments.py` | `FEATURES` list | Y |
| 9 | Silhouette 0.21-0.22 at every k (2-6) | NB05 §1 | 0.219, 0.215, 0.207, 0.214, 0.209 | Y |
| 9 | Cluster medians €8M / €5M / €1.5M / €1M | NB05 §2 | `attacker_groups(df)` median value per `kmeans_group` | Y |
| 10 | Spearman(minutes, value) = 0.51 | NB04 §5 | `spearmanr(total_minutes, log_market_value)` | Y |
| 10 | Other numbers repeat slides 5-9 | as above | - | Y |
| 11 | Same player in up to five seasons | data structure | 5 seasons, one row per player-season | Y |
| Backup A | Exclusion counts; 23,328 eligible (72.8%) | `exclusion_summary.csv` | as listed | Y |
| Backup B | Inertia 19,125 / 16,201 / 13,850 / 12,093 / 11,075 | NB05 §1 | `KMeans(k, n_init=20, random_state=0).inertia_` | Y |
| Backup B | Cluster sizes 1,576 / 1,018 / 2,046 / 1,455 and medians | NB05 §2 | group counts and medians | Y |
| Backup B | ARI minimum 0.92, median 0.97 (10 seeds); minimum 0.89, median 0.92 (80% subsamples) | NB05 §1 output | `adjusted_rand_score` vs seed-0 fit | Y |
| Backup B | Clusters ~23% of log-value variance | NB05 §3 | eta squared = 0.230 | Y |
| Backup C | Thresholds 0.40 / 0.23; segment sizes and medians | NB05 §6 | `segment_thresholds`, `domain_segments` | Y |
| Backup C | Segments ~14% vs clusters ~23% | NB05 §6 | eta squared 0.142 vs 0.230 | Y |
| Backup D | All 14 league medians | NB04 §7 | as slide 7 | Y |
| Backup E | Spearman 0.51 | NB04 §5 | as slide 10 | Y |

Interpretive statements (no number) and their basis:

- "Hump, not a line" (slides 5, 10): age-group and single-age medians rise to 24-26 and fall after 30 (NB04 §3).
- "Goals track value most for attackers" (slide 6): highest Spearman among positions.
- "Context, not cause" (slide 7) and "Descriptive only" (slide 8): methodological caution, not a result.
- "Weak separation; a continuum" (slide 9): silhouette ≈ 0.21 at every k, no sharp elbow, overlap in the PCA view (NB05 §1-2).
- "Likely runs both ways" (backup E): interpretation, stated as possible, not tested.
