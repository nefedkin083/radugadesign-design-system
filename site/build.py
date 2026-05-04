"""Build static site from tokens and principles. Output: site/dist/index.html."""
import pathlib
import yaml
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "tokens"
PRINCIPLES = ROOT / "principles"
DIST = ROOT / "docs"
DIST.mkdir(parents=True, exist_ok=True)


def read_md(path: pathlib.Path) -> str:
    if not path.exists():
        return ""
    md = path.read_text()
    # strip H1 — we render section titles ourselves
    if md.startswith("# "):
        md = md.split("\n", 1)[1].lstrip()
    return markdown.markdown(md, extensions=["fenced_code", "tables"])


def main():
    typo = yaml.safe_load((TOKENS / "typography.yaml").read_text())
    palette = yaml.safe_load((TOKENS / "colors.yaml").read_text())
    typo_md = read_md(PRINCIPLES / "typography.md")
    color_md = read_md(PRINCIPLES / "colors.md")

    primary_font = typo["decision"]["primary"]
    secondary_font = typo["decision"]["secondary"]

    # palette grid HTML
    hues = palette["hues"]
    tones = palette["tone_names"]
    rows = []
    rows.append("<thead><tr><th></th>" + "".join(f"<th>{h}</th>" for h in hues) + "</tr></thead>")
    body = []
    for ti, tone in enumerate(tones):
        cells = [f"<th>{tone}</th>"]
        for h in hues:
            hx = hues[h][ti]
            cells.append(f'<td><span class="sw" style="background:{hx}"></span><code>{hx}</code></td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    rows.append("<tbody>" + "".join(body) + "</tbody>")
    palette_table = "<table class='palette'>" + "".join(rows) + "</table>"

    css = f"""
    :root {{
      --ink: #0a0a0a;
      --paper: #ffffff;
      --muted: #6b6b6b;
      --line: #e6e6e6;
      --soft: #f6f6f6;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: var(--paper); color: var(--ink); }}
    body {{ font-family: 'Geologica', system-ui, sans-serif; font-size: 17px; line-height: 1.5; }}
    .wrap {{ max-width: 1280px; margin: 0 auto; padding: 64px 56px 120px; }}
    header {{ padding-bottom: 32px; border-bottom: 1px solid var(--line); margin-bottom: 56px; }}
    header h1 {{ font-size: 56px; line-height: 1; letter-spacing: -0.02em; margin: 0 0 18px; font-weight: 600; }}
    header p {{ color: var(--muted); margin: 0; max-width: 60ch; font-size: 19px; }}
    section {{ padding: 56px 0; border-bottom: 1px solid var(--line); }}
    section:last-of-type {{ border-bottom: none; }}
    h2 {{ font-size: 36px; letter-spacing: -0.015em; font-weight: 600; margin: 0 0 28px; }}
    h3 {{ font-size: 22px; font-weight: 600; margin: 32px 0 12px; }}
    p {{ margin: 0 0 14px; max-width: 70ch; }}
    a {{ color: var(--ink); }}
    code {{ font-family: 'Iosevka', 'SF Mono', Menlo, monospace; font-size: 14px; background: var(--soft); padding: 2px 6px; border-radius: 4px; }}
    pre {{ background: var(--soft); padding: 18px 22px; border-radius: 8px; overflow-x: auto; line-height: 1.5; }}
    pre code {{ background: none; padding: 0; font-size: 14px; }}
    ul, ol {{ padding-left: 22px; margin: 0 0 14px; }}
    li {{ margin: 6px 0; }}
    .specimen {{ margin-top: 28px; padding: 32px; border: 1px solid var(--line); border-radius: 12px; }}
    .specimen .display {{ font-size: 96px; line-height: 0.95; letter-spacing: -0.025em; font-weight: 600; margin: 0 0 16px; }}
    .specimen .display .light {{ color: #b8b8b8; font-weight: 300; }}
    .specimen .h2-demo {{ font-size: 32px; line-height: 1.1; font-weight: 500; margin: 0 0 14px; letter-spacing: -0.01em; }}
    .specimen .body {{ font-size: 18px; line-height: 1.5; max-width: 56ch; margin: 0 0 18px; }}
    .specimen .alpha {{ font-size: 18px; color: var(--muted); margin: 0; }}
    .secondary {{ font-family: 'Inter', system-ui, sans-serif; }}

    .palette {{ width: 100%; border-collapse: separate; border-spacing: 8px; font-size: 12px; margin-top: 8px; }}
    .palette th {{ font-weight: 500; color: var(--muted); text-align: left; padding: 6px 0; vertical-align: middle; }}
    .palette thead th {{ font-size: 13px; }}
    .palette tbody th {{ width: 80px; }}
    .palette td {{ padding: 0; }}
    .palette td .sw {{ display: block; width: 100%; height: 64px; border-radius: 6px; }}
    .palette td code {{ display: block; background: none; color: var(--muted); padding: 4px 0 0; font-size: 11px; }}

    .meta-row {{ display: flex; gap: 32px; flex-wrap: wrap; color: var(--muted); font-size: 14px; margin-top: 24px; }}
    .meta-row b {{ color: var(--ink); font-weight: 500; }}
    """

    html = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Radugadesign Design System</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geologica:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&family=Iosevka&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Radugadesign Design System</h1>
  <p>Машиночитаемая дизайн-система: токены, принципы, инструкции для агентов. Источник правды для людей и LLM.</p>
</header>

<section id="typography">
  <h2>Типографика</h2>
  <div class="meta-row">
    <span><b>Основной</b> · {primary_font}</span>
    <span><b>Резервный</b> · {secondary_font}</span>
    <span><b>Лицензия</b> · OFL · Google Fonts</span>
  </div>

  <div class="specimen">
    <div class="display">Radugadesign<span class="light">.</span></div>
    <div class="h2-demo">Студия дизайна и медиа-инсталляций</div>
    <div class="body">ROTOR — аудиовизуальная инсталляция, исследующая распространение волн в пространстве и добивающаяся уникального опыта для каждого зрителя.</div>
    <div class="alpha">AaBbCc DdEeFf 01234 АаБбВв ГгДдЕё</div>
  </div>

  <div class="specimen secondary">
    <div class="display">Inter</div>
    <div class="body">Резервный шрифт. Body-текст в плотных интерфейсах, мелкие подписи, табличные данные. Не использовать в заголовках и постерах.</div>
  </div>

  {typo_md}
</section>

<section id="palette">
  <h2>Цветовая палитра</h2>
  <p style="color:var(--muted); max-width: 60ch;">13 hue × 6 tone = 78 цветов. Палитра-инструмент, не идентичность бренда.</p>
  {palette_table}
  {color_md}
</section>

</div>
</body>
</html>
"""
    out = DIST / "index.html"
    out.write_text(html)
    print(f"✓ {out}  {out.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
