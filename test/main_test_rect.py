import pdfplumber
import pandas as pd
import fitz

from PIL import Image, ImageDraw

def do_overlap(rect1, rect2, pixel_diff=5):
    l1x = rect1['x0']
    r1x = rect1['x1']
    l1y = rect1['top']
    r1y = rect1['bottom']

    l2x = rect2['x0']
    r2x = rect2['x1']
    l2y = rect2['top']
    r2y = rect2['bottom']

    # If one rectangle is on left side of other
    if (l1x > r2x or l2x > r1x) and ((abs(l2x - r1x) > pixel_diff) and (abs(l1x - r2x) > pixel_diff)):
        return False

    # If one rectangle is above other
    if (r1y < l2y or r2y < l1y) and ((abs(l2y - r1y) > pixel_diff) and (abs(l1y - r2y) > pixel_diff)):
        return False

    return True


# Return true if the rect space matches any of the rects in the list
def checkIfARectangleMatchesList(rect, rect_list, pixel_diff=5):
    for i, im in enumerate(rect_list):
        overlap = do_overlap(rect, im, pixel_diff)

        if overlap:
            return True

    return False


# Merges a list of dictionary rectangles together, so we have less rectangles to worry about
def merge_rects_dicts(rects, pixel_diff=5):

    previous = len(rects)

    while True:
        clusters = list()
        for rect in rects:
            matched = False
            for cluster in clusters:
                if (do_overlap(rect, cluster, pixel_diff)):
                    matched = True
                    cluster['x0'] = min(cluster['x0'], rect['x0'])
                    cluster['x1'] = max(cluster['x1'], rect['x1'])
                    cluster['top'] = min(cluster['top'], rect['top'])
                    cluster['bottom'] = max(cluster['bottom'], rect['bottom'])

            if (not matched):
                clusters.append(rect)

        

        if (len(clusters) == previous):
            break

        previous = len(clusters)
        rects = clusters     

    
    return clusters

def tupleToRectDict(rect_tuple):
    return {"x0": rect_tuple[0],  "top": rect_tuple[1], "x1": rect_tuple[2], "bottom": rect_tuple[3]}

def RectDictToTuple(rect_dict):
    return [rect_dict["x0"], rect_dict["top"], rect_dict["x1"], rect_dict["bottom"]]

# Merges a list of tuple rectangles together, so we have less rectangles to worry about
def merge_rects_tuples(rects, pixel_diff=5):
    rects = merge_rects_dicts([tupleToRectDict(i) for i in rects], pixel_diff)
    return [RectDictToTuple(i) for i in rects]

def scale_coords(img, page_bbox, table_bbox):
    width_scale = img.original.width / (page_bbox[2] - page_bbox[0])
    height_scale = img.original.height / (page_bbox[3] - page_bbox[1])

    tx0, ty0, tx1, ty1 = table_bbox

    table_is_weird = ty0 > page_bbox[3]
    page_top = page_bbox[1]
    real_page_height = page_bbox[3] - page_bbox[1]

    ty0_local = ty0 - page_top
    ty1_local = ty1 - page_top
    # print(f"{ty0-ty1}")

    if table_is_weird:
        # print("Table is upside down, flipping y-coords")
        pdf_y0 = real_page_height - ty1_local
        pdf_y1 = real_page_height - ty0_local
    else:
        pdf_y0 = ty0_local 
        pdf_y1 = ty1_local 

    img_x0 = tx0 * width_scale
    img_x1 = tx1 * width_scale
    img_y0 = abs(pdf_y1 * height_scale)
    img_y1 = abs(pdf_y0 * height_scale)
    img_y0, img_y1 = sorted([img_y0, img_y1])
    img_x0, img_x1 = sorted([img_x0, img_x1])

    return (img_x0, img_x1, img_y0, img_y1)

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

input_file = r"D:\Documents\Coomaren\pullTablesFromPDF\input_pdfs\Salus Re - Financials_.pdf"
pdf_pdfplumber = pdfplumber.open(input_file)
pdf_fitz = fitz.open(input_file)

page_number = 14
page_plumber = pdf_pdfplumber.pages[page_number]
page_fitz = pdf_fitz.load_page(page_number)
img = page_plumber.to_image(resolution=150)
rects = page_plumber.rects

merged_rects_dicts = merge_rects_dicts(page_plumber.rects, pixel_diff=10)

spans, bboxs = extract_spans_from_page(page_fitz)

span_bboxes_merged = merge_rects_tuples(bboxs, pixel_diff=10)

valid_span_bboxes = [tupleToRectDict(i) for i in span_bboxes_merged if checkIfARectangleMatchesList(tupleToRectDict(i), merged_rects_dicts, pixel_diff=5)]

y_min = min([i["top"] for i in valid_span_bboxes])
y_max = max([i["bottom"] for i in merged_rects_dicts])
print(f"y_min: {y_min}, y_max: {y_max}")

spans_with_valid_bboxes = [i for i in spans if i["bbox"][1] >= y_min and i["bbox"][3] <= y_max]



d = ImageDraw.Draw(img.original)

for tup in spans_with_valid_bboxes:
    # print(tup)
    x0, x1, y0, y1 = scale_coords(img, page_plumber.bbox, tup["bbox"]) 
    d.rectangle(
            [x0, y0, x1, y1],
            outline="blue",
            width=2,
        )

# for merge_rects_dict in merge_rects_dicts:
#     img_x0, img_x1, img_y0, img_y1 = scale_coords(img, page_plumber.bbox, [merge_rects_dict['x0'], merge_rects_dict['top'], merge_rects_dict['x1'], merge_rects_dict['bottom']])



#     d.rectangle(
#                         [img_x0, img_y0, img_x1, img_y1],
#                         outline="red",
#                         width=4,
#                     )


img.original.show()
input("Press Enter to continue...")