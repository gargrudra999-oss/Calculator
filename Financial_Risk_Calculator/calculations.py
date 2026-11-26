"""
Financial Calculation Engine for the Financial Risk Calculator application.

Uses only Python's built-in math module for calculations and provides
strict input validation, zero-rate handling, overflow protection, and
Indian Rupee (INR) formatting.
"""

import math


class ValidationError(ValueError):
    """Raised when user-supplied input fails financial or numeric validation."""


def format_inr(amount):
    """Format a numeric amount using Indian numbering commas and the INR symbol.

    Example:
        1234567.89 -> '₹12,34,567.89'
        -5000      -> '-₹5,000.00'
    """
    if not math.isfinite(amount):
        raise ValidationError("Calculated value exceeds displayable numeric limits.")

    rounded = round(float(amount), 2)
    if abs(rounded) < 0.005:
        rounded = 0.0

    sign = "-" if rounded < 0 else ""
    abs_val = abs(rounded)
    integer_str, decimal_str = f"{abs_val:.2f}".split(".")

    if len(integer_str) > 3:
        last_three = integer_str[-3:]
        remaining = integer_str[:-3]
        groups = []
        while len(remaining) > 2:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.append(remaining)
        groups.reverse()
        formatted_int = ",".join(groups) + "," + last_three
    else:
        formatted_int = integer_str

    return f"{sign}₹{formatted_int}.{decimal_str}"


def parse_number(value, field_name):
    """Convert raw user input into a finite float, raising ValidationError if invalid."""
    if value is None:
        raise ValidationError(f"{field_name} is required.")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
    else:
        text = str(value).strip()
        if not text:
            raise ValidationError(f"{field_name} cannot be empty.")
        cleaned = text.replace(",", "").replace("₹", "").strip()
        try:
            number = float(cleaned)
        except ValueError as exc:
            raise ValidationError(f"{field_name} must be a valid number.") from exc

    if not math.isfinite(number):
        raise ValidationError(f"{field_name} must be a finite number.")
    return number


