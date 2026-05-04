"""Render the 13×6 brand palette grid as a PNG, mirroring Figma layout."""
import pathlib
import yaml
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
OUT = HERE / "palette.png"
TOKENS = pathlib.Path("/home/superlisa/workspace/radugadesign-design-system/tokens/colors.yaml")

INK = (10, 10, 10)
MUTED = (139, 139, 139)
LINE = (226, 226, 226)
BG = (10, 10, 10)


def font(name, size, wght=400):
    f = ImageFont.truetype(str(FONTS / name), size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def luma(hex_str):
    h = hex_str.lstrip("#")
    r, g, b = (int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    def chan(c): return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055) ** 2.4
    return 0.2126*chan(r) + 0.7152*chan(g) + 0.0722*chan(b)


def main():
    data = yaml.safe_load(TOKENS.read_text())
    hues = data["hues"]
    hue_names = list(hues.keys())
    tones = data["tone_names"]

    cell_w, cell_h = 120, 120
    pad_x, pad_y = 56, 30
    label_w = 88   # left column for tone labels
    label_h = 36   # top row for hue labels
    margin_top = 200
    margin_left = 56
    margin_right = 56
    margin_bottom = 56

    rows, cols = len(tones), len(hue_names)
    grid_w = label_w + cols * cell_w + (cols - 1) * pad_x
    grid_h = label_h + rows * cell_h + (rows - 1) * pad_y
    W = margin_left + grid_w + margin_right
    H = margin_top + grid_h + margin_bottom + 100

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # header
    d.text((margin_left, 60),
           "Цветовая палитра Radugadesign",
           font=font("Geologica.ttf", 44, 600), fill=(255, 255, 255))
    d.text((margin_left, 120),
           "13 hue × 6 tone · 78 цветов · извлечено из Figma rd4-C",
           font=font("Geologica.ttf", 22, 400), fill=(160, 160, 160))

    # hue labels along the top
    for ci, name in enumerate(hue_names):
        x = margin_left + label_w + ci * (cell_w + pad_x)
        d.text((x, margin_top - label_h + 4),
               name,
               font=font("Geologica.ttf", 18, 500),
               fill=(200, 200, 200))

    # tone labels along the left
    for ri, t in enumerate(tones):
        y = margin_top + label_h + ri * (cell_h + pad_y)
        d.text((margin_left, y + cell_h//2 - 12),
               t,
               font=font("Geologica.ttf", 16, 400),
               fill=(140, 140, 140))

    # grid
    for ri, t in enumerate(tones):
        for ci, name in enumerate(hue_names):
            hx = hues[name][ri]
            x = margin_left + label_w + ci * (cell_w + pad_x)
            y = margin_top + label_h + ri * (cell_h + pad_y)
            rgb = tuple(int(hx[i:i+2], 16) for i in (1, 3, 5))
            d.rectangle([x, y, x + cell_w, y + cell_h], fill=rgb)
            text_color = (255, 255, 255) if luma(hx) < 0.4 else (10, 10, 10)
            d.text((x + 8, y + cell_h - 24),
                   hx,
                   font=font("Geologica.ttf", 13, 500),
                   fill=text_color)

    img.save(OUT, optimize=True)
    print(f"✓ {OUT}  {OUT.stat().st_size//1024} KB  {img.size}")
    thumb = img.resize((600, int(img.size[1]*600/img.size[0])), Image.LANCZOS)
    thumb.save(HERE / "palette_thumb.png", optimize=True)


if __name__ == "__main__":
    main()
