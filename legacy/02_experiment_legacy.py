"""Reproducible conformal-prediction experiments on sklearn digits.

All numbers written to out/numbers.json are actually computed here; nothing is estimated.
Run with the isolated venv python.
"""
import os, json
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

SEEDS = list(range(10))
ALPHAS = [0.01, 0.02, 0.05, 0.10, 0.20, 0.30]
TARGET = 0.90
K = 10
plt.rcParams.update({"figure.dpi": 150, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3, "figure.facecolor": "white",
                     "axes.facecolor": "white", "savefig.facecolor": "white"})


def load_split(seed):
    X, y = load_digits(return_X_y=True)
    X = X.astype(float) / 16.0
    Xtr, Xrest, ytr, yrest = train_test_split(
        X, y, test_size=0.5, stratify=y, random_state=seed)
    Xcal, Xte, ycal, yte = train_test_split(
        Xrest, yrest, test_size=0.5, stratify=yrest, random_state=seed + 1000)
    # Small-sample high-stakes setting: keep only ~5% of the training pool
    # so the base model is not over-confident and prediction sets vary with alpha.
    Xtr_s, _, ytr_s, _ = train_test_split(
        Xtr, ytr, train_size=0.05, stratify=ytr, random_state=seed + 7)
    return Xtr_s, ytr_s, Xcal, ycal, Xte, yte


def fit_model(Xtr, ytr, seed):
    clf = make_pipeline(StandardScaler(),
                        LogisticRegression(max_iter=3000, C=1.0))
    clf.fit(Xtr, ytr)
    return clf


def scores_naive(P, y):
    return 1.0 - P[np.arange(len(y)), y]


def scores_aps(P, y, rng):
    """Romano et al. (2020) APS score with per-sample randomization."""
    p_true = P[np.arange(len(y)), y]
    u = rng.random(len(y))
    greater = np.where(P > p_true[:, None], P, 0.0).sum(axis=1)
    return greater + u * p_true


def conf_quantile(scores, alpha):
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    k = max(1, min(k, n))
    return float(np.sort(scores)[k - 1])


def _ensure_nonempty(P, sets):
    """Force the argmax class into empty sets (common engineering practice).
    This can only increase coverage, so the 1-alpha lower bound still holds."""
    for i in range(len(P)):
        if len(sets[i]) == 0:
            sets[i] = [int(np.argmax(P[i]))]
    return sets


def sets_naive(P, q):
    out = [np.flatnonzero(P[i] >= 1.0 - q).tolist() for i in range(len(P))]
    return _ensure_nonempty(P, out)


def sets_aps(P, q, u):
    """Prediction sets for APS. Ties in probability are broken by descending order."""
    out = []
    for i in range(len(P)):
        order = np.argsort(-P[i])
        ps = P[i][order]
        cum_before = np.concatenate([[0.0], np.cumsum(ps)[:-1]])
        s = cum_before + u[i] * ps
        out.append(sorted(order[s <= q].tolist()))
    return _ensure_nonempty(P, out)


def sets_threshold(P, alpha):
    """Baseline: treat the softmax score as a confidence and apply a hard threshold."""
    out = [np.flatnonzero(P[i] >= 1 - alpha).tolist() for i in range(len(P))]
    return _ensure_nonempty(P, out)


def sets_cumulative(P, alpha):
    """Baseline: accumulate top probabilities until reaching 1-alpha."""
    out = []
    for i in range(len(P)):
        order = np.argsort(-P[i])
        c = np.cumsum(P[i][order])
        k = int(np.searchsorted(c, 1 - alpha) + 1)
        out.append(sorted(order[:min(k, len(order))].tolist()))
    return _ensure_nonempty(P, out)


