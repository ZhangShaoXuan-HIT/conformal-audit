"""CIFAR-10 replication of audits A and B.

Model strength is the number of training samples: 1k, 5k, 30k.
Test set is 10k, calibration size varies over 500, 2000, 10000.
Audit A: a calibrated threshold is split conformal.
Audit B: non-empty post-processing inflates coverage.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common as C  # noqa: E402

SEEDS = range(5)
STRENGTHS = [100 / 30000, 1000 / 30000, 5000 / 30000, 1.0]
ALPHA_A = 0.10
N_CAL_A = 2000
ALPHAS_B = [0.05, 0.10, 0.20]
N_CALS_B = [500, 2000, 10000]
SCORES = ["naive", "aps_rand", "aps_det", "raps"]
RAPS_LAM = 0.01
RAPS_K = 2


def sets_for(score, Pcal, ycal, Pte, alpha, seed):
    rng = np.random.default_rng(seed + 17)
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
        q = C.conformal_quantile(C.aps_scores(Pcal, ycal, u_cal, lam=RAPS_LAM, k_reg=RAPS_K), alpha)
        return q, C.build_sets("raps", Pte, q, u=u_te, lam=RAPS_LAM, k_reg=RAPS_K)
    raise ValueError(score)


def row_for(score, sets, yte, Pte, alpha, seed, strength, n_train, n_cal, post):
    if post == "raw":
        s, nf = sets, 0
    else:
        s, nf = C.force_nonempty(sets, Pte)
    m = C.metrics(s, yte, Pte, alpha)
    h = C.hits(s, yte)
    lo, hi = C.normal_ci(h)
    return C.make_row(
        dataset="cifar10", model="logreg_resnet18", strength=strength, n_train=n_train,
        n_cal=n_cal, n_test=len(yte), alpha=alpha, score=score, postprocess=post,
        seed=seed, coverage_lo=lo, coverage_hi=hi, n_forced=nf, **m)


def run():
    Xtr, ytr, Xte, yte_all = C.load_cifar_features()
    rows = []
    # cache heads per (strength, seed)
    heads = {}
    splits = {}
    for seed in SEEDS:
        pool, cal_pool = C.make_splits_cifar(ytr, seed, n_cal=10000)
        splits[seed] = (pool, cal_pool)
        for strength in STRENGTHS:
            clf, n_train = C.fit_head(Xtr[pool], ytr[pool], strength, seed)
            heads[(strength, seed)] = (clf, n_train)
        print("seed", seed, "heads done", flush=True)

    # Audit A
    for strength in STRENGTHS:
        for seed in SEEDS:
            pool, cal_pool = splits[seed]
            clf, n_train = heads[(strength, seed)]
            _, cal = C.make_splits_cifar(ytr, seed, n_cal=N_CAL_A)
            Pcal = clf.predict_proba(Xtr[cal])
            Pte = clf.predict_proba(Xte)
            ycal, yte = ytr[cal], yte_all
            p_true_cal = Pcal[np.arange(len(ycal)), ycal]
            q = C.conformal_quantile(1.0 - p_true_cal, ALPHA_A)
            t_max = float(np.quantile(Pcal.max(axis=1), ALPHA_A))
            t_true = float(np.quantile(p_true_cal, ALPHA_A))
            u_te = np.random.default_rng(seed + 999).random(len(yte))
            q_aps = C.conformal_quantile(C.aps_scores(Pcal, ycal, np.random.default_rng(seed + 11).random(len(ycal))), ALPHA_A)
            methods = {
                "threshold_raw": [np.flatnonzero(Pte[i] >= 1.0 - ALPHA_A).astype(int).tolist() for i in range(len(yte))],
                "threshold_maxprob": [np.flatnonzero(Pte[i] >= t_max).astype(int).tolist() for i in range(len(yte))],
                "threshold_trueclass": [np.flatnonzero(Pte[i] >= t_true).astype(int).tolist() for i in range(len(yte))],
                "threshold_conformal": [np.flatnonzero(Pte[i] >= 1.0 - q).astype(int).tolist() for i in range(len(yte))],
                "conformal_naive": C.build_sets("naive", Pte, q),
                "conformal_aps": C.build_sets("aps_rand", Pte, q_aps, u=u_te),
            }
            mismatch = sum(1 for i in range(len(yte))
                           if sorted(methods["threshold_conformal"][i]) != sorted(methods["conformal_naive"][i]))
            for name, sets in methods.items():
                for post in ("raw", "forced"):
                    rows.append(row_for(name, sets, yte, Pte, ALPHA_A, seed, strength, n_train,
                                        len(ycal), post))
            if mismatch:
                print("MISMATCH", strength, seed, mismatch, flush=True)
    C.save_results(os.path.join(ROOT, "results", "equiv_cifar.json"), rows, "exp_cifar.py",
                   checks={"audit": "A", "seeds": list(SEEDS), "strengths": STRENGTHS})
    print("audit A rows", len(rows), flush=True)

    # Audit B
    rows_b = []
    for strength in STRENGTHS:
        for seed in SEEDS:
            pool, cal_pool = splits[seed]
            clf, n_train = heads[(strength, seed)]
            Pte = clf.predict_proba(Xte)
            yte = yte_all
            for n_cal in N_CALS_B:
                _, cal = C.make_splits_cifar(ytr, seed, n_cal=n_cal)
                Pcal = clf.predict_proba(Xtr[cal])
                ycal = ytr[cal]
                for alpha in ALPHAS_B:
                    for score in SCORES:
                        _, sets = sets_for(score, Pcal, ycal, Pte, alpha, seed)
                        for post in ("raw", "forced"):
                            rows_b.append(row_for(score, sets, yte, Pte, alpha, seed, strength,
                                                  n_train, len(ycal), post))
                print("b", strength, seed, n_cal, flush=True)
    C.save_results(os.path.join(ROOT, "results", "postprocess_cifar.json"), rows_b, "exp_cifar.py",
                   checks={"audit": "B", "seeds": list(SEEDS), "strengths": STRENGTHS,
                           "alphas": ALPHAS_B, "n_cals": N_CALS_B, "scores": SCORES})
    print("audit B rows", len(rows_b), flush=True)


if __name__ == "__main__":
    run()
