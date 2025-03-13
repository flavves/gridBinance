import pandas as pd
import openpyxl
import os
import json
import logging

class ReadExcelData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.sheetNames = None
        #logging.info(f"ReadExcelData instance created for file: {file_path}")

    def read_data(self):
        try:
            self.data = pd.read_excel(self.file_path)
            logging.info("Excel data successfully read.")
        except Exception as e:
            logging.error(f"Error reading Excel data: {e}")

    def get_data(self):
        if self.data is not None:
            return self.data
        else:
            logging.warning("No data available. Please read the data first.")
            return None
        
    def save_sheet_Names_To_Json(self):
        try:
            with open('sheetNames.json', 'w') as f:
                json.dump(self.sheetNames, f)
            logging.info("Sheet names successfully saved to JSON.")
        except Exception as e:
            logging.error(f"Error saving sheet names to JSON: {e}")
            
    def get_sheet_names(self):
        try:
            wb = openpyxl.load_workbook(self.file_path)
            self.sheetNames = wb.sheetnames
            self.save_sheet_Names_To_Json()
            logging.info("Sheet names retrieved successfully.")
            return self.sheetNames
        except Exception as e:
            logging.error(f"Error retrieving sheet names: {e}")
            return None
        
    def get_sheet_data(self, sheet_name):
        try:
            data = pd.read_excel(self.file_path, sheet_name=sheet_name)
            logging.info(f"Data read from sheet: {sheet_name}")
            return data
        except Exception as e:
            logging.error(f"Error reading data from sheet {sheet_name}: {e}")
            return None
    
    def get_column_names(self):
        if self.data is not None:
            return self.data.columns
        else:
            logging.warning("No data available. Please read the data first.")
            return None
    
    def get_column_data(self, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data[column_name]
            else:
                logging.warning(f"Column '{column_name}' does not exist.")
                return None
        else:
            logging.warning("No data available. Please read the data first.")
            return None
    
    def get_row_data(self, row_index):
        if self.data is not None:
            return self.data.iloc[row_index]
        else:
            logging.warning("No data available. Please read the data first.")
            return None
    
    def get_cell_data(self, row_index, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data.at[row_index, column_name]
            else:
                logging.warning(f"Column '{column_name}' does not exist.")
                return None
        else:
            logging.warning("No data available. Please read the data first.")
            return None
    
    def get_cell_data_by_index(self, row_index, column_index):
        if self.data is not None:
            return self.data.iat[row_index, column_index]
        else:
            logging.warning("No data available. Please read the data first.")
            return None
    
    def get_value_counts(self, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data[column_name].value_counts()
            else:
                logging.warning(f"Column '{column_name}' does not exist.")
                return None
        else:
            logging.warning("No data available. Please read the data first.")
            return None
    
    def get_unique_values(self, column_name):
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data[column_name].unique()
            else:
                logging.warning(f"Column '{column_name}' does not exist.")
                return None
        else:
            logging.warning("No data available. Please read the data first.")
            return None

    def get_value_index(self, column_name, value):
        if self.data is not None:
            if column_name in self.data.columns:
                indices = self.data.index[self.data[column_name] == value].tolist()
                if indices:
                    return indices
                else:
                    closest_value = self.data[column_name].iloc[(self.data[column_name] - value).abs().argsort()[:1]].values[0]
                    closest_indices = self.data.index[self.data[column_name] == closest_value].tolist()
                    logging.warning(f"Exact value '{value}' not found. Closest value is '{closest_value}'.")
                    return closest_indices
            else:
                logging.warning(f"Column '{column_name}' does not exist.")
                return None
        else:
            logging.warning("No data available. Please read the data first.")
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
        # Example usage of get_value_index
        indices = excel_reader.get_value_index('Price', 100)
        if indices is not None:
            print(f"Indices of value 100 in 'Price' column: {indices}")
"""
