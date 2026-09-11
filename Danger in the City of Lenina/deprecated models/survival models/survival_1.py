#V1 of the Survival Analysis & Cox PH Model -- Top model up to V3 of the Market Creator


!pip install -q lifelines

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter, KaplanMeierFitter

# Load Generated Macro Panel
df = pd.read_csv("macro_spatial_panel.csv")

df_survival = df.groupby('agent_id').agg({
    's_initial': 'first',
    'w_base': 'first',
    'effective_alpha': 'first',
    'has_elite_access': 'first',
    'd_port': 'first',
    'd_market': 'first',
    'd_elite': 'first',
    'is_ruined': 'max',
    'period': 'max'
}).reset_index()

# Map exact Transaction-to-Ruin round
ruin_times = df[df['is_ruined'] == 1].groupby('agent_id')['period'].min()
df_survival['t_ruin'] = df_survival['agent_id'].map(ruin_times).fillna(df_survival['period'])

# Identify agents exposed to predatory debt (Gota a Gota)
gota_agents = df[df['prior_loan_type'] == 'Gota_a_Gota']['agent_id'].unique()
df_survival['ever_used_gota'] = df_survival['agent_id'].isin(gota_agents).astype(int)

# Log-transform initial capital to scale variance
df_survival['log_s_initial'] = np.log(df_survival['s_initial'])

print("--- SURVIVAL DATASET SUMMARY ---")
print(f"Total Agents Analyzed: {len(df_survival)}")
print(f"Total Observed Defaults (Events): {df_survival['is_ruined'].sum()}")
print(f"Censored Observations (Survivors): {len(df_survival) - df_survival['is_ruined'].sum()}")
print(f"Mean Transactions-to-Ruin: {df_survival['t_ruin'].mean():.2f} rounds\n")

# Cox Proportional Hazards Model
cph_vars = [
    't_ruin', 'is_ruined', 'effective_alpha',
    'log_s_initial', 'd_port', 'has_elite_access', 'ever_used_gota'
]

cph = CoxPHFitter()
cph.fit(df_survival[cph_vars], duration_col='t_ruin', event_col='is_ruined')

print("--- COX PROPORTIONAL HAZARDS MODEL REGRESSION RESULTS ---")
cph.print_summary()

# Plot Kaplan-Meier Survival Curves
kmf = KaplanMeierFitter()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=100)

# Stratified financial decay by Predatory Credit Exposure (Gota a Gota)
mask_gota = (df_survival['ever_used_gota'] == 1)

kmf.fit(df_survival['t_ruin'][mask_gota], df_survival['is_ruined'][mask_gota], label="Exposed to Gota a Gota")
kmf.plot_survival_function(ax=ax1, color='#d62728', lw=2.5, ci_show=True)

kmf.fit(df_survival['t_ruin'][~mask_gota], df_survival['is_ruined'][~mask_gota], label="No Predatory Credit")
kmf.plot_survival_function(ax=ax1, color='#1f77b4', lw=2.5, ci_show=True)

ax1.set_title("Kaplan-Meier Curves: Effect of Predatory Credit", fontsize=11, fontweight='bold')
ax1.set_xlabel("Transaction Rounds ($T_{\\text{ruin}}$)", fontsize=10)
ax1.set_ylabel("Survival Probability $S(t)$", fontsize=10)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_ylim(-0.05, 1.05)

# Stratified financial decau by Institutional Access (Elite/Gatekept Market)
mask_elite = (df_survival['has_elite_access'] == 1)

kmf.fit(df_survival['t_ruin'][mask_elite], df_survival['is_ruined'][mask_elite], label="Elite Gatekept Access")
kmf.plot_survival_function(ax=ax2, color='#2ca02c', lw=2.5, ci_show=True)

kmf.fit(df_survival['t_ruin'][~mask_elite], df_survival['is_ruined'][~mask_elite], label="Non-Elite / Uneducated")
kmf.plot_survival_function(ax=ax2, color='#7f7f7f', lw=2.5, ci_show=True)

ax2.set_title("Kaplan-Meier Curves: Effect of Institutional Access", fontsize=11, fontweight='bold')
ax2.set_xlabel("Transaction Rounds ($T_{\\text{ruin}}$)", fontsize=10)
ax2.set_ylabel("Survival Probability $S(t)$", fontsize=10)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_ylim(-0.05, 1.05)

plt.tight_layout()
plt.show()
