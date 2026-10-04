"""Attacker groupings: K-means clusters (profile variables only) and rule-based segments."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

FEATURES = ["age", "total_minutes", "goals_per_90", "assists_per_90"]
SEED = 0
K = 4


def eligible_attackers(df):
    return df[(df["position"] == "Attack") & df["analysis_minutes_eligible"]].copy()


def scale_features(a, features=FEATURES):
    """Winsorise per-90 rates at the 99th percentile, then standardise. Market value is never used."""
    X = a[features].copy()
    for c in [f for f in features if f.endswith("_per_90")]:
        X[c] = X[c].clip(upper=X[c].quantile(0.99))
    return StandardScaler().fit_transform(X)


def kmeans_fit(Z, k=K, seed=SEED):
    return KMeans(k, n_init=20, random_state=seed).fit(Z)


def name_clusters(a, labels):
    """Descriptive names from each cluster's median profile (data-driven, deterministic)."""
    med = a.groupby(labels)[FEATURES].median()
    names, left = {}, set(med.index)
    for key, name in [("assists_per_90", "Creative attackers"), ("total_minutes", "Regular high-minute starters"),
                      ("age", "Older, fewer minutes")]:
        c = med.loc[list(left), key].idxmax()
        names[c] = name
        left.discard(c)
    for c in left:
        names[c] = "Younger, lower output"
    return names


def segment_thresholds(a):
    return {"goals_q3": a["goals_per_90"].quantile(0.75), "assists_q3": a["assists_per_90"].quantile(0.75)}


def domain_segments(a):
    """Rule order matters: high scorer, then creative, then everyone else by age."""
    t = segment_thresholds(a)
    seg = np.select(
        [a["goals_per_90"] >= t["goals_q3"], a["assists_per_90"] >= t["assists_q3"],
         a["age"] < 24, a["age"] < 29],
        ["High scorers", "Creative attackers", "Young (under 24)", "Prime age (24-28)"],
        default="Experienced (29+)")
    return pd.Series(seg, index=a.index)


def attacker_groups(df):
    """Eligible attackers with `kmeans_group` and `domain_segment` columns (+ PCA coords for plotting)."""
    from sklearn.decomposition import PCA
    a = eligible_attackers(df)
    Z = scale_features(a)
    km = kmeans_fit(Z)
    names = name_clusters(a, km.labels_)
    a["kmeans_group"] = pd.Series(km.labels_, index=a.index).map(names)
    a["domain_segment"] = domain_segments(a)
    pc = PCA(2, random_state=SEED).fit_transform(Z)
    a["pc1"], a["pc2"] = pc[:, 0], pc[:, 1]
    return a


AGE_BANDS = ["Young (under 24)", "Prime (24-28)", "Experienced (29+)"]


def age_output_groups(a):
    """Age band x output for eligible attackers. High output = top quartile of goals + assists per 90."""
    q = a["goal_contributions_per_90"].quantile(0.75)
    band = pd.Series(np.select([a["age"] < 24, a["age"] < 29], AGE_BANDS[:2], AGE_BANDS[2]), index=a.index)
    out = np.where(a["goal_contributions_per_90"] >= q, "High output", "Lower output")
    return a.assign(age_band=band, output=out), q
