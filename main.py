import os
from pathlib import Path
import tabula

# Base directory = folder where this script is located
BASE_DIR = Path(__file__).resolve().parent

input_dir = BASE_DIR / "input_pdfs"
output_dir = BASE_DIR / "output_csv"
output_dir.mkdir(parents=True, exist_ok=True)

pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
if not pdf_files:
    raise SystemExit(f"No PDF files found in input folder: {input_dir}")

total_tables = 0
for pdf_file in sorted(pdf_files):
    pdf_path = os.path.join(input_dir, pdf_file)
    print(f"Processing: {pdf_path}")

    # Extract all tables from all pages
    dfs = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)
    if not dfs:
        print(f"  No tables found in {pdf_file}")
        continue

    for idx, df in enumerate(dfs, start=1):
        out = os.path.join(
            output_dir,
            f"{os.path.splitext(pdf_file)[0]}_{idx}.csv"
        )
        # Add metadata columns if desired inside each DataFrame
        df.insert(0, "source_file", pdf_file)
        df.insert(1, "table_no", idx)
        df.to_csv(out, index=False)
        print(f"  Saved: {out}")

    total_tables += len(dfs)

print(f"Completed. Total tables extracted: {total_tables}")