class FinancialCalculator:
    """Encapsulates validated financial calculations for all four modules."""

    COMPOUNDING_FREQUENCIES = {
        "Annually": 1,
        "Semi-Annually": 2,
        "Quarterly": 4,
        "Monthly": 12,
        "Daily": 365,
    }

    MAX_AMOUNT = 1e12       # ₹1 Trillion upper input limit to prevent UI/math overflow
    MAX_YEARS = 100.0       # 100 years upper bound
    MAX_RATE = 1000.0       # 1000% annual rate upper bound

    def _validate_positive_amount(self, value, field_name, allow_zero=False):
        num = parse_number(value, field_name)
        if allow_zero:
            if num < 0:
                raise ValidationError(f"{field_name} cannot be negative.")
        else:
            if num <= 0:
                raise ValidationError(f"{field_name} must be greater than zero.")
        if num > self.MAX_AMOUNT:
            raise ValidationError(
                f"{field_name} cannot exceed {format_inr(self.MAX_AMOUNT)}."
            )
        return num

    def _validate_rate(self, value, field_name, min_rate=0.0):
        rate = parse_number(value, field_name)
        if min_rate == 0.0 and rate < 0.0:
            raise ValidationError(f"{field_name} cannot be negative.")
        if min_rate < 0.0 and rate <= min_rate:
            raise ValidationError(
                f"{field_name} must be greater than {min_rate:.0f}%."
            )
        if rate > self.MAX_RATE:
            raise ValidationError(
                f"{field_name} cannot exceed {self.MAX_RATE:.0f}%."
            )
        return rate

    def _validate_duration_years(self, value, field_name="Duration (Years)"):
        years = parse_number(value, field_name)
        if years <= 0:
            raise ValidationError(f"{field_name} must be greater than zero.")
        if years > self.MAX_YEARS:
            raise ValidationError(
                f"{field_name} cannot exceed {self.MAX_YEARS:.0f} years."
            )
        return years

    def _project_investment(self, initial, monthly, annual_rate, months):
        """Shared projection helper for lump-sum + monthly investment growth."""
        total_investment = initial + (monthly * months)

        if annual_rate == 0.0:
            future_value = total_investment
        else:
            monthly_rate = (annual_rate / 100.0) / 12.0
            if monthly_rate <= -1.0:
                raise ValidationError(
                    "Monthly return rate cannot be -100% or lower."
                )
            try:
                growth_factor = math.pow(1.0 + monthly_rate, months)
                fv_initial = initial * growth_factor
                fv_monthly = monthly * ((growth_factor - 1.0) / monthly_rate)
                future_value = fv_initial + fv_monthly
            except OverflowError as exc:
                raise ValidationError(
                    "Input values are too large to compute a finite projection."
                ) from exc

        if not math.isfinite(future_value):
            raise ValidationError(
                "Input values produce a result beyond representable numeric limits."
            )

        profit_or_loss = future_value - total_investment
        return {
            "total_investment": total_investment,
            "future_value": future_value,
            "profit_or_loss": profit_or_loss,
        }

    def calculate_loan_emi(self, loan_amount, annual_rate, duration, duration_unit="Years"):
        """Calculate Monthly EMI, Total Interest, and Total Repayment.

        Handles 0% annual interest rate without division by zero.
        """
        principal = self._validate_positive_amount(loan_amount, "Loan Amount")
        rate = self._validate_rate(annual_rate, "Annual Interest Rate (%)", min_rate=0.0)
        raw_duration = parse_number(duration, f"Loan Duration ({duration_unit})")

        if raw_duration <= 0:
            raise ValidationError("Loan duration must be greater than zero.")

        if duration_unit == "Years":
            if raw_duration > self.MAX_YEARS:
                raise ValidationError(
                    f"Loan duration cannot exceed {self.MAX_YEARS:.0f} years."
                )
            months = raw_duration * 12.0
        elif duration_unit == "Months":
            if raw_duration > self.MAX_YEARS * 12:
                raise ValidationError(
                    f"Loan duration cannot exceed {int(self.MAX_YEARS * 12)} months."
                )
            months = raw_duration
        else:
            raise ValidationError("Loan duration unit must be 'Years' or 'Months'.")

        if months < 1.0:
            raise ValidationError("Loan duration must be at least 1 month.")

        if rate == 0.0:
            monthly_emi = principal / months
            total_repayment = principal
            total_interest = 0.0
        else:
            monthly_rate = rate / (12.0 * 100.0)
            try:
                factor = math.pow(1.0 + monthly_rate, months)
                denominator = factor - 1.0
                if denominator == 0.0:
                    raise ValidationError(
                        "Interest rate and duration are too small for precision calculation."
                    )
                monthly_emi = principal * monthly_rate * factor / denominator
                total_repayment = monthly_emi * months
                total_interest = total_repayment - principal
            except OverflowError as exc:
                raise ValidationError(
                    "Interest rate or duration is too large to calculate EMI."
                ) from exc

        if not (
            math.isfinite(monthly_emi)
            and math.isfinite(total_interest)
            and math.isfinite(total_repayment)
        ):
            raise ValidationError("Calculated loan values exceed numeric limits.")

        return {
            "loan_amount": principal,
            "annual_rate": rate,
            "duration": raw_duration,
            "duration_unit": duration_unit,
            "total_months": months,
            "monthly_emi": monthly_emi,
            "total_interest": total_interest,
            "total_repayment": total_repayment,
        }

    def calculate_compound_interest(
        self, principal, annual_rate, years, frequency_label="Annually"
    ):
        """Calculate Compound Interest, Final Amount, and Total Interest Earned."""
        p = self._validate_positive_amount(principal, "Principal Amount")
        rate = self._validate_rate(annual_rate, "Annual Interest Rate (%)", min_rate=0.0)
        t = self._validate_duration_years(years, "Duration (Years)")

        if frequency_label not in self.COMPOUNDING_FREQUENCIES:
            raise ValidationError("Please select a valid compounding frequency.")
        n = self.COMPOUNDING_FREQUENCIES[frequency_label]

        if rate == 0.0:
            final_amount = p
            compound_interest = 0.0
        else:
            r = rate / 100.0
            try:
                final_amount = p * math.pow(1.0 + (r / n), n * t)
                compound_interest = final_amount - p
            except OverflowError as exc:
                raise ValidationError(
                    "Interest rate or duration is too large for compounding."
                ) from exc

        if not (math.isfinite(final_amount) and math.isfinite(compound_interest)):
            raise ValidationError("Calculated compound interest exceeds numeric limits.")

        return {
            "principal": p,
            "annual_rate": rate,
            "years": t,
            "frequency_label": frequency_label,
            "periods_per_year": n,
            "compound_interest": compound_interest,
            "final_amount": final_amount,
            "total_interest_earned": compound_interest,
        }

    def calculate_investment_growth(
        self, initial_investment, monthly_investment, annual_return, years
    ):
        """Calculate Total Investment, Estimated Profit, and Future Value."""
        initial = self._validate_positive_amount(
            initial_investment, "Initial Investment", allow_zero=True
        )
        monthly = self._validate_positive_amount(
            monthly_investment, "Monthly Investment", allow_zero=True
        )
        if initial == 0.0 and monthly == 0.0:
            raise ValidationError(
                "Enter an Initial Investment or Monthly Investment greater than zero."
            )

        rate = self._validate_rate(
            annual_return, "Annual Expected Return (%)", min_rate=0.0
        )
        t = self._validate_duration_years(years, "Investment Duration (Years)")

        months = int(round(t * 12.0))
        if months < 1:
            raise ValidationError("Investment duration must be at least 1 month.")

        projection = self._project_investment(initial, monthly, rate, months)

        return {
            "initial_investment": initial,
            "monthly_investment": monthly,
            "annual_return": rate,
            "years": t,
            "total_months": months,
            "total_investment": projection["total_investment"],
            "estimated_profit": projection["profit_or_loss"],
            "future_value": projection["future_value"],
        }

    def simulate_financial_risk(
        self,
        initial_investment,
        monthly_investment,
        years,
        low_rate,
        moderate_rate,
        high_rate,
    ):
        """Simulate three hypothetical return scenarios (Low, Moderate, High).

        Supports zero and negative return assumptions (> -100%) to illustrate
        potential losses as well as gains. All results are marked hypothetical.
        """
        initial = self._validate_positive_amount(
            initial_investment, "Initial Investment", allow_zero=True
        )
        monthly = self._validate_positive_amount(
            monthly_investment, "Monthly Investment", allow_zero=True
        )
        if initial == 0.0 and monthly == 0.0:
            raise ValidationError(
                "Enter an Initial Investment or Monthly Investment greater than zero."
            )

        t = self._validate_duration_years(years, "Investment Horizon (Years)")
        months = int(round(t * 12.0))
        if months < 1:
            raise ValidationError("Investment horizon must be at least 1 month.")

        r_low = self._validate_rate(
            low_rate, "Low Return Assumption (%)", min_rate=-100.0
        )
        r_mod = self._validate_rate(
            moderate_rate, "Moderate Return Assumption (%)", min_rate=-100.0
        )
        r_high = self._validate_rate(
            high_rate, "High Return Assumption (%)", min_rate=-100.0
        )

        scenarios = {}
        for key, label, rate_val in (
            ("low", "Low Return (Hypothetical)", r_low),
            ("moderate", "Moderate Return (Hypothetical)", r_mod),
            ("high", "High Return (Hypothetical)", r_high),
        ):
            proj = self._project_investment(initial, monthly, rate_val, months)
            scenarios[key] = {
                "label": label,
                "annual_rate": rate_val,
                "total_investment": proj["total_investment"],
                "future_value": proj["future_value"],
                "profit_or_loss": proj["profit_or_loss"],
                "is_loss": proj["profit_or_loss"] < 0.0,
            }

        low_fv = scenarios["low"]["future_value"]
        mod_fv = scenarios["moderate"]["future_value"]
        high_fv = scenarios["high"]["future_value"]

        differences = {
            "high_vs_low": high_fv - low_fv,
            "moderate_vs_low": mod_fv - low_fv,
            "high_vs_moderate": high_fv - mod_fv,
        }

        return {
            "is_hypothetical": True,
            "disclaimer": (
                "HYPOTHETICAL SCENARIOS: Values below are illustrative projections "
                "based on user-defined assumptions and are not guaranteed."
            ),
            "initial_investment": initial,
            "monthly_investment": monthly,
            "years": t,
            "total_months": months,
            "total_investment": scenarios["low"]["total_investment"],
            "scenarios": scenarios,
            "differences": differences,
        }
