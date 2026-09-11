# Danger in the City of Lenina: A Spatial Agent-Based Model of Credit Rationing, Market Access, and Financial Survival

> *Title inspired by Joanna Stingrey’s homonymous track.*

## Model Overview & Intuition

The **City of Lenina** is a synthetic computational environment populated by $N = 1000$ consumer archetypes who execute a single discrete consumption transaction per period ($t \in \{1, \dots, 30\}$). Agents require a single, non-storable consumer good (or representative consumption basket) to survive, optimize utility, and derive economic satisfaction.

The good is distributed across a degenerated, spatially segregated market structure featuring three distinct spatial centroids:
1. **The Port (Gray Market):** An informal, informationally opaque market selling a subpar version of the good at standard market prices. Sellers at the Port exploit information asymmetries, masking true quality to trap low-information consumers.
2. **The City Center (Baseline Formal Market):** A standard market hub offering baseline quality goods with transparent pricing.
3. **Sverdlova Avenue (Elite Gatekept Market):** A premium market location connected directly to primary production pipelines. It offers high-quality goods with zero information asymmetry, accessible only to agents who pay an institutional access fee.

Agents are initialized across the spatial topology with coordinates determined by Euclidean distances to these three centroids. Each agent is endowed with a stochastically assigned initial capital buffer ($S_{i,0}$), a baseline wage ($W_{\text{base}}$), and a measure of cognitive rationality ($\alpha_i \in [0, 1]$). 

Income is generated via factory production, combining a deterministic wage reflecting spatial/hierarchical positioning with a stochastic productivity commission.

---

## Behavioral Dynamics & Utility Architecture

Agent choice is governed by a convex combination of two distinct utility frameworks, parameterized by the agent's effective cognitive capacity ($\alpha$):

1. **The Rational Optimizer ($U_{\text{true}}$):** Evaluates choices based on true underlying quality relative to price ($Q_{\text{true}} / P$).
2. **The Fool ($U_{\text{fool}}$):** Inspired by Prince Myshkin in Dostoevsky’s *The Idiot*, "The Fool" is the foundational concept that gave way for the development of a bounded rationality model for the City of Lenina, it models a catastrophic non-optimizer who derives utility from distorted price-quality signals, systematically overpaying for low-quality goods ($P - 0.5 \cdot Q_{\text{perceived}}$).

Higher cognitive capacity ($\alpha$) shifts agent preference toward $U_{\text{true}}$. In baseline versions, institutional access to Sverdlova Avenue is granted via a static, one-off capital investment. In advanced iterations, this is extended to a **per-period dynamic subscription regime**, introducing inter-period savings incentives, liquidity thresholds, and endogenous market-switching behavior.

---

## Financialization, Credit Rationing, and Coercion

When an agent's available liquidity ($A_{i,t}$) is insufficient to cover transaction costs, the agent must draw from one of three credit tiers:

* **Formal Banking System:** Offers standard market interest rates ($r_{\text{market}}$) but enforces strict credit rationing based on a maximum Debt-Service-to-Income (DSI) cap ($\text{DSI} \le 40\%$). Formal debt enters the utility function as neutral.
* **Kinship Networks:** Offers low-interest concessionary loans ($r_{\text{kin}}$) for moderate, localized shortfalls.
* **Informal Lenders (*Gota a Gota*):** Operates as an unconstrained lender of last resort charging exorbitant interest rates ($r_{\text{gota}}$). Borrowing from *Gota a Gota* imposes a severe, constant disutility penalty ($\phi_{\text{coercion}}$) on all subsequent transactions, reflecting the threat of physical or psychological coercion.

Financial ruin occurs endogenously when an agent's available capital buffer drops to zero, terminating their participation in the economy.

---

## Econometric Methodology

The primary analytical goal is to evaluate survival trajectories and identify the structural determinants of systemic financial ruin across time ($T_{\text{ruin}}$). The econometric pipeline consists of:

1. **Kaplan-Meier Survival Analysis:** Non-parametric estimation of survival curves $S(t)$, stratified by credit channel exposure (*Gota a Gota* vs. formal credit) and market access frequency.
2. **Cox Proportional Hazards Model:** Semi-parametric modeling of instantaneous hazard rates of ruin as a function of spatial positioning, initial wealth endowment, rationality, and institutional access.
3. **Firth’s Penalized Likelihood Cox Model:** Implementation of an $L_2$ ridge penalty (`penalizer = 0.1`) to resolve quasi-complete separation issues caused by strong deterministic predictors (e.g., frequent elite market subscription vs. predatory credit traps).

---

## Model Evolution & Comparative Empirical Outcomes (V3 vs. V4)

To evaluate how market access mechanics influence financial ruin, the model was executed across two structural iterations ($N = 1000$, $T = 30$). The transition from a static, one-off entry fee (**V3**) to a dynamic, per-period subscription charge (**V4**) reveals how institutional fluidness alters credit dynamics and agent survival trajectories.

              ┌─────────────────────────────────────────┐
              │          INITIAL STATE (V3)             │
              │  Static One-Off Entry Fee to Sverdlova  │
              └────────────────────┬────────────────────┘
                                   │
                     [ High Barrier to Entry ]
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │       PREDATORY TRAP MECHANISM          │
              │  Gota a Gota is a Significant Predictor │
              │     p < 0.005 | Coercion Disutility     │
              └────────────────────┬────────────────────┘
                                   │
                   [ Introduce Per-Period Access ]
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │         DYNAMIC ACCESS (V4)             │
              │ Dynamic Subscription Fee (c_elite = 25) │
              └────────────────────┬────────────────────┘
                                   │
                [ Intermittent Capital Reset Valve ]
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │          EMPIRICAL SHIFT                │
              │  Gota a Gota loses significance (p=.36) │
              │  Elite Access Share Dominates (p<.005)  │
              └─────────────────────────────────────────┘

