from datetime import datetime
import time
import numpy as np
import pandas as pd
import requests
import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

# CONFIGURATION & U.S. DOMESTIC COMPANY CIK MAPPING
HEADERS = {'User-Agent': 'nicolas.bonfante@urosario.edu.co'}

US_IT_SERVICES_PANEL = {
    # Large-Cap & Commercial IT Consulting
    'IBM': '0000051143',
    'COGNIZANT': '0001058290',
    'EPAM': '0001352010',
    'GENPACT': '0001398659',
    'DXC': '0001688568',
    'KYNDRYL': '0001867087',
    # Government & Defense IT Consulting
    'BOOZ_ALLEN': '0001443646',
    'CACI': '0000016080',
    'LEIDOS': '0001336920',
    'SAIC': '0001578563',
    # Business Process & Transformation Services
    'CONCENTRIX': '0001802521',
    'CONDUENT': '0001677703',
    'EXL': '0001365135',
    'ALIGHT': '0001809104',
    'UNISYS': '0000101748',
    'GARTNER': '0000939219',
    # Digital & Software Engineering Services
    'PERFICIENT': '0001085869',
    'GLOBANT_US': '0001607008',
}

#SEC GAAP EXTRACTION ENGINE
def fetch_sec_gaap_financials(cik: str, ticker: str) -> pd.DataFrame:
  print(f'Fetching GAAP financials for {ticker} (CIK: {cik})...')
  url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json'

  try:
    res = requests.get(url, headers=HEADERS, timeout=10)
    if res.status_code != 200:
      print(f'  [HTTP {res.status_code}] Failed to fetch {ticker}')
      return pd.DataFrame()
  except Exception as e:
    print(f'  Connection error for {ticker}: {e}')
    return pd.DataFrame()

  time.sleep(0.15)
  facts = res.json().get('facts', {}).get('us-gaap', {})

  tag_map = {
      'revenue': [
          'RevenueFromContractWithCustomerExcludingAssessedTax',
          'Revenues',
          'SalesRevenueNet',
      ],
      'sga': [
          'SellingGeneralAndAdministrativeExpense',
          'GeneralAndAdministrativeExpense',
      ],
      'cogs': ['CostOfRevenue', 'CostOfGoodsAndServicesSold'],
      'operating_income': ['OperatingIncomeLoss'],
  }

  records = []

  # Extract Standalone 3-Month Quarters (Q1, Q2, Q3) & FY Totals
  for metric, tags in tag_map.items():
    for tag in tags:
      if tag in facts:
        units = facts[tag].get('units', {}).get('USD', [])
        for entry in units:
          val = entry.get('val')
          fp = entry.get('fp', '')
          fy = entry.get('fy')
          start = entry.get('start')
          end = entry.get('end')

          if val is not None and start and end and fy:
            fy_int = int(fy)
            if 2020 <= fy_int <= 2025:
              days = (
                  datetime.strptime(end, '%Y-%m-%d')
                  - datetime.strptime(start, '%Y-%m-%d')
              ).days

              if 80 <= days <= 100 and fp in ['Q1', 'Q2', 'Q3']:
                records.append({
                    'year': fy_int,
                    'quarter': fp,
                    'metric': metric,
                    'val': float(val),
                })
              elif 350 <= days <= 380 and fp == 'FY':
                records.append({
                    'year': fy_int,
                    'quarter': 'FY',
                    'metric': metric,
                    'val': float(val),
                })
        break

  df_raw = pd.DataFrame(records)
  if df_raw.empty:
    return pd.DataFrame()

  # Deduplicate by keeping the most recent SEC restatement/filing entry
  df_raw = df_raw.groupby(
      ['year', 'quarter', 'metric'], as_index=False
  ).last()

  # Pivot metrics to columns
  df_piv = df_raw.pivot(
      index=['year', 'quarter'], columns='metric', values='val'
  ).reset_index()

  # Calculate Implicit Standalone Q4 Metrics: Q4 = FY - (Q1 + Q2 + Q3)
  q4_rows = []
  years = df_piv['year'].unique()

  for y in years:
    df_y = df_piv[df_piv['year'] == y]
    fy_row = df_y[df_y['quarter'] == 'FY']
    q_rows = df_y[df_y['quarter'].isin(['Q1', 'Q2', 'Q3'])]

    if not fy_row.empty and len(q_rows) == 3:
      q4_data = {'year': y, 'quarter': 'Q4'}
      for col in ['revenue', 'sga', 'cogs', 'operating_income']:
        if col in df_piv.columns and col in fy_row.columns:
          fy_val = fy_row[col].values[0]
          q_sum = q_rows[col].sum()
          if pd.notna(fy_val) and pd.notna(q_sum):
            q4_data[col] = fy_val - q_sum
      q4_rows.append(q4_data)

  df_q4 = pd.DataFrame(q4_rows)

  # Combine Q1-Q3 with derived Q4 (drop FY summary rows)
  df_clean = pd.concat(
      [df_piv[df_piv['quarter'] != 'FY'], df_q4], ignore_index=True
  )
  df_clean['company'] = ticker

  #DERIVE SCALE-INDEPENDENT FINANCIAL RATIOS
  if 'revenue' in df_clean.columns:
    if 'sga' in df_clean.columns:
      df_clean['sga_ratio'] = df_clean['sga'] / df_clean['revenue']

    if 'cogs' in df_clean.columns:
      # Gross Margin: Delivery Efficiency
      df_clean['gross_margin'] = (
          df_clean['revenue'] - df_clean['cogs']
      ) / df_clean['revenue']

    if 'operating_income' in df_clean.columns:
      # Operating Margin: Core Operational Profitability
      df_clean['operating_margin'] = (
          df_clean['operating_income'] / df_clean['revenue']
      )

  return df_clean


