import pdfplumber
import math
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent

class PDFTableExtractor:
    def __init__(self):
        super().__init__()
        self.input_dir = BASE_DIR / "input_pdfs"
        self.output_dir = BASE_DIR / "output_csv"
        self.output_dir.mkdir(exist_ok=True)
        self.table_images = []
        self.current_index = -1

        self.pdf_paths = sorted(self.input_dir.glob("*.pdf"))
        self._pdf_index = 0
        self._current_pdf = None
        self._current_pdf_obj = None
        self._page_index = 0
        self._table_index = 0

    def load_next_image(self):
        if self.current_index < (len(self.table_images) - 1):
            image = self.table_images[self.current_index]
            self.current_index += 1
            return image[0]

        image = self._load_next_table_image()
        if image is None:
            return None

        self.table_images.append(image)
        self.current_index += 1
        return image[0]
    
    def load_previous_image(self):
        if self.current_index > 0:
            image = self.table_images[self.current_index - 1]
            self.current_index -= 1
            return image[0]
        else:
            return None
        
    def get_current_data(self):
        if 0 <= self.current_index  < len(self.table_images):
            return self.table_images[self.current_index]
        else:
            return None

    def _open_current_pdf(self):
        if self._current_pdf_obj is not None:
            self._current_pdf_obj.close()
            self._current_pdf_obj = None

        if self._pdf_index >= len(self.pdf_paths):
            return False

        self._current_pdf = self.pdf_paths[self._pdf_index]
        self._current_pdf_obj = pdfplumber.open(self._current_pdf)
        self._page_index = 0
        self._table_index = 0
        return True

    def _load_next_table_image(self):
        while True:
            if self._current_pdf_obj is None:
                if not self._open_current_pdf():
                    return None

            while self._page_index < len(self._current_pdf_obj.pages):
                page = self._current_pdf_obj.pages[self._page_index]
                tables = page.find_tables()

                if self._table_index < len(tables):
                    table = tables[self._table_index]
                    page_num = self._page_index + 1
                    table_num = self._table_index + 1
                    self._table_index += 1
                    if self._table_index >= len(tables):
                        self._page_index += 1
                        self._table_index = 0

                    image = self._render_table_image(page, table, self._current_pdf.stem, page_num, table_num)
                    return image

                self._page_index += 1
                self._table_index = 0

            self._current_pdf_obj.close()
            self._current_pdf_obj = None
            self._pdf_index += 1

    def _render_table_image(self, page, table, pdf_name, page_num, table_num):
        img = page.to_image(resolution=200)

        table_data = table.extract()
        df = pd.DataFrame(table_data[1:], columns=table_data[0])

        img_x0, img_x1, img_y0, img_y1 = self.scale_coords(img, page.bbox, table.bbox)
        d = ImageDraw.Draw(img.original)

        d.rectangle(
            [img_x0, img_y0, img_x1, img_y1],
            outline="red",
            width=4,
        )

        return (img.original.copy(), self.output_dir / pdf_name,f"{pdf_name}_p{page_num}_t{table_num}.csv", df)


    def scale_coords(self, img, page_bbox, table_bbox):
        image_scale = img.scale        
        tx0, ty0, tx1, ty1 = table_bbox

        page_top = page_bbox[1]
        real_page_height = page_bbox[3] - page_bbox[1]

        ty0_local = ty0 - page_top
        ty1_local = ty1 - page_top

        pdf_y0 = real_page_height - ty1_local
        pdf_y1 = real_page_height - ty0_local

        img_x0 = tx0 * image_scale
        img_x1 = tx1 * image_scale
        img_y0 = abs(pdf_y1 * image_scale)
        img_y1 = abs(pdf_y0 * image_scale)
        img_y0, img_y1 = sorted([img_y0, img_y1])

        return (img_x0, img_x1, img_y0, img_y1)
