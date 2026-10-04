"""Slide-sized copies of the final figures: same src/plots.py functions, same data, larger text.

Run from the repo root: python presentation/make_figures.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import plots
from src.data import load_player_season
from src.segments import FEATURES, age_output_groups, attacker_groups, eligible_attackers

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
                     "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10})


def save(fig, name, w, h, drop_title=True, short_labels=False):
    """Slide headlines carry the message, so axis titles are dropped unless asked to keep them."""
    fig.set_size_inches(w, h)
    for ax in fig.axes:
        if drop_title:
            ax.set_title("")
        if short_labels:  # "League\nmedian €4M, n=2,715" -> "League  €4M"
            ax.set_yticklabels([t.get_text().split("\n")[0] + "   " + t.get_text().split("median ")[1].split(",")[0]
                                for t in ax.get_yticklabels()], fontsize=9.5)
    if drop_title and fig._suptitle is not None:
        fig._suptitle.set_text("")
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=220)
    plt.close(fig)


df = load_player_season()
att = eligible_attackers(df)
g = attacker_groups(df)
ao, q = age_output_groups(att)

save(plots.fig_value_by_age(df), "age.png", 6.3, 4.1)
save(plots.fig_perf_vs_value(df, "Attack", ["goals_per_90"]), "attack_goals.png", 5.3, 4.1, drop_title=False)
save(plots.fig_value_by_league(df), "league.png", 5.6, 4.6, short_labels=True)
save(plots.fig_age_output(ao, q), "age_output.png", 8.2, 3.9)
save(plots.fig_group_heatmap(g, "kmeans_group", FEATURES), "kmeans_profiles.png", 6.8, 3.3)
save(plots.fig_value_vs_minutes(df), "minutes.png", 7.6, 3.8)

print("wrote", sorted(p.name for p in OUT.glob("*.png")))
