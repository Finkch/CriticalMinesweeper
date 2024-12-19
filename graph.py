import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from math import ceil, floor, log10

from fits import linear, exponential, exponentialp1, powerp1, rationalp1, horizontal


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
def histogram(reveals: dict, params: dict):

    results = reveals

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


def show_alphas(reveals, alphas, rhos):

    # Packeges key results together so they can be sorted
    results = sorted([[reveals[i], alphas[i], rhos[i]] for i in range(len(alphas))], key = lambda x: x[2])

    # Trims results
    #results = [results[i] for i in range(len(results)) if i % 20 == 0]
    nrs = []
    for result in results:
        si = [i for i in range(len(result[0])) if result[1][i] > 1]

        nrs.append([
            [result[0][i] for i in si],
            [result[1][i] for i in si],
            result[2]]
        )

    results = nrs

    infinities = []

    # Gets the plots
    fig, ax = plt.subplots()

    # Creates a scatter plot of growth factors for each rho
    for i in range(len(results)):
        ax.scatter(
            #[j for j in range(len(results[i][1]))],
            #sorted(results[i][1]),
            results[i][0],
            results[i][1],
            label = r'${\rho}$ = ' + f'{results[i][2]:.3f}'
        )

        # Gets a list of the earliest infinites
        # for j in range(len(results[i][0])):
        #     if results[i][0][j] >= 1:
        #         infinities.append([j, results[i][1]])
        #         break


    # Shows where each goes infinite
    #sx = [inf[0] for inf in infinities]
    #sy = [1 for inf in infinities]
    #ax.scatter(sx, sy, color = 'black', marker = 'x')


    # Performs a curve fit
    fits, covs, uncs = {}, {}, {}


    # Shows labels
    ax.set_xlabel(r'P(${\alpha} {\leq}$ X)')
    ax.set_ylabel(r'growth factor ${\alpha}$ (unitless)')

    ax.axhline(y = 1, color = 'black', linestyle = '-') 

    #ax.set_yscale('log')
    ax.set_xscale('log')

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

# Shows how a frontier behaves
def show_frontiers(frontiers, reveals, meta):

    # Successive differences, delta_f
    deltaf = [[frontier[i + 1] - frontier[i] for i in range(len(frontier) - 1)] for frontier in frontiers]


    # Calculates the mean delta_f for each trial.
    # Casts into numpy array for easy statistics
    deltaf_means = np.array([sum(delta) / len(delta) for delta in deltaf])
    growth = deltaf_means.mean()
    growth_unc = deltaf_means.std() / np.sqrt(len(deltaf_means))
    print(f'\n\tAverage delta_f for rho = {meta["rho"]}:\t{sigfigs(growth, growth_unc)}\n')


    # Performs a column-wise mean rather than a row-wise mean
    cw = sorted(deltaf, key = lambda x: len(x), reverse = True) # cw for column-wise
    column_mean = []
    for i in range(len(cw[0])): # Iterates over the longest row

        # Trims all rows shorter than i
        cw = [row for row in cw if len(row) > i]

        # Creates the column
        col = [cw[j][i] for j in range(len(cw))]

        # Adds the column's mean
        column_mean.append(sum(col) / len(col))


    # Packs, sorts, and unpacks important lists.
    # We do this so we can plot the same set of data readably.
    # The sort + slice shows evenly spaced (in iteration space) (thus, hopefully representative) trials
    packed = sorted(
        [(frontiers[i], deltaf[i]) for i in range(len(frontiers))], # Packes together data
        key = lambda x: len(x[0]),                                  # Sorts based on iterations to die out
        reverse = True                                              # Plot biggest first, so it doesn't overshadow
    #)[:: len(frontiers) // 5]                                       # Slices to get evenly spaced
    )

    # Unpacks data again
    frontiers = [tup[0] for tup in packed]
    deltaf = [tup[1] for tup in packed]

    # Makes a subset of data so the plots look reasonable rather than just noise.
    fraction        = 5 # What fraction of data to include
    frontiers_few   = frontiers[::  len(frontiers)  // fraction]
    deltaf_few      = deltaf[::     len(deltaf)     // fraction]


    # prepares to plot
    fig, axes = plt.subplots(2)

    # Frontier sizes.
    # If |f| -> 0, it dies out.
    # Plots in reverse 
    for frontier in frontiers_few:
        axes[0].plot(
            [i for i in range(len(frontier))],
            frontier,
            #label = u'$f_{max}$' + f' = {max(frontier)}',
            linewidth = 0.5
        )

    # Shows the change in successive frontier sizes
    for delta in deltaf_few:
        axes[1].plot(
            [i for i in range(len(delta))],
            delta,
            #label = u'mean $\delta$' + f' = {sum(delta) / len(delta):.4f}',
            linewidth = 0.5
        )


    # Shows column-wise mean of delta_f
    axes[1].plot(
        [i for i in range(len(column_mean))],
        column_mean,
        label = u'$\delta_f$ = ' + f'{sigfigs(growth, growth_unc)}',
        linewidth = 2
    )
    axes[1].axhline(y = 0, color = 'black')


    # Shows the mean frontier size by plotting its prefix sum
    fx = [i for i in range(len(column_mean))]
    frontier_prefix = [sum(column_mean[ : i + 1]) for i in range(len(column_mean))]

    # Performs a linear fit to the mean frontier size
    fits, cov = curve_fit(linear, fx, frontier_prefix, (1, 0))
    uncs = np.sqrt(np.diag(cov))

    # Creates some y-data for the linear fit
    fit_curve = [linear(x, *fits) for x in fx]

    # Plots mean frontier
    axes[0].plot(
        fx,
        frontier_prefix,
    )

    # Plots linear fit of mean frontier
    axes[0].plot(
        fx,
        fit_curve,
        label = f'y = {sigfigs(fits[0], uncs[0])} * x + {sigfigs(fits[1], uncs[1])}',
        color = 'black'
    )
    axes[0].set_xlabel('frontier index, i (unitless)')
    axes[0].set_ylabel(u'mean |$f_i$| (unitless)')


    # Adds axes labels
    axes[0].set_xlabel('frontier index, i (unitless)')
    axes[0].set_ylabel('frontier size, |f| (unitless)')
    
    axes[1].set_xlabel('frontier index, i (unitless)')
    axes[1].set_ylabel(u'$\delta_f$ (unitless)')

    # Adds legends
    axes[0].legend()
    axes[1].legend()

    plt.show()


def printout(arr, title):
    print(f'{title}:\n.. Mean:\t{sum(arr) / len(arr)}\n.. Median:\t{sorted(arr)[len(arr) // 2]}\n.. Min:\t\t{min(arr)}\n.. Max:\t\t{max(arr)}\n')
