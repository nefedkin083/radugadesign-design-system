"""Render tools/font_comparison.html to PNG via Playwright."""
import pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
HTML = HERE / "font_comparison.html"
OUT = HERE / "font_comparison.png"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1800, "height": 1200}, device_scale_factor=2)
        page = ctx.new_page()
        page.goto(HTML.absolute().as_uri())
        page.wait_for_load_state("networkidle")
        # wait for fonts
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(OUT), full_page=True)
        browser.close()
    print(f"✓ {OUT}  {OUT.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
