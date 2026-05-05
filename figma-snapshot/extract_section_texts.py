"""Extract every TEXT inside each guideline section into principles/patterns/<slug>.md."""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
DATA = json.loads((HERE / "guideline_page.json").read_text())
SECTIONS = json.loads((HERE / "guideline_sections.json").read_text())
OUT = pathlib.Path("/home/superlisa/workspace/radugadesign-design-system/principles/patterns")
OUT.mkdir(parents=True, exist_ok=True)


def index(root):
    by_id = {root["id"]: root}
    stack = [root]
    while stack:
        n = stack.pop()
        for c in n.get("children", []) or []:
            by_id[c["id"]] = c
            stack.append(c)
    return by_id


def collect_text(node, out):
    if node.get("type") == "TEXT":
        ch = node.get("characters", "")
        if ch:
            bb = node.get("absoluteBoundingBox") or {}
            out.append({
                "text": ch.strip(),
                "y": bb.get("y", 0),
                "x": bb.get("x", 0),
                "size": (node.get("style") or {}).get("fontSize"),
            })
    for c in node.get("children", []) or []:
        collect_text(c, out)


def main():
    root = list(DATA["nodes"].values())[0]["document"]
    by_id = index(root)
    written = 0
    for s in SECTIONS:
        node = by_id.get(s["id"])
        if not node:
            continue
        texts = []
        collect_text(node, texts)
        # sort top-down, then left-right
        texts.sort(key=lambda t: (round(t["y"]/20)*20, t["x"]))
        if not texts:
            continue
        lines = [
            f"# {s['name']}",
            "",
            f"`figma://{s['id']}` · {s['type']} · {s['w']}×{s['h']}",
            "",
            "## Тексты на слайде",
            "",
        ]
        for t in texts:
            sz = f" *(font {t['size']:.0f})*" if t.get("size") else ""
            line = t["text"].replace("\n", " · ")
            lines.append(f"- {line}{sz}")
        (OUT / f"{s['slug']}.md").write_text("\n".join(lines))
        written += 1
    print(f"wrote {written}/{len(SECTIONS)} principle md files")


if __name__ == "__main__":
    main()
