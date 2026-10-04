# Presentation

| File | What it is |
|---|---|
| `DATA400_market_value_presentation.pptx` / `.pdf` | Main deck: 11 slides, speaker notes in each slide's notes. The PDF is a PowerPoint export. |
| `DATA400_market_value_backup_slides.pptx` / `.pdf` | Separate backup deck for questions: title + 5 slides (A exclusions, B K-means details, C segment definitions, D league medians, E playing time). |
| `SPEAKER_NOTES.md` | Talking points for every slide: what to say, number to remember, caution, transition. |
| `CLAIM_VERIFICATION.md` | Every number on the slides, its source notebook and calculation. |
| `make_figures.py` | Re-renders the slide-sized figures in `figures/` from the processed data with the same `src/plots.py` functions as `figures/final/` (only size and text size differ). |
| `figures/` | Slide-sized figures used in the deck. |

Reproduce the figures from the repository root:

```bash
uv run python presentation/make_figures.py
```

Present the main deck (slides 1-10, then 11 if time allows). Keep the backup deck
open in a second window for questions.
