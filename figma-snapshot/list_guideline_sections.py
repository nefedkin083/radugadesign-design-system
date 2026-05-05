"""List meaningful sections/frames on guideline page from cached dump."""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
DATA = json.loads((HERE / "guideline_page.json").read_text())


def slugify(name: str) -> str:
    s = name.lower().strip()
    # transliterate Russian
    table = {
        "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"yo","ж":"zh","з":"z","и":"i","й":"y",
        "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f",
        "х":"h","ц":"ts","ч":"ch","ш":"sh","щ":"sch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
    }
    s = "".join(table.get(c, c) for c in s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "section"


def main():
    root = list(DATA["nodes"].values())[0]["document"]
    sections = []
    seen_slugs = {}
    for child in root.get("children", []):
        bb = child.get("absoluteBoundingBox") or {}
        w = bb.get("width", 0) or 0
        h = bb.get("height", 0) or 0
        ttype = child.get("type")
        name = child.get("name", "")
        # skip vector/text/group orphans, basic Figma boilerplate
        if ttype not in ("SECTION", "FRAME"):
            continue
        # skip frames that are too small or auto-named
        if ttype == "FRAME" and (w < 1200 or re.match(r"^Frame\s*\d", name)):
            continue
        slug = slugify(name)
        # disambiguate
        if slug in seen_slugs:
            seen_slugs[slug] += 1
            slug = f"{slug}-{seen_slugs[slug]}"
        else:
            seen_slugs[slug] = 1
        sections.append({
            "id": child["id"],
            "type": ttype,
            "name": name,
            "slug": slug,
            "w": int(w),
            "h": int(h),
        })

    out = pathlib.Path(HERE / "guideline_sections.json")
    out.write_text(json.dumps(sections, indent=2, ensure_ascii=False))
    print(f"sections: {len(sections)}")
    for s in sections:
        print(f"  {s['type']:8s} {s['id']:14s} {s['w']}x{s['h']:>6}  {s['name'][:60]}  → {s['slug']}")


if __name__ == "__main__":
    main()
