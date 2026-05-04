"""Render font_comparison.html via WeasyPrint (no browser)."""
import pathlib
from weasyprint import HTML

HERE = pathlib.Path(__file__).parent
HTML_FILE = HERE / "font_comparison.html"
OUT_PDF = HERE / "font_comparison.pdf"
OUT_PNG = HERE / "font_comparison.png"


def main():
    HTML(filename=str(HTML_FILE)).write_pdf(str(OUT_PDF))
    print(f"✓ pdf {OUT_PDF.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
