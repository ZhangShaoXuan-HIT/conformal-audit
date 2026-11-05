"""Audit C: the alpha_t update is not ACI.

Three drift schedules, two update rules, four step sizes, five seeds.
  fixed  alpha_{t+1} = alpha_t + gamma * (alpha - err_t)    correct ACI
  buggy  alpha_{t+1} = alpha_t + gamma * (alpha_t - err_t)  common mistake
Static calibration is included as a baseline.
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
STRENGTH = 0.05
GAMMAS = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
SEEDS = range(5)
N_BLOCKS = 9
BLOCK = 50
SCHEDULES = {
    "linear": np.linspace(0.0, 0.60, N_BLOCKS),
    "step": np.array([0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5]),
    "abrupt": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6, 0.6, 0.6]),
}


def q_at(sorted_scores, alpha):
    n = len(sorted_scores)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = max(1, min(k, n))
    return float(sorted_scores[k - 1])


def stream(seed, schedule):
    X, y = C.load_dataset("digits")
    pool, cal, test = C.make_splits(y, 449, seed)
    clf, n_train = C.fit_digits_model(X[pool], y[pool], STRENGTH, seed)
    Pcal = clf.predict_proba(X[cal])
    ycal = y[cal]
    sc = 1.0 - Pcal[np.arange(len(ycal)), ycal]
    sorted_sc = np.sort(sc)
    q_static = q_at(sorted_sc, ALPHA)

    rng = np.random.default_rng(seed + 31)
    Xte, yte = X[test], y[test]
    per = len(yte) // N_BLOCKS
    sigmas = SCHEDULES[schedule]
    Xs, ys, lvl = [], [], []
    for b in range(N_BLOCKS):
        idx = np.arange(b * per, (b + 1) * per)
        Xs.append(np.clip(Xte[idx] + rng.normal(0, sigmas[b], size=Xte[idx].shape), 0.0, 1.0))
        ys.append(yte[idx])
        lvl += [b] * len(idx)
    P = clf.predict_proba(np.vstack(Xs))
    ys = np.concatenate(ys)
    lvl = np.array(lvl)
    n = len(ys)

    static_sets = C.build_sets("naive", P, q_static)
    static_hit = C.hits(static_sets, ys)
    static_size = np.array([len(s) for s in static_sets], dtype=float)

    rows = []
    # static baseline
    rows.append(record("static", None, seed, schedule, static_hit, static_size,
                       np.full(n, ALPHA), q_static, n_train))
    for gamma in GAMMAS:
        for update in ("fixed", "buggy"):
            a = ALPHA
            hits = np.empty(n)
            sizes = np.empty(n)
            alphas = np.empty(n)
            for i in range(n):
                q = q_at(sorted_sc, a)
                st = C.build_sets("naive", P[i:i + 1], q)[0]
                hit = int(ys[i] in st)
                hits[i] = hit
                sizes[i] = len(st)
                alphas[i] = a
                err = 1 - hit
                if update == "fixed":
                    a = a + gamma * (ALPHA - err)
                else:
                    a = a + gamma * (a - err)
                a = float(np.clip(a, 0.001, 0.999))
            rows.append(record(update, gamma, seed, schedule, hits, sizes, alphas,
                               q_static, n_train))
    return rows


def record(update, gamma, seed, schedule, hits, sizes, alphas, q_static, n_train):
    hits = np.asarray(hits, dtype=float)
    sizes = np.asarray(sizes, dtype=float)
    alphas = np.asarray(alphas, dtype=float)
    block_cov = [float(hits[i * BLOCK:(i + 1) * BLOCK].mean()) for i in range(N_BLOCKS)]
    block_size = [float(sizes[i * BLOCK:(i + 1) * BLOCK].mean()) for i in range(N_BLOCKS)]
    alpha_block = [float(alphas[(i + 1) * BLOCK - 1]) for i in range(N_BLOCKS)]
    w = 50
    sliding = np.convolve(hits, np.ones(w) / w, mode="valid")
    sliding = sliding[::10].tolist()
    clip = float(np.mean((alphas <= 0.001 + 1e-9) | (alphas >= 0.999 - 1e-9)))
    return C.make_row(
        dataset="digits", model="logreg", strength=STRENGTH, n_train=n_train,
        n_cal=449, n_test=int(len(hits)), alpha=ALPHA, score="naive",
        postprocess="raw", seed=seed, schedule=schedule, update=update, gamma=gamma,
        coverage=float(hits.mean()), coverage_lo=None, coverage_hi=None,
        size=float(sizes.mean()), empty_rate=None,
        class_cov=None, class_dev_maxabs=None, worst_class_gap=None,
        ece=None, nll=None, accuracy=None,
        block_cov=block_cov, block_size=block_size, alpha_block=alpha_block,
        alpha_final=float(alphas[-1]), alpha_min=float(alphas.min()),
        alpha_max=float(alphas.max()), clip_fraction=clip,
        frac_sets_ge9=float(np.mean(sizes >= 9)), sliding_cov=sliding,
        q_static=q_static,
    )


def run():
    rows = []
    for seed in SEEDS:
        for schedule in SCHEDULES:
            rows.extend(stream(seed, schedule))
    C.save_results(
        os.path.join(ROOT, "results", "aci_digits.json"), rows, "exp_aci.py",
        checks={"rows": len(rows), "gammas": GAMMAS, "schedules": list(SCHEDULES),
                "seeds": list(SEEDS), "alpha": ALPHA, "strength": STRENGTH},
    )
    print("rows:", len(rows))
    for sched in SCHEDULES:
        sub = [r for r in rows if r["schedule"] == sched and r["update"] != "static"]
        fixed = [r for r in sub if r["update"] == "fixed" and r["gamma"] == 0.02]
        buggy = [r for r in sub if r["update"] == "buggy" and r["gamma"] == 0.02]
        print(sched, "fixed", round(float(np.mean([r["coverage"] for r in fixed])), 3),
              "buggy", round(float(np.mean([r["coverage"] for r in buggy])), 3))


if __name__ == "__main__":
    run()
