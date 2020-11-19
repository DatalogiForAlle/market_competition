import urllib
import pandas as pd
import numpy as np
import random

github_url = "https://raw.githubusercontent.com/DatalogiForAlle/market_competition/master"

def get_parameters():
    # Hent parametre som .csv-filer
    urllib.request.urlretrieve(github_url + "/p_params.csv", "p_params.csv")
    urllib.request.urlretrieve(github_url + "/pe_params.csv", "pe_params.csv")
    urllib.request.urlretrieve(github_url + "/q_params.csv", "q_params.csv")

    # Indlæs .csv filer
    pe_params = pd.read_csv('pe_params.csv')
    p_params = pd.read_csv('p_params.csv')
    q_params = pd.read_csv('q_params.csv')

    # Udvælg parametre fra det første eksperiment
    group_id = 1
    pe_params = pe_params[pe_params["Group"] == group_id]
    p_params = p_params[p_params["Group"] == group_id]
    q_params = q_params[q_params["Group"] == group_id]
    pe_params.reset_index()
    p_params.reset_index()
    q_params.reset_index()
    return pe_params, p_params, q_params

# Agent class
class Producer:
    def __init__(self, initial_price, initial_production, endowment, c, pe, p, q):
        # Initiale værdier
        self.price = initial_price
        self.price_t1 = initial_price # pris ved t-1
        self.price_t2 = initial_price # pris ved t-2
        
        self.market_price_forecast = self.price
        self.quantity = initial_production
        self.excess_supply = 0
        
        self.profit = 0
        self.profit_t1 = 0 # profit t-1
        self.profit_t2 = 0 # profit t-2
        self.price_adjustment = 0 # Pi i paperet

        # Vi sætter konstanterne epsilon, u, eta til 0 (paperet fortæller ikke hvordan de er sat)
        self.epsilon = random.gauss(0, 0.5)
        self.u = random.gauss(0, 0.5)
        self.eta = random.gauss(0, 0.5)

        # Koefficienter for agenten baseret på estimater
        self.pe = pe
        self.p = p
        self.q = q
        
        # Marginal produktionsomkostning
        self.mc = c
        
        # Balance is set to initial endowment
        self.balance = endowment
        self.bankrupt = False

    def set_price(self, market_price_t1, market_price_t2):
        if self.bankrupt:
            self.price = np.nan
            return
        
        # Forudsig indeværende periodes gennemsnitlige pris
        self.market_price_forecast = (self.pe.c
                                      + self.pe.alpha_1 * market_price_t1
                                      + self.pe.alpha_2 * self.market_price_forecast
                                      + self.pe.alpha_3 * market_price_t2
                                      + self.epsilon)

        # Opdater historiske priser
        self.price_t2 = self.price_t1
        self.price_t1 = self.price
        
        # Sæt vores pris denne periode
        self.price = (self.p.c 
                      + self.p.beta_1 * self.price
                      + self.p.beta_2 * self.market_price_forecast
                      + self.p.beta_3 * self.price_adjustment
                      + self.p.beta_4 * self.excess_supply
                      + self.u)

    def set_production_level(self):
        if self.bankrupt:
            self.quantity = np.nan
            return
        
        # Estimer efterspørgsel
        estimated_demand = (self.q.c
                            + self.q.gamma_1 * self.quantity
                            + self.q.gamma_2 * self.price
                            + self.q.gamma_3 * self.market_price_forecast
                            + self.q.gamma_4 * self.excess_supply
                            + self.eta)

        # Producer den mængde vi forventer der efterspørges
        self.quantity = max(estimated_demand, 0)

    def observe_demand(self, demand):
        if self.bankrupt:
            self.excess_supply = np.nan
            return
        
        # Opdater overskud i varer (hvor meget blev ikke solgt)
        self.excess_supply = max(self.quantity - demand, 0)
    
    def calculate_profit(self, demand):
        if self.bankrupt:
            self.profit = np.nan
            return
        
        # Opdater historisk profit
        self.profit_t2 = self.profit_t1
        self.profit_t1 = self.profit

        # Beregn profit i denne periode
        self.profit = self.price*demand - self.mc*self.quantity
        
        # Opdater balance
        self.balance += self.profit
        
        # Er vi gået konkurs?
        self.bankrupt = self.balance < 0

    def update_price_adjustment(self):
        # Korriger pricer i den retning som giver højere profit
        if self.bankrupt:
            self.price_adjustment = np.nan
            return
        
        # Ændring i pris i forrige periode
        price_difference = self.price_t1 - self.price_t2
        
        if self.profit_t1 < self.profit_t2:
            # Hvis profitten er gået ned, justerer vi prisen længere ned
            self.price_adjustment = - price_difference
        else:
            # Hvis profiten er gået op, justerer vi prisen længere op
            self.price_adjustment = price_difference

# # Hjælpefunktioner
# def get_attr(agents, attr):
#     x = []
#     for agent in agents:
#         x.append(getattr(agent, attr))
#     return x