def metrics(sets, y):
    cov = float(np.mean([int(y[i] in sets[i]) for i in range(len(y))]))
    size = float(np.mean([len(s) for s in sets]))
    empty = float(np.mean([int(len(s) == 0) for s in sets]))
    cls = []
    for c in range(K):
        idx = np.flatnonzero(y == c)
        cls.append(float(np.mean([int(y[i] in sets[i]) for i in idx])) if len(idx) else float("nan"))
    return {"coverage": cov, "size": size, "empty_rate": empty, "class_cov": cls}


def e1():
    rows = []
    for seed in SEEDS:
        Xtr, ytr, Xcal, ycal, Xte, yte = load_split(seed)
        clf = fit_model(Xtr, ytr, seed)
        Pcal, Pte = clf.predict_proba(Xcal), clf.predict_proba(Xte)
        sc_n = scores_naive(Pcal, ycal)
        sc_a = scores_aps(Pcal, ycal, np.random.default_rng(seed + 7))
        u_te = np.random.default_rng(seed + 999).random(len(yte))
        for alpha in ALPHAS:
            qn, qa = conf_quantile(sc_n, alpha), conf_quantile(sc_a, alpha)
            for name, st in (("naive", sets_naive(Pte, qn)),
                             ("APS", sets_aps(Pte, qa, u_te))):
                rows.append({"seed": seed, "alpha": alpha, "method": name,
                             **metrics(st, yte)})
    summary = []
    for alpha in ALPHAS:
        for name in ("naive", "APS"):
            sub = [r for r in rows if r["alpha"] == alpha and r["method"] == name]
            cov = np.array([r["coverage"] for r in sub])
            size = np.array([r["size"] for r in sub])
            empty = np.array([r["empty_rate"] for r in sub])
            cls = np.nanmean(np.array([r["class_cov"] for r in sub]), axis=0)
            summary.append({
                "alpha": alpha, "method": name, "target": 1 - alpha,
                "coverage_mean": float(cov.mean()), "coverage_std": float(cov.std(ddof=1)),
                "size_mean": float(size.mean()), "size_std": float(size.std(ddof=1)),
                "empty_rate_mean": float(empty.mean()),
                "class_cov_mean": cls.tolist(),
                "class_dev_maxabs": float(np.nanmax(np.abs(cls - (1 - alpha)))),
                "class_dev_std": float(np.nanstd(cls - (1 - alpha), ddof=1)),
            })
    return rows, summary


def temperature(P, y):
    """Fit a single temperature on calibration logits by minimising NLL."""
    from scipy.optimize import minimize_scalar
    from scipy.special import logsumexp
    logp = np.log(np.clip(P, 1e-12, 1.0))
    def nll(logT):
        z = logp / np.exp(logT)
        return float(-np.mean(z[np.arange(len(y)), y] - logsumexp(z, axis=1)))
    res = minimize_scalar(nll, bounds=(-2.0, 3.0), method="bounded")
    return float(np.exp(res.x)), float(res.fun)