#EXECUTION AND PANEL CONSTRUCTION
print('Starting GAAP Financial Extraction across U.S. IT Services Panel...\n')
all_dfs = [
    fetch_sec_gaap_financials(cik, ticker)
    for ticker, cik in US_IT_SERVICES_PANEL.items()
]

df_panel = pd.concat([d for d in all_dfs if not d.empty], ignore_index=True)

# Build Continuous Time Keys
quarter_order = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
df_panel['q_num'] = df_panel['quarter'].map(quarter_order)
df_panel = df_panel.dropna(subset=['q_num'])
df_panel['q_num'] = df_panel['q_num'].astype(int)

df_panel['quarter_id'] = (
    df_panel['year'].astype(str) + 'Q' + df_panel['q_num'].astype(str)
)

df_panel = df_panel.sort_values(['company', 'year', 'q_num']).reset_index(drop=True)

cols = [
    'company',
    'year',
    'quarter',
    'quarter_id',
    'revenue',
    'sga',
    'operating_income',
    'sga_ratio',
    'gross_margin',
    'operating_margin',
]
cols_to_use = [c for c in cols if c in df_panel.columns]
df_panel = df_panel[cols_to_use]

# Summary
print('\n======================================================')
print('   FINAL PANEL DATASET SUMMARY (U.S. IT SERVICES)     ')
print('======================================================')
print(f'Total Companies Processed: {df_panel["company"].nunique()}')
print(f'Total Quarterly Panel Observations: {len(df_panel)}')
print('\nPreview of First 15 Panel Rows:')
print(df_panel.head(15).to_string())

# Export Dataset to CSV
output_file = 'us_it_services_gaap_panel_2020_2025.csv'
df_panel.to_csv(output_file, index=False)
print(f"\nDataset successfully saved locally to '{output_file}'")

#EXOGENOUS SPIKE

warnings.filterwarnings('ignore')

FILE_PATH = 'us_it_services_gaap_panel_2020_2025.csv'

if not os.path.exists(FILE_PATH):
  raise FileNotFoundError(
      f"'{FILE_PATH}' not found. Please upload the CSV file to your Colab session."
  )

df = pd.read_csv(FILE_PATH)
print(f'Successfully loaded dataset with {len(df)} panel observations.')

df_clean = df.copy()

df_clean['log_revenue'] = np.log(df_clean['revenue'])

sga_p01 = df_clean['sga_ratio'].quantile(0.01)
sga_p99 = df_clean['sga_ratio'].quantile(0.99)
df_clean['sga_ratio_winsor'] = df_clean['sga_ratio'].clip(
    lower=sga_p01, upper=sga_p99
)

reg_vars = [
    'sga_ratio_winsor',
    'log_revenue',
    'company',
    'quarter_id',
    'year',
    'quarter',
]
df_reg = df_clean.dropna(subset=reg_vars).copy()

print(f'Cleaned Panel Observations for Estimation: N = {len(df_reg)}')

#MODEL 1: TWO-WAY FIXED EFFECTS (2WFE) OLS
print('\n==================================================================')
print('   MODEL 1: TWO-WAY FIXED EFFECTS (TWFE) - CLUSTERED SE (BY FIRM)  ')
print('==================================================================')

formula_twfe = 'sga_ratio_winsor ~ log_revenue + C(company) + C(quarter_id)'

model_twfe = smf.ols(formula_twfe, data=df_reg).fit(
    cov_type='cluster', cov_kwds={'groups': df_reg['company']}
)

print(f'Number of Observations (N): {int(model_twfe.nobs)}')
print(f'R-squared (Within/Overall): {model_twfe.rsquared:.4f}')
print(f'Adjusted R-squared:         {model_twfe.rsquared_adj:.4f}')
print('\n--- Target Elasticity / Coefficient ---')
coef_rev = model_twfe.params['log_revenue']
se_rev = model_twfe.bse['log_revenue']
p_val_rev = model_twfe.pvalues['log_revenue']

