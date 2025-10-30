# fetch_all_from_sitemap_index.py
import os, re, gzip, time, requests
from urllib.parse import urlparse, unquote
from pathlib import Path

INDEX_URL = "https://thebreastformstore.com/sitemap_index.xml"
OUTPUT_DIR = "sitemaps"
RECURSIVE = True     # True = segue sitemap_index aninhado; False = só os filhos do índice principal
SLEEP = 0.2
HEADERS = {"User-Agent": "Mozilla/5.0 (SitemapFetcher/1.0)"}
TIMEOUT = 30

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def safe_name(url: str) -> str:
    p = urlparse(url)
    tail = unquote(os.path.basename(p.path)) or "sitemap.xml"
    if p.query:
        # evita nomes repetidos quando há query (?from=...&to=...)
        q = re.sub(r"[^a-zA-Z0-9]+", "-", p.query)[:40].strip("-")
        root, ext = os.path.splitext(tail)
        tail = f"{root}__{q}{ext or '.xml'}"
    # normaliza
    if not tail.endswith((".xml", ".gz", ".xml.gz")):
        tail += ".xml"
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", tail)

def get(url: str) -> bytes:
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.content

def is_index(xml_bytes: bytes) -> bool:
    # simples: verifica a tag <sitemapindex
    return b"<sitemapindex" in xml_bytes.lower()

def extract_locs(xml_bytes: bytes) -> list[str]:
    # regex robusta contra namespaces/formatacao
    text = xml_bytes.decode("utf-8", "ignore")
    return re.findall(r"<loc>\s*(.*?)\s*</loc>", text, flags=re.I | re.S)

def save_file(url: str, content: bytes) -> str:
    name = safe_name(url)
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "wb") as f:
        f.write(content)
    # se for .gz, descompacta ao lado
    if path.endswith(".gz"):
        out_xml = path[:-3] if path.endswith(".xml.gz") else path[:-3] + ".xml"
        with gzip.open(path, "rb") as gz, open(out_xml, "wb") as out:
            out.write(gz.read())
        return out_xml
    return path

def crawl_index(index_url: str, visited: set[str] | None = None):
    if visited is None:
        visited = set()
    if index_url in visited:
        return
    visited.add(index_url)

    print(f"[INDEX] {index_url}")
    time.sleep(SLEEP)
    idx_bytes = get(index_url)
    idx_path = save_file(index_url, idx_bytes)
    locs = extract_locs(idx_bytes)
    print(f"  ↳ encontrados {len(locs)} sitemaps")

    for loc in locs:
        try:
            time.sleep(SLEEP)
            b = get(loc)
            saved = save_file(loc, b)
            print(f"  [OK] {loc} → {saved}")

            # Se quiser seguir índices aninhados
            if RECURSIVE and is_index(b):
                crawl_index(loc, visited)
        except Exception as e:
            print(f"  [ERRO] {loc}: {e}")

if __name__ == "__main__":
    crawl_index(INDEX_URL)
    print(f"\n✅ Concluído. Arquivos em ./{OUTPUT_DIR}")
