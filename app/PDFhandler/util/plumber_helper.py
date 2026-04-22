import pdfplumber
import pandas as pd
from PIL import ImageDraw

from app.PDFhandler.pdf_table_info import PdfTableInfo
from app.PDFhandler.util.scaling import scale_coords

def extract_tables_from_plumber_page(page, page_num):
    tables = page.find_tables()
    pdf_table_infos = []
    for table_num, table in enumerate(tables, start=1):
        img = page.to_image(resolution=200) 
        table_data = table.extract(y_tolerance=0.01)
        df = pd.DataFrame(table_data[1:], columns=table_data[0])
        img_x0, img_x1, img_y0, img_y1 = scale_coords(img, page.bbox, table.bbox)
        d = ImageDraw.Draw(img.original)

        d.rectangle(
                        [img_x0, img_y0, img_x1, img_y1],
                        outline="red",
                        width=4,
                    )

        pdf_table_infos.append(PdfTableInfo(img.original.copy(), df, table_num, page_num))

    return pdf_table_infos