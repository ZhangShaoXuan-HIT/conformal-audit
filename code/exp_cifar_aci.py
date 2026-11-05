"""CIFAR-10 audit C: the alpha_t update is not ACI, under image corruption.

Stream: 2,000 test images in 20 blocks of 100, Gaussian pixel noise ramping
from 0 to 0.40. Calibration is clean. Three seeds, two updates, two step sizes.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common as C  # noqa: E402

ALPHA = 0.10
SEEDS = [0, 1, 2]
GAMMAS = [0.02, 0.05]
N_BLOCKS = 20
BLOCK = 100
MAX_SIGMA = 0.40
STRENGTH = 1.0
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


def record(update, gamma, seed, hits, sizes, alphas):
    hits = np.asarray(hits, float)
    sizes = np.asarray(sizes, float)
    alphas = np.asarray(alphas, float)
    block_cov = [float(hits[i * BLOCK:(i + 1) * BLOCK].mean()) for i in range(N_BLOCKS)]
    block_size = [float(sizes[i * BLOCK:(i + 1) * BLOCK].mean()) for i in range(N_BLOCKS)]
    alpha_block = [float(alphas[(i + 1) * BLOCK - 1]) for i in range(N_BLOCKS)]
    w = 100
    sliding = np.convolve(hits, np.ones(w) / w, mode="valid")[::50].tolist()
    clip = float(np.mean((alphas <= 0.001 + 1e-9) | (alphas >= 0.999 - 1e-9)))
    return C.make_row(
        dataset="cifar10", model="logreg_resnet18", strength=STRENGTH, n_train=30000,
        n_cal=N_CAL, n_test=int(len(hits)), alpha=ALPHA, score="naive",
        postprocess="raw", seed=seed, schedule="noise_ramp", update=update, gamma=gamma,
        coverage=float(hits.mean()), size=float(sizes.mean()),
        block_cov=block_cov, block_size=block_size, alpha_block=alpha_block,
        alpha_final=float(alphas[-1]), alpha_min=float(alphas.min()),
        alpha_max=float(alphas.max()), clip_fraction=clip,
        frac_sets_ge9=float(np.mean(sizes >= 9)), sliding_cov=sliding,
    )


def run():
    imgs, labels = load_images()
    Xtr_feat, ytr, Xte_feat, yte = C.load_cifar_features()
    assert np.array_equal(labels, yte), "image order and feature order differ"

    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Identity()
    model.eval().to(device)

    rows = []
    sigmas = np.linspace(0.0, MAX_SIGMA, N_BLOCKS)
    for seed in SEEDS:
        pool, cal = C.make_splits_cifar(ytr, seed, n_cal=N_CAL)
        clf, _ = C.fit_head(Xtr_feat[pool], ytr[pool], STRENGTH, seed)
        Pcal = clf.predict_proba(Xtr_feat[cal])
        ycal = ytr[cal]
        sc = 1.0 - Pcal[np.arange(len(ycal)), ycal]
        sorted_sc = np.sort(sc)
        q_static = q_at(sorted_sc, ALPHA)

        rng = np.random.default_rng(seed + 41)
        per_class = (BLOCK * N_BLOCKS) // 10
        idx = np.concatenate([rng.choice(np.flatnonzero(labels == c), per_class, replace=False) for c in range(10)])
        rng.shuffle(idx)
        xs = []
        for b in range(N_BLOCKS):
            xb = imgs[idx[b * BLOCK:(b + 1) * BLOCK]]
            xb = torch.clamp(xb + torch.randn_like(xb) * float(sigmas[b]), 0.0, 1.0)
            xs.append(xb)
        P = clf.predict_proba(feature_batch(model, torch.cat(xs)))
        ystream = labels[idx]

        static_sets = C.build_sets("naive", P, q_static)
        static_hit = C.hits(static_sets, ystream)
        static_size = np.array([len(s) for s in static_sets], float)
        rows.append(record("static", None, seed, static_hit, static_size, np.full(len(ystream), ALPHA)))

        for gamma in GAMMAS:
            for update in ("fixed", "buggy"):
                a = ALPHA
                hits = np.empty(len(ystream))
                sizes = np.empty(len(ystream))
                alphas = np.empty(len(ystream))
                for i in range(len(ystream)):
                    q = q_at(sorted_sc, a)
                    st = C.build_sets("naive", P[i:i + 1], q)[0]
                    hit = int(ystream[i] in st)
                    hits[i] = hit
                    sizes[i] = len(st)
                    alphas[i] = a
                    err = 1 - hit
                    a = a + gamma * ((ALPHA if update == "fixed" else a) - err)
                    a = float(np.clip(a, 0.001, 0.999))
                rows.append(record(update, gamma, seed, hits, sizes, alphas))
        print("seed", seed, "done", flush=True)

    C.save_results(os.path.join(ROOT, "results", "aci_cifar.json"), rows, "exp_cifar_aci.py",
                   checks={"seeds": SEEDS, "gammas": GAMMAS, "max_sigma": MAX_SIGMA,
                           "n_blocks": N_BLOCKS, "block": BLOCK})
    print("rows", len(rows), flush=True)
    for update in ("static", "fixed", "buggy"):
        sub = [r for r in rows if r["update"] == update]
        if update != "static":
            sub = [r for r in sub if abs(r["gamma"] - 0.02) < 1e-12]
        print(update, "cov", round(float(np.mean([r["coverage"] for r in sub])), 3),
              "size", round(float(np.mean([r["size"] for r in sub])), 2),
              "alpha", round(float(np.mean([r["alpha_final"] for r in sub])), 4), flush=True)


if __name__ == "__main__":
    run()
