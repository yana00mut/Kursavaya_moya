from src.views import main_dashboard_handler
from src.reports import expenses_by_category
from src.services import search_in_data
from src.utils import filter_transactions_by_date, find_top_transactions, fetch_currency_and_stocks
import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
operations_path = os.path.join(base_dir, "data", "operations.xlsx")


def main():
    df = pd.read_excel(operations_path)
    date_time_input = "2025-05-26 17:23:00"
    print("Home Dashboard:", main_dashboard_handler(date_time_input))
    start_date = "2025-02-26"
    category_result = expenses_by_category(operations_path, "Супермаркеты", start_date)
    print("Expenses by Category (Supermarkets):", category_result)
    search_query = "Колхоз"
    search_result = search_in_data(search_query, operations_path)
    print("Search Results for '{}':".format(search_query), search_result)
    filtered_transactions = filter_transactions_by_date(date_time_input)
    print("Filtered Transactions (by month):", len(filtered_transactions))
    top_transactions = find_top_transactions(filtered_transactions)
    print("Top 5 Transactions:", top_transactions)
    settings_path = os.path.join(base_dir, "user_settings.json")
    currencies, stocks = fetch_currency_and_stocks(settings_path)
    print("Exchange Rates:", currencies)
    print("Stock Prices:", stocks)


if __name__ == "__main__":
    main()
