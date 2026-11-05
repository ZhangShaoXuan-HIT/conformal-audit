"""Phase 2: repeat audits A and B on CIFAR-10.

Two model strengths: linear head on raw pixels, linear head on pretrained
ResNet-18 features. Corruptions for the shift audit: noise, blur, contrast.
Output: results/*_cifar.json
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402


def run():
    raise SystemExit("phase 2: not implemented yet")


if __name__ == "__main__":
    run()
