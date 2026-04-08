import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
from pathlib import Path
from app.PDFhandler.pdf_extractor import PDFTableExtractor

BASE_DIR = Path(__file__).resolve().parent

# -------------------------
# App
# -------------------------
class ImageReviewApp(tk.Tk):
    def __init__(self, pdf_paths, output_dir):
        super().__init__()

        self.pdf_paths = pdf_paths
        self.output_dir = output_dir

        self.title("Image Review")
        self.geometry("800x600")

        self.image = None
        self.photo = None

        # Spinner
        self.spinner = ttk.Progressbar(self, mode="indeterminate")
        self.spinner.pack(pady=20)

        # Image label
        self.image_label = tk.Label(self)
        self.image_label.pack(expand=True)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        self.back_btn = tk.Button(btn_frame, text="Back", command=self.load_previous, state="disabled")
        self.save_btn = tk.Button(btn_frame, text="Save", command=self.save_csv, state="disabled")
        self.copy_btn = tk.Button(btn_frame, text="Copy", command=self.copy_csv, state="disabled")
        self.next_btn = tk.Button(btn_frame, text="Next", command=self.load_next)

        self.back_btn.pack(side="left", padx=5)
        self.save_btn.pack(side="left", padx=5)
        self.copy_btn.pack(side="left", padx=5)
        self.next_btn.pack(side="left", padx=5)

        self.pdf_extractor = PDFTableExtractor(self.pdf_paths, self.output_dir)
        self.start_spinner()
        self.load_next_image_async()

    # -------------------------
    # Spinner control
    # -------------------------
    def start_spinner(self):
        self.spinner.pack(pady=20)
        self.spinner.start(10)

    def stop_spinner(self):
        self.spinner.stop()
        self.spinner.pack_forget()

    # -------------------------
    # Image loading
    # -------------------------
    def load_next_image_async(self):
        threading.Thread(target=self._load_next_image, daemon=True).start()

    def _load_next_image(self):
        image = self.pdf_extractor.load_next_image()
        if image is None:
            self.after(0, self.no_more_images)
            return
        
        self.after(0, lambda: self.load_image(image))

    def load_previous_image_async(self):
        threading.Thread(target=self._load_previous_image, daemon=True).start()

    def _load_previous_image(self):
        image = self.pdf_extractor.load_previous_image()
        if image is None:
            self.after(0, self.no_more_images)
            return
        
        self.after(0, lambda: self.load_image(image))

    def load_image(self, im:Image):
        self.image = im  # <-- your generated image

        self.after(0, self.show_image)

    def show_image(self):
        self.stop_spinner()

        self.image.thumbnail((760, 460))
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_label.config(image=self.photo, text="")

        self.save_btn.config(state="normal")
        self.copy_btn.config(state="normal")

    # -------------------------
    # Buttons
    # -------------------------
    def no_more_images(self):
        self.stop_spinner()
        self.image_label.config(image="", text="No more images")
        self.save_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")

    def save_csv(self):
        _, dir,file_name,df = self.pdf_extractor.get_current_data()
        dir.mkdir(exist_ok=True)
        path = filedialog.asksaveasfilename(
            initialfile= file_name,
            initialdir=dir,
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if path:
            df.to_csv(path, index=False)

    def copy_csv(self):
        _, _,_,df = self.pdf_extractor.get_current_data()
        df.to_clipboard(index=False)    

    def load_next(self):
        self.image_label.config(image="")
        self.image = None
        self.photo = None

        self.back_btn.config(state="normal")
        self.save_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")

        self.start_spinner()
        self.load_next_image_async()

    def load_previous(self):
        self.image_label.config(image="")
        self.image = None
        self.photo = None

        self.save_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")

        self.start_spinner()
        self.load_previous_image_async()


