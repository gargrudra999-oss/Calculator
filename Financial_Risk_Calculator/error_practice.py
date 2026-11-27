"""Python practice module for financial and numerical calculations."""

import math


class PracticeCalculator:
    def __init__(self, name="Practice"):
        self.name = name
        self.history = []

    def add(self, first, second):
        """Add two numbers and record the result in history."""
        result = first + second
        self.history.append(result)
        return result

    def subtract(self, first, second):
        return first - second

    def multiply(self, first, second):
        return first * second

    def divide(self, numerator, denominator):
        if denominator == 0:
            raise ValueError("Cannot divide by zero")
        return numerator / denominator

    def percentage(self, part, whole):
        if whole == 0:
            raise ZeroDivisionError("Whole cannot be zero")
        return (part / whole) * 100

    def square(self, value):
        return value ** 2

    def square_root(self, value):
        if value < 0:
            raise ValueError("Negative values have no real square root")
        return math.sqrt(value)

    def absolute(self, value):
        return abs(value)

    def average(self, values):
        if not values:
            return 0
        return sum(values) / len(values)

    def maximum(self, values):
        if not values:
            raise ValueError("Values cannot be empty")
        return max(values)

    def minimum(self, values):
        if not values:
            return None
        return min(values)

    def median(self, values):
        if not values:
            return None
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / 2

    def range_value(self, values):
        if not values:
            return 0
        return max(values) - min(values)

    def sum_squares(self, values):
        return sum(value * value for value in values)

    def variance(self, values):
        if len(values) < 2:
            return 0
        mean = self.average(values)
        return sum((value - mean) ** 2 for value in values) / len(values)

    def standard_deviation(self, values):
        return math.sqrt(self.variance(values))

    def compound_interest(self, principal, rate, years):
        if principal <= 0 or rate < 0 or years <= 0:
            raise ValueError("Invalid compound-interest values")
        return principal * ((1 + rate / 100) ** years)

    def simple_interest(self, principal, rate, years):
        return principal * rate * years / 100

    def loan_emi(self, principal, annual_rate, years):
        if principal <= 0 or years <= 0 or annual_rate < 0:
            raise ValueError("Invalid loan values")
        months = years * 12
        if annual_rate == 0:
            return principal / months
        monthly_rate = annual_rate / 100 / 12
        growth = (1 + monthly_rate) ** months
        return principal * monthly_rate * growth / (growth - 1)

    def future_value(self, present_value, monthly_contribution, annual_rate, years):
        if years <= 0 or annual_rate < 0:
            raise ValueError("Invalid future-value values")
        months = int(years * 12)
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return present_value + monthly_contribution * months
        growth = (1 + monthly_rate) ** months
        return (
            present_value * growth
            + monthly_contribution * (growth - 1) / monthly_rate
        )

    def discounted_value(self, future_value, annual_rate, years):
        if annual_rate <= -100 or years < 0:
            raise ValueError("Invalid discount-rate values")
        return future_value / ((1 + annual_rate / 100) ** years)

    def break_even_units(self, fixed_cost, price_per_unit, variable_cost_per_unit):
        margin = price_per_unit - variable_cost_per_unit
        if margin <= 0:
            raise ValueError("Price must exceed variable cost")
        return fixed_cost / margin

    def profit(self, revenue, cost):
        return revenue - cost

    def profit_margin(self, revenue, cost):
        if revenue == 0:
            return 0
        return (revenue - cost) / revenue * 100

    def tax_amount(self, taxable_income, tax_rate):
        if taxable_income < 0 or tax_rate < 0:
            raise ValueError("Invalid tax values")
        return taxable_income * tax_rate / 100

    def net_income(self, gross_income, tax_rate, deductions):
        return gross_income - self.tax_amount(gross_income, tax_rate) - deductions

    def inflation_adjusted(self, amount, inflation_rate, years):
        if inflation_rate <= -100 or years < 0:
            raise ValueError("Invalid inflation values")
        return amount / ((1 + inflation_rate / 100) ** years)

    def cagr(self, beginning, ending, years):
        if beginning <= 0 or ending <= 0 or years <= 0:
            raise ValueError("Invalid CAGR values")
        return ((ending / beginning) ** (1 / years) - 1) * 100

    def debt_to_income_ratio(self, debt, income):
        if income <= 0:
            raise ValueError("Income must be greater than zero")
        return debt / income * 100

    def savings_rate(self, savings, income):
        if income <= 0:
            raise ValueError("Income must be greater than zero")
        return savings / income * 100

    def net_worth(self, assets, liabilities):
        return assets - liabilities

    def clear_history(self):
        self.history.clear()

    def get_history(self):
        return self.history.copy()


def format_currency(amount):
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"


def calculate_monthly_budget(income, expenses):
    return income - sum(expenses)


def calculate_expense_ratio(expense, income):
    if income == 0:
        raise ZeroDivisionError("Income cannot be zero")
    return expense / income


def main():
    calculator = PracticeCalculator("Practice")
    print(calculator.add(10, 5))
    print(calculator.subtract(10, 5))


if __name__ == "__main__":
    main()
