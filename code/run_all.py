"""One command to regenerate every table and figure."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["exp_equiv.py", "exp_postprocess.py", "exp_aci.py", "make_tables.py", "make_figures.py"]


def main():
    for step in STEPS:
        path = os.path.join(HERE, step)
        print("[run]", step, flush=True)
        subprocess.run([sys.executable, path], check=True)


if __name__ == "__main__":
    main()
