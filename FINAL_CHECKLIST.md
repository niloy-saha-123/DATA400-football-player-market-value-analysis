# Final checklist

Audited against the project brief and instructor feedback as I have them. I have
not seen the official DATA 400 rubric, so check this list against it.

| Requirement | Status | Evidence / note |
|---|---|---|
| One clear research question | DONE | README, unchanged from proposal |
| Credible, cited data source | DONE | transfermarkt-datasets (CC0); README references |
| Reproducible data preparation | DONE | `02_build_player_season.ipynb` rebuilds the CSV; re-run in a fresh clone and fresh venv gave an identical CSV and identical figures |
| Documented cleaning rules and exclusions | DONE | `DATA_PLAN.md`, `exclusion_summary.csv` |
| Dataset validated | DONE | asserts in notebook 02 §9 |
| EDA | DONE | notebooks 03 (exploratory) and 04 (final) |
| Informative visualization | DONE | 15 figures in `figures/final/`, 7 suggested for slides |
| Interpretation of results | DONE | `FINDINGS.md` (6 findings with evidence and limits) |
| Limitations stated | DONE | README, FINDINGS, notebooks, app methodology page |
| No causal overclaiming | DONE | wording is "associated"; no percentage-contribution chart |
| Instructor suggestion (clustering) addressed | DONE | notebook 05: K-means result reported as weak; rule-based segments labelled as segments |
| Interactive companion | DONE | `app.py`, all 6 pages and empty/extreme filters run without errors in Streamlit's test harness |
| Environment reproducible | DONE | pinned `requirements.txt` (Python 3.12) |
| Repo organised, no raw data or agent files committed | DONE | `.gitignore`; raw data, `.claude/`, `.serena/` ignored |
| Stakeholders / audience stated | NEEDS ATTENTION | one line in `report/REPORT_OUTLINE.md`; write a proper paragraph in the report |
| Presentation slides | NEEDS ATTENTION | not built; figure picks and talking points are ready (`figures/final/README.md`, `MEETING2.md`) |
| Written report | NEEDS ATTENTION | outline with exact statistics only; no prose |
| App checked by eye in a browser | NEEDS ATTENTION | tested programmatically and the server starts; I did not inspect the rendered layout. Open it once before presenting |
| Stale-valuation cause (384 of 416 exclusions are season 2024) | NEEDS ATTENTION | still not investigated; disclosed as a limitation |
| League handling beyond description | NEEDS ATTENTION | leagues are compared and checked within-league, but no model adjusts for league or club; state this as a scope choice |
| Pushed to GitHub | NEEDS ATTENTION | commits are local unless you have pushed; see `git status` |
