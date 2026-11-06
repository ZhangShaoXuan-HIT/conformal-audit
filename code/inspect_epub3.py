import zipfile, re

p = r"E:\A data-driven single substitution to overcome bias from conventional single substitution for LOD missingness in covariates in least squares regression.epub"
z = zipfile.ZipFile(p)
raw = z.read("EPUB/xhtml/index.xhtml").decode("utf-8", "ignore")

for pat in ["<sup", "CIT", "href=\"#", "ref-link", "citation"]:
    ms = list(re.finditer(pat, raw, re.I))
    print("\nPAT", pat, "count", len(ms))
    for m in ms[:3]:
        print(raw[max(0, m.start()-220):m.start()+260].replace("\n", " "))

# around a known body sentence
i = raw.find("non-detectable")
print("\nBODY AROUND non-detectable\n", raw[max(0,i-600):i+900])
