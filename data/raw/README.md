# data/raw

Raw dataset files go here. This folder is gitignored except for this file —
raw data is not committed to the repository (see project README for why).

## What to download

We use a subset of the tables from the
[transfermarkt-datasets](https://github.com/dcaribou/transfermarkt-datasets)
project (gzipped CSVs, hosted publicly, no auth required):

```bash
cd data/raw
for f in players appearances player_valuations games clubs competitions; do
  curl -LO "https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/${f}.csv.gz"
done
```

This downloads ~65 MB total (`appearances.csv.gz` is the largest at ~45 MB).
`game_events`, `game_lineups`, `transfers`, `countries`, `national_teams`, and
`club_games` are not downloaded — they aren't needed for the current
player-season analysis. Add them later only if a specific question requires
them.

Load any file directly with pandas, e.g. `pd.read_csv("data/raw/players.csv.gz")`.

See `DATA_PLAN.md` at the project root for what's in each table and how they
join.
