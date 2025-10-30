import os, gzip, csv, re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(".")
urls = set()

def read_xml_bytes(p: Path) -> bytes:
    if p.suffix == ".gz":
        with gzip.open(p, "rb") as f: return f.read()
    return p.read_bytes()

def extract_urls_from_xml(data: bytes):
    # tenta XML normal; se quebrar, faz fallback com regex simples
    try:
        root = ET.fromstring(data)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        # pega <url><loc> e também <sitemap><loc> (caso seja index)
        for tag in ("{http://www.sitemaps.org/schemas/sitemap/0.9}loc", "loc"):
            for loc in root.findall(f".//{tag}"):
                if loc.text: yield loc.text.strip()
        for loc in root.findall(".//sm:loc", ns):
            if loc.text: yield loc.text.strip()
    except Exception:
        for m in re.finditer(rb"<loc>(.*?)</loc>", data, flags=re.I|re.S):
            try: yield m.group(1).decode().strip()
            except: pass

for p in ROOT.rglob("*"):
    if p.is_file() and (p.suffix in [".xml"] or p.suffixes[-2:]==[".xml",".gz"] or p.suffix==".gz"):
        for u in extract_urls_from_xml(read_xml_bytes(p)):
            if u: urls.add(u)

urls = sorted(urls)
# TXT
Path("all_urls.txt").write_text("\n".join(urls), encoding="utf-8")
# CSV com uma coluna 'url'
with open("all_urls.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["url"]); w.writerows([[u] for u in urls])

print(f"OK! {len(urls)} URLs unificadas em all_urls.txt e all_urls.csv")
