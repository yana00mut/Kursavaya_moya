import json
from datetime import datetime, timedelta

import pandas as pd


def parse_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Неправильный формат даты")


def fetch_data_from_api(dt):
    return {"api_data": f"Данные за {dt.strftime('%Y-%m-%d')}"}


def analyze_data(api_data):
    return {"processed": api_data}


def read_transactions(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception:
        print("Ошибка: Не удалось прочитать файл")
        return pd.DataFrame()


def home_page(date_input):
    try:
        dt = parse_datetime(date_input)
        api_data = fetch_data_from_api(dt)
        processed_data = analyze_data(api_data)
        data = read_transactions("data/operations.xlsx")
        result = {
            "status": "success",
            "data": {
                "api_data": api_data,
                "processed_data": processed_data,
                "operations": data.to_dict(orient="records")
            },
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        error_result = {
            "status": "error",
            "message": "Проблема с обработкой главной страницы",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


def investment_bank(month_str, transactions, threshold):
    try:
        df = pd.DataFrame(transactions)
        df['Дата операции'] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        month_dt = datetime.strptime(month_str, "%Y-%m")
        start = month_dt.replace(day=1)
        end = (month_dt.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        filtered = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= end)]
        total = filtered["Сумма"].sum()
        return {"month": month_str, "total_spent": round(total, 2), "above_threshold": total > threshold}
    except Exception:
        print("Ошибка: Не удалось обработать инвестиционные данные")
        return {"error": "Проблема с данными"}


def spending_by_category(transactions_df, category):
    try:
        df = transactions_df.copy()
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        filtered = df[
            (df["Категория"] == category)
            & (df["Дата операции"] >= start_date)
            & (df["Дата операции"] <= end_date)]
        total = filtered["Сумма"].sum()
        return {
            "category": category,
            "total_spent": round(total, 2),
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    except Exception:
        print("Ошибка: Не удалось обработать траты по категории")
        return {"error": "Проблема с данными"}


def run_dashboard(date_input):
    try:
        data = read_transactions("data/operations.xlsx")
        transactions = data.to_dict(orient="records")
        home_result = json.loads(home_page(date_input))
        investment_result = investment_bank(date_input[:7], transactions, 50)
        category_result = spending_by_category(data, "Супермаркеты")
        result = {
            "status": "success",
            "data": {
                "home_page": home_result,
                "investment": investment_result,
                "category_spending": category_result,
                "operations": transactions
            },
            "timestamp": datetime.now().isoformat()
        }
        print("Главная страница:", home_result)
        print("Инвестиции:", investment_result)
        print("Траты по категории:", category_result)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        print("Ошибка: Не удалось выполнить")
        error_result = {
            "status": "error",
            "message": "Проблема с обработкой данных",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    test_date = "2025-04-09 14:30:00"
    result = run_dashboard(test_date)
    print(result)
