"""
Application entry point for the Financial Risk Calculator desktop suite.

Starts the offline Tkinter GUI, initializes the local SQLite3 database
automatically, and connects all financial calculation modules.
"""

import tkinter as tk
from tkinter import messagebox

from calculations import FinancialCalculator
from dashboard import FinancialRiskApp
from database import DatabaseError, DatabaseManager


def main():
    """Initialize backend services and launch the Financial Risk Calculator GUI."""
    try:
        db_manager = DatabaseManager()
    except DatabaseError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Could not initialize local database:\n{exc}")
        root.destroy()
        return

    calculator = FinancialCalculator()
    app = FinancialRiskApp(db_manager=db_manager, calculator=calculator)
    app.mainloop()


if __name__ == "__main__":
    main()
