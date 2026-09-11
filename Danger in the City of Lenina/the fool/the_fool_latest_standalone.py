#The Fool - V4
#
# Multi-Good Matrix & Non-Classical Regimes - Allotment remains there but so far I've not used it, see the inclusion of wealth decay for an expanded concept of allotment
#
# Behavioral Rules
# 1. The fool has a determinate allotment of resources
# 2. When presented with the choice, the fool always picks the most expensive option
# 3. The fool has no long-term vision whatsoever
# 4. The fool conflates quality with production cost, he will pick the lowest-quality one between two equally priced products, however, a higher price overrides a lower quality good
# 5. The fool negatively optimizes search distance, the more he has to look for a product, the more he wants it
# 6. THe fool is a Non-Pareto anti-optimizer
#
# Market Rules
# 1. The market is now a matrix M(S, G) across S sellers and G distinct goods.
# 2. Price function incorporates spatial transport and item markups: P_{s,g} = A_{s,g} + d_s.
# 3. The fool selects the joint tuple (s*, g*) that maximizes perceived utility: U = P_{s,g} - 0.5 * Q_{s,g}.
# 4. Market regimes where price signals carry non-classical information (for example, Veblen Goods) are the target of V4's evaluation.

import numpy as np
import pandas as pd

class MultiGoodSpatialMarket:
  """
  S x G market matrix centered around the city of Saint Petersburg (0,0)
  The design allows the parameterizatio of the covariance between Price and Quality
  """

  def __init__(self, n_sellers=20, n_goods=10, regime='classical', seed=42):
    np.random.seed(seed)
    self.n_sellers = n_sellers
    self.n_goods = n_goods
    self.regime = regime

    #Spatial coordinates
    self.x = np.random.uniform(-10, 10, n_sellers)
    self.y = np.random.uniform(-10, 10, n_sellers)
    self.distances = np.sqrt(self.x**2 + self.y**2)

    #Quality matrix (S x G)
    self.qualities = np.random.uniform(1.0, 10.0, size=(n_sellers, n_goods))

    if regime == 'classical':
      # Standard independent market: Price and Quality remain uncorrelated
      self.markups = np.random.uniform(10, 100, size=(n_sellers, n_goods))
    elif regime == "veblen":
      #Veblen regime: Price scales exponentially with quality (P ~ Q^2)
      self.markups = 1.5*(self.qualities**2) + np.random.normal(0,5, size=(n_sellers,n_goods))
      self.markups = np.abs(self.markups)
    elif regime == "perfect_signal":
      #Quality is the price (P = k*Q)
      self.markups = 12.0*self.qualities

    #Price Matrix
    self.prices = self.markups + self.distances[:, np.newaxis]

class TheFoolV4:
  def perceive_utility(self, price_matrix, quality_matrix):
    """
    The Fool's Tensor Heuristic maximizes spatial/item proce and penalizes quality
    """
    return price_matrix - (0.5*quality_matrix)

  def select_option(self, market):
    perceived_u = self.perceive_utility(market.prices, market.qualities)
    seller_idx, good_idx = np.unravel_index(np.argmax(perceived_u), perceived_u.shape)
    return seller_idx, good_idx

# Monte carlo

def run_v4_simulation(iterations=100):
  regimes = ["classical", "veblen", "perfect_signal"]
  results_summary = {}

  for r in regimes:
    accidental_optimizations = 0

    for i in range(iterations):
      market = MultiGoodSpatialMarket(n_sellers=20, n_goods = 10, regime = r, seed = i)

      true_utility = market.qualities / market.prices
      rat_s, rat_g = np.unravel_index(np.argmax(true_utility), true_utility.shape)

      fool = TheFoolV4()
      fool_s, fool_g = fool.select_option(market)

      if (fool_s == rat_s) and (fool_g == rat_g):
        accidental_optimizations += 1

    prob = accidental_optimizations / iterations
    results_summary[r] = prob
    print(f"Regime: {r:<15} | Accidental Optimizations: {accidental_optimizations}/{iterations} ({prob:.2%})")

  return results_summary

v4_results = run_v4_simulation(1000)

#Under formal market conditions, where seller information is completely known, the fool can't accidentally optimize, we have now our complete model for financial ruin
