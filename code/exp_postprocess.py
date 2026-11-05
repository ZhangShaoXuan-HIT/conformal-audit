"""Audit B: non-empty post-processing inflates coverage and set size.

Phase 1. Grid: score in {naive, aps_rand, aps_det, raps} x alpha x n_cal.
For every cell, record coverage/size/empty before and after force_nonempty.
Output: results/postprocess_digits.json
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402


def run():
    raise SystemExit("phase 1: not implemented yet")


if __name__ == "__main__":
    run()
