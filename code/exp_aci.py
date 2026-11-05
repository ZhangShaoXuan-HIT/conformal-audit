"""Audit C: the alpha_t update is not ACI.

Phase 1. Compare three updates on controlled drift streams:
  fixed   alpha_{t+1} = alpha_t + gamma * (alpha - err_t)      (correct)
  buggy   alpha_{t+1} = alpha_t + gamma * (alpha_t - err_t)    (common mistake)
  grid    fixed update over gamma in {0.005, 0.01, 0.02, 0.05}
Report per-block coverage with binomial CIs, mean size, clip fraction.
Output: results/aci_digits.json
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402


def run():
    raise SystemExit("phase 1: not implemented yet")


if __name__ == "__main__":
    run()
