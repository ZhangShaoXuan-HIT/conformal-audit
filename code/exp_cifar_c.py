"""CIFAR-10-C style drift audit.

Five corruption types, three severities, 1,000 images per block. The head and the
calibration are clean; the stream is corrupted. Static, fixed-alpha ACI and
alpha_t ACI are compared at gamma = 0.02.
"""
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from imagecorruptions import corrupt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common as C  # noqa: E402

ALPHA = 0.10
GAMMA = 0.02
SEVERITIES = [1, 3, 5]
CORRUPTIONS = ["gaussian_noise", "defocus_blur", "contrast", "brightness", "jpeg_compression"]
N_PER_SEV = 1000
SEEDS = [0, 1, 2]
N_CAL = 2000
device = "cuda" if torch.cuda.is_available() else "cpu"


def q_at(sorted_scores, alpha):
    n = len(sorted_scores)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = max(1, min(k, n))
    return float(sorted_scores[k - 1])


def load_images():
    tf = transforms.Compose([transforms.ToTensor()])
    ds = datasets.ImageFolder(os.path.join(ROOT, "data", "cifar10", "test"), transform=tf)
    loader = DataLoader(ds, batch_size=10000, shuffle=False, num_workers=0)
    imgs, labels = next(iter(loader))
    return imgs, labels.numpy()


def feature_batch(model, x):
    x = F.interpolate(x, size=224, mode="bilinear", align_corners=False)
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    x = (x - mean) / std
    out = []
    with torch.no_grad():
        for i in range(0, len(x), 256):
            out.append(model(x[i:i + 256].to(device)).cpu())
    return torch.cat(out).numpy()


def record(corruption, update, seed, hits, sizes, alphas, gamma):
    hits = np.asarray(hits, float)
    sizes = np.asarray(sizes, float)
    alphas = np.asarray(alphas, float)
    block_cov = [float(hits[i * N_PER_SEV:(i + 1) * N_PER_SEV].mean()) for i in range(3)]
    block_size = [float(sizes[i * N_PER_SEV:(i + 1) * N_PER_SEV].mean()) for i in range(3)]
    clip = float(np.mean((alphas <= 0.001 + 1e-9) | (alphas >= 0.999 - 1e-9)))
    return C.make_row(
        dataset="cifar10_c", model="logreg_resnet18", strength=1.0, n_train=30000,
        n_cal=N_CAL, n_test=int(len(hits)), alpha=ALPHA, score="naive",
        postprocess="raw", seed=seed, schedule=corruption, update=update, gamma=gamma,
        coverage=float(hits.mean()), size=float(sizes.mean()),
        block_cov=block_cov, block_size=block_size,
        alpha_final=float(alphas[-1]), alpha_min=float(alphas.min()),
        alpha_max=float(alphas.max()), clip_fraction=clip,
        frac_sets_ge9=float(np.mean(sizes >= 9)),
    )


def run():
    imgs, labels = load_images()
    Xtr, ytr, Xte, yte = C.load_cifar_features()

    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Identity()
    model.eval().to(device)

    rng = np.random.default_rng(7)
    idx = np.concatenate([rng.choice(np.flatnonzero(labels == c), N_PER_SEV // 10, replace=False) for c in range(10)])
    rng.shuffle(idx)

    pool, cal = C.make_splits_cifar(ytr, 0, n_cal=N_CAL)
    clf, _ = C.fit_head(Xtr[pool], ytr[pool], 1.0, 0)
    Pcal = clf.predict_proba(Xtr[cal])
    ycal = ytr[cal]
    sc = 1.0 - Pcal[np.arange(len(ycal)), ycal]
    sorted_sc = np.sort(sc)
    q_static = q_at(sorted_sc, ALPHA)

    rows = []
    for corruption in CORRUPTIONS:
        feats = []
        for sev in SEVERITIES:
            batch = []
            for i in idx:
                arr = (imgs[i].permute(1, 2, 0).numpy() * 255).astype(np.uint8)
                arr = corrupt(arr, corruption_name=corruption, severity=sev)
                batch.append(torch.from_numpy(arr).permute(2, 0, 1).float() / 255.0)
            feats.append(feature_batch(model, torch.stack(batch)))
        P = clf.predict_proba(np.concatenate(feats))
        ystream = np.tile(labels[idx], 3)
        print("features", corruption, P.shape, flush=True)

        for seed in SEEDS:
            rng2 = np.random.default_rng(seed + 101)
            order = np.concatenate([rng2.permutation(np.arange(b * N_PER_SEV, (b + 1) * N_PER_SEV)) for b in range(3)])
            Pp = P[order]
            ys = ystream[order]
            static_sets = C.build_sets("naive", Pp, q_static)
            sh = C.hits(static_sets, ys)
            ss = np.array([len(s) for s in static_sets], float)
            rows.append(record(corruption, "static", seed, sh, ss, np.full(len(ys), ALPHA), None))
            for update in ("fixed", "buggy"):
                a = ALPHA
                hits = np.empty(len(ys))
                sizes = np.empty(len(ys))
                alphas = np.empty(len(ys))
                for i in range(len(ys)):
                    q = q_at(sorted_sc, a)
                    st = C.build_sets("naive", Pp[i:i + 1], q)[0]
                    hit = int(ys[i] in st)
                    hits[i] = hit
                    sizes[i] = len(st)
                    alphas[i] = a
                    err = 1 - hit
                    a = a + GAMMA * ((ALPHA if update == "fixed" else a) - err)
                    a = float(np.clip(a, 0.001, 0.999))
                rows.append(record(corruption, update, seed, hits, sizes, alphas, GAMMA))
        print("done", corruption, flush=True)

    C.save_results(os.path.join(ROOT, "results", "aci_cifar_c.json"), rows, "exp_cifar_c.py",
                   checks={"corruptions": CORRUPTIONS, "severities": SEVERITIES,
                           "n_per_sev": N_PER_SEV, "seeds": SEEDS, "gamma": GAMMA})
    print("rows", len(rows), flush=True)
    for update in ("static", "fixed", "buggy"):
        sub = [r for r in rows if r["update"] == update]
        print(update, "cov", round(float(np.mean([r["coverage"] for r in sub])), 3),
              "size", round(float(np.mean([r["size"] for r in sub])), 2), flush=True)


if __name__ == "__main__":
    run()
