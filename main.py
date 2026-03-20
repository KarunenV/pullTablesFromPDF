import os
import tabula

pdf_path = r"d:\Documents\Coomaren\pullTablesFromPDF\Zurich Loss Run - Beau Geste XXV LLC - AL BAP-0141914 vao 1.7.25.PDF"
output_dir = r"d:\Documents\Coomaren\pullTablesFromPDF\output_csv"
os.makedirs(output_dir, exist_ok=True)

dfs = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

for idx, df in enumerate(dfs, start=1):
    out = os.path.join(output_dir, f"table_{idx}.csv")
    df.to_csv(out, index=False)
    print("Saved", out)
print("Total tables:", len(dfs))