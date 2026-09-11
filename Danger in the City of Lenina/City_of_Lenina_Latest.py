#V4 of the Market Creator -- Corrects Flat Hazard lines by including a subscription cost to the elite market as a problem of optimization in itself

# V4 of the Market Creator - Dynamic Access Subscription & Debt Memory

import numpy as np
import pandas as pd

def generate_and_export_macro_panel(n_agents=1000, n_periods=30, c_elite_subscription=25.0, seed=42, filename="macro_spatial_panel.csv"):
    np.random.seed(seed)

    # Spatial Centroids & Market Infrastructure
    port_center = np.array([-7.0, -7.0])
    market_center = np.array([5.0, 5.0])
    elite_center = np.array([0.0, 8.0])

    agent_coords = np.random.uniform(-10, 10, (n_agents, 2))
    d_port = np.linalg.norm(agent_coords - port_center, axis=1)
    d_market = np.linalg.norm(agent_coords - market_center, axis=1)
    d_elite = np.linalg.norm(agent_coords - elite_center, axis=1)

    # Market Stations (10 per cluster)
    n_sellers = 10
    sellers_port = port_center + np.random.normal(0, 1.2, (n_sellers, 2))
    sellers_city = market_center + np.random.normal(0, 1.2, (n_sellers, 2))
    sellers_elite = elite_center + np.random.normal(0, 0.6, (n_sellers, 2))
    all_sellers = np.vstack([sellers_port, sellers_city, sellers_elite])
    cluster_labels = np.array([0]*n_sellers + [1]*n_sellers + [2]*n_sellers)

    q_true = np.concatenate([
        np.random.uniform(1.0, 3.0, n_sellers),
        np.random.uniform(5.0, 7.0, n_sellers),
        np.random.uniform(8.5, 10.0, n_sellers)
    ])
    q_perceived = np.concatenate([
        q_true[:10] + np.random.uniform(4.0, 6.0, 10),
        q_true[10:20],
        q_true[20:]
    ])
    markups = np.concatenate([
        np.random.uniform(10, 20, 10),
        np.random.uniform(30, 50, 10),
        np.random.uniform(25, 40, 10)
    ])

    # Agent Endowment & Status
    s_i0 = np.random.lognormal(mean=6.2, sigma=0.6, size=n_agents)
    w_base = s_i0 * 0.12
    latent_alpha = np.random.uniform(0.1, 0.9, n_agents)

    # Rates & Parameters
    r_market, r_gota, r_kin = 0.08, 0.35, 0.02
    phi_coercion = 40.0
    max_dsi_formal = 0.40  # 40% Debt-Service-to-Income formal credit ceiling

    panel_records = []

    for i in range(n_agents):
        current_savings = s_i0[i]
        prior_loan = 0.0
        loan_type = 'None'
        is_ruined = False
        ruin_period = np.nan

        for t in range(1, n_periods + 1):
            if current_savings <= 0 and not is_ruined:
                is_ruined = True
                ruin_period = t

            commission = np.random.uniform(0.0, 0.20 * w_base[i])
            w_it = w_base[i] + commission

            # RULE 6: Calculate cumulative debt service obligations
            debt_service = 0.0
            if prior_loan > 0.0:
                if loan_type == 'Formal':
                    debt_service = prior_loan * (1 + r_market)
                elif loan_type == 'Kinship':
                    debt_service = prior_loan * (1 + r_kin)
                elif loan_type == 'Gota_a_Gota':
                    debt_service = prior_loan * (1 + r_gota)

            # RULE 1: Available Gross Liquidity
            a_it = max(0.0, current_savings + w_it - debt_service)

            # DYNAMIC RULE 2: Per-Period Elite Access Subscription
            # Agents pay subscription fee if liquidity allows a comfortable buffer
            can_afford_elite = (a_it >= c_elite_subscription + 10.0) and not is_ruined

            if can_afford_elite:
                a_it -= c_elite_subscription
                current_alpha = latent_alpha[i] + (1.0 - latent_alpha[i]) * 0.5
                has_active_elite_access = True
            else:
                current_alpha = latent_alpha[i]
                has_active_elite_access = False

            chosen_cluster = np.nan
            transaction_cost = 0.0
            new_loan = 0.0
            new_loan_type = 'None'
            shortfall = 0.0

            if a_it > 0 and not is_ruined:
                dists = np.linalg.norm(all_sellers - agent_coords[i], axis=1)
                prices = markups + dists

                # Dynamic cluster masking based on period subscription status
                mask = np.ones(len(prices), dtype=bool)
                if not has_active_elite_access:
                    mask[cluster_labels == 2] = False

                p_sub, qt_sub, qp_sub = prices[mask], q_true[mask], q_perceived[mask]
                u_true = (qt_sub / p_sub)
                u_true_norm = (u_true - u_true.min()) / (u_true.max() - u_true.min() + 1e-6)

                u_fool = p_sub - (0.5 * qp_sub)
                u_fool_norm = (u_fool - u_fool.min()) / (u_fool.max() - u_fool.min() + 1e-6)

                u_blend = (current_alpha * u_true_norm) + ((1 - current_alpha) * u_fool_norm)

                # Coercion Utility Subtraction (Rule 4)
                if loan_type == 'Gota_a_Gota':
                    u_blend -= phi_coercion

                chosen_local_idx = np.argmax(u_blend)
                global_idx = np.where(mask)[0][chosen_local_idx]
                chosen_cluster = cluster_labels[global_idx]
                transaction_cost = prices[global_idx]

                # Deficit Borrowing & Credit Rationing (Rule 3 & Rule 6)
                if transaction_cost > a_it:
                    shortfall = transaction_cost - a_it
                    dsi_ratio = debt_service / max(w_it, 1e-6)

                    # RULE 6: Formal banks enforce capacity caps (DSI <= 40%)
                    if (w_base[i] >= 45.0 or current_alpha >= 0.60) and dsi_ratio <= max_dsi_formal:
                        new_loan_type = 'Formal'
                    elif shortfall <= 100.0 and current_alpha > 0.35:
                        new_loan_type = 'Kinship'
                    else:
                        new_loan_type = 'Gota_a_Gota'

                    new_loan = shortfall
                    prior_loan = prior_loan + new_loan
                    current_savings = max(0.0, a_it + new_loan - transaction_cost)
                else:
                    new_loan_type = 'None'
                    new_loan = 0.0
                    prior_loan = max(0.0, prior_loan - debt_service)
                    current_savings = max(0.0, a_it - transaction_cost)
            else:
                current_savings = 0.0

            panel_records.append({
                'agent_id': i,
                'period': t,
                'x': agent_coords[i, 0],
                'y': agent_coords[i, 1],
                'd_port': d_port[i],
                'd_market': d_market[i],
                'd_elite': d_elite[i],
                's_initial': s_i0[i],
                'w_base': w_base[i],
                'w_it': w_it,
                'latent_alpha': latent_alpha[i],
                'current_alpha': current_alpha,
                'has_active_elite_access': int(has_active_elite_access),
                'available_capital': a_it,
                'savings_carried': current_savings,
                'prior_loan': prior_loan,
                'prior_loan_type': loan_type,
                'new_loan': new_loan,
                'new_loan_type': new_loan_type,
                'chosen_cluster': chosen_cluster,
                'is_ruined': int(is_ruined),
                'ruin_period': ruin_period
            })

            loan_type = new_loan_type if new_loan_type != 'None' else loan_type

    df_panel = pd.DataFrame(panel_records)
    df_panel.to_csv(filename, index=False)
    print(f"Dataset successfully saved to '{filename}'. Shape: {df_panel.shape}")
    return df_panel

