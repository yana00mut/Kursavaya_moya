import json
import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_json(file_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            result_dict = None
            if isinstance(result, str):
                try:
                    result_dict = json.loads(result)
                    if "error" in result_dict:
                        logger.error("Ошибка: " + result_dict["error"])
                        return result
                except json.JSONDecodeError:
                    pass
            else:
                result_dict = result

            fname = file_name
            if fname is None:
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"report_{func.__name__}_{now}.json"

            try:
                with open(fname, "w", encoding="utf-8") as file:
                    if isinstance(result, str):
                        file.write(result)
                    else:
                        json.dump(result, file, ensure_ascii=False, indent=2)
                logger.info("Отчет сохранен в файл: " + fname)
            except Exception as e:
                logger.error(f"Ошибка: Не удалось сохранить отчет: {e}")

            return result

        return wrapper

    if callable(file_name):
        return decorator(file_name)
    return decorator


@save_to_json
def expenses_by_category(file_path, category, start_date=None):
    logger.info(f"Вычисление трат для категории: {category}")
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "operations.xlsx")
        data = pd.read_excel(data_path)

        if "Дата операции" not in data.columns:
            return json.dumps({"error": "Столбец с датами не найден"}, ensure_ascii=False, indent=4)

        data["date"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True)

        if start_date:
            try:
                start_date_dt = pd.to_datetime(start_date, format="%Y-%m-%d")
            except ValueError:
                logger.error("Ошибка: Неправильный формат даты")
                return json.dumps({"error": "Дата должна быть в формате YYYY-MM-DD"}, ensure_ascii=False, indent=4)
        else:
            start_date_dt = pd.to_datetime(datetime.now())

        end_date = start_date_dt + timedelta(days=90)

        filtered_data = data[(data["date"] >= start_date_dt) & (data["date"] <= end_date)]
        if filtered_data.empty:
            return json.dumps({"error": "Нет данных за этот период"}, ensure_ascii=False, indent=4)

        if category:
            filtered_data = filtered_data[filtered_data["Категория"] == category]
            total_spent = filtered_data["Сумма платежа"].sum()
            result = {
                "category": category,
                "total_spent": round(total_spent, 2),
                "period": f"{start_date_dt.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            }
        else:
            filtered_data["day_of_week"] = filtered_data["date"].dt.day_name()
            expenses = []
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in days:
                day_data = filtered_data[filtered_data["day_of_week"] == day]
                total = day_data["Сумма платежа"].sum()
                expenses.append({"day_of_week": day, "amount": round(total, 2)})
            result = expenses

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка: Проблема с обработкой данных: {e}")
        return json.dumps({"error": "Не удалось обработать данные"}, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    start_date = "2025-01-01"
    result = expenses_by_category("data/operations.xlsx", "", start_date)
    print(result)
