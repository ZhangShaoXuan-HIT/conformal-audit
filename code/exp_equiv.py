"""Audit A: a calibrated softmax threshold is split conformal with the naive score.

Compares five decision rules at alpha = 0.10 on the digits benchmark:
  threshold_raw        fixed probability threshold at 1 - alpha
  threshold_maxprob    threshold at the alpha-quantile of the max probability
  threshold_trueclass  threshold at the alpha-quantile of the true-class probability
  threshold_conformal  threshold at 1 - q, where q is the conformal quantile
  conformal_naive      split conformal with s = 1 - p_y
  conformal_aps        split conformal with the randomised APS score

Every rule is evaluated twice, once with empty sets kept and once after the
argmax is forced into empty sets. The two evaluations are tagged separately.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common as C  # noqa: E402

ALPHA = 0.10
SEEDS = range(5)
STRENGTHS = [0.05, 0.25, 1.0]
N_CAL = 449
N_BOOT = 500

LABELS = {
    "threshold_raw": "softmax threshold, raw t = 1 - alpha",
    "threshold_maxprob": "threshold at max-prob quantile",
    "threshold_trueclass": "threshold at true-class quantile",
    "threshold_conformal": "threshold at t = 1 - q (conformal)",
    "conformal_naive": "split conformal, naive score",
    "conformal_aps": "split conformal, APS",
}


def one_rule(name, sets, yte, Pte, alpha, seed):
    rows = []
    for post in ("raw", "forced"):
        if post == "raw":
            s = sets
            n_forced = 0
        else:
            s, n_forced = C.force_nonempty(sets, Pte)
        m = C.metrics(s, yte, Pte, alpha)
        h = C.hits(s, yte)
        lo, hi = C.bootstrap_ci(h, n_boot=N_BOOT, seed=seed)
        rows.append(C.make_row(
            dataset="digits", model="logreg", strength=None, n_train=None,
            n_cal=None, n_test=len(yte), alpha=alpha, score=name,
            postprocess=post, seed=seed,
            coverage_lo=lo, coverage_hi=hi, n_forced=n_forced, **m,
        ))
    return rows


def run():
    X, y = C.load_dataset("digits")
    rows = []
    mismatches = 0
    for strength in STRENGTHS:
        for seed in SEEDS:
            pool, cal, test = C.make_splits(y, N_CAL, seed)
            clf, n_train = C.fit_digits_model(X[pool], y[pool], strength, seed)
            Pcal = clf.predict_proba(X[cal])
            Pte = clf.predict_proba(X[test])
            ycal, yte = y[cal], y[test]
            p_true_cal = Pcal[np.arange(len(ycal)), ycal]

            q = C.conformal_quantile(1.0 - p_true_cal, ALPHA)
            t_max = float(np.quantile(Pcal.max(axis=1), ALPHA))
            t_true = float(np.quantile(p_true_cal, ALPHA))

            u_cal = np.random.default_rng(seed + 11).random(len(ycal))
            u_te = np.random.default_rng(seed + 999).random(len(yte))
            q_aps = C.conformal_quantile(C.aps_scores(Pcal, ycal, u_cal), ALPHA)

            methods = {
                "threshold_raw": [np.flatnonzero(Pte[i] >= 1.0 - ALPHA).astype(int).tolist() for i in range(len(yte))],
                "threshold_maxprob": [np.flatnonzero(Pte[i] >= t_max).astype(int).tolist() for i in range(len(yte))],
                "threshold_trueclass": [np.flatnonzero(Pte[i] >= t_true).astype(int).tolist() for i in range(len(yte))],
                "threshold_conformal": [np.flatnonzero(Pte[i] >= 1.0 - q).astype(int).tolist() for i in range(len(yte))],
                "conformal_naive": C.build_sets("naive", Pte, q),
                "conformal_aps": C.build_sets("aps_rand", Pte, q_aps, u=u_te),
            }

            for i in range(len(yte)):
                if sorted(methods["threshold_conformal"][i]) != sorted(methods["conformal_naive"][i]):
                    mismatches += 1

            for name, sets in methods.items():
                for row in one_rule(name, sets, yte, Pte, ALPHA, seed):
                    row["strength"] = strength
                    row["n_train"] = n_train
                    row["n_cal"] = len(ycal)
                    rows.append(row)

    C.save_results(
        os.path.join(ROOT, "results", "equiv_digits.json"), rows, "exp_equiv.py",
        checks={"set_mismatches": mismatches, "n_rows": len(rows)},
    )
    print("rows:", len(rows))
    print("set mismatches between threshold(1-q) and conformal_naive:", mismatches)
    print("n_train by strength:", {s: sorted({r["n_train"] for r in rows if r["strength"] == s}) for s in STRENGTHS})
    print("n_cal:", sorted({r["n_cal"] for r in rows}))


if __name__ == "__main__":
    run()
