"""Probe: print parent chain of 'Цветовая палитра' title nodes and their siblings."""
import json
import pathlib
import urllib.request

FILE_KEY = "Y0MFrD0kbmtrWPkx9gpY1k"
ENV_FILE = pathlib.Path("/home/superlisa/workspace/.secrets/.env")


def load_token():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("FIGMA_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")


def fetch(path, token):
    req = urllib.request.Request(f"https://api.figma.com/v1{path}",
                                 headers={"X-Figma-Token": token})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode())


def index(root):
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


def main():
    token = load_token()
    full = fetch(f"/files/{FILE_KEY}?geometry=paths", token)
    parent, by_id = index(full["document"])
    titles = [nid for nid, n in by_id.items() if n.get("name") == "Цветовая палитра" and n.get("type") == "TEXT"]
    for tid in titles:
        chain = []
        cur = tid
        while cur in parent:
            cur = parent[cur]
            chain.append((cur, by_id[cur].get("type"), by_id[cur].get("name"), len(by_id[cur].get("children", []) or [])))
        print(f"\nTITLE {tid} parents:")
        for c in chain:
            print(f"  {c[0]:14s} {c[1]:10s}  children={c[3]:3d}  {c[2][:60]}")
    # for first title's grandparent, list its children
    if titles:
        gp = parent.get(parent.get(titles[0]))
        if gp:
            print(f"\nGrandparent {gp} children:")
            for c in by_id[gp].get("children", [])[:30]:
                bb = c.get("absoluteBoundingBox") or {}
                print(f"  {c.get('id'):14s} {c.get('type'):10s}  w={bb.get('width')!s:6}  h={bb.get('height')!s:6}  {c.get('name','')[:50]}")


if __name__ == "__main__":
    main()
