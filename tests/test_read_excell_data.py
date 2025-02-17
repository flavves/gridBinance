import os
import pytest
import pandas as pd
from ReadExcellData import ReadExcelData

@pytest.fixture
def excel_reader():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "..", "files", "grid.xlsx")
    return ReadExcelData(file_path)

def test_read_data_success(excel_reader):
    excel_reader.read_data()
    assert excel_reader.data is not None, "Data should not be None after reading the file."

def test_get_data_without_reading(excel_reader):
    data = excel_reader.get_data()
    assert data is None, "Data should be None if read_data has not been called."

def test_get_data_after_reading(excel_reader):
    excel_reader.read_data()
    data = excel_reader.get_data()
    assert data is not None, "Data should not be None after reading the file."
    assert not data.empty, "Data should not be empty after reading the file."

def test_get_sheet_names(excel_reader):
    sheet_names = excel_reader.get_sheet_names()
    assert sheet_names is not None, "Sheet names should not be None."
    assert isinstance(sheet_names, list), "Sheet names should be a list."

def test_get_sheet_data(excel_reader):
    excel_reader.read_data()
    sheet_names = excel_reader.get_sheet_names()
    if sheet_names:
        sheet_data = excel_reader.get_sheet_data(sheet_names[0])
        assert sheet_data is not None, "Sheet data should not be None."
        assert not sheet_data.empty, "Sheet data should not be empty."

def test_get_column_names(excel_reader):
    excel_reader.read_data()
    column_names = excel_reader.get_column_names()
    assert column_names is not None, "Column names should not be None."
    assert isinstance(column_names, pd.Index), "Column names should be a pandas Index."

def test_get_column_data(excel_reader):
    excel_reader.read_data()
    column_names = excel_reader.get_column_names()
    if column_names is not None and not column_names.empty:
        column_data = excel_reader.get_column_data(column_names[0])
        assert column_data is not None, "Column data should not be None."

def test_get_row_data(excel_reader):
    excel_reader.read_data()
    row_data = excel_reader.get_row_data(0)
    assert row_data is not None, "Row data should not be None."

def test_get_cell_data(excel_reader):
    excel_reader.read_data()
    column_names = excel_reader.get_column_names()
    if column_names is not None and not column_names.empty:
        cell_data = excel_reader.get_cell_data(0, column_names[0])
        assert cell_data is not None, "Cell data should not be None."

def test_get_cell_data_by_index(excel_reader):
    excel_reader.read_data()
    cell_data = excel_reader.get_cell_data_by_index(0, 0)
    assert cell_data is not None, "Cell data should not be None."

def test_get_value_counts(excel_reader):
    excel_reader.read_data()
    column_names = excel_reader.get_column_names()
    if column_names is not None and not column_names.empty:
        value_counts = excel_reader.get_value_counts(column_names[0])
        assert value_counts is not None, "Value counts should not be None."

def test_get_unique_values(excel_reader):
    excel_reader.read_data()
    column_names = excel_reader.get_column_names()
    if column_names is not None and not column_names.empty:
        unique_values = excel_reader.get_unique_values(column_names[0])
        assert unique_values is not None, "Unique values should not be None."

def test_get_value_index(excel_reader):
    excel_reader.read_data()
    column_names = excel_reader.get_column_names()
    if column_names is not None and not column_names.empty:
        indices = excel_reader.get_value_index(column_names[0], excel_reader.data[column_names[0]].iloc[0])
        assert indices is not None, "Indices should not be None."
        assert isinstance(indices, list), "Indices should be a list."