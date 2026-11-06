"""One command for the full paper pipeline.

Run with --dry-run to print the steps without executing them.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STEPS = [
    "exp_equiv.py",
    "exp_postprocess.py",
    "exp_aci.py",
    "exp_cifar.py",
    "exp_cifar_c.py",
    "exp_tabular.py",
    "exp_mapie_empty.py",
    "exp_library_runtime.py",
    "exp_cost_perpoint.py",
    "make_tables.py",
    "make_cifar_tables.py",
    "make_tabular_table.py",
    "make_cost_table.py",
    "make_fig1.py",
    "make_figures.py",
    "build_references.py",
]


def main():
    dry = "--dry-run" in sys.argv
    steps = list(STEPS)
    if not os.path.exists(os.path.join(ROOT, "data", "cifar10_features.npz")):
        steps.insert(0, "cifar_features.py")
    for step in steps:
        print("[run]", step, flush=True)
        if dry:
            continue
        subprocess.run([sys.executable, os.path.join(HERE, step)], check=True)


if __name__ == "__main__":
    main()