def e2(alpha=TARGET):
    rows, temps = [], []
    for seed in SEEDS:
        Xtr, ytr, Xcal, ycal, Xte, yte = load_split(seed)
        clf = fit_model(Xtr, ytr, seed)
        Pcal, Pte = clf.predict_proba(Xcal), clf.predict_proba(Xte)
        T, nll = temperature(Pcal, ycal)
        temps.append(T)
        Pte_t = np.clip(Pte ** (1.0 / T), 1e-12, 1.0)
        Pte_t /= Pte_t.sum(axis=1, keepdims=True)
        sc_n = scores_naive(Pcal, ycal)
        sc_a = scores_aps(Pcal, ycal, np.random.default_rng(seed + 7))
        u_te = np.random.default_rng(seed + 999).random(len(yte))
        variants = {
            "Softmax threshold (raw)": sets_threshold(Pte, alpha),
            "Temperature + threshold": sets_threshold(Pte_t, alpha),
            "Split conformal (naive)": sets_naive(Pte, conf_quantile(sc_n, alpha)),
            "Split conformal (APS)": sets_aps(Pte, conf_quantile(sc_a, alpha), u_te),
        }
        for name, st in variants.items():
            rows.append({"seed": seed, "method": name, **metrics(st, yte)})
    summary = []
    for name in ["Softmax threshold (raw)", "Temperature + threshold",
                 "Split conformal (naive)", "Split conformal (APS)"]:
        sub = [r for r in rows if r["method"] == name]
        cov = np.array([r["coverage"] for r in sub])
        size = np.array([r["size"] for r in sub])
        empty = np.array([r["empty_rate"] for r in sub])
        summary.append({"method": name, "coverage_mean": float(cov.mean()),
                        "coverage_std": float(cov.std(ddof=1)),
                        "size_mean": float(size.mean()), "size_std": float(size.std(ddof=1)),
                        "empty_rate_mean": float(empty.mean()),
                        "coverage_error_mean": float(np.mean(np.abs(cov - (1 - alpha))))})
    wilcoxon = None
    try:
        from scipy.stats import wilcoxon
        a = np.array([abs(r["coverage"] - (1 - alpha)) for r in rows
                      if r["method"] == "Softmax threshold (raw)"])
        b = np.array([abs(r["coverage"] - (1 - alpha)) for r in rows
                      if r["method"] == "Split conformal (APS)"])
        stat, p = wilcoxon(a, b)
        wilcoxon = {"statistic": float(stat), "p_value": float(p),
                    "comparison": "|coverage - 0.90|, raw softmax threshold vs APS, paired over 10 seeds"}
    except Exception as ex:
        wilcoxon = {"error": str(ex)}
    return rows, summary, {"T_mean": float(np.mean(temps)), "T_std": float(np.std(temps, ddof=1))}, wilcoxon


def e3(alpha=0.10, gamma=0.02, seed=0):
    Xtr, ytr, Xcal, ycal, Xte, yte = load_split(seed)
    clf = fit_model(Xtr, ytr, seed)
    Pcal = clf.predict_proba(Xcal)
    sc = scores_naive(Pcal, ycal)
    sorted_sc = np.sort(sc)
    q_static = conf_quantile(sorted_sc, alpha)
    rng = np.random.default_rng(seed + 31)
    levels = np.linspace(0.0, 0.60, 9)
    per = len(yte) // 9
    Xs, ys, lvl = [], [], []
    for li, s in enumerate(levels):
        idx = np.arange(li * per, (li + 1) * per)
        Xn = np.clip(Xte[idx] + rng.normal(0, s, size=Xte[idx].shape), 0.0, 1.0)
        Xs.append(Xn); ys.append(yte[idx]); lvl += [li] * len(idx)
    Xstream, ystream = np.vstack(Xs), np.concatenate(ys)
    lvl = np.array(lvl)
    Pstream = clf.predict_proba(Xstream)

    static_sets = sets_naive(Pstream, q_static)
    static_hit = np.array([int(ystream[i] in static_sets[i]) for i in range(len(ystream))])
    static_sizes = np.array([len(s) for s in static_sets])

    a_t = alpha
    ada_hit, ada_sizes, alphas = [], [], []
    for i in range(len(ystream)):
        n = len(sorted_sc)
        k = max(1, min(int(np.ceil((n + 1) * (1 - a_t))), n))
        q_t = float(sorted_sc[k - 1])
        st = sets_naive(Pstream[i:i + 1], q_t)[0]
        hit = int(ystream[i] in st)
        ada_hit.append(hit); ada_sizes.append(len(st)); alphas.append(a_t)
        err = 1 - hit
        a_t = float(np.clip(a_t + gamma * (a_t - err), 0.001, 0.999))
    ada_hit = np.array(ada_hit); ada_sizes = np.array(ada_sizes)

    w = 50
    def sliding(h):
        return np.array([h[max(0, i - w + 1):i + 1].mean() for i in range(len(h))])
    per_level = []
    for li, s in enumerate(levels):
        m = lvl == li
        per_level.append({"noise_sigma": float(s),
                          "static_cov": float(static_hit[m].mean()),
                          "adaptive_cov": float(ada_hit[m].mean()),
                          "static_size": float(static_sizes[m].mean()),
                          "adaptive_size": float(ada_sizes[m].mean())})
    return {
        "alpha": alpha, "gamma": gamma, "seed": seed, "target": 1 - alpha,
        "noise_levels": levels.tolist(), "stream_len": int(len(ystream)),
        "static_overall_cov": float(static_hit.mean()),
        "adaptive_overall_cov": float(ada_hit.mean()),
        "static_mean_size": float(static_sizes.mean()),
        "adaptive_mean_size": float(ada_sizes.mean()),
        "alpha_final": float(alphas[-1]), "alpha_min": float(min(alphas)),
        "alpha_max": float(max(alphas)),
        "static_sliding": sliding(static_hit).tolist(),
        "adaptive_sliding": sliding(ada_hit).tolist(),
        "alphas": [float(a) for a in alphas],
        "per_level": per_level,
        "example_images": Xstream[:6].tolist(),
        "example_labels": ystream[:6].tolist(),
        "example_sets_static": static_sets[:6],
        "example_sets_adaptive": None,
        "clean_images": Xte[:6].tolist(),
        "clean_labels": yte[:6].tolist(),
    }


