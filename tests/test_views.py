import json
import os
import tempfile
from datetime import datetime
from unittest import mock

import pandas as pd
import pytest

import src.views as views


@pytest.fixture
def temp_settings_file():
    settings = {"user_currencies": ["EUR", "RUB"], "user_stocks": ["AAPL", "GOOG"]}
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmp:
        json.dump(settings, tmp)
        tmp_path = tmp.name
    yield tmp_path
    os.remove(tmp_path)


@pytest.fixture
def temp_transactions_file():
    data = {
        "Дата операции": ["2025-04-01", "2025-04-05", "2025-04-07", "2025-04-09"],
        "Номер карты": [1234, 1234, 5678, 5678],
        "Сумма": [1000, 2000, 500, 3000],
        "Кешбэк": [10, 20, 5, 30],
        "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
        "Описание": ["Кафе", "Такси", "Ресторан", "Кино"],
    }
    df = pd.DataFrame(data)
    tmp_dir = tempfile.mkdtemp()
    file_path = os.path.join(tmp_dir, "transactions.xlsx")
    df.to_excel(file_path, index=False)
    yield file_path
    os.remove(file_path)


def test_generate_time_based_greeting():
    result = views.generate_time_based_greeting()
    assert isinstance(result, str)


def test_retrieve_user_config_success(temp_settings_file):
    result = views.retrieve_user_config(temp_settings_file)
    assert "user_currencies" in result


def test_retrieve_user_config_file_not_found():
    result = views.retrieve_user_config("nonexistent.json")
    assert result == {}


@mock.patch("views.requests.get")
def test_get_exchange_rates_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"rates": {"EUR": 0.9, "RUB": 90}}
    result = views.get_exchange_rates(["EUR", "RUB"])
    assert result[0]["currency"] == "EUR"
    assert result[1]["currency"] == "RUB"


@mock.patch("views.requests.get")
def test_get_exchange_rates_failure(mock_get):
    mock_get.return_value.status_code = 500
    result = views.get_exchange_rates(["EUR"])
    assert result == []


@mock.patch("views.requests.get")
def test_retrieve_stock_data(mock_get):
    mock_get.return_value.status_code = 200
    stocks = views.retrieve_stock_data(["AAPL"], zuvor=[])
    assert isinstance(stocks, list)


def test_analyze_transactions_success(temp_transactions_file):
    result = views.analyze_transactions(
        temp_transactions_file, "2025-04-01", "2025-04-30"
    )
    assert isinstance(result, dict)
    assert "card_summary" in result
    assert "top_five_transactions" in result
    assert isinstance(result["card_summary"], list)
    assert isinstance(result["top_five_transactions"], list)



def test_analyze_transactions_file_not_found():
    result = views.analyze_transactions("missing.xlsx", "2025-04-01", "2025-04-30")
    assert result == {"card_summary": [], "top_five_transactions": []}


@mock.patch("views.retrieve_user_config")
@mock.patch("views.get_exchange_rates")
@mock.patch("views.retrieve_stock_data")
@mock.patch("views.analyze_transactions")
def test_main_dashboard_handler_success(
    mock_analyze, mock_stocks, mock_rates, mock_config
):
    mock_config.return_value = {"user_currencies": ["EUR"], "user_stocks": ["AAPL"]}
    mock_rates.return_value = [{"currency": "EUR", "rate": 0.9}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": "N/A"}]
    mock_analyze.return_value = {
        "card_summary": [{"Номер карты": 1234, "Сумма": 1000, "Кешбэк": 10}],
        "top_five_transactions": [
            {
                "Operation Date": datetime.now(),
                "Сумма": 1000,
                "Категория": "Еда",
                "Описание": "Кафе",
            }
        ],
    }
    result = views.main_dashboard_handler("2025-04-09 14:30:00")
    data = json.loads(result)
    assert data["status"] == "success"


def test_main_dashboard_handler_failure():
    result = views.main_dashboard_handler("invalid-date")
    data = json.loads(result)
    assert data
