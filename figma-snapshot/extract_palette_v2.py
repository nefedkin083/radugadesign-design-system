"""Extract the curated palette grid from cached guideline_page.json."""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
DATA = json.loads((HERE / "guideline_page.json").read_text())


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
    bb = node.get("absoluteBoundingBox") or {}
    color = first_solid(node)
    if color:
        out.append({
            "id": node["id"], "type": node["type"],
            "x": bb.get("x"), "y": bb.get("y"),
            "w": bb.get("width"), "h": bb.get("height"),
            "hex": to_hex(color),
        })
    for c in node.get("children", []) or []:
        collect_swatches(c, out)


def main():
    root = list(DATA["nodes"].values())[0]["document"]
    parent, by_id = index_parents(root)
    titles = [nid for nid, n in by_id.items() if n.get("name") == "Цветовая палитра" and n.get("type") == "TEXT"]
    print(f"title nodes: {len(titles)}")

    best = None
    for tid in titles:
        cur = tid
        for depth in range(1, 8):
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
            print(f"  ancestor depth {depth} {anc.get('type'):8s} {cur:14s}  total={len(sw)} squares={len(squares)} med={med:.0f}")
            if 60 <= len(squares) <= 120:
                cand = (cur, anc, squares)
                if not best or len(squares) > len(best[2]):
                    best = cand

    if not best:
        print("not found")
        return
    cid, anc, squares = best
    print(f"\nchosen {cid} '{anc.get('name')}' swatches={len(squares)}")

    def cluster(vals, tol):
        vs = sorted(vals)
        out = [vs[0]]
        for v in vs[1:]:
            if v - out[-1] > tol:
                out.append(v)
        return out

    sizes = [s["w"] for s in squares]
    med = sorted(sizes)[len(sizes)//2]
    rows = cluster([s["y"] for s in squares], med*0.4)
    cols = cluster([s["x"] for s in squares], med*0.4)
    print(f"grid {len(rows)} x {len(cols)}")

    def nearest(v, lst):
        return min(range(len(lst)), key=lambda i: abs(lst[i]-v))

    grid = {}
    for s in squares:
        grid[(nearest(s["y"], rows), nearest(s["x"], cols))] = s["hex"]
    matrix = [[grid.get((r, c)) for c in range(len(cols))] for r in range(len(rows))]
    out = {
        "source_node_id": cid,
        "source_name": anc.get("name"),
        "rows": len(rows),
        "cols": len(cols),
        "matrix": matrix,
        "flat": sorted({s["hex"] for s in squares}),
    }
    (HERE / "palette_grid.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    md = ["# Brand palette grid (from Figma 'Цветовая палитра')", ""]
    md.append(f"node `{cid}` · `{anc.get('name')}` · grid {len(rows)} × {len(cols)} · unique {len(out['flat'])}")
    md.append("")
    md.append("## Grid (visual order)")
    md.append("")
    for row in matrix:
        md.append("`" + "  ".join((c or "       ") for c in row) + "`")
    md.append("")
    md.append("## All colors (sorted)")
    for hx in out["flat"]:
        md.append(f"- `{hx}`")
    (HERE / "palette_grid.md").write_text("\n".join(md))
    print("✓ palette_grid.json + palette_grid.md")


if __name__ == "__main__":
    main()
