"""Dump Figma file rd4-C structure and styles to JSON files.

Usage: python dump.py
Reads FIGMA_TOKEN from workspace/.secrets/.env.
"""
import json
import os
import pathlib
import sys
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def main():
    token = load_token()

    print("→ /files/{key}?depth=2 (pages + top frames)")
    shallow = fetch(f"/files/{FILE_KEY}?depth=2", token)
    (HERE / "file_shallow.json").write_text(
        json.dumps(shallow, indent=2, ensure_ascii=False)
    )

    print("→ /files/{key}/styles")
    styles = fetch(f"/files/{FILE_KEY}/styles", token)
    (HERE / "styles.json").write_text(
        json.dumps(styles, indent=2, ensure_ascii=False)
    )

    print("→ /files/{key}/components")
    components = fetch(f"/files/{FILE_KEY}/components", token)
    (HERE / "components.json").write_text(
        json.dumps(components, indent=2, ensure_ascii=False)
    )

    pages = shallow["document"]["children"]
    summary = [
        f"# Figma snapshot — {shallow.get('name', FILE_KEY)}",
        "",
        f"- last_modified: `{shallow.get('lastModified')}`",
        f"- version: `{shallow.get('version')}`",
        f"- pages: {len(pages)}",
        f"- styles: {len(styles.get('meta', {}).get('styles', []))}",
        f"- components: {len(components.get('meta', {}).get('components', []))}",
        "",
        "## Pages",
        "",
    ]
    for page in pages:
        frames = page.get("children") or []
        summary.append(f"### {page['name']}  (`{page['id']}`)")
        summary.append(f"top-level nodes: {len(frames)}")
        summary.append("")
        for fr in frames[:50]:
            summary.append(f"- {fr.get('type')}: {fr.get('name')} (`{fr.get('id')}`)")
        if len(frames) > 50:
            summary.append(f"- … +{len(frames) - 50} more")
        summary.append("")

    (HERE / "SUMMARY.md").write_text("\n".join(summary))
    print("✓ wrote file_shallow.json, styles.json, components.json, SUMMARY.md")


if __name__ == "__main__":
    main()
