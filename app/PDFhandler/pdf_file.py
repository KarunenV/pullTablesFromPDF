class pdf_file:
    def __init__(self, pdf_name, table_data):
        self.pdf_name = pdf_name
        self.table_data = table_data
        self.current_index = 0

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