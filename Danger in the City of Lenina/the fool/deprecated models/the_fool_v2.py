#The Fool - V2

# Rules
# 1. The fool has a determinate allotment of resources
# 2. When presented with the choice, the fool always picks the most expensive option
# 3. The fool has no long-term vision whatsoever
# 4. The fool conflates quality with production cost, he will pick the lowest-quality one between two equally priced products, however, a higher price overrides a lower uqality

#Proof of concept

allotment = 400
cost_a = 300
cost_b = 300
quality_a = 1
quality_b = 2

def fools_mind():

  if cost_a >= cost_b and quality_a < quality_b:
    print("The fool says A is better than B")
  elif cost_a < cost_b and quality_a < quality_b:
    print("The fool says B is better than A")
  elif cost_a <= cost_b and quality_a > quality_b:
    print("The fool says B is better than A")
  elif cost_a >= cost_b and quality_a > quality_b:
    print("the fool says A is better than B")

fools_mind()

