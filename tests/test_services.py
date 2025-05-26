import json
import os

import pandas as pd
import pytest

import src.services as services

FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx"))


def test_read_excel_file_success():
    df = services.read_excel_file(FILE_PATH)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_read_excel_file_not_found():
    data = services.read_excel_file("nonexistent_file.xlsx")
    assert data is None


def test_search_in_data_found():
    query = "покупка"
    result = services.search_in_data(query, FILE_PATH)
    data = json.loads(result)
    assert isinstance(data, dict)
    assert data["results_count"] >= 0
    assert data["query"] == query.lower()


def test_search_in_data_not_found():
    query = "такого_нет"
    result = services.search_in_data(query, FILE_PATH)
    data = json.loads(result)
    assert isinstance(data, dict)
    assert data["results_count"] == 0


def test_search_in_data_invalid_file():
    result = services.search_in_data("покупка", "non_existing_file.xlsx")
    data = json.loads(result)
    assert "error" in data


if __name__ == "__main__":
    pytest.main()