def savefig(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("[FIG]", name, flush=True)


def make_figures(summary1, rows1, summary2, rows2, e3res, class_rows):
    # fig3: class-conditional coverage at alpha=0.10
    target = 0.90
    rec_n = [s for s in summary1 if s["alpha"] == 0.10 and s["method"] == "naive"][0]
    rec_a = [s for s in summary1 if s["alpha"] == 0.10 and s["method"] == "APS"][0]
    x = np.arange(K)
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.bar(x - 0.2, rec_n["class_cov_mean"], 0.4, label="Split conformal (naive)", color="#378ADD")
    ax.bar(x + 0.2, rec_a["class_cov_mean"], 0.4, label="Split conformal (APS)", color="#D85A30")
    ax.axhline(target, color="#444441", linestyle="--", linewidth=1.2, label="Target 0.90")
    ax.set_xticks(x); ax.set_xlabel("Digit class"); ax.set_ylabel("Empirical coverage")
    ax.set_ylim(0.5, 1.02); ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Class-conditional coverage (alpha = 0.10)")
    savefig(fig, "fig3_class_coverage.png")

    # fig5: prediction-set examples, deliberately mixing singleton and multi-class sets
    Xtr, ytr, Xcal, ycal, Xte, yte = load_split(0)
    clf = fit_model(Xtr, ytr, 0)
    q = conf_quantile(scores_naive(clf.predict_proba(Xcal), ycal), 0.10)
    all_sets = sets_naive(clf.predict_proba(Xte), q)
    multi = [i for i, s in enumerate(all_sets) if len(s) >= 2]
    single = [i for i, s in enumerate(all_sets) if len(s) == 1]
    rp = np.random.default_rng(123)
    pick = list(rp.choice(multi, size=3, replace=False)) + list(rp.choice(single, size=3, replace=False))
    imgs, labs, ex_sets = Xte[pick], yte[pick], [all_sets[i] for i in pick]
    fig, axes = plt.subplots(2, 3, figsize=(6.6, 4.2))
    for i, ax in enumerate(axes.ravel()):
        ax.imshow(imgs[i].reshape(8, 8), cmap="gray_r", vmin=0, vmax=1)
        ax.set_title(f"true={labs[i]}  set={ex_sets[i]}", fontsize=9)
        ax.axis("off")
    fig.suptitle("Prediction sets on clean test digits (alpha = 0.10)", fontsize=10)
    fig.tight_layout()
    savefig(fig, "fig5_examples.png")

    # fig6: coverage and efficiency as functions of alpha (two panels, no label clutter)
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6))
    for name, color, marker in (("naive", "#378ADD", "o"), ("APS", "#D85A30", "s")):
        sub = [s for s in summary1 if s["method"] == name]
        al = [s["alpha"] for s in sub]
        axes[0].errorbar(al, [s["coverage_mean"] for s in sub],
                         yerr=[s["coverage_std"] for s in sub],
                         fmt=marker + "-", color=color, capsize=3, markersize=5, label=name)
        axes[1].errorbar(al, [s["size_mean"] for s in sub],
                         yerr=[s["size_std"] for s in sub],
                         fmt=marker + "-", color=color, capsize=3, markersize=5, label=name)
    axes[0].plot(ALPHAS, [1 - a for a in ALPHAS], "k--", linewidth=1.2, label="target 1-alpha")
    axes[0].set_xlabel("alpha"); axes[0].set_ylabel("Empirical coverage")
    axes[0].set_title("Coverage vs alpha"); axes[0].legend(fontsize=8)
    axes[1].set_xlabel("alpha"); axes[1].set_ylabel("Mean prediction-set size")
    axes[1].set_title("Efficiency vs alpha"); axes[1].legend(fontsize=8)
    fig.suptitle("Coverage and efficiency over alpha (10 repeated splits)", fontsize=10)
    fig.tight_layout()
    savefig(fig, "fig6_tradeoff.png")

    # fig7: baseline comparison
    names = [s["method"] for s in summary2]
    short = ["Softmax\nthreshold", "Temp. +\nthreshold", "Conformal\n(naive)", "Conformal\n(APS)"]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.6))
    cols = ["#888780", "#BA7517", "#378ADD", "#D85A30"]
    axes[0].bar(short, [s["coverage_mean"] for s in summary2],
                yerr=[s["coverage_std"] for s in summary2], color=cols, capsize=3)
    axes[0].axhline(0.90, color="#444441", linestyle="--", linewidth=1.2)
    axes[0].set_ylim(0, 1.12); axes[0].set_ylabel("Coverage")
    axes[0].set_title("Coverage (target 0.90)")
    axes[1].bar(short, [s["size_mean"] for s in summary2],
                yerr=[s["size_std"] for s in summary2], color=cols, capsize=3)
    axes[1].set_ylabel("Mean set size"); axes[1].set_title("Efficiency")
    for ax in axes:
        ax.tick_params(axis="x", labelsize=8)
    fig.suptitle("Confidence baselines vs conformal calibration (alpha = 0.10)", fontsize=10)
    fig.tight_layout()
    savefig(fig, "fig7_baselines.png")

    # fig8: drift trajectory
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    xs = np.arange(e3res["stream_len"])
    ax.plot(xs, e3res["static_sliding"], color="#888780", linewidth=1.8, label="Static calibration")
    ax.plot(xs, e3res["adaptive_sliding"], color="#1D9E75", linewidth=1.8, label="Online adaptive (ACI-style)")
    ax.axhline(e3res["target"], color="#444441", linestyle="--", linewidth=1.2, label="Target 0.90")
    for li, s in enumerate(e3res["noise_levels"]):
        if li:
            ax.axvline(li * (e3res["stream_len"] // 9), color="#B4B2A9", linewidth=0.5, alpha=0.6)
    ax.set_xlabel("Test stream (noise sigma increases left to right, 0 -> 0.60)")
    ax.set_ylabel("Sliding coverage (window = 50)")
    ax.set_ylim(0.10, 1.03); ax.legend(fontsize=8, loc="lower left")
    ax.set_title("Coverage under distribution shift")
    savefig(fig, "fig8_drift.png")

    # fig9: class-coverage deviation heatmap
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    mat = np.array([np.array(rec_n["class_cov_mean"]) - 0.90,
                    np.array(rec_a["class_cov_mean"]) - 0.90])
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-0.25, vmax=0.25, aspect="auto")
    ax.set_yticks([0, 1]); ax.set_yticklabels(["naive", "APS"], fontsize=9)
    ax.set_xticks(range(K)); ax.set_xlabel("Digit class")
    ax.set_title("Class-conditional coverage minus target (alpha = 0.10)")
    for i in range(2):
        for j in range(K):
            ax.text(j, i, f"{mat[i,j]:+.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax, shrink=0.8, label="deviation")
    savefig(fig, "fig9_heatmap.png")

    # fig10 is generated by build_report.py from the verified reference list,
    # so the counts are traceable to actual cited entries rather than a typed-in array.


def main():
    print("Base model accuracy ...", flush=True)
    accs = []
    for s in SEEDS:
        Xtr, ytr, _, _, Xte, yte = load_split(s)
        accs.append(float(fit_model(Xtr, ytr, s).score(Xte, yte)))
    base_acc = {"mean": float(np.mean(accs)), "std": float(np.std(accs, ddof=1))}
    print("E1 ...", flush=True)
    rows1, summary1 = e1()
    print("E2 ...", flush=True)
    rows2, summary2, tempinfo, wil = e2(alpha=0.10)
    print("E3 ...", flush=True)
    res3 = e3()
    print("Figures ...", flush=True)
    make_figures(summary1, rows1, summary2, rows2, res3, None)

    data = {
        "dataset": {"name": "scikit-learn load_digits", "n_samples": 1797, "n_features": 64,
                    "n_classes": 10, "scaling": "pixel / 16.0 into [0,1]",
                    "split": "stratified 50% train pool / 25% calibration / 25% test; "
                             "only 5% of the train pool (~44 samples) is actually used for fitting",
                    "model": "StandardScaler + LogisticRegression(max_iter=3000, C=1.0)",
                    "seeds": SEEDS, "alphas": ALPHAS},
        "base_accuracy": base_acc,
        "e1_summary": summary1, "e1_raw": rows1,
        "e2_summary": summary2, "e2_raw": rows2,
        "e2_temperature": tempinfo, "e2_wilcoxon": wil,
        "e3": {k: v for k, v in res3.items() if k not in
               ("example_images", "clean_images", "static_sliding", "adaptive_sliding", "alphas")},
        "e3_static_sliding": res3["static_sliding"],
        "e3_adaptive_sliding": res3["adaptive_sliding"],
    }
    with open(os.path.join(OUT, "numbers.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "numbers_brief.txt"), "w", encoding="utf-8") as f:
        f.write(f"=== Base model accuracy (10 seeds): {base_acc['mean']:.4f} +/- {base_acc['std']:.4f} ===\n")
        f.write("=== E1 (alpha, method, coverage mean±std, size mean±std) ===\n")
        for s in summary1:
            f.write(f"a={s['alpha']:.2f} {s['method']:6s} cov={s['coverage_mean']:.4f}±{s['coverage_std']:.4f} "
                    f"size={s['size_mean']:.3f}±{s['size_std']:.3f} "
                    f"empty={s['empty_rate_mean']:.3f} "
                    f"max|class dev|={s['class_dev_maxabs']:.4f}\n")
        f.write("\n=== E2 (target 0.90) ===\n")
        for s in summary2:
            f.write(f"{s['method']:28s} cov={s['coverage_mean']:.4f}±{s['coverage_std']:.4f} "
                    f"size={s['size_mean']:.3f}±{s['size_std']:.3f} "
                    f"empty={s['empty_rate_mean']:.3f} "
                    f"|err|={s['coverage_error_mean']:.4f}\n")
        f.write(f"temperature {tempinfo}\nwilcoxon {wil}\n")
        f.write("\n=== E3 ===\n")
        for k in ("static_overall_cov", "adaptive_overall_cov", "static_mean_size",
                  "adaptive_mean_size", "alpha_final", "alpha_min", "alpha_max", "stream_len"):
            f.write(f"{k} = {res3[k]}\n")
        f.write("per level:\n")
        for r in res3["per_level"]:
            f.write(f"  sigma={r['noise_sigma']:.2f} static={r['static_cov']:.3f} "
                    f"adaptive={r['adaptive_cov']:.3f} sizes={r['static_size']:.2f}/{r['adaptive_size']:.2f}\n")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