df_macro = generate_and_export_macro_panel()


# V2 of the Survival Analysis & Cox PH Model - Penalized Cox Regression (V4 Market Creator Compatible)

!pip install -q lifelines

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter, KaplanMeierFitter

# Load Generated Macro Panel (V4 Output)
df = pd.read_csv("macro_spatial_panel.csv")

# Aggregate cross-sectional summary metrics per agent
df_survival = df.groupby('agent_id').agg({
    's_initial': 'first',
    'w_base': 'first',
    'latent_alpha': 'first',
    'current_alpha': 'mean',                     # Mean realized rationality across time
    'has_active_elite_access': 'mean',          # Proportion of periods spent in elite market
    'd_port': 'first',
    'd_market': 'first',
    'd_elite': 'first',
    'is_ruined': 'max',
    'period': 'max'
}).reset_index()

# Rename subscription ratio metric for clarity
df_survival.rename(columns={'has_active_elite_access': 'share_elite_access'}, inplace=True)

# Map exact Transaction-to-Ruin round
ruin_times = df[df['is_ruined'] == 1].groupby('agent_id')['period'].min()
df_survival['t_ruin'] = df_survival['agent_id'].map(ruin_times).fillna(df_survival['period'])

# Identify agent credit channel exposures across time
gota_agents = df[df['prior_loan_type'] == 'Gota_a_Gota']['agent_id'].unique()
formal_agents = df[df['prior_loan_type'] == 'Formal']['agent_id'].unique()

