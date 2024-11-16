## Hypothesis

The company's financial statements have a causal impact on quarterly returns, with adjustments made to account for the confounding influences of the specified quarter, sector, and additional treatment-specific confounders.

### Brief

causal_study.ipynb found the causal impact (important metrics that gave the right decisions say top3 long of AAPL/MSFT/WMT, short of IBM/BA/TRV). And portfolio_study_result.ipynb incorporated such impact into the optimisation. (expected return can be hard to estimate, we can use causal factors' beta in the future or Black Litterman's Bayesian view. cov matrix estimation utilises historical returns as we control the ticker in causal inference, which means they have the same betas within the sector)

### $\sigma$ = 0.3, risk taking
![\sigma=0.3](./risk_taking.jpg)
