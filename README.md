# What Factors Are Most Associated with Football Player Market Value?

DATA 400 — Data Analytics Capstone Mini-Project, Dickinson College.

## Research question

Which player characteristics and performance statistics are most strongly
associated with a football (soccer) player's market value?

This is an **associational**, not causal, analysis: it describes what tends to
be higher or lower alongside market value, not what changes it. Market value is
Transfermarkt's estimate, not a sale price or transfer fee.

## Summary of findings

Details, evidence and limitations for each are in [`FINDINGS.md`](FINDINGS.md).

1. Value is extremely right-skewed, so a log scale is used throughout. Age follows a hump (plateau about 22-28, decline after 30), so one linear coefficient (Spearman -0.03) is misleading.
2. League is the largest single grouping: about 35% of log-value variance lies between leagues (vs 6.5% age group, 1% position). League medians range from €13M (Premier League) to €0.35M (Ukraine).
3. Playing time has the strongest simple numeric association (Spearman 0.51), and it works in both directions.
4. Goal involvement is more associated with value for attackers (0.45) than midfielders (0.26) or defenders (0.19).
5. Position and sub-position separate values little; goalkeepers are lowest.
6. K-means on attackers gives four readable but weakly separated groups (silhouette about 0.21 for every k). Rule-based segments are shown separately and labelled as segments.
7. Among attackers with at least 450 minutes, young (under 24) high-output attackers have the highest median value (€10M), ahead of prime-age (€8M) and experienced (€3.5M) high-output attackers.

## Audience and stakeholders

- **Football fans, journalists and students** who read Transfermarkt values and want
  to know what they track.
- **Analysts and recruitment staff** who use market values as a reference point.
- **Players and agents**, who are affected when estimated values shape negotiations
  and public perception.

Possible consequence: treating an estimate as a price, or an association as a cause,
could mislead decisions about players. The project therefore reports associations
only and states what it cannot show.

## Data

