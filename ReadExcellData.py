import pandas as pd
import openpyxl
import os

class ReadExcelData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def read_data(self):
        try:
            self.data = pd.read_excel(self.file_path)
            print("Data read successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_data(self):
        if self.data is not None:
            return self.data
        else:
            print("No data available. Please read the data first.")
            return None
"""
# Usage example
if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "files", "grid.xlsx")
    excel_reader = ReadExcelData(file_path)
    excel_reader.read_data()
    data = excel_reader.get_data()
    if data is not None:
        print(data.head())

"""
