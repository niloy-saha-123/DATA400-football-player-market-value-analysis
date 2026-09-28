# Data Plan

Working notes from inspecting the [transfermarkt-datasets](https://github.com/dcaribou/transfermarkt-datasets)
project (dbt schema docs + direct inspection of the actual CSVs, checked
2026-09-23). Update this file as decisions get made or assumptions get
tested — it's the log of "why we did it this way," not a static spec.

## Relevant tables

Of the 12 tables in the dataset, six are relevant to this project:

| Table | Rows (actual) | Role |
|---|---|---|
| `players` | 50,149 | player attributes (position, DOB, etc.) |
| `appearances` | ~1.4–2M (per dbt test bounds) | match-level stats, needs aggregation to season |
| `player_valuations` | 656,301 | dated market-value history — the target variable source |
| `games` | 88,958 | provides `season` and `competition_id` for each match |
| `clubs` | ~650–850 | club names, joined for readability |
| `competitions` | 65 | league/competition names and `type` |

Not downloaded (not needed yet): `game_events`, `game_lineups`, `transfers`,
`club_games`, `countries`, `national_teams`.

## Relevant columns (confirmed from dbt schema + direct inspection)

**`players`**: `player_id`, `name`, `date_of_birth`, `position`,
`sub_position`, `foot`, `height_in_cm`, `current_club_id`,
`current_club_domestic_competition_id`, `market_value_in_eur`,
`highest_market_value_in_eur`, `last_season`.

> `market_value_in_eur` / `highest_market_value_in_eur` on `players` are the
> **player's current snapshot value**, not historical — confirmed from the
> dbt model (`row_number() ... order by date desc`, `rn = 1`). **Do not use
> these for the player-season target.** Use `player_valuations` instead.

**`appearances`**: `appearance_id`, `game_id`, `player_id`, `player_club_id`,
`date`, `competition_id`, `goals`, `assists`, `minutes_played`,
`yellow_cards`, `red_cards`.

> No `season` column. Must join to `games` on `game_id` to get `season`.

**`player_valuations`**: `player_id`, `date`, `market_value_in_eur`,
`current_club_id`, `current_club_name`, `player_club_domestic_competition_id`.
Dated valuation snapshots, `date` range 2000-01-20 to 2026-06-12 in the data
actually downloaded.

**`games`**: `game_id`, `competition_id`, `competition_type`, `season`,
`date`, `home_club_id`/`away_club_id`. `season` is a direct integer column
(e.g. `2023` = the 2023/24 season) — no need to derive it from date.

**`clubs`**: `club_id`, `name`, `domestic_competition_id`.

**`competitions`**: `competition_id`, `name`, `type`
(`domestic_league` / `domestic_cup` / `international_cup` /
`national_team_competition` / `other`), `country_name`.

## Player-season construction (as built in `02_build_player_season.ipynb`)

1. `appearances` ⋈ `games` on `game_id` → attaches `season` and
   `competition_id`/`competition_type` to each appearance.
2. Filter to the 14 Aug–May domestic leagues and seasons 2020–2024 (see
   competition scope and season range decisions below).
3. Group by (`player_id`, `season`) → `appearances` (count of rows),
   `total_minutes` (sum), `goals` (sum), `assists` (sum) across all
   clubs/competitions the player played in that season. Derive
   `goals_per_90`, `assists_per_90`, `goal_contributions_per_90`.
4. Determine each player-season's primary club/competition (most minutes).
5. Join `players` on `player_id` for `position`, `sub_position`,
   `date_of_birth` → derive `age` as of the season's start (Aug 1).
6. Join a season-level market value from `player_valuations` using the
   July-31-of-`season+1` cutoff rule; record `valuation_age_days`.
7. Apply exclusions sequentially (missing position, missing DOB, no
   valuation, valuation older than 365 days, zero minutes) and save the
   counts to `data/processed/exclusion_summary.csv`.
8. Flag `analysis_minutes_eligible` (`total_minutes >= 450`) for per-90
   analysis. Low-minute rows are kept, not dropped.

## Decisions and assumptions (log) — FINALIZED for the player-season build

- **Season definition**: use `games.season` directly (already an integer
  season-start year) rather than deriving one from raw dates.

- **Competition scope (revised)**: domestic leagues only, further restricted
  to the **14 Aug–May "European-calendar" top-flight leagues** that show up
  consistently across all candidate seasons: LaLiga (Spain), Serie A
  (Italy), Premier League (England), Süper Lig (Türkiye), Liga Portugal,
  Bundesliga (Germany), Eredivisie (Netherlands), Ligue 1 (France), Ukraine
  Premier Liga, Russia Premier Liga, Jupiler Pro League (Belgium), Scottish
  Premiership, Super League Greece, Superliga Denmark.
  **Identity caveat (fixed):** the source `competitions.name` is not unique
  — Russia (`RU1`) and Ukraine (`UKR1`) are both `premier-liga` (and
  `bundesliga` / `superliga` also collide with out-of-scope Austria/Romania).
  The processed data keeps the unique `competition_id` and an explicit
  readable `competition` label (e.g. "Russian Premier League"). Russia and
  Ukraine are both kept; the 2022+ war context (disrupted Ukrainian league,
  Russian clubs cut off from European competition) is a caveat, not an
  exclusion.
  Excluded from this scope:
  - Domestic cups, international cups, and national-team competitions (as
    before — avoids double-counting minutes across very different
    competition strengths).
  - The 8 "calendar-year" domestic leagues (Argentina, Brazil, Japan,
    Mexico, MLS, Norway, South Korea, Sweden) — their season runs roughly
    within one calendar year instead of Aug–May, verified by checking each
    league's typical season-start month (see `01_data_inspection.ipynb`).
    Mixing both calendar conventions would break a single, consistent
    season-end valuation cutoff rule. This is a scope simplification for
    project manageability, not a data-quality exclusion — these leagues can
    be added back later with their own cutoff rule if needed.
  - **9 additional leagues classified as Aug–May by their `games` schedule
    but with zero rows in `appearances`**: Austria, Australia, Switzerland,
    Croatia, Poland, Romania, Saudi Arabia, Serbia, Czech Republic. This is
    a genuine gap in the source dataset's match-level scraping for those
    leagues (confirmed in `02_build_player_season.ipynb`), not a filtering
    choice — worth mentioning to the instructor as a limitation of the
    underlying data, not something this project caused.

- **Season range (revised): 2020/21–2024/25** (`season` values 2020–2024,
  5 seasons). Verified via `01_data_inspection.ipynb`: every candidate
  season from 2017–2025 has essentially the same coverage quality (5,800–
  6,800 players/season, all 14 leagues present, position/DOB >99.8%
  complete, 96%+ valuation coverage), so season *quality* did not drive the
  range choice. 2013–2019 was dropped for project-scope reasons: a 5-season
  recent window is enough player-seasons (~30k estimated) for the analysis
  without carrying an unnecessarily long history for a 7-week mini-project.
  2025/26 season data is complete for these leagues (season ends ~May 2026,
  well inside the dataset's July 2026 freeze) but was left out of the
  primary window to keep it to five most-recent, clearly-finished seasons.

- **Valuation → season mapping (decided)**: for each player-season, take
  the **latest `player_valuations` record on or before July 31 of
  `season + 1`** (e.g. for the 2023 season, cutoff = 2024-07-31).
  Reasoning, checked directly against the data:
  - Valuation updates are not continuous — Transfermarkt updates in a few
    rounds a year. In this dataset, valuation dates cluster heavily in
    **June** (post-season update) and **December** (mid-season update);
    median is ~2 valuations/player/year.
  - The Aug–May leagues in scope finish their seasons April–June, so the
    June update round is effectively "the" end-of-season valuation for most
    players.
  - A July 31 cutoff reliably captures that June update while staying
    ahead of the next season's transfer-window activity (valuation volume
    picks up again in August–September) — this avoids pulling in a value
    that already reflects a move or run of form from the *next* season.
  - Not used: nearest-to-season-start (would miss the performance just
    played), or a window average (adds complexity without a clear benefit
    for this project's scope).

- **Maximum valuation staleness (decided): 365 days.** The matched
  valuation must be no more than 365 days before the cutoff
  (`valuation_age_days <= 365`). Evidence (`02_build_player_season.ipynb`
  §6b): median lag 55 days, 95th percentile 76 days; the bulk of matches
  are 30–120 days old, then a thin tail (only 39 rows at 270–365 days) and
  416 rows (1.3%) older than 365 days, up to 2,472 days (6.8 years). Those
  416 are excluded and counted (384 of them in season 2024; cause not
  investigated). 365 is a practical cap, not a uniquely correct value.

- **Per-90 eligibility (decided): `total_minutes >= 450`.** Rows below the
  threshold are **kept** in the dataset; `goals_per_90`, `assists_per_90` and
  `goal_contributions_per_90` are only used for analysis when
  `analysis_minutes_eligible` is true. Evidence: before filtering, per-90
  values reach 90 (a goal in 1 minute); at 450 minutes the maximum goals/90
  is 1.50 and the attacker goals/90 spread and 99th percentile have mostly
  flattened, while ~73% of rows remain. 450 (five full matches) is a
  practical stability rule, not a universally correct threshold. Plots and
  correlations that use age, position, minutes, or market value alone use all
  rows.

- **League effect (open, not resolved).** Median market value differs by an
  order of magnitude between leagues (shown in `03_initial_eda.ipynb`).
  Pooled relationships will partly reflect league. No leagues have been
  removed. Options to discuss with the instructor: keep all and compare/stratify by
  league, or restrict to a smaller set of leagues.

- **Multi-club players within a season (decided)**: 6.4% of player-seasons
  in the chosen scope involve more than one club (3.3% involve more than
  one league/country) — a minority, but not negligible. Rule: **keep one
  row per player-season**. `total_minutes`, `goals`, `assists` are summed
  across all clubs/competitions played that season; `club` and
  `competition` are labeled using whichever club/competition the player
  logged the most minutes for that season (their "primary" club). This is
  the simplest rule that preserves the intended grain — it does not lose
  any performance data, only simplifies the descriptive club/league label
  for players who moved.

- **Age**: `date_of_birth` is missing for only 0.10% of players — reliable
  enough to use directly. Computed relative to that season's approximate
  start (August 1 of the season year), not the current date.

## Variables NOT to use until validated

- `players.market_value_in_eur` / `highest_market_value_in_eur` — current
  snapshot, wrong grain (see above).
- `players.current_club_id` / `current_club_name` /
  `current_club_domestic_competition_id` — reflect the player's *current*
  club, not their club during a given past season. Season-accurate club
  should come from `appearances.player_club_id` instead.
- Previous/lagged market value as the main explanatory variable — per the
  project brief, this would likely dominate and flatten the analysis. May be
  used later as one comparison point, not the primary predictor.
- `transfers` table / `transfer_fee` — not loaded yet; secondary at best.
- `agent_name`, `contract_expiration_date` — available but not clearly tied
  to the research question; leave out unless a specific reason comes up.
- Injury data — no dataset identified yet. Optional per the proposal; only
  add if something reliable and low-effort turns up.

## Data-quality notes

- `players.position` — 5 categories (`Attack`, `Defender`, `Midfield`,
  `Goalkeeper`, `Missing`); `Missing` is 586 players (~1.2%), excluded.
- `players.sub_position` — 13 categories, null only where `position` is also
  `Missing`.
- `players.date_of_birth` — 0.10% missing.
- `players.market_value_in_eur` (current snapshot) — 17.2% missing (inactive/
  retired/unvalued players); irrelevant once we switch to
  `player_valuations`, but a reminder that not every player has a value.
- `appearances` actual row count (downloaded file): 1,894,350; all key
  columns (`appearance_id`, `game_id`) unique/non-null, confirmed in
  `01_data_inspection.ipynb`.
- `player_valuations` unique on (`player_id`, `date`) — confirmed.
- Zero-minutes appearance rows: 3 out of 1,894,350 — negligible.
- Multi-club player-seasons (2020–2024, 14-league scope): 6.4% of
  player-seasons involve >1 club; 3.3% involve >1 league/country.

See §7 (Exclusions) of `02_build_player_season.ipynb` and
`data/processed/exclusion_summary.csv` for the exact row counts dropped at
each cleaning step.

## Current build results

`data/processed/player_season.csv` (5.6 MB, 21 columns) and
`data/processed/exclusion_summary.csv`, built by `02_build_player_season.ipynb`:

- **32,046 rows** (one per player-season), after exclusions.
- Started at 32,966 player-seasons; dropped 920, counted sequentially:
  9 missing position, 5 missing date of birth, 490 no valuation by the
  cutoff, 416 valuation older than 365 days, 0 zero-minute rows, 0 duplicate
  keys.
- Rows per season: 6,671 (2020), 5,860 (2021), 6,700 (2022), 6,679 (2023),
  6,136 (2024).
- Position counts: Defender 10,942; Midfield 9,428; Attack 9,116;
  Goalkeeper 2,560.
- Per-90 eligible (`total_minutes >= 450`): 23,328 rows (72.8%).
- `market_value_in_eur`: median €1.3M, mean €5.4M, range €20K–€200M
  (heavily right-skewed; log scale is used in the plots).
- 14 leagues with unique `competition_id` and unambiguous `competition`
  labels. Validity checks (no negative goals/assists/minutes, market value
  > 0, valuation age within 0–365 days, exactly 4 positions, no nulls) are
  asserted in the notebook.

## Open questions for the instructor

1. **League confound.** Market values differ hugely by league. Keep all 14
   leagues and stratify/control for league, or narrow to major leagues?
2. **Valuation rule.** Is "latest valuation on or before July 31, no older
   than 365 days" a reasonable season-end mapping?
3. **Depth.** Does the current position-aware EDA and visualization approach
   provide enough depth, or is there another comparison or visualization that
   would strengthen the analysis?

(The multi-club "primary club by minutes" rule and the 14-league Aug–May
scope are decided; they are documented above, not open.)
