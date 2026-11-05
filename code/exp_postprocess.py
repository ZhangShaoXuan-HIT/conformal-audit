"""Audit B: non-empty post-processing inflates coverage and set size.

Grid: score in {naive, aps_rand, aps_det, raps} x alpha x n_cal x model strength.
For every cell, record metrics before and after force_nonempty. The raw and
forced rows share the same prediction sets; only the post-processing differs.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common as C  # noqa: E402

ALPHAS = [0.05, 0.10, 0.20]
N_CALS = [100, 225, 449]
STRENGTHS = [0.05, 0.25, 1.0]
SEEDS = range(5)
SCORES = ["naive", "aps_rand", "aps_det", "raps"]
RAPS_LAM = 0.01
RAPS_K = 2
N_BOOT = 300


def make_sets(score, Pcal, ycal, Pte, alpha, rng):
    u_cal = rng.random(len(ycal))
    u_te = rng.random(len(Pte))
    if score == "naive":
        q = C.conformal_quantile(1.0 - Pcal[np.arange(len(ycal)), ycal], alpha)
        return q, C.build_sets("naive", Pte, q)
    if score == "aps_rand":
        q = C.conformal_quantile(C.aps_scores(Pcal, ycal, u_cal), alpha)
        return q, C.build_sets("aps_rand", Pte, q, u=u_te)
    if score == "aps_det":
        q = C.conformal_quantile(C.aps_scores(Pcal, ycal, 1.0), alpha)
        return q, C.build_sets("aps_det", Pte, q)
    if score == "raps":
        q = C.conformal_quantile(
            C.aps_scores(Pcal, ycal, u_cal, lam=RAPS_LAM, k_reg=RAPS_K), alpha)
        return q, C.build_sets("raps", Pte, q, u=u_te, lam=RAPS_LAM, k_reg=RAPS_K)
    raise ValueError(score)


def run():
    X, y = C.load_dataset("digits")
    rows = []
    cells = 0
    for strength in STRENGTHS:
        for seed in SEEDS:
            pool, _, _ = C.make_splits(y, 449, seed)
            clf, n_train = C.fit_digits_model(X[pool], y[pool], strength, seed)
            for n_cal in N_CALS:
                _, cal, test = C.make_splits(y, n_cal, seed)
                Pcal = clf.predict_proba(X[cal])
                Pte = clf.predict_proba(X[test])
                ycal, yte = y[cal], y[test]
                for alpha in ALPHAS:
                    for si, score in enumerate(SCORES):
                        rng = np.random.default_rng(seed * 100000 + n_cal * 100 + int(alpha * 100) + si)
                        q, sets = make_sets(score, Pcal, ycal, Pte, alpha, rng)
                        forced, n_forced = C.force_nonempty(sets, Pte)
                        for post, s, nf in (("raw", sets, 0), ("forced", forced, n_forced)):
                            m = C.metrics(s, yte, Pte, alpha)
                            h = C.hits(s, yte)
                            lo, hi = C.bootstrap_ci(h, n_boot=N_BOOT, seed=seed)
                            rows.append(C.make_row(
                                dataset="digits", model="logreg", strength=strength,
                                n_train=n_train, n_cal=len(ycal), n_test=len(yte),
                                alpha=alpha, score=score, postprocess=post, seed=seed,
                                coverage_lo=lo, coverage_hi=hi, q=q, n_forced=nf,
                                lam=RAPS_LAM if score == "raps" else None,
                                k_reg=RAPS_K if score == "raps" else None,
                                **m,
                            ))
                        cells += 1
    C.save_results(
        os.path.join(ROOT, "results", "postprocess_digits.json"), rows, "exp_postprocess.py",
        checks={"cells": cells, "rows": len(rows), "grid": {
            "alphas": ALPHAS, "n_cals": N_CALS, "strengths": STRENGTHS,
            "scores": SCORES, "seeds": list(SEEDS)}},
    )
    print("cells:", cells, "rows:", len(rows))
    print("n_train:", {s: sorted({r["n_train"] for r in rows if r["strength"] == s}) for s in STRENGTHS})


if __name__ == "__main__":
    run()