[Transfermarkt datasets](https://github.com/dcaribou/transfermarkt-datasets)
(David Caribou; public, CC0, scraped from Transfermarkt). We do not scrape
Transfermarkt ourselves. Raw files are not committed; see `data/raw/README.md`
for the download commands (six gzipped CSVs, about 65 MB).

## Analytical dataset

`data/processed/player_season.csv`: **32,046 rows, 26 columns**, one row per
player-season, 2020/21-2024/25, 14 August-May domestic top-flight leagues.
Every scope and cleaning decision is logged in [`DATA_PLAN.md`](DATA_PLAN.md).

- Appearances are joined to games and summed per player-season. When a player
  changed clubs, the row is labelled by the club with most minutes.
- Market value = latest Transfermarkt valuation on or before July 31 after the
  season, at most 365 days old.
- Per-90 statistics are only analysed for players with at least 450 minutes
  (23,328 rows, 72.8%, flagged by `analysis_minutes_eligible`); other rows are kept.
- 920 of 32,966 rows (2.8%) were excluded (missing position/date of birth, no or
  stale valuation): `data/processed/exclusion_summary.csv`.

Variables: `player_id`, `player_name`, `season`, `age`, `age_group`, `position`,
`sub_position`, `club`, `competition_id`, `competition`, `country`,
`appearances`, `total_minutes`, `minutes_per_appearance`, `goals`, `assists`,
`goal_contributions`, `goals_per_90`, `assists_per_90`,
`goal_contributions_per_90`, `analysis_minutes_eligible`,
`market_value_in_eur`, `market_value_millions`, `log_market_value` (log10),
`valuation_date`, `valuation_age_days`.

## Methods

- Descriptive statistics, medians on a log value axis, box plots, binned medians.
- Spearman rank correlations (robust to skew) and eta squared (share of log-value
  variance between groups) as association summaries. These are not
  "percentage contributions" and are not additive.
- Position-aware: goals/assists per 90 are interpreted for attackers and, more
  cautiously, midfielders; never as a quality measure for defenders or goalkeepers.
- **Segmentation (exploratory):** K-means (k = 4) on attackers with at least 450
  minutes using age, total minutes, goals/90 and assists/90 (per-90 rates capped
  at the 99th percentile, standardised; market value not used). Silhouette is
  about 0.21 for k = 2 to 6, so structure is weak and k = 4 was chosen for
  interpretability. Separately, **rule-based segments** (high scorers, creative,
  young, prime age, experienced) are defined with explicit cut-offs; they are
  segments, not clusters. Midfielders, defenders and goalkeepers are not
  segmented (no suitable variables). See `notebooks/05_player_segmentation.ipynb`.

## Figures

`figures/final/` holds the report/presentation figures (see
`figures/final/README.md` for the suggested presentation set). `figures/*.png`
are the earlier exploratory versions.

## Streamlit app

```bash
uv venv && uv pip install -r requirements.txt
uv run streamlit run app.py
```

A single scrolling data story for readers new to the project: research
question, what market value means, how the dataset was built, each finding
with its caveat, K-means clusters and rule-based segments, what the analysis
cannot conclude, limitations, and an expandable technical section. The app reads
`data/processed/player_season.csv` directly; no notebooks or raw data needed.

## Repository structure

```
.
├── README.md
├── FINDINGS.md            # six findings: evidence, interpretation, limitation
├── DATA_PLAN.md           # data inspection notes, joins, decisions, variables
├── MEETING2.md            # second instructor meeting notes
├── FINAL_CHECKLIST.md     # project requirements audit
├── app.py                 # Streamlit data story
├── requirements.txt       # pinned versions (Python 3.12)
├── src/
│   ├── data.py            # loading, constants, filtering
│   ├── plots.py           # figure functions shared by notebooks and app
│   ├── segments.py        # K-means clusters and rule-based segments (attackers)
│   └── ui.py              # CSS and small HTML helpers for the app
├── notebooks/
│   ├── 01_data_inspection.ipynb
│   ├── 02_build_player_season.ipynb
│   ├── 03_initial_eda.ipynb      # exploratory version
│   ├── 04_final_eda.ipynb
│   └── 05_player_segmentation.ipynb
├── data/
│   ├── raw/               # downloaded source files (gitignored)
│   └── processed/         # player_season.csv, exclusion_summary.csv
├── figures/               # exploratory figures
│   └── final/             # final figures
└── report/
    └── REPORT_OUTLINE.md
```

## Reproduction

```bash
uv venv --python 3.12
uv pip install -r requirements.txt
# download raw data as described in data/raw/README.md, then run in order:
for n in 02_build_player_season 03_initial_eda 04_final_eda 05_player_segmentation; do
  uv run jupyter nbconvert --to notebook --execute --inplace notebooks/$n.ipynb
done
uv run streamlit run app.py
```

Notebook 01 only inspects the raw tables. Notebook 02 rebuilds the processed
CSV; 04 and 05 regenerate `figures/final/`. The processed CSV is committed, so
notebooks 03-05 and the app run without the raw data.

## Limitations

- Transfermarkt values are estimates with their own biases and update timing.
- Associations only; age, playing time, output, club and league overlap.
- League is a large confounder; club strength is not in the data.
- No defensive, goalkeeping, injury or contract data; attacking statistics are
  informative mainly for attackers.
- The 450-minute, July 31 and 365-day rules are practical analytical choices.
- Scope: 14 August-May leagues only. Eight calendar-year leagues are excluded
  for a consistent valuation cut-off, and nine further leagues have no
  match-level data in the source.
- Russian and Ukrainian leagues are kept, but 2022+ is affected by the war.
- The same player appears in several seasons, so rows are not independent.

## References

- Caribou, D. *transfermarkt-datasets*. https://github.com/dcaribou/transfermarkt-datasets (data scraped from Transfermarkt, https://www.transfermarkt.com).
- Repository: https://github.com/niloy-saha-123/DATA400-football-player-market-value-analysis
