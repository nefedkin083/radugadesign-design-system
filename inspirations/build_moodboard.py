"""Render moodboard.html → moodboard.pdf via WeasyPrint."""
import pathlib
from weasyprint import HTML

HERE = pathlib.Path(__file__).parent
HTML(filename=str(HERE / "moodboard.html")).write_pdf(
    str(HERE / "moodboard.pdf"),
    presentational_hints=True,
)
print("✓", (HERE / "moodboard.pdf").stat().st_size // 1024, "KB")
