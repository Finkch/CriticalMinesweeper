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

# Todo:
#   * Get trials to cutoff early if they are very confident they are not infinite
#   x   * Improve CDFinder end condition
#   -       - End when step is sufficiently small?
#   x       - End when deviation between last n experiments is sufficiently small?
#   * Think about deltas in experiment: don't cutoff early when infinite, rather delta proportional to #infinite?
#   * When hitting infinite, step does not decrease?
#   x   * Add another bit (or repurpose 1) to code if cell in in RQ to avoid lengthy 'in' check
#   * Write key results to file 
#   * Make graphs of reveals vs. density
#           + Separate execution path for single experiment at high trial count (for certain plots)
#       - Reveals vs. density (trial)
#       - Mean/median reveals vs. density (experiment)
#       - Max reveals vs. density (experiment)
#       - Phase diagram cutoff vs. trials (CD finer)
#   x   * Figure out why rho_critical keeps changing and get a more true value
#   x       - Visual representation of Minesweeper state
#   x       - Be able to walk through Minesweeper states

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

from critical import CriticalDensity
from experiment import Experiment
from minesweeper import Minesweeper

from visualise import visualise, pygame_init

import graph

from time import time

# Execution path to hone in on a value for rho_critical
def main():

    performance = False
    quiet = False
    
    experiments = int(1e1)
    trials = int(1e2)
    cutoff = 1e5
    alpha = 0.65
    #step = 0.3
    step = 0
    #rho = 3 / 5
    rho = 0.1
    #do_cutoff = True
    do_cutoff = False

    finder_cutoff = 1e-6
    lastn = 5
    lastn = 0

    if performance:
        experiments = 10
        rho = 0.05
        step = 0
        cutoff = 1e4
        do_cutoff = False

    finder = CriticalDensity(experiments, trials, rho, cutoff, do_cutoff, step, alpha, lastn, finder_cutoff, compress = False)

    rho_critical = finder.find(quiet)

    print(finder.str_time())

    print(f'Critical density:\n\trho_critical = {rho_critical}\n')

    graph.histogram(finder)


# Execution path to visualise a given trial
def see_ms():

    rho = 0.1
    cutoff = 1000

    ms = Minesweeper(rho, cutoff, True)
    ms.sweep()

    pygame_init()
    visualise(ms)

# Execution path to run an experiment and see the results
def plot():
    
    trials = int(1e4)
    cutoff = int(1e5)

    rho = 0.1

    do_cutoff = False

    exp = Experiment(rho, cutoff, trials, do_cutoff)

    # Runs the experiment
    start = time()
    exp.begin(quiet = False)
    end = time()

    print(exp, end='')
    print(f'.. Time taken:\t\t{end - start:.4f}s')

    graph.histogram(exp)



#main()
#see_ms()
plot()