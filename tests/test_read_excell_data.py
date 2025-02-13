import os
import pytest
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