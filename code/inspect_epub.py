import zipfile, re, html, sys

p = r"E:\A data-driven single substitution to overcome bias from conventional single substitution for LOD missingness in covariates in least squares regression.epub"
z = zipfile.ZipFile(p)
print("FILES")
for n in z.namelist():
    print(" ", n)
print("\nTEXT SAMPLES")
for n in z.namelist():
    if not n.lower().endswith((".xhtml", ".html", ".htm")):
        continue
    raw = z.read(n).decode("utf-8", "ignore")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    print("\n---", n, len(text), "---")
    print(text[:1200])
    for kw in ["References", "REFERENCES", "[1]", "1."]:
        i = text.find(kw)
        if i >= 0:
            print("KW", kw, ":", text[max(0, i-200):i+900])
            break
