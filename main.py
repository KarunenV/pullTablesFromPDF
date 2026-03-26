import pdfplumber
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
input_dir = BASE_DIR / "input_pdfs"
output_dir = BASE_DIR / "output_csv"
output_dir.mkdir(exist_ok=True)

for pdf_path in input_dir.glob("*.pdf"):
    pdf_name = pdf_path.stem
    pdf_out_dir = output_dir / pdf_name
    pdf_out_dir.mkdir(exist_ok=True)

    print(f"\nProcessing {pdf_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            if not tables:
                continue

            for table_num, table in enumerate(tables, start=1):
                df = pd.DataFrame(table[1:], columns=table[0])

                out = pdf_out_dir / f"{pdf_name}_p{page_num}_t{table_num}.csv"
                df.to_csv(out, index=False)

                print(f"  Saved {out.name}")

            