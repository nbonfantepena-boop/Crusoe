#The Fool - V3

# Rules
# 1. The fool has a determinate allotment of resources
# 2. When presented with the choice, the fool always picks the most expensive option
# 3. The fool has no long-term vision whatsoever
# 4. The fool conflates quality with production cost, he will pick the lowest-quality one between two equally priced products, however, a higher price overrides a lower quality good
# 5. The fool negatively optimizes search distance, the more he has to look for a product, the more he wants it
# 6. THe fool is a Non-Pareto anti-optimizer

#First Transactional Model
#Price function is distance-dependent: P_i = A_i + d_i where A_i represents the seller's baseline price/final consumer price at that market station, referred to as markup (i.e. what the seller gets on top of whatever it costs them to have that product available in their market station)
# The fool's fundamental utility funcition is therefore U = price - 1/2*quality

import numpy as np
import pandas as pd

class Spatialmerket:
  "The fool's house is at (0,0), a centroid in the market grid that models his residence city of Saint Petersburg"
  def __init__(self, n_sellers = 50, seed = 42):
    np.random.seed(seed)
    self.n_sellers = n_sellers

    #features
    self.seller_id = [f"Seller_{i+1}" for i in range(n_sellers)]
    self.x = np.random.uniform(-10, 10, n_sellers)
    self.y = np.random.uniform(-10, 10, n_sellers)
    self.distance = np.sqrt(self.x**2 + self.y**2) #d_i
    self.markup = np.random.uniform(10, 100, n_sellers) #A_i
    self.quality = np.random.uniform(1, 5, n_sellers) #Q_i

    self.price = self.markup + self.distance
    self.df = pd.DataFrame({
        'seller_id': self.seller_id,
        'distance': self.distance,
        'markup': self.markup,
        'price': self.price,
        'quality': self.quality

    })

class TheFoolV3:
  def __init__(self, allotment = 500.0, generosity_index= 1.0):
    self.allotment = allotment
    self.generosity_index = generosity_index #Non-Pareto

  def perceive_utility(self,df):
    """
    Reminder - the fool's heuristic:
    Maximizes price (P_i) and penalizes quality (Q_i).
    Conflates a high searching cost with prestige/value
    """
    return df['price'] - (0.5*df['quality'])

  def select_option(self, market_df):
    perceived_u = self.perceive_utility(market_df)
    chosen_idx = np.argmax(perceived_u)
    return market_df.iloc[chosen_idx]

  def evaluate_pareto_transfer(self, current_cost, requested_surplus_transfer):
    """
    The fool, given his solidary nature, does not protest Pareto inefficiencies that come at his cost
    Thus, he accepts any price increase (delta_P > 0) willingly.
    """
    if requested_surplus_transfer >= 0:
      return True, current_cost + requested_surplus_transfer
    return False, current_cost

#WIll you ever optimize, darling? (Monte Carlo Sims)

def run_simulation(iterations=1000):
  accidental_optimizations = 0
  results = []

  for i in range(iterations):
    market = Spatialmerket(n_sellers=20, seed = i)
    df = market.df

    #True Pareto/ Highest Quality per Unit Price
    df['true_utility'] = df['quality']/df['price']
    rational_choice = df.loc[df['true_utility'].idxmax()]

    #A Fool's Pareto
    fool = TheFoolV3()
    fools_choice = fool.select_option(df)

    #See if the broken clock has been right at least once (if the anti-homo economicus randomly hit the optimum)
    is_optimal = (fools_choice['seller_id'] == rational_choice['seller_id'])
    if is_optimal:
      accidental_optimizations += 1

    results.append({
        'sim': i,
        'fool_price': fools_choice['price'],
        'rational_price': rational_choice['price'],
        'fool_quality': fools_choice['quality'],
        'rational_quality': rational_choice['quality'],
        'accidental_opt': is_optimal
    })

  res_df = pd.DataFrame(results)
  print(f"Total Simulations: {iterations}")
  print(f"Accidental Optimizations: {accidental_optimizations}")
  print(f"Probability of Accidental Optimization: {accidental_optimizations / iterations:.4%}")
  return res_df

sim_data = run_simulation(1000)

#Under standard independent random uniform distributions, accidental optimization can't occur, and the probability of an anti-optimizer agent remains zero, this proves that the agent in itself is correctly plotted to defy market logic
#In a classical regime, the fool would die impoverished and live unwittingly abused by the other market agents that are able to extract surplus from the fool's structurally inadequate decisions