### Comparative Summary Table

| Metric / Dimension | V3: Static Entry Barrier | V4: Dynamic Subscription Model | Structural Shift |
| :--- | :--- | :--- | :--- |
| **Sverdlova Access Rule** | Capital threshold for lifetime access | Per-period cover charge ($C_{\text{elite}} = 25.0$) | Converts static class barrier into fluid liquidity threshold |
| **Predatory Debt Effect (`ever_used_gota`)** | **Statistically Significant** ($p < 0.005$)<br>Primary driver of default | **Statistically Non-Significant** ($p = 0.36$, $z = 0.92$)<br>Predictive power absorbed | Predatory credit loses its status as an inescapable cause of ruin |
| **Institutional Access Effect (`share_elite_access`)** | Binary, highly skewed toward initial wealthy agents | **Dominant Predictor** ($p < 0.005$, $\text{coef} = -5.12$, $z = -19.73$) | Periodic access acts as a recurring capital and cognitive reset |
| **Agent Mobility & Strategy** | Permanent structural lock-in (trapped vs. safe) | Intermittent participation (precautionary saving to buy entry) | Introduces endogenous savings cycles and market-switching |
| **Survival Bimodal Split** | Wealth-based cleavage | Frequency-based cleavage ($\ge 30\%$ subscriber rounds $\to S(t) \approx 0.78$) | Financial survival depends on access frequency rather than baseline endowment |

---

### Key Takeaways from the Iteration

1. **Eradication of the Predatory Trap:** In V3, borrowing from *Gota a Gota* operates as a deterministic death spiral due to exorbitant interest rates ($r_{\text{gota}}$) and coercion penalties ($\phi_{\text{coercion}}$). In V4, allowing agents to periodically purchase access to efficient markets breaks the opportunistic monopoly of informal lenders, rendering `ever_used_gota` non-significant in predicting hazard rates of ruin.
2. **Access as a Structural Safety Valve:** In V4, every period an agent affords the subscription fee, their effective rationality ($\alpha$) is boosted, shielding them from the information asymmetries of the Port. This enables them to purchase high-quality goods at fair prices, preserving capital and generating an endogenous buffer against future defaults.
3. **Policy Implications:** Predatory debt exposure is not an exogenous behavioral failure, but an **endogenous symptom** of persistent institutional lockout. Lowering barriers to fluid, dynamic market participation eliminates the structural reliance on informal credit channels.

---

## Theoretical Literature Framework

The assumptions governing this computational market draw upon established theoretical models across financial economics, spatial search, and behavioral microeconomics:

* **Dynamic Market Access & Participation Costs:** The transition from static entry barriers to per-period cover charges draws on **Vissing-Jørgensen (2002)** and **Mankiw & Zeldes (1991)**, demonstrating how recurring fixed participation costs generate endogenous entry/exit dynamics and liquidity-driven market switching.
* **Credit Rationing & Informal Credit Traps:** Formal capacity caps and DSI ceilings are grounded in **Stiglitz & Weiss (1981)**. The coercion mechanics and local opportunistic monopolies of informal credit markets follow **Banerjee & Duflo (2010)**, while asset threshold dynamics mirror **Carter & Barrett (2006)**.
* **Bounded Rationality & Cognitive Bandwidth:** The dual-utility specification ($U_{\text{blend}}$) and the cognitive tax imposed by financial distress build upon **Gabaix (2014)** on sparse bounded rationality and **Mullainathan & Shafir (2013)** on scarcity-induced bandwidth limits.

---

### Reference Reading List

* **Banerjee, A. V., & Duflo, E. (2010).** *Gleanings from Services for the Poor: Credit Markets.* Journal of Economic Perspectives, 24(3), 61-80.
* **Carter, M. R., & Barrett, C. B. (2006).** *The Economics of Poverty Traps and Persistent Poverty: An Asset-Based Approach.* Journal of Development Studies, 42(2), 178-199.
* **Gabaix, X. (2014).** *A Sparsity-Based Model of Bounded Rationality.* Quarterly Journal of Economics, 129(4), 1661-1710.
* **Mankiw, N. G., & Zeldes, S. P. (1991).** *The Consumption of Stockholders and Nonstockholders.* Journal of Financial Economics, 29(1), 97-112.
* **Mullainathan, S., & Shafir, E. (2013).** *Scarcity: Why Having Too Little Means So Much.* Times Books, Henry Holt and Company.
* **Stiglitz, J. E., & Weiss, A. (1981).** *Credit Rationing in Markets with Imperfect Information.* American Economic Review, 71(3), 393-410.
* **Vissing-Jørgensen, A. (2002).** *Towards an Explanation of Household Portfolio Choice Risks: Estimating Fixed Fractional Costs of Stock Market Participation.* BMC Economics, 110(6), 825-853.
              
