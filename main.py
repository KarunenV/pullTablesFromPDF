# -------------------------
# Run
# -------------------------
from app.app import ImageReviewApp
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

if __name__ == "__main__":
    input_dir = BASE_DIR / "input_pdfs"
    output_dir = BASE_DIR / "output_csv"
    output_dir.mkdir(exist_ok=True)
    pdf_paths = sorted(input_dir.glob("*.pdf"))
    
    app = ImageReviewApp(pdf_paths, output_dir)
    app.mainloop()