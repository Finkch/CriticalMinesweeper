# A program to answer a single questions:
# On an infinite board, what is the critical density of mines such that
# the initial reveal is finite?
#
# According to ChatGPT, which says according to percolation theory, the answer is about pho = 0.59.
# I prefer my coffee drip brewed, so let's find out experimentally.
#       Wow...that was a bad joke.
#
# First real simulation has finished!
#   Experiments = 1e2
#   Trials      = 1e3
#   Cutoff      = 1e5
#       rho_critical ~= 0.1022 mines/cell
#
# First _real_ simulation has finished! (13+ hours)
#   Experiments = 1e2 (completed in 32)
#   Trials      = 1e4
#   Cutoff      = 1e6
#       rho_critical ~= 0.09929314020180824 mines/cell
#
# I reckon as cutoff -> inf, rho_critical -> decreases to true value at exponential decay.
# As such, rho_c ~= 0.099 is likely very close to the true value.
# Similarly, trials -> inf, rho_critical -> increases.

# Todo:
#   * Get trials to cutoff early if they are very confident they are not infinite
#   x   * Improve CDFinder end condition
#   -       - End when step is sufficiently small?
#   x       - End when deviation between last n experiments is sufficiently small?
#   * Think about deltas in experiment: don't cutoff early when infinite, rather delta proportional to #infinite?
#   * When hitting infinite, step does not decrease?
#   x   * Add another bit (or repurpose 1) to code if cell in in RQ to avoid lengthy 'in' check
#   x   * Write key results to file 
#   * Make graphs of reveals vs. density
#           + Separate execution path for single experiment at high trial count (for certain plots)
#       - Reveals vs. density (trial)
#       - Mean/median reveals vs. density (experiment)
#       - Max reveals vs. density (experiment)
#       - Phase diagram cutoff vs. trials (CD finer)
#   x   * Figure out why rho_critical keeps changing and get a more true value
#   x       - Visual representation of Minesweeper state
#   x       - Be able to walk through Minesweeper states
#   * Add new category for experiment results that is number of minimum reveals
#       - Since Sweeper has r, min_reveals = 2 * (r + 1) ^ 2
#           + Or just count during initialisation

# Questions about infinite Minesweeper:
#   * ! What is the critical density !
#   x   * Is CD proportional to the initial starting area?
#   x       + No! That means my assumption that surface area proportional p(infinite) was incorrect
#   x       + It seems what is really is that frontier size doesn't matter for p(infinite)! It's about the average!
#   * How would CDFinder fare if trials = very small and cutoff = very large?
#       - This paradigm assumes that below CD, p(infinite) is very large
#       - We could use this to approach CD from the right
#   * What is the curve formed by increasing trials and/or cutoff?
#       - We could use this curve to get a better estimate for CD

# Dangit. My performance gains caused rho_critical to go from 0.1034 to ~0.2
# In fact, oddly close to doubling. Huh...
#   ...
# Oki, doubling was just a coincidence. Turns out the clever "torq" optimisation was
# incorrect. It assumed that it only needed to check newly added neighbours rather than
# all adjacent cells. Here is a counter scenario:
#   Imagine two adjacent cells, A and B, where A is adjacent to a mine but not B. A is revealed 
#   first and adds neighbours, all to flag 0 meaning not in reveal queue. Then B is revealed but even
#   though it is zero value (not flag 4), its neighbours already exist so it cannot add them to torq.
# Something similar happened in reverse if B then A causing a cell to revealed that should not have been.
# This is another reason why we use BFS instead of DFS since DFS would reveal cells that maybe shouldn't be
# revealed.

# An interesting observation on the shape of the histogram:
# On logarithmic bins, the histogram follows a roughly normal distribution (albeit right skewed). At high densities,
# the histogram's median is centred on the range belowed the cutoff. However, at low densities it appears to be exponential growth.
# The thing is, how can you tell the difference between the left tail of a normal distribution and the left tail of exponential growth?
#
# Perhaps the approach is to check the derivative on the non-log histogram to see if it appears to converge?
#
# Hm, no no. Think about the non-x-log plot. There, at low densities, it would appear as if its exponentially decreasing. However, below the critical
# density, the curve would flip outward over flat to right-skewed, causing the cluster to go from zero to "infinity". What that would look like is
# all values concentrated at the cutoff, save for a few _very_ close to the minimum possible reveals (9).
# The x-log plot may be even more interesting! Yes, it is _very_ close to (log-)linear! I think finding the absolute, smallest, negative slope (as close
# to zero as possible) is a good way of finding the "true" rho_critical.
# Wait! On further testing, it does not appear to be log-linear. After taking the log, it still appears to be
# a decay function...so then what function fits?
# Well...linear fit has errors smaller than 5%, so it's linear with 95% confidence? At the very least,
# the exponential decay is _very_ close to being exact.

from critical import CriticalDensity
from experiment import Experiment

from time import time
from math import floor, log10

# Execution path to hone in on a value for rho_critical
def CDFinder():

    performance = False
    quiet = False
    
    experiments = int(1e2)
    trials = int(1e3)
    cutoff = 1e5
    alpha = 0.65
    step = 0.15
    rho = 2 / 5
    do_cutoff = True
    #do_cutoff = False
    r = 1

    finder_cutoff = 1e-5
    lastn = 5

    logdir = f'e{floor(log10(experiments))}x{floor(log10(trials))}x{floor(log10(cutoff))}rho{str(rho).replace(".", "-")}r{r}'

    if performance:
        experiments = 10
        rho = 0.05
        step = 0
        cutoff = 1e4
        do_cutoff = False


    for i in range(10):

        print(f'\nStarting CDFinder run {i + 1} with safe zone r = {i}')

        r = i
        logdir = f'e{floor(log10(experiments))}x{floor(log10(trials))}x{floor(log10(cutoff))}rho{str(rho).replace(".", "-")}r{r}'

        finder = CriticalDensity(experiments, trials, rho, cutoff, do_cutoff, r, step, alpha, lastn, finder_cutoff, compress = False, logdir = logdir)

        rho_critical = finder.find(quiet)

        print(finder.str_time())

        print(f'Critical density:\n\trho_critical = {rho_critical}\n')


# Execution path to perform a single experiment
def experiment():

    performance = False

    rho = 0.1
    trials = int(1e4)
    cutoff = int(1e7)
    do_cutoff = False
    r = 10

    logdir = f'{floor(log10(trials))}x{floor(log10(cutoff))}rho{str(rho).replace(".", "-")}r{r}'


    if performance:
        trials = 100
        rho = 0.05
        cutoff = 1e4
        do_cutoff = False
        logdir = None


    exp = Experiment(rho, cutoff, trials, do_cutoff, r, logdir = logdir)

    start = time()
    exp.begin(quiet = False)
    end = time()

    print(exp)
    print(f'.. Time taken:\t\t{end - start:.4f}s')



CDFinder()
#experiment()
