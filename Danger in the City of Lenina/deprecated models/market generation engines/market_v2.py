# V2 of the Market Creator - SCRAPPED - No debt Caps override the effect of rationality

import numpy as np
import pandas as pd

def generate_and_export_macro_panel(n_agents=1000, n_periods=30, entry_fee_elite=300.0, seed=42, filename="macro_spatial_panel.csv"):
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

    # Upfront Education Decision (Day 1)
    has_elite_access = (s_i0 >= entry_fee_elite * 2.0)
    effective_alpha = np.where(has_elite_access, latent_alpha + (1.0 - latent_alpha) * 0.5, latent_alpha)

    # Rates
    r_market, r_gota, r_kin = 0.08, 0.35, 0.02
    phi_coercion = 40.0

    panel_records = []

    for i in range(n_agents):
        current_savings = s_i0[i]
        if has_elite_access[i]:
            current_savings -= entry_fee_elite

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

            # Debt service from t-1
            debt_service = 0.0
            if prior_loan > 0:
                if loan_type == 'Formal':
                    debt_service = prior_loan * (1 + r_market)
                elif loan_type == 'Kinship':
                    debt_service = prior_loan * (1 + r_kin)
                elif loan_type == 'Gota_a_Gota':
                    debt_service = prior_loan * (1 + r_gota)

            # Available Balance (Rule 1 & Rule 6)
            a_it = max(0.0, current_savings + w_it - debt_service)

            # Shopping decision if not ruined
            chosen_cluster = np.nan
            transaction_cost = 0.0
            new_loan = 0.0
            new_loan_type = 'None'
            shortfall = 0.0

            if a_it > 0 and not is_ruined:
                dists = np.linalg.norm(all_sellers - agent_coords[i], axis=1)
                prices = markups + dists

                mask = np.ones(len(prices), dtype=bool)
                if not has_elite_access[i]:
                    mask[cluster_labels == 2] = False

                p_sub, qt_sub, qp_sub = prices[mask], q_true[mask], q_perceived[mask]
                u_true = (qt_sub / p_sub)
                u_true_norm = (u_true - u_true.min()) / (u_true.max() - u_true.min() + 1e-6)

                u_fool = p_sub - (0.5 * qp_sub)
                u_fool_norm = (u_fool - u_fool.min()) / (u_fool.max() - u_fool.min() + 1e-6)

                u_blend = (effective_alpha[i] * u_true_norm) + ((1 - effective_alpha[i]) * u_fool_norm)

                # Coercion Utility Subtraction (Rule 4)
                if loan_type == 'Gota_a_Gota':
                    u_blend -= phi_coercion

                chosen_local_idx = np.argmax(u_blend)
                global_idx = np.where(mask)[0][chosen_local_idx]
                chosen_cluster = cluster_labels[global_idx]
                transaction_cost = prices[global_idx]

                # Deficit Borrowing (Rule 3)
                if transaction_cost > a_it:
                  shortfall = transaction_cost - a_it
                  new_loan = shortfall

                # Formal banks evaluate income/alpha, NOT just elite status

                if w_base[i] >= 45.0 or effective_alpha[i] >= 0.60:
                  new_loan_type = 'Formal'
                elif shortfall <= 100.0 and effective_alpha[i] > 0.35:
                  new_loan_type = 'Kinship'
                else:
                  new_loan_type = 'Gota_a_Gota'
                  current_savings = max(0.0, a_it + new_loan - transaction_cost)
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
                'effective_alpha': effective_alpha[i],
                'has_elite_access': int(has_elite_access[i]),
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

            prior_loan = new_loan
            loan_type = new_loan_type

    df_panel = pd.DataFrame(panel_records)
    df_panel.to_csv(filename, index=False)
    print(f"Dataset successfully saved to '{filename}'. Shape: {df_panel.shape}")
    return df_panel

# Generate and Export
df_macro = generate_and_export_macro_panel()
