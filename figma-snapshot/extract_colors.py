"""Extract solid-fill colors from the Figma file. Aggregates global + per-page."""
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
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode())


def to_hex(c, opacity=1.0):
    r = round(c["r"] * 255)
    g = round(c["g"] * 255)
    b = round(c["b"] * 255)
    a = round(c.get("a", 1.0) * opacity * 255)
    if a >= 255:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


def walk(node, counter, samples):
    fills = node.get("fills") or []
    if isinstance(fills, list):
        for f in fills:
            if not isinstance(f, dict):
                continue
            if f.get("visible") is False:
                continue
            if f.get("type") == "SOLID" and "color" in f:
                hx = to_hex(f["color"], f.get("opacity", 1.0))
                counter[hx] += 1
                if len(samples[hx]) < 5:
                    name = node.get("name", "")[:60]
                    samples[hx].add(f"{node.get('type')}:{name}")
    for child in node.get("children", []) or []:
        walk(child, counter, samples)


def main():
    token = load_token()
    print("→ /files/{key}?geometry=paths")
    full = fetch(f"/files/{FILE_KEY}?geometry=paths", token)

    pages = full["document"]["children"]
    global_counter = collections.Counter()
    global_samples = collections.defaultdict(set)
    per_page = {}
    for p in pages:
        c = collections.Counter()
        s = collections.defaultdict(set)
        walk(p, c, s)
        per_page[p["name"]] = c
        # merge into global
        for k, v in c.items():
            global_counter[k] += v
            global_samples[k] |= s[k]

    # YAML token output
    def top_list(counter, n=40):
        return [{"hex": hx, "count": cnt} for hx, cnt in counter.most_common(n)]

    out = {
        "version": "0.1",
        "status": "draft (auto-extracted, awaiting curation)",
        "source": "figma rd4-C",
        "method": "solid fills aggregation",
        "guideline_top": top_list(per_page.get("guideline", collections.Counter())),
        "whole_file_top": top_list(global_counter),
    }

    import yaml
    yaml_path = pathlib.Path("/home/superlisa/workspace/radugadesign-design-system/tokens/colors.yaml")
    yaml_path.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True))
    print(f"✓ tokens/colors.yaml")

    # Markdown summary
    lines = ["# Colors in Figma file rd4-C", ""]
    lines.append(f"Total unique colors (global): **{len(global_counter)}**")
    lines.append("")
    lines.append("## Top 40 across the whole file")
    lines.append("")
    for hx, n in global_counter.most_common(40):
        ex = ", ".join(sorted(global_samples[hx])[:3])
        lines.append(f"- `{hx}` — {n}  · examples: {ex}")
    lines.append("")
    lines.append("## Per page (top 12)")
    lines.append("")
    for name, c in per_page.items():
        lines.append(f"### {name}  ({sum(c.values())} fills, {len(c)} unique)")
        for hx, n in c.most_common(12):
            lines.append(f"- `{hx}` — {n}")
        lines.append("")
    (HERE / "colors.md").write_text("\n".join(lines))

    (HERE / "colors.json").write_text(json.dumps({
        "global": global_counter.most_common(),
        "per_page": {k: v.most_common() for k, v in per_page.items()},
    }, indent=2, ensure_ascii=False))
    print("✓ figma-snapshot/colors.md, colors.json")


if __name__ == "__main__":
    main()
