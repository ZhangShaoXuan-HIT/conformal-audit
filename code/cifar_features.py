"""Cache ResNet-18 penultimate features for CIFAR-10.

Expects the fast.ai PNG layout: data/cifar10/train/<class>/*.png and test/.
Output: data/cifar10_features.npz with Xtr, ytr, Xte, yte.
"""
import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms, models, datasets

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device, flush=True)

tf = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
train = datasets.ImageFolder(os.path.join(DATA, "cifar10", "train"), transform=tf)
test = datasets.ImageFolder(os.path.join(DATA, "cifar10", "test"), transform=tf)
print("data ready", len(train), len(test), train.classes, flush=True)

model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.fc = nn.Identity()
model.eval().to(device)


def extract(ds, name):
    loader = DataLoader(ds, batch_size=256, shuffle=False, num_workers=0, pin_memory=True)
    feats, labels = [], []
    with torch.no_grad():
        for i, (x, y) in enumerate(loader):
            x = x.to(device, non_blocking=True)
            feats.append(model(x).cpu().numpy())
            labels.append(y.numpy())
            if i % 50 == 0:
                print(name, i, flush=True)
    return np.concatenate(feats), np.concatenate(labels)


Xtr, ytr = extract(train, "train")
Xte, yte = extract(test, "test")
path = os.path.join(DATA, "cifar10_features.npz")
np.savez_compressed(path, Xtr=Xtr, ytr=ytr, Xte=Xte, yte=yte)
print("saved", path, Xtr.shape, Xte.shape, Xtr.dtype, flush=True)

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=1.0))
clf.fit(Xtr[:30000], ytr[:30000])
print("linear probe accuracy:", round(float(clf.score(Xte, yte)), 4), flush=True)
