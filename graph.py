import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from math import ceil, floor, log10

from fits import linear, exponential, exponentialp1, powerp1, rationalp1


# Formats a number with its uncertainty.
# I will steal this function for later use - the simplest and cleanest I ever made it!
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


# These results are a straight delog.
# Instead, dict where key is radius of safe zone
def show_is_start_rho(results: dict):
    
    # Isolates the values of rho for easier calculation
    rhos = [rho for rho in results.values()]
    
    # Finds the average rho and its error
    mean = np.mean(rhos)
    se = np.std(rhos) / np.sqrt(len(rhos))
    
    # Prints the results
    print(f'Mean critical density over r = [0, 9]:\n.. {sigfigs(mean, se)}')

    # Creates the plot
    fig, ax1 = plt.subplots()

    # Creates a bar plot for the rhos
    ax1.set_xlabel('radius of safe starting area (cells)')
    ax1.set_ylabel('critical density')
    ax1.bar([k for k in results], rhos)


    plt.show()


def show_alphas(exps: list):
    
    # Grabs relevant data
    alphas = [exp['alphase'] for exp in exps]
    rhos = [float(exp['compressede']['rho']) for exp in exps]

    # Packeges key results together so they can be sorted
    results = sorted([[alphas[i], rhos[i]] for i in range(len(alphas))], key = lambda x: x[1])

    infinities = []

    # Gets the plots
    fig, ax = plt.subplots()

    # Creates a scatter plot of growth factors for each rho
    for i in range(len(results)):
        ax.scatter(
            [j / len(results[i][0]) for j in range(len(results[i][0]))],
            results[i][0],
            label = r'${\rho}$ = ' + f'{results[i][1]:.3f}'
        )

        # Gets a list of the earliest infinites
        # for j in range(len(results[i][0])):
        #     if results[i][0][j] >= 1:
        #         infinities.append([j, results[i][1]])
        #         break


    # Shows where each goes infinite
    sx = [inf[0] for inf in infinities]
    sy = [1 for inf in infinities]
    ax.scatter(sx, sy, color = 'black', marker = 'x')


    # Shows labels
    ax.set_xlabel(r'P(${\alpha} {\geq}$ X)')
    ax.set_ylabel(r'growth factor ${\alpha}$ (unitless)')

    ax.legend(loc = 'lower right')


    plt.show()

# When rho is zero, how does alpha grow?
def show_max_alphas(alphas, cutoffs):

    # Gets the important information
    alphas.sort(reverse = True)
    cutoffs = [i for i in range(len(cutoffs))] # Use radius rather than cells for cutoff

    # Gets initial guesses
    guesses = {
        'exponential': (-1, 2),
        'power': (-1, 2),
        'rational': (2, 3)
    }

    # Grabs the functions for the fits
    funcs = {
        'exponential': exponentialp1,
        'power': powerp1,
        'rational': rationalp1
    }

    # List of fits
    fits, covs, uncs = {}, {}, {}

    # Performs a series of fits
    for guess in guesses:

        # Does the fit
        fit, cov = curve_fit(funcs[guess], cutoffs, alphas)

        # Grabs the data and uncertainty
        fits[guess] = fit
        covs[guess] = cov
        uncs[guess] = np.sqrt(np.diag(cov))



    # Plots the data
    fig, ax = plt.subplots()
    ax.scatter(cutoffs, alphas, color = 'black')


    # Plots the guesses
    x = np.arange(min(cutoffs), max(cutoffs), 0.01)

    # Plots each of the guesses
    for guess in guesses:

        # Gets y data by applying the fit
        y = [funcs[guess](xi, *fits[guess]) for xi in x]

        # Plots
        ax.plot(x, y, label = guess)

        # Prints the best guess parameters
        print(f'Best fit for {guess}:\n.. a: {sigfigs(fits[guess][0], uncs[guess][0])}\n.. b: {sigfigs(fits[guess][1], uncs[guess][1])}\n')


    # Labels and such
    ax.set_xlabel('radius (cells)')
    ax.set_ylabel(r'max growth factor ${\alpha}_{max}$')

    ax.legend()

    plt.show()