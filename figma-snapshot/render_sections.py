"""Render all guideline sections via Figma /v1/images, download PNGs."""
import json
import pathlib
import sys
import time
import urllib.request
import urllib.parse

# unbuffered stdout for live progress in background mode
sys.stdout.reconfigure(line_buffering=True)

FILE_KEY = "Y0MFrD0kbmtrWPkx9gpY1k"
HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path("/home/superlisa/workspace/radugadesign-design-system/patterns/guideline")
OUT.mkdir(parents=True, exist_ok=True)
ENV_FILE = pathlib.Path("/home/superlisa/workspace/.secrets/.env")


def load_token():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("FIGMA_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")


def fetch_with_retry(url, headers, timeout=300):
    for attempt in range(8):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (400, 429, 500, 502, 503, 504):
                wait = 30 * (attempt + 1)
                print(f"  {e.code}, sleeping {wait}s")
                time.sleep(wait)
                continue
            raise
    raise SystemExit("rate limited too many times")


def main():
    token = load_token()
    sections = json.loads((HERE / "guideline_sections.json").read_text())
    print(f"sections: {len(sections)}")
    ids = [s["id"] for s in sections]

    # batch by ~30 ids per request to be safe
    id_to_slug = {s["id"]: s["slug"] for s in sections}
    id_to_meta = {s["id"]: s for s in sections}

    headers = {"X-Figma-Token": token}
    url_map = {}
    BATCH = 4
    SCALE = 1
    for i in range(0, len(ids), BATCH):
        batch = ids[i:i+BATCH]
        ids_q = ",".join(batch)
        url = f"https://api.figma.com/v1/images/{FILE_KEY}?ids={ids_q}&format=png&scale={SCALE}"
        print(f"batch {i//BATCH + 1}/{(len(ids)+BATCH-1)//BATCH}: {len(batch)} ids")
        body = fetch_with_retry(url, headers)
        data = json.loads(body)
        if data.get("err"):
            print(f"  err: {data['err']}")
            continue
        for k, v in (data.get("images") or {}).items():
            url_map[k] = v
        time.sleep(8)

    print(f"got urls: {len(url_map)}/{len(ids)}")
    (HERE / "guideline_image_urls.json").write_text(json.dumps(url_map, indent=2))

    # download
    manifest = []
    for nid, img_url in url_map.items():
        if not img_url:
            continue
        slug = id_to_slug[nid]
        meta = id_to_meta[nid]
        png_path = OUT / f"{slug}.png"
        try:
            req = urllib.request.Request(img_url)
            with urllib.request.urlopen(req, timeout=120) as r:
                png_path.write_bytes(r.read())
        except Exception as e:
            print(f"  fail {slug}: {e}")
            continue
        manifest.append({
            "id": nid,
            "name": meta["name"],
            "slug": slug,
            "type": meta["type"],
            "size": [meta["w"], meta["h"]],
            "file": f"patterns/guideline/{slug}.png",
            "bytes": png_path.stat().st_size,
        })
        print(f"  ✓ {slug}.png  {png_path.stat().st_size//1024} KB")

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    total_kb = sum(m["bytes"] for m in manifest) // 1024
    print(f"✓ {len(manifest)} files, total {total_kb} KB")


if __name__ == "__main__":
    main()
