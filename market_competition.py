import random
#import matplotlib.pyplot as plt

# Alpha: hvor meget forbrugere vil efterspørge, hvis prisen er nul
# alpha = 10.5

# Beta: hældning på demand-kurve, hvor stor effekt prisen på varen har på efterspørgslen
# beta = 1.75

# Theta: afgører hvilken indflydelse det har at prisen afviger fra markedsgennemsnittet
# theta = 1.45833

class Agent:
    def __init__(self, initial_price, quantity):
        # Initielle værdier
        self.price = initial_price
        self.market_price_forecast = self.price + random.gauss(0, 5)
        self.quantity = quantity
        self.excess_supply = 0

        # Normalfordelte konstanter (det står ikke i paperet hvordan de er sat)
        self.epsilon = random.gauss(0, 1)
        self.u = random.gauss(0, 1)
        self.eta = random.gauss(0, 1)

        # Koefficienter for agenten (pt. samme for alle agenter)
        # Disse er fra paperet, deltager 9, gruppe 4
        # beregnet via first-order heuristics

        # Koefficienter til estimering af markedspris
        self.w0 = 0.817 # vægtning af sidste obseverede markedspris
        self.w1 = 0.238 # vægtning af vores egen sidste forudsigelse

        # Koefficienter til beslutning af pris
        self.coeff_p = 0.832    # vægtning af sidste pris
        self.coeff_pe = 0.199   # vægtning af forventede markedspris
        self.coeff_S = -0.127  # straf for overskydende varer, der ikke bliver solgt

        # Koefficienter til beregning af efterspørgsel
        self.alpha = 11.812
        self.beta = 1.412
        self.theta = 1.058

    def update_price(self, market_price):
        # Forudsig fremtidig markedspris
        self.market_price_forecast = (self.w0 * market_price
                                      + self.w1 * self.market_price_forecast
                                      + self.epsilon)

        # Sæt vores pris denne periode
        self.price = (self.coeff_p * self.price
                      + self.coeff_pe * self.market_price_forecast
                      + self.coeff_S * self.excess_supply
                      + self.u)

    def observe_demand(self):
        # Beregn efterspørgsel
        demand = (self.alpha
                  - self.beta * self.price
                  + self.theta * self.market_price_forecast
                  + self.eta)

        # Opdater overskud i varer (hvor meget blev ikke solgt)
        excess_supply = max(self.quantity - demand, 0)

# Et par hjælpefunktioner
def average(prices):
    return sum(prices)/len(prices)

def prices(agents):
    prices = []
    for agent in agents:
        prices.append(agent.price)
    return prices

# Parametre for simulationen
num_agents = 2000 # Antal agenter
iterations = 50 # Antal iterationer
quantity_per_round = 20 # Alle agenter producerer lige meget

# Opret agenterne
agents = []
for i in range(num_agents):
    initial_price = random.gauss(15, 2)
    agent = Agent(initial_price, quantity_per_round)
    agents.append(agent)

# Kør simulationen
price_list = []
for t in range(iterations):
    # Beregn markedspris
    market_price = average(prices(agents))

    # Vis nuværende markedspris
    print(t, market_price)

    # Gem markedspris
    price_list.append(market_price)

    # Opdater agenterne
    for agent in agents:
        agent.update_price(market_price)
        agent.observe_demand()

# Plot
#plt.title('markedspris vs. tid')
#plt.xlabel('t')
#plt.ylabel('markedspris')
#plt.plot(range(iterations), price_list, 'm.')
#plt.show()

