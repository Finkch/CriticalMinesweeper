# Various fits for curve fitting

from numpy import e

def linear(x, m, b):
    return m * x + b

def exponential(x, m, b):
    return e ** (m * x + b) + 1
    # This is equivalent to...if m = ln(b)
    # m * e ** (m * x)

def exponentialp1(x, m, b):
    return e ** (m * x + b) + 1
    # This is equivalent to...if m = ln(b)
    # m * e ** (m * x)

def powerp1(x, a, b):
    return b * x ** a + 1

def rationalp1(x, a, b):
    return a / (x + b) + 1


# A function that starts at 0 and has a horizontal asymptote at 1
def horizontal(x, a, b):
    return a * x / (1 + b * x)