print(
    f'Log(Revenue) Coef: {coef_rev:.6f} | Std Error: {se_rev:.6f} | p-value:'
    f' {p_val_rev:.4f}'
)

if p_val_rev < 0.05:
  print(
      '==> Statistically Significant: Increases in scale significantly reduce'
      ' SG&A cost intensity.'
  )

#MODEL 2: Dif-in-Dif (AI EXPOSURE vs. SG&A INTENSITY)
print('\n==================================================================')
print('   MODEL 2: DIFF-IN-DIFF / SHIFT-SHARE (AI EXPOSURE POST-2022)   ')
print('==================================================================')

#Cross-Sectional AI Exposure Intensity Weights (0.0 to 1.0 Baseline) - I invented this data as random points in the range to see if the code overall worked
ai_exposure_map = {
    'EPAM': 0.90,
    'PERFICIENT': 0.85,
    'COGNIZANT': 0.75,
    'EXL': 0.70,
    'GENPACT': 0.65,
    'DXC': 0.55,
    'IBM': 0.50,
    'CONDUENT': 0.45,
    'ALIGHT': 0.40,
    'LEIDOS': 0.25,
    'BOOZ_ALLEN': 0.20,
}
df_reg['ai_exposure'] = df_reg['company'].map(ai_exposure_map)

#Time Shock (Post-2022 GenAI Adoption Expansion)
q_num = df_reg['quarter'].str[1].astype(int)
df_reg['ai_time_shock'] = np.where(
    df_reg['year'] >= 2023, (df_reg['year'] - 2022) + (q_num - 1) * 0.25, 0.0
)

# Interaction Term: Exposure * Time Shock
df_reg['ai_interaction'] = df_reg['ai_exposure'] * df_reg['ai_time_shock']

# Fit Interaction Panel Model with 2WFE
formula_did = (
    'sga_ratio_winsor ~ log_revenue + ai_interaction + C(company) +'
    ' C(quarter_id)'
)
model_did = smf.ols(formula_did, data=df_reg).fit(
    cov_type='cluster', cov_kwds={'groups': df_reg['company']}
)

coef_ai = model_did.params['ai_interaction']
se_ai = model_did.bse['ai_interaction']
p_val_ai = model_did.pvalues['ai_interaction']

print(f'Number of Observations (N): {int(model_did.nobs)}')
print(f'R-squared:                  {model_did.rsquared:.4f}')
print('\n--- Shift-Share Interaction (Build vs. Buy Assessment) ---')
print(
    f'AI Interaction Coef (beta_2): {coef_ai:.6f} | Std Error: {se_ai:.6f} |'
    f' p-value: {p_val_ai:.4f}'
)

if coef_ai < 0:
  print(
      '==> Structural Direction: Negative coefficient indicates high-exposure'
      ' firms achieve overhead dilution ("BUILD" Strategy / Internal AI'
      ' Efficiency).'
  )
else:
  print(
      '==> Structural Direction: Positive coefficient indicates high-exposure'
      ' firms pass through software costs ("BUY" Strategy / Third-party SaaS'
      ' Expansion).'
  )

# GRAPHS

# 2WFE Fitted Line vs. Raw Data Scatter
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_reg,
    x='log_revenue',
    y='sga_ratio_winsor',
    hue='company',
    style='company',
    s=70,
    alpha=0.8,
)

plt.title(
    'U.S. IT Services Panel: Scale Economies & SG&A Efficiency (2020–2025)',
    fontsize=13,
    pad=15,
)
plt.xlabel('Log Quarterly Revenue', fontsize=11)
plt.ylabel('SG&A Efficiency Ratio (Winsorized)', fontsize=11)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.0)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('panel_twfe_regression_plot.png', dpi=300)
plt.show()

# Trajectory Trends (High vs. Low AI Exposure)
df_reg['ai_group'] = np.where(
    df_reg['ai_exposure'] >= 0.60,
    'High AI Exposure (Digital Consultancies)',
    'Low AI Exposure (Legacy/Defense IT)',
)

plt.figure(figsize=(10, 5))
sns.lineplot(
    data=df_reg,
    x='year',
    y='sga_ratio_winsor',
    hue='ai_group',
    style='ai_group',
    markers=True,
    dashes=False,
    errorbar=None,
)
plt.axvline(
    x=2022.5,
    color='red',
    linestyle='--',
    label='GenAI Cost/Adoption Shock (Post-2022)',
)
plt.title(
    'SG&A Intensity Trajectories: High vs. Low AI Exposure Firms (2020–2025)',
    fontsize=12,
)
plt.xlabel('Year', fontsize=10)
plt.ylabel('SG&A Efficiency Ratio (Winsorized)', fontsize=10)
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('ai_exposure_sga_trend.png', dpi=300)
plt.show()

print(
    "\nExecution Complete! Plots saved as 'panel_twfe_regression_plot.png' and"
    " 'ai_exposure_sga_trend.png'."
)

