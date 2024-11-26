# A program to answer a single questions:
# On an infinite board, what is the critical density of mines such that
# the initial reveal is finite?
#
# According to ChatGPT, which says according to percolation theory, the answer is about pho = 0.59.
# I prefer my coffee drip brewed, so let's find out experimentally.
#       Wow...that was a bad joke.
#
# First real simulation has finished!

# Todo:
#   * Get trials to cutoff early if they are very confident they are not infinite
#   * Improve CDFinder end condition
#   *   - End when step is sufficiently small?
#   *   - End when deviation between last n experiments is sufficiently small?
#   * Think about deltas in experiment: don't cutoff early when infinite, rather delta proportional to #infinite?
#   * Add another bit (or repurpose 1) to code if cell in in RQ to avoid lengthy 'in' check
#   * Write key results to file 
#   * Make graphs of reveals vs. density
#       - Reveals vs. density (trial)
#       - Mean/median reveals vs. density (experiment)
#       - Max reveals vs. density (experiment)
#       - Phase diagram cutoff vs. trials (CD finer)

from critical import CriticalDensity
from experiment import Experiment

from time import time

# Performs many experiment to find critical density
def main():

    performance = True
    quiet = False
    
    experiments = int(1e1)
    trials = int(1e2)
    cutoff = 1e3
    alpha = 0.65
    step = 0.3
    rho = 3 / 5
    do_cutoff = True

    if performance:
        rho = 0.05
        step = 0
        do_cutoff = False

    finder = CriticalDensity(experiments, trials, rho, cutoff, do_cutoff, step, alpha)

    rho_critical = finder.find(quiet)

    print(f'Critical density:\n\trho_critical = {rho_critical}\n')

    print(finder.str_time())



main()