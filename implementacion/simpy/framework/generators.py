import numpy as np

def uniform_dist(low,high):
    return np.random.uniform(low,high)

def normal_dist(mu,std):
    return np.random.normal(mu,std,1)

def exponential_dist(mu):
    return np.random.exponential(mu)