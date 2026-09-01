# ==============================================================================
#  MULTIVARIATE JOHANSEN-JUSELIUS COINTEGRATION ENGINE
# ==============================================================================
#  Author: Nicolas Bonfante Peña
#  Reference: Johansen (1988, 1991), Osterwald-Lenum (1992)
#  Revisiting: An old-self authored code that I used for my intermediate econometrics capstone project, it has been translated to python from R
# ==============================================================================
# Key Corrections form the Legacy R Construction:
# 1. The Z-Matrix was corrected so that it evaluates lagged levels instead of lagged data
# 2. Cumulative sum on lambda-max (maxstat) was eliminated because the original Johansen model only uses cumulative sum on the trace
# 3. Critical values were reviewed, given that the prior iteration used the Osterwald-Lenum/Johansen Model 3 as universal for all critical values, when these were exclusive to evaluations with linear deterministic trends in data, and with the intercept in the cointegration space
# ==============================================================================


import numpy as np
import pandas as pd
import scipy.linalg as la


class JohansenCointegrationTest:

  def __init__(self, data: pd.DataFrame, lags: int = 1, model_type: int = 3):
    """Parameters:

    data : pd.DataFrame - Time-series panel (must be non-stationary I(1)). lags
    : int - Number of vector autoregressive (VAR) lags. model_type : int -
    Deterministic trend model (1 to 5 as per Johansen specification).
    """
    self.data = np.asarray(data)
    self.var_names = (
        data.columns
        if isinstance(data, pd.DataFrame)
        else [f'Var_{i+1}' for i in range(data.shape[1])]
    )
    self.n_obs, self.n_vars = self.data.shape
    self.lags = lags
    self.model_type = model_type

  def _build_deterministic_terms(self, T_len: int) -> np.ndarray:
    """Generates deterministic trend vectors based on Johansen model specifications."""
    t_seq = np.arange(1, T_len + 1)
    if self.model_type == 1:  # No deterministic terms
      return None
    elif self.model_type == 2:  # Restricted constant in cointegration space
      return np.ones((T_len, 1))
    elif self.model_type == 3:  # Unrestricted constant in VAR
      return np.ones((T_len, 1))
    elif self.model_type == 4:  # Linear trend in cointegration space
      return np.column_stack([np.ones((T_len, 1)), t_seq])
    elif self.model_type == 5:  # Quadratic trend in VAR
      return np.column_stack([np.ones((T_len, 1)), t_seq, t_seq**2])
    else:
      raise ValueError('model_type must be an integer between 1 and 5.')

  def fit(self, alpha: float = 0.05) -> pd.DataFrame:
    """Executes reduced-rank regression and calculates Trace & Max-Eigen statistics."""
    T = self.n_obs - self.lags
    diff_data = np.diff(self.data, axis=0)

    # Target Matrices: Delta Y_t (Y) and Lagged Levels Y_{t-1} (Z)
    Y = diff_data[self.lags - 1 :]  # Delta Y_t
    Z = self.data[self.lags - 1 : -1]  # Y_{t-1}

    # Control Matrix X: Lagged Differences + Deterministic terms
    X_list = []
    for i in range(1, self.lags):
      X_list.append(diff_data[self.lags - 1 - i : -i])

    D_terms = self._build_deterministic_terms(len(Y))

    if len(X_list) > 0:
      X = np.hstack(X_list)
      if D_terms is not None:
        X = np.hstack([X, D_terms])
    else:
      X = D_terms

    # Reduced-Rank Regression Residuals
    if X is not None:
      beta_Y = la.lstsq(X, Y)[0]
      R0 = Y - X @ beta_Y
      beta_Z = la.lstsq(X, Z)[0]
      R1 = Z - X @ beta_Z
    else:
      R0 = Y
      R1 = Z

    # Variance-Covariance Matrices (S00, S11, S01)
    S00 = (R0.T @ R0) / T
    S11 = (R1.T @ R1) / T
    S01 = (R0.T @ R1) / T
    S10 = S01.T

    # Solve Generalized Eigenvalue Problem: |lambda*S11 - S10 * S00^{-1} * S01| = 0
    inv_S00 = la.inv(S00)
    matrix_to_decompose = la.inv(S11) @ S10 @ inv_S00 @ S01

    eigenvalues, eigenvectors = la.eig(matrix_to_decompose)
    idx = np.argsort(np.real(eigenvalues))[::-1]

    lambda_vals = np.real(eigenvalues[idx])
    lambda_vals = np.clip(lambda_vals, 0, 1 - 1e-12)

    # Trace Statistic: -T * sum(ln(1 - lambda_i))
    trace_stat = np.zeros(self.n_vars)
    for r in range(self.n_vars):
      trace_stat[r] = -T * np.sum(np.log(1.0 - lambda_vals[r:]))

    # Max-Eigen Statistic: -T * ln(1 - lambda_{r+1})
    max_eigen_stat = -T * np.log(1.0 - lambda_vals)

    # Osterwald-Lenum (1992) Model 3 Critical Value Approximations (5% Significance)
    crit_vals_5pct = {
        2: {'trace': [15.49, 3.84], 'max': [14.26, 3.84]},
        3: {'trace': [29.80, 15.49, 3.84], 'max': [21.13, 14.26, 3.84]},
        4: {
            'trace': [47.85, 29.80, 15.49, 3.84],
            'max': [27.58, 21.13, 14.26, 3.84],
        },
    }

    n_v = self.n_vars
    crit_trace = crit_vals_5pct.get(n_v, {}).get(
        'trace', [np.nan] * n_v
    )
    crit_max = crit_vals_5pct.get(n_v, {}).get(
        'max', [np.nan] * n_v
    )

    results_df = pd.DataFrame({
        'Hypothesis (r)': [f'r <= {i}' for i in range(self.n_vars)],
        'Eigenvalue': lambda_vals,
        'Trace Stat': trace_stat,
        'Crit Value (5%)': crit_trace,
        'Reject Null (Trace)': trace_stat > crit_trace,
        'Max-Eigen Stat': max_eigen_stat,
        'Crit Value Max (5%)': crit_max,
        'Reject Null (Max)': max_eigen_stat > crit_max,
    })

    return results_df
