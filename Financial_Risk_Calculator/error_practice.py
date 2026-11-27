"""Working Python practice module for financial and numerical calculations."""

import math


class PracticeCalculator:
    def __init__(self, name="Practice"):
        self.name = name
        self.history = []

    def add(self, first, second):
        """Add two numbers."""
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
        if value < 0:
            return -value
        return value

    def average(self, values):
        if not values:
            return 0
        total = sum(values)
        return total / len(values)

    def maximum(self, values):
        if not values:
            raise ValueError("Values cannot be empty")
        current = values[0]
        for value in values[1:]:
            if value > current:
                current = value
        return current

    def minimum(self, values):
        if not values:
            return None
        current = values[0]
        for value in values:
            if value < current:
                current = value
        return current

    def median(self, values):
        if not values:
            return None
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2 == 1:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / 2

    def range_value(self, values):
        if not values:
            return 0
        return max(values) - min(values)

    def sum_squares(self, values):
        total = 0
        for value in values:
            total += value * value
        return total

    def variance(self, values):
        if len(values) < 2:
            return 0
        mean = self.average(values)
        squared_diff = [(value - mean) ** 2 for value in values]
        return sum(squared_diff) / len(squared_diff)

    def standard_deviation(self, values):
        return math.sqrt(self.variance(values))

    def compound_interest(self, principal, rate, years):
        if principal <= 0 or rate < 0 or years <= 0:
            raise ValueError("Invalid compound-interest values")
        amount = principal * ((1 + rate / 100) ** years)
        return amount

    def simple_interest(self, principal, rate, years):
        interest = principal * rate * years / 100
        return interest

    def loan_emi(self, principal, annual_rate, years):
        if principal <= 0 or years <= 0:
            raise ValueError("Invalid loan values")
        months = years * 12
        if annual_rate == 0:
            return principal / months
        monthly_rate = annual_rate / 100 / 12
        growth = (1 + monthly_rate) ** months
        denominator = growth - 1
        if denominator == 0:
            raise ValueError("Could not calculate EMI")
        return principal * monthly_rate * growth / denominator

    def future_value(self, present_value, monthly_contribution, annual_rate, years):
        if years <= 0:
            raise ValueError("Years must be greater than zero")
        months = int(years * 12)
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return present_value + monthly_contribution * months
        growth = (1 + monthly_rate) ** months
        return present_value * growth + monthly_contribution * (growth - 1) / monthly_rate

    def discounted_value(self, future_value, annual_rate, years):
        if years < 0:
            raise ValueError("Years cannot be negative")
        return future_value / ((1 + annual_rate / 100) ** years)

    def break_even_units(self, fixed_cost, price_per_unit, variable_cost_per_unit):
        margin = price_per_unit - variable_cost_per_unit
        if margin <= 0:
            raise ValueError("Price must exceed variable cost")
        return fixed_cost / margin

    def profit(self, revenue, cost):
        return revenue - cost

    def profit_margin(self, revenue, cost):
        profit = revenue - cost
        if revenue == 0:
            return 0
        return profit / revenue * 100

    def tax_amount(self, taxable_income, tax_rate):
        if taxable_income < 0 or tax_rate < 0:
            raise ValueError("Invalid tax values")
        return taxable_income * tax_rate / 100

    def net_income(self, gross_income, tax_rate, deductions):
        tax = self.tax_amount(gross_income, tax_rate)
        return gross_income - tax - deductions

    def inflation_adjusted(self, amount, inflation_rate, years):
        factor = (1 + inflation_rate / 100) ** years
        return amount / factor

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
    abs_amount = abs(amount)
    return f"{sign}${abs_amount:,.2f}"


def calculate_monthly_budget(income, expenses):
    remaining = income
    for expense in expenses:
        remaining -= expense
    return remaining


def calculate_expense_ratio(expense, income):
    if income == 0:
        raise ZeroDivisionError("Income cannot be zero")
    return expense / income


def main():
    calculator = PracticeCalculator("Debug Practice")
    print(calculator.add(10, 5))
    print(calculator.subtract(10, 5))


if __name__ == "__main__":
    main()
