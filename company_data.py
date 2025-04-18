import yfinance as yf
ticker = "COFORGE.BO"
stock = yf.Ticker(ticker)
balance_sheet = stock.balance_sheet
income_statement = stock.income_stmt
cash_flow = stock.cash_flow
print("Balance Sheet:")
print(balance_sheet)
print("\nIncome Statement:")
print(income_statement)
print("n\Cash Flow Statement:")
print(cash_flow)
import pandas as pd
file_name = f"{ticker}_Financials.xlsx"
with pd.ExcelWriter(file_name) as writer:
    balance_sheet.to_excel(writer, sheet_name= "Balance Sheet")
    income_statement.to_excel(writer, sheet_name= "Income Statement")
    cash_flow.to_excel(writer, sheet_name= "Cash Flow Statement")
    print(f"Financial data saved to {file_name}")
