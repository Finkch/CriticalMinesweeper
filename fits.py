# Various fits for curve fitting

from numpy import e

def linear(x, m, b):
    return m * x + b

def exponential(x, m, b):
    return e ** (m * x + b)
    # This is equivalent to...if m = ln(b)
    # m * e ** (m * x)