import pandas as pd
import numpy as np
from scipy.optimize import minimize


def calc_returns_cov(df, tickers):
    """
    Calculate the expected daily returns and the covariance matrix for the given tickers.

    Parameters:
    df (pd.DataFrame): DataFrame containing columns 'date', 'ticker', and 'adjClose'.
    tickers (list): List of tickers to include in the calculation.

    Returns:
    expected_returns (pd.Series): The mean daily returns for each ticker.
    cov_matrix (pd.DataFrame): The covariance matrix of daily returns for the tickers.
    """
    
    filtered_df = df[df['ticker'].isin(tickers)].copy()
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    pivot_df = filtered_df.pivot(index='date', columns='ticker', values='adjClose')
    returns = pivot_df.pct_change().dropna()
    expected_returns = returns.mean()
    
    # Calculate the covariance matrix of daily returns, need to be refined with better factor models
    cov_matrix = returns.cov()
    
    return expected_returns, cov_matrix

def portfolio_returns_std(weights, expected_returns, cov_matrix):
    """
    Calculate the portfolio's expected annual returns and annual standard deviation.

    Parameters:
    weights (np.ndarray): Portfolio weights.
    expected_returns (pd.Series): Expected daily returns.
    cov_matrix (pd.DataFrame): Covariance matrix of daily returns.

    Returns:
    float: Annualized portfolio return.
    float: Annualized portfolio standard deviation.
    """

    daily_returns = np.dot(weights, expected_returns)    
    annual_returns = daily_returns * 252
    portfolio_var = weights.T @ cov_matrix @ weights
    annual_std_dev = np.sqrt(portfolio_var) * np.sqrt(252)
    
    return annual_returns, annual_std_dev

def optimize_portfolio(expected_returns, cov_matrix, weighted_scores, delta, gamma, target_risk, risk_free_rate, long_only=False):
    """
    Optimize the portfolio considering the Sharpe ratio and weighted scores for a fixed level of risk.

    Parameters:
    expected_returns (pd.Series): Expected returns for each asset.
    cov_matrix (pd.DataFrame): Covariance matrix of asset returns.
    weighted_scores (pd.Series): Scores indicating preference for long or short positions.
    gamma (float): Weight indicating preference for weighted_scores.
    target_risk (float): Target risk level for the portfolio.
    risk_free_rate (float): Risk-free rate for calculating Sharpe ratio.

    Returns:
    np.ndarray: Optimal weights for the portfolio.
    float: Expected portfolio return.
    float: Expected portfolio volatility.
    float: Portfolio Sharpe ratio.
    """
    
    def objective_function(weights, expected_returns, cov_matrix, weighted_scores, risk_free_rate):
        annual_returns, annual_std_dev = portfolio_returns_std(weights, expected_returns, cov_matrix)
        sharpe_ratio = (annual_returns - risk_free_rate) / annual_std_dev
        # Penalise negative scores to favor short positions and reward positive scores to favor long positions
        weighted_score_component = np.dot(weights, weighted_scores)
        return -delta*sharpe_ratio - gamma * weighted_score_component

    # Constraints: weights must sum to 1 and portfolio risk must be equal to the target risk
    constraints = (
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'eq', 'fun': lambda x: np.sqrt(x.T @ cov_matrix @ x) * np.sqrt(252) - target_risk}
    )
    
    if long_only:
        # Bounds: weights can only be between 0 and 1 for long-only positions
        bounds = tuple((0, 1) for asset in range(len(expected_returns)))
    else:
        # Bounds: weights can be between -1 and 1 to allow short selling
        bounds = tuple((-1, 1) for asset in range(len(expected_returns)))

    # Initial guess (equal distribution)
    init_guess = [1. / len(expected_returns) for _ in range(len(expected_returns))]

    # Optimise the portfolio
    opt_results = minimize(
        objective_function, 
        init_guess, 
        args=(expected_returns, cov_matrix, weighted_scores, risk_free_rate),
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints
    )

    optimal_weights = opt_results.x

    # Calculate the portfolio performance with the optimal weights
    annual_returns, annual_std_dev = portfolio_returns_std(optimal_weights, expected_returns, cov_matrix)
    sharpe_ratio = (annual_returns - risk_free_rate) / annual_std_dev
    
    return optimal_weights, annual_returns, annual_std_dev, sharpe_ratio


