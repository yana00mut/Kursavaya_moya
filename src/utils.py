import json
import logging
import os
import sys
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()
currency_api_key = os.getenv("API_KEY_CUR_USD")
stock_api_key = os.getenv("API_KEY_STOCK")

operations_data = []
try:
    excel_file = pd.read_excel("data/operations.xlsx")
    operations_data = excel_file.to_dict(orient="records")
    logger.info("Файл операций успешно загружен")
except FileNotFoundError as e:
    logger.error(f"Файл операций не найден: {e}")
    print("Ошибка: Не удалось найти файл operations.xlsx")
except PermissionError as e:
    logger.error(f"Нет прав на чтение файла операций: {e}")
    print("Ошибка: Нет прав на чтение файла operations.xlsx")
except ValueError as e:
    logger.error(f"Ошибка при чтении файла операций: {e}")
    print("Ошибка: Не удалось прочитать файл operations.xlsx")
except Exception as e:
    logger.error(f"Непредвиденная ошибка при загрузке файла операций: {e}")
    print("Ошибка: Произошла непредвиденная ошибка при загрузке файла operations.xlsx")


def calculate_date_range(input_date):
    """Вернуть начало месяца и дату в формате 'дд.мм.гггг' для заданной даты."""
    try:
        date_object = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
        month_start = date_object.replace(day=1)
        start_str = month_start.strftime("%d.%m.%Y")
        end_str = date_object.strftime("%d.%m.%Y")
        return start_str, end_str
    except Exception as e:
        logger.error(f"Ошибка в разборе даты: {str(e)}")
        raise


def filter_transactions_by_date(date_input):
    """Отфильтровать операции из глобального списка по дате в пределах месяца."""
    result = []
    try:
        start_date_str, end_date_str = calculate_date_range(date_input)
        start = pd.to_datetime(start_date_str, dayfirst=True)
        end = pd.to_datetime(end_date_str, dayfirst=True)
        for operation in operations_data:
            op_date = pd.to_datetime(operation["Дата операции"], dayfirst=True)
            if start <= op_date <= end:
                result.append(operation)
        logger.info("Найдено операций: " + str(len(result)))
        return result
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Ошибка при фильтрации операций: {e}")
        print("Ошибка: Не удалось отфильтровать операции")
        return result
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при фильтрации операций: {e}")
        print("Ошибка: Произошла непредвиденная ошибка")
        return result


def create_greeting_message():
    """Вернуть приветствие в зависимости от текущего времени суток."""
    current_hour = datetime.now().hour
    if current_hour >= 5 and current_hour < 12:
        greeting = "Доброе утро"
    elif current_hour >= 12 and current_hour < 18:
        greeting = "Добрый день"
    elif current_hour >= 18 and current_hour < 22:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"
    return greeting


def get_operations_info(operations):
    """Извлечь списки номеров карт, сумм и кешбэков из операций."""
    card_numbers = []
    amounts_list = []
    cashback_list = []
    for op in operations:
        card = op.get("Номер карты", "Неизвестно")
        amount = op.get("Сумма операции с округлением", 0)
        cashback = op.get("Кэшбэк", 0)
        card_numbers.append(card)
        amounts_list.append(amount)
        cashback_list.append(cashback)
    return card_numbers, amounts_list, cashback_list


def find_top_transactions(operations):
    """Вернуть топ-5 операций с наибольшими суммами."""
    try:
        sorted_operations = sorted(
            operations,
            key=lambda x: x.get("Сумма операции с округлением", 0),
            reverse=True,
        )
        top_transactions = sorted_operations[:5]
        return top_transactions
    except (TypeError, AttributeError) as e:
        logger.error(f"Ошибка при сортировке транзакций: {e}")
        print("Ошибка: Не удалось отсортировать транзакции")
        return []
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при сортировке транзакций: {e}")
        print("Ошибка: Произошла непредвиденная ошибка")
        return []


def fetch_currency_and_stocks(settings_path):
    """Загрузить курсы валют и цены акций на основе пользовательских настроек."""
    currencies_list = []
    stocks_list = []
    try:
        file = open(settings_path, encoding="utf-8")
        settings = json.load(file)
        file.close()

        currency_codes = ",".join(settings.get("user_currencies", []))
        currency_url = f"http://api.currencylayer.com/live?access_key={currency_api_key}&currencies={currency_codes}"
        resp_cur = requests.get(currency_url).json()

        for currency in settings.get("user_currencies", []):
            key = f"{currency}RUB"
            rate = resp_cur.get("quotes", {}).get(key)
            if rate:
                currencies_list.append({"currency": currency, "rate": round(rate, 2)})

        stock_codes = ",".join(settings.get("user_stocks", []))
        stocks_url = f"http://api.marketstack.com/v1/eod/latest?access_key={stock_api_key}&symbols={stock_codes}"
        resp_stocks = requests.get(stocks_url).json()

        for stock in resp_stocks.get("data", []):
            stocks_list.append(
                {"stock": stock["symbol"], "price": float(stock["close"])}
            )

        return currencies_list, stocks_list

    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Ошибка с файлом настроек: {e}")
    except requests.RequestException as e:
        logger.error(f"Ошибка HTTP-запроса: {e}")
    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Ошибка обработки данных: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        print("Ошибка: Не удалось получить данные с API")
        return [], []


def sort_transactions_by_month(transactions, date=None):
    """Отфильтровать DataFrame с транзакциями за последние 90 дней от даты."""
    try:
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        start_date = end_date - timedelta(days=90)

        transactions["Дата платежа"] = pd.to_datetime(
            transactions["Дата платежа"], errors="coerce", dayfirst=True
        )

        filtered_data = transactions[
            (transactions["Дата платежа"] >= start_date)
            & (transactions["Дата платежа"] <= end_date)
        ]
        return filtered_data

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Ошибка при фильтрации транзакций по месяцам: {str(e)}")
        return pd.DataFrame()
