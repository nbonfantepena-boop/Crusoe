# ==============================================================================
#  OKUN'S LAW MACROECONOMIC ESTIMATION ENGINE
# ==============================================================================
#  Author: Nicolás Bonfante Peña
#  Reference: Okun (1962), Ball et al. (2017)
#  Revisiting: The legacy Okun's law architecture developed for my Intermediate Econometrics capstone project, represents the difference/deviation version of Okun's law
# ==============================================================================
#  Key Corrections:
# 1. Index timing and alignment were modernized to not depend on raw levels but rather capture the change in unemployment, therefore controlling spurious correlation
# 2. Potential growth was changed form a static quarterly potential output to a dynamic alternative modeled as a Hodrick-Prescott filter in order to capture the structural evolution of potential growth over time
# ==============================================================================


import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.filters.hp_filter import hpfilter


class OkunLawEstimator:

  def __init__(self, unemployment: pd.Series, gdp: pd.Series, freq: str = 'Q'):
    """Parameters:

    unemployment : pd.Series - Unemployment rate (percentage). gdp          :
    pd.Series - Real GDP (levels or log levels). freq         : str - 'Q' for
    Quarterly (HP lambda=1600), 'A' for Annual (HP lambda=100).
    """
    self.u = np.asarray(unemployment)
    self.y = np.asarray(gdp)
    self.hp_lambda = 1600 if freq.upper() == 'Q' else 100

  def fit_difference_model(
      self, potential_gdp_growth: float = None
  ) -> pd.DataFrame:
    """Estimates Difference Version: Delta(U_t) = alpha + beta * (g_t - g_bar) + e_t"""
    # Compute percentage GDP growth
    gdp_growth = np.diff(np.log(self.y)) * 100.0

    # Compute Unemployment Change Delta(U_t)
    delta_u = np.diff(self.u)

    # Output Gap / Growth Deviation
    if potential_gdp_growth is None:
      g_bar = np.mean(gdp_growth)
    else:
      g_bar = potential_gdp_growth

    gdp_dev = gdp_growth - g_bar

    # Fit OLS with Robust Standard Errors (HAC / Newey-West)
    X = sm.add_constant(gdp_dev)
    model = sm.OLS(delta_u, X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})

    return self._format_summary(model, 'Difference Model', gdp_dev, delta_u)

  def fit_gap_model(self) -> pd.DataFrame:
    """Estimates Gap Version using HP Filter: (U_t - U_t*) = alpha + beta * (Y_t - Y_t*) + e_t"""
    # HP Filter decomposition for Log GDP and Unemployment
    log_y = np.log(self.y) * 100.0
    gdp_cycle, gdp_trend = hpfilter(log_y, lamb=self.hp_lambda)
    u_cycle, u_trend = hpfilter(self.u, lamb=self.hp_lambda)

    X = sm.add_constant(gdp_cycle)
    model = sm.OLS(u_cycle, X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})

    return self._format_summary(model, 'HP-Gap Model', gdp_cycle, u_cycle)

  def _format_summary(self, model, model_type, x_var, y_var):
    beta = model.params[1]
    se = model.bse[1]
    t_stat = model.tvalues[1]
    p_val = model.pvalues[1]

    print(
        f'=================================================================='
    )
    print(f'   OKUN\'S LAW ESTIMATION: {model_type.upper()}')
    print(
        f'=================================================================='
    )
    print(f'Observations (N):          {len(y_var)}')
    print(f'R-squared:                 {model.rsquared:.4f}')
    print(
        f'Okun\'s Coefficient (beta): {beta:.6f} | SE: {se:.6f} | p-val:'
        f' {p_val:.4f}'
    )
    print(
        f'Interpretation:            A 1% increase in GDP growth relative to'
        f' trend yields a {abs(beta):.3f}% shift in unemployment.'
    )

    return model
