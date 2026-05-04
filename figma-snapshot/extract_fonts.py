"""Extract every TEXT node's font family/style/weight from the Figma file."""
import collections
import json
import pathlib
import urllib.request

FILE_KEY = "Y0MFrD0kbmtrWPkx9gpY1k"
HERE = pathlib.Path(__file__).parent
ENV_FILE = pathlib.Path("/home/superlisa/workspace/.secrets/.env")


def load_token() -> str:
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("FIGMA_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("FIGMA_TOKEN not found")


def fetch(path: str, token: str) -> dict:
    req = urllib.request.Request(
        f"https://api.figma.com/v1{path}",
        headers={"X-Figma-Token": token},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode())


def walk(node, out):
    if node.get("type") == "TEXT":
        st = node.get("style", {}) or {}
        out.append((
            st.get("fontFamily"),
            st.get("fontPostScriptName"),
            st.get("fontWeight"),
            st.get("fontSize"),
            st.get("italic", False),
        ))
    for child in node.get("children", []) or []:
        walk(child, out)


def main():
    token = load_token()
    print("→ /files/{key}?geometry=paths (full tree, no geometry)")
    full = fetch(f"/files/{FILE_KEY}?geometry=paths", token)
    out = []
    walk(full["document"], out)
    print(f"TEXT nodes: {len(out)}")

    fams = collections.Counter(t[0] for t in out if t[0])
    posts = collections.Counter((t[0], t[1], t[2]) for t in out if t[0])

    lines = ["# Fonts in Figma file rd4-C", ""]
    lines.append(f"Total TEXT nodes: **{len(out)}**")
    lines.append("")
    lines.append("## Font families by usage")
    lines.append("")
    for fam, n in fams.most_common():
        lines.append(f"- `{fam}` — {n}")
    lines.append("")
    lines.append("## Family + PostScript + weight (top 30)")
    lines.append("")
    for (fam, ps, w), n in posts.most_common(30):
        lines.append(f"- `{fam}` / `{ps}` / weight {w} — {n}")
    (HERE / "fonts.md").write_text("\n".join(lines))
    print("✓ wrote fonts.md")
    # Compact JSON for downstream
    (HERE / "fonts.json").write_text(json.dumps({
        "families": fams.most_common(),
        "variants": [(*k, v) for k, v in posts.most_common()],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
