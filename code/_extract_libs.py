import glob, os, tarfile, zipfile
ROOT = r"C:\Users\18372\Documents\cp-audit"
LIB = os.path.join(ROOT, "_libs")
SRC = os.path.join(LIB, "src")
os.makedirs(SRC, exist_ok=True)
for p in glob.glob(os.path.join(LIB, "*.whl")):
    with zipfile.ZipFile(p) as z:
        z.extractall(SRC)
    print("whl", os.path.basename(p))
for p in glob.glob(os.path.join(LIB, "*.tar.gz")):
    with tarfile.open(p) as t:
        t.extractall(SRC)
    print("tgz", os.path.basename(p))
for d in sorted(os.listdir(SRC)):
    print("dir", d)
