"""Render font comparison PNG via Pillow + local variable fonts."""
import pathlib
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
OUT = HERE / "font_comparison.png"

INK = (10, 10, 10)
MUTED = (139, 139, 139)
LIGHT = (180, 180, 180)
LINE = (226, 226, 226)

W = 1800
PAD = 72


def vfont(file: str, size: int, wght: float | None = None):
    f = ImageFont.truetype(str(FONTS / file), size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def draw_section(d: ImageDraw.ImageDraw, y0: int, font_file: str, label: str, note: str, blurb: str) -> int:
    # meta row
    f_meta = vfont("Geologica.ttf", 22, 600)
    f_note = vfont("Geologica.ttf", 18, 400)
    d.text((PAD, y0), label, font=f_meta, fill=INK)
    note_w = text_w(d, note, f_note)
    d.text((W - PAD - note_w, y0 + 4), note, font=f_note, fill=MUTED)
    y0 += 36
    d.line([(PAD, y0), (W - PAD, y0)], fill=LINE, width=1)
    y0 += 28

    # display
    f_disp = vfont(font_file, 168, 600)
    d.text((PAD, y0), "Radugadesign", font=f_disp, fill=INK)
    rdw = text_w(d, "Radugadesign", f_disp)
    f_disp_l = vfont(font_file, 168, 300)
    d.text((PAD + rdw, y0), ".", font=f_disp_l, fill=LIGHT)
    y0 += 180

    # subtitle
    f_h2 = vfont(font_file, 60, 500)
    d.text((PAD, y0), "Студия дизайна и медиа-инсталляций", font=f_h2, fill=INK)
    y0 += 88

    # body
    f_body = vfont(font_file, 28, 400)
    body_lines = [
        "ROTOR — аудиовизуальная инсталляция, исследующая распространение волн в",
        "пространстве и добивающаяся уникального опыта для каждого зрителя.",
    ]
    for line in body_lines:
        d.text((PAD, y0), line, font=f_body, fill=INK)
        y0 += 40
    y0 += 8

    # numbers
    f_num = vfont(font_file, 40, 500)
    d.text((PAD, y0), "01 — 04 · 2026 · +7 (495) 215-09-13", font=f_num, fill=INK)
    y0 += 60

    # alphabet
    f_alpha = vfont(font_file, 28, 400)
    d.text((PAD, y0), "AaBbCc DdEeFf 01234 АаБбВв ГгДдЕёЖжЗз", font=f_alpha, fill=MUTED)
    y0 += 48

    # blurb
    f_blurb = vfont("Geologica.ttf", 22, 400)
    d.text((PAD, y0), blurb, font=f_blurb, fill=MUTED)
    y0 += 56

    return y0


def main():
    sections = [
        ("Geologica.ttf", "1 · GEOLOGICA",
         "vf · Mikhail Sharanda · OFL · GF",
         "Самый нейтральный grotesque на Google Fonts. Близко к Pragmatica Next по характеру."),
        ("Onest.ttf", "2 · ONEST",
         "vf · Anatoly Roshchin · OFL · GF",
         "Острее и продуктовее. Сильная кириллица, читается лучше всего на экране."),
        ("Inter.ttf", "3 · INTER",
         "vf · Rasmus Andersson · OFL · GF",
         "Универсальный safe-выбор. Уже встречается в файле как вспомогательный."),
        ("Manrope.ttf", "4 · MANROPE",
         "vf · Mikhail Sharanda · OFL · GF",
         "Geometric sans, тёплый «техно» характер. Для акцентов и заголовков."),
    ]

    # estimate height
    H = 200 + len(sections) * 580 + 100
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # header
    f_h = vfont("Geologica.ttf", 36, 600)
    d.text((PAD, 56), "Pragmatica Next → Google Fonts кандидаты", font=f_h, fill=INK)
    f_sub = vfont("Geologica.ttf", 20, 400)
    d.text((PAD, 110), "для Google Slides и веба · кириллица + латиница · OFL", font=f_sub, fill=MUTED)
    d.line([(PAD, 158), (W - PAD, 158)], fill=LINE, width=1)

    y = 200
    for ff, label, note, blurb in sections:
        y = draw_section(d, y, ff, label, note, blurb)
        y += 24
        d.line([(PAD, y), (W - PAD, y)], fill=LINE, width=1)
        y += 32

    # crop to actual content
    img_cropped = img.crop((0, 0, W, y + 40))
    img_cropped.save(OUT, optimize=True)
    print(f"✓ {OUT}  {OUT.stat().st_size//1024} KB  {img_cropped.size}")


if __name__ == "__main__":
    main()
