import zipfile, re, html

p = r"E:\A data-driven single substitution to overcome bias from conventional single substitution for LOD missingness in covariates in least squares regression.epub"
z = zipfile.ZipFile(p)
raw = z.read("EPUB/xhtml/index.xhtml").decode("utf-8", "ignore")
text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
text = re.sub(r"<[^>]+>", " ", text)
text = html.unescape(re.sub(r"\s+", " ", text)).strip()

print("CITATION CONTEXTS")
for m in re.finditer(r"\[\d+(?:\s*[,\-–]\s*\d+)*\]", text):
    s = text[max(0, m.start()-160):m.end()+80]
    print("...", s.replace("\n", " "))
    if m.start() > 12000:
        break

print("\nREFERENCE ENTRIES")
i = text.find("References [1]")
print(text[i:i+2500])
