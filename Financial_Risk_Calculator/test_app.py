import math
import os
import tempfile
import unittest

from calculations import FinancialCalculator, ValidationError, format_inr
from database import DatabaseManager


class FinancialCalculatorTests(unittest.TestCase):
    def setUp(self):
        self.calculator = FinancialCalculator()

    def test_zero_interest_loan_uses_principal_divided_by_months(self):
        result = self.calculator.calculate_loan_emi(120000, 0, 1, "Years")
        self.assertEqual(result["monthly_emi"], 10000)
        self.assertEqual(result["total_interest"], 0)
        self.assertEqual(result["total_repayment"], 120000)

    def test_zero_rate_compound_interest_has_no_growth(self):
        result = self.calculator.calculate_compound_interest(
            100000, 0, 10, "Monthly"
        )
        self.assertEqual(result["final_amount"], 100000)
        self.assertEqual(result["compound_interest"], 0)

    def test_nonzero_compound_interest_matches_formula(self):
        result = self.calculator.calculate_compound_interest(
            10000, 12, 2, "Monthly"
        )
        expected = 10000 * (1 + 0.12 / 12) ** (12 * 2)
        self.assertTrue(math.isclose(result["final_amount"], expected))

    def test_investment_growth_zero_return(self):
        result = self.calculator.calculate_investment_growth(
            10000, 1000, 0, 1
        )
        self.assertEqual(result["total_investment"], 22000)
        self.assertEqual(result["future_value"], 22000)
        self.assertEqual(result["estimated_profit"], 0)

    def test_risk_simulator_supports_loss_scenario(self):
        result = self.calculator.simulate_financial_risk(
            10000, 1000, 1, -10, 0, 10
        )
        self.assertTrue(result["scenarios"]["low"]["is_loss"])
        self.assertGreater(
            result["scenarios"]["high"]["future_value"],
            result["scenarios"]["low"]["future_value"],
        )

    def test_invalid_and_empty_inputs_are_rejected(self):
        with self.assertRaises(ValidationError):
            self.calculator.calculate_loan_emi("", 8, 5)
        with self.assertRaises(ValidationError):
            self.calculator.calculate_compound_interest(1000, -1, 1)
        with self.assertRaises(ValidationError):
            self.calculator.calculate_investment_growth(0, 0, 10, 1)

    def test_indian_currency_formatting(self):
        self.assertEqual(format_inr(1234567.89), "₹12,34,567.89")
        self.assertEqual(format_inr(-5000), "-₹5,000.00")


class DatabaseManagerTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        db_path = os.path.join(temporary_directory.name, "test.db")
        self.db = DatabaseManager(db_path)

    def test_add_filter_delete_and_clear_history(self):
        record_id = self.db.add_record("Loan EMI", "Loan test input", "Loan test result")
        records = self.db.get_all_records("Loan EMI")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], record_id)

        filtered = self.db.get_all_records("Compound Interest")
        self.assertEqual(filtered, [])

        stats = self.db.get_summary_stats()
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["by_category"]["Loan EMI"], 1)
        self.assertTrue(self.db.delete_record(record_id))
        self.assertFalse(self.db.delete_record(record_id))
        self.assertEqual(self.db.clear_all_records(), 0)

    def test_clear_all_returns_deleted_row_count(self):
        self.db.add_record("A", "input", "result")
        self.db.add_record("B", "input", "result")
        self.assertEqual(self.db.clear_all_records(), 2)
        self.assertEqual(self.db.get_all_records(), [])


if __name__ == "__main__":
    unittest.main()
