import matplotlib.pyplot as plt
import numpy as np
from experiment import Experiment
from scipy.optimize import curve_fit
from math import ceil, floor, log10


# Plots a histogram of all trials.
# Only really makes sense is rho_critical is constant over experiments
def histogram(exp_results: dict):

    results = exp_results['fulle']
    params  = exp_results['compressede']

    #cutoff = int(params['cutoff'])
    cutoff = results[-1]

    # Sorts the data into bins
    n_bins = 50
    bins = [1] * (n_bins + 1) # Start at 1 in each bin so taking the log doesn't freak out later

    # Gets the cutoff value and uses that to determine bin size
    bin_size = ceil(cutoff / n_bins)


    # Places data into bins
    for result in results:
        bins[result // bin_size] += 1


    # "x-data" for the bins
    binx = [i * bin_size for i in range(n_bins + 1)]



    # Gets the figure and its axes
    fig, axes = plt.subplots(2)

    # Plots the linear version.
    # Uses bar rather than hist so we can later take log for linear fit
    axes[0].bar(
        binx,
        bins,
        bin_size * 0.9
    )
    axes[0].set_title(f'Histogram of reveals (rho = {params["rho"]})')


    # Logs the plot
    binsl = np.log(bins)



    # Plots a histogram.
    # Uses bar rather than hist so we can take log for linear fit
    axes[1].bar(
        binx, # Histogram bin positions
        binsl,
        bin_size * 0.9
    )
    axes[1].set_title(f'Log-linear histogram of reveals (rho = {params["rho"]})')


    # Performs a linear fit
    guess = (
        -1, bins[0]
    )
    fits, cov = curve_fit(linear, binx, binsl, guess)
    uncs = np.sqrt(np.diag(cov))

    # Creates a line for the data
    linx = np.arange(0, cutoff, n_bins)
    liny = [linear(x, fits[0], fits[1]) for x in linx]

    # Adds the best fit line to the plot
    axes[1].plot(linx, liny, linestyle='-', marker='', color = 'r')

    # Tries adding a line to linear plot
    expy = [exponential(x, fits[0], fits[1]) for x in linx]

    axes[0].plot(linx, expy, linestyle='-', marker='', color = 'r')

    # Shows the covariance matrix in full
    print('Covariance matrix:')
    print(cov)

    # Shows best guesses
    print(f'\nGuesses\n.. m:\t{sigfigs(fits[0], uncs[0])}\n.. b:\t{sigfigs(fits[1], uncs[1])}')

    plt.show()


def linear(x, m, b):
    return m * x + b

def exponential(x, m, b):
    return np.e ** (m * x + b)


# Formats a number with its uncertainty
def sigfigs(x, u):

    # Gets the power of x
    px = floor(log10(abs(x)))

    # Divides down both until x has one digit before the decimal
    x /= (10 ** px)
    u /= (10 ** px)

    # The precision of unc after 
    pu = abs(floor(log10(u)))


    # Formats and returns
    return f'({round(x, pu)} ± {round(u, pu)}) × 10^{px}'
