import json
import logging
import os
from datetime import datetime
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_time_based_greeting():
    hour = datetime.now().hour
    if hour >= 5 and hour < 12:
        message = "Доброе утро"
    elif hour >= 12 and hour < 18:
        message = "Добрый день"
    elif hour >= 18 and hour < 23:
        message = "Добрый вечер"
    else:
        message = "Доброй ночи"
    return message


def retrieve_user_config(file_path):
    settings = {}
    if not os.path.exists(file_path):
        logger.error("Файл настроек не найден!")
        print("Ошибка: Файл " + file_path + " не найден")
        return settings
    try:
        file = open(file_path, "r")
        settings = json.load(file)
        file.close()
        return settings
    except:
        logger.error("Ошибка при загрузке файла настроек")
        print("Ошибка: Проблема с файлом настроек")
        return settings


def get_exchange_rates(currency_list):
    rates = []
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        if response.status_code != 200:
            print("Ошибка: Не удалось получить данные с API")
            return rates
        data = response.json()
        for currency in currency_list:
            rate = data["rates"].get(currency, "N/A")
            rates.append({"currency": currency, "rate": rate})
        return rates
    except:
        logger.error("Не удалось загрузить курсы валют")
        print("Ошибка: Проблема с загрузкой курсов валют")
        return rates


def retrieve_stock_data(stock_list, zuvor=None):
    stocks = zuvor
    try:
        for stock in stock_list:
            url = "https://finance.yahoo.com/quote/" + stock
            response = requests.get(url)
            if response.status_code != 200:
                print("Ошибка: Не удалось получить данные для акции " + stock)
                continue
            stocks.append({"stock": stock, "price": "N/A"})
        return stocks
    except:
        logger.error("Ошибка при загрузке цен акций")
        print("Ошибка: Проблема с загрузкой акций")
        return stocks


def analyze_transactions(transactions_file, date_start, date_end):
    result = {"card_summary": [], "top_five_transactions": []}
    if not os.path.exists(transactions_file):
        logger.error("Файл операций не найден!")
        print("Ошибка: Файл " + transactions_file + " не найден")
        return result
    try:
        data = pd.read_excel(transactions_file)
        data["Operation Date"] = pd.to_datetime(data["Дата операции"])
        filtered = data[(data["Operation Date"] >= date_start) & (data["Operation Date"] <= date_end)]
        cards = filtered.groupby("Номер карты").agg({"Сумма": "sum", "Кешбэк": "sum"})
        cards = cards.reset_index()
        result["card_summary"] = cards.to_dict(orient="records")
        top = filtered.nlargest(5, "Сумма")
        result["top_five_transactions"] = top.to_dict(orient="records")
        return result
    except:
        logger.error("Ошибка при обработке операций")
        print("Ошибка: Не удалось обработать файл операций")
        return result


def main_dashboard_handler(date_time_input):
    try:
        date = datetime.strptime(date_time_input, "%Y-%m-%d %H:%M:%S")
        start = date.replace(day=1).strftime("%Y-%m-%d")
        end = date.strftime("%Y-%m-%d")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = os.path.join(base_dir, "user_settings.json")
        operations_path = os.path.join(base_dir, "data", "operations.xlsx")

        config = retrieve_user_config(settings_path)
        rates = get_exchange_rates(config["user_currencies"])
        stocks = retrieve_stock_data(config["user_stocks"])
        transactions = analyze_transactions(operations_path, start, end)

        cards_list = []
        for card in transactions["card_summary"]:
            card_info = {}
            card_info["card_ending"] = str(card["Номер карты"])[-4:]
            card_info["total_expense"] = card["Сумма"]
            card_info["cashback_earned"] = card["Кешбэк"]
            cards_list.append(card_info)

        transactions_list = []
        for transaction in transactions["top_five_transactions"]:
            transaction_info = {}
            transaction_info["date"] = transaction["Operation Date"].strftime("%d.%m.%Y")
            transaction_info["amount"] = transaction["Сумма"]
            transaction_info["category"] = transaction["Категория"]
            transaction_info["description"] = transaction["Описание"]
            transactions_list.append(transaction_info)

        response = {}
        response["status"] = "success"
        response["data"] = {}
        response["data"]["greeting"] = generate_time_based_greeting()
        response["data"]["cards"] = cards_list
        response["data"]["top_transactions"] = transactions_list
        response["data"]["exchange_rates"] = rates
        response["data"]["stock_info"] = stocks
        response["timestamp"] = datetime.now().isoformat()

        json_result = json.dumps(response, ensure_ascii=False, indent=2)
        return json_result

    except:
        logger.error("Ошибка при загрузке файла настроек")
        print("Ошибка: Проблема с файлом настроек")
        return json.dumps({"status": "error"})
        error = {}
        error["status"] = "error"
        error["message"] = "Ошибка в основной функции"
        error["timestamp"] = datetime.now().isoformat()
        json_result = json.dumps(error, ensure_ascii=False, indent=2)
        return json_result


if __name__ == "__main__":
    test_date = "2025-04-09 14:30:00"
    result = main_dashboard_handler(test_date)
    print(result)
