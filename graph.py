import matplotlib.pyplot as plt
import numpy as np
from experiment import Experiment
from scipy.optimize import curve_fit
from math import ceil


# Plots a histogram of all trials.
# Only really makes sense is rho_critical is constant over experiments
def histogram(experiment: Experiment):

    results = experiment.results

    # Sorts the data into bins
    n_bins = 20
    bins = [1] * (n_bins + 1) # Start at 1 in each bin so taking the log doesn't freak out later

    # Gets the cutoff value and uses that to determine bin size
    bin_size = ceil(experiment.cutoff / n_bins)

    # Places data into bins
    for result in results:
        bins[result // bin_size] += 1

    # Logs the plot
    bins = np.log(bins)

    # "x-data" for the bins
    binx = [i * bin_size for i in range(n_bins + 1)]


    # Plots a histogram.
    # Uses bar rather than hist so we can take log for linear fit
    plt.bar(
        binx, # Histogram bin positions
        bins,
        bin_size * 0.9
    )

    print(bins)

    # Performs a linear fit
    guess = (
        -1, bins[0]
    )
    fits, cov = curve_fit(linear, binx, bins, guess)
    uncs = np.sqrt(np.diag(cov))

    # Creates a line for the data
    linx = np.arange(0, experiment.cutoff, n_bins)
    liny = [linear(x, fits[0], fits[1]) for x in linx]

    # Adds the best fit line to the plot
    plt.plot(linx, liny, linestyle='-', marker='', color = 'r')


    # Shows best guesses
    print(f'Guesses\n.. m:\t{fits[0]} ± {uncs[0]}\n.. b:\t{fits[1]} ± {uncs[1]}')

    plt.show()


def linear(x, m, b):
    return m * x + b

