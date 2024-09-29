import pandas as pd
from sklearn.preprocessing import StandardScaler

def build_fundamental_features(financial_data):
    # Calculate additional financial ratios and metrics
    financial_data['gross_profit_margin'] = financial_data['grossProfit'] / financial_data['revenue']
    financial_data['net_profit_margin'] = financial_data['consolidatedIncome'] / financial_data['revenue']
    financial_data['debt_to_equity'] = financial_data['liabilitiesNonCurrent'] / financial_data['equity']
    financial_data['net_working_capital'] = financial_data['assetsCurrent'] - financial_data['debtCurrent']

    # Profitability features
    financial_data['return_on_assets'] = financial_data['consolidatedIncome'] / financial_data['totalAssets']
    financial_data['return_on_equity'] = financial_data['consolidatedIncome'] / financial_data['equity']

    # Liquidity Ratios
    financial_data['current_ratio'] = financial_data['assetsCurrent'] / financial_data['debtCurrent']
    financial_data['quick_ratio'] = (financial_data['cashAndEq'] + financial_data['acctRec']) / financial_data['debtCurrent']

    # Leverage Ratios
    financial_data['debt_to_assets'] = financial_data['totalLiabilities'] / financial_data['totalAssets']
    financial_data['interest_coverage_ratio'] = financial_data['opinc'] / financial_data['intexp']

    # Efficiency Ratios
    financial_data['asset_turnover_ratio'] = financial_data['revenue'] / financial_data['totalAssets']
    financial_data['inventory_turnover_ratio'] = financial_data['costRev'] / financial_data['inventory']

    # Market Ratios
    financial_data['earnings_per_share'] = financial_data['consolidatedIncome'] / financial_data['shareswa']

    # Cash Flow Ratios
    financial_data['operating_cash_flow_to_sales'] = financial_data['ncfo'] / financial_data['revenue']
    financial_data['free_cash_flow'] = financial_data['ncfo'] - financial_data['capex']

    # Growth Ratios
    financial_data['revenue_growth'] = financial_data['revenue'].pct_change()
    financial_data['earnings_growth'] = financial_data['consolidatedIncome'].pct_change()

    # Valuation Ratios
    financial_data['book_value_per_share'] = financial_data['equity'] / financial_data['shareswa']

    # Financial Ratios
    financial_data['operating_return_on_assets'] = financial_data['opinc'] / financial_data['totalAssets']
    financial_data['return_on_capital_employed'] = financial_data['ebit'] / (financial_data['totalAssets'] - financial_data['debtCurrent'])
    financial_data['long_term_debt_to_capitalization'] = financial_data['liabilitiesNonCurrent'] / (financial_data['liabilitiesNonCurrent'] + financial_data['equity'])
    financial_data['receivables_turnover'] = financial_data['revenue'] / financial_data['acctRec']
    financial_data['fixed_asset_turnover'] = financial_data['revenue'] / financial_data['assetsNonCurrent']

    financial_data['dividend_payout_ratio'] = financial_data['payDiv'] / financial_data['consolidatedIncome']
    financial_data['dividend_coverage_ratio'] = financial_data['consolidatedIncome'] / financial_data['payDiv']
    financial_data['cash_ratio'] = financial_data['cashAndEq'] / financial_data['debtCurrent']
    financial_data['operating_margin'] = financial_data['opinc'] / financial_data['revenue']

    financial_data['cash_flow_margin'] = financial_data['ncfo'] / financial_data['revenue']
    financial_data['equity_multiplier'] = financial_data['totalAssets'] / financial_data['equity']

    return financial_data



def scale_features(data, target, non_numeric_columns):
    """
    Scales the features of the DataFrame using StandardScaler while preserving the target and non-numeric columns.

    Parameters:
    data (pd.DataFrame): The input DataFrame containing the features, target, and non-numeric columns.
    target (str): The name of the target column to be preserved.
    non_numeric_columns (list): A list of names of the non-numeric columns to be preserved.

    Returns:
    pd.DataFrame: A new DataFrame with scaled features, the original target column, and the non-numeric columns.
    """

    # Separate non-numeric columns
    non_numeric_data = data[non_numeric_columns]

    # Drop non-numeric columns from the data
    data = data.drop(non_numeric_columns, axis=1)

    # Separate features and target
    features = data.drop(target, axis=1)
    target_values = data[target]

    # Apply StandardScaler to features only
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Create a DataFrame with the scaled features
    data_scaled = pd.DataFrame(scaled_features, columns=features.columns)

    # Add the target column back to the scaled DataFrame
    data_scaled[target] = target_values.values

    # Add the non-numeric columns back to the scaled DataFrame
    data_scaled = pd.concat([data_scaled, non_numeric_data.reset_index(drop=True)], axis=1)

    return data_scaled