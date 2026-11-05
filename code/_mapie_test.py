import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from mapie.classification import SplitConformalClassifier

X, y = make_classification(n_samples=8000, n_features=20, n_classes=5, n_informative=12,
                           class_sep=0.8, random_state=0)
Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, test_size=0.5, stratify=y, random_state=0)
Xcal, Xte, ycal, yte = train_test_split(Xtmp, ytmp, test_size=0.5, stratify=ytmp, random_state=0)
clf = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
print("accuracy", round(clf.score(Xte, yte), 4))

for score in ["lac", "aps"]:
    for inc in [True, False, "randomized"]:
        if score == "lac" and inc != True:
            continue
        m = SplitConformalClassifier(estimator=clf, confidence_level=0.90,
                                     conformity_score=score, prefit=True)
        m.conformalize(Xcal, ycal)
        kwargs = {"conformity_score_params": {"include_last_label": inc}} if score == "aps" else {}
        yp, sets = m.predict_set(Xte, **kwargs)
        s = sets[:, :, 0]
        sizes = s.sum(axis=1)
        cov = float(s[np.arange(len(yte)), yte].mean())
        print(score, "include_last_label=", inc, "coverage", round(cov, 4),
              "empty", round(float((sizes == 0).mean()), 4), "size", round(float(sizes.mean()), 3))
