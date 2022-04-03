from typing import Union
import numpy as np

def uniform_dist(low: Union[float, int], high: Union[float, int]):
    """Random data generator for the uniform distribution.

    Args:
        low (Union[float, int]): The minimum value that can be generated
        high (Union[float, int]): The maximum value that can be generated

    Returns:
        A random number uniformly distributed between [low, high)
    """
    return np.random.uniform(low,high)

def normal_dist(mu: Union[float, int], std: Union[float, int]):
    """Random data generator for the normal distribution.

    Args:
        mu (Union[float, int]): The mean of the distribution.
        std (Union[float, int]): The standard deviation of the distribution

    Returns:
        A random number that follows a normal distribution with mean mu and standard deviation std.
    """
    return np.random.normal(mu,std,1)

def exponential_dist(mu: Union[float, int]):
    """Random data generator for the exponential distribution.

    Args:
        mu (Union[float, int]): The mean or scale of the distribution.

    Returns:
        A random number that follows an exponential distribution with scale mu.
    """
    return np.random.exponential(mu)