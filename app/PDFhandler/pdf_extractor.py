import pdfplumber
import fitz
import pandas as pd
from pdfplumber import page
from app.PDFhandler.pdf_file_info import PdfFileInfo
from app.PDFhandler.pdf_table_info import PdfTableInfo
from app.PDFhandler.util.scaling import scale_coords
from app.PDFhandler.util.plumber_helper import extract_tables_from_plumber_page
from app.PDFhandler.util.fitz_helper import  extract_tables_from_fitz_page 


def extract_tables_from_pdf(pdf_path):
    pdf_table_infos =  []
    fitz_doc = fitz.open(pdf_path)
    plumber_doc = pdfplumber.open(pdf_path)

    try:
        for page_index, page_plumber in enumerate(plumber_doc.pages, start=0):
            tables = extract_tables_from_plumber_page(page_plumber, page_index + 1)
            if len(tables) > 0:
                pdf_table_infos.extend(tables)
                continue

            rects = page_plumber.rects
            if len(rects) > 2:
                img = page_plumber.to_image(resolution=200) 
                fitz_page = fitz_doc.load_page(page_index)
                pdf_table_infos.append(extract_tables_from_fitz_page(fitz_page, rects, img, page_plumber.bbox, page_index + 1))

    finally:
        fitz_doc.close()
        plumber_doc.close()

    return PdfFileInfo(pdf_path.stem, pdf_table_infos)

