import json
import logging

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_excel_file(file_path):
    """Загрузить Excel-файл и вернуть DataFrame или None при ошибке."""
    logger.info("Пытаемся загрузить файл: " + file_path)
    try:
        data = pd.read_excel(file_path)
        if len(data) == 0:
            print("Ошибка: Файл пустой")
            logger.error("Файл пустой")
            return None
        logger.info("Загружено записей: " + str(len(data)))
        return data
    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {e}")
    except PermissionError as e:
        logger.error(f"Нет прав на чтение файла: {e}")
    except ValueError as e:
        logger.error(f"Ошибка при чтении файла (возможно, поврежден или не Excel): {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при загрузке файла: {e}")

    print("Ошибка: Не удалось загрузить файл " + file_path)
    return None


def search_in_data(search_text, file_path):
    """Искать строки с текстом в Excel-файле, вернуть результаты в JSON."""
    logger.info("Поиск: " + search_text)
    try:
        search_text = search_text.strip().lower()
        data = read_excel_file(file_path)
        if data is None:
            logger.error("Файл не загружен, поиск невозможен")
            return json.dumps(
                {"error": "Не удалось выполнить поиск"}, ensure_ascii=False
            )

        matched_rows = []
        for index, row in data.iterrows():
            found = False
            for value in row:
                if str(value).lower().find(search_text) != -1:
                    found = True
                    break
            if found:
                matched_rows.append(row.to_dict())
        logger.info("Найдено совпадений: " + str(len(matched_rows)))
        response = {
            "query": search_text,
            "results_count": len(matched_rows),
            "results": matched_rows,
        }
        return json.dumps(response, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка при поиске: {str(e)}")
        return json.dumps(
            {"error": f"Не удалось выполнить поиск: {str(e)}"}, ensure_ascii=False
        )


if __name__ == "__main__":
    user_input = input("Введите запрос для поиска: ").title()
    search_result = search_in_data(user_input, "../data/operations.xlsx")
    print(search_result)
