import numpy as np
import pandas as pd
from fundamental_feature_engineer import build_fundamental_features

def load_and_prepare_data(balance_sheet_path, cash_flow_path, income_statement_path, stock_prices_path):
    balance_sheet = pd.read_csv(balance_sheet_path)
    cash_flow = pd.read_csv(cash_flow_path)
    income_statement = pd.read_csv(income_statement_path)
    stock_prices = pd.read_csv(stock_prices_path)

    balance_sheet['date'] = pd.to_datetime(balance_sheet['date'])
    cash_flow['date'] = pd.to_datetime(cash_flow['date'])
    income_statement['date'] = pd.to_datetime(income_statement['date'])
    stock_prices['date'] = pd.to_datetime(stock_prices['date'])
    stock_prices['return'] = stock_prices.groupby('ticker')['adjClose'].pct_change()
    
    return balance_sheet, cash_flow, income_statement, stock_prices

def preprocess_financial_data(balance_sheet, cash_flow, income_statement):
    pivot_balance_sheet = balance_sheet.pivot_table(
        index=['ticker', 'date', 'year', 'quarter'],
        columns='dataCode', values='value'
    ).reset_index()

    pivot_cash_flow = cash_flow.pivot_table(
        index=['ticker', 'date', 'year', 'quarter'],
        columns='dataCode', values='value'
    ).reset_index()

    pivot_income_statement = income_statement.pivot_table(
        index=['ticker', 'date', 'year', 'quarter'],
        columns='dataCode', values='value'
    ).reset_index()

    financial_data = pivot_balance_sheet.merge(
        pivot_cash_flow,
        on=['ticker', 'date', 'year', 'quarter'],
        suffixes=('_balance', '_cash'))

    financial_data = financial_data.merge(
        pivot_income_statement,
        on=['ticker', 'date', 'year', 'quarter'],
        suffixes=('', '_income'))

    financial_data = financial_data.loc[~(financial_data.quarter == 0)]  # remove annual one
    financial_data.columns.name = None
    financial_data = build_fundamental_features(financial_data)
    financial_data = financial_data.dropna(axis=1)
    return financial_data


def cap_inf(df):
    numeric_cols = df.select_dtypes(include=np.number)

    # Calculate the maximum and minimum values, ignoring np.inf and -np.inf
    max_value = numeric_cols[numeric_cols != np.inf].max().max()
    min_value = numeric_cols[numeric_cols != -np.inf].min().min()
    
    # Replace np.inf with the maximum value and -np.inf with the minimum value
    df.replace({np.inf: max_value, -np.inf: min_value}, inplace=True)
    return df
