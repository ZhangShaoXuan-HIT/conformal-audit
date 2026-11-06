"""Third dataset: covertype (7 classes, 54 features).

Audit B replication on tabular data. 120k stratified subset, logistic regression,
5 seeds, 3 alphas, 3 scores, raw vs forced.
"""
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common as C  # noqa: E402

ALPHAS = [0.05, 0.10, 0.20]
SEEDS = [0, 1, 2, 3, 4]
SCORES = ["naive", "aps_rand", "aps_det"]


def main():
    t0 = time.time()
    X, y = fetch_openml("covertype", version=3, as_frame=False, return_X_y=True)
    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=int) - 1
    X, _, y, _ = train_test_split(X, y, train_size=120000, stratify=y, random_state=0)
    print("subset", X.shape, "classes", np.bincount(y), "load", round(time.time()-t0,1), flush=True)

    rows = []
    for n_train in [6000, 60000]:
        for seed in SEEDS:
            Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=n_train,
                                                    test_size=120000 - n_train,
                                                    stratify=y, random_state=seed)
            Xcal, Xte, ycal, yte = train_test_split(Xtmp, ytmp, train_size=20000, test_size=40000,
                                                    stratify=ytmp, random_state=seed + 50)
            clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
            clf.fit(Xtr, ytr)
            Pcal = clf.predict_proba(Xcal)
            Pte = clf.predict_proba(Xte)
            print("n_train", n_train, "seed", seed, "fit+pred", round(time.time()-t0,1), flush=True)

            for ai, alpha in enumerate(ALPHAS):
                rng = np.random.default_rng(seed * 100 + ai)
                u_cal = rng.random(len(ycal))
                u_te = rng.random(len(yte))
                for score in SCORES:
                    if score == "naive":
                        sc = 1.0 - Pcal[np.arange(len(ycal)), ycal]
                        q = C.conformal_quantile(sc, alpha)
                        sets = C.build_sets("naive", Pte, q)
                    elif score == "aps_rand":
                        sc = C.aps_scores(Pcal, ycal, u_cal)
                        q = C.conformal_quantile(sc, alpha)
                        sets = C.build_sets("aps_rand", Pte, q, u=u_te)
                    else:
                        sc = C.aps_scores(Pcal, ycal, 1.0)
                        q = C.conformal_quantile(sc, alpha)
                        sets = C.build_sets("aps_det", Pte, q)

                    m = C.metrics(sets, yte, Pte, alpha)
                    forced, changed = C.force_nonempty(sets, Pte)
                    mf = C.metrics(forced, yte, Pte, alpha)
                    base = dict(dataset="covertype", model="logreg",
                                strength=n_train / 60000.0, n_train=n_train,
                                n_cal=20000, n_test=40000, alpha=alpha,
                                score=score, seed=seed, q=q)
                    rows.append(C.make_row(postprocess="raw", **base, **m))
                    rows.append(C.make_row(postprocess="forced", **base, **mf,
                                           delta=float(mf["coverage"] - m["coverage"]),
                                           changed=int(changed)))
            print("done", n_train, seed, "rows", len(rows), flush=True)

    C.save_results(os.path.join(ROOT, "results", "tabular.json"), rows, "exp_tabular.py",
                   checks={"dataset": "covertype", "n_subset": 120000,
                           "train_sizes": [6000, 60000],
                           "alphas": ALPHAS, "seeds": SEEDS, "scores": SCORES})
    print("saved rows", len(rows), "time", round(time.time()-t0,1), flush=True)
    for n_train in [6000, 60000]:
        for score in SCORES:
            for post in ["raw", "forced"]:
                s = [r for r in rows if r["score"] == score and r["postprocess"] == post
                     and r["alpha"] == 0.10 and r["n_train"] == n_train]
                print(n_train, score, post, "cov", round(float(np.mean([r["coverage"] for r in s])), 3),
                      "empty", round(float(np.mean([r["empty_rate"] for r in s])), 3),
                      "size", round(float(np.mean([r["size"] for r in s])), 2), flush=True)


if __name__ == "__main__":
    main()
