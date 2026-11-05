"""Library audit: MAPIE 1.6.0 empty-set policy for LAC and APS.

Five seeds, mean and SD. Saves results/mapie_empty.json.
"""
import json
import os
from collections import defaultdict

import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from mapie.classification import SplitConformalClassifier
import mapie

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "results", "mapie_empty.json")

rows = []
for seed in range(5):
    X, y = make_classification(n_samples=8000, n_features=20, n_classes=5,
                               n_informative=12, class_sep=0.8, random_state=seed)
    Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, test_size=0.5, stratify=y, random_state=seed)
    Xcal, Xte, ycal, yte = train_test_split(Xtmp, ytmp, test_size=0.5, stratify=ytmp, random_state=seed)
    clf = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
    for score in ["lac", "aps"]:
        for inc in ([True, False, "randomized"] if score == "aps" else [True]):
            model = SplitConformalClassifier(
                estimator=clf, confidence_level=0.90, conformity_score=score,
                prefit=True, random_state=seed)
            model.conformalize(Xcal, ycal)
            kwargs = {"conformity_score_params": {"include_last_label": inc}} if score == "aps" else {}
            _, sets = model.predict_set(Xte, **kwargs)
            s = sets[:, :, 0]
            sizes = s.sum(axis=1)
            rows.append({
                "seed": seed, "score": score, "include_last_label": inc,
                "coverage": float(s[np.arange(len(yte)), yte].mean()),
                "empty_rate": float((sizes == 0).mean()),
                "mean_size": float(sizes.mean()),
                "accuracy": float(clf.score(Xte, yte)),
                "n_test": int(len(yte)),
            })
    print("seed", seed, "done", flush=True)

groups = defaultdict(list)
for r in rows:
    groups[(r["score"], str(r["include_last_label"]))].append(r)
summary = []
for (score, inc), rs in groups.items():
    summary.append({
        "score": score, "include_last_label": inc,
        "coverage_mean": float(np.mean([r["coverage"] for r in rs])),
        "coverage_sd": float(np.std([r["coverage"] for r in rs], ddof=1)),
        "empty_rate_mean": float(np.mean([r["empty_rate"] for r in rs])),
        "size_mean": float(np.mean([r["mean_size"] for r in rs])),
        "accuracy_mean": float(np.mean([r["accuracy"] for r in rs])),
    })
    print(score, inc, "cov", round(summary[-1]["coverage_mean"], 4),
          "sd", round(summary[-1]["coverage_sd"], 4),
          "empty", round(summary[-1]["empty_rate_mean"], 4),
          "size", round(summary[-1]["size_mean"], 3), flush=True)

payload = {
    "library": "mapie", "version": mapie.__version__, "alpha": 0.10,
    "dataset": "make_classification 5 classes, 8000 samples, 5 seeds",
    "rows": rows, "summary": summary,
    "source": {
        "predict_set": "mapie/classification.py:238-283",
        "aps_doc": "mapie/conformity_scores/sets/aps.py:355-358",
        "lac_rule": "mapie/conformity_scores/sets/lac.py:205-207",
    },
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1)
print("saved", OUT)
