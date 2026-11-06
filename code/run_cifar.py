"""CIFAR-10 pipeline: audits A, B and C, tables, figures.

Requires torch, torchvision and data/cifar10_features.npz.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["exp_cifar.py", "exp_cifar_c.py", "make_cifar_tables.py", "make_figures.py"]


def main():
    for step in STEPS:
        print("[run]", step, flush=True)
        subprocess.run([sys.executable, os.path.join(HERE, step)], check=True)


if __name__ == "__main__":
    main()
