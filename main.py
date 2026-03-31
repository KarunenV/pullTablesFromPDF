import pdfplumber
import math
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent
input_dir = BASE_DIR / "input_pdfs"
output_dir = BASE_DIR / "output_csv"
output_dir.mkdir(exist_ok=True)

def scale_coords(coords, page_size, img_size, page_bbox):
    x0, top, x1, bottom = coords
    page_width, page_height = page_size
    img_width, img_height = img_size

    scale_x = img_width / page_width
    scale_y = img_height / page_height

    x0_scaled = x0 * scale_x
    top_scaled = (top - page_bbox[1]) * scale_y
    x1_scaled = x1 * scale_x
    bottom_scaled = (bottom - page_bbox[1]) * scale_y

    return (x0_scaled, top_scaled, x1_scaled, bottom_scaled)

for pdf_path in input_dir.glob("*.pdf"):
    pdf_name = pdf_path.stem
    pdf_out_dir = output_dir / pdf_name
    pdf_out_dir.mkdir(exist_ok=True)

    print(f"\nProcessing {pdf_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.find_tables()

            if not tables:
                continue
            
            for table_num, table in enumerate(tables, start=1):
                img = page.to_image(resolution=200)
                print(f"{table}")           
                x0, top, x1, bottom = table.bbox
                print(f"Table BBox: {table.bbox}")

                print(f"Page Height: {page.height}, page width: {page.width}")
                print(f"image height: {img.original.height}, image width: {img.original.width}")
                print(f"scale x: {img.original.width / page.width}, scale y: {img.original.height / page.height}")
                table_data = table.extract()
                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                print(f"data frame head:\n{df.head()}")

                # 🔁 Convert PDF coords → image coords
                image_scale = img.scale

            
                d =ImageDraw.Draw(img.original)
                tx0, ty0, tx1, ty1 = table.bbox

                page_top = page.bbox[1]
                real_page_height = page.bbox[3] - page.bbox[1]

                # Normalize to page-local space
                ty0_local = ty0 - page_top
                ty1_local = ty1 - page_top

                # Flip Y
                pdf_y0 = real_page_height - ty1_local
                pdf_y1 = real_page_height - ty0_local

                # Scale to pixels
                img_x0 = tx0 * image_scale
                img_x1 = tx1 * image_scale
                img_y0 = abs(pdf_y1 * image_scale) 
                img_y1 = abs(pdf_y0 * image_scale)

                print("Drawing rectangle at:", img_x0, img_y0, img_x1, img_y1)

                d.rectangle(
                    [img_x0, img_y0, img_x1, img_y1],
                    outline="red",
                    width=4
                    )
                
                out = pdf_out_dir / f"{pdf_name}_p{page_num}_t{table_num}.csv"


                img.original.show()
                res = input("Press Y to save...")

                if res.lower() == 'y':
                    df.to_csv(out, index=False)
                    print(f"  Saved {out.name}")

            