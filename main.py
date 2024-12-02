# A program to answer a single questions:
# On an infinite board, what is the critical density of mines such that
# the initial reveal is finite?
#
# According to ChatGPT, which says according to percolation theory, the answer is about pho = 0.59.
# I prefer my coffee drip brewed, so let's find out experimentally.
#       Wow...that was a bad joke.
#
# First real simulation has finished!
#   rho_critical ~= 0.1022 mines/cell

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

from critical import CriticalDensity
from visualise import visualise
from minesweeper import Minesweeper

# Performs many experiment to find critical density
def main():

    performance = False
    quiet = False
    
    experiments = int(1e2)
    trials = int(1e4)
    cutoff = 1e6
    alpha = 0.65
    step = 0.3
    rho = 3 / 5
    do_cutoff = True

    finder_cutoff = 1e-6
    lastn = 5

    if performance:
        experiments = 10
        rho = 0.05
        step = 0
        cutoff = 1e4
        do_cutoff = False

    finder = CriticalDensity(experiments, trials, rho, cutoff, do_cutoff, step, alpha, lastn, finder_cutoff)

    rho_critical = finder.find(quiet)

    print(finder.str_time())

    print(f'Critical density:\n\trho_critical = {rho_critical}\n')

def see_ms():

    rho = 0.1
    cutoff = 1000

    ms = Minesweeper(rho, cutoff, True)
    ms.sweep()

    visualise(ms)


main()
#see_ms()