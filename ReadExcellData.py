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
    
    def get_sheet_names(self):
        try:
            wb = openpyxl.load_workbook(self.file_path)
            sheet_names = wb.sheetnames
            return sheet_names
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_sheet_data(self, sheet_name):
        try:
            data = pd.read_excel(self.file_path, sheet_name=sheet_name)
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    def get_column_names(self):
        if self.data is not None:
            return self.data.columns
        else:
            print("No data available. Please read the data first.")
            return None
    
    def get_column_data(self, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data[column_name]
            else:
                print(f"Column '{column_name}' does not exist.")
                return None
        else:
            print("No data available. Please read the data first.")
            return None
    
    def get_row_data(self, row_index):
        if self.data is not None:
            return self.data.iloc[row_index]
        else:
            print("No data available. Please read the data first.")
            return None
    
    def get_cell_data(self, row_index, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data.at[row_index, column_name]
            else:
                print(f"Column '{column_name}' does not exist.")
                return None
        else:
            print("No data available. Please read the data first.")
            return None
    
    def get_cell_data_by_index(self, row_index, column_index):
        if self.data is not None:
            return self.data.iat[row_index, column_index]
        else:
            print("No data available. Please read the data first.")
            return None
    
    def get_value_counts(self, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data[column_name].value_counts()
            else:
                print(f"Column '{column_name}' does not exist.")
                return None
        else:
            print("No data available. Please read the data first.")
            return None
    
    def get_unique_values(self, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data[column_name].unique()
            else:
                print(f"Column '{column_name}' does not exist.")
                return None
        else:
            print("No data available. Please read the data first.")
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
