import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
import queue
from pathlib import Path
from app.PDFhandler.pdf_extractor import extract_tables_from_pdf

BASE_DIR = Path(__file__).resolve().parent

# -------------------------
# App
# -------------------------
class ImageReviewApp(tk.Tk):
    def __init__(self, pdf_paths, output_dir):
        super().__init__()

        self.pdf_paths = pdf_paths
        self.output_dir = output_dir
        self.process_pdfs = []
        self.result_queue = queue.Queue()

        self.title("Image Review")
        self.geometry("800x600")
        self.state("zoomed")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.image = None
        self.photo = None
        self.original_image = None

        self.paned = tk.PanedWindow(self, orient="horizontal")
        self.paned.grid(row=0, column=0, sticky="nsew")

        # Left listbox panel
        self.list_frame = tk.Frame(self.paned)
        self.list_frame.rowconfigure(0, weight=1)
        self.list_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(self.list_frame)
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.on_item_click)

        self.listbox_scrollbar = tk.Scrollbar(self.list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox_scrollbar.grid(row=0, column=1, sticky="ns", pady=10)
        self.listbox.config(yscrollcommand=self.listbox_scrollbar.set)

        self.paned.add(self.list_frame, minsize=200)

        # Image display panel
        self.image_frame = tk.Frame(self.paned, bg="black")
        self.image_frame.rowconfigure(0, weight=1)
        self.image_frame.rowconfigure(1, weight=0)
        self.image_frame.columnconfigure(0, weight=1)

        self.image_label = tk.Label(self.image_frame, bg="#333333")
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self.spinner = ttk.Progressbar(self.image_frame, mode="indeterminate")
        self.spinner.grid(row=1, column=0, sticky="n", pady=20)

        self.paned.add(self.image_frame)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=1, column=0, pady=10)

        self.back_btn = tk.Button(btn_frame, text="Back", command=self.load_previous, state="disabled")
        self.save_btn = tk.Button(btn_frame, text="Save", command=self.save_csv, state="disabled")
        self.copy_btn = tk.Button(btn_frame, text="Copy", command=self.copy_csv, state="disabled")
        self.next_btn = tk.Button(btn_frame, text="Next", command=self.load_next, state="disabled")

        self.back_btn.pack(side="left", padx=5)
        self.save_btn.pack(side="left", padx=5)
        self.copy_btn.pack(side="left", padx=5)
        self.next_btn.pack(side="left", padx=5)

        self.start_spinner()

        # Start processing PDFs in a separate thread
        self.processing_thread = threading.Thread(target=self._process_pdfs, daemon=True)
        self.processing_thread.start()

        # Start processing results in main thread
        self._process_results()

    #-------------------------
    # Listbox control
    #-------------------------
    def increase_index(self):
        index =  self._get_index()
        if index < (len(self.process_pdfs) - 1):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index + 1)

    def decrease_index(self):
        index = self._get_index()
        if index > 0:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index - 1)

    def _get_index(self):
        if not self.listbox.curselection():
            return -1
        return self.listbox.curselection()[0]

    def on_item_click(self, event):
        if not self.listbox.curselection():
            return
        
        index = self.listbox.curselection()[0]
        selected_pdf = self.process_pdfs[index]

        self.image_label.config(image="")
        self.image = None
        self.photo = None

        self.after(0, lambda: self.load_image(selected_pdf.get_current_table().image))

    # -------------------------
    # Spinner control
    # -------------------------
    def start_spinner(self):
        self.spinner.grid(row=1, column=0, sticky="n", pady=20)
        self.spinner.start(10)

    def stop_spinner(self):
        self.spinner.stop()
        self.spinner.grid_remove()


    def _process_pdfs(self):
        for pdf_path in self.pdf_paths:
            result = extract_tables_from_pdf(pdf_path)
            self.result_queue.put(result)

    def _process_results(self):
        try:
            while True:
                result = self.result_queue.get_nowait()
                self.on_pdf_finished(result)
        except queue.Empty:
            pass
        self.after(100, self._process_results)

    def on_pdf_finished(self, result):
        self.process_pdfs.append(result)
        self.after(0, lambda: self.listbox.insert(tk.END, result.pdf_name))

        if len(self.process_pdfs) == 1:
            self.stop_spinner()
            self.load_current_image_async()
            self.after(0, lambda: self.listbox.selection_set(0))



    # -------------------------
    # Image loading
    # -------------------------
    def load_current_image_async(self):
        threading.Thread(target=self._load_current_image, daemon=True).start()
    
    def _load_current_image(self):
        image = self.process_pdfs[self._get_index()].get_current_table().image
        if image is None:
            self.after(0, self.no_more_images)
            return
        
        self.after(0, lambda: self.load_image(image))

    def load_next_image_async(self):
        threading.Thread(target=self._load_next_image, daemon=True).start()

    def _load_next_image(self):
        image = self.process_pdfs[self._get_index()].load_next_table().image
        if image is None:
            self.after(0, self.no_more_images)
            return
        
        self.after(0, lambda: self.load_image(image))

    def load_previous_image_async(self):
        threading.Thread(target=self._load_previous_image, daemon=True).start()

    def _load_previous_image(self):
        image = self.process_pdfs[self._get_index()].load_previous_table().image
        if image is None:
            self.after(0, self.no_more_images)
            return
        
        self.after(0, lambda: self.load_image(image))

    def load_image(self, im:Image):
        self.original_image = im.copy()
        self.after(0, self.show_image)
        self.after(0, self.update_buttons)

    def show_image(self):
        self.stop_spinner()

        if not self.original_image:
            return

        width = max(self.image_frame.winfo_width() - 20, 10)
        height = max(self.image_frame.winfo_height() - 20, 10)

        image = self.original_image.copy()
        image.thumbnail((width, height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.photo, text="")

        self.save_btn.config(state="normal")
        self.copy_btn.config(state="normal")

    # -------------------------
    # Buttons
    # -------------------------
    def update_buttons(self):
        self.update_back()
        self.update_next()

    def update_back(self):
        listboxIndex = self._get_index()
        hasPrevious = self.process_pdfs[listboxIndex].has_previous_table()

        if not hasPrevious and listboxIndex > 0:
            self.back_btn.config(state="normal")
            self.back_btn.config(text="Previous file")
        elif not hasPrevious and listboxIndex <= 0:
            self.back_btn.config(state="disabled")
            self.back_btn.config(text="Back")
        else:
            self.back_btn.config(state="normal")
            self.back_btn.config(text="Back")

    def update_next(self):
        listboxIndex = self._get_index()
        hasNext = self.process_pdfs[listboxIndex].has_next_table()

        if not hasNext and listboxIndex < (len(self.process_pdfs) - 1):
            self.next_btn.config(state="normal")
            self.next_btn.config(text="Next file")
        elif not hasNext and listboxIndex >= (len(self.process_pdfs) - 1):
            self.next_btn.config(state="disabled")
            self.next_btn.config(text="Next")
        else:
            self.next_btn.config(state="normal")
            self.next_btn.config(text="Next")
    
    def no_more_images(self):
        self.stop_spinner()
        self.image_label.config(image="", text="No more images")
        self.save_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")

    def save_csv(self):
        self.process_pdfs[self._get_index()].save_csv(self.output_dir)


    def copy_csv(self):
        self.process_pdfs[self._get_index()].copy_csv()

    def load_next(self):
        self.image_label.config(image="")
        self.image = None
        self.photo = None
        if not self.process_pdfs[self._get_index()].has_next_table():
            self.increase_index()
            self.load_current_image_async()
        else:
            self.load_next_image_async()

    def load_previous(self):
        self.image_label.config(image="")
        self.image = None
        self.photo = None

        if not self.process_pdfs[self._get_index()].has_previous_table():
            self.decrease_index()
            self.load_current_image_async()
        else:
            self.load_previous_image_async()


