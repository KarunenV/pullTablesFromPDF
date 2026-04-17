class PdfTableInfo:
    def __init__(self, image, table_data, table_index, page_index):
        self.image = image
        self.table_data = table_data
        self.table_index = table_index
        self.page_index = page_index
        self.search_flag = False

    
    def update_search_flag(self, query):
        self.search_flag = query in self.table_data.to_string().lower()

