from app.PDFhandler.pdf_table_info import PdfTableInfo
from tkinter import filedialog

class PdfFileInfo:
    def __init__(self, pdf_name:str, table_data:list[PdfTableInfo]):
        self.pdf_name = pdf_name
        self.table_data = table_data
        self.current_index = 0
        self.current_search_start_index = 0
        

    def get_current_table(self):
        if 0 <= self.current_index < len(self.table_data):
            return self.table_data[self.current_index]
        else:
            return None
        
    def load_next_table(self):
        if self.current_index < (len(self.table_data) - 1):
            self.current_index += 1
            return self.table_data[self.current_index]
        else:
            return None
        
    def load_previous_table(self):
        if self.current_index > 0:
            self.current_index -= 1
            return self.table_data[self.current_index]
        else:
            return None
        
    def has_next_table(self):
        return self.current_index < (len(self.table_data) - 1)
    
    def has_previous_table(self):
        return self.current_index > 0
    
    def has_next_search_result(self):
        for index in range(self.current_search_start_index, len(self.table_data)):
            if self.table_data[index].search_flag:
                self.current_index = index
                self.current_search_start_index = index + 1
                return True
        return False
    
    def copy_csv(self):
        table = self.get_current_table()
        if table is not None:
            table.table_data.to_clipboard(index=False)

    def save_csv(self, output_dir):
        table =  self.get_current_table()
        filename = self.pdf_name + f"_page{table.page_index}_table{table.table_index}"
        path = filedialog.asksaveasfilename(
            initialfile= filename,
            initialdir= output_dir,
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if path:
            table.table_data.to_csv(path, index=False)

    def update_search_flag(self, query):
        for table in self.table_data:
            table.update_search_flag(query)