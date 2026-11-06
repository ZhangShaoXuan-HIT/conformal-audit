"""Runtime library audit: MAPIE, puncc, crepes, coverforest.

Same five-class synthetic data and alpha for all libraries. Records raw empty
rate, coverage and set size, then the forced coverage after inserting argmax.
"""
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

ROOT = r"C:\Users\18372\Documents\cp-audit"
OUT = os.path.join(ROOT, "results", "library_runtime.json")

X, y = make_classification(n_samples=8000, n_features=20, n_classes=5,
                           n_informative=12, class_sep=0.8, random_state=0)
X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=0.5, stratify=y, random_state=0)
X_cal, X_test, y_cal, y_test = train_test_split(X_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=0)
clf = LogisticRegression(max_iter=2000).fit(X_train, y_train)
P_test = clf.predict_proba(X_test)
argmax = P_test.argmax(axis=1)
n, K = len(y_test), P_test.shape[1]
print("accuracy", round(float((argmax == y_test).mean()), 4), "n_test", n, flush=True)


def norm_sets(sets, n, K):
    if isinstance(sets, np.ndarray):
        if sets.ndim == 3:
            sets = sets[:, :, 0]
        if sets.dtype == bool:
            return sets
        vals = np.unique(sets)
        if sets.shape == (n, K) and set(vals.tolist()).issubset({0, 1}):
            return sets.astype(bool)
        out = np.zeros((n, K), bool)
        for i in range(n):
            out[i, np.asarray(sets[i]).astype(int).ravel()] = True
        return out
    out = np.zeros((n, K), bool)
    for i, s in enumerate(sets):
        arr = np.asarray(s).ravel()
        if arr.size == 0:
            continue
        if arr.dtype == bool and arr.size == K:
            out[i] = arr
        elif np.issubdtype(arr.dtype, np.integer):
            out[i, arr.astype(int)] = True
    return out


def measure(sets):
    s = norm_sets(sets, n, K)
    cov = float(s[np.arange(n), y_test].mean())
    size = float(s.sum(axis=1).mean())
    empty = float((s.sum(axis=1) == 0).mean())
    f = s.copy()
    for i in range(n):
        if not f[i].any():
            f[i, argmax[i]] = True
    return {"coverage": cov, "empty_rate": empty, "mean_size": size,
            "forced_coverage": float(f[np.arange(n), y_test].mean()),
            "forced_size": float(f.sum(axis=1).mean())}


rows = []
def add(library, setting, result, error=None):
    row = {"library": library, "setting": setting, "n_test": n, "error": error}
    if result:
        row.update(result)
    rows.append(row)
    print(library, "|", setting, "|", error if error else
          "cov %.3f empty %.3f size %.2f forced %.3f" % (
              result["coverage"], result["empty_rate"], result["mean_size"], result["forced_coverage"]), flush=True)


# MAPIE
try:
    from mapie.classification import SplitConformalClassifier
    import mapie
    for score, inc in [("lac", True), ("aps", True), ("aps", False), ("aps", "randomized")]:
        m = SplitConformalClassifier(estimator=clf, confidence_level=0.90,
                                     conformity_score=score, prefit=True, random_state=0)
        m.conformalize(X_cal, y_cal)
        kwargs = {"conformity_score_params": {"include_last_label": inc}} if score == "aps" else {}
        _, sets = m.predict_set(X_test, **kwargs)
        add("MAPIE", "%s include_last_label=%s" % (score, inc), measure(sets))
except Exception as e:
    add("MAPIE", "all", None, "%s: %s" % (type(e).__name__, e))

# puncc
try:
    from deel.puncc.classification import LAC as PunccLAC, APS as PunccAPS
    from deel.puncc.api.prediction import BasePredictor

    class SkPredictor(BasePredictor):
        def __init__(self, model, is_trained=True, **kwargs):
            super().__init__(model, is_trained=is_trained, **kwargs)
        def predict(self, X, **kwargs):
            return self.model.predict_proba(X)

    pred = SkPredictor(clf)
    cp = PunccLAC(pred, train=False)
    cp.fit(X_fit=X_train, y_fit=y_train, X_calib=X_cal, y_calib=y_cal)
    _, sets = cp.predict(X_test, alpha=0.10)
    add("puncc", "LAC", measure(sets))
    for rand in [True, False]:
        cp = PunccAPS(pred, train=False, rand=rand)
        cp.fit(X_fit=X_train, y_fit=y_train, X_calib=X_cal, y_calib=y_cal)
        _, sets = cp.predict(X_test, alpha=0.10)
        add("puncc", "APS rand=%s" % rand, measure(sets))
except Exception as e:
    add("puncc", "all", None, "%s: %s" % (type(e).__name__, e))

# crepes
try:
    from crepes import WrapClassifier
    w = WrapClassifier(clf)
    w.fit(X_train, y_train)
    w.calibrate(X_cal, y_cal)
    p = np.asarray(w.predict_p(X_test, smoothing=False))
    sets = p >= 0.10
    add("crepes", "LAC (hinge) p>=alpha, no smoothing", measure(sets))
except Exception as e:
    add("crepes", "all", None, "%s: %s" % (type(e).__name__, e))

# coverforest
try:
    import sklearn.tree._tree as _tree
    if not hasattr(_tree, "DOUBLE"):
        _tree.DOUBLE = np.float64
    if not hasattr(_tree, "DTYPE"):
        _tree.DTYPE = np.float32
    from sklearn.ensemble._forest import ForestClassifier
    _orig_validate = ForestClassifier._validate_y_class_weight
    def _patched_validate(self, y, sample_weight=None):
        return _orig_validate(self, y, sample_weight)
    ForestClassifier._validate_y_class_weight = _patched_validate
    from coverforest import CoverForestClassifier
    for allow in [True, False]:
        cf = CoverForestClassifier(n_estimators=10, method="split",
                                   allow_empty_sets=allow, random_state=0)
        cf.fit(X_train, y_train, alpha=0.10, calib_size=0.3, valid_size=0.3)
        _, sets = cf.predict(X_test, alpha=0.10, binary_output=True)
        add("coverforest", "allow_empty_sets=%s" % allow, measure(sets))
except Exception as e:
    add("coverforest", "all", None, "%s: %s" % (type(e).__name__, e))

versions = {}
for name in ["mapie", "torchcp", "puncc", "crepes", "coverforest"]:
    try:
        versions[name] = __import__(name).__version__
    except Exception:
        versions[name] = None
payload = {"alpha": 0.10, "accuracy": float((argmax == y_test).mean()),
           "dataset": "make_classification 5 classes, 8000 samples", "versions": versions,
           "rows": rows}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1)
print("saved", OUT)
