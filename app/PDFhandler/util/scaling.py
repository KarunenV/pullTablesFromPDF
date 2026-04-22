import math

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

    return (img_x0, img_x1, img_y0, img_y1)
