# Crusoe
> *"I learned to look more upon the bright side of my condition, and less upon the dark side, and to consider what I enjoyed, rather than what I wanted."*  
> — Daniel Defoe, *Robinson Crusoe*

`Crusoe` is an open-source repository of quantitative economics, applied econometric models, microeconomic bridge projects, and self-authored analytical engines.

---

## Repository Architecture

```text
Crusoe/
│
├── Danger in the City of Lenina/             # Spatial agent-based model of credit rationing & market access
│   ├── python/                 # Object-oriented simulation engine & "The Fool" module
│   ├── notebooks/              # Kaplan-Meier & Cox Proportional Hazards empirical vignettes
│   └── output/                 # Survival curves and hazard ratio plots
│
├── johansen-engine/
│   ├── r/                      # Legacy custom R function implementation
│   ├── python/                 # Object-oriented Python JohansenCointegrationTest engine
│   └── notebooks/              # Empirical macro cointegration vignette
│
├── sec-gaap-panel/
│   ├── data/                   # SEC EDGAR processed panel dataset (2020–2025)
│   ├── scripts/                # TWFE OLS, DiD Shift-Share & Counterfactual simulation
│   └── output/                 # Regression plots and diagnostic exports
│
├── okun-law/
│   ├── r/                      # Custom R function for Okun's Law elasticity
│   ├── python/                 # Object-oriented Python OkunLawEstimator engine
│   └── notebooks/              # Comparative empirical macro vignette
│
└── README.md                   # Repository documentation
```

---

## Projects & Analytical Modules

### 1. Spatial Agent-Based Model of Credit & Market Access (`/Danger in the City of Lenina`)
A computational simulation evaluating financial ruin, credit rationing, and informal lending traps within a spatially segregated market economy (*The City of Lenina*).

* **Model Framework:** Simulates $N = 1000$ archetypes over $T = 30$ consumption periods across three spatial centroids (The Port / Gray Market, City Center / Baseline Formal Market, and Sverdlova Avenue / Elite Market).
* **Behavioral Architecture:** Utility is a convex combination of rational optimization ($U_{\text{true}}$) and Myshkinian non-optimization ($U_{\text{fool}}$), governed by an agent's effective cognitive capacity ($\alpha$). "The Fool" serves as an axiomatic foundation of anti-optimization.
* **Credit Tiers:** Integrates formal credit caps ($\text{DSI} \le 40\%$), kinship loans, and predatory lenders (*Gota a Gota*) carrying explicit coercion disutility ($\phi_{\text{coercion}}$).
* **Key Finding (V3 vs. V4 Iteration):** Moving from a static entry barrier to a dynamic, per-period subscription charge ($C_{\text{elite}} = 25.0$) breaks the predatory debt trap. Exposure to *Gota a Gota* credit drops to statistical non-significance ($p = 0.36$), while participation share in transparent elite markets (`share_elite_access`) becomes the dominant driver of financial survival ($p < 0.005$, $\text{coef} = -5.12$).

### 2. Custom Johansen-Juselius Cointegration Engine (`/johansen-engine`)
A ground-up implementation of the Johansen (1988, 1991) multivariate cointegration test designed to evaluate long-run equilibrium relationships without relying on black-box wrapper functions.

* **Mathematical Foundation:** Implements reduced-rank regression, canonical correlation analysis, and generalized eigenvalue decomposition ($|\lambda S_{11} - S_{10}S_{00}^{-1}S_{01}| = 0$).
* **Features:**
  * Supports all 5 deterministic trend specifications (Osterwald-Lenum / Johansen models).
  * Calculates exact Trace ($\lambda_{\text{trace}}$) and Maximum Eigenvalue ($\lambda_{\text{max}}$) statistics.
  * Cross-language implementations available in both **R** and **Python** (`johansen_engine`).
* **Applications:** Testing long-run macroeconomic equilibrium relationships (Okun's Law, Phillips Curve trade-offs) across diverse macro structures (e.g., US, Colombia, transitional economies).

### 3. GAAP Operational Efficiency & AI Cost-Shock Panel (`/sec-gaap-panel`)
An empirical evaluation of scale economies, SG&A overhead intensity, and corporate technology cost-absorption strategies across U.S. IT services firms (2020–2025).

* **Data Pipeline:** Custom Python extractors parsing quarterly SEC EDGAR XBRL filings (`10-K`, `10-Q`) .
* **Econometric Framework:**
  * **Model 1 (Scale Economies):** Two-Way Fixed Effects (TWFE) OLS with clustered standard errors by firm ($\hat{\beta}_{\text{scale}} = -0.024047$, $p = 0.0022$).
  * **Model 2 (Build vs. Buy Shift-Share):** Difference-in-Differences specification evaluating post-2022 GenAI adoption and token pricing shocks across cross-sectional digital exposure levels.
* **Key Finding:** Scale remains the primary driver of SG&A margin efficiency ($R^2 = 0.9438$). High-exposure digital consultancies demonstrate overhead dilution post-2022, supporting the "Build" (indigenous AI tool development) hypothesis over third-party API pass-through.

### 4. Okun's Law Macroeconomic Engine (`/okun-law`)
An empirical macroeconometric framework quantifying the elasticity trade-off between output growth deviations and unemployment changes across differing structural economies .

* **Specifications:**
  * **Difference Model:** $\Delta U_t = \alpha + \beta (g_t - \bar{g}) + \varepsilon_t$
  * **HP-Filter Gap Model:** $(U_t - \hat{U}_t) = \alpha + \beta (Y_t - \hat{Y}_t) + \varepsilon_t$
* **Methodological Features:**
  * Dynamic Hodrick-Prescott (HP) filter decomposition ($\lambda = 1600$ for quarterly data).
  * Heteroskedasticity and Autocorrelation Consistent (HAC / Newey-West) robust standard error adjustments.
  * Dual implementations in **R** and object-oriented **Python** (`okun_law`).
* **Applications:** Cross-country comparison of labor market flexibility and unemployment-growth responsiveness across emerging, reserve-currency, and transitional economies.

---

## Tech Stack & Econometrics Toolkit

* **Languages:** Python (3.10+), R
* **Data & Estimation:** `pandas`, `numpy`, `scipy.linalg`, `statsmodels`, `linearmodels`, `lifelines`
* **Visualization:** `matplotlib`, `seaborn`
* **Econometric & Computational Methods:** Spatial Agent-Based Modeling (ABM), Kaplan-Meier Survival Analysis, Cox Proportional Hazards (Firth's Penalized Likelihood), Two-Way Fixed Effects (TWFE), Difference-in-Differences (DiD), Vector Error Correction Models (VECM), Reduced-Rank Regression, Bartik Shift-Share Instrument.

---

## License
This repository is open-sourced under the MIT License. All scripts and frameworks are self-authored for research and quantitative portfolio demonstration purposes.
