# Final checklist

Checked against the *DATA 400 Individual Mini-Project Guide* (Fall 2026),
"Analysis and Communication Expectations" and "Evaluation Priorities", on
2026-10-04. Detailed grading rubrics had not been posted in the files available.

| Requirement (from the guide) | Status | Evidence / note |
|---|---|---|
| One clear, focused research question | DONE | README; unchanged since the proposal |
| Disciplinary connection, audience and stakeholders | DONE | README "Audience and stakeholders"; slide 2 |
| Obtainable, documented data source | DONE | transfermarkt-datasets (CC0); `data/raw/README.md` download commands |
| Variables, cleaning decisions, missing data explained | DONE | `DATA_PLAN.md`, `exclusion_summary.csv`, notebook 02 |
| Exploratory analysis and visualization | DONE | notebooks 03 (exploratory), 04 (final), 05 (segmentation); 16 figures in `figures/final/` |
| Appropriate comparisons | DONE | by position, league, age group; within-league checks; age x output |
| Description vs prediction vs causation distinguished | DONE | "associated" wording throughout; no causal claims; slide 10 footer, slide 11 |
| Uncertainty, assumptions, limitations, alternative explanations | DONE | `FINDINGS.md` limitation per finding; README; slide 11 |
| Possible consequences of the work | DONE | README "Audience and stakeholders" (risk of treating estimates as prices) |
| Reproducible, readable code | DONE | notebooks 01-05 re-run without errors in a fresh clone and fresh venv (2026-10-04): identical CSV and figures |
| Useful README with setup and reproduction steps | DONE | README |
| Repository structure (data, notebooks, figures, report, presentation) | DONE | all folders present |
| Presentation materials | DONE | `presentation/` (.pptx, .pdf, speaker notes, claim verification) |
| External sources cited | DONE | README references (dataset, Transfermarkt) |
| Written report | NEEDS ATTENTION | outline with verified statistics only (`report/REPORT_OUTLINE.md`); prose due Oct 15 |
| Stale-valuation cause (384 of 416 exclusions in season 2024) | NEEDS ATTENTION | not investigated; disclosed as a limitation |
| League/club adjustment | NOTE | leagues compared and within-league checks done; no model adjusts for league or club (scope choice) |
