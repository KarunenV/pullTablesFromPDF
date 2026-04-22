import fitz
from app.PDFhandler.pdf_table_info import PdfTableInfo

from PIL import ImageDraw

from app.PDFhandler.util.rectangle_helper import checkIfARectangleMatchesList, merge_rects_dicts, merge_rects_tuples, tupleToRectDict
from app.PDFhandler.util.table_helper import build_table_from_spans
from app.PDFhandler.util.scaling import scale_coords

def extract_spans_from_page(page_fitz):
    blocks = page_fitz.get_text("dict")["blocks"]
    spans = []
    bboxs = []  
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
                    bboxs.append(span["bbox"])
    return spans, bboxs

def extract_tables_from_fitz_page(page_fitz, rects, img, page_bbox, page_num):
    spans = extract_spans_from_page(page_fitz)

    merged_rects_dicts = merge_rects_dicts(rects, pixel_diff=5)
    spans, bboxs = extract_spans_from_page(page_fitz)
    span_bboxes_merged = merge_rects_tuples(bboxs, pixel_diff=5)
    valid_span_bboxes = [tupleToRectDict(i) for i in span_bboxes_merged if checkIfARectangleMatchesList(tupleToRectDict(i), merged_rects_dicts, pixel_diff=5)]

    y_min = min([i["top"] for i in valid_span_bboxes])
    y_max = max([i["bottom"] for i in merged_rects_dicts])

    spans_with_valid_bboxes = [i for i in spans if i["bbox"][1] >= y_min and i["bbox"][3] <= y_max]


    df = build_table_from_spans(spans_with_valid_bboxes)

    if df.empty:
        return []

    d = ImageDraw.Draw(img.original)

    for tup in spans_with_valid_bboxes:
        x0, x1, y0, y1 = scale_coords(img, page_bbox, tup["bbox"])
        d.rectangle(
                [x0, y0, x1, y1],
                outline="blue",
                width=2,
            )
    

    return PdfTableInfo(img.original.copy(), df, 1, page_num)