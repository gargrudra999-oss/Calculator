================================================================================
FINANCIAL RISK CALCULATOR — 100% PYTHON OFFLINE DESKTOP APPLICATION
================================================================================

OVERVIEW
--------
Financial Risk Calculator is a complete offline desktop application built
exclusively with Python's built-in standard libraries (Tkinter, ttk, SQLite3,
math, datetime, and os). No external packages, pip installations, external
images, or internet access are required.


PROJECT STRUCTURE
-----------------
Financial_Risk_Calculator/
|
|-- main.py          Application entry point
|-- database.py      SQLite3 database manager (auto-creates local .db file)
|-- calculations.py  Financial calculation engine, validation & INR formatting
|-- dashboard.py     Dark-navy Tkinter / ttk GUI dashboard & module views
|-- README.txt       Project documentation


HOW TO RUN
----------
1. Ensure Python 3 with Tkinter support is installed on your computer.
2. Open a terminal / command prompt in the Financial_Risk_Calculator folder.
3. Run:

       python main.py

On startup, the SQLite3 database file (financial_risk_calculator.db) is
automatically created inside the Financial_Risk_Calculator directory.


INCLUDED MODULES
----------------
1. Dashboard Home
   - Displays live summary metrics from SQLite3, quick-launch cards for each
     calculator, and the 5 most recent saved calculations.

2. Loan EMI Calculator
   - Inputs : Loan Amount (INR), Annual Interest Rate (%), Loan Duration
              (Years or Months)
   - Outputs: Monthly EMI, Total Interest, Total Repayment
   - Notes  : Handles 0% interest loans cleanly without division by zero.

3. Compound Interest Calculator
   - Inputs : Principal Amount (INR), Annual Interest Rate (%), Duration (Years),
              Compounding Frequency (Annually, Semi-Annually, Quarterly,
              Monthly, Daily)
   - Outputs: Compound Interest, Final Amount, Total Interest Earned

4. Investment Growth Calculator
   - Inputs : Initial Investment (INR), Monthly Investment / SIP (INR),
              Annual Expected Return (%), Investment Duration (Years)
   - Outputs: Total Investment, Estimated Profit, Future Value
   - Notes  : Uses monthly compounding (monthly rate = annual rate / 1200).

5. Financial Risk Simulator
   - Scenarios: Low Return, Moderate Return, and High Return (all editable)
   - Displays : Projected investment value, estimated profit or loss, and
                differences between scenarios (High vs Low, Moderate vs Low,
                High vs Moderate).

6. Calculation History (SQLite3)
   - Automatically stores every successful calculation with ID, category,
     input details, results, and date/time.
   - Supports filtering by category, viewing full record details, refreshing,
     deleting a selected record, and clearing all history.


TECHNOLOGY RESTRICTIONS FOLLOWED
--------------------------------
- Built-in libraries only: tkinter, tkinter.ttk, tkinter.messagebox, sqlite3,
  math, datetime, os
- No external libraries, frameworks, APIs, or cloud services
- No external images, icons, or fonts
- Indian Rupee (INR) formatting across all outputs
================================================================================
