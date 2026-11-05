"""Core utilities for the conformal audit project.

Design rule
-----------
build_sets NEVER forces non-empty sets. Forcing is a separate post-processing
step, applied explicitly and tagged in every result row. The audit depends on
keeping these two operations apart.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys

import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SCHEMA_VERSION = "1.0"


def environment() -> dict:
    import matplotlib
    import scipy
    import sklearn
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        commit = ""
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "matplotlib": matplotlib.__version__,
        "platform": platform.platform(),
        "git_commit": commit or None,
    }


def load_dataset(name: str):
    if name == "digits":
        X, y = load_digits(return_X_y=True)
        return X.astype(float) / 16.0, y.astype(int)
    raise ValueError("unknown dataset: " + str(name))


def make_splits(y, n_cal, seed, n_train_pool=898, n_test=450):
    """Fixed test set and fixed train pool; only the calibration size varies.

    This isolates the effect of n_cal from the effect of model strength.
    Returns sorted index arrays for (train_pool, calibration, test).
    """
    idx = np.arange(len(y))
    rest, test = train_test_split(idx, test_size=n_test, stratify=y, random_state=seed)
    pool, cal_pool = train_test_split(
        rest, train_size=n_train_pool, stratify=y[rest], random_state=seed + 1
    )
    if n_cal >= len(cal_pool):
        cal = cal_pool
    else:
        cal, _ = train_test_split(
            cal_pool, train_size=n_cal, stratify=y[cal_pool], random_state=seed + 2
        )
    return np.sort(pool), np.sort(cal), np.sort(test)


def fit_digits_model(X, y, strength, seed):
    """Fit a standardiser + multinomial logistic regression on a fraction of X."""
    if strength >= 1.0:
        idx = np.arange(len(y))
    else:
        idx, _ = train_test_split(
            np.arange(len(y)), train_size=strength, stratify=y, random_state=seed + 7
        )
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=1.0))
    clf.fit(X[idx], y[idx])
    return clf, int(len(idx))


def conformal_quantile(scores, alpha):
    s = np.sort(np.asarray(scores, dtype=float))
    n = len(s)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = max(1, min(k, n))
    return float(s[k - 1])


def _aps_parts(P):
    order = np.argsort(-P, axis=1, kind="stable")
    ps = np.take_along_axis(P, order, axis=1)
    cum = np.cumsum(ps, axis=1)
    cum_before = np.concatenate([np.zeros((len(P), 1)), cum[:, :-1]], axis=1)
    return order, ps, cum_before


def aps_scores(P, y, u, lam=0.0, k_reg=0):
    """Randomised APS score for the true label. u may be a scalar (deterministic APS)."""
    order, ps, cum_before = _aps_parts(P)
    inv = np.argsort(order, axis=1)
    rows = np.arange(len(y))
    rank = inv[rows, y]
    p_true = P[rows, y]
    u = np.asarray(u, dtype=float)
    if u.ndim == 0:
        u = np.full(len(y), float(u))
    s = cum_before[rows, rank] + u * p_true
    if lam:
        s = s + lam * np.maximum(0, rank + 1 - k_reg)
    return s


def build_sets(score, P, q, u=None, lam=0.0, k_reg=0):
    """Build prediction sets. Empty sets are kept as empty; never patched here."""
    n, K = P.shape
    if score == "naive":
        return [np.flatnonzero(P[i] >= 1.0 - q).astype(int).tolist() for i in range(n)]
    if score not in ("aps_rand", "aps_det", "raps"):
        raise ValueError("unknown score: " + str(score))
    order, ps, cum_before = _aps_parts(P)
    if score == "aps_det":
        uu = np.ones(n)
    else:
        if u is None:
            uu = np.full(n, 0.5)
        else:
            uu = np.asarray(u, dtype=float).reshape(-1)
            if len(uu) != n:
                raise ValueError("u must have one value per row")
    ranks = np.arange(K)[None, :]
    S = cum_before + uu[:, None] * ps
    if score == "raps" or lam:
        S = S + lam * np.maximum(0, ranks + 1 - k_reg)
    return [order[i][S[i] <= q].astype(int).tolist() for i in range(n)]


def force_nonempty(sets, P):
    out = []
    changed = 0
    for i, s in enumerate(sets):
        if len(s) == 0:
            out.append([int(np.argmax(P[i]))])
            changed += 1
        else:
            out.append(list(s))
    return out, changed


def hits(sets, y):
    return np.array([int(y[i] in sets[i]) for i in range(len(y))], dtype=float)


def ece(P, y, n_bins=15):
    conf = P.max(axis=1)
    pred = P.argmax(axis=1)
    acc = (pred == y).astype(float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    value = 0.0
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        if i < n_bins - 1:
            m = (conf >= lo) & (conf < hi)
        else:
            m = (conf >= lo) & (conf <= hi)
        if m.sum():
            value += m.mean() * abs(acc[m].mean() - conf[m].mean())
    return float(value)


def nll(P, y):
    p = np.clip(P[np.arange(len(y)), y], 1e-12, 1.0)
    return float(-np.mean(np.log(p)))


def metrics(sets, y, P, alpha):
    n = len(y)
    K = P.shape[1]
    cov = float(np.mean(hits(sets, y)))
    size = float(np.mean([len(s) for s in sets]))
    empty = float(np.mean([len(s) == 0 for s in sets]))
    class_cov = []
    for c in range(K):
        idx = np.flatnonzero(y == c)
        class_cov.append(float(np.mean(hits([sets[i] for i in idx], y[idx]))) if len(idx) else float("nan"))
    dev = np.array(class_cov, dtype=float) - (1.0 - alpha)
    pred = P.argmax(axis=1)
    return {
        "coverage": cov,
        "size": size,
        "empty_rate": empty,
        "class_cov": class_cov,
        "class_dev_maxabs": float(np.nanmax(np.abs(dev))),
        "worst_class_gap": float(max(0.0, -np.nanmin(dev))),
        "ece": ece(P, y),
        "nll": nll(P, y),
        "accuracy": float(np.mean(pred == y)),
    }


def bootstrap_ci(values, n_boot=1000, seed=0):
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    for b in range(n_boot):
        means[b] = v[rng.integers(0, len(v), len(v))].mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def make_row(**kw):
    base = {
        "dataset": None, "model": None, "strength": None, "n_train": None,
        "n_cal": None, "n_test": None, "alpha": None, "score": None,
        "postprocess": "raw", "seed": None,
        "coverage": None, "coverage_lo": None, "coverage_hi": None,
        "size": None, "empty_rate": None,
        "class_cov": None, "class_dev_maxabs": None, "worst_class_gap": None,
        "ece": None, "nll": None, "accuracy": None,
    }
    base.update(kw)
    return base


def save_results(path, rows, generated_by, checks=None):
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": generated_by,
        "environment": environment(),
        "checks": checks or {},
        "rows": rows,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, allow_nan=False)


# ---------------------------------------------------------------------------
# CIFAR-10 helpers (phase 2). Features are cached by code/cifar_features.py.
# ---------------------------------------------------------------------------

def load_cifar_features(path=None):
    path = path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "data", "cifar10_features.npz")
    d = np.load(path)
    return d["Xtr"].astype(np.float32), d["ytr"].astype(int), d["Xte"].astype(np.float32), d["yte"].astype(int)


def make_splits_cifar(y, seed, n_cal=2000, n_train_pool=30000):
    """Fixed 30k train pool; n_cal drawn from the remaining 20k.

    The official 10k CIFAR-10 test set is used for evaluation, so only the
    50k training labels are split here. Returns (train_pool_idx, cal_idx).
    """
    idx = np.arange(len(y))
    pool, cal_pool = train_test_split(idx, train_size=n_train_pool, stratify=y, random_state=seed + 1)
    if n_cal >= len(cal_pool):
        cal = cal_pool
    else:
        cal, _ = train_test_split(cal_pool, train_size=n_cal, stratify=y[cal_pool], random_state=seed + 2)
    return np.sort(pool), np.sort(cal)


def fit_head(X, y, strength, seed, max_iter=1000):
    """Standardiser + multinomial logistic regression on a fraction of the pool."""
    if strength >= 1.0:
        idx = np.arange(len(y))
    else:
        idx, _ = train_test_split(np.arange(len(y)), train_size=strength, stratify=y, random_state=seed + 7)
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=max_iter, C=1.0))
    clf.fit(X[idx], y[idx])
    return clf, int(len(idx))


def normal_ci(hits, z=1.96):
    p = float(np.mean(hits))
    n = len(hits)
    se = float(np.sqrt(max(p * (1.0 - p), 1e-12) / n))
    return max(0.0, p - z * se), min(1.0, p + z * se)