df_survival['ever_used_gota'] = df_survival['agent_id'].isin(gota_agents).astype(int)
df_survival['ever_used_formal'] = df_survival['agent_id'].isin(formal_agents).astype(int)

# Log-transform initial capital buffer to stabilize variance
df_survival['log_s_initial'] = np.log(df_survival['s_initial'])

print("--- SURVIVAL DATASET SUMMARY (V4 COMPATIBLE) ---")
print(f"Total Agents Analyzed: {len(df_survival)}")
print(f"Total Observed Defaults (Events): {df_survival['is_ruined'].sum()}")
print(f"Censored Observations (Survivors): {len(df_survival) - df_survival['is_ruined'].sum()}")
print(f"Mean Transactions-to-Ruin: {df_survival['t_ruin'].mean():.2f} rounds\n")

# Cox Proportional Hazards Model Setup
cph_vars = [
    't_ruin', 'is_ruined', 'current_alpha',
    'log_s_initial', 'd_port', 'share_elite_access', 'ever_used_gota'
]

# FIRTH / L2 RIDGE PENALIZATION:
# Penalizer eliminates infinite log-odds estimates caused by quasi-complete separation
cph = CoxPHFitter(penalizer=0.1)
cph.fit(df_survival[cph_vars], duration_col='t_ruin', event_col='is_ruined')

print("--- PENALIZED COX PROPORTIONAL HAZARDS REGRESSION RESULTS ---")
cph.print_summary()

# Plot Kaplan-Meier Survival Curves
kmf = KaplanMeierFitter()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=100)

# Stratification 1: Predatory Credit Exposure (Gota a Gota)
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

# Stratification 2: Dynamic Institutional Access (Active Subscription Ratio >= 30%)
mask_frequent_elite = (df_survival['share_elite_access'] >= 0.30)

kmf.fit(df_survival['t_ruin'][mask_frequent_elite], df_survival['is_ruined'][mask_frequent_elite], label="Frequent Elite Subscriber (≥30% rounds)")
kmf.plot_survival_function(ax=ax2, color='#2ca02c', lw=2.5, ci_show=True)

kmf.fit(df_survival['t_ruin'][~mask_frequent_elite], df_survival['is_ruined'][~mask_frequent_elite], label="Infrequent / Non-Subscriber (<30% rounds)")
kmf.plot_survival_function(ax=ax2, color='#7f7f7f', lw=2.5, ci_show=True)

ax2.set_title("Kaplan-Meier Curves: Effect of Dynamic Institutional Access", fontsize=11, fontweight='bold')
ax2.set_xlabel("Transaction Rounds ($T_{\\text{ruin}}$)", fontsize=10)
ax2.set_ylabel("Survival Probability $S(t)$", fontsize=10)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_ylim(-0.05, 1.05)

plt.tight_layout()
plt.show()
