# What Factors Are Most Associated with Football Player Market Value?

DATA 400 — Data Analytics Capstone, Dickinson College.

## Research question

Which player characteristics and performance statistics are most strongly
associated with a football (soccer) player's market value?

## Motivation

Transfermarkt market values are widely cited in football media and analysis,
but it's not always clear which factors actually track with them. This
project examines historical player data to see which characteristics — age,
position, playing time, goal involvement, league — are most strongly
associated with market value, and whether that relationship differs by
position.

This is an **associational**, not causal, analysis. We describe what tends to
be higher or lower alongside market value, not what causes it to change.

## Data source

[David Caribou's transfermarkt-datasets](https://github.com/dcaribou/transfermarkt-datasets) —
a public, cleaned, dbt-built dataset scraped from Transfermarkt, distributed
as CSV/DuckDB files. We do not scrape Transfermarkt ourselves.

Market value in this dataset is Transfermarkt's own estimate, not a verified
sale price and not necessarily the fee a club would actually pay.

## Unit of observation

One row per player-season: **32,046 player-seasons**, seasons 2020/21
through 2024/25, across 14 top-flight European domestic leagues. Built by
aggregating match-level appearances and joining a season-end market value
(no older than 365 days at the cutoff) — see `DATA_PLAN.md` for the exact construction and every scope/cleaning
decision.

## Variables

`player_id`, `player_name`, `season`, `age`, `position`, `sub_position`,
`club`, `competition_id`, `competition`, `country`, `appearances`,
`total_minutes`, `goals`, `assists`, `goals_per_90`, `assists_per_90`,
`goal_contributions_per_90`, `analysis_minutes_eligible`,
`market_value_in_eur`, `valuation_date`, `valuation_age_days`.

`club`/`competition` reflect a player's primary (most-minutes) club that
season — see `DATA_PLAN.md` for how multi-club seasons are handled.
`competition_id` is the unique league key (the source's own league `name`
is not unique: Russia and Ukraine are both `premier-liga`).

Per-90 columns are only meaningful when `analysis_minutes_eligible` is true
(`total_minutes >= 450`). Low-minute rows are kept, not deleted.

## Approach

- Clean and join the relevant tables, aggregate appearances to player-season.
- Exploratory data analysis: distributions, market value vs. age/position/
  performance stats, a correlation view for sensible numeric variables.
- **Position-aware analysis**: forwards, midfielders, defenders, and
  goalkeepers are not judged by the same stats. Comparisons are done within
  position (and sub-position, where the data supports it) rather than pooling
  all players together.
- A simple statistical method (e.g. a regression) may be added later if it
  helps answer the research question. Machine learning is not assumed to be
  necessary and won't be added without a clear reason.
- Optional: if injury data can be found that is reliable and easy to
  integrate, it may be added as a secondary variable. Not required, and not
  a second dataset until the core analysis is done.

## Limitations

- Market value is Transfermarkt's estimate, subject to its own biases and
  update lag — not ground truth.
- Analysis is restricted to 14 Aug–May European domestic leagues; 8
  calendar-year leagues (Brazil, MLS, Japan, etc.) are excluded for
  consistency, and 9 further leagues have no match-level data in the
  source dataset at all (see `DATA_PLAN.md`).
- Player valuations are recorded at irregular dates, not per season — "the"
  value for a season is the latest valuation on or before July 31 following
  that season, a documented assumption, not a given fact of the data.
- Players with no valuation on record before that cutoff (mostly fringe
  squad players) are dropped rather than imputed, as are valuations more
  than 365 days old at the cutoff — 920 of 32,966 rows (2.8%) in total, see
  `data/processed/exclusion_summary.csv`.
- Market values differ enormously between leagues, so pooled relationships
  partly reflect league. Not yet resolved (see `DATA_PLAN.md`).
- Russian and Ukrainian leagues are kept, but 2022+ seasons are affected by
  the war.
- Playing time, goals, and assists are influenced by team and tactical
  context that isn't captured here.

## Project structure

```
.
├── README.md
├── DATA_PLAN.md          # data inspection notes, joins, open questions
├── .gitignore
├── requirements.txt
├── data/
│   ├── raw/               # downloaded source files (gitignored, see below)
│   └── processed/         # player_season.csv, tracked in git
├── figures/               # saved EDA plots (.png)
└── notebooks/
    ├── 01_data_inspection.ipynb
    ├── 02_build_player_season.ipynb
    └── 03_initial_eda.ipynb
```

`src/`, `report/`, and `presentation/` will be added when there's something
to put in them, rather than as empty placeholders.

## Setup

```bash
uv venv
uv pip install -r requirements.txt
uv run jupyter lab
```

(Any standard Python 3.11+ environment with the packages in
`requirements.txt` works — `uv` is just what this project uses.)

## Data acquisition

Raw data is not committed to this repository (too large for GitHub, and
easy to regenerate). See `data/raw/README.md` for the exact download
commands. In short: six gzipped CSVs (`players`, `appearances`,
`player_valuations`, `games`, `clubs`, `competitions`) totaling ~65 MB,
downloaded from the dataset's public hosting.

## Reproducibility

- Raw data acquisition is documented in `data/raw/README.md`; anyone can
  re-download the exact same public files.
- Cleaning and aggregation decisions (season definition, which competitions
  are included, how a valuation date maps to a season, etc.) are logged in
  `DATA_PLAN.md` as they're made, not left implicit in notebook code.
- The processed player-season table, once built, is committed under
  `data/processed/` so the analysis can be re-run without re-downloading
  raw data.

## Current status

Data cleaned, joined, and aggregated to player-season
(`data/processed/player_season.csv`, 32,046 rows). Quality rules (valuation
staleness cap, per-90 minutes eligibility, unique league identity) are
applied and documented. EDA is in `notebooks/03_initial_eda.ipynb`. No
statistical modeling yet.

## Timeline

- **Sept 18–24**: inspect and clean data, combine required tables, aggregate
  to player-season, begin EDA.
- **Sept 25–Oct 1**: build/refine visualizations, simple supporting stats if
  useful, both instructor meetings, revise on feedback.
- **Oct 2–8**: finalize analysis, interpret findings, prepare presentation.
- **Oct 9–14**: finish written report, clean up repo, verify reproducibility,
  finish presentation materials.
- **Oct 15**: final submission.
