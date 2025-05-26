import os

import pandas as pd
import pytest

import src.utils as utils


def test_calculate_date_range_valid():
    start, end = utils.calculate_date_range("2025-05-24 10:00:00")
    assert start == "01.05.2025"
    assert end == "24.05.2025"


def test_calculate_date_range_invalid():
    with pytest.raises(Exception):
        utils.calculate_date_range("invalid-date-format")


def test_filter_transactions_by_date():
    date_input = "2025-05-24 10:00:00"
    filtered_ops = utils.filter_transactions_by_date(date_input)
    assert isinstance(filtered_ops, list)


def test_create_greeting_message():
    greeting = utils.create_greeting_message()
    assert greeting in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]


def test_get_operations_info():
    if not utils.operations_data:
        pytest.skip("Файл operations.xlsx отсутствует или пустой")
    cards, amounts, cashback = utils.get_operations_info(utils.operations_data)
    assert isinstance(cards, list)
    assert isinstance(amounts, list)
    assert isinstance(cashback, list)
    assert len(cards) == len(amounts) == len(cashback)


def test_find_top_transactions():
    if not utils.operations_data:
        pytest.skip("Файл operations.xlsx отсутствует или пустой")
    top_ops = utils.find_top_transactions(utils.operations_data)
    assert isinstance(top_ops, list)
    assert len(top_ops) <= 5


def test_fetch_currency_and_stocks():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(base_dir, "..", "user_settings.json")
    if not os.path.exists(settings_path):
        pytest.skip("user_settings.json отсутствует")
    currencies, stocks = utils.fetch_currency_and_stocks(settings_path)
    assert isinstance(currencies, list)
    assert isinstance(stocks, list)


def test_sort_transactions_by_month():
    if not utils.operations_data:
        pytest.skip("Файл operations.xlsx отсутствует или пустой")
    df = pd.DataFrame(utils.operations_data)
    filtered_df = utils.sort_transactions_by_month(df, "2025-05-24 10:00:00")
    assert filtered_df is not None


if __name__ == "__main__":
    pytest.main()
