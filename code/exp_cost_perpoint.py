"""Per-point cost experiment for the empty-set decision.

Policies, with c_e = 1 and c_a on a grid:
  abstain:   empty -> c_a; non-empty -> 0 if correct, 1 if wrong.
  force:     empty -> argmax; non-empty unchanged.
  per-point: empty -> force if c_a > 1 - p_max, else abstain.

The per-point rule uses p_max as a proxy for the conditional accuracy of the
argmax on empty sets. It is a heuristic, not a guarantee.
"""
import json
import os
import sys
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

ALPHA = 0.10
SEEDS = [0, 1, 2, 3, 4]
C_GRID = np.round(np.linspace(0.0, 1.0, 101), 4)
ROWS = []


def add_rows(dataset, seed, Pte, yte, sets):
    n = len(yte)
    empty = np.array([len(s) == 0 for s in sets])
    set_correct = np.array([yte[i] in sets[i] for i in range(n)], dtype=float)
    pmax = Pte.max(axis=1)
    argmax_correct = (Pte.argmax(axis=1) == yte).astype(float)
    forced_correct = np.where(empty, argmax_correct, set_correct)
    empty_rate = float(empty.mean())
    a_e = float(argmax_correct[empty].mean()) if empty.any() else float("nan")
    for c_a in C_GRID:
        loss_abstain = float(np.mean(1 - set_correct) + (c_a - 1.0) * empty_rate)
        loss_force = float(np.mean(1 - forced_correct))
        force_here = empty & (c_a > (1.0 - pmax))
        loss = np.where(empty,
                        np.where(force_here, 1.0 - argmax_correct, c_a),
                        1.0 - set_correct)
        ROWS.append({
            "dataset": dataset, "seed": seed, "n": n, "alpha": ALPHA,
            "score": "aps_det", "c_a": float(c_a), "c_e": 1.0,
            "empty_rate": empty_rate, "a_E": a_e,
            "loss_abstain": loss_abstain, "loss_force": loss_force,
            "loss_perpoint": float(loss.mean()),
            "perpoint_abstain_rate": float((empty & ~force_here).mean()),
        })


def run_digits():
    X, y = C.load_dataset("digits")
    for seed in SEEDS:
        pool, cal, test = C.make_splits(y, 449, seed)
        clf, _ = C.fit_digits_model(X[pool], y[pool], 0.25, seed)
        Pcal, Pte = clf.predict_proba(X[cal]), clf.predict_proba(X[test])
        q = C.conformal_quantile(C.aps_scores(Pcal, y[cal], 1.0), ALPHA)
        add_rows("digits", seed, Pte, y[test], C.build_sets("aps_det", Pte, q))
        print("digits", seed, flush=True)


def run_cifar():
    Xtr, ytr, Xte, yte = C.load_cifar_features()
    for seed in SEEDS:
        pool, cal = C.make_splits_cifar(ytr, seed, n_cal=2000)
        clf, _ = C.fit_head(Xtr[pool], ytr[pool], 1.0, seed)
        Pcal, Pte = clf.predict_proba(Xtr[cal]), clf.predict_proba(Xte)
        q = C.conformal_quantile(C.aps_scores(Pcal, ytr[cal], 1.0), ALPHA)
        add_rows("cifar10", seed, Pte, yte, C.build_sets("aps_det", Pte, q))
        print("cifar10", seed, flush=True)


def run_covertype():
    X, y = fetch_openml("covertype", version=3, as_frame=False, return_X_y=True)
    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=int) - 1
    X, _, y, _ = train_test_split(X, y, train_size=120000, stratify=y, random_state=0)
    for seed in SEEDS:
        Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=60000, test_size=60000,
                                                stratify=y, random_state=seed)
        Xcal, Xte, ycal, yte = train_test_split(Xtmp, ytmp, train_size=20000, test_size=40000,
                                                stratify=ytmp, random_state=seed + 50)
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        clf.fit(Xtr, ytr)
        Pcal, Pte = clf.predict_proba(Xcal), clf.predict_proba(Xte)
        q = C.conformal_quantile(C.aps_scores(Pcal, ycal, 1.0), ALPHA)
        add_rows("covertype", seed, Pte, yte, C.build_sets("aps_det", Pte, q))
        print("covertype", seed, flush=True)


def main():
    run_digits()
    run_cifar()
    run_covertype()
    C.save_results(os.path.join(ROOT, "results", "cost_perpoint.json"), ROWS,
                   "exp_cost_perpoint.py",
                   checks={"alpha": ALPHA, "seeds": SEEDS, "score": "aps_det",
                           "c_grid": [float(C_GRID[0]), float(C_GRID[-1]), len(C_GRID)]})
    print("rows", len(ROWS), flush=True)
    for ds in ["digits", "cifar10", "covertype"]:
        for c in [0.05, 0.10, 0.20, 0.50]:
            sub = [r for r in ROWS if r["dataset"] == ds and abs(r["c_a"] - c) < 1e-6]
            print(ds, c,
                  "abstain", round(float(np.mean([r["loss_abstain"] for r in sub])), 4),
                  "force", round(float(np.mean([r["loss_force"] for r in sub])), 4),
                  "perpoint", round(float(np.mean([r["loss_perpoint"] for r in sub])), 4),
                  flush=True)


if __name__ == "__main__":
    main()
