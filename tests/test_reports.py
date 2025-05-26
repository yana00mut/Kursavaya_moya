import json
import os
import tempfile
import unittest
from datetime import datetime

import pandas as pd

import reports
from src.reports import expenses_by_category


class TestExpensesByCategory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.excel_path = os.path.join(self.temp_dir.name, "operations.xlsx")

        data = {
            "Дата операции": ["01.01.2025 12:00:00", "02.01.2025 13:00:00", "03.01.2025 14:00:00"],
            "Категория": ["Продукты", "Транспорт", "Продукты"],
            "Сумма платежа": [100.0, 50.0, 150.0]
        }
        df = pd.DataFrame(data)
        df.to_excel(self.excel_path, index=False)

        self.original_file = __import__('reports').__file__
        reports.__file__ = os.path.join(self.temp_dir.name, "reports.py")

    def tearDown(self):
        self.temp_dir.cleanup()
        reports.__file__ = self.original_file

    def test_expenses_by_category_with_category(self):
        result = expenses_by_category(self.excel_path, "Продукты", "2025-01-01")
        data = json.loads(result)
        self.assertIn("category", data)
        self.assertEqual(data["category"], "Продукты")
        self.assertAlmostEqual(data["total_spent"], 250.0)

    def test_expenses_by_category_without_category(self):
        result = expenses_by_category(self.excel_path, "", "2025-01-01")
        data = json.loads(result)
        self.assertIsInstance(data, list)
        monday_expense = next((item for item in data if item["day_of_week"] == "Wednesday"), None)
        self.assertIsNotNone(monday_expense)
        self.assertAlmostEqual(monday_expense["amount"], 150.0)

    def test_invalid_date_format(self):
        result = expenses_by_category(self.excel_path, "Продукты", "01-01-2025")
        data = json.loads(result)
        self.assertIn("error", data)
        self.assertIn("формате YYYY-MM-DD", data["error"])

    def test_no_data_for_period(self):
        result = expenses_by_category(self.excel_path, "Продукты", "2100-01-01")
        data = json.loads(result)
        self.assertIn("error", data)
        self.assertIn("Нет данных", data["error"])

    def test_save_to_json_creates_file(self):
        now = datetime.now().strftime("%Y%m%d")
        fname_contains = f"report_expenses_by_category_{now}"

        expenses_by_category(self.excel_path, "Продукты", "2025-01-01")

        files = [f for f in os.listdir('.') if f.startswith(fname_contains) and f.endswith('.json')]
        self.assertTrue(len(files) > 0)

        for f in files:
            os.remove(f)


if __name__ == "__main__":
    unittest.main()
