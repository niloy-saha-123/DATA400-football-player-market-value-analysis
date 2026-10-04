# Presentation

| File | What it is |
|---|---|
| `DATA400_market_value_presentation.pptx` | Editable slides: 11 core slides, then a backup section (divider + 5 slides). Speaker notes are in each slide's notes. |
| `DATA400_market_value_presentation.pdf` | PDF export of the same deck (exported from PowerPoint). |
| `SPEAKER_NOTES.md` | Talking points for every slide: what to say, number to remember, caution, transition. |
| `CLAIM_VERIFICATION.md` | Every number on the slides, its source notebook and calculation. |
| `make_figures.py` | Re-renders the slide-sized figures in `figures/` from the processed data with the same `src/plots.py` functions as `figures/final/` (only size and text size differ). |
| `figures/` | Slide-sized figures used in the deck. |

Reproduce the figures from the repository root:

```bash
uv run python presentation/make_figures.py
```

Suggested run order for a short slot: slides 1-10, then 11 if time allows.
Backup slides are for questions only.
