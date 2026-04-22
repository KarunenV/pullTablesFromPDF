import pdfplumber
import pandas as pd
import fitz

from PIL import Image, ImageDraw


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def cluster_positions(values, tol=8):
    values = sorted(set(values))
    groups = []
    for value in values:
        if not groups or value - groups[-1][-1] > tol:
            groups.append([value])
        else:
            groups[-1].append(value)
    return [sum(group) / len(group) for group in groups]


def extract_spans_from_page(page_fitz):
    blocks = page_fitz.get_text("dict")["blocks"]
    spans = []
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line.get("spans", []):
                if span.get("text"):
                    spans.append({
                        "text": span["text"],
                        "bbox": span["bbox"],
                    })
    return spans


def build_table_from_spans(spans, row_tol=7, col_tol=12):
    valid_spans = []
    for span in spans:
        text = normalize_text(span["text"])
        if not text:
            continue
        x0, y0, x1, y1 = span["bbox"]
        valid_spans.append({
            "text": text,
            "x0": x0,
            "x1": x1,
            "cx": (x0 + x1) / 2,
            "cy": (y0 + y1) / 2,
        })

    if not valid_spans:
        return [], []

    row_centers = cluster_positions([span["cy"] for span in valid_spans], tol=row_tol)
    column_centers = cluster_positions([span["x0"] for span in valid_spans], tol=col_tol)

    rows = {i: [] for i in range(len(row_centers))}
    for span in valid_spans:
        row_index = min(range(len(row_centers)), key=lambda i: abs(span["cy"] - row_centers[i]))
        rows[row_index].append(span)

    table = []
    for row_index in sorted(rows):
        row_spans = sorted(rows[row_index], key=lambda s: s["x0"])
        row_cells = [""] * len(column_centers)
        for span in row_spans:
            col_index = min(range(len(column_centers)), key=lambda i: abs(span["cx"] - column_centers[i]))
            if row_cells[col_index]:
                row_cells[col_index] += " " + span["text"]
            else:
                row_cells[col_index] = span["text"]
        table.append([cell.strip() for cell in row_cells])

    return table, column_centers


input_file = r"D:\Documents\Coomaren\pullTablesFromPDF\input_pdfs\Salus Re - Financials_.pdf"
pdf_pdfplumber = pdfplumber.open(input_file)
pdf_fitz = fitz.open(input_file)

page_number = 16
page_plumber = pdf_pdfplumber.pages[page_number]
page_fitz = pdf_fitz.load_page(page_number)

spans = extract_spans_from_page(page_fitz)
table, column_centers = build_table_from_spans(spans)

with open("output.txt", "w", encoding="utf-8") as f:
    for row in table:
        f.write(" | ".join(row) + "\n")

if table:
    df = pd.DataFrame(table[1:], columns=table[0])
else:
    df = pd.DataFrame()

csv_path = "output_table.csv"
df.to_csv(csv_path, index=False)

print(f"Extracted {len(table)} rows and {len(column_centers)} columns")
print(f"Saved raw row output to output.txt and table to {csv_path}")




            

            



            

