#The Fool - V1

# Rules
# 1. The fool has a determinate allotment of resources
# 2. When presented with the choice, the fool always picks the most expensive option
# 3. The fool has no long-term vision whatsoever

#Demonstration of fundamental concept concept - assume equal products sourced on different parts of the city of Saint Petersburg

allotment = 400
cost_a = 100
cost_b = 300

def fools_mind(allotment, cost_a, cost_b):

  if cost_a > cost_b:
    print("The fool says A is better than B")
  else:
    print("The fool says B is better than A")

fools_mind(allotment,cost_a,cost_b)



