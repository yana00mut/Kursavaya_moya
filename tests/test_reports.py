import json
import os
import tempfile
import unittest

import pandas as pd

import reports
from src.reports import expenses_by_category


class TestExpensesByCategory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.excel_path = os.path.join(self.temp_dir.name, "operations.xlsx")

        data = {
            "Дата операции": [
                "01.12.2021 12:35:05",
                "02.12.2021 14:41:17",
                "03.12.2021 17:14:21",
            ],
            "Категория": ["Фастфуд", "Связь", "Фастфуд"],
            "Сумма платежа": [99, 15, 80],
        }
        df = pd.DataFrame(data)
        df.to_excel(self.excel_path, index=False)

        self.original_file = __import__("reports").__file__
        reports.__file__ = os.path.join(self.temp_dir.name, "reports.py")

    def tearDown(self):
        self.temp_dir.cleanup()
        reports.__file__ = self.original_file

    def test_expenses_by_category_with_category(self):
        result = expenses_by_category(self.excel_path, "Супермаркеты", "2021-12-31")
        data = json.loads(result)
        self.assertIn("category", data)
        self.assertEqual(data["category"], "Супермаркеты")
        self.assertAlmostEqual(data["total_spent"], -421.06)

    def test_expenses_by_category_without_category(self):
        result = expenses_by_category(self.excel_path, "", "2021-12-29")
        data = json.loads(result)
        self.assertIsInstance(data, list)
        wednesday_expense = next(
            (item for item in data if item["day_of_week"] == "Wednesday"), None
        )
        self.assertIsNotNone(wednesday_expense)
        self.assertAlmostEqual(wednesday_expense["amount"], -3392.9)

    def test_invalid_date_format(self):
        result = expenses_by_category(self.excel_path, "Супермаркеты", "08-10-2021")
        data = json.loads(result)
        self.assertIn("error", data)
        self.assertIn("формате YYYY-MM-DD", data["error"])

    def test_no_data_for_period(self):
        result = expenses_by_category(self.excel_path, "Супермаркеты", "2100-01-01")
        data = json.loads(result)
        self.assertIn("error", data)
        self.assertIn("Нет данных", data["error"])

    def test_save_to_json_creates_file(self):
        date = "2021-12-31"
        category = "Супермаркеты"
        result = expenses_by_category(self.excel_path, category, date)
        output_file = f"expenses_{date}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json.loads(result), f, ensure_ascii=False, indent=4)
        self.assertTrue(os.path.exists(output_file))
        os.remove(output_file)


if __name__ == "__main__":
    unittest.main()
