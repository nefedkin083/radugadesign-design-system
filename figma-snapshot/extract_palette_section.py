"""Find the curated 'Цветовая палитра' frame on guideline and extract swatches in grid order."""
import json
import pathlib
import urllib.request

FILE_KEY = "Y0MFrD0kbmtrWPkx9gpY1k"
HERE = pathlib.Path(__file__).parent
ENV_FILE = pathlib.Path("/home/superlisa/workspace/.secrets/.env")


def load_token():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("FIGMA_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("FIGMA_TOKEN not found")


def fetch(path, token):
    req = urllib.request.Request(
        f"https://api.figma.com/v1{path}",
        headers={"X-Figma-Token": token},
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode())


def to_hex(c):
    r, g, b = (round(c["r"]*255), round(c["g"]*255), round(c["b"]*255))
    return f"#{r:02X}{g:02X}{b:02X}"


def index_parents(root):
    parent = {}
    by_id = {root["id"]: root}
    stack = [root]
    while stack:
        n = stack.pop()
        for c in n.get("children", []) or []:
            parent[c["id"]] = n["id"]
            by_id[c["id"]] = c
            stack.append(c)
    return parent, by_id


def first_solid(node):
    fills = node.get("fills") or []
    if isinstance(fills, list):
        for f in fills:
            if isinstance(f, dict) and f.get("type") == "SOLID" and "color" in f and f.get("visible", True):
                return f["color"]
    return None


def collect_swatches(node, out):
    abs_box = node.get("absoluteBoundingBox") or {}
    color = first_solid(node)
    if color:
        out.append({
            "id": node.get("id"),
            "name": node.get("name"),
            "type": node.get("type"),
            "x": abs_box.get("x"),
            "y": abs_box.get("y"),
            "w": abs_box.get("width"),
            "h": abs_box.get("height"),
            "hex": to_hex(color),
        })
    for c in node.get("children", []) or []:
        collect_swatches(c, out)


def main():
    token = load_token()
    full = fetch(f"/files/{FILE_KEY}?geometry=paths", token)
    parent, by_id = index_parents(full["document"])

    # find TEXT-nodes named exactly 'Цветовая палитра'
    title_ids = [nid for nid, n in by_id.items() if n.get("name") == "Цветовая палитра" and n.get("type") == "TEXT"]
    print(f"title nodes: {len(title_ids)}")

    # walk up from each title — at each ancestor count square solid swatches; pick best across all
    best = None
    for tid in title_ids:
        cur = tid
        for _ in range(8):
            if cur not in parent:
                break
            cur = parent[cur]
            anc = by_id[cur]
            sw = []
            collect_swatches(anc, sw)
            sizes = [s["w"] for s in sw if s["w"]]
            if not sizes:
                continue
            med = sorted(sizes)[len(sizes)//2]
            squares = [s for s in sw if s["w"] and s["h"] and abs(s["w"]-med) < med*0.4 and abs(s["h"]-s["w"]) < s["w"]*0.4]
            if 50 <= len(squares) <= 200:
                cand = {"id": cur, "type": anc.get("type"), "name": anc.get("name"), "swatches": squares, "title_id": tid}
                if not best or len(squares) > len(best["swatches"]):
                    best = cand

    if not best:
        print("no palette container found")
        return
    print(f"chosen: {best['type']} {best['id']} '{best['name']}'  swatches: {len(best['swatches'])}")

    swatch_grid = best["swatches"]
    sizes = [s["w"] for s in swatch_grid]
    med = sorted(sizes)[len(sizes)//2]

    # snap to grid: cluster y (rows) and x (columns)
    def cluster(vals, tol):
        vs = sorted(vals)
        out = [vs[0]]
        for v in vs[1:]:
            if v - out[-1] > tol:
                out.append(v)
        return out

    rows = cluster([s["y"] for s in swatch_grid], med * 0.4)
    cols = cluster([s["x"] for s in swatch_grid], med * 0.4)
    print(f"grid: {len(rows)} rows × {len(cols)} cols")

    def nearest(v, lst):
        return min(range(len(lst)), key=lambda i: abs(lst[i]-v))

    grid = {}
    for s in swatch_grid:
        ri = nearest(s["y"], rows)
        ci = nearest(s["x"], cols)
        grid.setdefault((ri, ci), []).append(s)

    matrix = []
    for ri in range(len(rows)):
        row = []
        for ci in range(len(cols)):
            cell = grid.get((ri, ci))
            row.append(cell[0]["hex"] if cell else None)
        matrix.append(row)

    out = {
        "source": f"{best['type']} {best['id']} '{best['name']}'",
        "rows": len(rows),
        "cols": len(cols),
        "matrix": matrix,
        "flat": sorted({s["hex"] for s in swatch_grid}),
    }
    (HERE / "palette_grid.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    md = ["# Brand palette grid (extracted from Figma)", ""]
    md.append(f"source: `{out['source']}`  · rows {out['rows']} · cols {out['cols']} · unique {len(out['flat'])}")
    md.append("")
    md.append("## Grid")
    md.append("")
    for row in matrix:
        md.append("| " + " | ".join((c or " · ") for c in row) + " |")
    md.append("")
    md.append("## Unique colors")
    for hx in out["flat"]:
        md.append(f"- `{hx}`")
    (HERE / "palette_grid.md").write_text("\n".join(md))
    print("✓ palette_grid.json + palette_grid.md")


if __name__ == "__main__":
    main()
